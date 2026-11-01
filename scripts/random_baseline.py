"""Random (uniform over feasible actions) baseline diagnostic."""
import os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ml_impl"))
for v in ("OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","OMP_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(v, "1")
import numpy as np
from uav_wireless.env import SimConfig, UAVIoTEnv

def run(cfg, seed, steps):
    cfg = __import__("copy").deepcopy(cfg)
    cfg.seed = seed
    cfg.episode_len = steps
    env = UAVIoTEnv(cfg)
    obs, st = env.reset()
    for _ in range(steps):
        mask = np.stack(env.action_masks())
        for i in range(cfg.N):
            if not mask[i].any():
                mask[i, 0] = True
        acts = np.array([np.random.choice(np.where(mask[i])[0]) for i in range(cfg.N)], dtype=np.int64)
        obs, st, r, done, _ = env.step(acts)
        if done:
            break
    return env.summary()

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--steps", type=int, default=2000)
    ap.add_argument("--N", type=int, default=8)
    ap.add_argument("--M", type=int, default=20)
    ap.add_argument("--n_pads", type=int, default=2)
    a = ap.parse_args()
    cfg = SimConfig(N=a.N, M=a.M, n_pads=a.n_pads)
    res = [run(cfg, s, a.steps) for s in range(a.seeds)]
    cks = [r.get("CK", r.get("ck", 0)) for r in res]
    print("random baseline CK: mean=%.4f std=%.4f n=%d" % (np.mean(cks), np.std(cks), len(cks)))
    print("per-seed CK:", [round(c,4) for c in cks])
    os.makedirs("ml_impl/runs/diag", exist_ok=True)
    with open("ml_impl/runs/diag/random_baseline.json","w") as f:
        json.dump({"cks":cks,"summaries":res}, f)
