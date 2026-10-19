# Autonomous R&D State Tracker

## Current Phase
Phase 4: Report correction & paper completion (FINDINGS.txt audit)

## Professor Feedback
- Source: `Mlawn_midsem_report_FINAL_proff_feedback.pdf` (scanned images, no OCR)
- Independent review: `FINDINGS.txt` (20+ correctness findings, 5 literature findings)
- Key criticisms: dt/d_safe inconsistency, P_comm power level, z0 undefined, R_cov/Omega, symbol collisions, critic loss, value normalisation, reward undefined, "Swift" undefined

## Research Synthesis
- DeepResearch/QwenTab1.md: K-coverage feasibility, alternative metrics
- DeepResearch/QwenTab2.md: MAPPO correctness, GAE, hyperparameters
- FINDINGS.txt: 20 correctness findings + 5 literature findings with specific fixes

## Experiment Log
| Hypothesis | Change | Config | Result | vs Baseline |
|---|---|---|---|---|
| Feasible config (N=8) | N=5→8 | N=8,K=2,R=35 | CK=0.930±0.051, AG=1.0, SC=0.2 | SC 0→0.2 |
| GAE bootstrap fix | 0→V(s_{t+1}) | N=8,K=2 | Training converges | Fixed |
| Non-degenerate metrics | CovIntegral, MaxRefresh | all | Implemented | New |
| Reserve ablation | remove reserve | S8 stress | -0.058 CK | Confirmed |

## Paper Section Checklist
- [x] Introduction (updated with invention framing)
- [x] Literature Survey
- [x] System Model (needs fixes C1-C6, C11-C17)
- [x] Proposed ML Algorithm (needs fixes C7-C10, C13)
- [x] Comparison Models
- [x] Performance Metrics (updated with non-degenerate metrics)
- [x] Experimental Design Matrix
- [x] Results (added with feasible config numbers)
- [x] Conclusion (updated with honest limitations)
- [x] Feasibility Certificate (new subsection added)

## Active Task
Applying FINDINGS.txt fixes in priority order (Groups 1-5)