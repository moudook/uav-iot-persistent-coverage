"""Measure the RULE baselines at the alternative deployment.

The paper's own feasibility certificate identifies a better deployment
(N = 5, R_cov = 45 m), and the learned controller does better there.
The rule baselines were never measured at that operating point, so the
paper's headline gap is a statement about the eight-UAV deployment
alone.  The rules are deterministic, so this costs no training: the
same evaluation scenes, the same seeds, the same simulator.

    python analysis/alt_deployment_rules.py
"""
from __future__ import annotations

import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ML = os.path.dirname(HERE)
sys.path.insert(0, ML)

import numpy as np

from uav_wireless.experiments import (base_config, baseline_reactive,
                                      baseline_reactive_local)
from uav_wireless.env import UAVIoTEnv


def measure(cfg, eval_seeds=5, steps=2000):
    """The rules on the SAME protocol as the main table: the evaluation
    seeds 0..eval_seeds-1, each with the scene's own seed."""
    out = []
    for e in range(eval_seeds):
        c = copy.deepcopy(cfg)
        c.seed = e
        r = baseline_reactive(c, steps=steps, seed=e)
        rl = baseline_reactive_local(c, steps=steps, seed=e)
        out.append((r, rl))
    return out


def main() -> int:
    res = {"eval_seeds": 5, "steps": 2000, "deployments": {}}
    for name, over in (("reported_n8_r35", dict(N=8, R_cov=35.0)),
                       ("alternative_n5_r45", dict(N=5, R_cov=45.0))):
        cfg = base_config(seed=0, **over)
        rows = measure(cfg)
        react = [r["CK"] for r, _ in rows]
        reactl = [r["CK"] for _, r in rows]
        rsc = [r["SC"] for r, _ in rows]
        rlsc = [r["SC"] for _, r in rows]
        res["deployments"][name] = dict(
            N=int(cfg.N), R_cov=float(cfg.R_cov),
            reactive_CK=float(np.mean(react)),
            reactive_CK_std=float(np.std(react, ddof=1)) if len(react) > 1 else 0.0,
            reactive_local_CK=float(np.mean(reactl)),
            reactive_local_CK_std=float(np.std(reactl, ddof=1)) if len(reactl) > 1 else 0.0,
            reactive_SC=float(np.mean(rsc)),
            reactive_local_SC=float(np.mean(rlsc)),
            per_scene_reactive=[float(x) for x in react],
            per_scene_reactive_local=[float(x) for x in reactl],
        )
        print(f"  {name}: the reactive rule {np.mean(react):.4f}, "
              f"the local rule {np.mean(reactl):.4f}")
    out = os.path.join(HERE, "alt_deployment_rules.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)
    print(f"Saved -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
