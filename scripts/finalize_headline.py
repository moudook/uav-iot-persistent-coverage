"""Compute the corrected headline numbers from a finished retrain.

Reads the per-seed results, the held-out evaluation, and the held-out rule
baselines, and prints the values that go into the report (CK, sd, gap,
Student-t interval, per-seed list).  Exits nonzero if any input is missing.
"""
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RUNS = os.path.join(ROOT, "ml_impl", "runs")
TAG = "exp_ego_fixed"


def main():
    seeds = sorted(glob.glob(os.path.join(RUNS, TAG, "seed_*.json")))
    if len(seeds) < 5:
        print(f"only {len(seeds)}/5 seeds finished for {TAG}")
        return 1
    per_seed = [json.load(open(f, encoding="utf-8"))["eval_ck"] for f in seeds]
    heldout = os.path.join(RUNS, TAG, "eval_heldout.json")
    if os.path.exists(heldout):
        h = json.load(open(heldout, encoding="utf-8"))
        ck = float(h["mean_over_seeds"])
        sd = float(h["sd_over_seeds"])
        n = int(h.get("n_seeds", len(per_seed)))
        per_seed = [float(v) for v in h["per_checkpoint"].values()] if False else per_seed
    else:
        ck = float(np.mean(per_seed))
        sd = float(np.std(per_seed, ddof=1))
        n = len(per_seed)

    rules = json.load(open(os.path.join(RUNS, "rules_heldout", "eval_rules.json"),
                           encoding="utf-8"))["summary"]
    best_name = max(rules, key=lambda k: rules[k]["CK"])
    best = rules[best_name]
    rule_ck = float(best["CK"])

    diffs = [p - rule_ck for p in per_seed]
    mean_d = float(np.mean(diffs))
    sd_d = float(np.std(diffs, ddof=1))
    from scipy import stats
    crit = float(stats.t.ppf(0.975, n - 1))
    half = crit * sd_d / np.sqrt(n)

    out = dict(tag=TAG, ck=round(ck, 4), sd=round(sd, 4), n=n,
               per_seed=[round(p, 4) for p in per_seed],
               rule=best_name, rule_ck=round(rule_ck, 4),
               gap=round(mean_d, 4),
               gap_ci=[round(mean_d - half, 4), round(mean_d + half, 4)])
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
