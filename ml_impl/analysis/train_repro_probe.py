"""Is a training run reproducible from its seed, on a fixed device?

The paper's claim audit item T1 says it is.  Two runs of the energy
arm -- the same script, the same arguments, the same environment, the
same pinned device -- gave different coverage for the same arm and the
same training seed (0.744 and 0.733), so the claim is under test.

This trains the same configuration twice, in one process, and compares
the resulting weights and the per-episode history.

Run:  python analysis/train_repro_probe.py [--episodes 2]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
ML = os.path.dirname(HERE)
sys.path.insert(0, ML)

from uav_wireless.experiments import base_config          # noqa: E402
from uav_wireless.train import train_mappo                # noqa: E402


def weights_digest(agent):
    h = hashlib.sha256()
    for name, p in sorted(agent.actor.named_parameters()):
        h.update(name.encode())
        h.update(p.detach().cpu().numpy().tobytes())
    for name, p in sorted(agent.critic.named_parameters()):
        h.update(name.encode())
        h.update(p.detach().cpu().numpy().tobytes())
    return h.hexdigest()[:32]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=int, default=2)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()

    print(f"device={os.environ.get('UAV_DEVICE', 'cpu')}  "
          f"threads={torch.get_num_threads()}  episodes={a.episodes}")

    digests, cks = [], []
    for run in range(2):
        cfg = base_config(seed=a.seed)
        agent, hist = train_mappo(cfg, episodes=a.episodes,
                                  n_steps=cfg.episode_len, seed=a.seed,
                                  verbose=False)
        d = weights_digest(agent)
        digests.append(d)
        cks.append([round(float(h["CK"]), 6) for h in hist])
        print(f"  run {run}: weights {d}  history {cks[-1]}")

    if digests[0] == digests[1] and cks[0] == cks[1]:
        print("  the two runs agree: the training IS reproducible from "
              "its seed")
        return 0
    print("  THE TWO RUNS DIFFER: the training is NOT reproducible from "
          "its seed on this device")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
