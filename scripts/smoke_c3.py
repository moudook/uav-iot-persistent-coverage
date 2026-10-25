"""Smoke test: C3 credit mode (1 seed, 5 episodes)."""
import os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ml_impl"))
for v in ("OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","OMP_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(v, "1")
import numpy as np
from uav_wireless.experiments import base_config
from uav_wireless.mappo import MAPPO
from uav_wireless.train import train_mappo

cfg = base_config()
cfg.episode_len = 200
cfg.credit_mode = "c3"
cfg.credit_weight = 0.10
t0 = time.time()
agent, hist = train_mappo(cfg, episodes=5, n_steps=200, seed=0, verbose=True)
dt = time.time() - t0
cks = [h.get("CK", 0) for h in hist]
print("C3 smoke: CK=%.3f (min=%.3f max=%.3f) in %.1fs" % (cks[-1], min(cks), max(cks), dt))
