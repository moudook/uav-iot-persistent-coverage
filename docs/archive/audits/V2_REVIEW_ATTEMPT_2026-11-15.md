# Second-generation retrain attempt (2026-11-15)

Status: not promoted. The verified first-generation headline remains the
report's result.

## What was changed

The external code review identified several real defects, and they were fixed
and tested:

- Ng potential reset now starts at the current state (`_prev_phi = None`).
- Physics bills the executed action, not the sampled action; charge requests
  that lose arbitration pay hover power.
- PPO records the executed action and its log-probability when the mask or
  joint projection changes a move.
- PHY-aware ego features exclude sensors the UAV already serves.
- Return-mode assist mask forbids hovering when a pad-approaching move is
  feasible.
- Value normalisation initialises on the first batch instead of a 0.99 EMA
  from (0, 1).
- Scalable 3-dim identity replaces the N-dimensional one-hot.
- `eval_agent` forces the seed-defined scene.

## Result

The retrain used `exp_v2`: 200 episodes, 2000 steps, diff credit, per-agent
advantage normalisation, scalable identity, PHY ego features, assist-return,
and randomised layouts.

Completed seeds collapsed:

| seed | held-out CK | final training entropy |
|---|---|---|
| 0 | 0.3528 | 0.097 |
| 1 | 0.2809 | 0.055 |
| 3 | 0.3582 | 0.050 |
| 4 | 0.2767 | 0.083 |

Mean held-out CK is 0.317. The first-generation headline is
0.9566 +/- 0.0092, with training entropy around 1.0. The v2 policy became
nearly deterministic by episode 40 and never recovered. The four training
histories are stored under `docs/archive/audits/v2/`.

## Interpretation

This is an algorithmic failure of the aggressive v2 mixture, not a stale-file
problem. The most likely causes are the combination of difference rewards,
per-agent advantage normalisation, and layout randomisation, which removes the
noise that kept the first-generation policy exploratory. The next step is a
controlled ablation of those three changes, not more seeds of the same recipe.

The report, its artifacts, and `scripts/verify_report_numbers.py` are unchanged
and still pass 87/87 checks. The v2 checkpoints are experimental evidence only.
