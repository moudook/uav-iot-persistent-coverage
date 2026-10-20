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

    print("=" * 88)
    print(" A/B: is the credit assignment the limitation?")
    print(f" clustered start, {args.episodes} episodes x 2000 steps, "
          f"{args.seeds} training seeds, {args.eval_seeds} eval seeds")
    print("=" * 88)

    rows = []
    for name, trainer, evaluator, kw in [
            ("A: shared actor + centralised critic", train_mappo, eval_agent,
             dict(n_steps=None)),
            ("B: per-agent actor + local critic", train_ppo_local,
             eval_ppo_local, dict(steps=None))]:
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
                         CovIntegral=float(np.mean(cis)),
                         per_seed_CK=cks))

    out = os.path.join(HERE, "ab_credit.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)
    print(f"\nSaved -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
