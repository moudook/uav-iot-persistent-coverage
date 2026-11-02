# INNOVATIONS TRACKER - 10 innovations, combine the best

Status: 2026-11-02 21:00. Target: research-level publishable paper.

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
| Innov 1+2+4+5 (combined) | combined | small_battery | (pending) | -- | -- |

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
- Result: +0.007 on nominal (0.959 vs 0.952), not resolved.
- Status: TESTED (small positive).

## INNOVATION 6: Graph attention policy
- Result: 0.753 on small_battery (vs 0.831 curriculum, vs 0.765 anchor). WORSE.
- Status: TESTED (negative).

## INNOVATION 7: Intrinsic motivation (RND-lite)
- Status: IMPLEMENTED, not yet tested.

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
6. Difference credit is a small positive (+0.007).
7. The paper's thesis: "the ego observation is sufficient and necessary;
   the remaining gap on energy regimes is a genuine limitation."

## COMBINATION PLAN
Best so far: curriculum+energy (0.831 on small_battery, ties rule).
Next: test combined (curriculum+energy+diff) on small_battery.
If it beats the rule, that's the paper's algorithmic contribution.
EOF