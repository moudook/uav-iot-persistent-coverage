"""Convergence check: 1 seed at 1000 episodes (2e6 steps). G1 memo recommendation."""
import os, sys, time, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ml_impl"))
for v in ("OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","OMP_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(v, "1")
import numpy as np
from uav_wireless.experiments import base_config
from uav_wireless.train import train_mappo

cfg = base_config()
cfg.episode_len = 2000
OUT = os.path.join(os.path.dirname(__file__), "..", "ml_impl", "runs", "g1")
os.makedirs(OUT, exist_ok=True)
out_path = os.path.join(OUT, "convergence_seed0.json")
t0 = time.time()
agent, hist = train_mappo(cfg, episodes=1000, n_steps=2000, seed=0, verbose=True, log_every=50)
dt = time.time() - t0
rec = {"seed": 0, "episodes": 1000, "n_steps": 2000, "seconds": dt, "hist": hist,
       "final_ck": float(hist[-1].get("CK", 0.0)) if hist else None}
with open(out_path, "w") as f:
    json.dump(rec, f)
print("CONVERGENCE CHECK DONE in " + str(round(dt)) + "s, final CK=" + f"{rec['final_ck']:.4f}")
