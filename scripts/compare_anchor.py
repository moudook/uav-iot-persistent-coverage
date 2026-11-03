"""Compare the critical-coverage anchor arm (exp_anchor_eval) against the
base ego+shaping arm (exp_ego_eval) using the corrected held-out protocol.

Reads eval_heldout.json for both tags and computes:
  - mean/sd per arm
  - paired difference (same seed indices) + 95% CI (t-based)
  - stress comparison from stress_eval.json vs stress_eval_anchor.json
"""
import json, os, math

BASE = r"C:\Users\gbust\Downloads\Academic\Courses\Machine_learning_in_wireless_network\Project1"
RUNS = os.path.join(BASE, "ml_impl", "runs")


def load_heldout(tag):
    p = os.path.join(RUNS, tag, "eval_heldout.json")
    d = json.load(open(p, encoding="utf-8"))
    per = [v["mean"] for v in d["per_checkpoint"].values()]
    det = [v["det_mean"] for v in d["per_checkpoint"].values()]
    return per, det, d


def t_half(xs):
    n = len(xs)
    if n < 2:
        return 0.0
    mean = sum(xs) / n
    var = sum((x - mean) ** 2 for x in xs) / (n - 1)
    sd = math.sqrt(var)
    # t_{0.975, n-1}
    tcrit = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571,
             6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228}.get(n - 1, 2.0)
    return tcrit * sd / math.sqrt(n)


def mean(xs):
    return sum(xs) / len(xs)


per_base, det_base, _ = load_heldout("exp_ego_eval")
per_anchor, det_anchor, _ = load_heldout("exp_anchor_eval")

print("=== NOMINAL HELD-OUT (20 scenes, 5 frozen ckpts) ===")
print(f"base   : mean={mean(per_base):.4f}  CI [{mean(per_base)-t_half(per_base):.4f}, {mean(per_base)+t_half(per_base):.4f}]  det={mean(det_base):.4f}")
print(f"anchor : mean={mean(per_anchor):.4f}  CI [{mean(per_anchor)-t_half(per_anchor):.4f}, {mean(per_anchor)+t_half(per_anchor):.4f}]  det={mean(det_anchor):.4f}")

# paired difference (same seed ordering: both are seed_0..4)
diffs = [a - b for a, b in zip(per_anchor, per_base)]
dmean = mean(diffs)
dhalf = t_half(diffs)
print(f"paired anchor-base: {dmean:+.4f}  95% CI [{dmean-dhalf:+.4f}, {dmean+dhalf:+.4f}]")
if dhalf > 0 and abs(dmean) > dhalf:
    print("verdict: RESOLVED")
else:
    print("verdict: not resolved at this resolution")

print()
print("=== STRESS (zero-shot) ===")
s_base = json.load(open(os.path.join(RUNS, "stress_eval", "stress_eval.json"), encoding="utf-8"))
s_anchor = json.load(open(os.path.join(RUNS, "stress_eval", "stress_eval_anchor.json"), encoding="utf-8"))
print(f"{'regime':14s} {'base learner':>11s} {'anchor learner':>13s} {'base diff':>9s} {'anchor diff':>11s}")
for reg in ["nominal", "small_battery", "low_comm", "clustered", "failure", "multi_failure"]:
    b = s_base["regimes"].get(reg, {})
    a = s_anchor["regimes"].get(reg, {})
    bl = b.get("learner_mean")
    al = a.get("learner_mean")
    bd = b.get("learner_minus_rule")
    ad = a.get("learner_minus_rule")
    bl_s = f"{bl:.4f}" if bl == bl else "NA"
    al_s = f"{al:.4f}" if al == al else "NA"
    bd_s = f"{bd:+.4f}" if bd is not None else "--"
    ad_s = f"{ad:+.4f}" if ad is not None else "--"
    print(f"{reg:14s} {bl_s:>11s} {al_s:>13s} {bd_s:>9s} {ad_s:>11s}")