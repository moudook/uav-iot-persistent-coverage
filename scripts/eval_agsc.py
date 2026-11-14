"""Evaluate AG/SC (and CK) of a trained tag on held-out scenes.

The full held-out eval stores only CK statistics; the table also prints AG and
SC, so this script averages the three over the same held-out scene set.

Usage:
    python scripts/eval_agsc.py --tag exp_v2 --scenes 5 --steps 2000
"""
import argparse
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="exp_ego_fixed")
    ap.add_argument("--scenes", type=int, default=5)
    ap.add_argument("--steps", type=int, default=2000)
    ap.add_argument("--offset", type=int, default=1000)
    a = ap.parse_args()

    rundir = os.path.join(os.path.dirname(__file__), "..", "ml_impl",
                          "runs", a.tag)
    ckpts = sorted(glob.glob(os.path.join(rundir, "seed_*.pt")))
    scenes = list(range(a.offset, a.offset + a.scenes))
    out = []
    for ck in ckpts:
        meta = json.load(open(ck.replace(".pt", ".json"), encoding="utf-8"))
        c = base_config()
        c.ego_sensors = meta.get("ego", True)
        c.n_ego = meta.get("n_ego", 3)
        c.phy_ego_sensors = meta.get("phy_ego", False)
        c.use_critical_anchor = meta.get("anchor", False)
        c.use_scalable_id = meta.get("scalable_id", False)
        if "use_agent_id" in meta:
            c.use_agent_id = bool(meta["use_agent_id"])
        c.assist_return_mask = meta.get("assist_return", False)
        c.dist_shape_kappa = meta.get("shape", 0.0)
        c.use_w_penalty = meta.get("use_w", True)
        c.episode_len = a.steps
        env = UAVIoTEnv(c)
        ag = MAPPO(n_agents=c.N, obs_dim=env.obs_dim, state_dim=env.state_dim,
                   device="cpu")
        ag.load(ck)
        rows = [eval_agent(ag, c, steps=a.steps, seed=s, deterministic=False)
                for s in scenes]
        out.append({
            "ckpt": os.path.basename(ck),
            "CK": float(np.mean([r["CK"] for r in rows])),
            "AG": float(np.mean([r["AG"] for r in rows])),
            "SC": float(np.mean([r["SC"] for r in rows])),
        })
        print(ck, "CK", round(out[-1]["CK"], 4), "AG", round(out[-1]["AG"], 4),
              "SC", round(out[-1]["SC"], 4), flush=True)
    agg = {k: float(np.mean([o[k] for o in out])) for k in ("CK", "AG", "SC")}
    print("MEAN", {k: round(v, 4) for k, v in agg.items()})
    with open(os.path.join(rundir, "agsc.json"), "w") as f:
        json.dump({"per_ckpt": out, "mean": agg, "scenes": scenes}, f, indent=1)


if __name__ == "__main__":
    main()
