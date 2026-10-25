"""G3: methods at converged budgets on headroom-gated regimes."""
import os, sys, json, time, argparse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ml_impl"))
for v in ("OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","OMP_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(v, "1")
import numpy as np
from uav_wireless.experiments import base_config
from uav_wireless.mappo import MAPPO
from uav_wireless.train import train_mappo
sys.path.insert(0, os.path.dirname(__file__))
from stress_regimes import get_config

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--regime", required=True)
    ap.add_argument("--seeds", nargs="+", type=int, default=[0,1,2,3,4])
    ap.add_argument("--seed-idx", type=int, default=None)
    ap.add_argument("--episodes", type=int, default=200)
    ap.add_argument("--n-steps", type=int, default=2000)
    ap.add_argument("--credit-mode", default="team", choices=["team","c3"])
    args = ap.parse_args()

    seeds = args.seeds
    if args.seed_idx is not None:
        seeds = [seeds[args.seed_idx]]

    out_dir = os.path.join(os.path.dirname(__file__), "..", "ml_impl", "runs", "g3", args.regime, args.credit_mode)
    os.makedirs(out_dir, exist_ok=True)

    for s in seeds:
        out_path = os.path.join(out_dir, f"seed_{s}.json")
        if os.path.exists(out_path):
            print(f"seed {s}: already done, skipping")
            continue
        cfg = get_config(args.regime)
        cfg.episode_len = args.n_steps
        cfg.credit_mode = args.credit_mode
        t0 = time.time()
        agent, hist = train_mappo(cfg, episodes=args.episodes, n_steps=args.n_steps, seed=s, verbose=True, log_every=50)
        dt = time.time() - t0
        rec = {"regime": args.regime, "credit_mode": args.credit_mode, "seed": s,
               "episodes": args.episodes, "n_steps": args.n_steps, "seconds": dt, "hist": hist,
               "final_ck": float(hist[-1].get("CK", 0.0)) if hist else None}
        with open(out_path, "w") as f:
            import json
            json.dump(rec, f)
        print(f"seed {s}: DONE in {dt:.1f}s, final CK={rec['final_ck']:.4f}")

if __name__ == "__main__":
    main()
