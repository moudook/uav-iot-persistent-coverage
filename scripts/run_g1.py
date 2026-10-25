"""G1 budget truth test: retrain MAPPO at a larger budget across N seeds.

Usage:  python scripts/run_g1.py --seeds 0 1 2 3 4 --episodes 200 --n-steps 2000

Writes per-seed histories to ml_impl/runs/g1/seed_<s>.json and a summary CSV.
"""
import argparse, os, sys, json, time, subprocess
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ml_impl"))
for v in ("OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","OMP_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(v, "1")
import numpy as np, torch
from uav_wireless.env import UAVIoTEnv
from uav_wireless.experiments import base_config
from uav_wireless.mappo import MAPPO
from uav_wireless.train import train_mappo

HERE = os.path.dirname(os.path.abspath(__file__))
MLIMPL = os.path.join(HERE, "..", "ml_impl")
OUT = os.path.join(MLIMPL, "runs", "g1")
os.makedirs(OUT, exist_ok=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", nargs="+", type=int, default=[0,1,2,3,4])
    ap.add_argument("--episodes", type=int, default=200)
    ap.add_argument("--n-steps", type=int, default=2000)
    ap.add_argument("--seed-idx", type=int, default=None, help="run only this index into --seeds")
    args = ap.parse_args()

    seeds = args.seeds
    if args.seed_idx is not None:
        seeds = [seeds[args.seed_idx]]

    for s in seeds:
        out_path = os.path.join(OUT, f"seed_{s}.json")
        if os.path.exists(out_path):
            print(f"seed {s}: already done, skipping")
            continue
        cfg = base_config()
        cfg.episode_len = args.n_steps
        t0 = time.time()
        agent, hist = train_mappo(cfg, episodes=args.episodes, n_steps=args.n_steps, seed=s, verbose=True, log_every=20)
        dt = time.time() - t0
        rec = {"seed": s, "episodes": args.episodes, "n_steps": args.n_steps, "seconds": dt, "hist": hist,
               "final_ck": float(hist[-1].get("CK", 0.0)) if hist else None}
        with open(out_path, "w") as f:
            json.dump(rec, f)
        print(f"seed {s}: DONE in {dt:.1f}s, final CK={rec['final_ck']:.4f} -> {out_path}")

if __name__ == "__main__":
    main()
