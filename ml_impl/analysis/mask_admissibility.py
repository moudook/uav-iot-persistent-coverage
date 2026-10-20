"""
Does the safety filter admit the configurations the paper's own feasibility
certificate relies on?

TWO CHECKS
  1. The achievability construction.  The feasibility section exhibits 4K
     discs at the 2x2 cell centres, each layer displaced by a vector of
     norm <= R_cov - (S/2)*sqrt(2)/2, and shows that they K-cover the
     square.  If the simulator's action mask REJECTS that configuration, the
     achievability ceiling is not reachable by any policy and the ceiling
     is not comparable with what a policy can do.

  2. The connectivity guarantee.  The mask rejects any move whose
     prospective graph is disconnected, and the joint projection restores
     connectivity.  So the graph should be connected at EVERY step of a
     trajectory, and AG should be 1.000 -- unless a UAV LEAVES the active
     set (a failure, or a pack that empties away from a pad), in which case
     the remaining graph can fragment.  The two causes must be separated:
     a filter leak and a removal are different findings.

Run:  python analysis/mask_admissibility.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np

from uav_wireless.env import SimConfig, UAVIoTEnv
from uav_wireless.experiments import base_config

HERE = os.path.dirname(os.path.abspath(__file__))


def graph_properties(env):
    act, adj, _ = env.comm_graph()
    n = len(act)
    if n < 2:
        return dict(connected=True, ecc=0, artics=0, n=n)
    # eccentricity and articulation points
    ecc = 0
    for i in range(n):
        d = np.full(n, -1)
        d[i] = 0
        q = [i]
        while q:
            u = q.pop(0)
            for v in range(n):
                if adj[u, v] and d[v] < 0:
                    d[v] = d[u] + 1
                    q.append(v)
        ecc = max(ecc, int(d.max()))
    ap = env.articulation_points(adj)
    return dict(connected=bool(env.is_connected(adj)), ecc=ecc,
                artics=int(np.sum(ap)), n=n)


def check_constructions():
    cfg = base_config()
    S, R = cfg.side, cfg.R_cov
    margin = R - (S / 2.0) * np.sqrt(2.0) / 2.0
    base = [(S / 4, S / 4), (3 * S / 4, S / 4), (S / 4, 3 * S / 4),
            (3 * S / 4, 3 * S / 4)]
    constructions = {}

    # the paper's construction: two layers, each displaced by <= margin
    pos = []
    for layer in range(cfg.K):
        for k, (cx, cy) in enumerate(base):
            ang = 2 * np.pi * k / 4 + layer
            pos.append((cx + margin * np.cos(ang),
                        cy + margin * np.sin(ang)))
    constructions["paper's construction (2 layers)"] = pos

    # the 8-node ring, a valid covering family
    rad = 40.0
    constructions["8-node ring"] = [(rad * np.cos(2 * np.pi * i / 8),
                                      rad * np.sin(2 * np.pi * i / 8))
                                     for i in range(8)]

    # the plain 2x2 grid (4 UAVs is not the fleet, but the geometry)
    constructions["2x2 cell centres"] = base

    print("=" * 88)
    print(" IS THE CONSTRUCTION ADMITTED BY THE ACTION MASK?")
    print("=" * 88)
    for name, pos in constructions.items():
        env = UAVIoTEnv(cfg)
        env.reset()
        p = np.array(pos, dtype=float)
        if len(p) != cfg.N:
            # pad with the remaining positions of the base set
            p = np.concatenate([p, np.array(base)[:cfg.N - len(p)]])
        env.p[:] = p[:cfg.N]
        gp = graph_properties(env)
        # the mask admits HOLD for every agent iff the prospective graph is
        # connected and the mover is not an articulation point
        mask = env.action_masks()
        hover_ok = bool(mask[0][0])
        print(f"\n  {name}")
        print(f"    graph: connected={gp['connected']} eccentricity={gp['ecc']} "
              f"articulation points={gp['artics']}")
        print(f"    the mask admits HOLD for agent 0: {hover_ok}   "
              f"(the H-hop rule rejects a move whose prospective graph has a "
              f"node more than {cfg.mask_horizon} hops away)")
        if not gp["connected"]:
            print("    -> NOT ADMISSIBLE: the graph is disconnected")
        elif gp["ecc"] > cfg.mask_horizon:
            print(f"    -> NOT ADMISSIBLE under the H={cfg.mask_horizon} rule: "
                  f"eccentricity {gp['ecc']} > {cfg.mask_horizon}")
        elif gp["artics"] > 0:
            print("    -> NOT ADMISSIBLE: the graph has articulation points")
        else:
            print("    -> admissible")


def check_connectivity_cause():
    """Separate a filter leak from a removal.

    A filter leak is a step in which the graph is disconnected while every
    UAV is still active.  A removal is a step in which the graph is
    disconnected because a UAV left the active set (a failure, or a pack
    that emptied away from a pad).
    """
    cfg = base_config()
    env = UAVIoTEnv(cfg)
    env.reset()
    leak = removal = 0
    steps = 0
    rng = np.random.default_rng(0)
    for _ in range(cfg.episode_len):
        mask = env.action_masks()
        acts = np.array([rng.choice(np.flatnonzero(mask[i] + 1))
                         for i in range(cfg.N)], dtype=np.int64)
        before = len(env._active_idx())
        env.step(acts)
        after = len(env._active_idx())
        act, adj, _ = env.comm_graph()
        steps += 1
        if len(act) >= 2 and not env.is_connected(adj):
            if after < before:
                removal += 1
            else:
                leak += 1
    print()
    print("=" * 88)
    print(" IS THE GRAPH EVER DISCONNECTED WITH EVERY UAV STILL ACTIVE?")
    print("=" * 88)
    print(f"  steps                                     : {steps}")
    print(f"  disconnected because a UAV LEFT the active set : {removal}")
    print(f"  disconnected with every UAV still active      : {leak}")
    if leak == 0:
        print("  -> the safety filter never leaks: the graph is connected at")
        print("     every step in which the active set is unchanged.  A")
        print("     connectivity availability below 1.000 is therefore a")
        print("     consequence of UAVs LEAVING the active set (a failure, or")
        print("     a pack that empties away from a pad), not of the filter.")
    else:
        print("  -> THE FILTER LEAKS: the graph is disconnected with every UAV")
        print("     still active, so the safety filter does not maintain the")
        print("     connectivity invariant it claims.")


def main():
    check_constructions()
    check_connectivity_cause()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
