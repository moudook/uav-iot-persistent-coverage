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
  deterministic-mode improvement (+0.0137).

## Innovation 10: feasibility-aware planning (v2, working)
- Fixed the broken prototype (env.summary misuse, dead code). Model-based
  planning: sample K candidate joint actions from trained actor, roll each
  H steps in cloned env, execute best by cumulative CK.
- Smoke (200 steps, H=2 K=4, 2 scenes): planned ~0.906 vs base frozen
  0.885 at same 200-step protocol (+0.020).
- Full run launched: 500 steps, H=2 K=4, 20 scenes x 5 ckpts, plus base
  500-step reference eval. Results pending.

## Innovation 8: action repeat (protocol-corrected re-run)
- Earlier run had a protocol flaw: action_repeat=4 with n_steps=2000
  creates 8000-step episodes (not comparable to base 2000).
- Corrected: n_steps=500 decisions x repeat 4 = 2000 env steps/episode.
- 3 seeds launched under corrected protocol; done at evaluation with
  repeat=1 (as in eval_ckpt). Results pending.

## Pipeline status
- Background jobs: planning full run, base 500-step reference, AR training.
- Next: combined curriculum+energy+anchor on small_battery
  (launcher ready, waits for CPU).
