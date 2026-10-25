"""Behavior cloning: train actor on reactive rule (obs, action) pairs."""
import os, sys, pickle, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ml_impl"))
for v in ("OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","OMP_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(v, "6")
import numpy as np, torch, torch.nn as nn
from uav_wireless.env import UAVIoTEnv, SimConfig
from uav_wireless.experiments import base_config
from uav_wireless.mappo import Actor, N_ACTIONS

def main():
    cfg = base_config()
    env = UAVIoTEnv(cfg)
    obs_dim = env.obs_dim
    data = pickle.load(open(os.path.join(os.path.dirname(__file__), "..", "ml_impl", "bc_data.pkl"), "rb"))
    obs_arr = np.array([d[0] for d in data], dtype=np.float32)
    act_arr = np.array([d[1] for d in data], dtype=np.int64)
    print(f"BC data: {len(obs_arr)} pairs, obs_dim={obs_dim}")

    actor = Actor(obs_dim, hidden=128)
    opt = torch.optim.Adam(actor.parameters(), lr=1e-3)
    bs = 256
    n = len(obs_arr)
    t0 = time.time()
    for epoch in range(20):
        perm = np.random.permutation(n)
        total_loss = 0.0
        correct = 0
        for i in range(0, n, bs):
            idx = perm[i:i+bs]
            o = torch.as_tensor(obs_arr[idx], dtype=torch.float32)
            a = torch.as_tensor(act_arr[idx], dtype=torch.long)
            logits = actor(o)
            loss = nn.CrossEntropyLoss()(logits, a)
            opt.zero_grad()
            loss.backward()
            opt.step()
            total_loss += loss.item() * len(idx)
            correct += (logits.argmax(-1) == a).sum().item()
        acc = correct / n
        print(f"epoch {epoch:2d}: loss={total_loss/n:.4f} acc={acc:.3f} ({time.time()-t0:.1f}s)")
    # save
    out = os.path.join(os.path.dirname(__file__), "..", "ml_impl", "bc_actor.pt")
    torch.save(actor.state_dict(), out)
    print(f"saved BC actor to {out}")

if __name__ == "__main__":
    main()
