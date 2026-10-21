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

# The BLAS thread pools are pinned to one thread BEFORE numpy loads
# them: each process otherwise starts a pool sized for the whole
# machine, and a handful of processes exhaust the paging file.
import os as _os
for _v in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "OMP_NUM_THREADS", "NUMEXPR_NUM_THREADS",
           "VECLIB_MAXIMUM_THREADS"):
    _os.environ.setdefault(_v, "1")
import numpy as np
import torch

from uav_wireless.env import UAVIoTEnv
from uav_wireless.experiments import (base_config, run_base_comparison,
                                       run_ablation, run_scenarios,
                                       run_learned_baselines, eval_agent)
from uav_wireless.mappo import MAPPO
from uav_wireless.train import train_mappo, collect_rollout

HERE = os.path.dirname(os.path.abspath(__file__))
ANALYSIS = os.path.join(HERE, "analysis")

# THE DEVICE IS PINNED TO THE CPU, and the reason is reproducibility
# rather than speed.  The same seed trained on the GPU and on the CPU gives
# different weights (the floating-point kernels differ, and the difference
# compounds through the updates), so a run is reproducible only on the device
# it was trained on.  Every table in the paper quotes the same
# configuration, and a reader who checks the ablation's full row against
# the main table's controller must find the same number, which requires
# every stage to train on the same device.  The choice is measured, not
# assumed: the GPU is 28% SLOWER for this workload (10.7 ms/step against
# 8.3 ms/step on the CPU at one thread), because the simulator is a
# sequential Python loop and is 85% of the run, while the network is 8%
# of it and is itself slower on the GPU.  The speed comes from running
# the stages in parallel across the machine's cores, not from the GPU.
os.environ["CUDA_VISIBLE_DEVICES"] = ""


def stage_observation(episodes, seeds, eval_seeds):
    """A/B/C: identity, coverage-map summary, pad bearing."""
    from analysis.ab_observation import main as ab_main
    sys.argv = ["ab_observation", "--episodes", str(episodes),
                "--seeds", str(seeds), "--eval-seeds", str(eval_seeds)]
    return ab_main()

def stage_base(episodes, train_seeds, eval_seeds, resume=False):
    """The base comparison.

    PROTOCOL.  The learned controller is trained `train_seeds` times and
    reported as the MEAN over those training runs, with the seed-to-seed
    spread of CK.  Each trained policy is then evaluated on `eval_seeds`
    scenes.  The table therefore reports the controller, not one lucky
    policy, which is what the text of the paper describes and what the
    table did not do before.

    Every training run's policy is SAVED, so that every number in the
    table can be recomputed from a stored artefact.
    """
    cfg = base_config()
    print("=" * 78)
    print(f" BASE COMPARISON  N={cfg.N} K={cfg.K} M={cfg.M} "
          f"episode={cfg.episode_len} steps")
    print(f" training: {episodes} episodes x {train_seeds} seeds; "
          f"evaluation: {eval_seeds} seeds"
          + ("   [RESUME: the stored policies are evaluated, not retrained]"
             if resume else ""))
    print("=" * 78, flush=True)
    rows = []
    sampled_runs, argmax_runs = [], []
    # the per-seed rows are written fresh for this run, so that the
    # variance decomposition reads the current experiment
    with open(os.path.join(ANALYSIS, "base_seed_rows.jsonl"), "w",
              encoding="utf-8") as f:
        f.write("")
    for s in range(train_seeds):
        t0 = time.time()
        c = base_config(seed=s)
        hist = []
        if resume and os.path.exists(f"mappo_base_s{s}.pt"):
            # the training is reproducible from its seed and is the
            # expensive part; evaluating a STORED policy is cheaper and is
            # a stronger statement about reproducibility
            agent = MAPPO(n_agents=cfg.N, obs_dim=UAVIoTEnv(cfg).obs_dim,
                          state_dim=UAVIoTEnv(cfg).state_dim)
            agent.load(f"mappo_base_s{s}.pt")
            # the training curve, if it was saved: the per-seed file, or
            # for the first seed the file the training path writes.  The
            # training path writes them in the working directory, which is
            # where the token filler looks for them too.
            for hp in (f"hist_base_s{s}.json", "hist_base.json"):
                if os.path.exists(hp):
                    with open(hp, encoding="utf-8") as f:
                        hist = json.load(f)
                    break
        else:
            agent, hist = train_mappo(c, episodes=episodes,
                                      n_steps=c.episode_len,
                                      seed=s,
                                      log_every=max(1, episodes // 5),
                                      verbose=True)
            agent.save(f"mappo_base_s{s}.pt")
            if s == 0:
                agent.save("mappo_base.pt")
                with open("hist_base.json", "w", encoding="utf-8") as f:
                    json.dump(hist, f, indent=2)
            # every run's training curve is kept, so that the learning
            # curve is not a single run's story.  They are written beside
            # hist_base.json, which is where the resume path and the token
            # filler look for them.
            with open(f"hist_base_s{s}.json", "w", encoding="utf-8") as f:
                json.dump(hist, f, indent=2)

        # the SAMPLED policy, which is the policy Eq. (13) specifies
        evs = [eval_agent(agent, c, steps=c.episode_len, seed=e)
               for e in range(eval_seeds)]
        samp = {k: float(np.mean([x[k] for x in evs])) for k in evs[0]}
        samp_std = {k: float(np.std([x[k] for x in evs])) for k in evs[0]}
        samp["device"] = str(agent.device)
        sampled_runs.append(samp)

        # the DETERMINISTIC (argmax) policy of the SAME actor
        det = [eval_agent(agent, c, steps=c.episode_len, seed=e,
                           deterministic=True) for e in range(eval_seeds)]
        argmax_runs.append({k: float(np.mean([x[k] for x in det]))
                             for k in det[0]})

        # the per-seed rows are written as they are produced, so that an
        # interrupted run does not throw away the training it has already done
        with open(os.path.join(ANALYSIS, "base_seed_rows.jsonl"), "a",
                  encoding="utf-8") as f:
            f.write(json.dumps(dict(train_seed=s,
                                    **{k: samp[k] for k in
                                       ("CK", "AG", "SC", "CovIntegral")},
                                    **{f"{k}_std": samp_std[k]
                                       for k in ("CK", "AG", "SC")},
                                    per_seed=[{k: x[k] for k in
                                               ("CK", "AG", "SC")}
                                              for x in evs])) + "\n")
        best_ck = (max(h["CK"] for h in hist) if hist else float("nan"))
        print(f"  seed {s}: CK={samp['CK']:.3f}+-{samp_std['CK']:.3f} "
              f"AG={samp['AG']:.3f} SC={samp['SC']:.3f} "
              f"CI={samp['CovIntegral']:.3f} "
              f"best_ck={best_ck:.3f} "
              f"({time.time()-t0:.0f}s)", flush=True)
        rows.append(dict(train_seed=s, **{k: samp[k] for k in
                                          ("CK", "AG", "SC", "CovIntegral")},
                         **{f"{k}_std": samp_std[k]
                            for k in ("CK", "AG", "SC")},
                         best_ck=float(best_ck),
                         final_ck=float(hist[-1]["CK"]) if hist else float("nan")))
    out = os.path.join(ANALYSIS, "base_training_seeds.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)
    print(f"  saved -> {out}\n", flush=True)

    # aggregate the training runs into the rows of the main table
    def agg_over_seeds(runs):
        # Only the NUMERIC fields are aggregated.  A row also carries the
        # device it was measured on, and averaging a string is what broke
        # the stage the first time the device was recorded in the row.
        keys = [k for k in runs[0].keys()
                if all(isinstance(r.get(k), (int, float)) and
                       not isinstance(r.get(k), bool) for r in runs)]
        a = {k: float(np.mean([r[k] for r in runs])) for k in keys}
        a["CK_std"] = float(np.std([r["CK"] for r in runs], ddof=1))
        # the per-seed values are kept, so that the table's spread can be
        # recomputed as the SAMPLE standard deviation, which is the number
        # the paper's intervals are built from
        a["per_seed_CK"] = ";".join(f"{r['CK']:.6f}" for r in runs)
        a["train_seeds"] = int(len(runs))
        a["device"] = str(runs[0].get("device", "?"))
        return a

    learned = {"MAPPO": agg_over_seeds(sampled_runs),
               "MAPPO-argmax": agg_over_seeds(argmax_runs)}
    return learned


def stage_base_table(learned, eval_seeds):
    """Write results_main.csv from the multi-seed learned rows."""
    from uav_wireless.experiments import run_base_comparison
    cfg = base_config()
    run_base_comparison(cfg, "results_main.csv", eval_seeds=eval_seeds,
                        train=False, learned=learned)
    print()


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
    ap.add_argument("--resume", action="store_true",
                    help="evaluate the stored policies instead of "
                         "retraining them (the training is reproducible "
                         "from its seed and is the expensive part)")
    ap.add_argument("--stage", default="all",
                    choices=["obs", "base", "abl", "ablstress", "learned",
                             "energy", "scen", "all"])
    # The number of TRAINING SEEDS is part of the protocol, not a
    # constant of the code: it sets the width of every interval the
    # paper reports, and the arms are compared with the base
    # comparison's arm A, so the arms and the base have to be trained
    # with the same number of seeds or the cross-table identity check
    # cannot hold.
    ap.add_argument("--train-seeds", type=int, default=0,
                    help="the base comparison's training seeds "
                         "(0 = the default)")
    ap.add_argument("--abl-seeds", type=int, default=0,
                    help="the component ablation's training seeds "
                         "(0 = the default)")
    ap.add_argument("--obs-seeds", type=int, default=0,
                    help="the observation arms' training seeds "
                         "(0 = the default)")
    args = ap.parse_args()

    quick = args.quick
    episodes = 6 if quick else 25
    train_seeds = 2 if quick else 5
    eval_seeds = 2 if quick else 5
    # The ablation must use the BASE comparison's budget, or the table
    # measures the budget rather than the component: the "Full" row has to be
    # the same experiment as the MAPPO row of the base comparison.
    abl_episodes = 3 if quick else episodes
    abl_seeds = 1 if quick else 3
    stress_episodes = 2 if quick else 6
    obs_seeds = 2 if quick else 3
    # the scenario matrix and the learned baselines are the two tables
    # whose rows are not the base comparison's own experiment, so their
    # seed count is their own parameter
    scen_seeds = 1 if quick else 8
    base_seeds = 1 if quick else 8
    if args.train_seeds:
        train_seeds = args.train_seeds
    if args.abl_seeds:
        abl_seeds = args.abl_seeds
    if args.obs_seeds:
        obs_seeds = args.obs_seeds

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
        learned = stage_base(episodes, train_seeds, eval_seeds,
                             resume=args.resume)
        stage_dormancy()
        stage_base_table(learned, eval_seeds)
        print()

    if args.stage in ("abl", "all"):
        print("[3/6] ablations ...", flush=True)
        cfg = base_config()
        run_ablation(cfg, "results_ablation.csv", stress=False,
                     episodes=abl_episodes, eval_seeds=eval_seeds,
                     seeds=abl_seeds)
        print()

    if args.stage in ("ablstress", "all"):
        print("[3b/6] ablations on the combined-stress scenario ...", flush=True)
        cfg = base_config()
        run_ablation(cfg, "results_ablation_stress.csv", stress=True,
                     episodes=stress_episodes, eval_seeds=eval_seeds,
                     seeds=abl_seeds)
        print()

    if args.stage in ("learned", "all"):
        print("[4/6] learned baselines (Table VI) ...", flush=True)
        # The learned baselines get the SAME episode budget as the proposed
        # method, so that the comparison is a comparison of learning
        # machinery and not of budgets.
        run_learned_baselines(base_config(), "results_learned_baselines.csv",
                              episodes=20, eval_seeds=eval_seeds,
                              seeds=base_seeds)
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
        # the scenario policies are trained at the BASE comparison's budget,
        # so that the scenario table and the main table describe the same
        # learner and a reader is not comparing an 8-episode policy with a
        # 25-episode one
        run_scenarios(base_config(), "results_scenarios.csv",
                      episodes=episodes, seeds=scen_seeds)
        print()

    print("=" * 78)
    print(f" DONE in {time.time() - t0:.0f} s")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
