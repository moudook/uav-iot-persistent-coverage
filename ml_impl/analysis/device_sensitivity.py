"""
How much does the DEVICE change a training run?

The paper says the device and the thread count are part of the protocol,
because the floating-point kernels differ between the CPU and the GPU and
the order of the reductions differs with the thread count.  That was an
assertion.  This measures it: the same configuration, the same seed, the
same budget, on

    * the CPU with one thread,
    * the CPU with two threads,
    * the GPU,

and it reports how far apart the resulting weights are, and how far apart
the resulting coverages are.

The point is not that the differences are large.  They are small.  The
point is that they are not ZERO, that they compound through the updates,
and that a protocol which does not record the device is a protocol that
cannot tell two runs of the same configuration apart.

Usage:  python analysis/device_sensitivity.py [--episodes 2]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
ML = os.path.dirname(HERE)
sys.path.insert(0, ML)

from uav_wireless.experiments import base_config, eval_agent   # noqa: E402
from uav_wireless.train import train_mappo                    # noqa: E402


def weights(agent):
    out = []
    for p in list(agent.actor.parameters()) + list(agent.critic.parameters()):
        out.append(p.detach().cpu().numpy().ravel())
    return np.concatenate(out)


def run(device, threads, episodes, seed=0, eval_seeds=3):
    os.environ["UAV_DEVICE"] = device
    torch.set_num_threads(threads)
    cfg = base_config(seed=seed)
    t0 = time.time()
    agent, hist = train_mappo(cfg, episodes=episodes, n_steps=cfg.episode_len,
                              seed=seed, verbose=False, device=device)
    evs = [eval_agent(agent, cfg, steps=cfg.episode_len, seed=e)
           for e in range(eval_seeds)]
    ck = float(np.mean([e["CK"] for e in evs]))
    return dict(device=device, threads=threads, CK=ck,
                weights=weights(agent), seconds=time.time() - t0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=int, default=2)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default=os.path.join(HERE, "device_sensitivity.json"))
    ap.add_argument("--config", default="all",
                    help="which configuration to run: cpu1, cpu2, cuda or all. "
                         "One configuration per process is how the three are "
                         "run in parallel, and the GPU is a configuration in "
                         "its own right.")
    a = ap.parse_args()

    configs = {"cpu1": ("cpu", 1), "cpu2": ("cpu", 2),
               "cuda": ("cuda", 1)}
    if a.config == "all":
        todo = list(configs.values())
    else:
        todo = [configs[a.config]]
    runs = []
    for device, threads in todo:
        if device == "cuda" and not torch.cuda.is_available():
            print("  no GPU: the CUDA run is skipped")
            continue
        r = run(device, threads, a.episodes, seed=a.seed)
        r["config"] = f"{device}{threads}"
        print(f"  {device} with {threads} thread(s): CK={r['CK']:.6f} "
              f"({r['seconds']:.0f}s)", flush=True)
        runs.append(r)

    if len(runs) < 2:
        print("  not enough runs to compare")
        return 0

    ref = runs[0]
    rows = []
    for r in runs[1:]:
        dw = float(np.max(np.abs(r["weights"] - ref["weights"])))
        dck = abs(r["CK"] - ref["CK"])
        rows.append(dict(other_device=r["device"], other_threads=r["threads"],
                         max_abs_weight_difference=dw,
                         coverage_difference=dck))
        print(f"  {r['device']} with {r['threads']} thread(s) against "
              f"{ref['device']} with {ref['threads']} thread(s): the "
              f"weights differ by at most {dw:.2e} and the coverage by "
              f"{dck:.6f}")

    payload = dict(
        episodes=a.episodes, seed=a.seed, reference="cpu with 1 thread",
        comparisons=rows,
        note=("the differences are small and they are not zero, which is "
              "why the device and the thread count are recorded with every "
              "artefact"))
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"Saved -> {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
