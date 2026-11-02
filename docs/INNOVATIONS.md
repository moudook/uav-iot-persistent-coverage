# INNOVATIONS TRACKER - 10 innovations, combine the best

Status: 2026-11-02 04:30. Target: research-level publishable paper.
Each innovation: idea, novelty, implementation, test, result.

## INNOVATION 1: Curriculum learning over battery stress
- Idea: train with B_max from 60000 -> 15000 over episodes; the learner never sees depletion in nominal training.
- Novelty: staged battery curriculum for energy-aware MARL UAV coverage.
- Implementation: train_mappo curriculum params + env.cfg.B_max update.
- Test: small_battery regime (where learner currently loses -0.064).
- Status: IMPLEMENTING.

## INNOVATION 2: Energy-aware potential-based shaping
- Idea: telescoping potential on min-battery fraction; r += kappa_E*(phi_prev - gamma*phi_curr).
- Novelty: potential-based energy shaping that preserves optimal policy.
- Implementation: env.py reward + config flag energy_shape_kappa.
- Test: small_battery regime.
- Status: IMPLEMENTING.

## INNOVATION 3: Random observation shuffling (TAG-MAPPO style)
- Idea: shuffle agent order in the batch during update to break coordinate-index bias.
- Novelty: permutation-invariant training for shared-actor MARL.
- Implementation: collect_rollout / update shuffle.
- Test: clustered (spread start) regime.
- Status: IMPLEMENTING.

## INNOVATION 4: Reset-and-Finetune (R&F) training stability
- Idea: reset optimizer + decay LR at episode 100; syncs LR decay with optimizer reset.
- Novelty: from ORCHID (arXiv:2602.09994).
- Implementation: train_mappo.
- Test: convergence speed / final CK.
- Status: IMPLEMENTING.

## INNOVATION 5: Difference credit assignment
- Idea: per-agent marginal coverage reward r_i = r_team + beta*D_i.
- Novelty: credit assignment for shared team reward.
- Implementation: already in env.py (credit_mode="diff").
- Test: nominal (diff beta=2 already shows +0.007).
- Status: TESTING (diff2 sweep running).

## INNOVATION 6: Graph attention policy (TAG-MAPPO style)
- Idea: replace fixed 4-neighbor slots with self-attention over all agents.
- Novelty: permutation-invariant, handles variable N; addresses spread start.
- Implementation: new Actor class with attention.
- Test: clustered regime.
- Status: DESIGNED.

## INNOVATION 7: Intrinsic motivation (RND)
- Idea: curiosity bonus for novel states.
- Novelty: exploration in sparse-reward UAV coverage.
- Implementation: RND module in mappo.
- Test: small_battery.
- Status: DESIGNED.

## INNOVATION 8: Action repeat (temporal abstraction)
- Idea: execute each action k steps.
- Novelty: reduces decision frequency, easier credit assignment.
- Implementation: train loop.
- Test: convergence speed.
- Status: DESIGNED.

## INNOVATION 9: Self-play adversarial scenarios
- Idea: train against worst-case layouts.
- Novelty: robustness to deployment.
- Implementation: adversarial layout generator.
- Test: all regimes.
- Status: DESIGNED.

## INNOVATION 10: Feasibility-aware planning (H-step lookahead)
- Idea: roll out H steps ahead using feasibility mask.
- Novelty: model-based planning with feasibility.
- Implementation: env planning.
- Test: all regimes.
- Status: DESIGNED (H=3 already in mask).

## COMBINATION PLAN
Combine innovations 1+2+3+4+5 into a single "Innovative MAPPO" config
and test on all regimes. If it beats the anchor on small_battery and
clustered, that's the paper's algorithmic contribution.
EOF