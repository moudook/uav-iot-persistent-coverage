"""Smoke test: train MAPPO for a small budget on 1 seed. Verify no NaN/crash."""
import os, sys, time, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ml_impl"))
for v in ("OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","OMP_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(v, "1")
import numpy as np, torch
from uav_wireless.env import UAVIoTEnv
from uav_wireless.experiments import base_config
from uav_wireless.mappo import MAPPO
from uav_wireless.train import train_mappo

cfg = base_config()
cfg.episode_len = 200
t0 = time.time()
agent, hist = train_mappo(cfg, episodes=5, n_steps=200, seed=0, verbose=True)
dt = time.time() - t0
final_ck = hist[-1].get("CK", 0.0)
print("SMOKE OK: " + str(len(hist)) + " episodes in " + f"{dt:.1f}" + "s, final ck=" + f"{final_ck:.4f}")
with open(os.path.join(os.path.dirname(__file__), "..", "ml_impl", "smoke_hist.json"), "w") as f:
    json.dump({"hist": hist, "seconds": dt}, f)
print("saved smoke_hist.json")
