# LOG — experiment & decision log

Append-only. Each entry: date, question, expected result, decision it changes, outcome.

## 2026-10-25
- G0 setup: initialized git repo, saved MASTER_PROMPT.md, created STATE.md/CLAIMS.md/LOG.md/NEGATIVE.md skeletons.
- Hardware measured: i5-11400H 6c/12t, RTX 2050 4GB, Python 3.13.14, torch 2.6.0+cu124.
- Retracted claims logged in CLAIMS.md (#1-4).
- Next: throughput benchmark, OMNeT++/INET install check, novelty gate.
---
## 2026-10-25 (cont.)
- Throughput benchmark: scripts/bench_throughput.py → 231.8 steps/sec single env (4.31 ms/step), N=5, M=20. At this rate, 2e6 steps/seed ≈ 2.4 h single-threaded; with 6 parallel seeds ≈ 2.4 h. Vectorization (32-128 parallel envs) needed for G1+ (R3).
- OMNeT++/INET: NOT installed. Need opp_env + OMNeT++ 6.4 + INET 4.7. Install during G0/G2.
- Missing Python pkgs installed: gymnasium, rliable, optuna, pettingzoo, pytest, ruff, pandas (already present), matplotlib (already), seaborn (already), pyzmq, protobuf. vmas/benchmarl/epymarl not yet installed (optional).
- Git repo initialized at repo root; commits: master prompt, state skeleton.

## 2026-10-29 — INET Step B: silent ini override bug (invalidates earlier Step B numbers)

**Question.** Does the simulator's geometric `R_comm = 40 m` reflect what the
802.11 PHY actually delivers, and what is the true PDR(distance) curve?

**What went wrong.** Every earlier Step A/B run set submodule parameters with
patterns of the form `**.uav[*].mobility.traceFile`. OMNeT++ matches
`**.mobility.X` and `**.**.mobility.X` through a module vector, but NOT
`**.uav[*].mobility.X`. The mismatch is silent: no warning, no error, the NED
default stays in force.

Measured directly with a sentinel (invalid mobility type):
  `**.uav[0].mobility.typename`  -> ignored
  `*.uav[*].mobility.typename`   -> ignored
  `**.**.mobility.typename`      -> matches
  `**.mobility.typename`         -> matches

Consequence: a sweep that believed it was moving two nodes from 5 m to 4000 m
returned PDR = 0.9950 at every distance -- because every run replayed the same
default trace, `episode_000.movements`. Fourteen "measurements" of one
configuration. The identical per-run packet counts (201 sent, 199 received)
were the tell.

**Fix.** Own the scenario. `Simulation/omnet_uav2/{UavPair,UavSwarm}.ned`
expose every knob as a NETWORK-LEVEL parameter with a `sim` prefix (prefix
needed because `mobility.traceFile = traceFile` refers to itself). Single-star
patterns on network parameters demonstrably apply. Geometry is a 3-D BonnMotion
trace, so altitude is real (the old scenario had UAVs at z = 0 while the Python
simulator hovers at z = 50 m -- a second silent mismatch).

**Guard.** `scripts/inet_probe.py::self_test` is causal, not nominal:
shortening the send interval 5x must yield ~5x the packets. Two earlier versions
of this guard were themselves useless -- one passed while the NED file failed to
load, the other used sensitivity = -1e9 dBm, which is *maximum* sensitivity, not
invalid, so every packet still arrived.

**Status of older claims.** Any Step A/B number produced through
`**.uav[*]...` patterns must be treated as unverified. The 98.75% unicast PDR
figure came from the example ini run directly (not through those patterns) and
is plausible, but it is not a PDR(distance) measurement and must not be quoted
as one.
