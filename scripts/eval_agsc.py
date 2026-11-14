"""Evaluate AG/SC (and CK) of the corrected retrain on held-out scenes.

The full held-out eval stores only CK statistics; the table also prints AG and
SC, so this script averages the three over the same held-out scene set.
"""
import glob
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ml_impl"))
for v in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS",
          "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(v, "1")

from uav_wireless.env import UAVIoTEnv
from uav_wireless.experiments import base_config, eval_agent
from uav_wireless.mappo import MAPPO

TAG = "exp_ego_fixed"
SCENES = list(range(1000, 1005))   # same offset; 5 scenes to keep it quick
STEPS = 2000


def main():
    rundir = os.path.join(os.path.dirname(__file__), "..", "ml_impl", "runs", TAG)
    ckpts = sorted(glob.glob(os.path.join(rundir, "seed_*.pt")))
    cfg = base_config()
    cfg.ego_sensors = True
    cfg.n_ego = 3
    cfg.dist_shape_kappa = 0.5
    cfg.episode_len = STEPS
    out = []
    for ck in ckpts:
        meta = json.load(open(ck.replace(".pt", ".json"), encoding="utf-8"))
        c = base_config()
        c.ego_sensors = meta.get("ego", True)
        c.n_ego = meta.get("n_ego", 3)
        c.dist_shape_kappa = meta.get("shape", 0.0)
        c.use_w_penalty = meta.get("use_w", True)
        c.episode_len = STEPS
        env = UAVIoTEnv(c)
        ag = MAPPO(n_agents=c.N, obs_dim=env.obs_dim, state_dim=env.state_dim,
                   device="cpu")
        ag.load(ck)
        rows = [eval_agent(ag, c, steps=STEPS, seed=s, deterministic=False)
                for s in SCENES]
        out.append({
            "ckpt": os.path.basename(ck),
            "CK": float(np.mean([r["CK"] for r in rows])),
            "AG": float(np.mean([r["AG"] for r in rows])),
            "SC": float(np.mean([r["SC"] for r in rows])),
        })
        print(ck, "CK", round(out[-1]["CK"], 4), "AG", round(out[-1]["AG"], 4),
              "SC", round(out[-1]["SC"], 4))
    agg = {k: float(np.mean([o[k] for o in out])) for k in ("CK", "AG", "SC")}
    print("MEAN", {k: round(v, 4) for k, v in agg.items()})
    with open(os.path.join(rundir, "agsc.json"), "w") as f:
        json.dump({"per_ckpt": out, "mean": agg}, f, indent=1)


if __name__ == "__main__":
    main()
