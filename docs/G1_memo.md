# G1 Memo — Budget Truth Test (2026-10-25)

## Question
Does the existing MAPPO converge at a larger budget, and what do the converged results mean for the thesis?

## Setup
- 5 seeds (0-4), 200 episodes x 2000 steps = 400k env steps/seed (~8x the midsem's 50k).
- Old nominal regime (N=5, M=20, side=80, R_cov=35, R_comm=40, K=2, 2 pads, no failures).
- Device: CPU. BLAS pinned to 1 thread.
- Training time: ~63 min/seed (5 seeds in parallel ~63 min total).

## Results
| Seed | Final CK | Last-10 mean CK | Min (all) | Max (all) |
|------|----------|-----------------|-----------|-----------|
| 0    | 0.5078   | 0.6070          | 0.3976    | 0.8259    |
| 1    | 0.6750   | 0.6968          | 0.2424    | 0.8973    |
| 2    | 0.3678   | 0.4913          | 0.2467    | 0.8674    |
| 3    | 0.3324   | 0.4533          | 0.2293    | 0.5977    |
| 4    | 0.3352   | 0.4736          | 0.2796    | 0.6688    |
| Mean | 0.4436   | 0.5444          | —         | —         |
| SD   | 0.1479   | 0.1251          | —         | —         |

Reactive rule (unprivileged): 0.972 (deterministic). Oracle ceiling: 1.000.

## Findings
1. **MAPPO does NOT converge at 400k steps.** Last-10 CK ranges 0.45-0.70 across seeds with high variance. The learning curve oscillates wildly (min 0.23, max 0.90 within a single seed). No seed shows a clear plateau.
2. **The midsem's 0.674 (single seed, 25 ep = 50k steps) was a lucky seed.** At 400k steps with 5 seeds, the mean is 0.44 — much worse and highly variable. The original "0.298 gap" is meaningless.
3. **Headroom gate (R6): ceiling - best rule = 1.000 - 0.972 = 0.028 < 0.10.** The nominal regime FAILS the headroom gate. No "main" result can be reported in this regime. Need stress regimes (R6) to create headroom.
4. **High variance across seeds** (sd 0.15 on final CK) indicates the training is unstable — possibly due to the team reward, the observation, or insufficient exploration. This is consistent with the credit-assignment hypothesis but not proof.

## Implications for the thesis
- The original thesis (network-in-the-loop) is UNAFFECTED by this — C1/C2/C3 are about network realism, not about beating the rule in the nominal regime.
- The "MAPPO underperforms a reactive rule" finding from the midsem is RETRACTED (R10). It was an artifact of undertraining and single-seed luck.
- The stress regimes (R6) are now critical: we need regimes where ceiling - best rule >= 0.10 to have a meaningful "main" result. Candidates: sequential/multiple failures, single-pad bottleneck, small battery, low R_comm, clustered sensors, high traffic load, network degradation.
- The credit-assignment diagnosis (C3) is still a hypothesis, not a finding. Needs ablation at converged budgets.

## Decisions
- Retain thesis (network-in-the-loop MARL). The G1 result does not invalidate it.
- Next: G2 (OMNeT++ Steps A+B) to build the information-channel model. INET 4.6 installing in WSL2.
- Need to run G1 at 2e6 steps (1000 episodes) to check convergence, OR pivot to stress regimes first (R6 headroom gate).
- Recommend: run 1 seed at 2e6 steps (1000 ep) as a convergence check before committing to full 5-seed run.

## Status of retracted claims (docs/CLAIMS.md)
- #1 (0.298 gap): RETRACTED (confirmed by G1 — no convergence, high variance).
- #2 ("none of the arms explains it"): RETRACTED.
- #3 (credit-assignment diagnosis): RETRACTED (still a hypothesis).
- #4 (SC biconditional): FIXED.

---
Commit hash: (to be recorded)
---
