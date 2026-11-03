# INNOVATIONS TRACKER - 10 innovations, combine the best

Status: 2026-11-02 23:10. Target: research-level publishable paper.

## RESULTS SO FAR (canonical, survives compaction)

| innovation | config | regime | CK | vs anchor | vs rule |
|---|---|---|---|---|---|
| anchor (ego+shape) | base | nominal | 0.952 | -- | +0.029 (resolved) |
| anchor (ego+shape) | base | small_battery | 0.765 | -- | -0.064 |
| Innov 1+2+4 (curriculum+energy+R&F) | +curriculum+energy+R&F | small_battery | 0.831 | +0.066 | +0.002 (tied) |
| Innov 6 (graph attention) | +attn | small_battery | 0.753 | -0.012 | -0.076 |
| Innov 5 (diff credit beta=2) | diff2 | nominal | 0.959 | +0.007 | +0.036 |
| no_w (W_t removed) | no_w | nominal | 0.940 | -0.012 | +0.017 |
| full_obs (global state) | full_obs | nominal | 0.863 | -0.090 | -0.060 |
| Innov 1+2+4+5 (combined) | combined | small_battery | 0.816 | +0.051 | -0.013 |
| Innov 7 (intrinsic) | +intrinsic | small_battery | 0.834 | +0.069 | +0.005 (tied) |

## INNOVATION 1: Curriculum learning over battery stress
- Result: +0.066 on small_battery (0.765 -> 0.831). Ties the rule (+0.002).
- Status: TESTED (partial win).

## INNOVATION 2: Energy-aware potential-based shaping
- Result: combined with curriculum; effect not isolated.
- Status: TESTED (combined).

## INNOVATION 3: Random observation shuffling
- Status: DESIGNED (no-op for shared policy; needs obs rework).

## INNOVATION 4: Reset-and-Finetune (R&F)
- Result: included in curriculum run.
- Status: TESTED (combined).

## INNOVATION 5: Difference credit assignment
- Result: +0.007 on nominal (0.959 vs 0.952), not resolved. HURTS on small_battery (-0.015).
- Status: TESTED (small positive on nominal, negative on small_battery).

## INNOVATION 6: Graph attention policy
- Result: 0.753 on small_battery (vs 0.831 curriculum, vs 0.765 anchor). WORSE.
- Status: TESTED (negative).

## INNOVATION 7: Intrinsic motivation (RND-lite)
- Result: 0.834 on small_battery (vs 0.831 curriculum, vs 0.829 rule). +0.003 vs curriculum. Basically no effect.
- Status: TESTED (no effect).

## INNOVATION 8: Action repeat
- Status: IMPLEMENTED, not yet tested.

## INNOVATION 9: Adversarial scenarios
- Status: IMPLEMENTED, not yet tested.

## INNOVATION 10: Feasibility-aware planning
- Status: DESIGNED (script exists).

## KEY FINDINGS
1. The ego-centric observation is the main driver (+0.093 on nominal).
2. Full global state HURTS (-0.090) - more information is worse.
3. Attention HURTS (-0.078) - the MLP is better than attention here.
4. Curriculum helps on small_battery (+0.066) but doesn't close the gap.
5. W_t penalty is NOT the bottleneck (no effect).
6. Difference credit is a small positive on nominal (+0.007) but HURTS on small_battery (-0.015).
7. Intrinsic motivation has no effect (+0.003).
8. The paper's thesis: "the ego observation is sufficient and necessary;
   the remaining gap on energy regimes is a genuine limitation."

## COMBINATION PLAN
Best so far: curriculum+energy (0.831 on small_battery, ties rule).
Diff credit HURTS when combined (-0.015).
Intrinsic has no effect (+0.003).
Attention makes it worse (-0.078).
The residual on energy regimes is genuine; the rule's explicit recharge
logic beats the learned policy. This is the paper's publishable finding.
EOF


## INNOVATION 11: Critical-coverage anchor feature
- What: one scalar added to the ego-centric observation: the fraction of
  sensors UAV i currently covers that have EXACTLY K total coverage
  (ncov == K). If UAV i moves, those sensors drop below K.
  Directly addresses the spread_start weakness: the learner loses there
  (0.959 vs rule 0.997) because it cannot see that leaving a sensor
  breaks K-coverage.
- Status: IMPLEMENTED (cfg.use_critical_anchor, obs_dim +1) and TRAINING
  under corrected protocol (5 seeds, 200 ep, held-out eval on seeds
  1000-1019). Results pending.
- Design intent: zero extra mechanism, one scalar, tests the hypothesis
  that the spread_start gap is an observation blind-spot rather than a
  control limitation.
- Evaluation: compare vs exp_ego_eval (base) on nominal held-out; and on
  stress regimes via eval_stress.py --tag exp_anchor_eval (separate
  artifact stress_eval_anchor.json so the report artifact stays intact).
- Result (2026-11-03): nominal held-out 0.9521 vs base 0.9512, paired
  +0.0009, 95% CI [-0.014, +0.016] -> NOT resolved. Deterministic eval
  improved 0.9412 -> 0.9549 (+0.0137). On stress: clustered (spread_start)
  -0.0384 -> -0.0350 (better, still loses); failure +0.0338 -> +0.0388;
  multi_failure +0.0349 -> +0.0377; small_battery -0.0644 -> -0.0693
  (slightly worse). Verdict: directional but small; does not close the
  spread_start gap. Not a headline result on its own.
- Note: the anchor feature may be most valuable in the deterministic/argmax
  deployment mode (det +0.0137), which is the mode a deployed controller
  uses. Worth reporting as a secondary observation.
