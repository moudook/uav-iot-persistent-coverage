"""
CTDE MAPPO for UAV-IoT persistent coverage. Section IV-A / Algorithm 1.

- Shared actor  pi_theta(a_i | o_i)   with masked logits  (deployment-ready)
- Centralized critic V_phi(s_t)      (training only)
- GAE (26), clipped PPO (28), critic loss (29)
- Parameter sharing across UAVs: one actor, one critic, N agents.
"""

from __future__ import annotations

import numpy as np
import torch
import torch.nn as nn

from .env import N_ACTIONS, UAVIoTEnv, SimConfig


def mlp(sizes, act=nn.ReLU, out_act=None):
    layers = []
    for a, b in zip(sizes[:-1], sizes[1:]):
        layers += [nn.Linear(a, b), act()]
    if out_act is not None:
        layers[-1] = nn.Linear(sizes[-2], sizes[-1])
        layers.append(out_act())
    return nn.Sequential(*layers)


class Actor(nn.Module):
    """Shared policy with masked softmax over the 6 discrete actions."""

    def __init__(self, obs_dim, hidden=128):
        super().__init__()
        self.net = mlp([obs_dim, hidden, hidden], nn.ReLU, None)
        self.head = nn.Linear(hidden, N_ACTIONS)

    def forward(self, obs):
        return self.head(self.net(obs))


class Critic(nn.Module):
    def __init__(self, state_dim, hidden=128):
        super().__init__()
        self.net = mlp([state_dim, hidden, hidden], nn.ReLU, None)
        self.head = nn.Linear(hidden, 1)

    def forward(self, s):
        return self.head(self.net(s)).squeeze(-1)


class MAPPO:
    def __init__(
        self,
        obs_dim=UAVIoTEnv.OBS_DIM,
        state_dim=UAVIoTEnv.STATE_DIM,
        n_agents=5,
        hidden=128,
        lr=3e-4,
        gamma=0.99,
        gae_lambda=0.95,
        clip=0.2,
        ent_coef=0.01,
        vf_coef=0.5,
        max_grad_norm=0.5,
        device="cpu",
    ):
        self.device = torch.device(device)
        self.actor = Actor(obs_dim, hidden).to(self.device)
        self.critic = Critic(state_dim, hidden).to(self.device)
        self.opt = torch.optim.Adam(
            list(self.actor.parameters()) + list(self.critic.parameters()), lr=lr
        )
        self.gamma = gamma
        self.lam = gae_lambda
        self.clip = clip
        self.ent_coef = ent_coef
        self.vf_coef = vf_coef
        self.max_grad_norm = max_grad_norm
        self.n_agents = n_agents

    # ------------------------------------------------------------------
    def masked_logits(self, obs, mask):
        logits = self.actor(obs)
        return logits.masked_fill(~mask, float("-inf"))

    @torch.no_grad()
    def act(self, obs_np, mask_np, deterministic=False):
        obs = torch.as_tensor(obs_np, dtype=torch.float32, device=self.device)
        mask = torch.as_tensor(mask_np, dtype=torch.bool, device=self.device)
        logits = self.masked_logits(obs, mask)
        # a fully-masked row would give NaNs: fall back to hover (index 0)
        bad = torch.isinf(logits).all(dim=-1)
        if bad.any():
            logits[bad] = torch.zeros_like(logits[bad])
            logits[bad, 0] = 1.0
        logp = torch.log_softmax(logits, dim=-1)
        if deterministic:
            a = logp.argmax(dim=-1)
        else:
            a = torch.distributions.Categorical(logits=logp).sample()
        return a.cpu().numpy()

    # ------------------------------------------------------------------
    def update(self, batch):
        obs = torch.as_tensor(batch["obs"], dtype=torch.float32, device=self.device)
        mask = torch.as_tensor(batch["mask"], dtype=torch.bool, device=self.device)
        acts = torch.as_tensor(batch["acts"], dtype=torch.long, device=self.device)
        old_logp = torch.as_tensor(batch["logp"], dtype=torch.float32, device=self.device)
        adv = torch.as_tensor(batch["adv"], dtype=torch.float32, device=self.device)
        ret = torch.as_tensor(batch["ret"], dtype=torch.float32, device=self.device)
        states = torch.as_tensor(batch["states"], dtype=torch.float32, device=self.device)
        old_val = torch.as_tensor(batch["values"], dtype=torch.float32, device=self.device)

        # The critic sees the single global state s_t, but the returns/values
        # are recorded per agent because the team reward is broadcast. Sample
        # agent 0 for the value targets and expand the state accordingly, so
        # the critic loss compares like with like.
        n_agents = acts.shape[1]
        states_c = states.unsqueeze(1).expand(-1, n_agents, -1).reshape(
            states.shape[0] * n_agents, -1
        )
        ret_c = ret.reshape(-1)
        old_val_c = old_val.reshape(-1)

        adv = (adv - adv.mean()) / (adv.std() + 1e-8)

        # ---- clipped PPO actor loss (28) ----------------------------
        logits = self.masked_logits(obs, mask)
        logp = torch.log_softmax(logits, dim=-1)
        logp_a = logp.gather(-1, acts.unsqueeze(-1)).squeeze(-1)
        ratio = torch.exp(logp_a - old_logp)
        s1 = ratio * adv
        s2 = torch.clamp(ratio, 1 - self.clip, 1 + self.clip) * adv
        actor_loss = -torch.min(s1, s2).mean()

        # ---- entropy bonus (masked actions only) --------------------
        p = logp.exp() * mask
        ent = -(p * logp.clamp(min=-1e8)).sum(-1)
        ent = torch.where(mask.any(-1), ent, torch.zeros_like(ent)).mean()

        # ---- critic loss (29) --------------------------------------
        new_val = self.critic(states_c)
        critic_loss = ((new_val - ret_c) ** 2).mean()
        adv_l2 = ((new_val - old_val_c) ** 2).mean()

        loss = actor_loss + self.ent_coef * ent + self.vf_coef * critic_loss + 0.01 * adv_l2
        self.opt.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_(
            list(self.actor.parameters()) + list(self.critic.parameters()),
            self.max_grad_norm,
        )
        self.opt.step()
        return dict(
            actor=float(actor_loss),
            critic=float(critic_loss),
            entropy=float(ent),
            value=float(new_val.mean()),
        )

    def save(self, path):
        torch.save(
            dict(actor=self.actor.state_dict(), critic=self.critic.state_dict()),
            path,
        )

    def load(self, path):
        d = torch.load(path, map_location=self.device)
        self.actor.load_state_dict(d["actor"])
        self.critic.load_state_dict(d["critic"])