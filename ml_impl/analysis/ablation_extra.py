"""
One extra ablation variant: the coverage-map summary on its own.

The canonical configuration includes the broadcast coverage-map summary, so
the component ablation's "with-map" row is a duplicate of the full
configuration and the summary's own effect is not isolated by it.  This
script runs the missing variant -- the same configuration with the summary
removed -- under exactly the ablation's protocol, and appends it to the
ablation CSV.

Run:  python analysis/ablation_extra.py
"""

from __future__ import annotations

import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np

from uav_wireless.experiments import base_config, eval_agent
from uav_wireless.train import train_mappo

HERE = os.path.dirname(os.path.abspath(__file__))
ML = os.path.dirname(HERE)

EPISODES = 10
EVAL_SEEDS = 3


def main():
    c = base_config(seed=0, map_grid=0)
    agent, _ = train_mappo(c, episodes=EPISODES, n_steps=c.episode_len,
                           seed=0, verbose=False)
    evs = [eval_agent(agent, c, steps=c.episode_len, seed=s)
           for s in range(EVAL_SEEDS)]
    agg = {k: float(np.mean([x[k] for x in evs])) for k in evs[0]}
    print(f"no-map  CK={agg['CK']:.3f} AG={agg['AG']:.3f} SC={agg['SC']:.3f} "
          f"CI={agg['CovIntegral']:.3f} Stranded={agg['Stranded']:.1f}")

    path = os.path.join(ML, "results_ablation.csv")
    rows = []
    if os.path.exists(path):
        with open(path, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
            fields = list(rows[0].keys())
    else:
        fields = ["model", "CK", "AG", "SC", "CovIntegral", "Stranded"]

    row = {"model": "no-map"}
    for k in ("CK", "AG", "SC", "CovIntegral", "Stranded"):
        if k in agg:
            row[k] = agg[k]
    for k in fields:
        row.setdefault(k, "")
    rows.append(row)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"appended to {path}")

    out = os.path.join(HERE, "ablation_extra.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(row, f, indent=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
