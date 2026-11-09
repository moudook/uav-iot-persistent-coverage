"""KL-anchored residual fine-tuning: BC init + PPO with KL penalty to BC ref."""
import os, sys, json, time, argparse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ml_impl"))
for v in ("OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","OMP_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(v, "1")
import numpy as np
from uav_wireless.experiments import base_config
from uav_wireless.train import train_mappo
from stress_regimes import get_config
sys.path.insert(0, os.path.dirname(__file__))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--regime", default="single_pad")
    ap.add_argument("--seeds", nargs="+", type=int, default=[0])
    ap.add_argument("--episodes", type=int, default=200)
    ap.add_argument("--n-steps", type=int, default=2000)
    ap.add_argument("--kl-coef", type=float, default=0.5)
    ap.add_argument("--kl-target", type=float, default=0.01)
    ap.add_argument("--ent-floor", type=float, default=0.3)
    ap.add_argument("--ent-floor-coef", type=float, default=0.1)
    ap.add_argument("--clip", type=float, default=0.05)
    ap.add_argument("--lr", type=float, default=3e-5)
    ap.add_argument("--ent-coef", type=float, default=0.0)
    args = ap.parse_args()

    bc_path = os.path.join(os.path.dirname(__file__), "..", "ml_impl", "bc_actor.pt")
    out_dir = os.path.join(os.path.dirname(__file__), "..", "ml_impl", "runs", "kl_anchored", args.regime)
    os.makedirs(out_dir, exist_ok=True)

    for s in args.seeds:
        cfg = get_config(args.regime)
        cfg.episode_len = args.n_steps
        cfg.credit_mode = "team"
        t0 = time.time()
        agent, hist = train_mappo(cfg, episodes=args.episodes, n_steps=args.n_steps, seed=s,
                                  verbose=True, log_every=50, bc_path=bc_path,
                                  ref_bc_path=bc_path, kl_coef=args.kl_coef,
                                  kl_target=args.kl_target, ent_floor=args.ent_floor,
                                  ent_floor_coef=args.ent_floor_coef, clip=args.clip,
                                  lr=args.lr, ent_coef=args.ent_coef)
        dt = time.time() - t0
        out_path = os.path.join(out_dir, f"seed_{s}.json")
        rec = {"regime": args.regime, "method": "kl_anchored", "seed": s,
               "episodes": args.episodes, "n_steps": args.n_steps, "seconds": dt,
               "hist": hist, "final_ck": float(hist[-1].get("CK", 0.0)) if hist else None,
               "params": {"kl_coef": args.kl_coef, "kl_target": args.kl_target,
                          "ent_floor": args.ent_floor, "clip": args.clip, "lr": args.lr}}
        with open(out_path, "w") as f:
            json.dump(rec, f)
        print(f"seed {s}: DONE in {dt:.1f}s, final CK={rec['final_ck']:.4f}")

if __name__ == "__main__":
    main()
