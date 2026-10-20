"""
A/B: does the observation have to identify the agent?

HYPOTHESIS
  The paper justifies parameter sharing with Foerster et al. (AAMAS 2016):
  a shared network is sound only if each agent's own observation identifies
  it, so that the shared network can still specialise.  The observation of
  Eq. (4) carries position, velocity, battery, mode, the neighbour slots
  and the tail features -- but no identity.  In a symmetric deployment every
  agent therefore receives (almost) the same input, and the deterministic
  policy picks the SAME action for all of them: the swarm translates as a
  rigid blob and never disperses.  Measured on the dynamic simulator: 1.00
  distinct actions out of 8, and a swarm spread frozen at its initial value.

  Adding a one-hot agent identity to the observation should restore the
  specialisation the sharing argument depends on.

PROTOCOL
  Identical seeds, identical budget, identical evaluation seeds.  The only
  difference is whether the observation carries the identity.

Run:  python analysis/ab_agent_id.py [--episodes 40] [--seeds 3]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np

from uav_wireless.env import SimConfig
from uav_wireless.experiments import eval_agent
from uav_wireless.train import train_mappo

HERE = os.path.dirname(os.path.abspath(__file__))


def distinct_actions(agent, cfg, seed=0, steps=200, deterministic=True):
    """How many DISTINCT actions do the N agents choose, and how far does
    the swarm spread from its centroid?  Both are the direct symptoms of the
    symmetry problem."""
    import copy
    c = copy.deepcopy(cfg)
    c.seed = seed
    from uav_wireless.env import UAVIoTEnv
    from uav_wireless.seeding import seed_evaluation
    seed_evaluation(seed)
    env = UAVIoTEnv(c)
    obs, st = env.reset()
    distinct, spreads = [], []
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
    return float(np.mean(distinct)), float(np.mean(spreads)), float(np.max(spreads))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=int, default=40)
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--eval-seeds", type=int, default=3)
    args = ap.parse_args()

    base = SimConfig(N=8, K=2, R_cov=35.0, M=20, episode_len=400, seed=0,
                     start_clustered=True)
    arms = [("no agent identity", False), ("agent identity", True)]

    print("=" * 78)
    print(" A/B: agent identity in the observation")
    print(f" clustered start, N=8, K=2, R_cov=35, M=20, {args.episodes} "
          f"episodes x 400 steps, {args.seeds} training seeds, "
          f"{args.eval_seeds} eval seeds")
    print("=" * 78)

    rows = []
    for name, use_id in arms:
        print(f"\n--- {name} ---", flush=True)
        cks, ags, scs, cis, nds, sps = [], [], [], [], [], []
        for s in range(args.seeds):
            t0 = time.time()
            c = SimConfig(**{**base.dict(), "seed": s, "use_agent_id": use_id})
            agent, hist = train_mappo(c, episodes=args.episodes, n_steps=400,
                                      seed=s, verbose=False)
            evs = [eval_agent(agent, c, steps=c.episode_len, seed=e)
                   for e in range(args.eval_seeds)]
            agg = {k: float(np.mean([x[k] for x in evs])) for k in evs[0]}
            nd, sp, spmax = distinct_actions(agent, c, seed=0,
                                             deterministic=True)
            cks.append(agg["CK"]); ags.append(agg["AG"]); scs.append(agg["SC"])
            cis.append(agg["CovIntegral"]); nds.append(nd); sps.append(sp)
            print(f"  seed {s}: CK={agg['CK']:.3f} AG={agg['AG']:.3f} "
                  f"SC={agg['SC']:.3f} CI={agg['CovIntegral']:.3f} "
                  f"distinct={nd:.2f}/8 spread={sp:5.1f} m "
                  f"best_ck={max(h['CK'] for h in hist):.3f} "
                  f"({time.time()-t0:.0f}s)", flush=True)
        print(f"  {name:20s} CK={np.mean(cks):.3f}±{np.std(cks):.3f} "
              f"AG={np.mean(ags):.3f} SC={np.mean(scs):.3f} "
              f"CI={np.mean(cis):.3f} distinct={np.mean(nds):.2f}/8 "
              f"spread={np.mean(sps):.1f} m", flush=True)
        rows.append(dict(arm=name, use_agent_id=use_id,
                         CK=float(np.mean(cks)), CK_std=float(np.std(cks)),
                         AG=float(np.mean(ags)), SC=float(np.mean(scs)),
                         CovIntegral=float(np.mean(cis)),
                         distinct_actions=float(np.mean(nds)),
                         mean_spread_m=float(np.mean(sps)),
                         per_seed_CK=cks))

    out = os.path.join(HERE, "ab_agent_id.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)
    print(f"\nSaved -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
