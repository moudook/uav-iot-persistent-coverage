"""
Where does the connectivity availability below 1.000 come from?

The paper claims that the JOINT PROJECTION restores connectivity after a
set of individually admissible moves that would jointly disconnect the
swarm.  If that were the whole story, the connectivity availability AG
would be 1.000 for every controller, because the swarm starts connected
and the projection restores the previous (connected) configuration when it
cannot repair the new one.

The measured AG is 0.964 to 0.998, so something else is going on.  The
candidate is the ACTIVE SET: a UAV whose pack empties away from a pad
leaves the swarm, and a failure removes a UAV, and the graph is computed
over the UAVs that are still active.  Removing a node can disconnect the
graph that the projection had kept connected.

This script measures the accounting directly: at every step it records
whether the graph is connected and whether any UAV left the active set
during that step.  It then reports the two cases separately:

  * DISCONNECTED WITH NO ACTIVE-SET CHANGE: this would be a HOLE in the
    projection, and it is the thing the paper's claim must survive.
  * DISCONNECTED AFTER AN ACTIVE-SET CHANGE: the invariant was broken by
    a UAV leaving, not by a move.

Run:  python analysis/connectivity_accounting.py [--episodes 3]
"""

from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from uav_wireless.env import UAVIoTEnv
from uav_wireless.experiments import base_config

HERE = os.path.dirname(os.path.abspath(__file__))


def account(seed, steps, policy="random", agent=None, eval_seed=None):
    """One episode, with the connectivity accounting at every step.

    Three mechanisms can break the connectivity invariant, and they are
    told apart here:

      * an UAV LEAVES the active set (its pack empties away from a pad);
      * an UAV is TELEPORTED to a charging pad by the reserve mechanism,
        which can put it out of communication range of the swarm -- and
        the number of active UAVs does not change, so a count comparison
        alone cannot see it;
      * neither, in which case the joint projection has failed.
    """
    cfg = base_config()
    cfg.seed = seed
    env = UAVIoTEnv(cfg)
    obs, _ = env.reset()
    rows = []
    was_connected = True
    for t in range(steps):
        mask = np.stack(env.action_masks())
        for i in range(cfg.N):
            if mask[i].sum() == 0:
                mask[i, 0] = True
            if policy == "random":
                valid = np.nonzero(mask[i])[0]
                acts_i = int(valid[np.random.randint(len(valid))])
            else:
                acts_i = 0
        if agent is not None:
            acts = np.asarray(agent.act(obs, mask, deterministic=False))
        else:
            acts = np.array([acts_i] * cfg.N, dtype=np.int64)
        before = len(env._active_idx())
        p_before = env.p.copy()
        failed_before = env.failed.copy()
        obs, _, _, done, _ = env.step(acts)
        after = len(env._active_idx())
        act, adj, _ = env.comm_graph()
        connected = env.is_connected(adj)
        # only a TRANSITION into disconnection is a new event: a graph that
        # was already disconnected stays disconnected, and the cause is in
        # an earlier step
        if not connected and was_connected:
            teleported = int(np.sum(
                np.linalg.norm(env.p - p_before, axis=1) > 2.0))
            left = int(np.sum(failed_before & ~env.failed))
            revived = int(np.sum(~failed_before & env.failed))
            rows.append(dict(t=t, n_active_before=before,
                             n_active_after=after, left=(after < before),
                             teleported=teleported, left_agents=left,
                             revived_agents=revived,
                             policy_seed=seed, eval_seed=eval_seed))
        was_connected = connected
        if done:
            break
    return rows


def load_agent(policy_seed):
    from uav_wireless.env import UAVIoTEnv as _E
    from uav_wireless.mappo import MAPPO
    cfg = base_config()
    agent = MAPPO(n_agents=cfg.N, obs_dim=_E(cfg).obs_dim,
                  state_dim=_E(cfg).state_dim)
    agent.load(f"mappo_base_s{policy_seed}.pt")
    return agent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=int, default=3)
    ap.add_argument("--steps", type=int, default=2000)
    ap.add_argument("--policy", default="random",
                    choices=["random", "mappo"])
    ap.add_argument("--full", action="store_true",
                    help="every stored policy on every evaluation scene, "
                         "which is what the reported availability averages")
    args = ap.parse_args()
    rows = []
    if args.full:
        # the reported AG is the mean over the TRAINING runs and the
        # evaluation scenes, so the accounting has to cover the same set
        for ps in range(5):
            agent = load_agent(ps)
            for es in range(5):
                rows.extend(account(ps, args.steps, policy="mappo",
                                    agent=agent, eval_seed=es))
    else:
        agent = None
        if args.policy == "mappo":
            agent = load_agent(0)
        for s in range(args.episodes):
            rows.extend(account(s, args.steps, policy=args.policy,
                                agent=agent))
    n = len(rows)
    by_left = sum(1 for r in rows if r["left"])
    by_tel = sum(1 for r in rows if r.get("teleported", 0) > 0)
    unexplained = [r for r in rows
                    if not r["left"] and r.get("teleported", 0) == 0]
    print(f"policy: {args.policy}{' (full matrix)' if args.full else ''}")
    print(f"disconnected steps: {n}")
    print(f"  an UAV left the active set           : {by_left}")
    print(f"  an UAV was teleported to a pad       : {by_tel}")
    print(f"  UNEXPLAINED (a hole in the filter)  : {len(unexplained)}")
    if unexplained:
        print("  first unexplained steps:",
              [(r["t"], r["n_active_before"], r["n_active_after"])
               for r in unexplained[:6]])
    out = os.path.join(HERE, "connectivity_accounting.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(dict(policy=args.policy, full=bool(args.full),
                       disconnected_steps=n, after_active_set_change=by_left,
                       after_teleport=by_tel,
                       unexplained=len(unexplained), rows=rows),
                  f, indent=2)
    print(f"Saved -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
