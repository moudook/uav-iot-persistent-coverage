"""
Full experiment matrix, one reproducible run.

Run:  python run_all.py [--quick] [--stage STAGE]

Stages (all write their artefacts into the ml_impl directory):
    obs       A/B/C: what the local observation must contain
    base      base comparison: rule baselines vs the proposed MAPPO
    abl       component ablation on the base configuration and on S8
    scen      S1..S9 design matrix
    all       every stage, in that order

Artefacts:
    mappo_base.pt                 the trained policy of the base configuration
    hist_base.json                training curve of the base policy
    results_main.csv              base comparison
    results_ablation.csv          ablation on the base configuration
    results_ablation_stress.csv   ablation on the S8 combined-stress scenario
    results_scenarios.csv         S1..S9 design matrix
    analysis/ab_observation.json  the A/B/C numbers
    analysis/dormancy.json        plasticity probe of the trained actor

Every configuration is built from experiments.base_config(), so the numbers
in the paper, the numbers in the CSVs and the numbers in the audit all
describe the same experiment.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import torch

from uav_wireless.env import UAVIoTEnv
from uav_wireless.experiments import (base_config, run_base_comparison,
                                       run_ablation, run_scenarios,
                                       run_learned_baselines)
from uav_wireless.mappo import MAPPO
from uav_wireless.train import train_mappo, collect_rollout

HERE = os.path.dirname(os.path.abspath(__file__))
ANALYSIS = os.path.join(HERE, "analysis")


def stage_observation(episodes, seeds, eval_seeds):
    """A/B/C: identity, coverage-map summary, pad bearing."""
    from analysis.ab_observation import main as ab_main
    sys.argv = ["ab_observation", "--episodes", str(episodes),
                "--seeds", str(seeds), "--eval-seeds", str(eval_seeds)]
    return ab_main()

def stage_base(episodes, train_seeds, eval_seeds):
    cfg = base_config()
    print("=" * 78)
    print(f" BASE COMPARISON  N={cfg.N} K={cfg.K} M={cfg.M} "
          f"episode={cfg.episode_len} steps")
    print(f" training: {episodes} episodes x {train_seeds} seeds; "
          f"evaluation: {eval_seeds} seeds")
    print("=" * 78, flush=True)
    rows = []
    for s in range(train_seeds):
        t0 = time.time()
        c = base_config(seed=s)
        agent, hist = train_mappo(c, episodes=episodes, n_steps=c.episode_len,
                                  seed=s, log_every=max(1, episodes // 5),
                                  verbose=True)
        if s == 0:
            agent.save("mappo_base.pt")
            with open("hist_base.json", "w", encoding="utf-8") as f:
                json.dump(hist, f, indent=2)
        evs = [__import__("uav_wireless.experiments", fromlist=["eval_agent"])
               .eval_agent(agent, c, steps=c.episode_len, seed=e)
               for e in range(eval_seeds)]
        agg = {k: float(np.mean([x[k] for x in evs])) for k in evs[0]}
        std = {k: float(np.std([x[k] for x in evs])) for k in evs[0]}
        # the per-seed rows are written as they are produced, so that an
        # interrupted run does not throw away the training it has already done
        with open(os.path.join(ANALYSIS, "base_seed_rows.jsonl"), "a",
                  encoding="utf-8") as f:
            f.write(json.dumps(dict(train_seed=s,
                                    **{k: agg[k] for k in
                                       ("CK", "AG", "SC", "CovIntegral")},
                                    **{f"{k}_std": std[k]
                                       for k in ("CK", "AG", "SC")},
                                    per_seed=[{k: x[k] for k in
                                               ("CK", "AG", "SC")}
                                              for x in evs])) + "\n")
        print(f"  seed {s}: CK={agg['CK']:.3f}±{std['CK']:.3f} "
              f"AG={agg['AG']:.3f} SC={agg['SC']:.3f} "
              f"CI={agg['CovIntegral']:.3f} "
              f"best_ck={max(h['CK'] for h in hist):.3f} "
              f"({time.time()-t0:.0f}s)", flush=True)
        rows.append(dict(train_seed=s, **{k: agg[k] for k in
                                          ("CK", "AG", "SC", "CovIntegral")},
                         **{f"{k}_std": std[k] for k in ("CK", "AG", "SC")},
                         best_ck=float(max(h["CK"] for h in hist)),
                         final_ck=float(hist[-1]["CK"])))
    out = os.path.join(ANALYSIS, "base_training_seeds.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)
    print(f"  saved -> {out}\n", flush=True)
    return rows


def stage_dormancy():
    """Plasticity probe of the trained actor."""
    ck = os.path.join(HERE, "mappo_base.pt")
    if not os.path.exists(ck):
        print("  no trained policy yet; skipping the plasticity probe")
        return
    from analysis.dormancy import probe, summarise
    cfg = base_config()
    env = UAVIoTEnv(cfg)
    agent = MAPPO(n_agents=cfg.N, obs_dim=env.obs_dim,
                   state_dim=env.state_dim)
    agent.load(ck)
    batch, _ = collect_rollout(env, agent, n_steps=200)
    rows = summarise(probe(agent, batch))
    out = os.path.join(ANALYSIS, "dormancy.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)
    for r in rows:
        print(f"  {r['layer']}: dormant={r['dormant_frac_0.01']:.3f} "
              f"silent={r['silent_frac_0.01']:.3f} "
              f"dead={r['dead_frac_0.01']:.3f}")
    print(f"  saved -> {out}\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--stage", default="all",
                    choices=["obs", "base", "abl", "learned", "energy", "scen", "all"])
    args = ap.parse_args()

    quick = args.quick
    episodes = 6 if quick else 30
    train_seeds = 2 if quick else 5
    eval_seeds = 2 if quick else 5
    abl_episodes = 3 if quick else 12
    stress_episodes = 2 if quick else 8
    obs_seeds = 2 if quick else 2

    t0 = time.time()
    print("=" * 78)
    print(" UAV-IoT PERSISTENT COVERAGE -- FULL EXPERIMENT MATRIX")
    c = base_config()
    print(f" config: N={c.N} K={c.K} R_cov={c.R_cov} M={c.M} "
          f"episode={c.episode_len} steps  B_max={c.B_max:.0f} J")
    print(f" episodes={episodes} train_seeds={train_seeds} "
          f"eval_seeds={eval_seeds}")
    print("=" * 78 + "\n", flush=True)

    if args.stage in ("obs", "all"):
        print("[1/6] observation A/B/C ...", flush=True)
        stage_observation(episodes, obs_seeds, eval_seeds)
        print()

    if args.stage in ("base", "all"):
        print("[2/6] base comparison ...", flush=True)
        stage_base(episodes, train_seeds, eval_seeds)
        stage_dormancy()
        # the rule baselines on the same scenes
        from uav_wireless.experiments import run_base_comparison
        cfg = base_config()
        agent = MAPPO(n_agents=cfg.N, obs_dim=UAVIoTEnv(cfg).obs_dim,
                       state_dim=UAVIoTEnv(cfg).state_dim)
        agent.load("mappo_base.pt")
        run_base_comparison(cfg, "results_main.csv", eval_seeds=eval_seeds,
                            train=False, agent=agent)
        print()

    if args.stage in ("abl", "all"):
        print("[3/6] ablations ...", flush=True)
        cfg = base_config()
        run_ablation(cfg, "results_ablation.csv", stress=False,
                     episodes=abl_episodes)
        print()
        run_ablation(cfg, "results_ablation_stress.csv", stress=True,
                     episodes=stress_episodes)
        print()

    if args.stage in ("learned", "all"):
        print("[4/6] learned baselines (Table VI) ...", flush=True)
        # The learned baselines get the SAME episode budget as the proposed
        # method, so that the comparison is a comparison of learning
        # machinery and not of budgets.
        run_learned_baselines(base_config(), "results_learned_baselines.csv",
                              episodes=episodes, eval_seeds=eval_seeds,
                              seeds=2 if quick else 3)
        print()

    if args.stage in ("energy", "all"):
        print("[5/6] the energy-management diagnosis ...", flush=True)
        from analysis.ab_energy_management import main as em_main
        sys.argv = ["ab_energy_management", "--episodes", str(episodes),
                    "--seeds", str(obs_seeds), "--eval-seeds", str(eval_seeds)]
        em_main()
        print()

    if args.stage in ("scen", "all"):
        print("[6/6] scenario matrix ...", flush=True)
        run_scenarios(base_config(), "results_scenarios.csv",
                      episodes=abl_episodes)
        print()

    print("=" * 78)
    print(f" DONE in {time.time() - t0:.0f} s")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
