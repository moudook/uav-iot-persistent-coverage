# MASTER PROMPT v3 — UAV-IoT Persistent K-Coverage: Research Sprint to a Publishable Paper

## 0. FIRST ACTIONS (do these before anything else, and again after every compaction)
1. Run `date`. Save this whole prompt verbatim to `docs/MASTER_PROMPT.md` and git-commit it (only on the first run).
2. After every compaction or new session, read in this order: `docs/MASTER_PROMPT.md` → `STATE.md` → `docs/CLAIMS.md` → the last 50 lines of `docs/LOG.md`. Then continue from the top item of the BACKLOG in STATE.md.
3. Check what is running in the background: `tmux ls`, `nvidia-smi`, the tail of each `runs/*/log.txt`.

## 1. DEADLINE — NON-NEGOTIABLE
- Sprint window: 2026-10-24 until **2026-11-07 23:59 local time**.
- You MUST NOT stop, declare completion, or wait for user input before that time. There are no exceptions: "the paper is done", "waiting for a run" and "nothing left to do" are not valid reasons.
- If you believe you are done, you are wrong. Pull the next BACKLOG item. If the BACKLOG has fewer than 10 items, refill it from section 12.
- Only the user can end the sprint early.

## 2. FIXED vs CHANGEABLE
FIXED — the problem statement. These never change:
- N active UAVs plus 1 reserve UAV and M fixed IoT sensors.
- Persistent K-coverage, and a connected inter-UAV graph that relays data to a sink.
- Finite batteries, limited charging pads with contention, and UAV failures with recovery.
- Decentralized execution, with multi-agent RL as the core method.
- OMNeT++ (with INET) is COMPULSORY and must be load-bearing (section 5).

CHANGEABLE: algorithms, reward, observations, architecture, training pipeline, simulator code, evaluation regimes, paper framing, title and structure.

## 3. WHY THE MIDSEM REPORT IS NOT PUBLISHABLE (accept this; do not argue with it)
1. **Undertrained learner.** MAPPO trained for 25 episodes × 2000 steps ≈ 5×10⁴ env steps per seed. Its own budget sweep (0.588 → 0.624 → 0.674) was still rising. Every arm that "rules out" an explanation used the same tiny budget. Therefore these are all UNSUPPORTED and are retracted until re-measured at a converged budget:
   - the 0.298 gap,
   - "none of the arms explains it",
   - the credit-assignment diagnosis.
   For scale, POGS-QMIX (Drones, 2026; https://www.mdpi.com/2504-446X/10/9/688) used 150k steps per method, and typical MAPPO results use millions.
2. **No headroom.** The privileged rule reaches 0.972 against a ceiling of 1.000, so learning cannot show any value in that regime.
3. **OMNeT++ was decorative.** It was only used to check path-loss algebra. No policy was ever executed inside it.
4. **The novelty claims are already taken.** Do not reuse any of these as "new":
   - Difference/WLU rewards for persistent UAV coverage: Sun et al. 2023, https://www.sciencedirect.com/science/article/abs/pii/S0925231222014862
   - Communication-aware RL training under delay and loss: CALF 2026, https://arxiv.org/abs/2603.12543
   - Failure-resilient graph MAPPO for UAV coverage: TAG-MAPPO 2026, https://arxiv.org/html/2602.10029v2
   - Energy-aware persistent coverage MARL with a return-energy mask and a greedy-controller ablation: POGS-QMIX 2026 (link above)
   - Connectivity-preserving coverage PPO: https://arxiv.org/html/2605.17999v1
   - Joint coverage, connectivity and charging: Trotta et al., IEEE T-RO 2018
   - The packing-number feasibility bound is a one-liner. Oracle ceilings and graded metrics have precedent.
5. **Logic error.** "SC(π)=0 ∀π ⟺ F=∅" is false. Only F=∅ ⇒ SC≡0 holds.
6. **Unreadable writing.** 11 contributions, hedging in every sentence, a self-referential abstract, process narration.
7. **Unfair comparison.** The rule was possibly designed on the evaluation scenes. Hyperparameters and wall-clock time were not reported, and no information-access table was given.

Treat every external review point as TRUE until refuted by an experiment or an exact quotation. "It is mentioned somewhere in the paper" is not the same as "it is handled".

## 4. RESEARCH THESIS (default spine — verify it with the novelty gate in section 6)
**Working title:** *"The Swarm Is Its Own Network: Network-in-the-Loop MARL for Persistent Fault-Tolerant K-Coverage in UAV-IoT"*

**Core idea.** In a decentralized UAV swarm, each UAV's view of its neighbours and of the coverage-deficit map arrives over the multi-hop 802.11 network that the swarm itself forms. Movement decisions change the topology, which changes packet delivery and information age, which changes the quality of future decisions. This self-referential coupling of control and information is ignored by:
- abstract-disc MARL,
- generic delay/loss models (CALF), and
- fixed-topology co-simulation.

Every competitor in section 3.4 assumes perfect or i.i.d.-degraded information.

**Contributions (at most 4 in the final paper):**
- **C1 — Network-in-the-loop evaluation.** An OMNeT++/INET co-simulation in which policies act only on information that actually arrived through simulated 802.11 ad hoc links over the current UAV topology. Measure sensor→sink delivery (PDR, end-to-end delay) over the swarm graph as a first-class metric next to K-coverage.
- **C2 — Topology-conditioned information model plus training.** Fit an "information channel" from INET runs. It gives delivery probability and age distribution as a function of distance, hop count, neighbour count/load and the topology state. Train policies under it (fast, in Python) and compare with policies trained under ideal information and under i.i.d. loss (a CALF-style baseline). Hypothesis H2: policies trained with topology-conditioned information keep K-coverage and connectivity better in closed-loop OMNeT++ than both baselines, because they learn to protect the links that carry their own information.
- **C3 — Redundancy- and criticality-aware credit.** Per-agent counterfactual signals in closed form:
  - K-coverage marginal: (1/(KM))·|{d : i covers d, n_d ≤ K}|.
  - Connectivity criticality: the change in the number of connected components / articulation status when i is removed (union-find, cheap).
  - Delivery criticality: the change in sensor→sink reachable fraction when i is removed.

  Distinguish it explicitly from Sun 2023's WLU (age-based, 1-coverage, no connectivity). The objective min(n_d/K,1) is monotone submodular, so connect to submodular-MARL theory (https://arxiv.org/abs/2603.06810) and prove a short alignment/variance lemma. C3 is a supporting contribution, not the headline.
- **C4 — Fair, falsifiable evaluation.** Converged training, tuned baselines including strong rules, a headroom gate, and a coverage achievability ceiling (the oracle — call it exactly that), all with rliable statistics.

**Safety-net method (always implement it): residual / rule-anchored MAPPO.** A rule prior (behaviour cloning initialization or KL-to-rule regularization, annealed) plus PPO fine-tuning. This means the learned controller should never be worse than the rule, so any gain is attributable to learning. Report it as one method among others.

## 5. MAKING OMNeT++ LOAD-BEARING (step by step; each step is time-boxed)
- **Install:** use opp_env (the officially recommended route). Install OMNeT++ 6.4 + INET 4.7, or, if build problems take more than 3 hours, OMNeT++ 6.2/6.3 + INET 4.6. Record versions in `docs/ENV.md`. When you are stuck, use the AI docs at https://ai.omnetpp.org and https://ai-inet.omnetpp.org.
- **Step A (≤1.5 days) — trajectory replay.**
  - Export Python-simulator trajectories as BonnMotion traces (INET's BonnMotionMobility) or as a per-node waypoint file.
  - INET scenario: N+1 UAV hosts plus M sensor hosts plus 1 sink, Ieee80211 ad hoc, and routing (AODV or static shortest path recomputed per step; justify the choice).
  - Traffic: periodic neighbour beacons (position, battery, mode, local deficit), sensor data to the sink, and the deficit-map broadcast.
  - Use ScenarioManager for UAV crash/shutdown at failure times.
  - Measure: per-link beacon delivery, information age, sensor→sink PDR and delay.
- **Step B (≤1 day) — fit the information-channel model** (lookup tables or a small GLM). Validate it on held-out INET runs. Plot predicted vs. simulated delivery and age.
- **Step C (≤3 days) — closed-loop bridge.**
  - Add a C++ module that blocks every control step (Δt) on a ZeroMQ REQ/REP socket, in the Veins-Gym pattern (ZMQ + protobuf; https://github.com/ComNetsHH/omnetpp-ml/blob/main/docs/openai_gym.md).
  - It sends each UAV's RECEIVED-information observation to Python. Python returns actions, and the module sets the next positions.
  - Use Cmdenv and run multiple OMNeT++ instances in parallel.
  - Native Python control of OMNeT++ is only planned for 7.0, so do not wait for it.
  - **Fallback:** if Step C is not working by **2026-11-01**, use the step-synchronized trajectory-replay loop. Recompute observations from INET-received packets offline, and use the Step-B model for training. State this honestly in the paper.
- **Step D — final evaluation.** Evaluate every final policy in closed-loop OMNeT++ on the TEST scenes (≥20 episodes per method per regime). Report the gap between the Python simulator and OMNeT++ for every method.

## 6. NOVELTY GATE (days 1–2, run in parallel with engineering; repeat at every milestone)
For each of C1, C2 and C3, run three kinds of search:
- Qwen Deep Research.
- DeepSeek (Search + DeepThink) with at least 3 differently worded queries.
- Direct Google Scholar/arXiv checks.

Target: "network-in-the-loop MARL UAV", "co-simulation OMNeT++/ns-3 MARL swarm closed loop", "topology-dependent information age multi-agent control", "UAV swarm coverage with realistic communication RL", "difference reward K-coverage connectivity".

Write `docs/NOVELTY.md`:
- the 5 closest papers per contribution, each with a verified URL/DOI;
- what each does and does not do;
- a one-paragraph delta for our work.

If a contribution is already taken, sharpen or replace it within the fixed problem and log the reason. Read the 2025 survey on multi-UAV RL with realistic communication models (Cattai et al., IEEE OJ-VT) for gap statements.

## 7. HARD RULES
- **R1 — Artefact-only numbers.** Every number in the paper comes from a results JSON via `scripts/make_macros.py` → LaTeX `\newcommand`. Never type a number by hand.
- **R2 — Pre-registration.** Before main experiments, write `PREREG.md` (hypotheses H1–H4, metrics, seeds, budgets, analysis, stopping rules) and commit it with the hash recorded. Log every deviation.
- **R3 — Convergence before conclusions.**
  - A run counts as converged when the IQM of the last 10% of training is within one bootstrap SE of the previous 10%, OR it has hit the pre-registered max budget.
  - First measure throughput. Then set the budgets: target ≥2×10⁶ env steps per seed for main methods, more if curves still rise.
  - Always plot learning curves against env steps.
- **R4 — Fair comparison.**
  - Use disjoint TRAIN / TUNE / TEST scene seeds.
  - Every method, including the rules, gets an equal tuning budget on TUNE (Optuna, same number of trials).
  - TEST is used only for the final numbers.
  - Publish an information-access table: what each controller sees, and whether it is fresh (ideal) or as received (network).
- **R5 — Statistics.** ≥10 seeds for main methods, ≥5 for ablations. Use rliable IQM with stratified-bootstrap 95% CIs, paired where possible, and report effect sizes.
- **R6 — Headroom gate.** Report a regime as a "main" result only if ceiling − best tuned rule ≥ 0.10 on the primary metric. Build stress regimes inside the fixed problem:
  - sequential or multiple failures,
  - a single-pad bottleneck,
  - small battery,
  - low R_comm,
  - clustered sensor layouts,
  - high traffic load,
  - network-in-the-loop information degradation.
- **R7 — Trust the learner.**
  - Before the experiments that matter, validate your MAPPO on MPE simple_spread or a VMAS task and match a published curve, or port the env to BenchMARL/EPyMARL.
  - Unit-test: reward terms, masks, termination vs. truncation, value (de)normalization, and observation construction from received packets.
  - Use property-based tests (hypothesis) for geometry and graph code.
- **R8 — Mask audit.** Log the masked-action fraction per controller. Ablate the full mask against a connectivity-only mask. The old report shows about 1500 unexecuted actions per episode even for the rule — explain or fix that.
- **R9 — Sanity ordering.** Every evaluation must satisfy random < hover < rule ≤ oracle ceiling. A violation means a bug: stop and fix.
- **R10 — Honesty.** Never write "learned X", "verified" or "done" without a script that reproduces it. Negative results are reported, not buried. Keep a `docs/NEGATIVE.md`.
- **R11 — No fabricated citations.** Every reference must be fetched and checked (title, authors, venue, year). LLM-suggested citations are leads only.
- **R12 — Reproducibility.**
  - Seed everything.
  - Every result file stores the git hash, config and wall-clock.
  - `make paper` rebuilds all figures, tables and the PDF from a clean clone.
- **R13 — Claims ledger.** `docs/CLAIMS.md` records every claim the paper makes, its evidence file, and its status (supported / weak / retracted). The paper may only contain claims marked "supported".
- **R14 — Writing.**
  - IEEE conference format, 6 pages plus references (an arXiv long version is optional).
  - At most 4 contributions.
  - Abstract structure: problem → idea → method → 2–3 headline numbers.
  - No process narration ("the first version was wrong…"), no self-referential sentences, hedges only where they are needed.
- **R15 — No silent scope creep.** Every new idea goes into the BACKLOG with an estimated cost. Only start it when it serves C1–C4.

## 8. EXPERIMENT INTELLIGENCE (do not run experiments blindly)
- **Before every run,** write 3 lines in `docs/LOG.md`: the question, the expected result, and the decision it will change. If no decision depends on it, don't run it.
- **Run a smoke test first:** 1 seed, a short budget, curves inspected. Only then launch the full seeds.
- **Run kill criteria:** NaNs, entropy collapse before 10% of the budget, or a value loss that diverges. Kill the run, diagnose, and log it.
- **Prioritize runs** that resolve the largest uncertainty per GPU-hour.
- **Ablate one factor at a time,** against the same seeds and scenes.

## 9. BROWSER USE TO BOOST YOUR INTELLIGENCE (re-learn this after every compaction; keep `## BROWSER HOWTO` in STATE.md up to date with the exact clicks/URLs that worked)
- **Qwen Chat — https://chat.qwen.ai, Deep Research mode.** Use it for literature sweeps, novelty checks and design critiques. Begin every prompt with: "Today is <output of date>. Prioritize 2024–2026 work. Return titles, venues, years, URLs/DOIs, and what each paper does NOT do."
- **DeepSeek — https://chat.deepseek.com, Search + DeepThink on.** Use it for broad, fast lookups across hundreds of sources: library APIs, OMNeT++/INET build errors, hyperparameter conventions, venue rules. Always state the current date.
- **Hostile-reviewer passes.** At every milestone (end of D3, D7, D11 and D13), paste the abstract, contributions, method and key tables separately into Qwen and DeepSeek with: "You are a harsh IEEE ICC/TMC reviewer. List fatal flaws, missing baselines, and overclaims. Score 1–5."
  - Log the replies in `docs/REVIEWS.md`.
  - For each point, either fix it (with a commit) or rebut it with evidence.
- **Cross-check rule.** When Qwen and DeepSeek disagree on a fact, fetch the primary source yourself.
- **Use idle time for the browser,** while training runs.

## 10. BACKGROUND vs FOREGROUND
- **BACKGROUND** (tmux sessions; logs to `runs/<id>/log.txt`; checkpoints every N updates; auto-resume): training, sweeps, OMNeT++ batch runs (Cmdenv, opp_runall), long evaluations, LaTeX builds.
- **FOREGROUND:** code, tests, analysis of finished runs, the novelty gate, literature, writing, reviewer passes.
- **Hardware first.** Check `nproc`, RAM and `nvidia-smi` (probably an RTX 2050 with 4 GB).
  - Small MLP policies are CPU-bound, so vectorize the env (batched NumPy/Numba or a batched torch env, 32–128 parallel envs) and benchmark steps/sec before planning budgets.
  - Run concurrent seeds up to the core count minus 1.
  - Mind thermals: if the GPU temperature stays above 85 °C, reduce parallelism.
- **Never sleep-wait.** Poll jobs every 20–40 minutes while doing foreground work.
- **Watchdog.** `scripts/watchdog.sh` restarts crashed jobs and updates `runs/STATUS.md`.

## 11. TOOLS TO INSTALL (day 1; log versions and reasons in docs/ENV.md)
- **Core Python stack:** uv or conda, Python 3.11, torch (CUDA), numpy, numba, scipy, networkx.
- **RL libraries:** gymnasium, pettingzoo, vmas, and benchmarl or epymarl (trusted baselines: MAPPO, IPPO, QMIX).
- **Evaluation and tuning:** rliable, optuna, tensorboard.
- **Testing:** pytest, hypothesis, ruff, pre-commit.
- **Analysis:** pandas, matplotlib, seaborn.
- **OMNeT++ bridge:** pyzmq, protobuf; opp_env, OMNeT++, INET, scavetool.
- **Terminal:** tmux, htop, nvtop.
- **LaTeX:** latexmk or tectonic, chktex.
- **Anything else that clearly saves time** — install it and log why.

## 12. PLAN WITH GO/NO-GO GATES (adapt, but log every change and its reason)
- **G0 — Oct 24–25 — setup and trust.**
  - Prompt saved, STATE skeleton written, tools installed.
  - Env vectorized and throughput measured.
  - MAPPO validated on a reference task.
  - SC biconditional fixed. Retracted claims marked in CLAIMS.md.
  - Novelty gate started.
- **G1 — Oct 25–27 — budget truth test.**
  - Retrain the existing MAPPO until it converges (5 seeds) in the old nominal regime and in 2 stress regimes. Tune the rule on TUNE.
  - Decision: write a 1-page memo, `docs/G1_memo.md`, on what the converged results mean for the thesis.
- **G2 — Oct 26–29 — OMNeT++ Steps A and B.** Replay, measurement and the information-channel model. Deliverable: plots of information age and delivery vs. topology. Decision: is information degradation large enough to matter (more than 0.05 coverage loss for the ideal-info rule under it)? If not, increase load or lower R_comm within the problem, or pivot weight to C3 + residual.
- **G3 — Oct 28–Nov 2 — methods at converged budgets on headroom-gated regimes:**
  - tuned rule (ideal info) and tuned rule (received info),
  - greedy assignment,
  - IPPO,
  - MAPPO (team reward),
  - MAPPO + C3 credit,
  - residual MAPPO,
  - QMIX (trusted library),
  - training variants: ideal info / i.i.d. loss (CALF-style) / topology-conditioned (ours).
- **G4 — Oct 30–Nov 4 — OMNeT++ Step C** (the bridge, with the fallback rule from section 5), then Step D closed-loop TEST evaluation.
- **G5 — Nov 2–7 — paper.**
  - Rewrite from scratch, all figures from scripts.
  - Claims audit and two hostile-reviewer rounds.
  - Clean-clone `make paper`.
  - Keep improving experiments until the deadline.
- **Venue research** (verify on the official sites, record in `docs/VENUES.md`): ICC 2027 workshops (paper deadline listed as 17 Jan 2027), VTC2027-Spring recent results (listed as 15 Jan 2027), an arXiv preprint, and a journal extension (e.g. IEEE IoT-J / TMC / Drones).
- **BACKLOG refill sources:** extra seeds; harder regimes; scaling to N = 6/10/12; generalization without retraining; the GNN/attention actor (compare with TAG-MAPPO's approach); reviewer points; figure polish; literature updates.

## 13. HONEST OUTCOME TEMPLATES (choose the one the data supports; never force one)
- **(a) Learning wins under the network-in-the-loop setting** → headline C1 + C2.
- **(b) Rules win even when converged, but topology-aware training narrows the gap and the residual method beats the rule** → headline "learning helps exactly where information degrades", plus residual MAPPO.
- **(c) No learning advantage anywhere** → a rigorous benchmark paper: network-in-the-loop evaluation, converged and tuned baselines, and the reasons why. Still publishable at a workshop if well powered and clearly written.

## 14. STATE PROTOCOL (session auto-compacts at ~450k tokens)
STATE.md must always contain:
- the last-update timestamp;
- the current gate and milestone;
- running jobs (id, command, ETA, log path);
- finished results and their paths;
- decisions with their reasons;
- open questions;
- the BACKLOG (prioritized, at least 10 items);
- `## BROWSER HOWTO`;
- `## HARD RULES` (a short form of section 7).

Update it every 30–60 minutes and before any long command. Commit often with clear messages.

**START NOW:** `date` → save the prompt → measure hardware → write the STATE.md skeleton → start the throughput benchmark in the background → open Qwen Deep Research for the novelty gate while it runs.
