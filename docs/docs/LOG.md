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
