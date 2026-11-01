"""Random (uniform over feasible actions) baseline.

SI-2's diagnostic: a learner that scores BELOW this control is not merely
weaker than a hand-written rule, it is worse than chance, which points at the
reward or the credit rather than at the capacity of the policy class.  The
control is only useful if it is measured on the same configuration and the
same scenes as everything else, so the configuration comes from
`base_config()` and the scene is selected by the seed, exactly as the rule
baselines and the learned controllers are.

Run:  python scripts/random_baseline.py --seeds 10 --steps 2000
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ml_impl"))
for _v in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import copy

import numpy as np

from uav_wireless.env import SimConfig, UAVIoTEnv          # noqa: F401
from uav_wireless.experiments import base_config


def run(cfg, seed, steps):
    """One episode of uniform sampling over the feasible-action set."""
    c = copy.deepcopy(cfg)
    c.seed = seed
    c.episode_len = steps
    rng = np.random.default_rng(seed * 7919 + 13)
    env = UAVIoTEnv(c)
    obs, st = env.reset()
    for _ in range(steps):
        mask = np.stack(env.action_masks())
        for i in range(c.N):
            if not mask[i].any():
                mask[i, 0] = True
        acts = np.array([rng.choice(np.where(mask[i])[0]) for i in range(c.N)],
                        dtype=np.int64)
        obs, st, r, done, _ = env.step(acts)
        if done:
            break
    return env.summary()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=10)
    ap.add_argument("--steps", type=int, default=2000)
    ap.add_argument("--tag", default="diag")
    a = ap.parse_args()

    cfg = base_config()
    res = [run(cfg, s, a.steps) for s in range(a.seeds)]
    cks = [float(r.get("CK", r.get("ck", 0.0))) for r in res]
    mean = float(np.mean(cks))
    sd = float(np.std(cks, ddof=1)) if len(cks) > 1 else 0.0
    print("random baseline CK: mean=%.4f sd(sample)=%.4f n=%d"
          % (mean, sd, len(cks)))
    print("per-seed CK:", [round(c, 4) for c in cks])
    outdir = os.path.join(os.path.dirname(__file__), "..", "ml_impl",
                          "runs", a.tag)
    os.makedirs(outdir, exist_ok=True)
    out = os.path.join(outdir, "random_baseline.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"cks": cks, "seeds": list(range(a.seeds)),
                   "steps": a.steps, "mean": mean, "sd": sd,
                   "summaries": res}, f, indent=1)
    print("wrote", out)


if __name__ == "__main__":
    main()
