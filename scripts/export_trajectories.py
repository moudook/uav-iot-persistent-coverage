"""Export Python-simulator UAV trajectories as BonnMotion trace files for INET.

Usage: python scripts/export_trajectories.py --episodes 5 --out Simulation/omnet_uav/traces

Writes one .movements file per episode, each line = one UAV's trajectory as
(t x y t x y ...) tuples, compatible with INET's BonnMotionMobility.
"""
import os, sys, argparse, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ml_impl"))
for v in ("OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","OMP_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(v, "1")
import numpy as np
from uav_wireless.env import UAVIoTEnv
from uav_wireless.experiments import base_config

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=int, default=3)
    ap.add_argument("--out", default="Simulation/omnet_uav/traces")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    cfg = base_config()
    cfg.episode_len = 200  # short for Step A
    cfg.failure_enabled = False
    for ep in range(args.episodes):
        env = UAVIoTEnv(cfg)
        env.cfg.seed = args.seed + ep  # vary seed
        obs, state = env.reset()
        # trajectories[ui] = list of (t, x, y)
        trajs = [[] for _ in range(cfg.N)]
        dt = cfg.dt
        t = 0.0
        for ui in range(cfg.N):
            trajs[ui].append((t, float(env.p[ui,0]), float(env.p[ui,1])))
        steps = 0
        while steps < cfg.episode_len:
            acts = [0]*cfg.N  # hover for replay baseline (Step A)
            obs, state, r, done, info = env.step(acts)
            t += dt
            for ui in range(cfg.N):
                trajs[ui].append((t, float(env.p[ui,0]), float(env.p[ui,1])))
            steps += 1
            if done:
                break
        # write BonnMotion file
        out_file = os.path.join(args.out, f"episode_{ep:03d}.movements")
        with open(out_file, "w") as f:
            for ui in range(cfg.N):
                parts = []
                for (tt, x, y) in trajs[ui]:
                    parts.append(f"{tt:.3f} {x:.3f} {y:.3f}")
                f.write(" ".join(parts) + "\n")
        print(f"episode {ep}: {steps} steps, {cfg.N} UAVs -> {out_file}")
    # also write sensors and pads
    sensors_file = os.path.join(args.out, "sensors.txt")
    with open(sensors_file, "w") as f:
        for s in env.sensors:
            f.write(f"{s[0]:.3f} {s[1]:.3f}\n")
    pads_file = os.path.join(args.out, "pads.txt")
    with open(pads_file, "w") as f:
        for p in env.pads:
            f.write(f"{p[0]:.3f} {p[1]:.3f}\n")
    print(f"sensors -> {sensors_file}, pads -> {pads_file}")

if __name__ == "__main__":
    main()
