"""Run the corrected ablation matrix under the fixed learner + eval protocol.

Each arm is a configuration flag, trained for `--episodes` with `--seeds`
seeds, then evaluated frozen on the held-out scenes.  Every arm that the
report's superseded section claimed something about is here:

  baseline (bugfix only, done already)
  ego+shape (done already)              -- the two anchors
  no_w       W_t penalty removed
  kappa 0.1 / 1.0                       distance-shaping weight
  n_ego 5                               more bearing targets
  diff beta 0.5 / 2.0                   difference credit
  randomize_layout on                   train on randomized layouts
  full_obs                              replace ego bearings with full global
                                        coverage state (value-of-information)
  ideal (info)                          full state + no action mask penalty
                                        (optional)

Run:  python scripts/sweep_knobs.py --seeds 0 1 2 --episodes 200 \
          --n-steps 2000 --eval-seeds 20 --tags no_w kappa1 n_ego5 diff2 full_obs
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

from uav_wireless.experiments import base_config, eval_agent
from uav_wireless.train import train_mappo

#: tag -> config overrides on top of the ego+shape anchor
ARMS = {
    "no_w": dict(use_w_penalty=False),
    "kappa1": dict(dist_shape_kappa=1.0),
    "kappa01": dict(dist_shape_kappa=0.1),
    "n_ego5": dict(n_ego=5),
    "diff05": dict(credit_mode="diff", diff_beta=0.5),
    "diff2": dict(credit_mode="diff", diff_beta=2.0),
    "rand_layout": dict(randomize_layout=True),
    "full_obs": dict(use_agent_id=True, map_grid=4, use_pad_bearing=True,
                     ego_sensors=False, dist_shape_kappa=0.0),
    "ideal_info": dict(use_agent_id=True, map_grid=4, use_pad_bearing=True,
                       ego_sensors=False, dist_shape_kappa=0.0,
                       use_w_penalty=False),
}

ANCHOR = dict(ego_sensors=True, n_ego=3, dist_shape_kappa=0.5)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", nargs="+", type=int, default=[0, 1, 2])
    ap.add_argument("--episodes", type=int, default=200)
    ap.add_argument("--n-steps", type=int, default=2000)
    ap.add_argument("--eval-seeds", type=int, default=20)
    ap.add_argument("--tags", nargs="+", default=sorted(ARMS))
    ap.add_argument("--prefix", default="sweep")
    args = ap.parse_args()

    MLIMPL = os.path.join(os.path.dirname(__file__), "..", "ml_impl")
    for tag in args.tags:
        if tag not in ARMS:
            print("unknown arm:", tag)
            return 1
        outdir = os.path.join(MLIMPL, "runs", args.prefix + "_" + tag)
        os.makedirs(outdir, exist_ok=True)
        for s in args.seeds:
            p = os.path.join(outdir, "seed_%d.json" % s)
            if os.path.exists(p):
                print("[skip]", tag, s, "(exists)")
                continue
            cfg = base_config()
            for k, v in ANCHOR.items():
                setattr(cfg, k, v)
            for k, v in ARMS[tag].items():
                setattr(cfg, k, v)
            cfg.episode_len = args.n_steps
            t0 = time.time()
            agent, hist = train_mappo(cfg, episodes=args.episodes,
                                      n_steps=args.n_steps, seed=s,
                                      verbose=True, log_every=40,
                                      epochs=10, n_minibatch=4)
            dt = time.time() - t0
            agent.save(os.path.join(outdir, "seed_%d.pt" % s))
            scenes = list(range(1000, 1000 + args.eval_seeds))
            ev = []
            for es in scenes:
                r = eval_agent(agent, cfg, steps=args.n_steps, seed=es,
                               deterministic=False)
                ev.append(float(r["CK"]))
            rec = dict(seed=s, tag=tag, episodes=args.episodes,
                       n_steps=args.n_steps, seconds=dt,
                       train_ck=float(hist[-1].get("CK", 0.0)),
                       eval_ck=float(np.mean(ev)),
                       eval_ck_std=float(np.std(ev, ddof=1)),
                       eval_per_seed=ev, eval_seeds=scenes,
                       hist=hist)
            with open(p, "w", encoding="utf-8") as f:
                json.dump(rec, f)
            print("[done] %s seed %d  train=%.3f eval=%.3f (%.0fs)"
                  % (tag, s, rec["train_ck"], rec["eval_ck"], dt),
                  flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
