"""
Why does the deterministic policy fail to deploy from a clustered start?

OBSERVATION
  From a clustered start the stochastic policy reaches CK = 0.65 during
  training, but the DETERMINISTIC (argmax) evaluation returns CK = 0.35 --
  the same as a controller that never moves.

HYPOTHESIS
  The actor is shared.  With a near-uniform policy (entropy ~1.61 of a
  maximum ln 6 = 1.79) and a common team reward, the argmax action is
  likely to be THE SAME for every UAV, because their observations are
  similar.  The swarm then translates as a rigid blob and never disperses.
  Sampling breaks the symmetry by accident, which is why the stochastic
  policy does better.

  This is the parameter-sharing symmetry problem: Foerster et al. require
  each agent's own observation to identify it so that a shared network can
  still specialise.  With an identical initial blob, the observations are
  nearly identical and the specialisation has no basis.

MEASUREMENT
  1. deterministic vs stochastic evaluation
  2. the number of DISTINCT actions chosen by the N agents under each
  3. the spread of the swarm (mean distance from the centroid) over time

Run:  python analysis/symmetry_check.py [--episodes 25]
"""

from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import torch

from uav_wireless.env import SimConfig, UAVIoTEnv
from uav_wireless.experiments import eval_agent
from uav_wireless.train import train_mappo

HERE = os.path.dirname(os.path.abspath(__file__))


def action_diversity(agent, cfg, seed=0, steps=200, deterministic=True):
    """How many distinct actions do the N agents choose, and how spread out
    does the swarm get?"""
    import copy
    c = copy.deepcopy(cfg)
    c.seed = seed
    env = UAVIoTEnv(c)
    obs, st = env.reset()
    distinct = []
    spreads = []
    for _ in range(steps):
        mask = np.stack(env.action_masks())
        for i in range(c.N):
            if mask[i].sum() == 0:
                mask[i, 0] = True
        acts = agent.act(obs, mask, deterministic=deterministic)
        distinct.append(len(set(acts.tolist())))
        spreads.append(float(np.mean(np.linalg.norm(
            env.p - env.p.mean(axis=0), axis=1))))
        obs, st, r, done, _ = env.step(acts)
        if done:
            break
    return (float(np.mean(distinct)), float(np.mean(spreads)),
            float(np.max(spreads)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=int, default=25)
    args = ap.parse_args()

    cfg = SimConfig(N=8, K=2, R_cov=35.0, M=20, episode_len=400, seed=0,
                     start_clustered=True)
    print("=" * 78)
    print(" SYMMETRY CHECK -- clustered start, N=8, K=2")
    print("=" * 78)

    for use_id in (False, True):
        name = ("with agent identity" if use_id
                else "without agent identity (current Eq. 4)")
        c = SimConfig(**{**cfg.dict(), "seed": 0, "use_agent_id": use_id})
        agent, hist = train_mappo(c, episodes=args.episodes, n_steps=400,
                                  seed=0, verbose=False)
        print(f"\n--- {name} ---")
        print(f"  training CK: best={max(h['CK'] for h in hist):.3f} "
              f"final={hist[-1]['CK']:.3f}  "
              f"entropy={np.mean([h['entropy'] for h in hist[-5:]]):.3f}")
        for det in (True, False):
            evs = [eval_agent(agent, c, steps=c.episode_len, seed=s,
                              deterministic=det) for s in range(3)]
            ck = sum(e["CK"] for e in evs) / 3
            ag = sum(e["AG"] for e in evs) / 3
            sc = sum(e["SC"] for e in evs) / 3
            nd, sp, spmax = action_diversity(agent, c, seed=0,
                                             deterministic=det)
            print(f"  eval deterministic={str(det):5s}  CK={ck:.3f} AG={ag:.3f} "
                  f"SC={sc:.3f}   distinct actions/agent={nd:.2f}/8  "
                  f"mean spread={sp:6.1f} m  max spread={spmax:6.1f} m")

    print("\nThe distinct-action count is the diagnostic: with a shared actor "
          "and a\nshared reward, the deterministic policy tends to pick the "
          "SAME action for\nevery UAV, so the swarm translates as a rigid "
          "blob and never disperses.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
