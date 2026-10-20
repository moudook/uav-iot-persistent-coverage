"""
Rollout collector + MAPPO training loop + rule-based baselines (Table VIII).

Baselines:
  Fixed          — hold initial formation, recharge at a fixed threshold
  Greedy         — lowest battery wins the pad, same motion rule
  Reactive       — deterministic uncovered-sensor + connectivity heuristic
  Vanilla MAPPO  — same learner with the proposed design switched off
"""

from __future__ import annotations

import numpy as np
import torch

from .env import (
    A_HOVER, A_PX, A_NX, A_PY, A_NY, A_CHARGE, N_ACTIONS,
    UAVIoTEnv, SimConfig,
)
from .mappo import MAPPO


# ----------------------------------------------------------------------
# Rollout buffer
# ----------------------------------------------------------------------
def collect_rollout(env, agent, n_steps, deterministic=False):
    """
    Roll out one episode, recording per-agent transitions for the MAPPO update.
    Shared (team) reward is broadcast to every agent (Dec-POMDP, eq. 23).
    """
    obs, state = env.reset()
    n = env.cfg.N

    B = dict(
        obs=np.zeros((n_steps, n, env.obs_dim), np.float32),
        mask=np.zeros((n_steps, n, N_ACTIONS), bool),
        acts=np.zeros((n_steps, n), np.int64),
        logp=np.zeros((n_steps, n), np.float32),
        adv=np.zeros((n_steps, n), np.float32),
        ret=np.zeros((n_steps, n), np.float32),
        states=np.zeros((n_steps, env.state_dim), np.float32),
        values=np.zeros((n_steps, n), np.float32),
    )

    t = 0
    truncated = False
    while t < n_steps:
        mask = np.stack(env.action_masks())
        if mask.sum(axis=1).min() == 0:            # never leave an agent stuck
            for i in range(n):
                if mask[i].sum() == 0:
                    mask[i] = True
                    mask[i, A_HOVER] = True

        if agent is None:
            acts = np.zeros(n, dtype=np.int64)
            logp = np.zeros(n, np.float32)
        else:
            import torch
            acts = agent.act(obs, mask, deterministic=deterministic)
            obs_t = torch.as_tensor(obs, dtype=torch.float32, device=agent.device)
            mask_t = torch.as_tensor(mask, dtype=torch.bool, device=agent.device)
            with torch.no_grad():
                lp = torch.log_softmax(agent.masked_logits(obs_t, mask_t), -1)
                logp = lp.gather(-1, torch.as_tensor(acts, device=lp.device).unsqueeze(-1)).squeeze(-1)
                logp = logp.cpu().numpy()

        import torch
        with torch.no_grad():
            v = agent.value(torch.as_tensor(state, dtype=torch.float32, device=agent.device)).cpu().numpy()
        v = np.full(n, float(v))                   # team value broadcast

        B["obs"][t] = obs
        B["mask"][t] = mask
        B["acts"][t] = acts
        B["logp"][t] = logp
        B["states"][t] = state
        B["values"][t] = v

        obs, state, r, done, _ = env.step(acts)
        B["adv"][t] = r
        t += 1
        if done:
            break
    # Distinguish a genuine terminal state from a truncation.
    #
    # The environment ends an episode when the mission time limit is reached.
    # That is a TRUNCATION, not a terminal state: the value of the final state
    # is still meaningful, so the GAE recursion must bootstrap from V(s_{t+1}).
    # Conflating the two biases every value target downward.  The environment
    # therefore reports `terminated` separately, and the rollout trusts it
    # rather than inferring termination from `done`.
    env_terminated = bool(getattr(env, "terminated", False))
    truncated = not env_terminated
    terminal_state = state if truncated else None

    # ---- GAE (26) with bootstrap at truncation -----------------------
    # At a natural termination, the bootstrap value is 0. At a truncation
    # (hit the horizon without done), we must bootstrap with V(s_{t+1}) so
    # the value target is not biased downward. A previous revision used 0 in
    # both cases, underestimating returns at the horizon.
    adv = np.zeros_like(B["adv"])
    last_gae = np.zeros(n, np.float32)
    # Bootstrap value for the boundary (only used when truncated).
    if truncated and agent is not None and terminal_state is not None:
        import torch
        with torch.no_grad():
            v_boot = agent.value(
                torch.as_tensor(terminal_state, dtype=torch.float32, device=agent.device)
            ).cpu().numpy()
        bootstrap_val = np.full(n, float(v_boot))
    else:
        bootstrap_val = np.zeros(n, np.float32)
    for step in reversed(range(t)):
        if step + 1 < t:
            next_val = B["values"][step + 1]
        else:
            next_val = bootstrap_val
        delta = B["adv"][step] + agent_gamma(agent) * next_val - B["values"][step]
        last_gae = delta + agent_gamma(agent) * agent_lam(agent) * last_gae
        adv[step] = last_gae
    B["adv"] = adv
    # The batch must be truncated to the number of steps actually collected
    # BEFORE the returns are formed.  The episode now ends early whenever a
    # UAV failure terminates the mission, so t is not always n_steps, and
    # forming the returns from the untruncated advantage array gave a
    # shape mismatch (and would have silently mis-aligned the targets).
    B = {k: v[:t] for k, v in B.items()}
    B["ret"] = B["adv"] + B["values"]
    return B, env.summary()


def agent_gamma(agent):
    return agent.gamma if agent else 0.99


def agent_lam(agent):
    return agent.lam if agent else 0.95


def agent_obs_dim(agent):
    """Input width of the agent's actor network.

    Replaced a stub that returned the literal 32. That hardcoded value matched
    neither the observation layout (which used to write only 24 of 32 slots and
    now writes exactly 30) nor any configuration other than the reference one,
    so a buffer sized from it silently disagreed with the environment.
    """
    first = next(agent.actor.parameters())
    return int(first.shape[-1])


# ----------------------------------------------------------------------
# Training
# ----------------------------------------------------------------------
def train_mappo(cfg: SimConfig, episodes=120, n_steps=400, seed=0, log_every=10,
               verbose=True, per_agent_adv_norm=False, ent_coef=0.01,
               value_norm=True, device=None):
    torch.manual_seed(seed)
    env = UAVIoTEnv(cfg)
    if device is None:
        # the policy network and the critic are small, and the simulator is a
        # sequential Python loop, so the GPU is used for the network and the
        # PPO update while the control loop stays on the host
        device = "cuda" if torch.cuda.is_available() else "cpu"
    agent = MAPPO(n_agents=cfg.N, obs_dim=env.obs_dim, state_dim=env.state_dim,
                  per_agent_adv_norm=per_agent_adv_norm, ent_coef=ent_coef,
                  value_norm=value_norm, device=device)
    hist = []
    for ep in range(episodes):
        B, summ = collect_rollout(env, agent, n_steps)
        losses = agent.update(B)
        rec = dict(episode=ep, mean_reward=float(B["adv"][:, 0].mean()), **losses)
        rec.update({k: float(v) for k, v in summ.items()})
        hist.append(rec)
        if verbose and (ep % log_every == 0 or ep == episodes - 1):
            print(
                f"[MAPPO ep {ep:3d}] R={rec['mean_reward']:+.4f} "
                f"CK={rec.get('CK',0):.3f} AG={rec.get('AG',0):.3f} "
                f"Crit={rec.get('Crit',0):.3f} ent={rec['entropy']:.3f}"
            )
    return agent, hist


# ----------------------------------------------------------------------
# Rule-based baselines (Table VIII)
# ----------------------------------------------------------------------
def _seeded(cfg: SimConfig, seed: int) -> SimConfig:
    """Copy of cfg with the episode seed applied.

    The seed selects the random scene (sensor layout, pad placement, initial
    positions and the shadowing draw).  Every baseline must apply it, or a
    "five-seed" comparison degenerates into the same episode run five times
    while the learned policy is evaluated on five different scenes.
    """
    import copy
    c = copy.deepcopy(cfg)
    c.seed = int(seed)
    return c


def _move_toward(env, i, target):
    c = env.cfg
    d = target - env.p[i]
    if np.linalg.norm(d) < 1e-6:
        return A_HOVER
    step = c.v_max * c.dt
    # snap to the dominant cardinal axis (discrete action space)
    if abs(d[0]) >= abs(d[1]):
        return A_PX if d[0] > 0 else A_NX
    return A_PY if d[1] > 0 else A_NY


def _uncovered_target(env):
    ncov = env.coverage_counts()
    under = np.where(ncov < env.cfg.K)[0]
    if len(under):
        return env.sensors[under[np.argmin(np.linalg.norm(env.sensors[under] - env.p.mean(0), axis=1))]]
    return env.pads[0]


def baseline_fixed(cfg: SimConfig, steps=1000, seed=0):
    """Fixed formation with threshold recharge.

    The `seed` argument selects the episode's random scene (sensor layout,
    pad placement, initial positions).  It MUST be applied to the config:
    accepting the argument and ignoring it would make every "seed" in a
    multi-seed comparison the same episode, which silently turns a
    five-seed comparison into one repeated run.
    """
    cfg = _seeded(cfg, seed)
    env = UAVIoTEnv(cfg)
    obs, st = env.reset()
    for _ in range(steps):
        acts = np.zeros(cfg.N, dtype=np.int64)
        for i in env._active_idx():
            if env.E[i] <= env.return_threshold(i):
                # walk straight to the nearest pad, charge on arrival
                if np.min(np.linalg.norm(env.pads - env.p[i], axis=1)) <= env.cfg.pad_service_radius:
                    acts[i] = A_CHARGE
                else:
                    acts[i] = _move_toward(env, i, env.pads[int(np.argmin(np.linalg.norm(env.pads - env.p[i], axis=1)))])
            else:
                acts[i] = A_HOVER
        obs, st, r, done, _ = env.step(acts)
        if done:
            break
    return env.summary()


def baseline_greedy(cfg: SimConfig, steps=1000, seed=0):
    """Greedy lowest-battery recharge with the same motion rule."""
    cfg = _seeded(cfg, seed)
    env = UAVIoTEnv(cfg)
    obs, st = env.reset()
    for _ in range(steps):
        acts = np.zeros(cfg.N, dtype=np.int64)
        for i in env._active_idx():
            if env.E[i] <= env.return_threshold(i):
                if np.min(np.linalg.norm(env.pads - env.p[i], axis=1)) <= env.cfg.pad_service_radius:
                    acts[i] = A_CHARGE
                else:
                    acts[i] = _move_toward(env, i, env.pads[int(np.argmin(np.linalg.norm(env.pads - env.p[i], axis=1)))])
            else:
                acts[i] = _move_toward(env, i, _uncovered_target(env))
        obs, st, r, done, _ = env.step(acts)
        if done:
            break
    return env.summary()


def baseline_reactive(cfg: SimConfig, steps=1000, seed=0):
    """Deterministic coverage + connectivity heuristic (no learning)."""
    cfg = _seeded(cfg, seed)
    env = UAVIoTEnv(cfg)
    obs, st = env.reset()
    for _ in range(steps):
        acts = np.zeros(cfg.N, dtype=np.int64)
        ncov = env.coverage_counts()
        under = np.where(ncov < cfg.K)[0]
        for k, i in enumerate(env._active_idx()):
            if env.E[i] <= env.return_threshold(i):
                if np.min(np.linalg.norm(env.pads - env.p[i], axis=1)) <= cfg.pad_service_radius:
                    acts[i] = A_CHARGE
                else:
                    acts[i] = _move_toward(env, i, env.pads[int(np.argmin(np.linalg.norm(env.pads - env.p[i], axis=1)))])
                continue
            if len(under) == 0:
                acts[i] = A_HOVER
                continue
            # assign the k-th uncovered sensor round-robin so the swarm splits up
            tgt = env.sensors[under[k % len(under)]]
            acts[i] = _move_toward(env, i, tgt)
        obs, st, r, done, _ = env.step(acts)
        if done:
            break
    return env.summary()
