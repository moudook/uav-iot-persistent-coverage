"""Consolidated summary of all innovation experiments from the 2026-11-03
autonomous session. Run after all background jobs complete."""
import json, os, math

BASE = r"C:\Users\gbust\Downloads\Academic\Courses\Machine_learning_in_wireless_network\Project1"
RUNS = os.path.join(BASE, "ml_impl", "runs")

def heldout(tag):
    p = os.path.join(RUNS, tag, "eval_heldout.json")
    if not os.path.exists(p):
        return None
    d = json.load(open(p, encoding="utf-8"))
    per = [v["mean"] for v in d["per_checkpoint"].values()]
    det = [v["det_mean"] for v in d["per_checkpoint"].values()]
    return per, det

def t_half(xs):
    n = len(xs)
    if n < 2:
        return 0.0
    m = sum(xs) / n
    var = sum((x - m) ** 2 for x in xs) / (n - 1)
    sd = math.sqrt(var)
    tcrit = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571,
             6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228}.get(n-1, 2.0)
    return tcrit * sd / math.sqrt(n)

out = []
out.append("=" * 72)
out.append("INNOVATION RESULTS SUMMARY - 2026-11-03 (autonomous session)")
out.append("=" * 72)

# headline nominal arms
arms = {
    "base (ego+shape)": "exp_ego_eval",
    "anchor (+1 critical feature)": "exp_anchor_eval",
    "action-repeat (train rep=4)": "exp_ar_eval",
}
out.append("\n--- NOMINAL held-out (20 scenes, 5 seeds) ---")
for label, tag in arms.items():
    r = heldout(tag)
    if not r:
        out.append(f"  {label}: no eval_heldout.json yet")
        continue
    per, det = r
    m = sum(per) / len(per)
    h = t_half(per)
    dm = sum(det) / len(det)
    out.append(f"  {label:28s} mean={m:.4f} CI [{m-h:.4f}, {m+h:.4f}] det={dm:.4f}")

# paired diffs vs base (same seed indices; AR has 3 seeds, base has 5)
base_per, _ = heldout("exp_ego_eval")
if base_per:
    out.append("\n--- paired diffs vs base (same seed indices) ---")
    for label, tag in [("anchor", "exp_anchor_eval"), ("action-repeat", "exp_ar_eval")]:
        r = heldout(tag)
        if not r:
            continue
        per, _ = r
        n = min(len(per), len(base_per))
        diffs = [a - b for a, b in zip(per[:n], base_per[:n])]
        dm = sum(diffs) / len(diffs)
        dh = t_half(diffs)
        verdict = "RESOLVED" if (dh > 0 and abs(dm) > dh) else "not resolved"
        out.append(f"  {label:12s} n={n} {dm:+.4f} CI [{dm-dh:+.4f}, {dm+dh:+.4f}]  {verdict}")

# planning
pl = os.path.join(RUNS, "exp_ego_eval", "eval_planning_500.json")
ck = os.path.join(RUNS, "exp_ego_eval", "eval_ckpt_500.json")
if os.path.exists(pl) and os.path.exists(ck):
    out.append("\n--- PLANNING vs BASE at 500-step protocol ---")
    dp = json.load(open(pl, encoding="utf-8"))
    dc = json.load(open(ck, encoding="utf-8"))
    pp = [v["mean"] for v in dp["per_checkpoint"].values()]
    pc = [v["mean"] for v in dc["per_checkpoint"].values()]
    mp = sum(pp) / len(pp); mc = sum(pc) / len(pc)
    diffs = [p - c for p, c in zip(pp, pc)]
    dm = sum(diffs) / len(diffs); dh = t_half(diffs)
    verdict = "RESOLVED" if (dh > 0 and abs(dm) > dh) else "not resolved"
    out.append(f"  base {mc:.4f} vs planned {mp:.4f}: {dm:+.4f} CI [{dm-dh:+.4f}, {dm+dh:+.4f}]  {verdict}")
else:
    out.append("\n--- PLANNING: results not ready yet ---")

# combined small_battery
cb = os.path.join(RUNS, "innov_currid_energy_anchor")
if os.path.isdir(cb):
    js = [f for f in os.listdir(cb) if f.startswith("seed_") and f.endswith(".json")]
    if js:
        cks = [json.load(open(os.path.join(cb, f), encoding="utf-8")).get("eval_ck") for f in js]
        cks = [c for c in cks if c is not None]
        out.append("\n--- combined curriculum+energy+anchor on small_battery ---")
        out.append(f"  n={len(cks)} mean={sum(cks)/len(cks):.4f} per-seed={[round(c,4) for c in cks]}")
        out.append("  (reference: curriculum+energy alone = 0.831, ties rule)")
    else:
        out.append("\n--- combined small_battery: training not finished ---")

txt = "\n".join(out)
print(txt)
dst = os.path.join(BASE, "docs", "INNOVATION_SUMMARY_2026-11-03.txt")
open(dst, "w", encoding="utf-8").write(txt)
print()
print("wrote", dst)