"""Compare team vs C3 credit on a regime (G3).

Usage: python scripts/analyze_c3.py single_pad
Reads ml_impl/runs/g3/<regime>/{team,c3}/seed_*.json and reports mean CK,
last-10 CK, entropy, headroom, and a paired seed-level delta.
"""
import os, sys, json, statistics

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
G3 = os.path.join(PROJ, "ml_impl", "runs", "g3")


def load(regime, mode):
    d = os.path.join(G3, regime, mode)
    if not os.path.isdir(d):
        return []
    out = []
    for f in sorted(os.listdir(d)):
        if not f.startswith("seed_") or not f.endswith(".json"):
            continue
        rec = json.load(open(os.path.join(d, f)))
        hist = rec.get("hist", [])
        cks = [h.get("CK", 0.0) for h in hist]
        ents = [h.get("entropy", 0.0) for h in hist]
        out.append({
            "seed": rec["seed"],
            "final_ck": rec.get("final_ck"),
            "mean_ck": statistics.fmean(cks) if cks else None,
            "last10_ck": statistics.fmean(cks[-10:]) if len(cks) >= 10 else None,
            "min_ent": min(ents) if ents else None,
            "final_ent": ents[-1] if ents else None,
        })
    return out


def summarise(rows):
    if not rows:
        return None
    def m(key):
        vals = [r[key] for r in rows if r[key] is not None]
        return (statistics.fmean(vals), statistics.pstdev(vals)) if vals else (None, None)
    fc, _ = m("final_ck")
    lc, _ = m("last10_ck")
    ent, _ = m("final_ent")
    return {
        "n": len(rows),
        "final_ck": m("final_ck"),
        "last10_ck": m("last10_ck"),
        "final_ent": m("final_ent"),
        "headroom": (1 - fc) if fc is not None else None,
    }


def main():
    regime = sys.argv[1] if len(sys.argv) > 1 else "single_pad"
    team = load(regime, "team")
    c3 = load(regime, "c3")
    print(f"=== {regime}: team vs C3 ===")
    for label, rows in (("team", team), ("c3", c3)):
        s = summarise(rows)
        if s is None:
            print(f"  {label}: no data")
            continue
        fc, fc_sd = s["final_ck"]
        lc, lc_sd = s["last10_ck"]
        ent, _ = s["final_ent"]
        print(f"  {label:4s} n={s['n']}  final CK={fc:.4f} (sd {fc_sd:.4f})  "
              f"last10={lc:.4f}  ent={ent:.3f}  headroom={s['headroom']:.4f}")

    # paired delta by seed
    t_by = {r["seed"]: r for r in team}
    c_by = {r["seed"]: r for r in c3}
    common = sorted(set(t_by) & set(c_by))
    if common:
        deltas = [c_by[s]["final_ck"] - t_by[s]["final_ck"] for s in common]
        print(f"  paired delta (c3 - team) over {len(common)} seeds: "
              f"mean={statistics.fmean(deltas):+.4f}  "
              f"range=[{min(deltas):+.4f}, {max(deltas):+.4f}]")


if __name__ == "__main__":
    main()
