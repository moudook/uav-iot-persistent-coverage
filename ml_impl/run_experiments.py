"""
Entry point. Run from Project1/ml_impl:

    python run_experiments.py main        # baselines vs MAPPO, 5 seeds
    python run_experiments.py ablation    # ablate each proposed component
    python run_experiments.py scenarios   # S1..S8 design matrix
    python run_experiments.py all         # everything (long)
"""

import sys
import time
from uav_wireless import SimConfig
from uav_wireless.experiments import run_base_comparison, run_ablation, run_scenarios


def base_cfg():
    # Feasible config: N=8 meets the corner-packing bound N>=4K=8 for K=2.
    # (N=5 was provably infeasible; see feasibility.py and the report's
    # corrected deployment parameters.)
    return SimConfig(N=8, K=2, R_cov=35.0, episode_len=400, seed=0)


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "main"
    c = base_cfg()
    t0 = time.time()
    if which in ("main", "all"):
        run_base_comparison(c, "results_main.csv")
    if which in ("ablation", "all"):
        run_ablation(c, "results_ablation.csv")
    if which in ("scenarios", "all"):
        run_scenarios(c, "results_scenarios.csv")
    print(f"\nTotal wall time: {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()