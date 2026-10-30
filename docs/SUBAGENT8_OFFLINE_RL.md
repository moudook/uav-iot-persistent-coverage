# Subagent 8 - Offline RL / Batch RL (first-principles, 2026-10-30)

From ses_e76ee63e4ffe1nbVVsHvkk6Rpx (Mercury 3, read-only).

## Reframed problem
Value sought: a learned controller whose CK reliably beats the handwritten reactive rule (0.740/0.716) under the project's own protocol (200 eps x 2000 steps, 5 seeds, CK). Central paradox: the data already contains a better-than-rule controller - BC extracts ~0.8-0.98 - but any online optimization (PPO/MAPPO) destroys it (residual seed4 log: CK 0.862 at ep 0 -> 0.450 at ep 199). The binding constraint is not credit assignment (C3 null) or reward design; it is on-policy distributional drift.

## Ground truths
1. The rule is a deterministic, decentralized policy; its behavior is reproducible and cheap to roll out. 2. The simulator is seeded and deterministic; dataset generation is exact and repeatable. 3. Offline RL with in-sample constraints provably never evaluates OOD actions (IQL, ICLR 2022; ICQ-MA, NeurIPS 2021), eliminating the drift that kills PPO.

## Constraint ledger (rows that changed the answer)
- Existing bc_data.pkl is (obs, action) pairs only - no r, s' - so it cannot train any TD method. [verified, collect_bc_data.py] -> must regenerate a full-transition dataset.
- Actions are discrete (6), 8 agents, shared params: cheap independent-per-agent critics fit the existing architecture. [verified]
- C3 credit null (per-agent actor + local critic changed nothing) means a per-agent, shared-parameter offline scheme is not a priori crippled. [verified; corrected as assumption]
- OMAR (ICML 2022): naive MA-CQL degrades with agent count; CFCQL (NeurIPS 2023) and ICQ-MA are agent-count-insensitive. [sourced]

## Portfolio (by mechanism)
- A. IQL-Ind (recommended): per-agent IQL with shared params; expectile V per agent, in-sample Q targets, policy extraction by advantage-weighted regression. Never queries OOD actions; extraction is weighted BC within support, so it cannot diverge like PPO. Outperforms BC when the dataset supports stitching (high-value segments from rule variants + BC rollouts).
- B. ICQ-MA / CFCQL as theory-stronger alternatives if stitching needs a joint value (mixer/counterfactual conservatism). Higher implementation cost.
- C. Dataset + mode-robust BC (control): explicitly models the rule's multimodal target selection (round-robin), which plain cross-entropy averages into blended bad actions.
- D. Baseline: BC (already trained), reactive rule, MAPPO, residual-PPO.

## Recommendation
Train A (IQL-Ind) on a frozen dataset of full transitions: (s, a, r, s') collected from the rule across regimes (nominal, single_pad, small_battery) and 5 seeds under the 2000-step protocol, plus epsilon-perturbed BC rollouts for coverage (~30 min/seed at 231 steps/s, parallelizable). Rationale: BC proves the rule's behavior is learnable and already above the rule; offline RL adds (i) self-selection across modes instead of mean-mode averaging and (ii) segment stitching across behavior policies - with zero online drift. Worst case it degrades to BC, which still beats the rule if the BC numbers replicate under the full protocol.

## Stress test
Premortem risks: (1) dataset too narrow -> IQL ~= BC, safe but no gain; (2) long-horizon Q variance -> keep batch norm/double Q, evaluate on 5 eval scenes; (3) failure/recovery events rare in data -> oversample failure-rich episodes during collection. Rival hypothesis: BC's 0.8-0.98 may not replicate under the 2000-step energy-binding protocol (BC was trained on 500-step data) - hence BC must be re-run under the exact protocol as a control. [ASSUMPTION: cheap to test]

## TEST (pre-registered, R2/R4/R5)
Hypothesis: IQL-Ind CK > BC CK + 0.02 and > rule CK + 0.03 (paired CI excluding 0). Minimal test: 1 seed, 1 regime, collect D, train IQL-Ind, sanity-check in-sample Q vs empirical discounted returns (corr > 0.9) and eval CK >= BC CK - 0.01 (~1-2 h). Full test: 5 seeds, frozen D, same seeded eval scenes as MAPPO runs; report IQM + paired CI.

## KILL RULE
If full-run IQL-Ind mean CK <= BC CK (CI covers 0): offline-RL improvement is dead - ship BC alone (validated under protocol). If IQL-Ind CK < rule CK - 0.02: the entire "learned beats rule" thesis fails via this route; stop and report.

## CONFIDENCE
- [verified] PPO collapse from BC init (residual log); rule dataset lacks r/s'; rule CK values.
- [sourced] IQL, ICQ-MA, CQL, CFCQL, OMAR results.
- [ASSUMPTION] stitching headroom exists in this environment (cost to test: low - it is the primary comparison).
- [reasoned] AWR extraction cannot diverge like PPO because it only regresses onto in-support actions; tagging as hypothesis, not fact.
- Sources: IQL (ICLR 2022, arXiv:2010.06213), ICQ-MA (NeurIPS 2021), OMAR (ICML 2022), CFCQL (NeurIPS 2023).
