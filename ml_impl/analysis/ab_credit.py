"""
A/B: is the credit assignment the limitation?

THE REMEDY THE DIAGNOSIS IMPLIES
  The diagnosis is that a parameter-shared actor trained on a team reward
  cannot learn a division of labour: every agent receives the SAME
  advantage, so the gradient cannot distinguish an agent whose action
  helped from one whose action was irrelevant.  The remedy is a per-agent
  signal.

THE TWO ARMS
  A  the proposed method: a parameter-shared actor with a centralised
     critic, so the advantage is a broadcast team signal.
  B  the same learner with the credit changed and nothing else: a
     per-agent actor and a per-agent LOCAL critic on the agent's own
     observation, so the advantage is the agent's own.

  Both use the same simulator, the same observation, the same action mask,
  the same team reward and the same episode budget.  The only difference
  is whose advantage the gradient sees.  If B is much better than A, the
  diagnosis is confirmed and the remedy is demonstrated.  If they are the
  same, the diagnosis is wrong and the paper must say so.

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
