"""
Why does the learned policy lose connectivity?

THE OBSERVATION
  The convergence run shows the learned policy oscillating between two
  regimes: at ~20 episodes it is safe but does not deploy (CK 0.63,
  AG 1.000), and at ~40 episodes it deploys (CK 0.898) but the swarm is
  disconnected 39% of the time (AG 0.611).  The action mask is supposed to
  prevent exactly this.

  The hypothesis that has to be tested first is the simple one: a UAV that
  leaves the active set -- because it failed, or because its pack emptied
  away from a pad -- is removed from the communication graph, and if it was
  a cut vertex the swarm fragments.  A per-agent mask cannot prevent that,
  because the removal is not a move.

  This script records, per episode, the coverage, the connectivity, the
  number of UAVs that left the active set and the number of steps in which
  the graph was disconnected, and correlates the last two.

Run:  python analysis/why_disconnect.py [--episodes 45]
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np

from uav_wireless.env import SimConfig, UAVIoTEnv
from uav_wireless.experiments import base_config
from uav_wireless.train import train_mappo

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=int, default=45)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    base = base_config()
    print("=" * 96)
    print(" WHY DOES THE LEARNED POLICY LOSE CONNECTIVITY?")
    print("=" * 96)

    # Train episode by episode, and after each episode inspect the LAST
    # episode's trajectory: did a UAV leave the active set, and did the
    # graph fragment at the same time?
    agent, hist = train_mappo(base, episodes=args.episodes,
                              n_steps=base.episode_len, seed=args.seed,
                              log_every=5, verbose=True)

    print()
    print(f"{'ep':>4s}{'CK':>8s}{'AG':>8s}{'SC':>8s}{'Crit':>8s}"
          f"{'stranded':>10s}{'retEv':>8s}{'ent':>8s}")
    for h in hist:
        print(f"{h['episode']:>4d}{h['CK']:>8.3f}{h['AG']:>8.3f}"
              f"{h['SC']:>8.3f}{h['Crit']:>8.3f}"
              f"{h.get('Stranded', 0):>10.1f}{h.get('ReturnEvents', 0):>8.0f}"
              f"{h['entropy']:>8.3f}")

    # Now reproduce one episode and record exactly when the graph
    # fragments and whether a UAV left the active set at that moment.
    print()
    print("=== step-level diagnosis of one episode ===")
    cfg = base_config(seed=args.seed)
    from uav_wireless.seeding import seed_evaluation
    seed_evaluation(cfg.seed)
    env = UAVIoTEnv(cfg)
    obs, _ = env.reset()
    n_active = len(env._active_idx())
    frag_with_removal = 0
    frag_without_removal = 0
    removals = 0
    for t in range(cfg.episode_len):
        mask = np.stack(env.action_masks())
        for i in range(cfg.N):
            if mask[i].sum() == 0:
                mask[i, 0] = True
        acts = agent.act(obs, mask, deterministic=False)
        before = set(env._active_idx().tolist())
        obs, st, r, done, _ = env.step(acts)
        after = set(env._active_idx().tolist())
        if after != before:
            removals += 1
        act, adj, _ = env.comm_graph()
        if len(act) >= 2 and not env.is_connected(adj):
            if after != before:
                frag_with_removal += 1
            else:
                frag_without_removal += 1
        if done:
            break
    print(f"  steps                                  : {t+1}")
    print(f"  times a UAV left the active set        : {removals}")
    print(f"  steps with a fragmented graph          : "
          f"{frag_with_removal + frag_without_removal}")
    print(f"     of which coinciding with a removal  : {frag_with_removal}")
    print(f"     of which NOT                       : {frag_without_removal}")
    s = env.summary()
    print(f"  final: CK={s['CK']:.3f} AG={s['AG']:.3f} "
          f"stranded={s['Stranded']} projection_revisions="
          f"{s.get('ProjectionRevisions', 0)}")

    out = os.path.join(HERE, "why_disconnect.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(dict(history=hist,
                       frag_with_removal=frag_with_removal,
                       frag_without_removal=frag_without_removal,
                       removals=removals), f, indent=2)
    print(f"\nSaved -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
