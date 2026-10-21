"""
A/B: is the credit assignment the limitation?

WHAT THIS ACTUALLY TESTS, PRECISELY
  The two arms differ in the learner that produces the advantage:

    A  the proposed method: a PARAMETER-SHARED actor with a CENTRALISED
       critic, so every agent receives the same broadcast team advantage.
    B  the same simulator, observation, action mask, team reward and episode
       budget, with a PER-AGENT actor and a PER-AGENT LOCAL critic, so each
       agent's advantage has its own baseline.

  It is worth being exact about what that does and does not change.  With a
  team reward r_t broadcast to every agent, the advantage is
  r_t + gamma V(o') - V(o).  Giving each agent its own value function
  changes the BASELINE of that expression, and therefore the variance of
  the advantage -- it does not change its SIGNAL, which is still the same
  team reward for every agent.  So arm B is a comparison of a per-agent
  BASELINE and of parameter sharing; it is NOT an implementation of the
  per-agent ADVANTAGE estimators of COMA, DAE or GPAE, which change the
  signal by supplying a per-agent reward (a difference reward) or a
  counterfactual baseline.

  This is the cheapest available test of the hypothesis, and the result
  has to be read with that scope in mind: if arm B does not close the gap,
  the correct conclusion is that a per-agent baseline and unshared
  parameters are not sufficient -- not that per-agent credit is
  insufficient, which is a different and more expensive experiment.

Run:  python analysis/ab_credit.py [--episodes 30] [--seeds 2]
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
from uav_wireless.baselines_rl import (train_ppo_local, eval_ppo_local)

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=int, default=30)
    ap.add_argument("--seeds", type=int, default=2)
    ap.add_argument("--eval-seeds", type=int, default=5)
    args = ap.parse_args()

    # the two arms share their training seeds, so the comparison between
    # them is paired; a paired interval needs at least three seeds
    if args.seeds < 3:
        print(f"  (raising the training seeds from {args.seeds} to 3: a "
              f"paired interval over the shared seeds needs at least three)")
        args.seeds = 3

    print("=" * 88)
    print(" A/B: is the credit assignment the limitation?")
    print(f" clustered start, {args.episodes} episodes x 2000 steps, "
          f"{args.seeds} training seeds, {args.eval_seeds} eval seeds")
    print("=" * 88)

    rows = []
    out_path = os.path.join(HERE, "ab_credit.json")
    run_device = os.environ.get("UAV_DEVICE", "cpu")
    # RESUME: an arm measured under the same protocol is reused, and the
    # artefact is written after every arm, so an interruption does not cost
    # the training that has already been done
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

    for name, trainer, evaluator, kw in [
            ("A: shared actor + centralised critic", train_mappo, eval_agent,
             dict(n_steps=None)),
            ("B: per-agent actor + local critic", train_ppo_local,
             eval_ppo_local, dict(steps=None))]:
        if name in done:
            rows.append(done[name])
            print(f"--- {name} --- reused from a previous run "
                  f"(CK={done[name]['CK']:.3f})", flush=True)
            write_out()
            continue
        print(f"\n--- {name} ---", flush=True)
        cks, ags, scs, cis = [], [], [], []
        for s in range(args.seeds):
            t0 = time.time()
            c = base_config(seed=s)
            kw = dict(kw)
            for k in list(kw):
                if kw[k] is None:
                    kw.pop(k)
            if trainer is train_mappo:
                kw["n_steps"] = c.episode_len
            else:
                kw["steps"] = c.episode_len
            agent, hist = trainer(c, episodes=args.episodes, seed=s,
                                  verbose=False, **kw)
            evs = [evaluator(agent, c, steps=c.episode_len, seed=e)
                   for e in range(args.eval_seeds)]
            device_used = str(getattr(agent, "device", "cpu"))
            agg = {k: float(np.mean([x[k] for x in evs])) for k in evs[0]}
            std = {k: float(np.std([x[k] for x in evs])) for k in evs[0]}
            cks.append(agg["CK"]); ags.append(agg["AG"]); scs.append(agg["SC"])
            cis.append(agg["CovIntegral"])
            best = max(h.get("CK", 0) for h in hist)
            print(f"  seed {s}: CK={agg['CK']:.3f}±{std['CK']:.3f} "
                  f"AG={agg['AG']:.3f} SC={agg['SC']:.3f} "
                  f"CI={agg['CovIntegral']:.3f} best_train_ck={best:.3f} "
                  f"({time.time()-t0:.0f}s)", flush=True)
        print(f"  {name:44s} CK={np.mean(cks):.3f}±{np.std(cks):.3f} "
              f"AG={np.mean(ags):.3f} SC={np.mean(scs):.3f} "
              f"CI={np.mean(cis):.3f}", flush=True)
        rows.append(dict(arm=name, CK=float(np.mean(cks)),
                         CK_std=float(np.std(cks)), AG=float(np.mean(ags)),
                         SC=float(np.mean(scs)),
                         device=str(device_used),
                         episodes=int(args.episodes), seeds=int(args.seeds),
                         eval_seeds=int(args.eval_seeds),
                         CovIntegral=float(np.mean(cis)),
                         per_seed_CK=cks))

        write_out()

    write_out()
    print(f"\nSaved -> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
