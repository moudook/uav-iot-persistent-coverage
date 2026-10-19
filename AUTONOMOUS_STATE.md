# Autonomous R&D State Tracker

## Current Phase
Phase 5: results regeneration on a task with headroom.

**Contract:** autonomous sprint, 19 Oct 2026 -> 26 Oct 2026.
Re-read this file, `Mlawn-midsem-tex.tex`, and `FINDINGS.txt` after any
context compaction before writing anything.

## Key Files
| Path | What |
|---|---|
| `Mlawn-midsem-tex.tex` | The paper. 14 pages, compiles clean, 0 undefined refs. |
| `FINDINGS.txt` | Independent review: 20 correctness + 5 literature findings. |
| `ml_impl/run_all.py` | **Single driver for the whole experiment matrix.** |
| `ml_impl/analysis/claim_audit.py` | Recomputes every checkable claim. |
| `ml_impl/analysis/phy_equivalence.py` | Python PHY vs INET path loss: 0.012 dB. |
| `ml_impl/analysis/dormancy.py` | Per-agent plasticity probe. |
| `ml_impl/analysis/clustered_comparison.py` | The decisive comparison (clustered start). |
| `ml_impl/analysis/diagnose_gap.py` | Separates protocol / sharpness / regime. |
| `DeepResearch/DeepSeekTab1-3.md` | Batch 1 + 2 research (saved via browser download). |
| `Simulation/UAV_IoT_Demo/sim/PhyValidation.ned` | OMNeT++ 802.11 PHY scenario + control. |

## Defects found and fixed this session (all with tests)
| # | Defect | Fix |
|---|---|---|
| 1 | Baselines accepted `seed` and ignored it -> "5 seeds" was 1 scene x5 | `_seeded()` copies the config with the seed applied |
| 2 | Env reported the time limit through the terminal flag -> GAE bootstrapped 0 at every episode boundary | env reports `terminated` vs `truncated` separately |
| 3 | Centred-ring start pre-solved the task (CK 0.850 at t=0) | `start_clustered=True` -> CK 0.150 at t=0, still connected |
| 4 | `run_scenarios` passed `seed=0` while the config carried its own seed | pass `c.seed` |
| 5 | `run_scenarios` evaluated only the first variant of each scenario | evaluate every variant |

## KEY NUMBERS
| Result | Value |
|---|---|
| Feasibility bound | N >= 4K; N=5/K=2 provably infeasible; N=8 feasible |
| Oracle ceiling | CK = 1.000 (connected) |
| MAPPO, ring start, 50 ep, 5 seeds | CK 0.930+-0.051, AG 1.000, SC 0.200 |
| Baselines, ring start, 5 seeds (after seed fix) | CK 0.900, AG 1.000, SC 0.000 |
| Baselines, clustered start | CK 0.350+-0.147, AG 1.000, SC 0.000 |
| Dormancy probe | 0.000 dormant, 0.000 dead, 15-31% silent (vs 40-45% reported for vanilla MAPPO) |
| Model equivalence | max 0.012 dB vs INET BreakpointPathLoss |
| Claim audit | 17 verified, 0 failed, 4 informational |
| Tests | 70 passing; mutation check catches all 10 historical bugs |

## IMPORTANT NEGATIVE RESULTS (do not forget)
- The first OMNeT++ validation counted MAC frames and reported links closing
  at 50 km. The control (TX crushed 60 dB) returned the same count, proving
  the observable was not physical. `minSnir` turned out to be a cached
  constant. **A physical-layer claim without a negative control is not a
  measurement.** The paper reports this as a methodological point and claims
  only model equivalence (0.012 dB), not a runtime cross-validation.
- The research found NO 2023-2026 paper that certifies a persistent-coverage
  instance infeasible, and NO paper that names the all-constraints-simultaneous
  metric as degenerate. Both are the paper's novelty claim.
- Closest prior work: "Feasibility Ceilings Before Learning"
  (arXiv:2610.20823, Oct 2026). The paper no longer claims a first; it states
  the difference precisely.

## Paper Section Checklist
- [x] Introduction (invention framing)  [x] Literature Survey + near-miss table
- [x] Research Gap (names counterexamples + two verified absences)
- [x] System Model  [x] Feasibility Certificate  [x] Proposed ML Algorithm
- [x] Comparison Models  [x] Performance Metrics  [x] Experimental Design Matrix
- [x] Results  [x] Claim Audit and PHY Validation  [x] Conclusion

## Remaining Work
- [ ] Finish the clustered-start comparison and put the numbers in the paper
- [ ] Decide: pooled vs per-agent advantage, based on the A/B
- [ ] Re-run the full matrix (run_all.py) with the winning configuration
- [ ] Refresh README to match
- [ ] Final compile + commit before 26 Oct
