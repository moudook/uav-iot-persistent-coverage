# Subagent 6 - Multi-Objective/Pareto (first-principles, 2026-10-30)

From ses_e76ee63e7fferTcBCjFyc7Zvu8 (Mercury 3, read-only).

## Reframed problem
Goal: learned decentralized policy whose CK beats reactive rule (0.7402 single_pad, 0.7162 small_battery). Central paradox: coverage-seeking, energy-conservation, connectivity-maintenance actions conflict; single scalar reward forces one fixed tradeoff, so gradient conflicts erase the coverage signal exactly where it matters.

## Ground truths & evidence
- Reward is one weighted sum of 7 terms (env.py L1280-1309): lam_O=1.0, lam_D=2.0 on a binary D_t, lam_C=0.5, lam_E=0.1, lam_W=0.05, lam_B=0/2.0. Rare binary events at weight 2.0 dominate the shared return -> high-variance GAE -> CK swings 0.23-0.90 within a seed (G1_memo).
- Residual MAPPO (BC init + PPO) collapses to entropy exactly 0.000 and identical degenerate CK=0.450 (NEGATIVE.md): scalar gradient actively walks policy off high-coverage Pareto region.
- Headroom gate passes (oracle 0.26-0.63 above rule): rule is not optimal, room exists.
- Small_battery worst gap (0.346): regime where scalar energy-vs-coverage tradeoff is tightest.

## Proposal: two orthogonal levers
(A) Fix misalignment/delay (cheap): r_t = -lam_O*U_t - lam_D*D_t - lam_R*R_t - lam_C*Crit_t - lam_B*B_t - lam_W*W_tilde, with W_tilde = W_t only if min_i(E_i - E_req_i) > 0 (never punish movement that may be maintenance), lam_B = 1.0.

(B) Potential-based shaping (PBRS; Ng et al. 1999, Devlin/Kudenko 2011 for MARL): Phi_i(s) = kappa_E*clip((E_i - E_req_i)/E_req_i, 0, 1)*1[E_i >= E_req_i] + kappa_P*(1 - d_i,pad/D_max)*1[E_i < E_req_i]. r_i^shaped = r_t + gamma*Phi_i(s') - Phi_i(s), with Phi_i = 0 at terminal/truncated states. State-based, optimum preserved. Each agent's potential uses its own battery/position, breaking the symmetry that prevents specialization.

(C) Curriculum: Phase 1 coverage skill (near-infinite battery, no failures, 2 pads); Phase 2 energy skill (restore B_max, enable A+B); Phase 3 full stress (1 pad + failures). Gate phases on eval CK plateaus; keep entropy floor (masked entropy >=0.3).

## Why it should work
A removes anti-charge gradient and activates dense immediate shortfall signal. B converts 1000-step-delayed decision into per-step telescoping gradient and gives each UAV distinguishable potential (fixes credit + symmetry). C prevents cold-start joint failure (deployment+energy+contention), the collapse mode seen in every PPO variant.

## TEST
A vs current MAPPO and reactive rule; 5 seeds, 200x2000 steps, single_pad and small_battery; paired per-seed comparison. Success: mean CK >=0.76 both regimes.

## KILL RULE
Pre-registered. Kill shaping arm if A does not beat seed-matched MAPPO by >=+0.05 in BOTH regimes (paired t, p<0.05). Kill B if fails to beat A by >=0.03. Then conclude gap is optimization (entropy), not reward structure, pivot to curriculum+entropy-floor or report null.

## CONFIDENCE
- [FACT: repo code] W_t anti-charge, lam_B=0, E_t scale, C3 marginal-coverage mechanism.
- [FACT: measured logs] entropy collapse, BC->PPO degeneracy.
- [FACT: sourced] PBRS optimality preservation; curriculum precedent in UAV MARL.
- [REASONED: untested] energy-timing dominates stress regimes; staged A->B->C separates it.
- [UNKNOWN] whether A alone suffices; hence cheapest-first ordering.
- Sources: arXiv:2202.12028 (evolutionary MORL UAV MEC, Pareto set), arXiv:2601.14092 (attention-MORL UAV-IoT data/energy tradeoff), arXiv:2410.19372 (MGDA++ strong-Pareto MARL), arXiv:2610.35736 (objective-wise counterfactual credit MOMARL), ICLR 2025 reward-dimension-reduction.
