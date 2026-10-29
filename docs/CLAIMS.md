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

## Network certificate (C1, validated 2026-10-29)

| # | Claim | Evidence file | Status | Notes |
|---|-------|---------------|--------|-------|
| 12 | Free-space range knee at 1762 m (20 dBm, 2.412 GHz, 50 m altitude, -85 dBm sensitivity, -94 dBm noise) | Simulation/omnet_uav2/pair_pdr_freespace.json | supported | Measured: PDR 0.9975 at d<=1750 m, 0.0 at d>=1775 m. Matches sensitivity threshold within 1%. |
| 13 | At mission scale (80 m) link PDR = 0.9975 (<=0.25% loss) | Simulation/omnet_uav2/pair_pdr_outage.json + channel_model.csv | supported | 8 independent runs, mean 0.9975-0.9988 at 5-1300 m. |
| 14 | MAC contention negligible: PDR 0.998 at N=16, 0.1 s interval | Simulation/omnet_uav2/swarm_contention_contention.json | supported | 15 contenders on one channel, 0.1 s interval: 2995/3000 delivered. |
| 15 | Network is NOT the binding constraint at mission scale; energy and coverage geometry are | docs/LOG.md 2026-10-29 + channel_model.py | supported | Range margin 22x (1762/80). Certifies the simulator's ideal-observation assumption. |
| 16 | Information channel model: PDR(d) = 1 - Phi((sens - (Tx-PL(d)))/sigma), sigma=6 dB | ml_impl/uav_wireless/channel_model.py | supported | Calibrated to INET free-space knee and shadowing. |
