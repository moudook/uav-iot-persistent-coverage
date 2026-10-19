# Autonomous R&D State Tracker

## Current Phase
Phase 5: Claim audit, PHY validation, and manuscript completion.

**Contract:** autonomous 1-week sprint, 19 Oct 2026 -> 26 Oct 2026.
Re-read this file, `Mlawn-midsem-tex.tex`, and `FINDINGS.txt` after any
context compaction before writing anything.

## Key Files
| Path | What |
|---|---|
| `Mlawn-midsem-tex.tex` | The paper. Compiles clean, 13 pages, 0 undefined refs. |
| `FINDINGS.txt` | Independent review: 20 correctness + 5 literature findings. **Read this.** |
| `Mlawn_midsem_report_FINAL_proff_feedback.pdf` | Professor feedback (8 scanned pages, no OCR available) |
| `ml_impl/analysis/claim_audit.py` | Recomputes every checkable claim. 17 verified, 0 failed, 4 INFO. |
| `ml_impl/analysis/phy_equivalence.py` | Python PHY vs INET `BreakpointPathLoss`. max delta **0.012 dB**. |
| `ml_impl/analysis/phy_validation.py` | OMNeT++ cross-validation harness (control-driven). |
| `ml_impl/analysis/feasibility.py` | Region/sensor packing bounds + teleporting oracle. |
| `Simulation/UAV_IoT_Demo/sim/PhyValidation.ned` | OMNeT++ 802.11 PHY scenario. |
| `Simulation/UAV_IoT_Demo/simulations/phy_validation.ini` | 6 configs incl. the negative control. |
| `Simulation/UAV_IoT_Demo/results/*.sca` | OMNeT++ scalar outputs (evidence). |

## Professor Feedback -> Status
| Finding | Status |
|---|---|
| C1 dt/d_safe/v_max consistency | dt=0.2 s already; braking distance 25 m recorded as a stated limitation |
| C2 P_comm power level | Table IV has P_elec=5 W, P_tx=0.5 W (already split) |
| C3 z0 undefined | z0=50 m present, footprint half-width 37.7 m (74 deg FOV) |
| C4 R_cov/Omega | 80x80 m, R_cov=35 m; N=8 now feasible |
| C5 a_i symbol clash | already kappa_i |
| C7 MAPPO critic loss | replaced with clipped form + Huber/clip/normalize note |
| C8 value normalisation | stated in the report |
| C9 detach statement | stated ("computed once per rollout, treated as a constant") |
| C10 parameter sharing | rewritten with Foerster conditions + Fu et al. limitation |
| C11 sink undefined | sink added as a graph vertex |
| C13 sign consistency | sentence present |
| C15 "Swift" undefined | already removed |
| C16 symbol collisions | already E_t^cons / D_t^deg / R_t^rec |
| C17 reward terms | all six defined in the Table V |
| D1 Trotta 2018 missing | ADDED to Table I + bibliography |
| D2 gap statement vacuous | REWRITTEN to name the near-misses |
| D3 contribution 2 prior art | reframed as a design choice |
| D4 citation additions | hartuv2018, shi2025, scherer2016, datsko2024, luna2022 ADDED |
| D5 citation form | qiu2020 (ICC) added alongside the qiu2019 preprint |

## Experiment Log
| Hypothesis | Change | Config | Result |
|---|---|---|---|
| Feasible config | N=5 -> 8 | N=8,K=2,R=35 | CK 0.930+-0.051, AG 1.0, **SC 0.200** (was 0.0) |
| GAE bootstrap | 0 -> V(s_{t+1}) | all | fixed silent bug |
| Non-degenerate metrics | CovIntegral, MaxRefresh | all | implemented + tested |
| Reserve ablation | remove reserve | S8 stress | -0.058 CK |
| Multi-seed training | seeds 0-4 | N=8,K=2 | final CK [0.95,0.95,1.00,0.85,0.90]; every seed hits CK=1.0 |
| Claim audit | recompute all claims | 21 items | 17 verified, 0 failed, 4 INFO |
| PHY model equivalence | Python vs INET source | 24 points | max 0.012 dB |
| OMNeT++ control | TX power -60 dB | 1e-6 W | **control FAILED the first observable** -> rebuilt |

## IMPORTANT NEGATIVE RESULT (do not forget)
The first OMNeT++ validation counted MAC frames and reported links closing at
50 km. The control (TX crushed 60 dB) returned the same count, proving the
observable was not physical. `minSnir` turned out to be a cached constant
(identical for every node, every range, every power). **A physical-layer claim
without a negative control is not a measurement.** The control config
`PhyValidationControl` is kept so the check is repeatable. The paper reports
this as a methodological point, and the *model equivalence* (0.012 dB) is what
is actually claimed, not a runtime cross-validation.

## Paper Section Checklist
- [x] Introduction (invention framing)
- [x] Literature Survey (+3 near-miss rows, Trotta 2018)
- [x] Research Gap (rewritten to name counterexamples)
- [x] System Model (sink vertex, reward terms, parameter consistency para)
- [x] Feasibility Certificate (NEW subsection)
- [x] Proposed ML Algorithm (clipped critic loss, sharing justification)
- [x] Comparison Models
- [x] Performance Metrics (+2 non-degenerate metrics)
- [x] Results (base, ablation, multi-seed)
- [x] Claim Audit and PHY Validation (NEW subsection)
- [x] Conclusion (results + honest limitations)

## Remaining Work
- [ ] Re-run base/ablation with the corrected physical parameters? (optional;
      the report records the current values and their derived quantities)
- [ ] DeepSeek research batches 1-2 (2-tab limit) for 2023-2026 citations
- [ ] Refresh README numbers to match the report
- [ ] Final compile + commit before 26 Oct
