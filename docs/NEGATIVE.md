# NEGATIVE — negative results log

Negative results are reported, not buried (R10).

## Retracted from midsem report (pending re-measurement)
- 0.298 gap (reactive - MAPPO): undertrained (25 episodes). Retract until converged.
- "None of the arms explains it": same tiny budget.
- Credit-assignment diagnosis: same tiny budget.
- SC(π)=0 ∀π ⟺ F=∅: logic error (only F=∅ ⇒ SC≡0).

## New negative results (to be logged during sprint)
(none yet)
---

## 2026-10-29 — INET ini overrides were silently ignored

Not a physics result; a tooling result, and it invalidates earlier Step B data.

- `**.uav[*].mobility.<param>` does not match through a module vector in
  OMNeT++ 6.4. No warning is emitted; the NED default silently wins.
- A 17-point distance sweep (5 m to 4000 m) returned PDR = 0.9950 at every
  point, with identical packet counts, because all 17 runs replayed one default
  trace. Reported here so the number is never reused.
- The Python simulator hovers UAVs at z = 50 m, but the original INET scenario
  put every node at z = 0 m (constraintAreaMaxZ = 0). The two models were not
  describing the same geometry.
- Replacement: `Simulation/omnet_uav2/` with network-level parameters and a
  causal self-test (send interval must scale packet count). See LOG.md entry of
  the same date.

## 2026-10-31 - C3 credit and residual MAPPO do not beat team-reward MAPPO

**Question.** Does redundancy/criticality-aware credit (C3) or residual MAPPO
(BC init + PPO) improve on team-reward MAPPO?

**Result.** No on both.

- C3 vs team, paired over 5 seeds:
  - single_pad: delta +0.013 (p = 0.66, t = 0.47), P(c3 > team) = 0.56
  - small_battery: delta -0.024 (p = 0.68, t = -0.44), P(c3 > team) = 0.40
  - Neither is significant; effect sizes are within seed noise.
- Residual MAPPO (BC init + PPO), 5 seeds on single_pad: entropy collapses to
  exactly 0.000 by end of training. Final CK = 0.4500 in 2/2 complete seeds
  (identical degenerate deterministic trajectories). Seed 2-4 pending.
  - Compare: MAPPO team = 0.6149, reactive rule = 0.7402.
  - The 3-episode smoke test (CK = 0.792) was a spec: the BC policy is good,
    but PPO fine-tuning drives it into a degenerate fixed schedule.

**What this means for the paper.** The learning-improvement thesis (C3, residual)
fails. The survivals are: C1 network certificate (supported), stress regimes
preventing collapse (supported), headroom-gated evaluation methodology (C4).
The paper must report the null results honestly: in this setting, trained policies
do not beat a well-tuned reactive rule.
