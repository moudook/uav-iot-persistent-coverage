"""Export a learned-policy trajectory as a BonnMotion trace for INET/Qtenv.

The demo replays the frozen actor from a checkpoint, step by step, and writes
one line per UAV as (t x y) triples at the simulator's control period.  This is
the trace the OMNeT++ visualization should show: the swarm starting in its
clustered deployment and spreading across the field under the learned policy.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ml_impl"))
for v in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS",
          "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(v, "1")

import numpy as np

from uav_wireless.env import UAVIoTEnv
from uav_wireless.experiments import base_config
from uav_wireless.mappo import MAPPO

CKPT = os.path.join(os.path.dirname(__file__), "..", "ml_impl", "runs",
                    "exp_ego_eval", "seed_0.pt")
OUT = os.path.join(os.path.dirname(__file__), "..", "Simulation", "omnet_uav",
                   "traces", "episode_policy.movements")
STEPS = 200      # 200 x 0.2 s = 40 s, matching the INET sim-time-limit
SEED = 7         # a scene where the policy deploys rather than hovers


def main():
    cfg = base_config()
    cfg.ego_sensors = True
    cfg.n_ego = 3
    cfg.dist_shape_kappa = 0.5
    cfg.episode_len = STEPS
    cfg.seed = SEED
    env = UAVIoTEnv(cfg)
    agent = MAPPO(n_agents=cfg.N, obs_dim=env.obs_dim,
                  state_dim=env.state_dim, device="cpu")
    agent.load(CKPT)

    obs, _ = env.reset()
    traj = [[(0.0, float(env.p[i, 0]), float(env.p[i, 1]))]
            for i in range(cfg.N)]
    for t in range(1, STEPS + 1):
        mask = np.stack(env.action_masks())
        acts = agent.act(obs, mask, deterministic=True)
        obs, _state, _r, done, _ = env.step(acts)
        for i in range(cfg.N):
            traj[i].append((t * cfg.dt, float(env.p[i, 0]), float(env.p[i, 1])))
        if done:
            break

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        for i in range(cfg.N):
            f.write(" ".join(f"{t:.3f} {x:.3f} {y:.3f}"
                             for t, x, y in traj[i]) + "\n")

    s = env.summary()
    xs = np.array([p[1] for p in traj[0]])
    ys = np.array([p[2] for p in traj[0]])
    print(f"wrote {OUT}")
    print(f"steps={len(traj[0])-1} CK={s.get('CK', 0):.3f} AG={s.get('AG', 0):.3f}")
    print(f"UAV0 path: start ({traj[0][0][1]:.1f},{traj[0][0][2]:.1f}) "
          f"end ({traj[0][-1][1]:.1f},{traj[0][-1][2]:.1f})")
    allx = np.concatenate([[p[1] for p in tr] for tr in traj])
    ally = np.concatenate([[p[2] for p in tr] for tr in traj])
    print(f"field span: x {allx.min():.1f}-{allx.max():.1f}, "
          f"y {ally.min():.1f}-{ally.max():.1f}")


if __name__ == "__main__":
    main()
