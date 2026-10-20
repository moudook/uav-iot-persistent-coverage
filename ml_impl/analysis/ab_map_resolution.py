"""
A/B: the resolution of the broadcast coverage map, and the fairness of the
comparison with the rule-based heuristic.

THE FAIRNESS PROBLEM
  The Reactive heuristic assigns UAVs to uncovered sensors using the EXACT
  set of under-covered sensors.  The learned policy receives a coarse
  G x G summary of where the deficit is, because a fixed-size summary is
  what a broadcast can carry.  The two therefore do not have the same
  information, and a coverage comparison between them is not on equal
  footing: some of the gap is an information gap, not a control gap.

  The observation of Eq. (4) states that the infrastructure aggregates the
  IoT service reports and broadcasts the summary, so the resolution of that
  summary is a design parameter of the framework, and it should be chosen
  by measurement rather than by assertion.

WHAT THIS MEASURES
  For G in {4, 6, 8, 12}: the coverage, the connectivity, the entropy of
  the policy, the number of distinct actions under the deterministic
  (argmax) policy, and the spread of the swarm.  The spread and the
  distinct-action count are the direct symptoms of the shared-actor
  symmetry problem, and they are what tells us whether a finer map lets the
  shared actor specialise.

Run:  python analysis/ab_map_resolution.py [--episodes 20] [--seeds 2]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np

from uav_wireless.experiments import base_config, eval_agent
from uav_wireless.train import train_mappo

HERE = os.path.dirname(os.path.abspath(__file__))


def distinct_actions(agent, cfg, seed=0, steps=200, deterministic=True):
    import copy
    from uav_wireless.env import UAVIoTEnv
    c = copy.deepcopy(cfg)
    c.seed = seed
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
    return float(np.mean(distinct)), float(np.mean(spreads))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=int, default=20)
    ap.add_argument("--seeds", type=int, default=2)
    ap.add_argument("--eval-seeds", type=int, default=3)
    ap.add_argument("--grids", default="4,6,8,12")
    args = ap.parse_args()

    grids = [int(g) for g in args.grids.split(",")]
    base = base_config()
    print("=" * 92)
    print(" A/B: the resolution of the broadcast coverage map")
    print(f" clustered start, {args.episodes} episodes x {base.episode_len} "
          f"steps, {args.seeds} training seeds, {args.eval_seeds} eval seeds")
    print("=" * 92)

    rows = []
    for G in grids:
        print(f"\n--- G = {G} ({G}x{G} cells, {G*G} values) ---", flush=True)
        cks, ags, scs, cis, nds, sps, ents, bests = ([] for _ in range(8))
        for s in range(args.seeds):
            t0 = time.time()
            c = base_config(seed=s, map_grid=G)
            agent, hist = train_mappo(c, episodes=args.episodes,
                                      n_steps=c.episode_len, seed=s,
                                      verbose=False)
            evs = [eval_agent(agent, c, steps=c.episode_len, seed=e)
                   for e in range(args.eval_seeds)]
            agg = {k: float(np.mean([x[k] for x in evs])) for k in evs[0]}
            nd, sp = distinct_actions(agent, c, seed=0, deterministic=True)
            cks.append(agg["CK"]); ags.append(agg["AG"]); scs.append(agg["SC"])
            cis.append(agg["CovIntegral"]); nds.append(nd); sps.append(sp)
            ents.append(float(np.mean([h["entropy"] for h in hist[-5:]])))
            bests.append(max(h["CK"] for h in hist))
            print(f"  seed {s}: CK={agg['CK']:.3f} AG={agg['AG']:.3f} "
                  f"SC={agg['SC']:.3f} CI={agg['CovIntegral']:.3f} "
                  f"ent={ents[-1]:.3f} distinct(argmax)={nd:.2f}/8 "
                  f"spread={sp:5.1f} m best_ck={bests[-1]:.3f} "
                  f"({time.time()-t0:.0f}s)", flush=True)
        print(f"  G={G:<3d} CK={np.mean(cks):.3f}±{np.std(cks):.3f} "
              f"AG={np.mean(ags):.3f} SC={np.mean(scs):.3f} "
              f"CI={np.mean(cis):.3f} entropy={np.mean(ents):.3f} "
              f"distinct(argmax)={np.mean(nds):.2f}/8 "
              f"spread={np.mean(sps):.1f} m best_ck={np.mean(bests):.3f}",
              flush=True)
        rows.append(dict(grid=G, n_cells=G * G,
                         CK=float(np.mean(cks)), CK_std=float(np.std(cks)),
                         AG=float(np.mean(ags)), SC=float(np.mean(scs)),
                         CovIntegral=float(np.mean(cis)),
                         entropy=float(np.mean(ents)),
                         distinct_actions=float(np.mean(nds)),
                         mean_spread_m=float(np.mean(sps)),
                         best_ck=float(np.mean(bests)),
                         per_seed_CK=cks))

    out = os.path.join(HERE, "ab_map_resolution.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)
    print(f"\nSaved -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
