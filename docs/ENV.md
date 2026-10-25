# ENV — environment record

## Hardware
- CPU: Intel Core i5-11400H, 6 cores / 12 threads
- GPU: NVIDIA GeForce RTX 2050, 4 GB VRAM, driver 610.62, CUDA 13.3
- OS: Windows 11, PowerShell
- RAM: (to measure)

## Python
- Python 3.13.14
- torch 2.6.0+cu124 (CUDA available)
- numpy 2.5.1, scipy 1.18.0, networkx 3.6.1, pandas 3.0.5, matplotlib 3.11.1, seaborn 0.13.2
- gymnasium 1.4.0, pettingzoo 1.27.0, rliable 1.2.0, optuna 5.0.0
- pytest 9.1.1, hypothesis 6.165.1, ruff 0.17.2
- pyzmq 27.1.0, protobuf 6.33.6
- numba: (to check)

## OMNeT++ / INET
- IN PROGRESS (2026-10-25): opp_env + OMNeT++ 6.4.0 downloading via WSL2 Ubuntu 26.04 (tmux session omnet_install). Download ~30% complete and climbing. Source partial. Build (configure + make -j4) pending.
- Install plan: follow https://omnetpp.org/download/ and https://inet.omnetpp.org (ai docs at https://ai.omnetpp.org).

## OMNeT++ AI docs
- https://ai.omnetpp.org
- https://ai-inet.omnetpp.org

## Tools not available on Windows
- tmux (use background processes + watchdog script instead)
- nproc (use (Get-CimInstance Win32_Processor).NumberOfLogicalProcessors)
- head/tail (use Select-Object -First/-Last)
- wc (use Measure-Object)
---
