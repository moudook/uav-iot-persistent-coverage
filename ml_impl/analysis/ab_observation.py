"""
A/B/C: what must the local observation contain for a shared policy to work?

BACKGROUND
  The paper justifies parameter sharing with Foerster et al. (AAMAS 2016):
  a shared network is sound only if each agent's own observation identifies
  it, so the shared network can still specialise.  Two things are missing
  from the observation of Eq. (4) as originally written.

  1. IDENTITY.  The observation carries position, velocity, battery, mode,
     the neighbour slots and the tail features, but no identity.  In a
     symmetric deployment every agent therefore receives (almost) the same
     input, and the deterministic policy picks the SAME action for all of
     them: the swarm translates as a rigid blob and never disperses.
     Measured on the dynamic simulator: 1.00 distinct actions out of 8, and a
     swarm spread frozen at its initial value.

  2. A COVERAGE-MAP SUMMARY.  The agent knows HOW MANY sensors it covers
     but not WHICH sensors are under-covered, so nothing in the observation
     points it towards the deficit and there is no gradient signal for
     deployment.  A G x G grid of the share of under-covered sensors per
     cell is the standard fix; the infrastructure that owns the charging
     pads also aggregates the IoT service reports and broadcasts it, so this
     is a communication assumption rather than an oracle.

ARMS
  A  local only                (Eq. (4) as written)
  B  + agent identity          (one-hot, length N)
  C  + agent identity + map    (4 x 4 coverage-map summary)

PROTOCOL
  Identical seeds, identical budget, identical evaluation seeds.  The rule
  baselines are evaluated on the same scenes for reference.

Run:  python analysis/ab_observation.py [--episodes 40] [--seeds 3]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np

from uav_wireless.env import SimConfig, UAVIoTEnv
from uav_wireless.experiments import base_config, eval_agent
from uav_wireless.train import (train_mappo, baseline_fixed, baseline_greedy,
                                 baseline_reactive)

HERE = os.path.dirname(os.path.abspath(__file__))


def distinct_actions(agent, cfg, seed=0, steps=200, deterministic=True):
    """How many DISTINCT actions do the N agents choose, and how far does the
    swarm spread from its centroid?  Both are the direct symptoms of the
    symmetry problem."""
    import copy
    c = copy.deepcopy(cfg)
    c.seed = seed
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
    return float(np.mean(distinct)), float(np.mean(spreads))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=int, default=40)
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--eval-seeds", type=int, default=3)
    args = ap.parse_args()

    base = base_config()
    arms = [
        ("A local only", dict(use_agent_id=False, map_grid=0,
                              use_pad_bearing=False)),
        ("B + identity", dict(use_agent_id=True, map_grid=0,
                              use_pad_bearing=False)),
        ("C + identity + map", dict(use_agent_id=True, map_grid=4,
                                    use_pad_bearing=True)),
    ]

    print("=" * 78)
    print(" A/B/C: what the local observation must contain")
    print(f" clustered start, N=8, K=2, R_cov=35, M=20, {args.episodes} "
          f"episodes x {base.episode_len} steps, {args.seeds} training seeds, "
          f"{args.eval_seeds} eval seeds")
    print("=" * 78)

    e = UAVIoTEnv(base)
    e.reset()
    nc = e.coverage_counts()
    print(f" initial: CK={np.mean(nc >= base.K):.3f}  "
          f"covered={int(np.sum(nc >= base.K))}/{base.M}  "
          f"connected={e.is_connected(e.comm_graph()[1])}\n")

    # --- reference: the rule-based baselines on the same scenes ---------
    print("--- rule-based baselines (reference) ---", flush=True)
    rows = []
    for name, fn in [("Fixed", baseline_fixed),
                     ("Greedy", baseline_greedy),
                     ("Reactive", baseline_reactive)]:
        evs = [fn(base, steps=base.episode_len, seed=s)
               for s in range(args.eval_seeds)]
        agg = {k: float(np.mean([x[k] for x in evs])) for k in evs[0]}
        std = {k: float(np.std([x[k] for x in evs])) for k in evs[0]}
        print(f"  {name:22s} CK={agg['CK']:.3f}±{std['CK']:.3f} "
              f"AG={agg['AG']:.3f} SC={agg['SC']:.3f} "
              f"CI={agg['CovIntegral']:.3f}", flush=True)
        rows.append(dict(arm=name, kind="baseline",
                         CK=agg["CK"], CK_std=std["CK"], AG=agg["AG"],
                         SC=agg["SC"], CovIntegral=agg["CovIntegral"]))

    # --- the three learned arms ----------------------------------------
    for name, delta in arms:
        print(f"--- {name} ---", flush=True)
        cks, ags, scs, cis, nds, sps, bests = [], [], [], [], [], [], []
        for s in range(args.seeds):
            t0 = time.time()
            c = SimConfig(**{**base.dict(), "seed": s, **delta})
            agent, hist = train_mappo(c, episodes=args.episodes,
                                      n_steps=c.episode_len,
                                      seed=s, verbose=False)
            evs = [eval_agent(agent, c, steps=c.episode_len, seed=e)
                   for e in range(args.eval_seeds)]
            agg = {k: float(np.mean([x[k] for x in evs])) for k in evs[0]}
            nd, sp = distinct_actions(agent, c, seed=0, deterministic=True)
            cks.append(agg["CK"]); ags.append(agg["AG"]); scs.append(agg["SC"])
            cis.append(agg["CovIntegral"]); nds.append(nd); sps.append(sp)
            bests.append(max(h["CK"] for h in hist))
            print(f"  seed {s}: CK={agg['CK']:.3f} AG={agg['AG']:.3f} "
                  f"SC={agg['SC']:.3f} CI={agg['CovIntegral']:.3f} "
                  f"distinct(argmax)={nd:.2f}/8 spread={sp:5.1f} m "
                  f"best_ck={bests[-1]:.3f} ({time.time()-t0:.0f}s)", flush=True)
        print(f"  {name:22s} CK={np.mean(cks):.3f}±{np.std(cks):.3f} "
              f"AG={np.mean(ags):.3f} SC={np.mean(scs):.3f} "
              f"CI={np.mean(cis):.3f} distinct(argmax)={np.mean(nds):.2f}/8 "
              f"spread={np.mean(sps):.1f} m best_ck={np.mean(bests):.3f}",
              flush=True)
        rows.append(dict(arm=name, kind="learned",
                         **{k: delta[k] for k in delta},
                         CK=float(np.mean(cks)), CK_std=float(np.std(cks)),
                         AG=float(np.mean(ags)), SC=float(np.mean(scs)),
                         CovIntegral=float(np.mean(cis)),
                         distinct_actions=float(np.mean(nds)),
                         mean_spread_m=float(np.mean(sps)),
                         best_ck=float(np.mean(bests)),
                         per_seed_CK=cks))

    out = os.path.join(HERE, "ab_observation.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)
    print(f"\nSaved -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
