"""Is the evaluation of a FIXED policy a function of the policy and the
scene?

The paper's audit item R1 says it is, and the claim audit's item T1 says
a training run is reproducible from its seed on a fixed device.  Two runs
of the energy arm, with the same script, the same environment, the same
device and the same seeds, gave different coverage for the same arm
(0.744 and 0.733) while their stranding and return counts were
identical -- so the training was identical and the EVALUATION was not.

This probe evaluates the SAME saved policy on the SAME scene twice, in
two processes, and prints the hashes of the trajectory so that a
difference can be located rather than merely noticed.

Run:  python analysis/repro_probe.py [--hashseed 0]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ML = os.path.dirname(HERE)
sys.path.insert(0, ML)

from uav_wireless.experiments import base_config, eval_agent   # noqa: E402
from uav_wireless.env import UAVIoTEnv                    # noqa: E402
from uav_wireless.mappo import MAPPO                      # noqa: E402
import torch                                              # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--policy", default=os.path.join(ML, "mappo_base_s0.pt"))
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--hashseed", default=os.environ.get("PYTHONHASHSEED", "?"))
    a = ap.parse_args()

    print(f"PYTHONHASHSEED={a.hashseed}  "
          f"torch threads={torch.get_num_threads()}  "
          f"device={os.environ.get('UAV_DEVICE', 'cpu')}")

    cfg = base_config(seed=a.seed)
    agent = MAPPO(n_agents=cfg.N,
                  obs_dim=UAVIoTEnv(cfg).obs_dim,
                  state_dim=UAVIoTEnv(cfg).state_dim)
    agent.load(a.policy)
    evs = [eval_agent(agent, cfg, steps=cfg.episode_len, seed=e)
           for e in range(3)]
    for i, e in enumerate(evs):
        print(f"  scene {i}: CK={e['CK']:.6f} AG={e['AG']:.6f} "
              f"SC={e['SC']:.6f} Stranded={e['Stranded']:.6f} "
              f"ReturnEvents={e['ReturnEvents']:.6f}")
    h = hashlib.sha256(json.dumps(
        [{k: float(v) for k, v in e.items() if isinstance(v, (int, float))}
         for e in evs], sort_keys=True).encode()).hexdigest()
    print(f"  the digest of the three evaluations: {h[:32]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
