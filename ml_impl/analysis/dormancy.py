"""
Plasticity / dormancy diagnostic for the shared MAPPO actor.

WHY
---
The 2026 literature (Qiu et al., "PRIME: Plasticity Recovery in Multi-Agent
Environments for UAV-Assisted Emergency Communication Networks",
arXiv:2607.17922) reports that in vanilla MAPPO 40-45% of neurons are
dormant, that this "internal degradation does not surface in standard reward
curves or training loss plots", and that in shared-parameter training a
neuron can look inactive on one agent's observations while still receiving
strong gradients from another agent's data.  Their diagnostic is therefore
two-directional: a neuron is only truly dead if it is simultaneously
activation-dormant AND gradient-silent.

No catalogue of MAPPO silent bugs with controlled experiments was found in
that search.  This module implements the two-directional probe for this
codebase so that the claim "the trained policy is not silently degraded" is
measured rather than assumed.

METHOD
------
One forward pass over a collected rollout, with the hidden-layer activations
retained.  Then one backward pass PER AGENT, so that the gradient each
individual agent contributes to each neuron is separable -- a single shared
backward pass would only expose the summed gradient and would hide the very
per-agent effect PRIME warns about.

Definitions (relative to the layer, so they are scale-free):
  activation a_i  = mean over (step, agent) of |activation of neuron i|
  gradient  g_i  = mean over (step, agent) of |gradient w.r.t. neuron i|
  dormant(i)     = a_i < tau_a * mean_j(a_j)
  silent(i)      = g_i < tau_g * mean_j(g_j)

Both thresholds are swept, and the full percentile distribution is reported, so
a reader can apply their own criterion instead of trusting one.

Run:  python analysis/dormancy.py [checkpoint]
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import torch

from uav_wireless.env import SimConfig, UAVIoTEnv
from uav_wireless.mappo import MAPPO
from uav_wireless.train import collect_rollout

HERE = os.path.dirname(os.path.abspath(__file__))
THRESHOLDS = (0.001, 0.01, 0.05, 0.10)


def probe(agent, batch):
    """Return per-layer, per-agent activation and gradient statistics."""
    obs = torch.as_tensor(batch["obs"], dtype=torch.float32, device=agent.device)
    mask = torch.as_tensor(batch["mask"], dtype=torch.bool, device=agent.device)
    acts = torch.as_tensor(batch["acts"], dtype=torch.long, device=agent.device)
    old_logp = torch.as_tensor(batch["logp"], dtype=torch.float32, device=agent.device)
    adv = torch.as_tensor(batch["adv"], dtype=torch.float32, device=agent.device)
    adv = (adv - adv.mean()) / (adv.std() + 1e-8)

    n_steps, n_agents = acts.shape
    hidden_layers = [m for m in agent.actor.net if isinstance(m, torch.nn.Linear)]

    captured = {}

    def make_hook(name):
        def hook(_mod, _inp, out):
            out.retain_grad()
            captured[name] = out
        return hook

    handles = [m.register_forward_hook(make_hook(f"L{i}"))
               for i, m in enumerate(hidden_layers)]

    # one forward pass; masked logits exactly as in training
    logits = agent.masked_logits(obs, mask)
    logp = torch.log_softmax(logits, dim=-1)
    logp_a = logp.gather(-1, acts.unsqueeze(-1)).squeeze(-1)
    ratio = torch.exp(logp_a - old_logp)
    per_agent_loss = -torch.min(ratio * adv,
                                torch.clamp(ratio, 1 - agent.clip, 1 + agent.clip) * adv)

    # per-agent backward so each agent's gradient contribution is separable
    grads = {f"L{i}": [] for i in range(len(hidden_layers))}
    for a in range(n_agents):
        agent.actor.zero_grad(set_to_none=True)
        per_agent_loss[:, a].mean().backward(retain_graph=True)
        for name, out in captured.items():
            # the loss only touches agent a's slice, so only that slice of the
            # layer output carries gradient
            grads[name].append(out.grad.detach().abs()[:, a, :])   # (T, H)
    for h in handles:
        h.remove()

    stats = {}
    for i, name in enumerate(sorted(captured.keys())):
        out = captured[name]                            # (T, N, H)
        act = out.detach().abs()                        # (T, N, H)
        g = torch.stack(grads[name], dim=0)              # (A, T, H)
        # per-neuron, per-agent: activation of agent a's own samples, and the
        # gradient agent a's loss puts on each neuron
        act_per_agent = act.permute(1, 0, 2)             # (A, T, H)
        act_per_agent = act_per_agent.mean(dim=1)         # (A, H)
        grad_per_agent = g.mean(dim=1)                   # (A, H)
        stats[name] = dict(
            n_neurons=int(out.shape[-1]),
            act_per_neuron=act.mean(dim=(0, 1)).cpu().numpy().tolist(),
            grad_per_neuron=grad_per_agent.mean(dim=0).cpu().numpy().tolist(),
            act_per_agent=act_per_agent.cpu().numpy().tolist(),      # (A, H)
            grad_per_agent=grad_per_agent.cpu().numpy().tolist(),    # (A, H)
        )
    return stats


def summarise(stats):
    out = []
    for name, s in stats.items():
        a = np.asarray(s["act_per_neuron"], dtype=float)
        g = np.asarray(s["grad_per_neuron"], dtype=float)
        a_mean = a.mean()
        g_mean = g.mean()
        row = dict(layer=name, n_neurons=s["n_neurons"],
                   act_mean=float(a_mean), grad_mean=float(g_mean),
                   act_percentiles={str(p): float(np.percentile(a, p))
                                    for p in (1, 5, 25, 50, 75, 95, 99)},
                   grad_percentiles={str(p): float(np.percentile(g, p))
                                    for p in (1, 5, 25, 50, 75, 95, 99)})
        for tau in THRESHOLDS:
            row[f"dormant_frac_{tau}"] = float(np.mean(a < tau * a_mean))
            row[f"silent_frac_{tau}"] = float(np.mean(g < tau * g_mean))
            row[f"dead_frac_{tau}"] = float(
                np.mean((a < tau * a_mean) & (g < tau * g_mean)))
        # per-agent view (PRIME: dormancy depends on which agent's data)
        pa = np.asarray(s["act_per_agent"], dtype=float)    # (A, H)
        pg = np.asarray(s["grad_per_agent"], dtype=float)   # (A, H)
        row["per_agent_act_mean"] = pa.mean(axis=1).tolist()
        row["per_agent_grad_mean"] = pg.mean(axis=1).tolist()
        # a neuron that is dormant for one agent but alive for another
        dorm_a = pa < 0.01 * pa.mean(axis=1, keepdims=True)
        alive_anywhere = (~dorm_a).any(axis=0)
        row["neurons_dormant_for_some_agent_only"] = int(
            (dorm_a.any(axis=0) & alive_anywhere).sum())
        out.append(row)
    return out


def main():
    ckpt = sys.argv[1] if len(sys.argv) > 1 else "mappo_base.pt"
    if not os.path.exists(ckpt):
        print(f"checkpoint not found: {ckpt}")
        return 2

    cfg = SimConfig(N=8, K=2, R_cov=35.0, episode_len=400, seed=0)
    env = UAVIoTEnv(cfg)
    agent = MAPPO(n_agents=cfg.N, obs_dim=env.obs_dim, state_dim=env.state_dim)
    agent.load(ckpt)

    batch, _ = collect_rollout(env, agent, n_steps=200, deterministic=False)
    stats = probe(agent, batch)
    rows = summarise(stats)

    print("=" * 78)
    print(f" DORMANCY / PLASTICITY PROBE -- {ckpt}")
    print(" per-agent backward passes; thresholds relative to the layer mean")
    print("=" * 78)
    for r in rows:
        print(f"\nlayer {r['layer']}  ({r['n_neurons']} neurons)")
        print(f"  mean |activation| = {r['act_mean']:.3e}   "
              f"mean |gradient| = {r['grad_mean']:.3e}")
        print(f"  activation percentiles: "
              + " ".join(f"p{k}={v:.2e}" for k, v in r["act_percentiles"].items()))
        print(f"  gradient  percentiles: "
              + " ".join(f"p{k}={v:.2e}" for k, v in r["grad_percentiles"].items()))
        for tau in THRESHOLDS:
            print(f"  tau={tau:<6} dormant={r[f'dormant_frac_{tau}']:.3f}  "
                  f"silent={r[f'silent_frac_{tau}']:.3f}  "
                  f"dead(dormant AND silent)={r[f'dead_frac_{tau}']:.3f}")
        pa = np.asarray(r["per_agent_act_mean"], dtype=float)
        pg = np.asarray(r["per_agent_grad_mean"], dtype=float)
        print("  per-agent mean activation: "
              + " ".join(f"{v:.2e}" for v in pa))
        print("  per-agent mean gradient : "
              + " ".join(f"{v:.2e}" for v in pg))
        print(f"  neurons dormant for SOME agent but alive for another: "
              f"{r['neurons_dormant_for_some_agent_only']}")

    with open(os.path.join(HERE, "dormancy.json"), "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)
    print(f"\nSaved -> {os.path.join(HERE, 'dormancy.json')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
