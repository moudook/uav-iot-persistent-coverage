"""Evaluate reactive rule on each stress regime to check headroom (R6)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ml_impl"))
for v in ("OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","OMP_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(v, "1")
from uav_wireless.train import baseline_reactive
from stress_regimes import get_config
sys.path.insert(0, os.path.dirname(__file__))

for name in ["nominal", "single_pad", "small_battery", "low_comm", "failure", "multi_failure"]:
    cfg = get_config(name)
    cfg.episode_len = 200
    summary = baseline_reactive(cfg, steps=200, seed=0)
    ck = summary.get("CK", 0.0)
    headroom = 1.0 - ck
    print(f"{name}: reactive CK = {ck:.4f}, headroom = {headroom:.4f} {'OK' if headroom>=0.10 else 'FAIL'}")
