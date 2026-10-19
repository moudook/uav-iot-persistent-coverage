"""
The decisive comparison, in a regime where the task has headroom.

WHY A SECOND REGIME
-------------------
With the default centred-ring deployment the swarm already covers 17 of 20
sensors at t=0, so every controller -- including one that never moves --
scores CK = 0.900 and the achievable range is roughly [0.9, 1.0].  A
comparison in that regime cannot separate the methods.

With `start_clustered=True` the swarm starts as a connected blob in one
corner: still connected at t=0, but covering only 3 of 20 sensors.  The
controller must deploy across the field and hold K=2 redundancy while
keeping the graph connected.  This is the standard persistent-coverage
benchmark arrangement and it is the regime in which the connectivity
constraint and the feasibility mask actually bind.

ARMS
  Fixed / Greedy / Reactive      rule-based baselines
  MAPPO (pooled advantage)       the configuration reported in the paper
  MAPPO (per-agent advantage)    the credit-assignment variant

Run:  python analysis/clustered_comparison.py [--episodes 40] [--seeds 3]
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
from uav_wireless.train import (train_mappo, baseline_fixed, baseline_greedy,
                                 baseline_reactive)

HERE = os.path.dirname(os.path.abspath(__file__))


def base_cfg():
    return SimConfig(N=8, K=2, R_cov=35.0, M=20, episode_len=400, seed=0,
                     start_clustered=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=int, default=40)
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--eval-seeds", type=int, default=3)
    args = ap.parse_args()

    cfg = base_cfg()
    print("=" * 78)
    print(" CLUSTERED-START COMPARISON  (N=8, K=2, R_cov=35, M=20, "
          "start_clustered=True)")
    print(f" training: {args.episodes} episodes x 400 steps x {args.seeds} "
          f"seeds;  evaluation: {args.eval_seeds} seeds")
    print("=" * 78)

    # --- initial state, so the reader can see the headroom --------------
    from uav_wireless.env import UAVIoTEnv
    e = UAVIoTEnv(cfg)
    e.reset()
    nc = e.coverage_counts()
    act, adj, _ = e.comm_graph()
    print(f" initial state: CK={np.mean(nc >= cfg.K):.3f}  "
          f"connected={e.is_connected(adj)}  "
          f"sensors with K coverage: {int(np.sum(nc >= cfg.K))}/{cfg.M}\n")

    rows = []

    # --- rule-based baselines ------------------------------------------
    print("--- rule-based baselines ---", flush=True)
    for name, fn in [("Fixed", baseline_fixed),
                     ("Greedy", baseline_greedy),
                     ("Reactive", baseline_reactive)]:
        evs = [fn(cfg, steps=cfg.episode_len, seed=s)
               for s in range(args.eval_seeds)]
        agg = {k: float(np.mean([x[k] for x in evs])) for k in evs[0]}
        std = {k: float(np.std([x[k] for x in evs])) for k in evs[0]}
        print(f"  {name:22s} CK={agg['CK']:.3f}±{std['CK']:.3f} "
              f"AG={agg['AG']:.3f} SC={agg['SC']:.3f} "
              f"CI={agg['CovIntegral']:.3f}", flush=True)
        rows.append(dict(model=name, train_seeds=0,
                         **{k: agg[k] for k in ("CK", "AG", "SC", "CovIntegral")},
                         **{f"{k}_std": std[k] for k in ("CK", "AG", "SC")}))

    # --- learned policies ----------------------------------------------
    for name, per_agent in (("MAPPO (pooled adv)", False),
                            ("MAPPO (per-agent adv)", True)):
        print(f"--- {name} ---", flush=True)
        cks, ags, scs, cis, ents = [], [], [], [], []
        for s in range(args.seeds):
            t0 = time.time()
            c = SimConfig(**{**cfg.dict(), "seed": s})
            agent, hist = train_mappo(c, episodes=args.episodes, n_steps=400,
                                      seed=s, verbose=False,
                                      per_agent_adv_norm=per_agent)
            evs = [eval_agent(agent, c, steps=c.episode_len, seed=e)
                   for e in range(args.eval_seeds)]
            agg = {k: float(np.mean([x[k] for x in evs])) for k in evs[0]}
            cks.append(agg["CK"]); ags.append(agg["AG"])
            scs.append(agg["SC"]); cis.append(agg["CovIntegral"])
            ents.append(float(np.mean([h["entropy"] for h in hist[-5:]])))
            print(f"  seed {s}: CK={agg['CK']:.3f} AG={agg['AG']:.3f} "
                  f"SC={agg['SC']:.3f} CI={agg['CovIntegral']:.3f} "
                  f"best_ck={max(h['CK'] for h in hist):.3f} "
                  f"ent={ents[-1]:.3f} ({time.time()-t0:.0f}s)", flush=True)
        print(f"  {name:22s} CK={np.mean(cks):.3f}±{np.std(cks):.3f} "
              f"AG={np.mean(ags):.3f} SC={np.mean(scs):.3f} "
              f"CI={np.mean(cis):.3f} entropy={np.mean(ents):.3f}", flush=True)
        rows.append(dict(model=name, train_seeds=args.seeds,
                         CK=float(np.mean(cks)), AG=float(np.mean(ags)),
                         SC=float(np.mean(scs)),
                         CovIntegral=float(np.mean(cis)),
                         CK_std=float(np.std(cks)),
                         AG_std=float(np.std(ags)),
                         SC_std=float(np.std(scs)),
                         entropy=float(np.mean(ents))))

    out = os.path.join(HERE, "clustered_comparison.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)
    print(f"\nSaved -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
