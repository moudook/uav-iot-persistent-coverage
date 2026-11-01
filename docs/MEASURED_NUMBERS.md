# MEASURED NUMBERS - canonical, survives context compaction

Last updated: 2026-11-02 01:20 (machine local time)
Every number here was produced by the artefact named next to it. If a number
here disagrees with `midsem_numbers.tex`, the `.tex` is regenerated from the
artefacts and wins.

## The configuration under test

`ml_impl/uav_wireless/experiments.py :: base_config()`

    N = 8 UAVs, M = 20 sensors, K = 2, R_cov = 35 m, field 80 x 80 m
    episode_len = 2000 steps, B_max = 30 kJ, charge_rate = 2e-4
    start_clustered = True, use_agent_id = True, map_grid = 4,
    use_pad_bearing = True
    training: 200 episodes, 10 PPO epochs, 4 minibatches, gamma 0.99,
    lambda 0.95, clip 0.20, lr 3e-4, ent_coef 0.01

## Evaluation scenes - three different sets, do not mix them

| set | seed range | n | artefact |
|---|---|---|---|
| pre-correction "5 scenes" | 0-4 | 5 | `ml_impl/results_main.csv` |
| mid | 0-9 | 10 | `ml_impl/runs/rules/eval_rules.json` |
| **held-out (use this)** | **1000-1019** | **20** | `ml_impl/runs/rules_heldout/eval_rules.json` |

Training seeds are 0,1,2,... so scenes 0-4 are NOT held out. Use 1000+.

## Rule baselines (deterministic given a scene)

### Held-out, 20 scenes, seeds 1000-1019  <- the citable set
`ml_impl/runs/rules_heldout/eval_rules.json`

| rule | CK | sd over scenes |
|---|---|---|
| Fixed | 0.3641 | 0.1096 |
| Greedy | 0.7128 | 0.1241 |
| Reactive (global) | 0.8323 | 0.1433 |
| Reactive (local assignment) | **0.9233** | 0.0777 |

### 10 scenes, seeds 0-9
`ml_impl/runs/rules/eval_rules.json`
Fixed 0.3530 / Greedy 0.7918 / Reactive 0.8737 / Reactive-local 0.9451

### 5 scenes, seeds 0-4  <- reproduces the report's pre-correction table EXACTLY
computed from the 10-scene per-scene values:

| rule | over seeds 0-4 | report table |
|---|---|---|
| Fixed | 0.3714 | 0.372 |
| Greedy | 0.7836 | 0.784 |
| Reactive | 0.9530 | 0.953 |
| Reactive-local | 0.9722 | 0.972 |

CONTROL RESULT: the rule half of the pre-correction table is reproducible at
current HEAD. Only the learner's number moved. This is the control that makes
the re-measurement readable.

## Random baseline (uniform over the feasible-action set)

| set | CK | sd | artefact |
|---|---|---|---|
| held-out 20 scenes | 0.5612 | 0.1252 | `ml_impl/runs/diag/random_baseline.json` |
| 10 scenes (0-9) | 0.5395 | 0.1280 | (overwritten; see git history) |

RETRACTED: the earlier "random = 0.860 +- 0.034" used `SimConfig` DEFAULTS
instead of `base_config()` - a different instance. It was never comparable.
Consequence: the claim "the learned controller scores below random" is
withdrawn. 0.749 (train CK) is ABOVE 0.561 (eval random).

## Learned controllers

### si_fixed - Part-1 bug fixes only, NO ego obs, NO shaping
`ml_impl/runs/si_fixed/seed_{0,1,2}.json`, 200 episodes, 3 seeds
train-episode CK (NOT a result; exploratory policy, one scene):
    0.779 / 0.712 / 0.756  ->  mean 0.7488, sd 0.0343
entropy 1.40 -> 1.05, min 0.46-0.61, no collapse.
NO CHECKPOINT SAVED - cannot be re-evaluated without retraining.

### exp_ego_shape - ego bearings + distance shaping (no eval, train CK only)
`ml_impl/runs/exp_ego_shape/seed_0.json`
train-episode CK 0.9259, entropy 1.34 -> 1.10 (min 0.49).
NO CHECKPOINT SAVED. Seeds 1-4 were killed (no checkpoint = not citable).

### exp_ego_eval - ego bearings + shaping, HELD-OUT PROTOCOL
`ml_impl/runs/exp_ego_eval/seed_*.json` + `seed_*.pt`   [RUNNING, 5 seeds]
Seeds 0,1 launched 21:42; seeds 2,3,4 launched 21:47. ETA ~22:40-23:00.
These save `.pt`, so they can be re-evaluated any time with
`python scripts/eval_ckpt.py --tag exp_ego_eval --eval-offset 1000 --eval-seeds 20`

### bugfix_eval - bug fixes only, HELD-OUT PROTOCOL (the ablation)
`ml_impl/runs/bugfix_eval/seed_*.json` + `seed_*.pt`    [RUNNING, seed 0]
Launched 21:47. Same protocol, configuration without ego obs / shaping.

## Numbers that are DEAD - never quote again

| number | was | why dead |
|---|---|---|
| 0.674 | MAPPO CK | buggy learner (entropy sign flipped, 25 gradient steps) |
| 0.298 | gap to reactive rule | follows from 0.674 |
| 0.860 +- 0.034 | random baseline | wrong config (SimConfig defaults) |
| 0.749 | "the fixed learner's result" | it is a TRAIN-time CK, not a result |
| 0.926 | "the ego+shape result" | also a TRAIN-time CK, one seed, one scene |

## Scripts

    scripts/eval_rules.py         rules over a scene set  -> runs/<tag>/eval_rules.json
    scripts/random_baseline.py    random over a scene set -> runs/diag/random_baseline.json
    scripts/run_exp.py            train + save .pt + eval
    scripts/eval_ckpt.py          evaluate saved .pt on any scene set (no retraining)
    scripts/make_midsem_numbers.py  regenerate midsem_numbers.tex from all artefacts


## STRESS REGIMES - zero-shot (2026-11-02, frozen policy, 5 held-out scenes)

learner = exp_ego_eval (5 seeds, mean), rule = Reactive-local, headroom = 1 - rule CK

| regime | rule CK | learner CK | learner - rule | headroom |
|---|---|---|---|---|
| nominal | 0.9213 | 0.9475 | +0.0262 | 0.0787 |
| single_pad | 0.8758 | NA (state dim changes) | -- | 0.1242 |
| small_battery | 0.8290 | 0.7646 | -0.0644 | 0.1710 |
| low_comm | 0.8037 | 0.9284 | +0.1246 | 0.1963 |
| failure | 0.9124 | 0.9462 | +0.0338 | 0.0876 |
| multi_failure | 0.9104 | 0.9453 | +0.0349 | 0.0896 |
| clustered (start=unclustered) | 0.9970 | 0.9587 | -0.0384 | 0.0030 |

Learner ahead on 4/6 same-architecture regimes; loses on small_battery and spread start.
Mean diff over same-arch regimes: +0.0197.

## FINAL VERDICT (2026-11-02)

    learner (ego+shape)   = 0.9522  (95% CI [0.9392, 0.9653], 5 seeds)
    best rule (Reactive-local) = 0.9233
    learner - rule = +0.0289  (95% CI [+0.0159, +0.0420])  -> excludes zero

    bug fixes only = 0.8594  (95% CI [0.8363, 0.8825], 5 seeds)
    ablation: +ego/shaping = +0.0928, resolved

    random = 0.5612 (20 scenes)

The 0.298 gap is gone. The learner is ahead of the strongest rule by 0.029,
resolved. The 0.093 gain comes from the observation change, not from the bug
fixes alone.

## Report state

- `Mlawn-midsem-tex.tex` sec:results has a supersession box (added 2026-11-01).
- `Mlawn-midsem-tex.tex` sec:protocol rewritten to the real protocol.
- `midsem_numbers.tex` is generated; report inputs it after the token macros.
- `docs/second_sprint_draft.tex` holds the new section; {{VERDICT}} and
  {{WHAT_SURVIVES}} are the only unwritten parts, both waiting on exp_ego_eval.
