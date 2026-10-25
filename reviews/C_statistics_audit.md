# Reviewer C — Statistics and protocol audit (orchestrator's own review)

## Recomputed headline table vs. the paper's

Recomputed from `ml_impl/results_main.csv` (per_seed_CK, 8 seeds):

| policy | n | mean (recomputed) | paper CK | sd ddof=0 (recomputed) | sd ddof=1 (recomputed) | paper CK_std |
|---|---|---|---|---|---|---|
| MAPPO | 8 | 0.674071 | 0.674071 | 0.056517 | 0.060419 | 0.060419 |
| MAPPO-argmax | 8 | 0.418271 | 0.418271 | 0.057839 | 0.061833 | 0.061833 |

Finding: the CSV's CK_std equals the *sample* sd (ddof=1), not the population sd (ddof=0). The paper's prose is claimed to use sample sd and the CSVs population sd, "disclosed" — but both use sample sd. The disclosure is therefore either absent or false. CONFIRMED by direct recomputation.

## Findings (ranked)

1. **blocker** — `Mlawn-midsem-tex.tex:1758,1819` — "seed-to-seed spread 0.064 (SE 0.037) ... 3 training runs" while Table XII uses 8 runs (0.674 ± 0.060). The variance-decomposition token pulls from a 3-seed `base_seed_rows.jsonl` instead of the 8-seed base artefact. CONFIRMED (recomputed: 8-seed std = 0.0604, SE = 0.0214, not 0.064/0.037). Fixed this session (tokVarSeed now 0.060, tokVarSeedSe 0.021, prose says 8 runs).

2. **major** — `Mlawn-midsem-tex.tex` gap interval — paired one-sample interval over the learned controller's training seeds, evaluation scenes held fixed. The 0.261 lower bound vs 0.199 Bonferroni-adjusted upper limit (older draft) is a paired-vs-unpaired comparison across different families; the multiplicity family is the observation arms, not the gap. The paper does not state the distributional assumption (normality of per-seed means) or the pairing explicitly in the same place as the number. SUSPECTED (did not re-derive the interval from per-seed values; needs fill_tokens inspection).

3. **major** — `Mlawn-midsem-tex.tex:2420` (Table XV ablation) — 12 rows, deltas are FULL minus variant (positive = component helps). Several intervals straddle zero (e.g. criticality −0.000 [−0.011, +0.010], degraded-service +0.010 [−0.035, +0.055], energy-cost +0.000 [−0.000, +0.000], under-coverage −0.010 [−0.060, +0.039]). The prose correctly says these "include zero" and does not claim an effect. CONFIRMED (read the table). The Bonferroni note is present but counts the arms as a family of paired tests.

4. **major** — `Mlawn-midsem-tex.tex:2669` — "feasibility certificate is audited, not asserted." The certified numbers (34.9 m worst-covered point, packing number 2.13 over 30 draws) are measurements of the simulator's geometry, not bounds. The covering bound N >= 4K is a bound; the audit numbers are measurements. The paper conflates the two. CONFIRMED (read 2669-2670).

5. **major** — power: with 8 training seeds and per-seed sd ~0.06, the detectable effect at two-sided 0.05 is roughly 0.06 (Cohen's d ~1.0) — i.e. only large effects are detectable. The ablation's null results ("no effect") are phrased as "not resolved by this arm" in some places and as "no effect" in others; the paper's own text at 2356 says "the widest of the arms resolves no effect smaller than about 0.042", which is the correct phrasing. CONFIRMED (2356).

6. **minor** — `ml_impl/analysis/determinism_check.json` — reports 170/170 identical, but names `scen_old.csv` (unshipped) as the "old" file. The claim is not reproducible from shipped artefacts. CONFIRMED (read the json).

7. **minor** — `Mlawn-midsem-tex.tex` artefact list — 9 paths referenced; all exist. CONFIRMED (checked).

8. **minor** — `ml_impl/results_main.csv` — the baseline rows (Fixed, Greedy, Reactive, Reactive-local) have no per_seed_CK, so their sd is not recomputable from the CSV; only MAPPO and MAPPO-argmax can be verified. SUSPECTED (may be in separate logs).

9. **minor** — `Mlawn-midsem-tex.tex:1725` Table XII — CovDef column was blank for the four rule-based rows (now populated: 0.628, 0.216, 0.047, 0.028 = 1-CK). CONFIRMED (fixed this session).

10. **minor** — `Mlawn-midsem-tex.tex:2088` — spread direction prose said "rises to 11.0 m" but 11.0 < 11.8 (Arm B). Fixed to "falls back to 11.0 m". CONFIRMED (fixed this session).

## Top 3 in full

1. **blocker — sample vs population sd disclosure is wrong.** Recomputation shows CK_std in results_main.csv equals the sample sd (ddof=1): MAPPO 0.060419 = std(ddof=1) of the 8 per-seed values. The paper claims the CSVs use population sd (ddof=0) and that this is "disclosed". It is not: both use sample sd. Either the disclosure is missing or the claim is false. Fix: state once, in the same sentence as the first reported sd, "standard deviations are sample (ddof=1) throughout, including in the CSVs." Evidence: results_main.csv MAPPO row, recomputed sd0=0.056517, sd1=0.060419, CSV=0.060419.

2. **major — the variance decomposition is on the wrong sample.** VAR_SEED (0.064, SE 0.037) and "3 training runs" come from base_seed_rows.jsonl, which holds a 3-seed run, while the headline is an 8-seed run. The fix (done this session) recomputes VAR_SEED from the 8-seed base table (0.060, SE 0.021). The scene decomposition (0.098, SE 0.044) is unaffected because it measures per-scene variation of a fixed controller. Evidence: fill_tokens.py lines 2280-2312, base_seed_rows.jsonl (3 rows, 1352 bytes), results_main.csv MAPPO per_seed_CK (8 values).

3. **major — certificate vs measurement conflation.** The paper reports "the feasibility certificate is audited, not asserted" and gives audit numbers (34.9 m worst-covered point, packing number 2.13 over 30 draws). Those are measurements of the simulator's geometry, not bounds. The actual bound is N >= 4K. A reviewer reading Section III and the audit paragraph together will ask which numbers are bounds and which are measurements, and the paper does not say. Fix: label each audit number explicitly as "measured" or "proved." Evidence: 2669-2670, 849-860.
