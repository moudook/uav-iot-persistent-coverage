# STATE — current sprint state

Last update: 2026-10-25 13:20 local

## Current gate / milestone
G0 — setup and trust (Oct 24–25). In progress.

## Hardware
- CPU: Intel i5-11400H, 6 cores / 12 threads
- GPU: NVIDIA RTX 2050, 4 GB VRAM, driver 610.62, CUDA 13.3
- RAM: (to be measured)
- Python 3.13.14, torch 2.6.0+cu124 (CUDA available)
- OS: Windows 11, PowerShell

## Running jobs
- OMNeT++ 6.4.0 install: tmux session omnet_install in WSL2 Ubuntu. Building omnetpp-6.4.0 (--install + configure + make -j4). Log: /tmp/opp_build.log

## Finished results
- Throughput benchmark: 231.8 steps/sec single env, 4.31 ms/step (N=5,M=20, 2000 steps). At this rate, 2e6 steps/seed ~2.4 h single-threaded; ~2.4 h for 6 parallel seeds. Vectorization (32-128 envs) needed for G1+.
- SC biconditional fixed in Mlawn-midsem-tex.tex (line 947): F=empty => SC=0 (one-directional). Gate passes.
- OMNeT++/INET: NOT installed. opp_env + OMNeT++ 6.4 + INET 4.7 needed.

## Decisions
- 2026-10-25: Initialized git repo at repo root (was not a git repo before). Committed docs/MASTER_PROMPT.md.
- 2026-10-25: Hardware matches prompt's "RTX 2050 4 GB" expectation.

## Open questions
- Is OMNeT++/INET installed? NO (as of 2026-10-25). Need opp_env + OMNeT++ 6.4 + INET 4.7.
- Is opp_env available?
- Is the existing Project1 simulator vectorized? (need throughput benchmark)

## BACKLOG (prioritized, >=10 items)
1. Measure RAM and disk free space.
2. Check if OMNeT++/INET/opp_env installed; record in docs/ENV.md.
3. Vectorize the existing UAV env and benchmark steps/sec (G0).
4. Validate MAPPO on MPE simple_spread or VMAS (G0/R7).
5. Fix SC biconditional (logic error, section 3.5 of master prompt) — retracted claim.
6. Mark retracted claims in docs/CLAIMS.md (0.298 gap, "none of the arms explains it", credit-assignment diagnosis).
7. Start novelty gate (Qwen Deep Research + DeepSeek + Google Scholar) for C1/C2/C3.
8. Install core Python stack if missing (numpy, numba, scipy, networkx, gymnasium, rliable, optuna, pytest, hypothesis).
9. Write PREREG.md skeleton (hypotheses H1-H4).
10. Write docs/CLAIMS.md skeleton.
11. Write docs/LOG.md.
12. Write docs/NEGATIVE.md.
13. Throughput benchmark smoke test (1 seed, short budget).
14. Inspect Project1/ml_impl simulator code structure for vectorization.

## BROWSER HOWTO
- Qwen Chat: https://chat.qwen.ai (Deep Research mode). Begin prompt with "Today is 2026-10-25. Prioritize 2024-2026 work..."
- DeepSeek: https://chat.deepseek.com (Search + DeepThink on).
- OMNeT++ AI docs: https://ai.omnetpp.org, https://ai-inet.omnetpp.org
- Veins-Gym pattern: https://github.com/ComNetsHH/omnetpp-ml/blob/main/docs/openai_gym.md

## HARD RULES (short form)
R1 artefact-only numbers. R2 pre-registration. R3 convergence before conclusions. R4 fair comparison (disjoint TRAIN/TUNE/TEST). R5 >=10 seeds main, >=5 ablations, rliable IQM. R6 headroom gate (ceiling - best rule >= 0.10). R7 trust the learner (validate on reference task). R8 mask audit. R9 sanity ordering. R10 honesty. R11 no fabricated citations. R12 reproducibility (seed, git hash, make paper). R13 claims ledger. R14 IEEE 6 pages, <=4 contributions. R15 no silent scope creep.
---
