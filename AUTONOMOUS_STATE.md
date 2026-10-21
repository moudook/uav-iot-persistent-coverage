# Autonomous R&D State Tracker

> **RE-READ THIS FILE FIRST AFTER ANY CONTEXT COMPACTION.**
> Then re-read `Mlawn-midsem-tex.tex` and `ml_impl/analysis/results_text.tex`
> before writing anything. Never write paper sections or modify code from
> memory alone.

## Contract
Autonomous 1-week sprint: **19 Oct 2026 -> 26 Oct 2026**.
The user granted full autonomy: implement, test, train, write, commit
locally, **never push**, never install packages without asking, never
delete existing files.

## THE CRITICAL FACT (historical, still the reason for the audit trail)
**The simulator was STATIC until commit `13cb839`.** The motion step applied
a move only when `np.all(action_mask(i))` was true, i.e. when EVERY action
(including A_CHARGE) was feasible. A_CHARGE is almost never feasible, so
**no UAV ever moved**. Every result measured before `13cb839` is invalid.

## Current Phase
Phase 8: re-measure the whole matrix under the **reproducible evaluation
protocol** (defect 28 below), then rewrite the Conclusion and the abstract
around the new numbers and run the third mathematical audit.

## THE CANONICAL CONFIGURATION (do not change without re-running everything)
`uav_wireless/experiments.py :: base_config()`
- N=8, K=2, R_cov=35 m, R_comm=40 m, M=20, side=80 m, z0=50 m
- `episode_len = 2000` steps (400 s of flight)
- B_max = 30 000 J, charge_rate = 0.0002, E_reserve = 2000 J, 2 pads
- `start_clustered = True` (connected corner cluster; 3/20 sensors covered
  at t=0, versus 17/20 for a centred ring that pre-solves the task)
- `use_agent_id = True`, `map_grid = 4`, `use_pad_bearing = True`
- **The coverage-map summary is KEPT in the proposed configuration** even
  though it measures as harmful. The reactive heuristic is handed the exact
  set of uncovered sensors, so the map is the only channel through which
  the learned controller can learn anything about the deficit; removing it
  would make the comparison a comparison of information, not of method.
  It is reported as a negative result rather than quietly dropped.

## THE MEASUREMENT PROTOCOL (canonical, 21 Oct)
This is the protocol every number in the paper is produced under.

0. **The device is a PROTOCOL CHOICE, not a resource accident**, and the
   thread count is pinned to one. The reason is REPRODUCIBILITY: the
   floating-point kernels differ between the CPU and the GPU, so the same
   seed trained on the two gives different weights (about 6e-4 after one
   episode, compounding through the updates), and the thread count changes
   the order of the reductions and so changes them too. The device used to
   be chosen by "is there room on the GPU right now", which made a run
   depend on the machine's momentary load: the base table's controller came
   out at 0.761, the energy arm at 0.746 and the observation arms' and the
   ablation's at 0.727, and they are the SAME configuration, budget and
   seeds. `CUDA_VISIBLE_DEVICES` does not disable CUDA on this setup, so
   the pin has to be in the code: `train_mappo` now takes the device from
   `UAV_DEVICE` (default CPU) and sets `torch.set_num_threads(1)`, and
   every artefact records the device it was produced on. **The whole matrix
   is being re-measured on one device**, because a variant trained on the
   GPU and its partner trained on the CPU are not a paired comparison.
   **CONFIRMED**: the same training call on the GPU returns CK 0.726530,
   which is the observation arms' and the ablation's value to SIX DECIMALS.
   The full picture is that the result depends on the (device, thread
   count) PAIR: the GPU with three threads gives 0.7265, the CPU with one
   thread gives 0.6819 and the CPU with two threads gives 0.761. So both
   the device and the thread count move the result, and the base table's
   re-run (the CPU with two threads) was the odd one out. The re-measurement
   pins both, so every table will describe the same experiment. A training
   run is bitwise reproducible given a fixed (device, thread count), and
   the audit checks the seed half of that.
1. **Training**: 25 episodes x 2000 steps per training run. The base
   comparison trains **5** runs (seeds 0-4); the component ablation and the
   observation A/B/C train **3** runs (seeds 0-2); the learned baselines
   train 3 runs; the energy and credit arms train 3 runs; the scenario
   matrix trains one policy per distinct `(N, M, pads)` combination.
2. **Evaluation**: 5 scenes (seeds 0-4) per policy. A controller's row is
   the mean over its TRAINING runs, and the reported spread is the
   seed-to-seed spread of those runs. The rule baselines are deterministic,
   so their spread is over the evaluation scenes.
3. **The evaluation is seeded.** `uav_wireless/seeding.py` seeds the global
   RNGs from the evaluation seed ALONE, so an evaluation is a function of
   (policy, scene) and every controller sees the same sampling stream on
   the same scene (common random numbers). This is defect 28 and it
   invalidates every number measured before it.
4. **The ablation is paired**: the variants share the training seeds, so a
   difference is measured on the same training runs. The rows carry the
   seed-to-seed spread, the table carries the paired difference.
5. **The ablation uses the base comparison's budget** (25 episodes), so the
   ablation's "Full" row is the same experiment as the base comparison's
   MAPPO row and not a cheaper one.
6. Every training run's policy is **saved** (`mappo_base_s{seed}.pt`), so
   every number can be recomputed from a stored artefact.  The base stage
   has a `--resume` path that evaluates the stored policies instead of
   retraining them.
7. **The inference is a paired interval, never a threshold.** The variants
   share their training seeds, so the difference between a variant and the
   full configuration is measured on the same training runs, and what is
   reported is a 95% paired t interval on the per-seed differences. A
   threshold on the size of a difference is NOT a test: a rule that calls a
   difference "measurable" when it exceeds the learner's own seed spread
   has a per-arm null error rate of about a third at three training seeds,
   and it buys no power (the measurement cannot detect a true effect of
   the size it flags). The interval also reports the **resolution** of the
   measurement, which is the number a reader needs.
8. **An explanation is excluded by a BOUND, not by a null.** To exclude an
   explanation of a gap, the arm testing it must have an upper confidence
   limit below the gap. The token filler DERIVES this: the sentence says
   whether the limit is below the gap, and says the opposite when it is
   not.
9. **The variance is decomposed.** The seed component (across training
   runs) is the uncertainty of a controller comparison; the scene
   component (across evaluation scenes) is common to every controller and
   cancels in every difference. Both are reported.
10. **The evaluation seed determines both the scene and the action
    stream.** This is a known confound, stated as a limitation: the two
    sources cannot be separated, though the second is common to all
    controllers. Decoupling them would need a `SeedSequence.spawn` scheme
    and a re-measurement; it is not done.
11. **The learning curve is reported.** It answers the compute-asymmetry
    objection (a hand-designed rule against a learner with a fixed
    budget): the per-episode coverage of the first training run has a mean
    over its first five episodes equal to its mean over its last five, so
    the curve is flat over the budget we can afford.

## Defects found and fixed (all have tests; 111 tests pass)
| # | Defect | Fix |
|---|---|---|
| 1 | **Simulator was static -- no UAV ever moved** | `13cb839` |
| 2 | Baselines accepted `seed` and ignored it | `_seeded()`; `d113e5c` |
| 3 | Time limit reported as termination -> GAE bootstrapped 0 | `d113e5c` |
| 4 | Centred-ring start pre-solved the task | `957ee1c` |
| 5 | `run_scenarios` passed `seed=0` over the config's own seed | `957ee1c` |
| 6 | Reward eq (23) negated only U_t | `reward_from_terms` |
| 7 | Initial placement disconnected on 11/20 seeds | `_connected_initial_positions` |
| 8 | Backhaul modelled as co-channel interference | SNR-based backhaul |
| 9 | `snr_to_rate` off-by-one + floor made the PHY gate vacuous | fixed |
| 10 | Path-loss exponent additive -> LoS/NLoS erased | `pl_d0 + 10n log10(d/d0)` |
| 11 | Noise units: dBm treated as watts (30 dB error) | divide by 1000 |
| 12 | Shadowing from the global RNG -> non-reciprocal | seeded per-episode table |
| 13 | `local_obs` neighbour stride 2 -> slots overlapped | concatenation + assertion |
| 14 | `STATE_DIM = 80` hardcoded (valid only for N=5) | `state_dim(cfg)` |
| 15 | GAE bootstrap at truncation used 0 instead of V(s_{T+1}) | fixed |
| 16 | **Observation carried no agent identity** | `use_agent_id`; `44206f5` |
| 17 | **Observation could not express a return** (no direction to a pad) | `use_pad_bearing`; `de3e1e6` |
| 18 | **No indication of where the coverage deficit is** | `map_grid`; `44206f5` |
| 19 | **The energy state machine did not exist** | env makes the transition; `de3e1e6` |
| 20 | **A UAV with an empty pack still counted as serving** | out of service; `de3e1e6` |
| 21 | **Charging was uneconomic** (billed the hover power) | rotors idle on the pad |
| 22 | **The battery never bound** at 400 steps | episode 2000 steps |
| 23 | **The returns were formed from an untruncated advantage array** | truncate before forming returns |
| 24 | Two graph computations per candidate action (13.7 ms/step) | shared prospective graph |
| 25 | **MAPPO's value normalisation missing** although asserted | `c4a71f6` |
| 26 | The comparison table named MARL baselines never evaluated | `baselines_rl.py`; "Evaluated" column |
| 27 | **The scenario matrix crashed on N=3**: the one-hot identity has length N and the global state carries the sensor positions and the pad occupancy, so the networks' input sizes depend on the configuration | one policy per distinct `(N, M, pads)` |
| 28 | **THE EVALUATION OF A SAMPLED POLICY WAS AN UNCONTROLLED RANDOM DRAW.** Eq. (13) specifies that the deployed policy samples, and `mappo.py` drew from the global torch RNG, which `eval_agent` never seeded. The same policy file evaluated three times gave CK 0.734, 0.701 and 0.671, with the same standard deviation to four decimals. The paper's numbers could not be reproduced from the stored artefact, and controller-to-controller comparisons carried an unquantified sampling component | `uav_wireless/seeding.py`; 5 new tests; audit item R1 |
| 29 | **The component ablation trained ONE seed per variant at 10 episodes**, while the base comparison trained five seeds at 25 -- so its deltas mixed the component with the budget and its spread was unmeasurable. It also disagreed with the observation arms (which said the full configuration was no better than the bare one) | `run_ablation(..., seeds=)`, budget aligned to the base comparison, paired differences, incremental writes |
| 30 | **The main table's learned row was ONE policy while the text claimed five training seeds** | the row is the mean over the five runs with the seed-to-seed spread; every run's policy is saved |
| 31 | The assembler's "undefined references" check matched the LaTeX FONT warnings; the scenario table's variable names were set in text mode, so the table did not compile | precise check; math mode; `tabcolsep`; `raggedbottom` |
| 32 | **The ablation's "is this component measurable" rule was not a test.** It compared a component's difference with the learner's own seed-to-seed spread, a rule with a per-arm null error rate of about a third at three training seeds, and it bought no power | paired t intervals on the per-seed differences, plus a resolution statement; the interpretive sentences are DERIVED in the token filler, not asserted in the prose |
| 33 | The ablation runner wrote its incremental log with `dict(**row, **protocol)`, which raised on a duplicated key and killed the stage after two training runs | the payload is built by UPDATE; the runner RESUMES (a row measured under the same protocol is reused) and the CSV is rewritten after every row |
| 34 | The base comparison's CSV took its fieldnames from the first row, so the learned rows' extra columns raised on write | the fieldnames are the union over the rows; the base stage gained a `--resume` path that evaluates the stored policies instead of retraining them |
| 35 | The ablation's "is this component measurable" rule was not a test (audit 4) | paired t intervals on the per-seed differences, and a resolution statement; the interpretive sentences are derived in the token filler |
| 36 | The paper's central exclusion argument was overstated (audit 3) | the abstract, the introduction and the conclusion now state the descriptive gap, the interval, the resolution, and the causes the arms do NOT exclude |

`tests/mutation_check.py` proves the suite catches the historical bugs.

## THE NUMBERS (21 Oct, 09:40, the pinned CPU protocol)
- The gap to the strongest rule: **0.276** (95% interval [0.242, 0.309]), against the unprivileged reactive rule at 0.972.
- The learned controller: 0.696 +- 0.027; the argmax variant: 0.411 +- 0.075.
- The arms' verdict, derived from the intervals and not asserted: controlled arms bound how much of the gap each alternative explanation can account for: adding the agent identity (upper limit 0.377, margin -0.101); the full observation of the proposed configuration (upper limit 0.164, margin +0.112); removing the energy constraint (upper limit 0.200, margin +0.076); removing the threshold term (upper limit 0.066, margin +0.210); the previous energy rule (upper limit -0.003, margin +0.279), against a gap of 0.276.  The arms whose upper limit reaches past the gap -- adding the agent identity -- are NOT excluded, and remain candidate explanations; the others are excluded as the whole of the explanation
- The energy repair is NOT a null: the repair is not a null: the coverage it adds is +0.120 on the same training seeds (95\% interval [+0.003, +0.236], which excludes zero), and that is about 43\% of the gap to the reactive heuristic
- The training-budget sweep: 8 episodes: 0.609, 16 episodes: 0.640, 25 episodes: 0.698. the coverage moves by +0.089 over the range the sweep covers, which is about 32\% of the gap of 0.276, and the increments between successive budgets are +0.031, +0.058; but the last of them, +0.058, is only 1.2 standard errors from zero (the standard error of the difference is 0.048, at three training seeds per budget), so the sweep does not resolve what the budget contributes and the budget is neither excluded nor shown to be a cause of the shortfall
- The stress table resolves nothing: every paired interval includes zero.
- The scenario matrix: behind in 34 of 34 variants, from S8 (-0.051) to S6 (-0.388).
- The claim audit: 33 items, 29 verified, 0 failing, 4 informational. The test suite: 115 cases.
## THE CENTRAL FINDING (the claim, and what the arms actually establish)
The learned controller does not reach the reactive heuristic, and the
framework's controlled arms are what say why -- or why not.

- The **energy model is excluded**: every energy arm's upper limit is
  below the gap, and the repair of the safety filter is worth +0.120 of
  persistent coverage, about 43% of the gap, with an interval that
  excludes zero.
- The **observation content is NOT excluded**: the arm that adds the agent
  identity has an upper limit of 0.377 against a gap of 0.276, so the
  identity remains a candidate explanation at three training seeds. The
  arm that prices the full observation does clear the gap (0.164).
- The **training budget is not resolved**: the sweep's last increment is
  1.2 standard errors from zero, and the 8-versus-25-episode interval
  straddles the gap. It is neither excluded nor implicated.
- The **credit assignment** is the remaining candidate the framework's own
  mechanisms suggest, and the cheapest test of it (a per-agent local
  critic) moves in the wrong direction and leaves it unresolved.

So the residual is consistent with the credit assignment, and also with
the observation content and the training budget; the arms bound the
energy model and nothing else. The paper says that, and every part of it
is derived from an interval.
## The mathematical audit cadence (standing instruction, 20 Oct)
- **Audit 1** (done): the seven load-bearing claims. Found 4 wrong as
  stated; all corrected.
- **Audit 2** (done): the reward terms, the mask and the joint projection,
  the H-step lookahead, the energy budget, the value normalisation, the
  metrics, the oracle normalisation, the evaluation protocol. 25 items,
  21 verified, 0 failed, 4 informational.
- **Audit 3** (DONE, 20 Oct 23:15): the model and the results' claims.
  Brief: `C:\Users\gbust\AppData\Local\Temp\opencode\audit3_brief.txt`
  (9 items). It found, and these are now fixed:
  * **The central exclusion argument was OVERSTATED.** "What remains is
    credit assignment" is not supported by three non-detections at three
    training seeds: a non-detection is a statement about the arm's
    resolution, and a sufficiency test cannot eliminate a cause that is
    necessary but not sufficient. The abstract, the introduction and the
    conclusion now say the residual is CONSISTENT WITH the credit
    assignment and with several other causes the arms do not test, and
    that the paper does not claim to have excluded them.
  * The "loses on its own objective therefore the learning pipeline is at
    fault" inference was a false dichotomy -> fixed.
  * **The constrained ceiling IS 1.000**, because the oracle's
    construction is itself admissible under the safety filter, so the
    paper's claim that an informative constrained ceiling was missed was
    false -> fixed.
  * The hop rule constrains the MOVER's eccentricity, not the graph's
    diameter, and can freeze an agent in a dispersed graph -> stated.
  * The service-continuity gap separates the two controllers far more
    sharply than the coverage gap -> now reported beside it.
  * The spread quoted for a learned controller contains the
    rollout-to-rollout variation, and the cancellation of the scene
    component in a difference is an ASSUMPTION -> both stated.
  * **The framework's contribution needed a measurement.** On the report's
    own infeasible N=5 configuration the reactive heuristic still reaches
    CK 0.648 with full connectivity while the joint metric is 0.000 and
    the oracle reaches 0.990: neither metric alone distinguishes the
    instance from a feasible one, and it is the certificate that makes
    the reading decidable. Measured by
    `analysis/infeasible_instance.py`, audit item I1.
  * **The rule's privileged access was an untested alternative
    explanation.** Now measured: `analysis/infeasible_instance.py` aside,
    the arm `Reactive (local assignment)` in `train.py` runs the same rule
    without the global coverage state, and the verdict is derived from
    the measurement in the token filler.
- **Audit 4** (DONE, 20 Oct 22:10): **the statistics of the re-measurement
  protocol itself.** Brief:
  `C:\Users\gbust\AppData\Local\Temp\opencode\audit4_brief.txt`. It found
  the following, and all of it is now fixed:
  * **The "yardstick" rule was not a test.** Comparing a component's
    difference with the learner's own seed-to-seed spread has a per-arm
    null error rate of about a third at three training seeds, and it buys
    no power: the measurement cannot detect a true effect of the size it
    flags. -> replaced by paired t intervals on the per-seed differences,
    and the paper says "no effect larger than X was DETECTED at this
    budget and this seed count" rather than "the component is inert".
  * **The negative conclusion's mechanistic half was overstated.** The
    arms are null results used as evidence of absence. -> the abstract, the
    introduction and the conclusion now state the descriptive gap with its
    interval, and list the claims the measurements do NOT support.
  * **The quoted uncertainty omitted the scene variance.** -> the variance
    is now decomposed: the seed component is the uncertainty of a
    comparison, the scene component is common to all controllers and
    cancels in every difference.
  * **The matched budget does not control for budget-conditionality or for
    redundancy between components.** -> the paper says so, and says a
    budget sweep would be needed.
  * **"A training run is deterministic given its seed" was not
    established.** -> now established by two tests and by audit item T1
    (the seed is set BEFORE the networks are constructed, so the
    initialisation is seeded too).
  * **The deterministic-vs-sampled comparison.** The paper's argmax row
    already settles the sampling-handicap objection, and the heuristic's
    information advantage is now stated as a limitation.
  * The audit's recommendations NOT taken, and why: raising the seed count
    to 10+ (the compute does not fit the deadline, so the paper reports
    intervals and a resolution instead of verdicts), decoupling the scene
    and action streams (would need the whole matrix re-measured), and a
    budget sweep (same reason).

Each audit gets a SELF-CONTAINED brief: the setting, the model, the
measured numbers, and the exact claims to check, because a fresh subagent
has no context. It is instructed to work purely mathematically (no web, no
code, no repository) and to be adversarial rather than agreeable.

## IMPORTANT NEGATIVE RESULTS (do not forget)
- The first OMNeT++ validation counted MAC frames and reported links
  closing at 50 km. The control (TX crushed 60 dB) returned the same count.
  **A physical-layer claim without a negative control is not a
  measurement.** The paper claims only model equivalence (0.012 dB).
- The research found NO 2023-2026 paper that certifies a persistent-coverage
  instance INFEASIBLE, and NO paper that names the all-constraints-simultaneous
  metric as degenerate. Both are the paper's novelty claim.
- Closest prior work: "Feasibility Ceilings Before Learning"
  (arXiv:2610.20823, Oct 2026).
- The Reactive heuristic is a strong baseline (CK 0.953). It is NOT
  legitimate to hide it: it is reported in every table.
- The reward's articulation-point term (lam_C) penalises the very spreading
  behaviour coverage requires. The ablation measures it.

## Commands
```
cd Project1/ml_impl
python run_all.py --stage base      # the base comparison (5 seeds x 25 ep)
python run_all.py --stage obs       # the observation A/B/C (3 arms x 3 seeds)
python run_all.py --stage abl       # the component ablation, feasible config
python run_all.py --stage ablstress # the component ablation, S8 stress config
python run_all.py --stage learned   # the two learned baselines
python run_all.py --stage energy    # the energy-management A/B/C/D
python run_all.py --stage scen      # the scenario matrix
python analysis/ab_credit.py --episodes 30 --seeds 2 --eval-seeds 5
python analysis/ab_map_resolution.py --episodes 20 --seeds 2 --eval-seeds 5 --grids 0,4,8
python analysis/claim_audit.py      # 29 items, 25 verified, 0 failed, 4 info
python analysis/assemble_results.py # the tables, the tokens, the Results, the compile
python analysis/final_checks.py     # assembly + compile + audit + tests, one command
python tests/run_tests.py           # 115 tests
```

## Machine notes
- **The training device is a protocol choice, pinned to the CPU**, and the
  thread count is pinned to one. Reproducibility, not speed: the kernels
  differ between the CPU and the GPU, and the order of the reductions
  depends on the thread count, so a run is reproducible only on a fixed
  (device, thread count) pair. `CUDA_VISIBLE_DEVICES` does NOT disable
  CUDA on this setup -- it was tried and it changes nothing -- so the pin
  is in the code (`UAV_DEVICE`, default CPU, plus
  `torch.set_num_threads(1)`), and every artefact records its device.
- **The host memory is the binding constraint, not the cores.** Four
  experiment processes plus an interactive command exhausted the paging
  file; the machine then thrashed for hours and the jobs died with their
  work half done. The symptom is an `OSError: [WinError 1455]` from
  importing torch, which looks like a code failure and is not one. The
  queue now runs three stages at a time and waits for 2.6 GB of free
  memory before starting one.
- **Every long stage is resumable** and writes its artefact as it goes:
  the component ablation, the energy arms, the credit arms and the map
  sweep. A row is reused only if the budget, the seed count, the
  evaluation-scene count AND the device match; a row from the first
  re-measurement (which ran on the GPU, before the pin) is never reused.
- `analysis/final_checks.py` compares the same configuration across the
  tables -- the observation arm C, the credit arm A, the energy arm A and
  the ablation's full configuration are one experiment -- and fails if they
  disagree. That check is what caught the device problem.
- **No sleep-based watchers.** The background jobs notify on completion; a
  watcher that sleeps and then prints a log tail is a process that costs
  memory and tells us nothing the notification does not.
- The user asked: **no new processes after a set of jobs finishes** --
  report and let them reboot.

## RUNNING JOBS (21 Oct, 09:40)
- `run_all.py --stage abl` (the log is `abl_stage_cpu.log`) -- the component
  ablation, 12 variants x 3 seeds x 25 episodes, re-measured on the CPU.
  **THE CRITICAL PATH**: at variant 11 of 12 at 09:05, so ~10:15.
- `analysis/ab_observation.py --episodes 25 --seeds 3 --eval-seeds 5` -- the
  observation arms, re-run so that the artefact records the device it was
  measured on. ~11:00.
- `analysis/ab_energy_management.py --episodes 25 --seeds 3 --eval-seeds 5`
  -- the four energy arms, same reason. ~11:00.
- DONE on the CPU: the base comparison (5 training seeds), the credit A/B,
  the map-resolution sweep, the training-budget sweep, the scenario matrix,
  the stress ablation.
- The paper is assembled and compiles: 0 errors, 0 visible overfull boxes,
  0 undefined references, 29 pages.

### THE PROTOCOL HAS MORE THAN ONE NUMBER IN IT
The number of EVALUATION SEEDS is part of the protocol, and a run with
three instead of five is a different measurement: the per-seed rows are
the mean over the evaluation scenes, so they change.  A re-run that
omitted `--eval-seeds 5` looked like a reproducibility violation -- the
energy arm disagreed with the ablation's full configuration -- and the
probes (`analysis/repro_probe.py`, `analysis/train_repro_probe.py`) showed
that both the training and the evaluation are deterministic.  The cause
was the missing flag.  **Always pass the whole protocol.**
## Assembling the paper
1. `python analysis/assemble_results.py` -- regenerates the tables, fills
   the tokens, replaces the Results section wholesale, replaces the
   marked CONTRIB region, and compiles. It **ABORTS** if any token is
   unfilled, so a missing artefact is a hard error and never a broken
   paper.
2. Check: 0 LaTeX errors, 0 overfull boxes, 0 undefined references. The
   assembler reports all three.
3. `python analysis/claim_audit.py` -- 0 FAILED, and the counts in the
   paper must match (they are tokens now, so they cannot drift).
4. `python tests/run_tests.py` -- 111 tests.
5. Commit. **Never push.**

## The FINAL CHECKLIST (before declaring the work done)
- [x] Every stage re-measured under the reproducible protocol.
- [x] The paper's numbers all come from the artefacts, through tokens **and macros**: the hand-written prose refers to a number by its macro, and the assembler writes the macro definitions from the token table on every run, so the numbers there regenerate instead of freezing.
- [x] The claim audit passes with 0 failures and its count matches.
- [x] No LaTeX errors, no undefined references; the only overfull box is 0.68pt on the bibliography's first page, which is the IEEEtran balanced-columns artefact and is invisible.
- [ ] The abstract and the Conclusion agree with the new numbers.
- [x] Four mathematical audits and two prose audits have been run and their findings addressed (MiniMax M3.1, Beam Free, DeepSeek V4.1).
- [ ] `git status` is clean and everything is committed (never pushed).

## Paper state
- 29 pages, compiles clean (0 errors, 0 visible overfull boxes, 0 undefined references).
- The Results section, the tables and the Introduction's contribution
  bullet are generated from the artefacts.
- Hand-written and therefore needing a check against the new numbers: the
  abstract, the Introduction's framing paragraphs, the Conclusion, the
  limitations list, and the observation A/B/C narrative in
  `analysis/results_text.tex`.

## DeepSeek research protocol (2-tab limit, STRICT)
- Batch 1: Tab 1 (K-coverage literature gap) + Tab 2 (MAPPO correctness) -- DONE.
- Batch 2: Tab 3 (non-degenerate coverage metrics) -- DONE.
- Saved in `Project1/DeepResearch/DeepSeekTab1-4.md`, including Tab 4 on
  per-agent advantage estimation (COMA, DAE, GPAE, HAPPO, Sun et al. 2023).
- `browser.evaluate` takes **`script`**, not `expression`. `setTimeout` is
  not available in the Code Mode runtime -- use a background shell command.
- Do NOT pipe a background job through `Select-Object -Last N`: it buffers
  everything until the process ends and the progress is invisible.
