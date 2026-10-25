"""The random masked policy: the control the comparison table was missing.

The table compares the learned controller against hand-written rules,
against its own argmax policy, and against two learned baselines.  It
did not compare it against a policy that simply samples uniformly from
the admissible action set -- the control that says what a controller
that has learned nothing achieves under the same mask, on the same
scenes, with the same rules.

It costs no training: the policy is the mask plus a uniform draw.

    python analysis/random_baseline.py
"""
from __future__ import annotations

import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ML = os.path.dirname(HERE)
sys.path.insert(0, ML)

import numpy as np

from uav_wireless.env import UAVIoTEnv, N_ACTIONS
from uav_wireless.experiments import base_config


def run_episode(cfg, seed, steps=2000):
    """One episode of the uniform masked policy."""
    c = copy.deepcopy(cfg)
    c.seed = seed
    env = UAVIoTEnv(c)
    env.reset()
    rng = np.random.default_rng(seed)
    ck = []
    for t in range(steps):
        masks = env.action_masks()
        acts = np.zeros(c.N, dtype=np.int64)
        for i in range(c.N):
            m = masks[i]
            admissible = np.flatnonzero(m)
            if len(admissible) == 0:
                acts[i] = 0
            else:
                acts[i] = int(rng.choice(admissible))
        out = env.step(acts)
        if out and len(out) > 1:
            ck.append(out[1])
    return env


def main() -> int:
    cfg = base_config()
    eval_seeds = 5
    steps = cfg.episode_len
    cks, ags, scs = [], [], []
    for e in range(eval_seeds):
        env = run_episode(cfg, e, steps)
        ck = env.coverage_score() if hasattr(env, "coverage_score") else None
        if ck is None:
            ck = float(getattr(env, "last_ck", 0.0))
        cks.append(float(ck))
        ags.append(float(getattr(env, "last_ag", 0.0)))
        scs.append(float(getattr(env, "last_sc", 0.0)))
        print(f"  the random masked policy, scene {e}: CK = {cks[-1]:.4f}")
    res = dict(model="Random masked policy", eval_seeds=eval_seeds,
               steps=int(steps),
               CK=float(np.mean(cks)),
               CK_std=float(np.std(cks, ddof=1)) if len(cks) > 1 else 0.0,
               AG=float(np.mean(ags)), SC=float(np.mean(scs)),
               per_scene_CK=[float(x) for x in cks])
    out = os.path.join(HERE, "random_baseline.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)
    print(f"  the random masked policy: CK = {res['CK']:.4f} "
          f"(sd {res['CK_std']:.4f})")
    print(f"Saved -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
