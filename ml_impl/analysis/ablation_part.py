"""Run part of the component ablation, into its own CSV.

The ablation is the longest job in the matrix: twelve variants, each
trained once per training seed, and it is the critical path of the whole
paper, because the component table's paired intervals are what the
paper's component claims rest on.  Run as one process it takes about
eleven hours.  The machine has twelve logical cores and each training run
is single-threaded, so the variants are split across processes instead
and each part writes to its OWN csv and its OWN resume log, which keeps
the parts from interfering with each other.

    python analysis/ablation_part.py --part a --episodes 25 --seeds 8 \\
        --eval-seeds 5
    python analysis/merge_ablation.py     # the parts -> results_ablation.csv
"""

from __future__ import annotations

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ML = os.path.dirname(HERE)
sys.path.insert(0, ML)

# The BLAS thread pools are pinned to one thread BEFORE numpy loads
# them: each process otherwise starts a pool sized for the whole
# machine, and a handful of processes exhaust the paging file.
import os as _os
for _v in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "OMP_NUM_THREADS", "NUMEXPR_NUM_THREADS",
           "VECLIB_MAXIMUM_THREADS"):
    _os.environ.setdefault(_v, "1")
from uav_wireless.experiments import base_config, run_ablation   # noqa: E402

# The split.  "Full" and "VanillaMAPPO" are the two ends of the table
# and go to the same part, so that a part is never made of only the
# middle of the comparison.
PARTS = {
    "a": ["Full", "no-criticality", "no-degraded", "no-energy-cost",
          "no-undercoverage", "no-reserve"],
    "b": ["no-arbitration", "no-mask", "no-agent-id", "no-map",
          "no-pad-bearing", "VanillaMAPPO"],
    "stress_a": ["Full", "no-criticality", "no-degraded", "no-energy-cost",
                 "no-undercoverage", "no-reserve"],
    "stress_b": ["no-arbitration", "no-mask", "no-agent-id", "no-map",
                 "no-pad-bearing", "VanillaMAPPO"],
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", required=True, choices=sorted(PARTS))
    ap.add_argument("--episodes", type=int, default=25)
    ap.add_argument("--seeds", type=int, default=8)
    ap.add_argument("--eval-seeds", type=int, default=5)
    ap.add_argument("--out", default="")
    a = ap.parse_args()

    stress = a.part.startswith("stress")
    key = a.part[-1]
    out = a.out or os.path.join(
        ML, f"results_ablation{'_stress' if stress else ''}_part{key}.csv")
    cfg = base_config()
    run_ablation(cfg, out, stress=stress, episodes=a.episodes,
                 eval_seeds=a.eval_seeds, seeds=a.seeds,
                 only=PARTS[a.part])
    print(f"\npart {a.part} -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
