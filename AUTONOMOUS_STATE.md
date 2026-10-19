# Autonomous R&D State Tracker

> **RE-READ THIS FILE FIRST AFTER ANY CONTEXT COMPACTION.**
> Then re-read `Mlawn-midsem-tex.tex` and `FINDINGS.txt` before writing
> anything. Never write paper sections or modify code from memory alone.

## Contract
Autonomous 1-week sprint: **19 Oct 2026 -> 26 Oct 2026**.
The user (PhD-level R&D contractor arrangement) granted full autonomy:
implement, test, train, write, commit locally, never push, never install
packages without asking, never open >2 browser tabs at once.

## THE CRITICAL FACT
**The simulator was STATIC until commit `13cb839`.** The motion step applied
a move only when `np.all(action_mask(i))` was true, i.e. when EVERY action
(including A_CHARGE) was feasible. A_CHARGE is almost never feasible, so
**no UAV ever moved**. Every result measured before `13cb839` is invalid.
All results have been regenerated since.

## Current Phase
Phase 7: regenerate the whole matrix on the corrected simulator, then rewrite
the paper's Results, Conclusion and Abstract around the new numbers.

## THE CANONICAL CONFIGURATION (do not change without re-running everything)
`uav_wireless/experiments.py :: base_config()`
- N=8, K=2, R_cov=35 m, R_comm=40 m, M=20, side=80 m, z0=50 m
- `episode_len = 2000` steps (400 s of flight)
- B_max = 30 000 J, charge_rate = 0.0002/step, E_reserve = 2000 J, 2 pads
- `start_clustered = True` (connected corner cluster; 3/20 sensors covered
  at t=0, versus 17/20 for a centred ring that pre-solves the task)
- `use_agent_id = True`, `map_grid = 4`, `use_pad_bearing = True`
- Reference (Reactive heuristic, 3 seeds): CK=0.918 AG=1.000 SC=0.612

## Defects found and fixed (all have tests; 92 tests pass)
| # | Defect | Fix / commit |
|---|---|---|
| 1 | **Simulator was static -- no UAV ever moved** | chosen-action feasibility; `13cb839` |
| 2 | Baselines accepted `seed` and ignored it -> "5 seeds" was 1 scene x5 | `_seeded()`; `d113e5c` |
| 3 | Time limit reported as termination -> GAE bootstrapped 0 at every boundary | `terminated` vs `truncated`; `d113e5c` |
| 4 | Centred-ring start pre-solved the task | `start_clustered`; `957ee1c` |
| 5 | `run_scenarios` passed `seed=0` over the config's own seed | pass `c.seed`; `957ee1c` |
| 6 | Reward eq (23) negated only U_t | pure `reward_from_terms` |
| 7 | Initial placement disconnected on 11/20 seeds | `_connected_initial_positions` |
| 8 | Backhaul modelled as co-channel interference | SNR-based backhaul |
| 9 | `snr_to_rate` off-by-one + floor made the PHY gate vacuous | fixed |
| 10 | Path-loss exponent additive -> LoS/NLoS erased | `pl_d0 + 10n log10(d/d0)` |
| 11 | Noise units: dBm treated as watts (30 dB error) | divide by 1000 |
| 12 | Shadowing from the global RNG -> non-reciprocal, non-reproducible | seeded per-episode table |
| 13 | `local_obs` neighbour stride 2 -> slots overlapped | concatenation + assertion |
| 14 | `STATE_DIM = 80` hardcoded (valid only for N=5) | `state_dim(cfg)` |
| 15 | GAE bootstrap at truncation used 0 instead of V(s_{t+1}) | fixed |
| 16 | **Observation carried no agent identity** -> shared actor cannot specialise (measured 1.00 distinct actions out of 8) | `use_agent_id`; `44206f5` |
| 17 | **Observation could not express a return** -- it had the energy cost of the flight to a pad but not the direction | `use_pad_bearing`; `de3e1e6` |
| 18 | **No indication of where the coverage deficit is** | `map_grid` (4x4 broadcast summary); `44206f5` |
| 19 | **The energy state machine did not exist** -- the env never made the serve->return transition, so a learned policy could never charge | env makes the transition; `de3e1e6` |
| 20 | **A UAV with an empty pack still counted as serving** | out of service, reserve can recover it; `de3e1e6` |
| 21 | **Charging was uneconomic** -- a charging UAV was billed the full hover power, so it lost more than the pad put back | rotors idle on the pad; `de3e1e6` |
| 22 | **The battery never bound** -- at 400 steps the pack spent 13% and the return state never fired | episode 2000 steps; `de3e1e6` |
| 23 | **The returns were formed from an untruncated advantage array** -> shape mismatch whenever an episode ended early | truncate before forming returns |
| 24 | Two graph computations per candidate action (13.7 ms/step) | shared prospective graph, 6.8 ms/step |
| 25 | **MAPPO's value normalisation was missing** although the report asserted it | `MAPPO.value()` accessor + EMA statistics; `c4a71f6` |
| 26 | The report's comparison table named MARL baselines that were never evaluated | two implemented (`baselines_rl.py`); "Evaluated" column added; `c381bcf` |

`tests/mutation_check.py` proves the suite catches all 10 historical bugs.

## Key results so far (all on the CORRECTED simulator)
| Quantity | Value |
|---|---|
| Feasibility bound | N >= 4K; N=5/K=2 provably infeasible; N=8 feasible; oracle CK=1.000 |
| Reactive heuristic, clustered, 2000 steps | CK 0.947, AG 1.000, SC 0.751, CI 0.053 |
| Greedy, clustered | CK 0.770, AG 1.000, SC 0.062, CI 0.230 |
| Fixed, clustered | CK 0.372, AG 1.000, SC 0.000, CI 0.628 |
| Observation A local only | CK 0.658+-0.018, AG 0.979, SC 0.033, distinct(argmax) 1.47/8, spread 7.8 m |
| Observation B + identity | CK 0.507+-0.115, AG 0.977, SC 0.020, distinct(argmax) 2.43/8, spread 12.1 m |
| Observation C + identity + map | CK ~0.64 (2 seeds so far), distinct(argmax) 2.98/8 |
| Connectivity in the deployed regime (audit C6) | mean node degree 4.01 of 7; graph complete in only 12% of steps |
| Energy regime (Reactive, 2000 steps) | 283 return transitions, 0.7 stranded UAVs, 8.3% of the swarm returning |
| Claim audit | 22 items: 18 verified, 0 failed, 4 informational |
| Model equivalence | max 0.012 dB vs INET BreakpointPathLoss |
| INET runtime probe | minSnir tracks TX exactly (27.0 dB per 27.0 dB) but NOT distance (0.0000 dB spread over 10-80 m) |
| Dormancy probe | 0.000 dormant, 0.000 dead, 15-31% gradient-silent |
| Tests | 92 passing |

## THE CENTRAL FINDING (as of 20 Oct, still being confirmed)
**The shared-team-reward credit assignment, not the observation content, is
the binding limitation of the learned controller.** Evidence so far:
1. The policy stays near-uniform (entropy 1.2-1.5 of a maximum of 1.79) --
   it diffuses rather than commits.
2. Without the agent identity the argmax policy picks the same action for
   every UAV (1.47 distinct of 8) and the swarm's spread is frozen at 7.8 m.
3. ADDING the identity fixes that symptom (2.43 distinct, spread 12.1 m) but
   REDUCES coverage (0.658 -> 0.507): dispersing without coordination covers
   less, not more.
4. The coverage-map summary does not rescue it either (arm C ~0.64).
5. Per-agent advantage normalisation is ineffective, because with a
   broadcast team reward the per-agent advantage sequences are nearly
   identical, so normalising them per agent is a rescaling, not a
   reallocation of credit.

Competing explanation being tested: the policy may simply be under-trained
(analysis/convergence.py, 120 episodes). The Reactive heuristic reaches CK
0.947 while the learned policy's best training episode reaches ~0.82, so the
budget question is real and must be answered before the conclusion is drawn.

**Implication for the paper's framing:** the contribution is the
FEASIBILITY-CERTIFIED EVALUATION FRAMEWORK, and the framework's value is
precisely that it exposes this: a paper reporting only "CK = 0.93 vs 0.85"
was reporting a number produced by a simulator in which no UAV moved. The
honest result is that at the reported parameters the task is easy enough
that a well-designed reactive heuristic is competitive with parameter-shared
CTDE MAPPO, and the paper diagnoses why.


## IMPORTANT NEGATIVE RESULTS (do not forget)
- The first OMNeT++ validation counted MAC frames and reported links closing
  at 50 km. The control (TX crushed 60 dB) returned the same count, proving
  the observable was not physical. **A physical-layer claim without a
  negative control is not a measurement.** The paper claims only model
  equivalence (0.012 dB).
- The research found NO 2023-2026 paper that certifies a persistent-coverage
  instance INFEASIBLE, and NO paper that names the all-constraints-simultaneous
  metric as degenerate. Both are the paper's novelty claim.
- Closest prior work: "Feasibility Ceilings Before Learning"
  (arXiv:2610.20823, Oct 2026). The paper states the difference precisely.
- **The Reactive heuristic is a strong baseline** (CK 0.918). It is NOT
  legitimate to hide it: it is reported in every table, and the honest claim
  is about the JOINT invariant, not about coverage alone.
- The reward's articulation-point term (lam_C) penalises the very spreading
  behaviour coverage requires. The ablation now measures it rather than
  assuming it (variant "no-criticality").

## Commands
```
cd Project1/ml_impl
python run_all.py                 # the whole matrix (~5 h)
python run_all.py --stage obs     # observation A/B/C
python run_all.py --stage base    # base comparison
python run_all.py --stage abl     # ablations
python run_all.py --stage scen    # scenario matrix
python analysis/claim_audit.py    # every checkable claim
python analysis/energy_regime.py  # the energy-regime sweep
python tests/run_tests.py         # 88 tests
```

## Paper state
- 14 pages, compiles clean, 0 undefined refs.
- Sections already rewritten: abstract, feasibility certificate, claim audit
  and PHY validation, near-miss table, two externally verified absences.
- **Edited but NOT yet validated with numbers:** the local-observation
  section (identity + map + pad bearing), the parameter table (episode 2000,
  clustered deployment), the CTDE parameter-sharing paragraph, the
  initial-deployment / episode-length paragraph, scenario S9.
- **Still to rewrite once the matrix lands:** the whole Results section
  (Tables `tab:results_main`, `tab:results_abl`), the Conclusion, the
  abstract, and the limitations list.

## DeepSeek research protocol (2-tab limit, STRICT)
- Batch 1: Tab 1 (K-coverage literature gap) + Tab 2 (MAPPO correctness) -- DONE, saved.
- Batch 2: Tab 3 (non-degenerate coverage metrics) -- DONE, saved.
- Recipe (in the browser-navigation skill): one pushback per COMPLETED
  reply; confirm the reply has settled via `innerText.length` stopping; ~2 min
  wait; explicit DATE CORRECTION (the model assumes an earlier year); save
  via the Blob-download trick (`browser.evaluate` -> anchor click ->
  `browser.files.list` -> `browser.files.get`), which moves a 40 KB
  transcript to disk without putting it in the model context.
- `browser.evaluate` takes **`script`**, not `expression`. `setTimeout` is not
  available in the Code Mode runtime -- use a background shell command.
- NOTE: do NOT pipe a background job through `Select-Object -Last N`; it
  buffers everything until the process ends and the progress is invisible.
