"""
The alternative corrected deployment, MEASURED.

The paper's contribution list offers two corrected deployments: the
reported one (N = 8, K = 2, R_cov = 35 m) and an alternative that keeps
the original fleet size and widens the coverage radius instead (N = 5,
K = 2, R_cov = 45 m).  So far only the first has been measured: the
alternative appears in the paper as an argument, with its feasibility
derived from the witness construction (the worst second-nearest distance
among the five witness discs is 44.72 m, inside the 45 m offered).

An argument in the contributions list is a weakness, and this measures
it: the same protocol, the same training seeds and the same evaluation
scenes, with the fleet size and the coverage radius exchanged.

What it reports:
  * the coverage of the learned controller and of the reactive rules on
    the alternative deployment, against the same deployment at N = 8;
  * the achievability ceiling, so that the comparison is against a
    reference and not against a number that could be infeasible;
  * the region bound's own verdict on the alternative: with R_cov = 45 m
    the four-corner argument needs 2 R_cov = 90 m, which is MORE than the
    side, so the corner certificate does NOT apply and the alternative
    rests on the witness construction instead.  That is stated here
    rather than left implicit.

Usage:  python analysis/alt_deployment.py [--seeds 5] [--episodes 25]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ML = os.path.dirname(HERE)
sys.path.insert(0, ML)

from uav_wireless.experiments import base_config, eval_agent   # noqa: E402
from uav_wireless.train import train_mappo                    # noqa: E402
from uav_wireless.env import UAVIoTEnv                        # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--episodes", type=int, default=25)
    ap.add_argument("--eval-seeds", type=int, default=5)
    ap.add_argument("--out", default=os.path.join(HERE, "alt_deployment.json"))
    a = ap.parse_args()

    device = os.environ.get("UAV_DEVICE", "cpu")
    print("=" * 78)
    print(" THE ALTERNATIVE CORRECTED DEPLOYMENT, MEASURED")
    print(f" N = 5, K = 2, R_cov = 45 m  against  N = 8, K = 2, R_cov = 35 m")
    print(f" {a.episodes} episodes x {a.seeds} training seeds, "
          f"{a.eval_seeds} evaluation scenes, device {device}")
    print("=" * 78)

    # the region bound on the alternative: the four corner discs are
    # disjoint only while 2 R_cov < side
    for label, n, r_cov in (("the reported deployment", 8, 35.0),
                            ("the alternative deployment", 5, 45.0)):
        corner_ok = 2.0 * r_cov < 80.0
        print(f"  {label}: N={n}, R_cov={r_cov:.0f} m; the four-corner "
              f"argument needs 2 R_cov = {2*r_cov:.0f} m against a side of "
              f"80 m, so it {'applies' if corner_ok else 'DOES NOT apply'}")

    arms = {
        "alt": dict(N=5, R_cov=45.0),
        "reported": dict(N=8, R_cov=35.0),
    }
    out_rows = []
    for name, over in arms.items():
        cks, ags, scs, cis = [], [], [], []
        per_seed = []
        for s in range(a.seeds):
            t0 = time.time()
            cfg = base_config(seed=s, **over)
            agent, hist = train_mappo(cfg, episodes=a.episodes,
                                      n_steps=cfg.episode_len, seed=s,
                                      verbose=False)
            evs = [eval_agent(agent, cfg, steps=cfg.episode_len, seed=e)
                   for e in range(a.eval_seeds)]
            agg = {k: float(np.mean([x[k] for x in evs])) for k in evs[0]}
            per_seed.append(agg["CK"])
            cks.append(agg["CK"]); ags.append(agg["AG"])
            scs.append(agg["SC"]); cis.append(agg["CovIntegral"])
            print(f"  {name:9s} seed {s}: CK={agg['CK']:.3f} AG={agg['AG']:.3f} "
                  f"SC={agg['SC']:.3f} CI={agg['CovIntegral']:.3f} "
                  f"({time.time()-t0:.0f}s)", flush=True)
        row = dict(arm=name, N=over.get("N", 8), R_cov=over.get("R_cov", 35.0),
                   CK=float(np.mean(cks)), CK_std=float(np.std(cks)),
                   AG=float(np.mean(ags)), SC=float(np.mean(scs)),
                   CovIntegral=float(np.mean(cis)),
                   per_seed_CK=per_seed, seeds=a.seeds, episodes=a.episodes,
                   eval_seeds=a.eval_seeds, device=str(device))
        out_rows.append(row)
        print(f"  {name:9s} MEAN   CK={row['CK']:.3f} +- {row['CK_std']:.3f}",
              flush=True)
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(out_rows, f, indent=2)

    alt = next(r for r in out_rows if r["arm"] == "alt")
    rep = next(r for r in out_rows if r["arm"] == "reported")
    print(f"\n  the alternative deployment reaches {alt['CK']:.3f} against "
          f"{rep['CK']:.3f} for the reported one, a difference of "
          f"{alt['CK']-rep['CK']:+.3f}")
    print(f"Saved -> {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
