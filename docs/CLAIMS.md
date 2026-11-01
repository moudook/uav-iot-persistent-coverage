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

## Second sprint: learner defects and protocol correction (2026-11-01)

| # | Claim | Evidence file | Status | Notes |
|---|-------|---------------|--------|-------|
| 17 | The reported collapse was caused by a sign-flipped entropy term (+c2H in the loss) and by severe under-training (25 gradient steps total, no PPO epochs) | ml_impl/uav_wireless/mappo.py; runs/si_fixed/ | supported | Both fixed; entropy now decays from 1.40 to 1.05 over 200 episodes instead of collapsing. |
| 18 | "The learned controller scores below a random policy" | runs/diag/random_baseline.json | RETRACTED | The 0.860 figure was measured with `SimConfig` defaults, not with `base_config()`; it is a different instance. Re-measured on the paper's configuration the random policy scores 0.539. The comparison was never like-for-like. |
| 19 | Training-episode CK is a valid comparison against a rule baseline | - | RETRACTED | It is measured by an exploratory policy on one scene while the policy is still changing. Superseded by the frozen-policy, held-out-scene protocol of Section~\ref{sec:protocol}. |
| 20 | Rule baselines reproduce at the current HEAD | runs/rules/eval_rules.json | supported | Fixed 0.353, Greedy 0.792, Reactive 0.874, Reactive-local 0.945 over scenes 0-9; over scenes 0-4 they reproduce the report's table exactly (0.372/0.784/0.953/0.972), which shows the table's protocol was 5 scenes. |
| 21 | Ego-centric sensor bearings + potential-based distance shaping lift the learner above the bug-fixed baseline | runs/exp_ego_eval/ vs runs/bugfix_eval/ | supported | 0.9522 vs 0.8594 (+0.0928, resolved), frozen-policy, 20 held-out scenes. |
| 22 | The learner is ahead of the strongest rule on the nominal configuration | runs/exp_ego_eval/eval_heldout.json vs runs/rules_heldout/ | supported | +0.0289, 95% CI [+0.0159, +0.0420], excludes zero. |
| 23 | The learner is ahead on 4/6 same-architecture stress regimes, behind on small battery and spread start | runs/stress_eval/stress_eval.json | supported | zero-shot; NA on regimes whose state dim changes (single_pad). |
| 24 | The pre-correction gap (0.298) and random baseline (0.860) are retracted | docs/MEASURED_NUMBERS.md | retracted | 0.860 was a config mismatch; 0.298 was a broken learner + train-CK eval. |
