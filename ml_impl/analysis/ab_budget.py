"""
Is the training budget the explanation?  A sweep over it.

The audit's point was that a null in a single-budget arm says nothing
about the component, and that a component which matters only at a larger
budget is invisible at the one that was used.  It also asked for a
learning curve to answer the compute-asymmetry objection.

This sweeps the budget for the FULL configuration: the same configuration,
the same seeds, trained for 8, 16 and 25 episodes and evaluated on the
same scenes.  If the coverage does not move with the budget, then the
budget is not what the shortfall is made of -- which is the claim the
paper makes, and which a single budget cannot establish.

Run:  python analysis/ab_budget.py [--seeds 3] [--eval-seeds 5]
"""
from __future__ import annotations

import argparse
import json
import os
import sys

# The BLAS thread pools are pinned to one thread BEFORE numpy loads
# them: each process otherwise starts a pool sized for the whole
# machine, and a handful of processes exhaust the paging file.
import os as _os
for _v in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "OMP_NUM_THREADS", "NUMEXPR_NUM_THREADS",
           "VECLIB_MAXIMUM_THREADS"):
    _os.environ.setdefault(_v, "1")
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from uav_wireless.experiments import base_config, eval_agent
from uav_wireless.train import train_mappo

HERE = os.path.dirname(os.path.abspath(__file__))
BUDGETS = (8, 16, 25)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--eval-seeds", type=int, default=5)
    ap.add_argument("--budgets", default=",".join(str(b) for b in BUDGETS))
    args = ap.parse_args()
    budgets = [int(b) for b in args.budgets.split(",")]

    print("=" * 78)
    print(" A/B: is the shortfall made of the training budget?")
    print(f" budgets {budgets} episodes, {args.seeds} training seeds, "
          f"{args.eval_seeds} eval seeds, device "
          f"{os.environ.get('UAV_DEVICE', 'cpu')}")
    print("=" * 78)

    out_path = os.path.join(HERE, "ab_budget.json")
    cache_path = os.path.join(HERE, "ab_budget_cache.json")
    device = str(os.environ.get("UAV_DEVICE", "cpu"))
    # The training is the expensive part, and the server can restart in the
    # middle of a sweep.  Every finished (budget, seed) is therefore
    # cached with the PROTOCOL it was measured under, and a cached value
    # is reused only when the protocol matches exactly -- a row measured
    # at a different seed count, on a different device, or on a different
    # number of evaluation scenes is a different measurement.
    proto = dict(seeds=int(args.seeds), eval_seeds=int(args.eval_seeds),
                 device=device)
    cache = {}
    if os.path.exists(cache_path):
        try:
            blob = json.load(open(cache_path, encoding="utf-8"))
            if blob.get("protocol") == proto:
                cache = blob.get("rows", {})
            else:
                print("  the cache was measured under a different protocol "
                      "and is ignored")
        except Exception:
            cache = {}
    if cache:
        print(f"  resuming from the cache: {len(cache)} finished "
              f"(budget, seed) pairs")

    def save_cache():
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(dict(protocol=proto, rows=cache), f, indent=2)

    rows = []
    for b in budgets:
        cks = []
        for s in range(args.seeds):
            key = f"{b}:{s}"
            if key in cache:
                ck = float(cache[key])
                cks.append(ck)
                print(f"  budget {b:3d}  seed {s}: CK={ck:.3f} (cached)",
                      flush=True)
                continue
            c = base_config(seed=s)
            agent, hist = train_mappo(c, episodes=b, n_steps=c.episode_len,
                                      seed=s, verbose=False)
            evs = [eval_agent(agent, c, steps=c.episode_len, seed=e)
                   for e in range(args.eval_seeds)]
            ck = float(np.mean([e["CK"] for e in evs]))
            cks.append(ck)
            cache[key] = ck
            save_cache()
            print(f"  budget {b:3d}  seed {s}: CK={ck:.3f} "
                  f"(last training episode "
                  f"{hist[-1].get('CK', float('nan')):.3f})", flush=True)
        row = dict(episodes=b, CK=float(np.mean(cks)),
                   CK_std=float(np.std(cks, ddof=1)) if len(cks) > 1 else 0.0,
                   per_seed_CK=cks,
                   seeds=int(args.seeds), eval_seeds=int(args.eval_seeds),
                   device=device)
        rows.append(row)
        print(f"  budget {b:3d}  MEAN  CK={row['CK']:.3f} +- "
              f"{row['CK_std']:.3f}", flush=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=2)

    lo, hi = rows[0], rows[-1]
    spread = hi["CK"] - lo["CK"]
    print(f"\nthe coverage moves by {spread:+.3f} between the shortest and "
          f"the longest budget")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)
    print(f"Saved -> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
