import os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ml_impl"))
for v in ("OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","OMP_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(v, "1")
import numpy as np
from uav_wireless.env import UAVIoTEnv
from uav_wireless.experiments import base_config
from uav_wireless.mappo import MAPPO

cfg = base_config()
cfg.episode_len = 200
cfg.failure_enabled = False

# load first MAPPO checkpoint deterministically
ck = sorted(os.listdir(os.path.join(os.path.dirname(__file__), "..", "ml_impl", "runs", "exp_ego_eval")))
ckpts = [os.path.join(os.path.dirname(__file__), "..", "ml_impl", "runs", "exp_ego_eval", f) for f in ck if f.endswith(".pt")]
print("ckpts", ckpts)
import torch
agent = MAPPO(obs_dim=68, n_actions=6 if False else None, device="cpu") if False else None

# simpler: use greedy move-toward-nearest-deficit heuristic
env = UAVIoTEnv(cfg)
env.cfg.seed = 1000
obs, _ = env.reset()
trajs = [[] for _ in range(cfg.N)]
t = 0.0
for ui in range(cfg.N):
    trajs[ui].append((t, float(env.p[ui,0]), float(env.p[ui,1])))
ncov = env.coverage_counts()
for step in range(200):
    acts = [0]*cfg.N
    ncov = env.coverage_counts()
    deficient = [d for d in range(cfg.M) if ncov[d] < cfg.K]
    for i in range(cfg.N):
        if not deficient:
            acts[i] = 0
            continue
        dists = [(float(np.linalg.norm(env.sensors[d]-env.p[i])), d) for d in deficient]
        dists.sort()
        target = env.sensors[dists[0][1]]
        dx = target[0]-env.p[i,0]; dy = target[1]-env.p[i,1]
        if abs(dx) >= abs(dy):
            acts[i] = 1 if dx>0 else 2
        else:
            acts[i] = 3 if dy>0 else 4
        if np.linalg.norm([dx,dy]) < 2.0:
            acts[i] = 0
    res = env.step(np.array(acts))
    obs = res[0]
    t += cfg.dt
    for ui in range(cfg.N):
        trajs[ui].append((t, float(env.p[ui,0]), float(env.p[ui,1])))
    if res[3]:
        break

# write
out_dir = os.path.join(os.path.dirname(__file__), "..", "Simulation", "omnet_uav", "traces")
os.makedirs(out_dir, exist_ok=True)
out_file = os.path.join(out_dir, "episode_moving.movements")
with open(out_file, "w") as f:
    for ui in range(cfg.N):
        parts = []
        for (tt, x, y) in trajs[ui]:
            parts.append(f"{tt:.3f} {x:.3f} {y:.3f}")
        f.write(" ".join(parts) + "\n")
print("wrote", out_file)
print("start spread (first UAVs):", trajs[0][:3])
print("end (last):", trajs[0][-3:])
print("summary:", env.summary().get("CK"))
