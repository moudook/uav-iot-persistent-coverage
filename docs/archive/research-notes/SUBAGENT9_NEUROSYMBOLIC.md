# Subagent 9 - Neuro-Symbolic / Rule-Augmented Learning (first-principles, 2026-10-30)

From ses_e76ee63e2ffeOJBridePTNW0U8 (Mercury 3, read-only).

## Reframed problem
Outcome: a controller whose CK beats the reactive rule (0.740 single_pad, 0.716 small_battery) reproducibly. The mechanism is not the goal. Paradox: supervision copies the rule (BC 0.79-0.98) but RL continuation destroys it (entropy -> exactly 0, degenerate fixed schedule, CK ~0.45, docs/NEGATIVE.md), while from-scratch MAPPO stalls at 0.37-0.71. So: keep the rule as an executable anchor, learn only where to deviate.

## Ground truths
(1) Feasible policy exists: the rule itself scores 0.740/0.716; oracle ceiling 1.0, headroom ~0.26 [FACT: results_main.csv, FINDINGS.md]. (2) Discrete 6-action space: additive real residuals (classic RPL) don't apply; the discrete analogue is Bernoulli gating over rule vs learned action. (3) BC reaches rule-level skill from the existing 11-feature observation, so the rule class is imitable [FACT: NEGATIVE.md].

## Ledger
[FACT] BC+PPO collapses (measured). [ASSUMPTION] Collapse is unanchored exploitation under 200 episodes, not credit (C3 null weakly rules credit out). [ASSUMPTION] Rule suboptimality is localized: contention, return timing, failure reconfiguration.

## Portfolio
- Baseline: full-network MAPPO (fails), BC+PPO (fails), rule (0.74).
- M1 (best bet) Rule-anchored gating. Policy = Bernoulli gate g_o(g_i) choosing baseline_reactive_local's precomputed action or a learned deviate head. Init g -> follow rule (p=0.9), BC warm-start both heads off rule rollouts, then PPO. Floor: if g collapses to always-rule, CK = 0.74 >= all MAPPO runs. Prior art: RPL (Silver et al., arXiv:1812.06298) with non-differentiable base; deterministic-high-level/DRL-low-level UAV swarm (PMC10648592).
- M2 (cheap) Threshold tuning. CEM/random search over 6-10 rule parameters (return threshold, local radius, tie-break). If a tuned rule beats 0.74, the win exists without neural nets; tells us if learning is needed at all.
- M3 (high-variance) Differentiable soft decision tree as gate (Silva et al. PMLR 2020; Distill2Explain 2024), leaves = {rule, deviate}, BC pretrain then KL-anchored PPO; interpretable (VIPER-style extraction, Bastani et al. NeurIPS 2018).

## Why M1 should work
It converts "learn a complete controller from sparse noisy reward" into "learn rare local corrections to a known-good base". Gradient signal fires only where the rule errs; the base supplies long-horizon competence. Entropy-collapse becomes benign: worst case equals the rule, which already beats MAPPO. The observation already contains pad bearing, deficit map, identity, battery [FACT: AUTONOMOUS_STATE.md], so the gate has its inputs.

## Stress test
Risks: gate never fires (result: equality); override under value-noise (degrade); corrections unlearnable in budget. Mitigations: paired eval, common random numbers, capped deviation-rate schedule, entropy floor + KL anchor.

## Cheapest test
Reuse env/train/eval; wrap env to call baseline_reactive_local for rule branch (exists). 200 episodes x 2000 steps, 5 seeds, single_pad + small_battery, paired deltas on identical eval scenes. Run M2 in parallel (one day).

RECOMMENDATION: M1 rule-anchored gate as best bet; M2 as parallel control to test whether learning is even required.
TEST: H: CK(gate) > CK(rule). Success: paired 95% CI on Delta excludes 0 with mean Delta >= +0.03, gate usage 2-50%, end-entropy > 0.3.
KILL RULE: Stop if Delta <= +0.01 (CI includes 0), or CK(gate) < CK(rule) - 0.02, or usage < 2% with no improvement; report anchored-floor result and pivot to M2-only.
CONFIDENCE: rule/MAPPO/BC/collapse numbers [FACT: measured in repo]; RPL, soft-tree, programmatic-policy lines exist [FACT: web-verified]; gating beats rule within budget [ASSUMPTION: untested]; collapse mechanism [ASSUMPTION].
- Sources: RPL (Silver et al., arXiv:1812.06298), deterministic-high-level/DRL-low-level UAV swarm (PMC10648592), Silva et al. PMLR 2020, Distill2Explain 2024, Bastani et al. NeurIPS 2018.
