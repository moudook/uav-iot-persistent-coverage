"""Re-run the budget sweep under the FIXED learner + eval protocol.

The superseded section claims "budget is excluded as the explanation of the
shortfall" from a sweep at 8/16/25 episodes run with the buggy learner.  This
re-runs the sweep at 25/50/100/200 episodes with the fixed learner and the
frozen-policy evaluation, so the claim is either re-established or dropped.

Run:  python scripts/sweep_budget.py --seeds 0 1 2 --budgets 25 50 100 200
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

ANCHOR = dict(ego_sensors=True, n_ego=3, dist_shape_kappa=0.5, use_w_penalty=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", nargs="+", type=int, default=[0, 1, 2])
    ap.add_argument("--budgets", nargs="+", type=int, default=[25, 50, 100, 200])
    ap.add_argument("--n-steps", type=int, default=2000)
    ap.add_argument("--eval-seeds", type=int, default=20)
    ap.add_argument("--prefix", default="budget")
    args = ap.parse_args()

    MLIMPL = os.path.join(os.path.dirname(__file__), "..", "ml_impl")
    scenes = list(range(1000, 1000 + args.eval_seeds))
    rows = []
    for ep in args.budgets:
        outdir = os.path.join(MLIMPL, "runs", "%s_ep%d" % (args.prefix, ep))
        os.makedirs(outdir, exist_ok=True)
        for s in args.seeds:
            p = os.path.join(outdir, "seed_%d.json" % s)
            if os.path.exists(p):
                d = json.load(open(p, encoding="utf-8"))
                print("[skip] ep=%d seed %d eval=%.3f"
                      % (ep, s, d["eval_ck"]), flush=True)
                rows.append(d)
                continue
            cfg = base_config()
            for k, v in ANCHOR.items():
                setattr(cfg, k, v)
            cfg.episode_len = args.n_steps
            t0 = time.time()
            agent, hist = train_mappo(cfg, episodes=ep, n_steps=args.n_steps,
                                      seed=s, verbose=True, log_every=25,
                                      epochs=10, n_minibatch=4)
            dt = time.time() - t0
            agent.save(os.path.join(outdir, "seed_%d.pt" % s))
            ev = []
            for es in scenes:
                r = eval_agent(agent, cfg, steps=args.n_steps, seed=es,
                               deterministic=False)
                ev.append(float(r["CK"]))
            d = dict(seed=s, episodes=ep, n_steps=args.n_steps, seconds=dt,
                     train_ck=float(hist[-1].get("CK", 0.0)),
                     eval_ck=float(np.mean(ev)),
                     eval_ck_std=float(np.std(ev, ddof=1)),
                     eval_per_seed=ev, eval_seeds=scenes, hist=hist)
            with open(p, "w", encoding="utf-8") as f:
                json.dump(d, f)
            rows.append(d)
            print("[done] ep=%d seed %d train=%.3f eval=%.3f (%.0fs)"
                  % (ep, s, d["train_ck"], d["eval_ck"], dt), flush=True)

    # summary: mean over seeds per budget
    print("\n=== budget sweep summary (eval CK, mean over seeds) ===")
    summ = {}
    for ep in args.budgets:
        xs = [r["eval_ck"] for r in rows if r["episodes"] == ep]
        if xs:
            summ[ep] = dict(mean=float(np.mean(xs)),
                            sd=float(np.std(xs, ddof=1)),
                            n=len(xs), per_seed=xs)
            print("ep=%3d  eval=%.4f (sd %.4f, n=%d)  per-seed=%s"
                  % (ep, summ[ep]["mean"], summ[ep]["sd"], len(xs),
                     [round(v, 4) for v in xs]))
    out = os.path.join(MLIMPL, "runs", args.prefix + "_summary.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(summ, f, indent=1)
    print("wrote", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
