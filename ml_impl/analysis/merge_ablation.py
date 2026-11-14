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


def _merge_part_rows(parts):
    rows = {}
    proto = set()
    config_hashes = set()
    for part in parts:
        for row in part:
            model = row.get("model", "")
            if not model:
                raise ValueError("a part contains a row with no model")
            if model in rows:
                raise ValueError(f"duplicate model row: {model}")
            config_hash = row.get("config_hash", "").strip()
            if not config_hash:
                raise ValueError(f"{model} is missing config_hash")
            rows[model] = row
            config_hashes.add(config_hash)
            proto.add((row.get("episodes"), row.get("train_seeds"),
                       row.get("device")))

    if len(config_hashes) != 1:
        raise ValueError("the parts do not share one config_hash")
    if len(proto) != 1:
        raise ValueError(f"the parts do not share one protocol: {sorted(proto)}")
    return rows, next(iter(proto))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stress", action="store_true")
    a = ap.parse_args()

    tag = "_stress" if a.stress else ""
    parts = [os.path.join(ML, f"results_ablation{tag}_part{k}.csv")
             for k in ("a", "b")]
    out = os.path.join(ML, f"results_ablation{tag}.csv")

    part_rows = []
    for p in parts:
        if not os.path.exists(p):
            print(f"  MISSING: {os.path.basename(p)}")
            continue
        with open(p, newline="", encoding="utf-8") as f:
            part_rows.append(list(csv.DictReader(f)))

    try:
        rows, protocol = _merge_part_rows(part_rows)
    except ValueError as exc:
        print(f"  merge refused: {exc}", file=sys.stderr)
        return 1

    missing = [v for v in ORDER if v not in rows]
    if missing:
        print(f"  the merge is INCOMPLETE: {', '.join(missing)}")
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
    print(f"Saved -> {out}  ({len(ORDER)} variants, protocol {protocol})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
