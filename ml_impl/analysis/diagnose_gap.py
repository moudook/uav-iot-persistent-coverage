"""
Diagnose the gap between the learned policy and the Reactive heuristic.

The scenario sweep showed the Reactive heuristic matching or beating MAPPO on
the sparse-sensor variant, which is the opposite of the base comparison.  This
script separates three candidate causes without retraining anything:

  1. evaluation protocol  -- deterministic (argmax) vs stochastic sampling
  2. policy sharpness     -- how far the actor is from uniform
  3. scenario regime      -- sensor count, which changes what is achievable

Run:  python analysis/diagnose_gap.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import torch

from uav_wireless.env import SimConfig, UAVIoTEnv
from uav_wireless.mappo import MAPPO
from uav_wireless.train import baseline_reactive, collect_rollout

HERE = os.path.dirname(os.path.abspath(__file__))


def eval_agent(agent, cfg, steps=400, seed=0, deterministic=True):
    import copy
    c = copy.deepcopy(cfg)
    c.seed = seed
    env = UAVIoTEnv(c)
    obs, st = env.reset()
    for _ in range(steps):
        mask = np.stack(env.action_masks())
        for i in range(c.N):
            if mask[i].sum() == 0:
                mask[i, 0] = True
        acts = agent.act(obs, mask, deterministic=deterministic)
        obs, st, r, done, _ = env.step(acts)
        if done:
            break
    return env.summary()


def main():
    ckpt = "mappo_base.pt"
    if not os.path.exists(ckpt):
        print(f"checkpoint not found: {ckpt}")
        return 2

    print("=" * 92)
    print(" GAP DIAGNOSIS: learned policy vs Reactive heuristic")
    print("=" * 92)

    for M, label in ((10, "S1 sparse (M=10)"), (20, "base (M=20)"),
                     (40, "S1 dense (M=40)")):
        cfg = SimConfig(N=8, K=2, R_cov=35.0, M=M, episode_len=400, seed=0)
        env = UAVIoTEnv(cfg)
        print(f"\n--- {label} ---")

        # The checkpoint's critic was trained at a specific state_dim, which
        # scales with M.  It can only be loaded for the configuration it was
        # trained on, so the learned policy is only compared where it exists.
        agent = None
        try:
            agent = MAPPO(n_agents=cfg.N, obs_dim=env.obs_dim,
                           state_dim=env.state_dim)
            agent.load(ckpt)
        except RuntimeError as exc:
            print(f"  (no learned policy for this M: {exc.args[0][:60]}...)")

        if agent is not None:
            for det in (True, False):
                evs = [eval_agent(agent, cfg, seed=s, deterministic=det)
                       for s in range(5)]
                ck = sum(e["CK"] for e in evs) / 5
                ag = sum(e["AG"] for e in evs) / 5
                sc = sum(e["SC"] for e in evs) / 5
                print(f"  MAPPO  deterministic={str(det):5s}  CK={ck:.3f} "
                      f"AG={ag:.3f} SC={sc:.3f}")

            # how sharp is the learned policy?
            batch, _ = collect_rollout(env, agent, n_steps=100)
            obs = torch.as_tensor(batch["obs"], dtype=torch.float32)
            mask = torch.as_tensor(batch["mask"], dtype=torch.bool)
            with torch.no_grad():
                logits = agent.masked_logits(obs, mask)
                p = torch.softmax(logits, dim=-1)
                p = p * mask
                p = p / p.sum(-1, keepdim=True).clamp(min=1e-9)
                ent = -(p * p.clamp(min=1e-9).log()).sum(-1)
            print(f"  policy entropy {ent.mean().item():.4f} "
                  f"(uniform over 6 actions = {np.log(6):.4f}, "
                  f"deterministic = 0)")

        rs = [baseline_reactive(cfg, steps=400, seed=s) for s in range(5)]
        ck = sum(e["CK"] for e in rs) / 5
        ag = sum(e["AG"] for e in rs) / 5
        sc = sum(e["SC"] for e in rs) / 5
        print(f"  Reactive heuristic              CK={ck:.3f} AG={ag:.3f} "
              f"SC={sc:.3f}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
