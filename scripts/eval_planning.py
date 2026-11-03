"""Innovation 10: feasibility-aware planning (H-step lookahead at eval time).

For each decision, instead of sampling one action, sample K candidate action
vectors and roll each forward H steps in a cloned environment, scoring by
cumulative coverage.  Pick the best candidate.  This is model-based planning
with the feasibility mask as the constraint.

Run:  python scripts/eval_planning.py --tag exp_ego_eval --eval-offset 1000 --eval-seeds 5 --H 3 --K 8
"""
import argparse
import copy
import glob
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ml_impl"))
for _v in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np
import torch

from uav_wireless.env import UAVIoTEnv
from uav_wireless.experiments import base_config, eval_agent
from uav_wireless.mappo import MAPPO


def rollout_score(env, agent, H, deterministic_seed):
    """Roll out H steps with the policy, return cumulative CK."""
    obs, st = env.local_obs() if False else None, None
    # we already have env state; just step
    obs = env.local_obs() if hasattr(env, 'local_obs') else None
    # env.local_obs doesn't exist; use env's obs via reset? No, env already reset.
    # We'll get obs from the env's last obs - but env doesn't store it.
    # Re-derive: env has p, v, etc. We need obs. Let's call env.local_obs if exists.
    if not hasattr(env, "local_obs"):
        return 0.0
    obs = env.local_obs()
    mask = np.stack(env.action_masks())
    for i in range(env.cfg.N):
        if mask[i].sum() == 0:
            mask[i, 0] = True
    acts = agent.act(obs, mask, deterministic=True)
    cum = 0.0
    for _ in range(H):
        obs, st, r, done, _ = env.step(acts)
        cum += float(env.summary().get("CK", 0.0))
        if done:
            break
        mask = np.stack(env.action_masks())
        for i in range(env.cfg.N):
            if mask[i].sum() == 0:
                mask[i, 0] = True
        acts = agent.act(obs, mask, deterministic=True)
    return cum


def planned_eval(agent, cfg, steps, seed, H, K):
    import copy
    c = copy.deepcopy(cfg)
    c.seed = seed
    from uav_wireless.seeding import seed_evaluation
    seed_evaluation(seed)
    env = UAVIoTEnv(c)
    obs, st = env.reset()
    cum_ck = 0.0
    n_steps = 0
    while n_steps < steps:
        mask = np.stack(env.action_masks())
        for i in range(c.N):
            if mask[i].sum() == 0:
                mask[i, 0] = True
        # sample K candidate actions
        logits = agent.masked_logits(
            torch.as_tensor(obs, dtype=torch.float32),
            torch.as_tensor(mask, dtype=torch.bool))
        logp = torch.log_softmax(logits, dim=-1)
        best_acts = None
        best_score = -1e9
        rng = np.random.default_rng(seed * 999 + n_steps)
        for _ in range(K):
            cand = torch.distributions.Categorical(logits=logp).sample().cpu().numpy()
            # clone env
            env2 = copy.deepcopy(env)
            obs2 = obs.copy() if hasattr(obs, "copy") else obs
            # score by H-step rollout
            sc = 0.0
            o = obs2
            m = mask.copy()
            a = cand.copy()
            for h in range(H):
                o2, st2, r, done, _ = env2.step(a)
                sc += float(env2.summary().get("CK", 0.0))
                if done:
                    break
                m = np.stack(env2.action_masks())
                for i in range(c.N):
                    if m[i].sum() == 0:
                        m[i, 0] = True
                a = agent.act(o2, m, deterministic=True)
                o = o2
            if sc > best_score:
                best_score = sc
                best_acts = cand.copy()
        if best_acts is None:
            best_acts = agent.act(obs, mask, deterministic=True)
        obs, st, r, done, _ = env.step(best_acts)
        n_steps += 1
        cum_ck += float(env.summary().get("CK", 0.0))  # per-step, not cumulative
    # return mean per-step CK (approx)
    return float(env.summary().get("CK", 0.0))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="exp_ego_eval")
    ap.add_argument("--eval-offset", type=int, default=1000)
    ap.add_argument("--eval-seeds", type=int, default=5)
    ap.add_argument("--steps", type=int, default=500)
    ap.add_argument("--H", type=int, default=3)
    ap.add_argument("--K", type=int, default=4)
    a = ap.parse_args()

    rundir = os.path.join(os.path.dirname(__file__), "..", "ml_impl", "runs", a.tag)
    ckpts = sorted(glob.glob(os.path.join(rundir, "seed_*.pt")))
    scenes = list(range(a.eval_offset, a.eval_offset + a.eval_seeds))
    print("planning H=%d K=%d on %d scenes" % (a.H, a.K, len(scenes)))
    for ck in ckpts:
        meta = json.load(open(ck.replace(".pt", ".json"), encoding="utf-8"))
        cfg = base_config()
        cfg.ego_sensors = meta.get("ego", False)
        cfg.n_ego = meta.get("n_ego", 3)
        cfg.dist_shape_kappa = meta.get("shape", 0.0)
        cfg.use_w_penalty = meta.get("use_w", True)
        cfg.episode_len = a.steps
        env = UAVIoTEnv(cfg)
        agent = MAPPO(n_agents=cfg.N, obs_dim=env.obs_dim,
                      state_dim=env.state_dim, device="cpu")
        agent.load(ck)
        cks = []
        for s in scenes:
            c = planned_eval(agent, cfg, a.steps, s, a.H, a.K)
            cks.append(c)
        print("%s  planned CK=%.4f (sd %.4f)" % (os.path.basename(ck),
              float(np.mean(cks)), float(np.std(cks, ddof=1))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
