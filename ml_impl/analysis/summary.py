"""
The final summary, read from the artefacts.

Every number in the report and in the state file comes from here, so the
two cannot disagree with the measurements.

Run:  python analysis/summary.py [--json]
"""
from __future__ import annotations

import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ML = os.path.dirname(HERE)


def rows_csv(name):
    p = os.path.join(ML, name)
    if not os.path.exists(p):
        return []
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def json_file(name):
    p = os.path.join(HERE, name)
    if not os.path.exists(p):
        return []
    return json.load(open(p, encoding="utf-8"))


def main():
    out = {}

    main_rows = {r["model"]: r for r in rows_csv("results_main.csv")}
    # the numeric columns are converted; the DEVICE is a string and is
    # reported as one
    NUMERIC = ("CK", "CK_std", "AG", "SC", "CovIntegral", "ReturnEvents",
               "Stranded", "train_seeds")
    out["main"] = {k: {c: (float(v[c]) if v.get(c) not in (None, "")
                              else None)
                        for c in NUMERIC
                        if c in v}
                    | {"device": v.get("device", "")}
                    for k, v in main_rows.items()}
    if "MAPPO" in main_rows and "Reactive" in main_rows:
        gap = (float(main_rows["Reactive"]["CK"])
               - float(main_rows["MAPPO"]["CK"]))
        out["gap_vs_reactive"] = round(gap, 3)
    for cand in ("Reactive-local",):
        if cand in main_rows and "MAPPO" in main_rows:
            out["gap_vs_best_rule"] = round(
                float(main_rows[cand]["CK"])
                - float(main_rows["MAPPO"]["CK"]), 3)

    for f, key in (("ab_observation.json", "observation"),
                   ("ab_credit.json", "credit"),
                   ("ab_energy_management.json", "energy"),
                   ("ab_map_resolution.json", "map_resolution"),
                   ("ab_budget.json", "budget")):
        rs = json_file(f)
        if rs:
            out[key] = [{k: (round(v, 4) if isinstance(v, float) else v)
                         for k, v in r.items() if k != "per_seed_CK"}
                        for r in rs]

    abl = rows_csv("results_ablation.csv")
    if abl:
        out["ablation"] = {r["model"]: {"CK": round(float(r["CK"]), 4),
                                        "CK_std": round(float(r.get("CK_std")
                                                             or 0), 4),
                                        "device": r.get("device", "")}
                           for r in abl}
    stress = rows_csv("results_ablation_stress.csv")
    if stress:
        out["ablation_stress"] = {r["model"]: {"CK": round(float(r["CK"]), 4)}
                                   for r in stress}

    scen = rows_csv("results_scenarios.csv")
    if scen:
        wins = losses = ties = 0
        for r in scen:
            try:
                d = float(r["mappo_CK"]) - float(r["react_CK"])
            except (TypeError, ValueError, KeyError):
                continue
            if d > 0.02:
                wins += 1
            elif d < -0.02:
                losses += 1
            else:
                ties += 1
        out["scenarios"] = {"variants": len(scen), "ahead": wins,
                            "behind": losses, "level": ties}

    learned = rows_csv("results_learned_baselines.csv")
    if learned:
        out["learned_baselines"] = {r["model"]: {"CK": round(float(r["CK"]), 4),
                                                 "CK_std": round(float(
                                                     r.get("CK_std") or 0), 4)}
                                     for r in learned}

    audit = json_file("claim_audit.json")
    if audit:
        from collections import Counter
        c = Counter(r["status"] for r in audit)
        out["audit"] = {"items": len(audit), "verified": c.get("PASS", 0),
                        "failed": c.get("FAIL", 0),
                        "informational": c.get("INFO", 0)}

    if "--json" in sys.argv:
        print(json.dumps(out, indent=2))
        return 0

    print("=" * 74)
    print(" THE MEASURED PAPER, read from the artefacts")
    print("=" * 74)
    for k, v in out.get("main", {}).items():
        ck = v.get("CK")
        std = v.get("CK_std")
        s = f"{ck:.3f}" + (f" +- {std:.3f}" if std else "")
        sc = v.get("SC")
        print(f"  {k:22s} CK {s:>18s}   SC {sc:.3f}   device {v.get('device','-')}")
    for k in ("gap_vs_reactive", "gap_vs_best_rule"):
        if k in out:
            print(f"  {k:22s} {out[k]:+.3f}")
    if "ablation" in out:
        print("\n  the component ablation:")
        for k, v in out["ablation"].items():
            print(f"    {k:22s} CK {v['CK']:.3f} +- {v['CK_std']:.3f}")
    if "budget" in out:
        print("\n  the training-budget sweep:")
        for r in out["budget"]:
            print(f"    {r['episodes']:3d} episodes  CK {r['CK']:.3f} "
                  f"+- {r['CK_std']:.3f}")
    if "audit" in out:
        a = out["audit"]
        print(f"\n  the claim audit: {a['items']} items, {a['verified']} "
              f"verified, {a['failed']} failed, {a['informational']} "
              f"informational")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
