"""Targeted trainer: train one configuration, then EVALUATE the final policy.

The evaluation is the point.  Training writes a CK for every episode, but that
CK is measured while the policy is still stochastic and still improving, on
one scene; comparing it against a deterministic rule measured on ten scenes is
not a comparison.  This script therefore trains, saves the final actor, and
then rolls the frozen policy out on a fixed set of evaluation scenes, exactly
as the rule baselines of `scripts/eval_rules.py` are rolled out.

Protocol
--------
train:   episodes x n_steps, seed = --seeds entry
save:    runs/<tag>/seed_<s>.pt          (actor + critic, MAPPO.save)
eval:    `--eval-seeds` scenes, the SAMPLED policy (Eq. 13 of the report),
         plus the argmax policy recorded separately and not used for the
         headline number.

Artefact: runs/<tag>/seed_<s>.json

    train_ck        CK of the last training episode (stochastic, 1 scene)
    eval_ck         mean CK over the evaluation scenes (the headline)
    eval_ck_std     sample standard deviation over the evaluation scenes
    eval_per_seed   per-scene CK
    eval_det_ck     mean CK of the argmax policy over the same scenes

Run:
    python scripts/run_exp.py --seeds 0 1 2 --episodes 200 --n-steps 2000 \
        --ego --shape 0.5 --eval-seeds 10 --tag exp_ego_shape_eval
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ml_impl"))
for _v in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np

from uav_wireless.env import UAVIoTEnv, SimConfig          # noqa: F401
from uav_wireless.experiments import base_config, eval_agent
from uav_wireless.train import train_mappo

HERE = os.path.dirname(os.path.abspath(__file__))
MLIMPL = os.path.join(HERE, "..", "ml_impl")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", nargs="+", type=int, default=[0])
    ap.add_argument("--episodes", type=int, default=200)
    ap.add_argument("--n-steps", type=int, default=2000)
    ap.add_argument("--ego", action="store_true")
    ap.add_argument("--n-ego", type=int, default=3)
    ap.add_argument("--shape", type=float, default=0.0)
    ap.add_argument("--no-w", action="store_true")
    ap.add_argument("--credit-mode", default="team")
    ap.add_argument("--diff-beta", type=float, default=1.0)
    ap.add_argument("--randomize-layout", action="store_true")
    ap.add_argument("--eval-seeds", type=int, default=10)
    ap.add_argument("--eval-offset", type=int, default=1000,
                    help="first scene seed; disjoint from the "
                         "training seeds")
    ap.add_argument("--tag", default="exp")
    args = ap.parse_args()

    outdir = os.path.join(MLIMPL, "runs", args.tag)
    os.makedirs(outdir, exist_ok=True)

    for s in args.seeds:
        out_path = os.path.join(outdir, "seed_%d.json" % s)
        if os.path.exists(out_path):
            print("seed %d: already done, skipping" % s, flush=True)
            continue
        cfg = base_config()
        cfg.episode_len = args.n_steps
        cfg.credit_mode = args.credit_mode
        cfg.diff_beta = args.diff_beta
        cfg.ego_sensors = args.ego
        cfg.n_ego = args.n_ego
        cfg.dist_shape_kappa = args.shape
        cfg.use_w_penalty = not args.no_w
        cfg.randomize_layout = args.randomize_layout

        t0 = time.time()
        agent, hist = train_mappo(cfg, episodes=args.episodes,
                                  n_steps=args.n_steps, seed=s, verbose=True,
                                  log_every=20, epochs=10, n_minibatch=4)
        dt = time.time() - t0
        agent.save(os.path.join(outdir, "seed_%d.pt" % s))

        scenes = list(range(args.eval_offset,
                            args.eval_offset + args.eval_seeds))
        ev = []
        for es in scenes:
            r = eval_agent(agent, cfg, steps=args.n_steps, seed=es,
                           deterministic=False)
            ev.append({k: float(v) for k, v in r.items()
                       if isinstance(v, (int, float, np.floating))})
        evd = [float(eval_agent(agent, cfg, steps=args.n_steps, seed=es,
                                deterministic=True)["CK"])
               for es in scenes]
        cks = [e["CK"] for e in ev]
        rec = {
            "seed": s, "episodes": args.episodes, "n_steps": args.n_steps,
            "seconds": dt, "ego": args.ego, "n_ego": args.n_ego,
            "shape": args.shape, "use_w": not args.no_w,
            "credit_mode": args.credit_mode, "diff_beta": args.diff_beta,
            "randomize_layout": args.randomize_layout,
            "train_ck": float(hist[-1].get("CK", 0.0)) if hist else None,
            "eval_seeds": scenes, "eval_offset": args.eval_offset,
            "eval_ck": float(np.mean(cks)),
            "eval_ck_std": float(np.std(cks, ddof=1)) if len(cks) > 1 else 0.0,
            "eval_per_seed": cks,
            "eval_summary": ev,
            "eval_det_ck": float(np.mean(evd)),
            "final_ck": float(np.mean(cks)),   # the headline is the eval CK
            "hist": hist,
        }
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(rec, f)
        print("seed %d: DONE %.0fs train + %.0fs eval | eval CK=%.4f "
              "(sd %.4f) det=%.4f train_ck=%.4f"
              % (s, dt, time.time() - t0 - dt, rec["eval_ck"],
                 rec["eval_ck_std"], rec["eval_det_ck"], rec["train_ck"]),
              flush=True)


if __name__ == "__main__":
    main()
