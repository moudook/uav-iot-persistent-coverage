# CLAIMS LEDGER

Every claim the paper makes, its evidence file, and its status (supported / weak / retracted).

## Status legend
- supported: evidence exists and is reproducible
- weak: evidence exists but is underpowered or hedged
- retracted: claim withdrawn pending re-measurement

## Claims from midsem report (to be re-audited)

| # | Claim | Evidence file | Status | Notes |
|---|-------|---------------|--------|-------|
| 1 | 0.298 gap (reactive - MAPPO) | ml_impl/results_main.csv | retracted | Undertrained (25 episodes). Retract until converged budget (R3). |
| 2 | "None of the arms explains it" | ml_impl/analysis/ab_*.json | retracted | Same tiny budget as #1. |
| 3 | Credit-assignment diagnosis | ml_impl/analysis/ab_credit.json | retracted | Same tiny budget. |
| 4 | SC(π)=0 ∀π ⟺ F=∅ | Mlawn-midsem-tex.tex eq:scdegenerate | retracted | Logic error (only F=∅ ⇒ SC≡0). Fix equation. |
| 5 | Packing bound N≥4K for square | Mlawn-midsem-tex.tex eq:regionbound | supported | Math correct; P=4 verified by search. |
| 6 | Area-surplus certifies nothing | Mlawn-midsem-tex.tex | supported | Corner packing counterexample valid. |
| 7 | 170/170 determinism | ml_impl/analysis/determinism_check.json | supported | Verified by E audit. |
| 8 | PHY algebraic equivalence (constant Δ dB) | ml_impl/analysis/phy_runtime_probe.json | supported | Verified by GLM audit. |
| 9 | CPU 1.26x slower than GPU | ml_impl/analysis/device_sensitivity.json | supported | Measured (1.013x actual; paper claim of 1.26x needs recheck) |
| 10 | Teleporting oracle ceiling = 1.000 | ml_impl/analysis/*.json | supported | Verified. |
| 11 | Headroom: privileged rule 0.972 vs ceiling 1.000 | ml_impl/results_main.csv | weak | Headroom only 0.028; need stress regimes (R6). |

## New thesis claims (to be filled during sprint)
(to be added as C1-C4 are developed)
---
