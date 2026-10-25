"""Collect (obs, action) pairs from the reactive rule for behavior cloning."""
import os, sys, json, pickle
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ml_impl"))
for v in ("OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","OMP_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(v, "1")
import numpy as np
from uav_wireless.env import UAVIoTEnv, A_HOVER, A_CHARGE, N_ACTIONS
from uav_wireless.experiments import base_config
from uav_wireless.train import _seeded, _move_toward

def collect(cfg, steps=500, seed=0):
    cfg = _seeded(cfg, seed)
    env = UAVIoTEnv(cfg)
    obs, st = env.reset()
    pairs = []  # list of (obs_i, action_i) for each agent
    for _ in range(steps):
        acts = np.zeros(cfg.N, dtype=np.int64)
        ncov = env.coverage_counts()
        under = np.where(ncov < cfg.K)[0]
        for k, i in enumerate(env._active_idx()):
            if env.E[i] <= env.return_threshold(i):
                if np.min(np.linalg.norm(env.pads - env.p[i], axis=1)) <= cfg.pad_service_radius:
                    acts[i] = A_CHARGE
                else:
                    acts[i] = _move_toward(env, i, env.pads[int(np.argmin(np.linalg.norm(env.pads - env.p[i], axis=1)))])
                continue
            if len(under) == 0:
                acts[i] = A_HOVER
                continue
            tgt = env.sensors[under[k % len(under)]]
            acts[i] = _move_toward(env, i, tgt)
        # record (obs, acts) for active agents
        for i in env._active_idx():
            pairs.append((obs[i].copy(), int(acts[i])))
        obs, st, r, done, _ = env.step(acts)
        if done:
            break
    return pairs

if __name__ == "__main__":
    cfg = base_config()
    cfg.episode_len = 500
    all_pairs = []
    for seed in range(3):
        pairs = collect(cfg, steps=500, seed=seed)
        all_pairs.extend(pairs)
        print(f"seed {seed}: {len(pairs)} pairs, total {len(all_pairs)}")
    out = os.path.join(os.path.dirname(__file__), "..", "ml_impl", "bc_data.pkl")
    with open(out, "wb") as f:
        pickle.dump(all_pairs, f)
    print(f"saved {len(all_pairs)} pairs to {out}")
