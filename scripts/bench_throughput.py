import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ml_impl"))
from uav_wireless.env import UAVIoTEnv, SimConfig
import numpy as np

cfg = SimConfig(N=5, M=20, episode_len=200)
env = UAVIoTEnv(cfg)
obs, state = env.reset()
t0 = time.time()
steps = 0
target = 2000
while steps < target:
    acts = [int(np.random.randint(0,6)) for _ in range(cfg.N)]
    obs, state, r, done, info = env.step(acts)
    steps += 1
    if done:
        obs, state = env.reset()
dt = time.time() - t0
print(f"steps={steps} time={dt:.2f}s steps/sec={steps/dt:.1f}")
print(f"per-step ms={1000*dt/steps:.2f}")
