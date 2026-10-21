"""Merge the ablation's parts into the one CSV the paper reads.

The component ablation is split across processes so that the matrix does
not wait on one long job.  Each part writes its own CSV; this assembles
them into `results_ablation.csv` (or the stress table) in the canonical
variant order, and it REJECTS a merge that is missing a variant or that
mixes protocols: a table assembled from parts measured under different
budgets or on different devices is not a measurement, it is a collage.
"""

from __future__ import annotations

import argparse
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ML = os.path.dirname(HERE)
sys.path.insert(0, ML)

ORDER = ["Full", "no-criticality", "no-degraded", "no-energy-cost",
         "no-undercoverage", "no-reserve", "no-arbitration", "no-mask",
         "no-agent-id", "no-map", "no-pad-bearing", "VanillaMAPPO"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stress", action="store_true")
    a = ap.parse_args()

    tag = "_stress" if a.stress else ""
    parts = [os.path.join(ML, f"results_ablation{tag}_part{k}.csv")
             for k in ("a", "b")]
    out = os.path.join(ML, f"results_ablation{tag}.csv")

    rows = {}
    proto = set()
    for p in parts:
        if not os.path.exists(p):
            print(f"  MISSING: {os.path.basename(p)}")
            continue
        with open(p, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                rows[r["model"]] = r
                proto.add((r.get("episodes"), r.get("train_seeds"),
                           r.get("device")))

    missing = [v for v in ORDER if v not in rows]
    if missing:
        print(f"  the merge is INCOMPLETE: {', '.join(missing)}")
        return 1
    if len(proto) != 1:
        print(f"  the parts do not share one protocol: {sorted(proto)}")
        return 1

    fields = []
    for v in ORDER:
        for k in rows[v]:
            if k not in fields:
                fields.append(k)
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for v in ORDER:
            w.writerow({k: rows[v].get(k, "") for k in fields})
    print(f"Saved -> {out}  ({len(ORDER)} variants, protocol {proto.pop()})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
