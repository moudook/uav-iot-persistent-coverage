"""
Controlled A/B: does per-agent advantage normalisation help?

HYPOTHESIS
  With a shared team reward, every agent receives the SAME advantage, so the
  policy gradient cannot distinguish an agent whose action helped from one
  whose action was irrelevant.  Normalising each agent's advantages over its
  own history gives every agent a signal relative to its own behaviour
  instead of to the pooled batch, and should therefore sharpen the shared
  policy and improve the coverage/connectivity trade-off.  Generalised
  per-agent advantage estimation (Kim et al., AAMAS 2026) addresses the same
  problem for the multi-agent case.

PROTOCOL
  Identical seeds, identical budget, identical evaluation seeds.  Only the
  advantage normalisation differs.  The baseline arm is the configuration
  used for every number reported in the paper.

Run:  python analysis/ab_per_agent_adv.py [--episodes 30] [--seeds 3]
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

from uav_wireless.env import SimConfig, UAVIoTEnv
from uav_wireless.mappo import MAPPO
from uav_wireless.train import train_mappo
from uav_wireless.experiments import eval_agent

HERE = os.path.dirname(os.path.abspath(__file__))


def run_arm(name, cfg, episodes, seeds, per_agent, ent_coef):
    rows = []
    for s in range(seeds):
        t0 = time.time()
        c = SimConfig(**{**cfg.dict(), "seed": s})
        agent, hist = train_mappo(c, episodes=episodes, n_steps=400, seed=s,
                                  verbose=False,
                                  per_agent_adv_norm=per_agent,
                                  ent_coef=ent_coef)
        evs = [eval_agent(agent, c, steps=c.episode_len, seed=e)
               for e in range(3)]
        agg = {k: float(np.mean([e[k] for e in evs])) for k in evs[0]}
        ent = float(np.mean([h["entropy"] for h in hist[-5:]]))
        rows.append(dict(arm=name, seed=s, **{k: agg[k] for k in
                                              ("CK", "AG", "SC", "CovIntegral")},
                         entropy=ent, best_ck=float(max(h["CK"] for h in hist)),
                         final_ck=float(hist[-1]["CK"]),
                         seconds=time.time() - t0))
        print(f"  {name:16s} seed {s}: CK={agg['CK']:.3f} AG={agg['AG']:.3f} "
              f"SC={agg['SC']:.3f} CI={agg['CovIntegral']:.3f} "
              f"ent={ent:.3f} best_ck={rows[-1]['best_ck']:.3f} "
              f"({rows[-1]['seconds']:.0f}s)", flush=True)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=int, default=30)
    ap.add_argument("--seeds", type=int, default=3)
    args = ap.parse_args()

    base = SimConfig(N=8, K=2, R_cov=35.0, episode_len=400, seed=0)
    arms = [
        ("pooled-adv (base)", False, 0.01),
        ("per-agent-adv", True, 0.01),
    ]
    print("=" * 78)
    print(" A/B: advantage normalisation  (N=8, K=2, R_cov=35, "
          f"{args.episodes} episodes x 400 steps, {args.seeds} training seeds)")
    print("=" * 78)

    all_rows = []
    for name, pa, ec in arms:
        print(f"\n--- {name} ---", flush=True)
        all_rows += run_arm(name, base, args.episodes, args.seeds, pa, ec)

    print("\n" + "=" * 78)
    for name, _, _ in arms:
        rs = [r for r in all_rows if r["arm"] == name]
        ck = np.mean([r["CK"] for r in rs])
        sc = np.mean([r["SC"] for r in rs])
        ag = np.mean([r["AG"] for r in rs])
        ci = np.mean([r["CovIntegral"] for r in rs])
        ent = np.mean([r["entropy"] for r in rs])
        print(f" {name:18s} CK={ck:.3f} AG={ag:.3f} SC={sc:.3f} "
              f"CI={ci:.3f} entropy={ent:.3f}")
    print("=" * 78)

    out = os.path.join(HERE, "ab_per_agent_adv.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(all_rows, f, indent=2)
    print(f"Saved -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
