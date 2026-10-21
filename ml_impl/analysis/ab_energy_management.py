"""
The energy-management diagnosis, and the fix.

THE OBSERVATION
  The step-level diagnosis (analysis/why_disconnect.py) showed that the
  learned policy strands ALL EIGHT UAVs in every episode, while the
  Reactive heuristic strands 0.7.  A UAV that strands has an empty pack
  away from a charging pad: it can no longer fly, it leaves the swarm, and
  it stops covering.  The learned policy is not primarily failing at
  coverage, it is failing at ENERGY MANAGEMENT -- it does not learn to turn
  back in time.

WHY
  The reward's energy term prices what is CONSUMED.  Flying 30 m to a pad
  costs about 480 J, which is 1.6% of a 30 kJ pack, so the energy term
  contributes about 0.0016 to the cost.  The cost of arriving home is
  instead paid LATE and by the team: the UAV leaves the swarm, the coverage
  deficit rises, and the graph may fragment.  A consumption term cannot
  teach a controller to turn back before the consequence arrives.

  The fix follows the paper's own metric table, which already lists
  "minimum battery level, and threshold violations" under Energy: a cost
  term for the shortfall below the return threshold, which is exactly the
  return-urgency feature the observation already carries.

THE THREE ARMS
  A  as-is                    the consumption term only
  B  no energy constraint    the same policy with a pack that cannot run
                              out.  If the diagnosis is right, the coverage
                              jumps; if it is wrong, it does not.
  C  + threshold violation   the proposed term.

Run:  python analysis/ab_energy_management.py [--episodes 40] [--seeds 2]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# The BLAS thread pools are pinned to one thread BEFORE numpy loads
# them: each process otherwise starts a pool sized for the whole
# machine, and a handful of processes exhaust the paging file.
import os as _os
for _v in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "OMP_NUM_THREADS", "NUMEXPR_NUM_THREADS",
           "VECLIB_MAXIMUM_THREADS"):
    _os.environ.setdefault(_v, "1")
import numpy as np

from uav_wireless.experiments import base_config, eval_agent
from uav_wireless.train import train_mappo

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=int, default=40)
    ap.add_argument("--seeds", type=int, default=2)
    ap.add_argument("--eval-seeds", type=int, default=3)
    ap.add_argument("--lam-B", type=float, default=2.0)
    args = ap.parse_args()

    # The four arms differ from arm A in one respect each, and they share
    # arm A's TRAINING SEEDS, so the comparison between an arm and arm A is
    # paired: the difference is measured on the same training runs and its
    # interval is a paired t interval.  A paired interval needs at least
    # three training seeds to be worth reporting (with two, the interval
    # half-width is a multiple of twelve standard deviations), so the
    # script enforces that minimum rather than accepting a schedule that
    # cannot support the inference the paper draws from it.
    if args.seeds < 3:
        print(f"  (raising the training seeds from {args.seeds} to 3: a "
              f"paired interval over the shared seeds needs at least three)")
        args.seeds = 3

    arms = [
        ("A: the proposed configuration", dict(lam_B=2.0)),
        ("B: + a pack that cannot run out", dict(lam_B=2.0, B_max=300_000.0)),
        ("C: without the threshold term", dict(lam_B=0.0)),
        ("D: with the previous energy rule", dict(lam_B=2.0,
                                                 strict_energy_mask=False)),
    ]

    print("=" * 96)
    print(" A/B/C: is the learned policy failing at ENERGY MANAGEMENT?")
    print(f" clustered start, {args.episodes} episodes x 2000 steps, "
          f"{args.seeds} training seeds, {args.eval_seeds} eval seeds")
    print("=" * 96)

    rows = []
    out_path = os.path.join(HERE, "ab_energy_management.json")
    run_device = os.environ.get("UAV_DEVICE", "cpu")
    # RESUME.  The arms are written as they finish, so an interrupted run
    # does not repeat the training it has already done, and an arm measured
    # under a different protocol (a different budget or a different number
    # of training seeds) is never reused.
    done = {}
    if os.path.exists(out_path):
        try:
            for r in json.load(open(out_path, encoding="utf-8")):
                if (int(r.get("episodes", -1)) == int(args.episodes)
                        and int(r.get("seeds", -1)) == int(args.seeds)
                        and int(r.get("eval_seeds", -1)) == int(args.eval_seeds)
                        and str(r.get("device", "")) == run_device):
                    done[r["arm"]] = r
        except Exception:
            done = {}

    def write_out():
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=2)

    for name, kw in arms:
        if name in done:
            rows.append(done[name])
            print(f"--- {name} --- reused from a previous run "
                  f"(CK={done[name]['CK']:.3f})", flush=True)
            write_out()
            continue
        print(f"\n--- {name} ---", flush=True)
        cks, ags, scs, cis, strs, rets = ([] for _ in range(6))
        for s in range(args.seeds):
            t0 = time.time()
            c = base_config(seed=s, **kw)
            agent, hist = train_mappo(c, episodes=args.episodes,
                                      n_steps=c.episode_len, seed=s,
                                      verbose=False)
            evs = [eval_agent(agent, c, steps=c.episode_len, seed=e)
                   for e in range(args.eval_seeds)]
            device_used = str(agent.device)
            agg = {k: float(np.mean([x[k] for x in evs])) for k in evs[0]}
            cks.append(agg["CK"]); ags.append(agg["AG"]); scs.append(agg["SC"])
            cis.append(agg["CovIntegral"])
            strs.append(float(np.mean([h.get("Stranded", 0)
                                        for h in hist[-5:]])))
            rets.append(float(np.mean([h.get("ReturnEvents", 0)
                                        for h in hist[-5:]])))
            print(f"  seed {s}: CK={agg['CK']:.3f} AG={agg['AG']:.3f} "
                  f"SC={agg['SC']:.3f} CI={agg['CovIntegral']:.3f} "
                  f"stranded/ep={strs[-1]:.1f} returns/ep={rets[-1]:.1f} "
                  f"({time.time()-t0:.0f}s)", flush=True)
        print(f"  {name:32s} CK={np.mean(cks):.3f}±{np.std(cks):.3f} "
              f"AG={np.mean(ags):.3f} SC={np.mean(scs):.3f} "
              f"CI={np.mean(cis):.3f} stranded/ep={np.mean(strs):.1f} "
              f"returns/ep={np.mean(rets):.1f}", flush=True)
        rows.append(dict(arm=name, **kw,
                         CK=float(np.mean(cks)), CK_std=float(np.std(cks)),
                         AG=float(np.mean(ags)), SC=float(np.mean(scs)),
                         CovIntegral=float(np.mean(cis)),
                         stranded_per_episode=float(np.mean(strs)),
                         return_events_per_episode=float(np.mean(rets)),
                         per_seed_CK=cks,
                         device=str(device_used),
                         episodes=int(args.episodes),
                         seeds=int(args.seeds),
                         eval_seeds=int(args.eval_seeds)))
        # the artefact is written after every arm, so an interrupted run
        # keeps the arms it has already measured
        write_out()

    write_out()
    print(f"\nSaved -> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
