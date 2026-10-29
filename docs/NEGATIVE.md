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
