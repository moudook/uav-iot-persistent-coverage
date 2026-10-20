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
        obs_dim: int | None = None,
        state_dim: int | None = None,
        n_agents=5,
        hidden=128,
        lr=3e-4,
        gamma=0.99,
        gae_lambda=0.95,
        clip=0.2,
        ent_coef=0.01,
        vf_coef=0.5,
        max_grad_norm=0.5,
        per_agent_adv_norm=False,
        value_norm=True,
        device="cpu",
    ):
        # Dimensions are configuration-dependent (they scale with N, M and
        # n_pads). Falling back to the reference-config constants keeps old
        # call sites working, but callers should pass env.obs_dim and
        # env.state_dim so the networks always match the environment.
        obs_dim = UAVIoTEnv.OBS_DIM if obs_dim is None else obs_dim
        state_dim = UAVIoTEnv.STATE_DIM if state_dim is None else state_dim
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
        # Per-agent advantage normalisation.  With a shared team reward every
        # agent receives the SAME advantage, so the policy gradient cannot
        # distinguish an agent whose action helped from one whose action was
        # irrelevant.  Normalising each agent's advantages over its own
        # history gives every agent a signal relative to its own behaviour
        # rather than to the pooled batch.  (Generalised per-agent advantage
        # estimation, Kim et al., AAMAS 2026, addresses the same problem for
        # the multi-agent case.)
        self.per_agent_adv_norm = per_agent_adv_norm
        # MAPPO's value normalisation.  The critic predicts the returns in a
        # normalised space defined by running statistics of the return
        # distribution; the value is un-normalised at every point of use.
        self.value_norm = value_norm
        self.ret_ema_beta = 0.99
        # floor on the standard deviation of the returns, so that a policy
        # with nearly constant returns cannot drive the normalisation to
        # zero and collapse the advantage
        self.ret_std_floor = 1.0
        self._ret_mean = 0.0
        self._ret_std = 1.0

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
    def value(self, states):
        """The value of a batch of global states, in the ORIGINAL reward scale.

        With value normalisation the critic's raw output is the NORMALISED
        value, so every place that uses V(s) -- the TD residual, the GAE
        recursion and the bootstrap at a truncation boundary -- must
        un-normalise it first.  Forgetting this is the classic way to
        introduce a silent scale error into the advantage estimates.
        """
        v = self.critic(states)
        if self.value_norm:
            v = v * self._ret_std + self._ret_mean
        return v

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

        if self.per_agent_adv_norm:
            # normalise each agent's advantages over its own time history
            adv = (adv - adv.mean(dim=0, keepdim=True)) / (
                adv.std(dim=0, keepdim=True) + 1e-8)
        else:
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
        if self.value_norm:
            # MAPPO's value normalisation.  The critic is trained to predict
            # the RETURNS in a normalised space, using running statistics of
            # the return distribution; the value is un-normalised wherever it
            # is used (the TD residual, the GAE recursion and the
            # bootstrap).  Without it the critic has to fit a target whose
            # absolute scale drifts with the reward balance, which is one of
            # the components the MAPPO paper identifies as load-bearing.
            with torch.no_grad():
                b = self.ret_ema_beta
                self._ret_mean = (1 - b) * self._ret_mean + b * float(ret_c.mean())
                sd = float(ret_c.std())
                # The standard deviation of the returns is FLOORED.  Without a
                # floor, a policy whose returns become nearly constant drives
                # sigma to zero, and the normalised target (R - mu)/sigma then
                # explodes; the advantage collapses to zero and the policy
                # gradient vanishes.  That failure mode is self-reinforcing,
                # and it is a plausible cause of a policy that freezes.
                self._ret_std = max((1 - b) * self._ret_std + b * sd,
                                    self.ret_std_floor)
            target_c = (ret_c - self._ret_mean) / (self._ret_std + 1e-8)
            critic_loss = ((new_val - target_c) ** 2).mean()
            # The value-clipping auxiliary term compares the new prediction
            # with the old one, so both must live in the SAME space.  The
            # recorded old value is in the original scale, so it has to be
            # normalised before the comparison.
            old_val_c = (old_val_c - self._ret_mean) / (self._ret_std + 1e-8)
        else:
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
            dict(actor=self.actor.state_dict(), critic=self.critic.state_dict(),
                 value_norm=self.value_norm,
                 ret_mean=self._ret_mean, ret_std=self._ret_std),
            path,
        )

    def load(self, path):
        d = torch.load(path, map_location=self.device)
        self.actor.load_state_dict(d["actor"])
        self.critic.load_state_dict(d["critic"])
        if "ret_mean" in d:
            self._ret_mean = float(d["ret_mean"])
            self._ret_std = float(d["ret_std"])