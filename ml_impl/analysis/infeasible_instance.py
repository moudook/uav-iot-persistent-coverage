"""
The framework's first claim, measured: what the metrics do on an
INFEASIBLE configuration.

The paper claims that a coverage ratio reported without an achievability
reference cannot distinguish a strong controller from an infeasible
configuration, and that the joint service-continuity metric is
degenerate on such a configuration.  That is a claim about what the
METRICS show, and it deserves a measurement rather than an assertion.

This script runs a controller on the report's ORIGINAL configuration,
N = 5, K = 2, R_cov = 35 m, which the feasibility certificate of
Section III proves infeasible for the REGION requirement, and reports the
two metrics side by side with the teleporting achievability oracle on the
same scene:

  * the coverage ratio CK, which is NOT zero, and which a reader with no
    achievability reference cannot interpret: it is consistent with a
    mediocre controller on a feasible instance;
  * the service-continuity metric SC, which IS zero -- the degenerate
    behaviour the paper describes, and which is therefore equally
    consistent with a perfect controller and an infeasible instance;
  * the oracle's CK, which is what tells the two apart: the sensors are
    coverable, so the shortfall is the controller's, and the region is
    not coverable at all, so no controller can serve the whole area.

Run:  python analysis/infeasible_instance.py
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np

from uav_wireless.env import SimConfig, UAVIoTEnv
from uav_wireless.train import baseline_reactive
from uav_wireless.experiments import base_config

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    rows = []
    for seed in range(5):
        # the report's ORIGINAL configuration: the corner-packing bound
        # gives N >= 4K = 8, so N = 5 is provably infeasible for the
        # region requirement
        cfg = base_config()
        cfg.N = 5
        cfg.K = 2
        cfg.M = 20
        cfg.R_cov = 35.0
        cfg.R_comm = 40.0
        cfg.episode_len = 2000
        cfg.seed = seed
        s = baseline_reactive(cfg, steps=cfg.episode_len, seed=seed)
        # the teleporting achievability oracle on the same scene
        try:
            from analysis.feasibility import analyse_scene
            o = analyse_scene(seed, cfg, iters=60, restarts=8)
            orc = float(o.get("oracle_CK_connected", float("nan")))
        except Exception as exc:                            # pragma: no cover
            orc = float("nan")
        rows.append(dict(seed=seed, CK=float(s["CK"]), AG=float(s["AG"]),
                         SC=float(s["SC"]),
                         CovIntegral=float(s["CovIntegral"]),
                         oracle_CK=orc))
        print(f"seed {seed}: CK={s['CK']:.3f} AG={s['AG']:.3f} "
              f"SC={s['SC']:.3f} oracle_CK={orc:.3f}")
    agg = {k: float(np.mean([r[k] for r in rows]))
           for k in ("CK", "AG", "SC", "CovIntegral", "oracle_CK")}
    print(f"\nmean over the seeds: CK={agg['CK']:.3f} AG={agg['AG']:.3f} "
          f"SC={agg['SC']:.3f} oracle_CK={agg['oracle_CK']:.3f}")
    out = os.path.join(HERE, "infeasible_instance.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(dict(rows=rows, mean=agg), f, indent=2)
    print(f"Saved -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
