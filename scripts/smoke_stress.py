"""Smoke test all stress regimes (1 seed, 5 episodes each)."""
import os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ml_impl"))
for v in ("OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","OMP_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(v, "1")
import numpy as np
from uav_wireless.experiments import base_config
from uav_wireless.mappo import MAPPO
from uav_wireless.train import train_mappo
from stress_regimes import get_config
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

for name in ["nominal", "single_pad", "small_battery", "low_comm", "failure"]:
    cfg = get_config(name)
    cfg.episode_len = 200
    t0 = time.time()
    agent, hist = train_mappo(cfg, episodes=3, n_steps=200, seed=0, verbose=False)
    dt = time.time() - t0
    cks = [h.get("CK", 0) for h in hist]
    print(f"{name}: CK={cks[-1]:.3f} (min={min(cks):.3f} max={max(cks):.3f}) in {dt:.1f}s -- {'OK' if not any(np.isnan(cks)) else 'NaN!'}")
