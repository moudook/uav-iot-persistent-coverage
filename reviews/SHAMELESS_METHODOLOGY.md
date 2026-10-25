# Shameless Methodology Review

## 1. Missing baselines/controls — MAJOR (SUSPECTED)
- file:line: Mlawn-midsem-tex.tex:460 (gap statement); ml_impl/uav_wireless/baselines_rl.py
- quoted: "A hand-designed reactive rule outperforms the learned controller by 0.298..."
- attack: No IL/BC, no single-agent PPO, no random policy, no greedy-with-memory, no tuned rule. Only one hand-designed reactive rule as the strong baseline. A reviewer will demand an IL/BC upper bound and a random policy floor.
- evidence: inspect baselines_rl.py for list of baselines; check if random policy exists.

## 2. Sample size / power — MAJOR (CONFIRMED)
- file:line: Mlawn-midsem-tex.tex:1860
- quoted: "5 evaluation scenes it varies by 0.098"
- attack: 8 training seeds, 5 eval scenes. Detectable effect size for paired t with n=8 at alpha=0.05 is ~1.1 Cohen's d -> ~0.11-0.13 in coverage units, comparable to reported gaps. Marginal power. "No significant difference" claims risk being underpowered.
- evidence: power analysis script.

## 3. Statistical test choice — MAJOR (SUSPECTED)
- file:line: Mlawn-midsem-tex.tex:2348
- quoted: "The comparison is paired: a difference is measured on the same training..."
- attack: Normality not stated/tested; multiplicity: Bonferroni mentioned but only after the fact; 134 tests claimed (tokNTests=134) but correction only over 6. Family-wise error across 134 uncontrolled.
- evidence: grep for normality/Shapiro.

## 4. Feasibility certificate — MAJOR (SUSPECTED)
- file:line: Mlawn-midsem-tex.tex:499
- quoted: "N >= 4K and is tight at the reported parameters"
- attack: Is it a bound or a measurement? The sensor-set instance excludes N=5 for 13% of random draws — so the "certificate" is probabilistic, not a proof. Assumption of disc geometry may not hold in simulated runs (links, not discs).
- evidence: feasibility.py.

## 5. Information asymmetry — MAJOR (CONFIRMED)
- file:line: Mlawn-midsem-tex.tex:2145
- quoted: "adding the agent identity ... full observation of the proposed configuration"
- attack: Heuristic gets exact deficit set; policy gets 4x4 map. Quantified partially via arms but the asymmetry itself (exact set vs coarse map) is never isolated as a baseline. A fair comparison would give the heuristic the same 4x4 map.
- evidence: check baselines.

## 6. Training budget — MAJOR (CONFIRMED)
- file:line: Mlawn-midsem-tex.tex:1910
- quoted: "the sweep has not saturated"
- attack: 25 episodes x 2000 steps; curve still rising; "lost" may mean "not yet trained". Paper admits non-saturation but still excludes budget as explanation only over range.
- evidence: hist_base.json learning curve.

## 7. Ablation pairing — MINOR (CONFIRMED)
- file:line: Mlawn-midsem-tex.tex:2318
- quoted: "Every variant is trained on the same configuration... same training seeds"
- attack: Intervals paired on same training seed — stated. But stress table shows components not separated; "component helps" claim only for under-coverage term. OK. Minor: worst resolution 0.042 > some deltas.
- evidence: results_ablation.csv.

## 8. Determinism claim — MINOR (SUSPECTED)
- file:line: Mlawn-midsem-tex.tex (tokDeterminismText)
- quoted: "all 170 of the compared values agreed exactly"
- attack: 170/170 identical on scenario matrix; but unshipped scen_old.csv not checked; reproducibility across hardware not tested. Sufficient for determinism of code but not of results pipeline.
- evidence: determinism_check.json.

## 9. Device claim — MAJOR (SUSPECTED)
- file:line: Mlawn-midsem-tex.tex:1980
- quoted: "The device and the ... not a paired comparison at all."
- attack: CPU only, 1.26x slower than GPU asserted; device_sensitivity logs exist but merge not clearly reported. Is 1.26x a measurement or assertion?
- evidence: device_sensitivity.json.

## 10. "We did X" not done — BLOCKER (SUSPECTED)
- file:line: Mlawn-midsem-tex.tex:460
- quoted: "automated claim audit (38 items, 0 failing)"
- attack: Audit does not audit Section VIII results. Claim audit counts pass but scope excludes results. A reviewer reads 0 failing as full validation.
- evidence: claim_audit.py scope.

## Additional
- n/a baselines for random policy.
- Gap CI [0.248,0.349] unpaired? Actually paired over 8 seeds — stated.
- Pack endurance 600s etc.

Write file.
