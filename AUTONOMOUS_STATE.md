# Autonomous R&D State Tracker

> **RE-READ THIS FILE FIRST AFTER ANY CONTEXT COMPACTION.**
> Then re-read `Mlawn-midsem-tex.tex` and `FINDINGS.txt` before writing
> anything. Never write paper sections or modify code from memory alone.

## Contract
Autonomous 1-week sprint: **19 Oct 2026 -> 26 Oct 2026**.
The user (PhD-level R&D contractor arrangement) granted full autonomy:
implement, test, train, write, commit locally, never push, never install
packages without asking, never open >2 browser tabs at once.

## THE CRITICAL FACT (read this first)
**The simulator was STATIC until commit `13cb839`.** The motion step applied a
move only when `np.all(action_mask(i))` was true, i.e. when EVERY action
(including A_CHARGE) was feasible. A_CHARGE is almost never feasible, so
**no UAV ever moved**. Consequences:
- coverage could not change -> every controller scored identically;
- the persistent-coverage problem was a *motion* problem and was not simulated;
- the action mask / H-step lookahead / articulation check were exercised on a
  static swarm -> they appeared to have no effect in the ablation;
- **every result measured before `13cb839` is invalid and has been discarded.**

Fix: apply the move when the **chosen** action is feasible. The mask is now
computed once per step for all agents against the pre-move state.

## Current Phase
Phase 6: regenerate ALL results on the now-dynamic simulator, then rewrite
the paper's Results/Conclusion/Abstract around the new numbers.

## Key Files
| Path | What |
|---|---|
| `Mlawn-midsem-tex.tex` | The paper. 14 pages, compiles clean, 0 undefined refs. |
| `FINDINGS.txt` | Independent review: 20 correctness + 5 literature findings. **Read it.** |
| `ml_impl/run_all.py` | **Single driver for the whole experiment matrix.** `python run_all.py` |
| `ml_impl/analysis/claim_audit.py` | Recomputes every checkable claim (17 pass / 0 fail / 4 INFO). |
| `ml_impl/analysis/phy_equivalence.py` | Python PHY vs INET path loss: max 0.012 dB. |
| `ml_impl/analysis/dormancy.py` | Per-agent plasticity probe (0.000 dormant, 0.000 dead). |
| `ml_impl/analysis/clustered_comparison.py` | Baselines vs both MAPPO arms, clustered start. |
| `ml_impl/analysis/symmetry_check.py` | Diagnostic for the shared-actor symmetry problem. |
| `ml_impl/analysis/diagnose_gap.py` | Separates protocol / sharpness / regime. |
| `ml_impl/analysis/ab_per_agent_adv.py` | A/B on advantage normalisation. |
| `Simulation/UAV_IoT_Demo/sim/PhyValidation.ned` | OMNeT++ 802.11 PHY scenario + control. |
| `DeepResearch/DeepSeekTab1-3.md` | Batch 1+2 research (saved via browser download trick). |
| `AUTONOMOUS_STATE.md` | This file. |
| `C:\Users\gbust\.config\opencode\skills\browser-navigation\references\chatbots.md` | DeepSeek recipe (updated this session). |

## Defects found and fixed (all have tests; 73 tests pass)
| # | Defect | Fix / commit |
|---|---|---|
| 1 | **Simulator was static -- no UAV ever moved** | chosen-action feasibility test; `13cb839` |
| 2 | Baselines accepted `seed` and ignored it -> "5 seeds" was 1 scene x5 | `_seeded()`; `d113e5c` |
| 3 | Env reported the time limit through the terminal flag -> GAE bootstrapped 0 at every boundary | `terminated` vs `truncated`; `d113e5c` |
| 4 | Centred-ring start pre-solved the task (CK 0.850 at t=0) | `start_clustered=True` (CK 0.150); `957ee1c` |
| 5 | `run_scenarios` passed `seed=0` over the config's own seed | pass `c.seed`; `957ee1c` |
| 6 | `run_scenarios` evaluated only the first variant of each scenario | evaluate every variant |
| 7 | Reward eq (23) negated only U_t | pure `reward_from_terms` |
| 8 | Initial placement disconnected on 11/20 seeds | `_connected_initial_positions` |
| 9 | Backhaul modelled as co-channel interference | SNR-based backhaul |
| 10 | `snr_to_rate` off-by-one + floor made the PHY gate vacuous | `side="right"-1`, 0.0 below sensitivity |
| 11 | Path-loss exponent additive -> LoS/NLoS erased | `pl_d0 + 10n log10(d/d0)` |
| 12 | Noise units: dBm treated as watts (30 dB error) | divide by 1000 |
| 13 | Shadowing drawn from the global RNG -> non-reciprocal, non-reproducible | seeded per-episode table |
| 14 | `local_obs` neighbour stride 2 with 4 fields/slot -> slots overlapped | concatenation + assertion |
| 15 | `STATE_DIM = 80` hardcoded (only valid for N=5) | `state_dim(cfg)` |
| 16 | GAE bootstrap at truncation used 0 instead of V(s_{t+1}) | fixed in `collect_rollout` |
| 17 | Observation carries no agent identity -> shared actor cannot specialise | `use_agent_id` option (Foerster condition ii) |

`tests/mutation_check.py` proves the suite catches all 10 historical bugs.

## Experiment log
| # | Hypothesis | Change | Result |
|---|---|---|---|
| 1 | Feasible config | N=5 -> 8 | N=5/K=2 provably infeasible; N=8 feasible |
| 2 | GAE bootstrap | 0 -> V(s_{t+1}) | fixed silent bug |
| 3 | Non-degenerate metrics | CovIntegral, MaxRefresh | implemented + tested |
| 4 | Reserve ablation | remove reserve | -0.058 CK (on the now-invalid static sim) |
| 5 | Plasticity probe | per-agent backward | 0.000 dormant / 0.000 dead vs 40-45% reported for vanilla MAPPO |
| 6 | Model equivalence | Python vs INET source | max 0.012 dB over 24 points |
| 7 | Claim audit | recompute 21 claims | 17 verified, 0 failed, 4 informational |
| 8 | Baseline seeding | apply seed | Fixed baseline rose 0.850 -> 0.900 (honest) |
| 9 | Task headroom | clustered start | baselines fell 0.900 -> 0.350 |
| 10 | Shared-actor symmetry | measured distinct actions | **1.00 of 8** under deterministic eval; swarm spread frozen at 8.5 m |

**All of rows 1-4 and 8-10 were measured on the STATIC simulator and must be
re-run after `13cb839`.**

## Key numbers (ALL PENDING REGENERATION after the static-simulator fix)
- Feasibility: N >= 4K; N=5/K=2 provably infeasible; N=8 feasible; oracle CK = 1.000
- Dormancy probe: 0.000 dormant, 0.000 dead, 15-31% gradient-silent (this one
  is NOT affected by the static bug -- it measures the network, not the motion)
- Model equivalence: max 0.012 dB (not affected)
- Claim audit: 17/0/4 (not affected)

## The paper's structure is now settled; only numbers change
- Introduction: invention = **feasibility-certified evaluation framework**
  (lower bound + achievability ceiling + non-degenerate metrics).
- Research Gap: rewritten to NAME the near-misses (Trotta 2018, Scherer 2016,
  Hartuv 2018, Shi 2025, Song 2024, Fan 2026, Datta 2025, Viana 2026,
  "Feasibility Ceilings Before Learning" arXiv:2610.20823).
- **Two externally verified absences** (DeepSeek Tab 3, over the same corpus):
  (a) no 2023-2026 paper certifies a persistent-coverage instance INFEASIBLE;
  (b) no 2023-2026 paper names the all-constraints-simultaneous metric as
  degenerate.  Both are in the paper with the corpus bound stated.
- New subsections: Feasibility Certificate; Claim Audit and PHY Validation.
- Theory now cited: Huang & Ontanon (FLAIRS 2022) for masking + its
  single-agent limit; Pardo et al. (ICML 2018) for the truncation bootstrap;
  Foerster et al. (AAMAS 2016) for the parameter-sharing conditions; Fu et al.
  (ICML 2022) for the XOR limitation.
- Negative result reported honestly: the first OMNeT++ validation counted MAC
  frames and reported links closing at 50 km; a control with TX crushed 60 dB
  returned the same count, proving the observable was not physical. The paper
  claims only model equivalence (0.012 dB), not a runtime cross-validation.

## DeepSeek research protocol (2-tab limit, STRICT)
- Batch 1: Tab 1 (K-coverage literature gap) + Tab 2 (MAPPO correctness) -- DONE, saved.
- Batch 2: Tab 3 (non-degenerate coverage metrics) -- DONE, saved.
- Recipe (now in the browser-navigation skill): one pushback per COMPLETED
  reply; confirm the reply has settled via `innerText.length` stopping; ~2 min
  wait; explicit DATE CORRECTION (the model assumes an earlier year -- it
  believed 2025 when the date was Oct 2026); save via the Blob-download trick
  (`browser.evaluate` -> anchor click -> `browser.files.list` ->
  `browser.files.get`), which moves a 40 KB transcript to disk with zero
  transcript text through the model context.
- `browser.evaluate` takes **`script`**, not `expression`. `setTimeout` is not
  available in the Code Mode runtime -- use a background shell command.

## Browser skill (updated)
`C:\Users\gbust\.config\opencode\skills\browser-navigation\references\chatbots.md`
-- DeepSeek section now has: the tool-API gotchas, the download-to-disk trick,
the date correction, rate-limit recovery, and the pushback pacing rule.

## IMMEDIATE NEXT STEPS (in order)
1. `cd Project1/ml_impl && python run_all.py` (full matrix, ~40-60 min) on the
   now-dynamic simulator. Consider making the base config `start_clustered=True`
   so the task has headroom -- decide by looking at the numbers.
2. Run `python analysis/clustered_comparison.py` for the decisive comparison.
3. Re-run `analysis/claim_audit.py`, `analysis/phy_equivalence.py`,
   `analysis/dormancy.py` (the last two are unaffected by the motion fix).
4. Rewrite the paper's Results, Conclusion and Abstract with the NEW numbers;
   the claim structure stays as it is now.
5. Refresh `ml_impl/README.md` to match.
6. Commit after every milestone.
