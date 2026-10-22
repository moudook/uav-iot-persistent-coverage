"""Compare two measurements of the same configuration and record the verdict.

The paper claims that a training run is a function of its seed: the same
configuration, the same seed and the same protocol give the same numbers.
The claim audit checks that property inside a run; this script checks it
across two INDEPENDENT runs of a whole matrix, which is the stronger form
of the same statement.

Usage:
    python analysis/determinism_check.py --old OLD.csv --new NEW.csv

It writes analysis/determinism_check.json, and the token table reads
that file for the sentence the paper prints.
"""
from __future__ import annotations

import argparse
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

# the columns that the comparison covers: the learned controller's three
# metrics and the two rules' coverage, on every variant
KEYS = ("mappo_CK", "mappo_SC", "mappo_AG", "react_CK", "reactlocal_CK")


def read(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--old", required=True, help="the earlier measurement")
    ap.add_argument("--new", required=True, help="the later measurement")
    ap.add_argument("--out", default=os.path.join(HERE, "determinism_check.json"))
    args = ap.parse_args()

    old, new = read(args.old), read(args.new)
    if len(old) != len(new):
        print(f"  the row counts differ: {len(old)} against {len(new)}")
        return 1

    compared = 0
    differing = 0
    max_diff = 0.0
    worst = None
    for o, n in zip(old, new):
        if (o.get("scenario"), o.get("variant")) != (n.get("scenario"),
                                                    n.get("variant")):
            print("  the rows are in a different order; aborting")
            return 1
        for k in KEYS:
            if o.get(k) in (None, "") or n.get(k) in (None, ""):
                continue
            compared += 1
            d = abs(float(o[k]) - float(n[k]))
            if d > max_diff:
                max_diff = d
                worst = [o.get("scenario"), o.get("variant"), k,
                         float(o[k]), float(n[k])]
            if d > 1e-9:
                differing += 1

    verdict = ("the two runs agree exactly" if differing == 0 else
               f"{differing} of {compared} values differ")
    out = dict(compared=int(compared), differing=int(differing),
               max_abs_difference=float(max_diff), worst=worst,
               keys=list(KEYS), verdict=verdict,
               old=os.path.basename(args.old), new=os.path.basename(args.new))
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"  {compared} values compared, {differing} differ, "
          f"the largest difference {max_diff:g}")
    print(f"  {verdict}")
    print(f"Saved -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
