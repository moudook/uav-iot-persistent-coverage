"""Evaluate the rule baselines over a set of evaluation scenes.

The report compares a learned policy against four deterministic rules.  For
that comparison to be a comparison, both sides have to be measured over the
SAME set of scenes: the rules are deterministic given a scene, so their
seed-to-seed spread is scene-to-scene spread, and a single-scene number for
a rule is not comparable with a multi-scene mean for a learner.

Writes ml_impl/runs/rules/eval_rules.json:

    {"eval_seeds": [0..n-1],
     "rules": {"Fixed": [ck per seed], ...},
     "summary": {"Fixed": {"CK": mean, "CK_std": sample sd}, ...}}

Run:  python scripts/eval_rules.py --eval-seeds 10
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ml_impl"))
for _v in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np

from uav_wireless.experiments import base_config
from uav_wireless.train import (baseline_fixed, baseline_greedy,
                                baseline_reactive, baseline_reactive_local)

RULES = [
    ("Fixed", baseline_fixed),
    ("Greedy", baseline_greedy),
    ("Reactive", baseline_reactive),
    ("Reactive-local", baseline_reactive_local),
]

FIELDS = ("CK", "AG", "SC", "Energy", "Distance", "UnexecutedActions",
          "CovIntegral", "ReturnEvents", "Stranded")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--eval-seeds", type=int, default=10)
    ap.add_argument("--steps", type=int, default=2000)
    ap.add_argument("--tag", default="rules")
    args = ap.parse_args()

    outdir = os.path.join(os.path.dirname(__file__), "..", "ml_impl",
                          "runs", args.tag)
    os.makedirs(outdir, exist_ok=True)
    out = os.path.join(outdir, "eval_rules.json")

    cfg = base_config()
    steps = args.steps or cfg.episode_len
    rec = {"eval_seeds": list(range(args.eval_seeds)), "steps": steps,
           "rules": {}, "summary": {}}
    for name, fn in RULES:
        per = []
        for s in rec["eval_seeds"]:
            r = fn(cfg, steps=steps, seed=s)
            per.append({k: (float(r[k]) if k in r and r[k] is not None else None)
                        for k in FIELDS})
        rec["rules"][name] = per
        cks = [p["CK"] for p in per]
        rec["summary"][name] = {
            "CK": float(np.mean(cks)),
            "CK_std": float(np.std(cks, ddof=1)) if len(cks) > 1 else 0.0,
            "n": len(cks),
            "per_seed_CK": cks,
        }
        for k in ("AG", "SC"):
            vals = [p[k] for p in per if p[k] is not None]
            if vals:
                rec["summary"][name][k] = float(np.mean(vals))
        for k in ("Energy", "Distance", "UnexecutedActions"):
            vals = [p[k] for p in per if p[k] is not None]
            if vals:
                rec["summary"][name][k] = float(np.mean(vals))
        print("%-16s CK=%.4f (sd %.4f) n=%d"
              % (name, rec["summary"][name]["CK"],
                 rec["summary"][name]["CK_std"], len(cks)), flush=True)

    with open(out, "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=1)
    print("wrote", out)


if __name__ == "__main__":
    main()
