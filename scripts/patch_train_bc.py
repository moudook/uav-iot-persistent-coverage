p = "ml_impl/uav_wireless/train.py"
s = open(p).read()

# 1. Add bc_path param to signature
old_sig = "def train_mappo(cfg: SimConfig, episodes=120, n_steps=400, seed=0, log_every=10,\n               verbose=True, per_agent_adv_norm=False, ent_coef=0.01,\n               value_norm=True, device=None):"
new_sig = "def train_mappo(cfg: SimConfig, episodes=120, n_steps=400, seed=0, log_every=10,\n               verbose=True, per_agent_adv_norm=False, ent_coef=0.01,\n               value_norm=True, device=None, bc_path=None):"
assert old_sig in s, "sig not found"
s = s.replace(old_sig, new_sig)

# 2. After agent creation, load BC weights if bc_path given
old_agent = "    agent = MAPPO(n_agents=cfg.N, obs_dim=env.obs_dim, state_dim=env.state_dim,\n                  per_agent_adv_norm=per_agent_adv_norm, ent_coef=ent_coef,\n                  value_norm=value_norm, device=device)\n"
new_agent = old_agent + '''    if bc_path:
        import torch, os
        if os.path.exists(bc_path):
            try:
                sd = torch.load(bc_path, map_location=agent.device, weights_only=True)
                agent.actor.load_state_dict(sd)
                if verbose:
                    print(f"[train] loaded BC actor from {bc_path}")
            except Exception as e:
                if verbose:
                    print(f"[train] BC load failed ({e}); training from scratch")
'''
assert old_agent in s, "agent not found"
s = s.replace(old_agent, new_agent)

open(p, "w").write(s)
print("done")
