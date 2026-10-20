"""
The reproducibility probe: is an evaluation a function of (policy, scene)?

The deployed policy SAMPLES its actions, and the sampling draws from the
global torch RNG.  If that RNG is not seeded at the start of an
evaluation, then every evaluation is a fresh random draw: the same policy
on the same scene gives a different answer every time, the paper's numbers
cannot be reproduced from the stored artefact, and a comparison between two
controllers carries an unquantified sampling component.

This probe compares the two things that matter, separately:

  * the SEQUENCE OF SAMPLED ACTIONS, step by step.  This is the direct
    evidence that the sampling stream is controlled: if the actions agree
    for every step, the stream is the same.
  * the EPISODE SUMMARY (coverage, energy, distance, coverage deficit),
    which is what the paper quotes.

They are reported separately because they fail for different reasons.  The
actions can agree while the summary differs, if some quantity outside the
seeded stream moves; that would be a different defect, and it should be
visible as such rather than hidden inside a single equality.

Run:  python analysis/reproducibility_probe.py [--trials 20]
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch

from uav_wireless.env import SimConfig, UAVIoTEnv
from uav_wireless.mappo import MAPPO
from uav_wireless.seeding import seed_evaluation

HERE = os.path.dirname(os.path.abspath(__file__))
SUMMARY_KEYS = ("CK", "Energy", "Distance", "CovIntegral")


def rollout_actions(agent, cfg, seed, steps):
    """The sampled action sequence and the episode summary."""
    c = copy.deepcopy(cfg)
    c.seed = seed
    seed_evaluation(seed)
    env = UAVIoTEnv(c)
    obs, _ = env.reset()
    acts = []
    for _ in range(steps):
        mask = np.stack(env.action_masks())
        for i in range(c.N):
            if mask[i].sum() == 0:
                mask[i, 0] = True
                mask[i] = mask[i] | (mask[i] == 0)
        a = agent.act(obs, mask, deterministic=False)
        acts.append(tuple(int(x) for x in np.asarray(a).ravel()))
        obs, _, _, done, _ = env.step(a)
        if done:
            break
    return acts, env.summary()


def probe(cfg=None, steps=60, seed=2, agent=None):
    """One reproducibility check.  Returns a dict of the findings."""
    if cfg is None:
        cfg = SimConfig(N=4, K=2, M=8, episode_len=steps, seed=0)
    if agent is None:
        e = UAVIoTEnv(cfg)
        agent = MAPPO(n_agents=cfg.N, obs_dim=e.obs_dim,
                      state_dim=e.state_dim)
    # the ambient state is deliberately different for the two evaluations
    torch.manual_seed(11)
    a1, s1 = rollout_actions(agent, cfg, seed, steps)
    torch.manual_seed(999_983)
    a2, s2 = rollout_actions(agent, cfg, seed, steps)
    first_diff = None
    for i, (x, y) in enumerate(zip(a1, a2)):
        if x != y:
            first_diff = i
            break
    same_actions = a1 == a2
    same_summary = all(s1[k] == s2[k] for k in SUMMARY_KEYS)
    return dict(
        same_actions=bool(same_actions),
        same_summary=bool(same_summary),
        first_divergent_step=first_diff,
        n_steps=len(a1),
        summary_a={k: float(s1[k]) for k in SUMMARY_KEYS},
        summary_b={k: float(s2[k]) for k in SUMMARY_KEYS},
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=20)
    args = ap.parse_args()
    bad = []
    for t in range(args.trials):
        r = probe()
        if not (r["same_actions"] and r["same_summary"]):
            bad.append(r)
            print(f"trial {t}: DIVERGED at step {r['first_divergent_step']} "
                  f"actions_same={r['same_actions']} "
                  f"summary_same={r['same_summary']}")
    print(f"{args.trials - len(bad)}/{args.trials} trials reproduced exactly")
    out = os.path.join(HERE, "reproducibility_probe.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(dict(trials=args.trials, failures=bad), f, indent=2)
    print(f"Saved -> {out}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
