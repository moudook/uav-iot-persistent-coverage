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

## THE MEASUREMENT PROTOCOL (canonical, 20 Oct, 22:00)
This is the protocol every number in the paper is produced under.

1. **Training**: 25 episodes x 2000 steps per training run. The base
   comparison trains **5** runs (seeds 0-4); the component ablation and the
   observation A/B/C train **3** runs (seeds 0-2); the learned baselines
   train 3 runs; the energy and credit arms train 1-2 runs; the scenario
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

`tests/mutation_check.py` proves the suite catches the historical bugs.

## The numbers (BEING RE-MEASURED under the protocol above, 20 Oct 22:00)
The last complete set, measured **before** defect 28 was fixed, is in git
history at `dbc68f7` and is **NOT** quotable, because the evaluation was an
uncontrolled draw. What it said, and what the re-measurement is testing:

| Controller | CK | AG | SC | CovDef |
|---|---|---|---|---|
| Fixed formation | 0.372 | 1.000 | 0.000 | 0.628 |
| Greedy recharge | 0.786 | 0.964 | 0.066 | 0.214 |
| **Reactive heuristic** | **0.953** | 1.000 | **0.751** | 0.047 |
| Independent DQN | 0.396 | 0.990 | 0.000 | 0.604 |
| Masked PPO, local critic | 0.649 | 0.983 | 0.001 | 0.351 |
| **MAPPO (proposed)** | **0.734** | 0.968 | 0.031 | 0.266 |
| MAPPO (argmax) | 0.426 | 0.965 | 0.000 | 0.574 |
| Oracle (ceiling) | 1.000 | | | |

The **rule baselines and the oracle are unaffected by defect 28** (they are
deterministic), so their rows above stand. The learned rows are being
re-measured and will move by the size of the uncontrolled term, which is
why they are not quotable until the re-measurement lands.

**The energy arms** (four controlled arms, one difference each) said the
energy model is **not** what limits the controller: A 0.701, B (a pack that
cannot run out) 0.722, C (no threshold term) 0.739, D (the previous energy
rule) 0.716 -- all inside the learner's seed spread. What the previous rule
did was strand 7.4 of the 8 UAVs per episode against 1.0 for the corrected
one: a real defect in the safety filter, whose repair changed the coverage
by 0.015, not by 0.1. **Being re-measured.**

**The scenario matrix** (34 variants) showed the learned controller *ahead*
in the pre-deployed regime (0.874 against 0.817) and level under combined
stress (0.567 against 0.572). **Being re-measured.**

## THE CENTRAL FINDING (the claim, not yet the final numbers)
The learned controller does not reach the reactive heuristic, and the
framework's controlled arms are what identify why. The candidate
explanations are the content of the observation, the energy model, and the
credit assignment of a shared team reward.
- The **energy model is rejected** by the four controlled arms.
- The **observation content is not the binding factor**: the A/B/C arms do
  not separate, and the component ablation prices the observation terms
  separately. The observation terms are what make the controller work at
  all, not what stops it working.
- The **credit assignment** is what remains, and the cheapest remedy (a
  per-agent local critic) does not close the gap.

**Watch this**: the old energy prose claimed the corrected filter rule
raised the coverage from 0.638 to 0.734. That comparison was **not
controlled** -- the two runs differed in more than the rule. The controlled
arms say the difference is 0.015. The prose now quotes the controlled arms.

## The mathematical audit cadence (standing instruction, 20 Oct)
- **Audit 1** (done): the seven load-bearing claims. Found 4 wrong as
  stated; all corrected.
- **Audit 2** (done): the reward terms, the mask and the joint projection,
  the H-step lookahead, the energy budget, the value normalisation, the
  metrics, the oracle normalisation, the evaluation protocol. 25 items,
  21 verified, 0 failed, 4 informational.
- **Audit 3** (NEXT, after the re-measurement lands): the assembled
  Results section and the Conclusion. The brief is drafted at
  `C:\Users\gbust\AppData\Local\Temp\opencode\audit3_brief.txt` -- 8 items:
  protocol fairness, the metric-is-the-objective circularity, the mask's
  soundness for simultaneous moves, the H-hop rule's semantics, a
  constrained upper bound, the internal consistency of CK and SC, the
  seed-variance weighting, and which claimed contributions the measurements
  actually support.
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
python tests/run_tests.py           # 111 tests
```

## Machine notes
- Two GPU processes together exhaust host memory and make CUDA allocation
  fail: **run one GPU job at a time**. The GPU is within noise of the CPU
  at this scale (11.1 vs 11.2 ms/step), so CPU-only jobs are preferred:
  set `CUDA_VISIBLE_DEVICES=""` and `OMP_NUM_THREADS=3`.
- Four concurrent CPU jobs of ~1.3 GB each fit in the 15.7 GB of RAM.
- A background job writes its artefact on completion, and the ablation now
  writes each ROW as it finishes, so an interrupted run is re-run rather
  than lost.
- The user asked: **no new processes after a set of jobs finishes** --
  report and let them reboot.

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
- [ ] Every stage re-measured under the reproducible protocol.
- [ ] The paper's numbers all come from the artefacts, through tokens.
- [ ] The claim audit passes with 0 failures and its count matches.
- [ ] No LaTeX errors, no overfull boxes, no undefined references.
- [ ] The abstract and the Conclusion agree with the new numbers.
- [ ] The third mathematical audit has been run and its findings addressed.
- [ ] `git status` is clean and everything is committed (never pushed).

## Paper state
- 24 pages, compiles clean (0 errors, 0 overfull, 0 undefined refs).
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
