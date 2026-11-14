# Code and logic audit - 2026-11-14

Goal: verify the whole pipeline (env math, learner, evaluation, tables) before any retraining.
Then: prune non-informative scenarios/columns, retrain the corrected headline, update numbers.

## Audit map
1. Environment math: reward signs (all terms must be negative costs), shaping vs Ng, W_t
   semantics vs Table V, D_t definition, energy model (draw/charge/threshold/reserve),
   action mask + projection, coverage/connectivity, observation features, metrics.
2. Learner math: PPO losses (signs), entropy, clipping, GAE bootstrap, advantage
   normalisation, value normalisation, active mask, minibatch indexing, gamma under
   action-repeat, optimiser/grad-clip, determinism, save/load.
3. Evaluation + analysis: scene sets/offsets, deterministic vs sampled actions, rule
   baselines, aggregation axes, ddof, CI math, table row/column selection, claim audit.
4. Data: which scenarios/columns carry information (discrimination), which are dead
   (pinned, aliases, duplicates).

## Delegation
- Worker A: env.py reward/energy/metrics/obs audit (read-only, report findings).
- Worker B: mappo.py + train.py learner math audit (read-only).
- Worker C: eval_* + analysis pipeline audit (read-only).
- Main: verify every load-bearing finding at file:line, fix confirmed bugs, run tests,
  prune scenarios, launch training.

## Verification verdicts (filled as work completes)
(pending)
