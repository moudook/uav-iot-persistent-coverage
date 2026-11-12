"""
A/B: does the policy need to be sharper to deploy?

DIAGNOSIS
  In the clustered deployment the trained actor stays near-uniform (entropy
  1.2-1.5 against a maximum of ln 6 = 1.79), and the deterministic (argmax)
  policy picks the SAME action for every UAV, so the swarm translates as a
  rigid body and never disperses (measured: 1.7 distinct actions out of 8,
  swarm spread frozen at its initial value).  The sampled policy disperses
  by chance rather than by design.

  Two candidate causes and one candidate fix are separated here:

    (a) the exploration bonus is too large, so the policy never commits;
    (b) the shared team reward gives every agent the same advantage, so
        there is no per-agent credit to sharpen against.

  This script varies only the entropy coefficient.  If (a) is the cause, a
  smaller coefficient sharpens the policy, raises the number of distinct
  actions under the argmax policy, spreads the swarm, and improves the
  coverage.  If the coefficient makes no difference, the cause is (b) and
  the fix has to be in the credit assignment, not in the exploration.

Run:  python analysis/ab_entropy.py [--episodes 20] [--seeds 2]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import torch

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
    args = ap.parse_args()

    base = base_config()
    arms = [("ent=0.010 (current)", 0.010), ("ent=0.001 (sharper)", 0.001)]

    print("=" * 84)
    print(" A/B: the entropy coefficient of the proposed policy")
    print(f" clustered start, {args.episodes} episodes x {base.episode_len} "
          f"steps, {args.seeds} training seeds, {args.eval_seeds} eval seeds")
    print("=" * 84)

    rows = []
    for name, ec in arms:
        print(f"\n--- {name} ---", flush=True)
        cks, ags, scs, cis, nds, sps, ents, bests = ([] for _ in range(8))
        for s in range(args.seeds):
            t0 = time.time()
            c = base_config(seed=s)
            agent, hist = train_mappo(c, episodes=args.episodes,
                                      n_steps=c.episode_len, seed=s,
                                      verbose=False, ent_coef=ec)
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
        ck_std = float(np.std(cks, ddof=1)) if len(cks) > 1 else 0.0
        print(f"  {name:22s} CK={np.mean(cks):.3f}±{ck_std:.3f} "
              f"AG={np.mean(ags):.3f} SC={np.mean(scs):.3f} "
              f"CI={np.mean(cis):.3f} entropy={np.mean(ents):.3f} "
              f"distinct(argmax)={np.mean(nds):.2f}/8 "
              f"spread={np.mean(sps):.1f} m best_ck={np.mean(bests):.3f}",
              flush=True)
        rows.append(dict(arm=name, ent_coef=ec,
                         CK=float(np.mean(cks)), CK_std=ck_std,
                         AG=float(np.mean(ags)), SC=float(np.mean(scs)),
                         CovIntegral=float(np.mean(cis)),
                         entropy=float(np.mean(ents)),
                         distinct_actions=float(np.mean(nds)),
                         mean_spread_m=float(np.mean(sps)),
                         best_ck=float(np.mean(bests)),
                         per_seed_CK=cks))

    out = os.path.join(HERE, "ab_entropy.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)
    print(f"\nSaved -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
