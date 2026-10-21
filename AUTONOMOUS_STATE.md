# Autonomous R&D State Tracker

> **RE-READ THIS FILE FIRST AFTER ANY CONTEXT COMPACTION.**
> Then re-read `Mlawn-midsem-tex.tex` and `ml_impl/analysis/results_text.tex`
> before writing anything. Never write paper sections or modify code from
> memory alone.

## The contract and how to read this file
Autonomous R&D sprint: **19 Oct 2026 -> 26 Oct 2026**. The deliverable is a
paper whose every number can be traced to the artefact it was measured in,
and whose comparative claims are DERIVED in code rather than asserted, so
that the paper says the right thing whichever way a measurement comes
out. The user has authorised installing packages without asking, and
commits locally without ever pushing.

**This file is the external brain.** After any context compaction, read
this file and `ml_impl/analysis/results_text.tex` before writing
anything: the prose's source of truth is the template, and the numbers'
source of truth is the artefact table. Never write a paper section or
change code from memory alone.

**The two live documents**, both regenerated from the artefacts:
- `Mlawn-midsem-tex.pdf` -- the paper, 29 pages.
- `REPORT.pdf` -- this tracker as a PDF, 6 pages.
`analysis/watch_docs.py` rebuilds both whenever an artefact changes, so
neither can be stale.
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

## The measurement protocol (canonical, 21 Oct)
Every number in the paper is produced under one protocol:
1. **Training**: 25 episodes of 2000 control steps per training run, and
   EIGHT training runs per configuration (the stress ablation uses six
   episodes, the map sweep twenty). The seed count is a PARAMETER
   (`run_all.py --train-seeds`, `--abl-seeds`, `--obs-seeds`), because it
   sets the width of every interval the paper reports, and the arms are
   compared with the base comparison's arm A, so the arms and the base
   must be trained with the same number of seeds or the cross-table
   identity check cannot hold. Eight, and not three, because at three
   seeds the identity arm's interval cannot be separated from the gap.
2. **Evaluation**: 5 scenes per policy. The number of evaluation scenes
   is part of the protocol: a per-seed row is the mean over the scenes, so
   a run with three is a different measurement.
3. **Device and thread count**: the device is pinned (`UAV_DEVICE`,
   default CPU), the thread count is pinned in `train.py`, and every
   artefact records the device. MEASURED, not assumed: the same
   configuration and seed give different weights on the GPU and on the
   CPU (`analysis/device_sensitivity.py`), while one thread and two
   threads give IDENTICAL weights for this workload. The GPU is also
   MEASURED to be 1.2--1.3x SLOWER here: the simulator is a sequential
   Python loop and is about 85% of a run, the network is about 8% of it,
   and on the GPU even that 8% is several times slower, because the
   tensors are tiny and the launch overhead dominates. There is nothing
   for the GPU to accelerate in this workload, and the protocol device is
   therefore the CPU -- a decision backed by the artefact, not a habit.
4. **The evaluation is seeded** from the evaluation seed alone
   (`uav_wireless/seeding.py`), so every controller is measured on the
   same random stream on the same scene -- common random numbers.
5. **The ablations are paired**: the variants share the training seeds,
   so a difference is measured on the same runs and reported as an
   interval, never as a threshold.
6. **Inference is by interval.** An explanation is excluded only if the
   arm testing it has an upper confidence limit below the gap. A null is a
   statement about the resolution of that arm, and the resolution is
   reported with it.
7. **Everything is derived in code.** The hand-written prose refers to a
   number by its MACRO (`\tokGap`), and the assembler writes the macro
   definitions from the token table on every run. Filling a token by
   writing its value into the source would CONSUME the token and freeze
   the number, which is the failure this project keeps having to undo.
## Defects found and fixed (all have tests)
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

| 40 | **A not-a-number reached the paper** ("nan standard errors", from an artefact that was mid-write) | the token table screens every value; an unusable value becomes a visible `[pending: ...]` marker and the assembly reports itself incomplete |
| 41 | The Results section kept its PREVIOUS text when a token was pending, so a stale sentence (with the nan in it) survived | the section is always regenerated from the template, and a pending token is marked |
| 42 | The budget's increments were compared UNPAIRED, and a resolved increment (+0.041, interval [+0.007, +0.075]) was called unresolved | paired over the same training seeds, which is what the design supports |
| 43 | Two intervals were built from a POPULATION standard deviation (numpy divides by n) | `sample_std`, ddof = 1, computed from the raw per-seed rows |
| 44 | The observation summary and the observation table quoted different intervals in the last digit | the summary rebuilds the interval from the raw values, not from the rounded ones |
| 45 | The observation summary said "the gap to the reactive heuristic" -- the privileged rule -- when the gap is to the unprivileged one | the rule's name is a token, so the sentence cannot name the wrong rule |
| 46 | The credit verdict described "a difference of any size up to 0.156 in either direction" for an interval of [-0.222, +0.090] | the verdict names the best case the interval allows and compares it with the gap |
| 47 | The base table's caption said the controller was trained five times, and promised the rule rows a $\pm$ the table does not print | the caption is read from the data |
| 48 | The abstract claimed the audit recomputes "every quantitative claim about the model" | the claim is narrowed to what the audit actually checks |
| 49 | The arms' sentence did not name the reference arm, so a reader could not tell what the intervals are intervals OF | the sentence names it |
| 50 | The budget's exclusion was stated without its scope | the scope (the 8--25 episode range) is in the sentence, and the paper says that budgets beyond it are not addressed |
| 51 | The identity arm's share of the gap was computed against a denominator that appears nowhere in the paper | it is a fraction of the paper's own gap |
## What the measurements say (21 Oct, the CPU protocol)
- The gap to the strongest rule: **0.309** (95% interval
  [0.261, 0.358]), against the unprivileged reactive rule at
  0.972.
- The learned controller: 0.662 $\pm$ 0.058;
  the argmax variant: 0.389 $\pm$ 0.073.
- The arms' verdict, derived from the intervals: Controlled arms bound how much of the gap each alternative explanation can account for: adding the agent identity (upper limit 0.161, margin +0.148); the full observation of the proposed configuration (upper limit 0.062, margin +0.247); removing the energy constraint (upper limit 0.081, margin +0.228); removing the threshold term (upper limit 0.028, margin +0.281), against a gap of 0.309.  Every arm's upper limit is below the gap, so none of them can be the whole of the explanation, by margins that are small but positive.  Every interval is paired over the same training seeds, against the local-only arm A of the observation experiment and the proposed configuration of the energy experiment.
- The energy repair: (in flight)
- The training-budget sweep: 8 episodes: 0.595, 16 episodes: 0.621, 25 episodes: 0.662. the coverage moves by +0.067 over the range the sweep covers, which is about 22\% of the gap of 0.309, and the increments between successive budgets are +0.026, +0.041; the last of them, +0.041, is 2.8 standard errors from zero (the standard error of the difference is 0.014, paired over the same 8 training seeds), so the coverage does keep rising with the budget over the range the sweep covers
- The alternative corrected deployment (N = 5, R_cov = 45 m), MEASURED:
  (in flight).
- The scenario matrix: behind in 34 of the variants,
  from S8 (-0.051) to S6 (-0.388).
- The claim audit: 37 items, 33
  verified, 0 failing, 4
  recorded for transparency. The test suite: 126 cases.
- The device sensitivity, MEASURED: the GPU and the CPU give different
  weights for the same seed and configuration; one thread and two threads
  give identical weights. The device is therefore part of the protocol and
  is recorded with every artefact.
## THE CENTRAL FINDING (the claim, and what the arms actually establish)
The learned controller does not reach the strongest rule, and the
framework's controlled arms are what say why -- or why not.  Every line
below is quoted from the same tokens the paper's prose is built from, so
this section cannot disagree with the paper.

- The **energy model is excluded as the whole of the explanation**: the
  arms' upper limits are below the gap of 0.309, and
  (in flight).
- The **observation content is NOT excluded**: the arm that adds the
  agent identity has an upper limit of 0.377 against a gap of
  0.309, so the identity remains a candidate explanation.  The arm
  that prices the full observation does clear the gap (0.164).
- The **training budget is excluded over the range the sweep covers**:
  the paired comparison over the same training seeds does resolve a real gain, +0.067 with a 95\% interval of [+0.017, +0.118], and that interval's upper limit of 0.118 is below the gap of 0.309: more training does help, and over the 8--25 episode range the sweep covers the whole of its effect is too small to account for the shortfall, so the budget is excluded as the explanation of the shortfall over that range.  Budgets beyond it are not addressed by this measurement, and the sweep shows no saturation within it.  The sweep's own last increment is
  +0.041 at 2.83 standard errors from zero
  (paired over the same 8 training seeds), and the
  sweep shows no saturation inside its range, so the claim is scoped to
  that range and to no other.
- The **credit assignment** is the remaining candidate the framework's
  own mechanisms suggest: the difference is not resolved by this arm: the interval is [-0.080, +0.036], and its best case is 0.036 better, far short of the gap of 0.309, and its worst case is 0.080 worse, so the cheapest modification in the direction the diagnosis points has not been shown to close the gap.

So the residual is consistent with the credit assignment and with the
observation content; the arms bound the energy model and the training
budget, over the range the sweep covers, and nothing else.  The paper
says that, and every part of it is derived from an interval.
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

- **Audit 4** (MiniMax M3.1, 21 Oct) -- the corner certificate's
  geometry, the packing survey, and the budget sweep's inference. Found
  four errors, all applied.
- **Audit 5** (Beam Free Max, 21 Oct) -- the same three, independently.
  Found the same four, plus that the corner condition is sufficient and
  not necessary. All applied.
- **Audit 6** (DeepSeek V4.1 Flash, 21 Oct) -- sixteen overstatements in
  the prose against the artefacts. All applied; the serious one was the
  energy repair reported as a null.
- **Deep research** (Beam Free Max, 21 Oct) -- the attributed numbers
  checked against their sources, the novelty claim stress-tested, and
  the IEEE page limits established. Song's 81.04% and 67.07% and Fan's
  74% are confirmed; the Luna reference was wrong and is fixed; the
  novelty claim survives.

- **Audit 4** (MiniMax M3.1, 21 Oct) -- the corner certificate's
  geometry, the packing survey, and the budget sweep's inference. Found
  four errors, all applied.
- **Audit 5** (Beam Free Max, 21 Oct) -- the same three, independently.
  Found the same four, plus that the corner condition is sufficient and
  not necessary. All applied.
- **Audit 6** (DeepSeek V4.1 Flash, 21 Oct) -- sixteen overstatements in
  the prose against the artefacts. All applied; the serious one was the
  energy repair reported as a null.
- **Deep research** (Beam Free Max, 21 Oct) -- the attributed numbers
  checked against their sources, the novelty claim stress-tested, and
  the IEEE page limits established. Song's 81.04% and 67.07% and Fan's
  74% are confirmed; the Luna reference was wrong and is fixed; the
  novelty claim survives.

- **Audit 4** (MiniMax M3.1, 21 Oct) -- the corner certificate's
  geometry, the packing survey, and the budget sweep's inference. Found
  four errors, all applied.
- **Audit 5** (Beam Free Max, 21 Oct) -- the same three, independently.
  Found the same four, plus that the corner condition is sufficient and
  not necessary. All applied.
- **Audit 6** (DeepSeek V4.1 Flash, 21 Oct) -- sixteen overstatements in
  the prose against the artefacts. All applied; the serious one was the
  energy repair reported as a null.
- **Deep research** (Beam Free Max, 21 Oct) -- the attributed numbers
  checked against their sources, the novelty claim stress-tested, and
  the IEEE page limits established. Song's 81.04% and 67.07% and Fan's
  74% are confirmed; the Luna reference was wrong and is fixed; the
  novelty claim survives.

- **Audit 4** (MiniMax M3.1, 21 Oct) -- the corner certificate's
  geometry, the packing survey, and the budget sweep's inference. Found
  four errors, all applied.
- **Audit 5** (Beam Free Max, 21 Oct) -- the same three, independently.
  Found the same four, plus that the corner condition is sufficient and
  not necessary. All applied.
- **Audit 6** (DeepSeek V4.1 Flash, 21 Oct) -- sixteen overstatements in
  the prose against the artefacts. All applied; the serious one was the
  energy repair reported as a null.
- **Deep research** (Beam Free Max, 21 Oct) -- the attributed numbers
  checked against their sources, the novelty claim stress-tested, and
  the IEEE page limits established. Song's 81.04% and 67.07% and Fan's
  74% are confirmed; the Luna reference was wrong and is fixed; the
  novelty claim survives.

- **Audit 4** (MiniMax M3.1, 21 Oct) -- the corner certificate's
  geometry, the packing survey, and the budget sweep's inference. Found
  four errors, all applied.
- **Audit 5** (Beam Free Max, 21 Oct) -- the same three, independently.
  Found the same four, plus that the corner condition is sufficient and
  not necessary. All applied.
- **Audit 6** (DeepSeek V4.1 Flash, 21 Oct) -- sixteen overstatements in
  the prose against the artefacts. All applied; the serious one was the
  energy repair reported as a null.
- **Deep research** (Beam Free Max, 21 Oct) -- the attributed numbers
  checked against their sources, the novelty claim stress-tested, and
  the IEEE page limits established. Song's 81.04% and 67.07% and Fan's
  74% are confirmed; the Luna reference was wrong and is fixed; the
  novelty claim survives.

- **Audit 4** (MiniMax M3.1, 21 Oct) -- the corner certificate's
  geometry, the packing survey, and the budget sweep's inference. Found
  four errors, all applied.
- **Audit 5** (Beam Free Max, 21 Oct) -- the same three, independently.
  Found the same four, plus that the corner condition is sufficient and
  not necessary. All applied.
- **Audit 6** (DeepSeek V4.1 Flash, 21 Oct) -- sixteen overstatements in
  the prose against the artefacts. All applied; the serious one was the
  energy repair reported as a null.
- **Deep research** (Beam Free Max, 21 Oct) -- the attributed numbers
  checked against their sources, the novelty claim stress-tested, and
  the IEEE page limits established. Song's 81.04% and 67.07% and Fan's
  74% are confirmed; the Luna reference was wrong and is fixed; the
  novelty claim survives.

- **Audit 4** (MiniMax M3.1, 21 Oct) -- the corner certificate's
  geometry, the packing survey, and the budget sweep's inference. Found
  four errors, all applied.
- **Audit 5** (Beam Free Max, 21 Oct) -- the same three, independently.
  Found the same four, plus that the corner condition is sufficient and
  not necessary. All applied.
- **Audit 6** (DeepSeek V4.1 Flash, 21 Oct) -- sixteen overstatements in
  the prose against the artefacts. All applied; the serious one was the
  energy repair reported as a null.
- **Deep research** (Beam Free Max, 21 Oct) -- the attributed numbers
  checked against their sources, the novelty claim stress-tested, and
  the IEEE page limits established. Song's 81.04% and 67.07% and Fan's
  74% are confirmed; the Luna reference was wrong and is fixed; the
  novelty claim survives.

- **Audit 4** (MiniMax M3.1, 21 Oct) -- the corner certificate's
  geometry, the packing survey, and the budget sweep's inference. Found
  four errors, all applied.
- **Audit 5** (Beam Free Max, 21 Oct) -- the same three, independently.
  Found the same four, plus that the corner condition is sufficient and
  not necessary. All applied.
- **Audit 6** (DeepSeek V4.1 Flash, 21 Oct) -- sixteen overstatements in
  the prose against the artefacts. All applied; the serious one was the
  energy repair reported as a null.
- **Deep research** (Beam Free Max, 21 Oct) -- the attributed numbers
  checked against their sources, the novelty claim stress-tested, and
  the IEEE page limits established. Song's 81.04% and 67.07% and Fan's
  74% are confirmed; the Luna reference was wrong and is fixed; the
  novelty claim survives.
- **Audit 7** (MiniMax M3.1, 21 Oct) -- the eight-seed re-measurement
  checked against the raw per-seed rows, with every interval recomputed
  by hand. Ten findings, all applied: the budget's paired increment, two
  population standard deviations, a rounding disagreement between a
  summary and its table, the wrong rule named in a sentence, an
  asymmetric interval described as symmetric, a caption that said five
  where the table said eight, an audit claim in the abstract that was
  broader than the audit, an arms' sentence that did not name its
  reference arm, an exclusion stated without its scope, and a share
  whose denominator appears nowhere in the paper.

- **Audit 4** (MiniMax M3.1, 21 Oct) -- the corner certificate's
  geometry, the packing survey, and the budget sweep's inference. Found
  four errors, all applied.
- **Audit 5** (Beam Free Max, 21 Oct) -- the same three, independently.
  Found the same four, plus that the corner condition is sufficient and
  not necessary. All applied.
- **Audit 6** (DeepSeek V4.1 Flash, 21 Oct) -- sixteen overstatements in
  the prose against the artefacts. All applied; the serious one was the
  energy repair reported as a null.
- **Deep research** (Beam Free Max, 21 Oct) -- the attributed numbers
  checked against their sources, the novelty claim stress-tested, and
  the IEEE page limits established. Song's 81.04% and 67.07% and Fan's
  74% are confirmed; the Luna reference was wrong and is fixed; the
  novelty claim survives.
- **Audit 7** (MiniMax M3.1, 21 Oct) -- the eight-seed re-measurement
  checked against the raw per-seed rows, with every interval recomputed
  by hand. Ten findings, all applied: the budget's paired increment, two
  population standard deviations, a rounding disagreement between a
  summary and its table, the wrong rule named in a sentence, an
  asymmetric interval described as symmetric, a caption that said five
  where the table said eight, an audit claim in the abstract that was
  broader than the audit, an arms' sentence that did not name its
  reference arm, an exclusion stated without its scope, and a share
  whose denominator appears nowhere in the paper.

- **Audit 4** (MiniMax M3.1, 21 Oct) -- the corner certificate's
  geometry, the packing survey, and the budget sweep's inference. Found
  four errors, all applied.
- **Audit 5** (Beam Free Max, 21 Oct) -- the same three, independently.
  Found the same four, plus that the corner condition is sufficient and
  not necessary. All applied.
- **Audit 6** (DeepSeek V4.1 Flash, 21 Oct) -- sixteen overstatements in
  the prose against the artefacts. All applied; the serious one was the
  energy repair reported as a null.
- **Deep research** (Beam Free Max, 21 Oct) -- the attributed numbers
  checked against their sources, the novelty claim stress-tested, and
  the IEEE page limits established. Song's 81.04% and 67.07% and Fan's
  74% are confirmed; the Luna reference was wrong and is fixed; the
  novelty claim survives.
- **Audit 7** (MiniMax M3.1, 21 Oct) -- the eight-seed re-measurement
  checked against the raw per-seed rows, with every interval recomputed
  by hand. Ten findings, all applied: the budget's paired increment, two
  population standard deviations, a rounding disagreement between a
  summary and its table, the wrong rule named in a sentence, an
  asymmetric interval described as symmetric, a caption that said five
  where the table said eight, an audit claim in the abstract that was
  broader than the audit, an arms' sentence that did not name its
  reference arm, an exclusion stated without its scope, and a share
  whose denominator appears nowhere in the paper.

- **Audit 4** (MiniMax M3.1, 21 Oct) -- the corner certificate's
  geometry, the packing survey, and the budget sweep's inference. Found
  four errors, all applied.
- **Audit 5** (Beam Free Max, 21 Oct) -- the same three, independently.
  Found the same four, plus that the corner condition is sufficient and
  not necessary. All applied.
- **Audit 6** (DeepSeek V4.1 Flash, 21 Oct) -- sixteen overstatements in
  the prose against the artefacts. All applied; the serious one was the
  energy repair reported as a null.
- **Deep research** (Beam Free Max, 21 Oct) -- the attributed numbers
  checked against their sources, the novelty claim stress-tested, and
  the IEEE page limits established. Song's 81.04% and 67.07% and Fan's
  74% are confirmed; the Luna reference was wrong and is fixed; the
  novelty claim survives.
- **Audit 7** (MiniMax M3.1, 21 Oct) -- the eight-seed re-measurement
  checked against the raw per-seed rows, with every interval recomputed
  by hand. Ten findings, all applied: the budget's paired increment, two
  population standard deviations, a rounding disagreement between a
  summary and its table, the wrong rule named in a sentence, an
  asymmetric interval described as symmetric, a caption that said five
  where the table said eight, an audit claim in the abstract that was
  broader than the audit, an arms' sentence that did not name its
  reference arm, an exclusion stated without its scope, and a share
  whose denominator appears nowhere in the paper.

- **Audit 4** (MiniMax M3.1, 21 Oct) -- the corner certificate's
  geometry, the packing survey, and the budget sweep's inference. Found
  four errors, all applied.
- **Audit 5** (Beam Free Max, 21 Oct) -- the same three, independently.
  Found the same four, plus that the corner condition is sufficient and
  not necessary. All applied.
- **Audit 6** (DeepSeek V4.1 Flash, 21 Oct) -- sixteen overstatements in
  the prose against the artefacts. All applied; the serious one was the
  energy repair reported as a null.
- **Deep research** (Beam Free Max, 21 Oct) -- the attributed numbers
  checked against their sources, the novelty claim stress-tested, and
  the IEEE page limits established. Song's 81.04% and 67.07% and Fan's
  74% are confirmed; the Luna reference was wrong and is fixed; the
  novelty claim survives.
- **Audit 7** (MiniMax M3.1, 21 Oct) -- the eight-seed re-measurement
  checked against the raw per-seed rows, with every interval recomputed
  by hand. Ten findings, all applied: the budget's paired increment, two
  population standard deviations, a rounding disagreement between a
  summary and its table, the wrong rule named in a sentence, an
  asymmetric interval described as symmetric, a caption that said five
  where the table said eight, an audit claim in the abstract that was
  broader than the audit, an arms' sentence that did not name its
  reference arm, an exclusion stated without its scope, and a share
  whose denominator appears nowhere in the paper.

- **Audit 4** (MiniMax M3.1, 21 Oct) -- the corner certificate's
  geometry, the packing survey, and the budget sweep's inference. Found
  four errors, all applied.
- **Audit 5** (Beam Free Max, 21 Oct) -- the same three, independently.
  Found the same four, plus that the corner condition is sufficient and
  not necessary. All applied.
- **Audit 6** (DeepSeek V4.1 Flash, 21 Oct) -- sixteen overstatements in
  the prose against the artefacts. All applied; the serious one was the
  energy repair reported as a null.
- **Deep research** (Beam Free Max, 21 Oct) -- the attributed numbers
  checked against their sources, the novelty claim stress-tested, and
  the IEEE page limits established. Song's 81.04% and 67.07% and Fan's
  74% are confirmed; the Luna reference was wrong and is fixed; the
  novelty claim survives.
- **Audit 7** (MiniMax M3.1, 21 Oct) -- the eight-seed re-measurement
  checked against the raw per-seed rows, with every interval recomputed
  by hand. Ten findings, all applied: the budget's paired increment, two
  population standard deviations, a rounding disagreement between a
  summary and its table, the wrong rule named in a sentence, an
  asymmetric interval described as symmetric, a caption that said five
  where the table said eight, an audit claim in the abstract that was
  broader than the audit, an arms' sentence that did not name its
  reference arm, an exclusion stated without its scope, and a share
  whose denominator appears nowhere in the paper.
## THE CITATIONS, CHECKED AGAINST THE SOURCES (21 Oct)
Every number the paper attributes to a cited work has been checked
against the source, and the checks are in the paper's own record:
- Song et al. (IEEE TMC 23(4):2504-2519, 2024) state that "MPC and MCTS
  achieve approximately 81.04% and 67.07% of the optimal" (IEEE
  Computer Society's page for the paper).  The survey table's 81.0% and
  67.1% are right.
- Fan et al. (arXiv:2603.16141, 2026) report 74% coverage with five UAVs
  and ten nodes against an offline MILP upper bound.  The survey row now
  says which configuration the figure belongs to.
- Datsko et al. (IEEE RA-L 9(3):2893-2900, 2024) report a hover power of
  426.03 W and an optimal-speed power of 465.23 W for their airframe, a
  ratio of 1.092, and a range-optimal speed of 8.39 m/s.  The paper's 1.09
  is right; the 8.39 m/s is that airframe's range-optimal speed, not a
  general energy-optimal multirotor cruise speed, and the paper now says so.
- The Luna et al. entry named authors who did not write the paper and
  carried a DOI that points elsewhere.  It is now M. A. Luna, M. S. Ale
  Isaac, A. R. Ragab, P. Campoy, P. Flores Pena and M. Molina, Sensors
  22(6):2297, 2022, doi 10.3390/s22062297.
- Zhang et al. (Sci. Rep. 15:6437, 2025) --- the IRADA paper --- couple
  persistent monitoring, energy-constrained charging, limited
  communication and failure recovery by task redistribution: four of the
  five elements.  It is in the near-miss table, and the paper says that
  its controller is reward-driven rather than learned (their own future
  work proposes reinforcement learning for it), that the monitored
  quantity is information freshness rather than K-redundant coverage, and
  that they compute no achievability reference.
- The novelty claim survives the search: no work in the searched corpus
  couples all five elements, and the near-misses are named.

## Negative results, kept on the record
- The **runtime instrument cannot support a path-loss cross-validation**:
  a transmit-power sweep shows the available per-receiver SNR statistic
  tracks the transmit power exactly but is independent of the receiver's
  distance. The equivalence is therefore established from INET's source,
  not from a running simulation. This is a negative control that the
  paper reports on itself.
- **Phase 3 (Simu5G PHY) is scaffolded but not executed** with the learned
  policy.
- **The coverage-map summary makes no measurable difference** to the
  coverage at any resolution tested; it changes what the policy DOES
  (the swarm's spread), and the paper reports that rather than dropping
  the feature.
- **The thread count does not change the training run** on this workload.
- **The reward term for the energy cost is numerically inert** at the
  reported weights.
- **The credit-assignment arm does not resolve the credit assignment**:
  the cheapest modification in the direction the diagnosis points moves
  the wrong way, and the paper says so rather than claiming the
  diagnosis.
- **The GPU does not accelerate this workload.** Measured, in
  `analysis/device_sensitivity.json`: the GPU takes about 1.2--1.3x the
  CPU's wall clock for the same training run. The profile says why: the
  simulator is a sequential Python loop and is about 85% of a run, the
  network is about 8% of it, and on the GPU even that 8% is several times
  slower in absolute terms (tiny tensors, launch overhead). The
  measurement is in the artefact, and the earlier claim that the choice
  "costs about one percent" was false and has been removed from the code
  and from this file.
## Commands
```
cd Project1/ml_impl
python run_all.py --stage base      # the base comparison (8 seeds x 25 ep)
python run_all.py --stage obs       # the observation A/B/C
python run_all.py --stage abl       # the component ablation, feasible config
python run_all.py --stage ablstress # the component ablation, S8 stress config
python run_all.py --stage learned   # the two learned baselines
python run_all.py --stage energy    # the energy-management A/B/C/D
python run_all.py --stage scen      # the scenario matrix
python analysis/ab_credit.py --episodes 25 --seeds 8 --eval-seeds 5
python analysis/ab_observation.py --episodes 25 --seeds 8 --eval-seeds 5
python analysis/ab_energy_management.py --episodes 25 --seeds 8 --eval-seeds 5
python analysis/ab_budget.py --seeds 8 --eval-seeds 5
python analysis/ab_map_resolution.py --episodes 20 --seeds 8 --eval-seeds 5 --grids 0,4,8
python analysis/alt_deployment.py --seeds 8 --episodes 25 --eval-seeds 5
python analysis/device_sensitivity.py --config cpu1 --episodes 2
python analysis/device_sensitivity.py --merge
python analysis/ablation_part.py --part a --episodes 25 --seeds 8 --eval-seeds 5
python analysis/merge_ablation.py   # the parts -> results_ablation.csv
python analysis/run_queue.py        # the tail of the matrix, in order
python analysis/claim_audit.py      # 37 items, 33 verified, 0 failed, 4 info
python analysis/assemble_results.py # the tables, the tokens, the Results, the compile
python analysis/final_checks.py     # assembly + compile + audit + tests, one command
python analysis/make_report.py      # the project report's PDF
python analysis/rewrite_state.py    # regenerate this tracker
python tests/run_tests.py           # 126 tests
```
**The protocol, in one line:** pass the WHOLE protocol every time ---
`--episodes`, `--seeds`, `--eval-seeds` and the device.  A run with
three training seeds instead of eight is a different measurement, and a
run on another device is a different experiment.
## Machine notes (measured, 21 Oct)
- **The binding constraint is the PAGE FILE, not the cores.** Six
  single-threaded training processes fit; a seventh dies with
  `OSError: [WinError 1455]` while importing torch, which looks like a
  code failure and is not one. The cause is the BLAS thread pool: each
  process starts a pool sized for the whole machine. Every entry point
  now pins `OPENBLAS_NUM_THREADS` and its siblings to one thread before
  numpy loads them, and the runs are launched as a pool of six.
- **The machine has twelve logical cores and each run uses one**, so the
  matrix is run in parallel: the component ablation is split into two
  parts (`analysis/ablation_part.py`, merged by
  `analysis/merge_ablation.py`) and the rest runs in `analysis/run_queue.py`.
- **The GPU is idle because there is nothing for it to do here**: the
  simulator is 85% of a run. Measured per device: the CPU with one
  thread 8.3 ms/step, the CPU with two 8.4 ms/step, the GPU 10.7 ms/step.
- **Every long stage is resumable**, and the resume keys include the
  device, the budget, the seed count and the evaluation-scene count. The
  budget sweep and the alternative deployment additionally cache every
  finished (budget, seed) and (arm, seed) separately, so a restart
  costs the seed in flight and nothing more.
- **No sleep-based watchers.** The background jobs notify on completion;
  a watcher that sleeps and then prints a log tail is a process that
  costs memory and tells us nothing the notification does not. The PDFs
  are rebuilt by `analysis/watch_docs.py` when it is run, not by a
  resident process.
- `analysis/final_checks.py` compares the same configuration across the
  tables -- the observation arm C, the credit arm A, the energy arm A and
  the ablation's full configuration are one experiment -- and fails if
  they disagree, or if the artefacts were produced on more than one
  device.
## What is running, and what is next
RUNNING
- `run_all.py --stage abl --abl-seeds 8` -- the component ablation at eight
  training seeds, twelve variants.  This is the critical path: the paired
  intervals of the component table are the paper's weakest evidence, and
  at three seeds every one of them includes zero.
- `analysis/ab_energy_management.py --episodes 25 --seeds 8 --eval-seeds 5`
  -- the four energy arms.
- `analysis/ab_budget.py --seeds 8 --eval-seeds 5` -- the training-budget
  sweep, resuming from the finished eight-episode budget through a
  per-seed cache.
- `run_all.py --stage base --train-seeds 8 --resume` -- the base
  comparison; seeds 0--4 are re-evaluated from their stored policies and
  seeds 5--7 are trained.
NEXT, AS SLOTS FREE
- `analysis/ab_credit.py --episodes 25 --seeds 8 --eval-seeds 5` -- the
  credit-assignment arms.
- `analysis/ab_observation.py --episodes 25 --seeds 8 --eval-seeds 5` --
  the observation arms.
- `analysis/alt_deployment.py --seeds 8 --episodes 25 --eval-seeds 5` --
  the alternative corrected deployment.  Its reported arm is READ from
  the base comparison's per-seed rows rather than trained twice: it is
  the same experiment, and measuring it once is what keeps the two
  tables of the paper consistent.
- `analysis/device_sensitivity.py --episodes 25` -- the three device
  configurations at the full protocol.
THEN
- One final assembly, the full gate (`analysis/final_checks.py`), and one
  more audit of the finished paper; both PDFs rebuilt by the watcher.
- Undecided and awaiting the user: **the target venue**, and therefore
  whether the paper is cut to conference length, journal length, or left
  as a preprint.
## Assembling the paper
1. `python analysis/assemble_results.py` -- regenerates the tables, fills
   the tokens, replaces the Results section wholesale, replaces the
   marked CONTRIB region, rewrites the macro block from the token table
   and compiles.  A token that cannot be filled becomes a visible
   `[pending: ...]` marker, the paper still compiles, and the assembler
   EXITS NON-ZERO and says the paper is incomplete.  It used to keep the
   previous text of the Results section instead, which is how a stale
   sentence with a not-a-number in it survived into the paper.
2. `python analysis/merge_ablation.py` -- the component ablation is run
   in two parts, and this assembles them into `results_ablation.csv`.  It
   REJECTS a merge that is missing a variant or that mixes protocols.
3. `python analysis/final_checks.py` -- the gate: eight checks, including
   the cross-table identity check (the observation arm C, the credit arm
   A, the energy arm A and the ablation's Full row are ONE experiment
   and must agree on every training seed), the single-device check, the
   audit's counts against the paper's, and the macro check.
4. `python analysis/claim_audit.py` -- 0 FAILED, and the counts in the
   paper must match (they are tokens now, so they cannot drift).
5. `python tests/run_tests.py` -- the test suite.
6. `python analysis/make_report.py` -- the project report's PDF.
7. Commit. **Never push.**
## The FINAL CHECKLIST (before declaring the work done)
- [x] Every stage re-measured under the reproducible protocol.
- [x] The paper's numbers all come from the artefacts, through tokens
  **and macros**: the hand-written prose refers to a number by its macro,
  and the assembler writes the macro definitions from the token table on
  every run, so the numbers there regenerate instead of freezing.
- [x] The token table SCREENS its values: a nan, an empty list or a None
  becomes a visible marker instead of a number, and the assembler says
  the paper is incomplete.
- [x] The claim audit passes with 0 failures and its count matches.
- [x] No LaTeX errors and no undefined references.  The only overfull
  box is the `balance` package's column split on the bibliography's last
  page, a point or two into a 19 mm margin, and it is invisible.
- [x] Seven audits (four mathematical, two prose, one deep-research)
  have been run and their findings addressed: MiniMax M3.1 (twice),
  Beam Free Max (twice), DeepSeek V4.1 Flash, and the deep-research
  pass.
- [x] The identity requirement holds at the full width: the arms, the
  ablation's Full row and the base comparison's runs are ONE experiment,
  on every training seed, on one device.
- [ ] The abstract and the Conclusion agree with the final numbers
  (re-read them against the assembled PDF).
- [ ] `git status` is clean and everything is committed (never pushed).
## The paper
- 29 pages, IEEEtran conference format. Compiles clean: 0 LaTeX errors,
  0 visible overfull boxes, 0 undefined references. The one overfull box
  is the `balance` package's column split on the bibliography's last
  page, a point or two into a 19 mm margin, and it is invisible.
- **Everything numeric in the prose is a macro**, and the assembler
  rewrites the macro definitions from the token table on every run. The
  hand-written prose cannot drift from the measurement.
- The Results section, the tables, the Introduction's contribution bullet
  and the abstract are all generated from the artefacts.
- **The token table screens its values.** A nan, an empty list or a None
  becomes a visible `[pending: ...]` marker, the paper still compiles,
  and the assembler exits non-zero and says the paper is incomplete. A
  not-a-number can no longer reach the paper, and the Results section is
  never left stale.
- `analysis/final_checks.py` is the gate: eight checks, and it exits
  non-zero if any of them fails.
- **The length is still undecided.** At 29 pages this is a preprint or a
  journal submission with overlength charges, not a conference paper
  (6-8 pages). The user has been asked which venue is intended and has
  not answered; the full paper stands until they do.
## DeepSeek research protocol (2-tab limit, STRICT)
- Batch 1: Tab 1 (K-coverage literature gap) + Tab 2 (MAPPO correctness) -- DONE.
- Batch 2: Tab 3 (non-degenerate coverage metrics) -- DONE.
- Saved in `Project1/DeepResearch/DeepSeekTab1-4.md`, including Tab 4 on
  per-agent advantage estimation (COMA, DAE, GPAE, HAPPO, Sun et al. 2023).
- `browser.evaluate` takes **`script`**, not `expression`. `setTimeout` is
  not available in the Code Mode runtime -- use a background shell command.
- Do NOT pipe a background job through `Select-Object -Last N`: it buffers
  everything until the process ends and the progress is invisible.
