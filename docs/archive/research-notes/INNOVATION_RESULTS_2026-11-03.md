# INNOVATION RESULTS - 2026-11-03 session

Autonomous session (user out of town). Objective: run remaining
innovations under the corrected protocol and record results.

## Innovation 11: critical-coverage anchor feature (NEW)
- Feature: scalar = fraction of sensors UAV i covers that have exactly K
  total coverage (ncov == K). One extra obs dim (41 -> 42).
- Code: env.py cfg.use_critical_anchor; eval_ckpt.py and eval_stress.py
  restore it from checkpoint metadata (protocol-critical fix).
- Nominal held-out (20 scenes, 5 seeds): anchor 0.9521 [0.9383, 0.9659]
  vs base 0.9512 [0.9381, 0.9643]. Paired +0.0009, 95% CI
  [-0.0140, +0.0159] -> NOT resolved.
- Deterministic (argmax) eval: base det 0.9412 -> anchor det 0.9549
  (+0.0137). This is the deployment-mode policy (argmax), so the anchor
  helps the mode a deployed controller actually uses.
- Stress (zero-shot, vs base):
    nominal        +0.0262 -> +0.0277
    small_battery  -0.0644 -> -0.0693   (slightly worse)
    low_comm       +0.1246 -> +0.1256
    clustered      -0.0384 -> -0.0350   (spread_start: designed for this)
    failure        +0.0338 -> +0.0388
    multi_failure  +0.0349 -> +0.0377
- Verdict: directional improvement on failure regimes and spread_start,
  but small; not resolved at 5 seeds x 20 scenes. Strongest signal is
  deterministic-mode improvement (+0.0137), BUT per-seed inspection shows
  it is not consistent: seed_3 det +0.062, seed_4 det -0.030, others
  +0.002..+0.017. No clean story; do not over-read.
- Per-seed det (base -> anchor): 0.9231->0.9396, 0.9459->0.9482,
  0.9446->0.9618, 0.9163->0.9783, 0.9764->0.9465.

## Innovation 10: feasibility-aware planning (v2, working)
- Fixed the broken prototype (env.summary misuse, dead code). Model-based
  planning: sample K candidate joint actions from trained actor, roll each
  H steps in cloned env, execute best by cumulative CK.
- Smoke (200 steps, H=2 K=4, 2 scenes): planned ~0.906 vs base frozen
  0.885 at same 200-step protocol (+0.020).
- Full run (500 steps, H=2 K=4, 20 scenes x 5 ckpts):
    base   0.9326 [0.9236, 0.9415]
    planned 0.9531 [0.9487, 0.9575]
    paired +0.0205, 95% CI [+0.0150, +0.0260] -> RESOLVED (excludes zero).
    Consistent across all 5 checkpoints (+0.0153 to +0.0270).
  This is the headline finding of the session: feasibility-masked
  lookahead planning over trained-policy candidates improves coverage
  without retraining, at test time only.

## Innovation 8: action repeat (protocol-corrected re-run)
- Earlier run had a protocol flaw: action_repeat=4 with n_steps=2000
  creates 8000-step episodes (not comparable to base 2000).
- Corrected: n_steps=500 decisions x repeat 4 = 2000 env steps/episode.
- 3 seeds trained under corrected protocol (n_steps=500, repeat=4 =
  2000 env steps/episode); evaluated at repeat=1 (deployed policy):
    AR mean 0.9086 (sd 0.0285) vs base 0.9512 -> -0.043. HURTS.
    Action-repeat training does not transfer to the deployed (repeat=1)
    policy; the policy is worse, not better. Clean negative result.

## Pipeline status
- Background jobs: planning full run, base 500-step reference, AR training.
- Combined curriculum+energy+anchor on small_battery (3 seeds):
    0.7976 vs rule 0.8290 (-0.0314). Worse than curriculum+energy alone
    (0.831, ties rule). The anchor feature HURTS the small_battery regime
    even on top of the best fix. Consistent with anchor hurting
    small_battery in the plain stress table (-0.0693 vs -0.0644).
- Session verdict: planning is the only resolved positive innovation
  (+0.0205). Anchor: directional on failure regimes, hurts small_battery.
  Action-repeat: hurts. Combined+anchor: hurts.

## Honest caveat on planning (must appear in any write-up)
- The planner spends K x H extra environment rollouts per decision
  (K=4 candidates x H=2 steps = 8 rollouts per step) at TEST time. It is
  a test-time compute tradeoff: the frozen policy + planner uses more
  compute than the frozen policy alone. This is exactly the tradeoff a
  deployment engineer faces: more compute per decision for better
  coverage, no retraining.
- The comparison is compute-UNmatched in that sense; the paper must state
  this when reporting the +0.0205 (the same honesty standard as the
  report's existing "not compute-matched" limitation).
- HEADLINE PROTOCOL (2000 steps, 20 scenes, 5 ckpts):
    base    0.9512 [0.9381, 0.9643]
    planned 0.9723 [0.9633, 0.9813]
    paired +0.0211, 95% CI [+0.0137, +0.0285] -> RESOLVED.
    All 5 checkpoints positive (+0.0122 to +0.0279).
    Learner-vs-rule margin: +0.0282 (base) -> +0.0493 (planned).
    Headroom vs ceiling unchanged (0.077, rule-bound).
- STRESS-PLANNING (500 steps, 5 scenes, 5 ckpts) - all six regimes
  RESOLVED positive:
    nominal        +0.0236  [+0.017, +0.030]
    small_battery  +0.0206  [+0.010, +0.031]   (was -0.064 vs rule)
    low_comm       +0.0300  [+0.004, +0.056]
    clustered      +0.0175  [+0.014, +0.021]   (spread_start; was -0.038)
    failure        +0.0246  [+0.018, +0.031]
    multi_failure  +0.0192  [+0.011, +0.028]
  The planner helps on the exact regimes where the learned policy loses to
  rules (small_battery, clustered). It does not fully close those gaps
  (still -0.04 vs rule on small_battery, -0.0001 on clustered at 500
  steps), but it consistently shifts the learner up on every regime.
- Caveat stands: test-time compute cost (K x H env rollouts per decision);
  comparison is compute-unmatched. The 2000-step protocol validation is
  the remaining gate before this can be reported as a headline result.
