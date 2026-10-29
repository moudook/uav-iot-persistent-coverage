# Current Findings (2026-10-31, pre-residual)

## Completed experiments
- G3: 25/25 MAPPO seeds across 5 stress regimes (failure, multi_failure, single_pad, small_battery, low_comm)
- C3 credit: 10/10 seeds (single_pad, small_battery, team vs c3)
- Residual MAPPO: 2/5 seeds (seed2 running)

## Key results

### MAPPO stress regimes (team reward, 5 seeds each, 200 ep x 2000 steps)
| Regime | CK mean | sd | entropy | headroom | vs reactive |
|---|---|---|---|---|---|
| single_pad | 0.615 | 0.125 | 1.266 | 0.385 | -0.125 |
| small_battery | 0.371 | 0.083 | 0.810 | 0.629 | -0.346 |
| low_comm | 0.377 | 0.061 | 1.175 | 0.623 | -0.299 |
| failure | 0.630 | 0.136 | 1.369 | 0.370 | -0.086 |
| multi_failure | 0.713 | 0.139 | 1.206 | 0.287 | -0.003 |

### C3 credit vs team (paired, 5 seeds)
- single_pad: delta +0.013 (p=0.66, not significant). C3 slightly better.
- small_battery: delta -0.024 (p=0.68, not significant). C3 slightly worse.
- Conclusion: C3 credit does NOT significantly improve over team reward. Negative result.

### Entropy stability
- All stress regimes: stable entropy (no collapse). min_ent ranges 0.31-0.99.
- Nominal MAPPO collapsed at ep 675 (entropy -> 0). Stress regimes fix this.

### Headroom gate
- All 5 regimes PASS (headroom >= 0.10, range 0.287-0.629).

### Network certificate (INET, supported)
- Free-space range knee: 1762 m. At 80 m mission scale, PDR = 0.9975.
- Contention: PDR 0.998 at N=16. Network is NOT the binding constraint.
- Channel model: PDR(d) = 1 - Phi((sens - (Tx-PL(d)))/sigma), sigma=6 dB.

### Residual MAPPO (partial, 2/5 seeds)
- Smoke test: CK=0.792 vs MAPPO 0.378 after 3 ep (promising).
- Full results pending (seed2 running, seeds 3-4 queued).

### rliable aggregates (MAPPO team across 5 regimes as tasks, n=25)
- mean=0.541 [0.477, 0.613], IQM=0.525 [0.437, 0.620], median=0.503

## Implications for paper
1. C3 contribution is weak (not significant). Consider reframing as "credit assignment explored, no significant gain."
2. Stress regimes are the real contribution: prevent collapse, improve CK.
3. Residual MAPPO (BC init) may be the headline result if full runs confirm smoke test.
4. Network certificate (C1) is solid and novel.
5. C4 (fair evaluation) is the methodology contribution.
