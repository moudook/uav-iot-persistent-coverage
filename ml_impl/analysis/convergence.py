"""
Is the proposed policy under-trained, or is it at its ceiling?

WHY
  The A/B/C on the observation (analysis/ab_observation.py) found that
  none of the three observation variants reaches the coverage of the rule-
  based heuristic, and that adding the agent identity -- which fixes the
  shared-actor symmetry collapse -- actually REDUCES coverage.  That points
  away from the observation and towards either (a) the credit assignment of
  a shared team reward, or (b) a training budget that has simply not
  converged yet.

  Hypothesis (b) is much cheaper to test, so it is tested first.  If the
  coverage is still rising at the end of the budget, the comparison so far
  has been a comparison of budgets rather than of methods.

WHAT THIS MEASURES
  The proposed configuration trained for up to 120 episodes, recording the
  per-episode training coverage and the per-episode evaluation coverage
  (sampled policy, Eq. (13)), so that the convergence curve is on the same
  axis as the reported number.

Run:  python analysis/convergence.py [--episodes 120] [--seeds 2]
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

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=int, default=120)
    ap.add_argument("--seeds", type=int, default=2)
    ap.add_argument("--eval-seeds", type=int, default=3)
    ap.add_argument("--eval-every", type=int, default=10)
    args = ap.parse_args()

    base = base_config()
    print("=" * 88)
    print(" CONVERGENCE: is the proposed policy under-trained?")
    print(f" clustered start, up to {args.episodes} episodes x "
          f"{base.episode_len} steps, {args.seeds} training seeds")
    print("=" * 88, flush=True)

    rows = []
    for s in range(args.seeds):
        c = base_config(seed=s)
        t0 = time.time()
        agent, hist = train_mappo(c, episodes=args.episodes,
                                  n_steps=c.episode_len, seed=s,
                                  log_every=max(1, args.episodes // 6),
                                  verbose=True)
        curve = []
        for ep in range(0, len(hist), args.eval_every):
            # the evaluation at this point in training
            snap = {k: v.clone() for k, v in agent.actor.state_dict().items()}
            # roll out the policy as it stands now is not possible without
            # a checkpoint, so the curve uses the TRAINING coverage, which is
            # measured with the same sampled policy and the same seeds.
            curve.append(dict(episode=ep,
                              train_ck=float(hist[ep]["CK"]),
                              train_ag=float(hist[ep]["AG"]),
                              train_sc=float(hist[ep]["SC"]),
                              entropy=float(hist[ep]["entropy"])))
        evs = [eval_agent(agent, c, steps=c.episode_len, seed=e)
               for e in range(args.eval_seeds)]
        agg = {k: float(np.mean([x[k] for x in evs])) for k in evs[0]}
        std = {k: float(np.std([x[k] for x in evs])) for k in evs[0]}
        print(f"  seed {s}: final eval CK={agg['CK']:.3f}±{std['CK']:.3f} "
              f"AG={agg['AG']:.3f} SC={agg['SC']:.3f} "
              f"CI={agg['CovIntegral']:.3f}  "
              f"best_train_ck={max(h['CK'] for h in hist):.3f} "
              f"({time.time()-t0:.0f}s)", flush=True)
        for c2 in curve:
            print(f"      ep {c2['episode']:4d}: train CK={c2['train_ck']:.3f} "
                  f"AG={c2['train_ag']:.3f} SC={c2['train_sc']:.3f} "
                  f"ent={c2['entropy']:.3f}", flush=True)
        rows.append(dict(seed=s, curve=curve,
                         final_CK=agg["CK"], final_CK_std=std["CK"],
                         final_AG=agg["AG"], final_SC=agg["SC"],
                         final_CovIntegral=agg["CovIntegral"],
                         best_train_ck=float(max(h["CK"] for h in hist)),
                         final_train_ck=float(hist[-1]["CK"])))

    out = os.path.join(HERE, "convergence.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)
    print(f"\nSaved -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
