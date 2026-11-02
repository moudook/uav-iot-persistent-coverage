"""Targeted trainer (innovation-aware)."""
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
    ap.add_argument("--energy-kappa", type=float, default=0.0)
    ap.add_argument("--no-w", action="store_true")
    ap.add_argument("--credit-mode", default="team")
    ap.add_argument("--diff-beta", type=float, default=1.0)
    ap.add_argument("--randomize-layout", action="store_true")
    ap.add_argument("--curriculum", action="store_true")
    ap.add_argument("--rf-at", type=int, default=None)
    ap.add_argument("--lr-decay", type=float, default=0.5)
    ap.add_argument("--eval-seeds", type=int, default=20)
    ap.add_argument("--eval-offset", type=int, default=1000)
    ap.add_argument("--tag", default="exp")
    ap.add_argument("--attn", action="store_true")
    ap.add_argument("--regime", default="nominal",
                    help="stress regime name (nominal, small_battery, "
                         "low_comm, failure, etc.)")
    args = ap.parse_args()

    outdir = os.path.join(MLIMPL, "runs", args.tag)
    os.makedirs(outdir, exist_ok=True)

    for s in args.seeds:
        out_path = os.path.join(outdir, "seed_%d.json" % s)
        if os.path.exists(out_path):
            print("seed %d: already done, skipping" % s, flush=True)
            continue
        if args.regime and args.regime != "nominal":
            import sys as _sys
            _sys.path.insert(0, os.path.join(os.path.dirname(__file__)) )
            from stress_regimes import get_config as _gc
            cfg = _gc(args.regime)
        else:
            cfg = base_config()
        cfg.episode_len = args.n_steps
        cfg.credit_mode = args.credit_mode
        cfg.diff_beta = args.diff_beta
        cfg.ego_sensors = args.ego
        cfg.n_ego = args.n_ego
        cfg.dist_shape_kappa = args.shape
        cfg.energy_shape_kappa = args.energy_kappa
        cfg.use_w_penalty = not args.no_w
        cfg.randomize_layout = args.randomize_layout

        t0 = time.time()
        agent, hist = train_mappo(cfg, episodes=args.episodes,
                                  n_steps=args.n_steps, seed=s, verbose=True,
                                  log_every=20, epochs=10, n_minibatch=4,
                                  curriculum=args.curriculum,
                                  rf_at=args.rf_at, lr_decay=args.lr_decay,
                                  attn=args.attn)
        dt = time.time() - t0
        agent.save(os.path.join(outdir, "seed_%d.pt" % s))

        scenes = list(range(args.eval_offset, args.eval_offset + args.eval_seeds))
        ev = []
        for es in scenes:
            r = eval_agent(agent, cfg, steps=args.n_steps, seed=es,
                           deterministic=False)
            ev.append(float(r["CK"]))
        evd = [float(eval_agent(agent, cfg, steps=args.n_steps, seed=es,
                                deterministic=True)["CK"])
               for es in scenes]
        cks = ev
        rec = {
            "seed": s, "episodes": args.episodes, "n_steps": args.n_steps,
            "seconds": dt, "ego": args.ego, "n_ego": args.n_ego,
            "shape": args.shape, "energy_kappa": args.energy_kappa,
            "use_w": not args.no_w, "credit_mode": args.credit_mode,
            "diff_beta": args.diff_beta, "curriculum": args.curriculum,
            "rf_at": args.rf_at, "randomize_layout": args.randomize_layout,
            "train_ck": float(hist[-1].get("CK", 0.0)) if hist else None,
            "eval_seeds": scenes, "eval_offset": args.eval_offset,
            "eval_ck": float(np.mean(cks)),
            "eval_ck_std": float(np.std(cks, ddof=1)) if len(cks) > 1 else 0.0,
            "eval_per_seed": cks, "eval_det_ck": float(np.mean(evd)),
            "final_ck": float(np.mean(cks)),
            "hist": hist,
        }
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(rec, f)
        print("seed %d: DONE %.0fs | eval CK=%.4f (sd %.4f) det=%.4f train_ck=%.4f"
              % (s, dt, rec["eval_ck"], rec["eval_ck_std"],
                 rec["eval_det_ck"], rec["train_ck"]), flush=True)


if __name__ == "__main__":
    main()
