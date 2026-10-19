"""
Full experiment matrix, in one reproducible run.

Run:  python run_all.py [--quick]

Produces, in the ml_impl directory:
    mappo_base.pt              trained MAPPO policy (feasible config)
    hist_base.json             training curve
    results_main.csv           baselines vs MAPPO, 5 seeds
    results_ablation.csv       component ablation, S8 combined stress
    results_ablation_feasible.csv   component ablation, feasible base config
    results_scenarios.csv      S1..S8 design matrix, every variant
    dormancy.json              plasticity probe of the trained actor

Every baseline honours the seed it is given, and the environment reports
termination separately from truncation, so the GAE bootstrap is correct at
every episode boundary.
"""

from __future__ import annotations

import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import torch

from uav_wireless import SimConfig
from uav_wireless.experiments import (run_base_comparison, run_ablation,
                                       run_scenarios)
from uav_wireless.env import UAVIoTEnv
from uav_wireless.mappo import MAPPO
from uav_wireless.train import train_mappo


def base_cfg():
    """Feasible configuration: N=8 meets the corner-packing bound N>=4K=8."""
    return SimConfig(N=8, K=2, R_cov=35.0, episode_len=400, seed=0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true",
                    help="shorter training and fewer evaluation seeds")
    args = ap.parse_args()

    quick = args.quick
    cfg = base_cfg()
    episodes = 20 if quick else 50
    n_steps = 400
    eval_seeds = 2 if quick else 5

    t0 = time.time()
    print("=" * 78)
    print(" UAV-IoT PERSISTENT COVERAGE -- FULL EXPERIMENT MATRIX")
    print(f" config: N={cfg.N} K={cfg.K} R_cov={cfg.R_cov} "
          f"episode_len={cfg.episode_len}  episodes={episodes}  "
          f"eval seeds={eval_seeds}")
    print("=" * 78 + "\n")

    # ---- 1. train the proposed policy --------------------------------
    print("[1/5] training MAPPO on the feasible configuration ...", flush=True)
    agent, hist = train_mappo(cfg, episodes=episodes, n_steps=n_steps,
                               seed=0, log_every=max(1, episodes // 5),
                               verbose=True)
    agent.save("mappo_base.pt")
    import json
    with open("hist_base.json", "w") as f:
        json.dump(hist, f)
    best = max(h["CK"] for h in hist)
    print(f"      done: {len(hist)} episodes, best CK={best:.3f}, "
          f"final CK={hist[-1]['CK']:.3f}\n", flush=True)

    # ---- 2. plasticity probe ----------------------------------------
    print("[2/5] plasticity probe of the trained actor ...", flush=True)
    try:
        from analysis.dormancy import probe, summarise
        from uav_wireless.train import collect_rollout
        env = UAVIoTEnv(cfg)
        batch, _ = collect_rollout(env, agent, n_steps=200)
        rows = summarise(probe(agent, batch))
        with open(os.path.join("analysis", "dormancy.json"), "w") as f:
            json.dump(rows, f, indent=2)
        for r in rows:
            print(f"      {r['layer']}: dormant={r['dormant_frac_0.01']:.3f} "
                  f"silent={r['silent_frac_0.01']:.3f} "
                  f"dead={r['dead_frac_0.01']:.3f}", flush=True)
    except Exception as exc:  # pragma: no cover
        print(f"      skipped: {exc}")
    print()

    # ---- 3. base comparison -----------------------------------------
    print("[3/5] base comparison (baselines vs MAPPO) ...", flush=True)
    run_base_comparison(cfg, "results_main.csv", eval_seeds=eval_seeds,
                        train=False, agent=agent)
    print()

    # ---- 4. ablations ------------------------------------------------
    print("[4/5] ablation on the S8 combined-stress scenario ...", flush=True)
    run_ablation(cfg, "results_ablation.csv", stress=True)
    print()
    print("[4b/5] ablation on the feasible base configuration ...", flush=True)
    run_ablation(cfg, "results_ablation_feasible.csv", stress=False)
    print()

    # ---- 5. scenario matrix ------------------------------------------
    print("[5/5] S1..S8 design matrix ...", flush=True)
    run_scenarios(cfg, "results_scenarios.csv")
    print()

    print("=" * 78)
    print(f" ALL DONE in {time.time() - t0:.0f} s")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
