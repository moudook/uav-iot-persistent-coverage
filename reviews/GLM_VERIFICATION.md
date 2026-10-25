# GLM VERIFICATION — adversarial fact-check of `Mlawn-midsem-tex.tex`

Method: read the full .tex (all 2975 lines) top to bottom; every macro-tracked number was recomputed from the artefact it cites (`results_scenarios.csv`, `results_ablation(_stress).csv`, `claim_audit.json`, `determinism_check.json`, `phy_equivalence.json`, `phy_validation.json`, `phy_runtime_probe.json`, `infeasible_instance.json`, `corner_transfer.json`, `dormancy.json`, `ab_map_resolution.json`, `connectivity_accounting.json`, `alt_deployment.json`, `ab_energy_management.json`, `ab_credit.json`, `ab_budget.json`, `ab_observation.json`); every `\cite` key was checked against the 44 `\bibitem`s; five external references were spot-checked against their sources (web, arXiv full text). No files were modified except this one.

---

## Summary verdict (≤200 words)

The paper is **clean of fraud**. Every load-bearing number I could recompute from the repository's artefacts matched exactly: all paired 95% intervals in the ablation, stress-ablation, energy, credit, budget, observation, map-sweep and alternative-deployment experiments; all 9 scenario row means; all 34 per-variant deficits and their extremes (−0.598 S6 / −0.080 S2); the claim-audit counts (38/34/4/0); determinism (170/0); the PHY algebraic-equivalence delta (0.012 dB over 24 rows); the link margins (+43.2/+46.9 dB, hand-recomputed); the infeasibility-teaser numbers (0.648/1.000/0.990); corner-transfer, dormancy, map-resolution and connectivity-accounting figures. All `\cite` keys resolve. The `ceilings2026` quote and the `prime2026` 40–45% figure are verbatim/accurate against the cited works.

However, verification found **two confirmed figure/artefact inconsistencies** (a stale `fig:scen` plot disagreeing with the CSV for 26 of 34 markers, and a hardcoded, unreproducible "13.7 dB"), **one wrong attributed number** (`fan2026` "74%"), and several minor prose/bibitem defects. One attributed number (`song2024` 81.0%/67.1%) could not be verified in either direction. None of these overturn any conclusion, but `fig:scen` and its caption still disagree with each other and must be regenerated before submission.

---

## Findings (each quotes exact text; evidence filenames given)

### F1 — [major, CONFIRMED] `fig:scen` is stale: markers contradict the artefact its own caption cites
- **File:line:** `Mlawn-midsem-tex.tex:2585` (in-figure marker coordinates); caption at `:2590`; identical duplicated source `ml_impl/analysis/fig_scen.tex:24`.
- **Quote:** `"(1,-0.304) (2,-0.434) ... (5,-0.071) ... (11,-0.528) ... (21,-0.598) ... (30,-0.519) ... (33,-0.177)"` vs caption `"It is behind the stronger rule in \tokScenLosses{} of the \tokScenVariants{} variants, by between \tokScenSpanMin{} and \tokScenSpanMax{} of persistent coverage"`.
- **Objection:** Recomputing the 34 variant deficits (learned minus stronger rule) from `ml_impl/results_scenarios.csv` gives a minimum magnitude of 0.080 (`S2`, −0.080) and maximum 0.598 (`S6`), matching the caption macros — but **26 of the 34 figure markers disagree with the CSV** (all >0.005), e.g. marker 2 −0.434 vs CSV −0.383; marker 5 −0.071 vs CSV −0.080; marker 11 −0.528 vs CSV −0.485; marker 16 −0.331 vs CSV −0.293. The figure contains a marker at **−0.071**, i.e. a variant shown as behind by only 0.071, which is *outside the caption's own stated range [0.080, 0.598]* — figure and caption contradict each other on the page. Timestamps confirm the cause: `fig_scen.tex` was generated 22-10 12:29, while `results_scenarios.csv` was re-written 22-10 18:05 (run `q3_scen` ended 18:05) and the macros were (re)filled later. The figure was rendered from a pre-final scenario run and never regenerated.
- **Status:** CONFIRMED (recomputation script evidence: `%TEMP%\opencode\verify6.py`).

### F2 — [major, CONFIRMED] The "13.7 dB" path-loss spread is hardcoded and is not reproducible from the probe's own parameters
- **File:line:** `Mlawn-midsem-tex.tex:2751–2753`.
- **Quote:** `"although the configured path loss differs by 13.7~dB between the nearest and the farthest of them, and the link-closure threshold is the same at every distance when the configured path loss requires it to be 13.7~dB lower at 80~m."`
- **Objection:** The number is carried as **plaintext strings**, not computed values, in `phy_runtime_probe.py:182` and `:195` (`f"(the configured path loss differs by 13.7 dB)"`) and echoed into `phy_runtime_probe.json:66,73` — no code path computes it. Recomputing from the probe's *own* parameter set (`phy_runtime_probe.py:68–73`: L01 = 40.04 dB, ALPHA = 2.0 across all distances per `:109`, UAV at Z0 = 50 m, receivers at flat 10 → 80 m, and the script's own 3-D slant conversion `d3 = sqrt(h²+50²)` at `:161`): the configured path-loss spread between the nearest (slant 50.99 m → PL 74.19 dB) and the farthest (slant 94.34 m → PL 79.52 dB) receiver is **20·log10(94.34/50.99) = 5.34 dB**; with flat 2-D distances it is **20·log10(80/10) = 18.06 dB**. Neither is 13.7 dB, and searching the whole project tree for "13.7" finds it only as prose/strings, never as a computed quantity. The qualitative conclusion (the statistic does not track distance) is unaffected, but the one quantitative justification for it is unsupported.
- **Status:** CONFIRMED (numeric), recomputed by hand from `phy_runtime_probe.py`'s printed geometry.

### F3 — [major, CONFIRMED] Number attributed to `fan2026` does not appear in that work in the claimed configuration
- **File:line:** `Mlawn-midsem-tex.tex:560`.
- **Quote:** `"Reports 74\% coverage with five UAVs and ten nodes, against an offline MILP upper bound, i.e.\ with an achievability reference."`
- **Objection:** The cited paper (arXiv:2603.16141v2, Fan et al., *Communication-Aware MARL for Cooperative UAV Deployment*) reports, at M=5, N=10, coverage of **0.76±0.02 (RC+PO), 0.77 (RC+FO), 0.78 (UC+PO), 0.79 (UC+FO)** with the MILP reference at **0.84** (its Table II). Its **0.74** value belongs to a *different* configuration: M=3, N=6, RC, FO. So "74% with five UAVs and ten nodes" attributes the wrong row; the correct five-UAV number under restricted communication and partial observability is 76%, and the correct MILP upper-bound reference value at (5,10) is 0.84, which actually *strengthens* the "achievability reference" framing the table is making. The paper's qualitative description (MILP upper bound, five UAVs, ten nodes) is otherwise accurate.
- **Status:** CONFIRMED against arXiv:2603.16141v2 full text.

### F4 — [minor, CONFIRMED] `fan2026` bibitem omits a co-author
- **File:line:** `Mlawn-midsem-tex.tex:2962`.
- **Quote:** `"E. Fan, Y. Chen, Z. Shan, M. Caesar, and J. Kim, ..."`.
- **Objection:** The actual author list is **Enguang Fan, Zihan Shan, Yifan Chen, Klara Nahrstedt, Matthew Caesar, Jae Kim** (six authors). The bibitem drops K. Nahrstedt and reorders Chen before Shan. Everything else (title, arXiv:2603.16141, 2026) is correct.
- **Status:** CONFIRMED.

### F5 — [minor, CONFIRMED] The `lee2026` numbers are real but are used out of their experimental context
- **File:line:** `Mlawn-midsem-tex.tex:582`.
- **Quote:** `"The closest empirical demonstration is in \cite{lee2026}, which reports a feasible rate of 0\% over ten solver executions alongside a mean $k$-coverage ratio of 33.33\%: the binary flag is zero while the graded quantity is substantial"`.
- **Objection:** The numbers are verifiable — in arXiv:2609.01930 (Lee et al.), the Supplementary C-D2 penalty-sensitivity study states: *"an infeasible BoS solution was retained in every execution, yielding a feasible rate of 0% and a mean 3-coverage ratio of 33.33%"*, at penalty coefficient **λ=0.25, i.e. below the derivation's own exactness threshold λ>|W|** (0% (0/10), 33.33%±11.11). That is a deliberately mis-tuned hyperparameter, not instance infeasibility: the same paper's actual evaluations report 90% feasible-run rate / 99.3% 3-coverage (hardware) and 100% feasible (simulator). The sentence's framing as "the closest empirical demonstration" of binary-metric degeneracy never tells the reader that the 0%-feasible run was produced by a penalty coefficient the same paper proves is insufficient — a materially different mechanism from "the all-constraints metric collapses on an infeasible instance". Honest use, but the context is a one-clause omission away from misleading.
- **Status:** CONFIRMED (numbers); characterization is the objection.

### F6 — [minor, SUSPECTED] Numbers attributed to `song2024` could not be verified
- **File:line:** `Mlawn-midsem-tex.tex:559`.
- **Quote:** `"Reports MPC and MCTS at 81.0\% and 67.1\% of the MILP optimum, i.e.\ against an achievability reference."`
- **Objection:** The reference (`Song, Chin, Yang, Ros, IEEE TMC vol. 23 no. 4, 2024, doi 10.1109/TMC.2023.3259461`) is a paywalled journal article; no preprint, copy, or abstract quoting these figures was reachable, and the numbers do not appear in any local artefact in this repository (the local research corpus `research/09_REFERENCES_VERIFIED.md` predates the citation list and does not cover song2024). The bibitem itself is plausibly real (authors, venue, volume OK). The attributed figures are therefore **unverified in both directions** — they may well be correct, but nothing auditable in the project supports them.
- **Status:** SUSPECTED.

### F7 — [minor, CONFIRMED] Rounding divergence between `claim_audit.json` PH3 and the paper's verified margin
- **File:line:** `claim_audit.json:244` vs `Mlawn-midsem-tex.tex:2690`.
- **Quote (artefact):** `"measured": "46.8 dB (SNR 48.8 dB vs threshold 2.0 dB)"` (audit item PH3). **Paper:** `"is $+46.9$~dB (inter-UAV link, 40.0~m)"`.
- **Objection:** The paper's +46.9 dB is the correct value (recomputed by hand: PL(40 m) = 40.04 + 20·log10(40) = 72.08 dB; SNR = 27 − 72.08 − (−93.99) = +48.91 dB; margin = +46.91 dB), so the *paper* is right and the *audit artefact string* carries a stale/rounded 46.8/48.8. Strictly the artefact diverges from reality, but the paper's headline validation-claim ("recorded by the OMNeT++ run the two agree to 0.012 dB") is distinct and verified. Flagged so that regenerating the audit does not reintroduce a mismatch.
- **Status:** CONFIRMED (against the recomputation and `phy_validation.json`-derived margins).

### F8 — [minor, CONFIRMED] `phy_runtime_probe.json` mislabels dBW values as "tx_dbm"
- **File:line:** `phy_runtime_probe.json:6` (and `phy_runtime_probe.py:147`).
- **Quote (artefact):** `"tag": "0.5W", "tx_w": 0.5, "tx_dbm": -3.010299956639812` — and note strings `"the link is open at -3 dBm and closed at -60 dBm"`.
- **Objection:** −3.01 is dBW (10·log10(0.5)), not dBm; 0.5 W is +27 dBm, exactly as the paper's Table `tab:phyprobe` (`Mlawn-midsem-tex.tex:2736–2739`) correctly prints (+27, 0, −30, −90 dBm) and 10·log10(tx) is reused for the "delta TX" check, where the label cancels. No number in the paper is affected; the artefact's *key name and note strings* are wrong, which matters because `claim_audit.py`/future readers may consume them as dBm.
- **Status:** CONFIRMED.

### F9 — [minor, CONFIRMED] Garbled geometry sentence (underlying claim holds)
- **File:line:** `Mlawn-midsem-tex.tex:875`.
- **Quote:** `"the corner separations are $80$\,m and the side is $80\,\mathrm{m}>2R_{\mathrm{cov}}=70$\,m"`.
- **Objection:** As written this is a tautology/word-salad: the side being 80 m is *why* adjacent corner separations are 80 m; "corner separations are 80 m" alone is wrong for the diagonal, which is 80√2 = 113 m. What the argument needs — and what the sentence should say — is that *each separation between distinct corners* (80 m adjacent, 113 m diagonal) exceeds 2R_cov = 70 m, so no disc can cover two corners. The underlying claim (P(Ω, R) = 4, four pairwise-disjoint corner discs, 40×40 sub-squares with diameter 56.6 m < 70 m) is correct, as is the packing bound K·4 = 8.
- **Status:** CONFIRMED (text defect, math intact).

### F10 — [minor, CONFIRMED] `tokArmsSummarySentence` final clause reads as wrong baseline pairing
- **File:line:** macro at `Mlawn-midsem-tex.tex:139`, expanded at `:494` and `:2821`.
- **Quote:** `"Every interval is paired over the same training seeds, against the local-only arm A of the observation experiment and the proposed configuration of the energy experiment."`
- **Objection:** As expanded, this says every arm's interval is paired "against the local-only arm A ... and the proposed configuration of the energy experiment", which is false as a universal claim — e.g. the credit arm is paired against the full proposed controller, the energy arms against the full energy rule, the identity/observation arms against their own modified baselines. The intended meaning (each arm is paired per-seed, against the configuration it modifies, on the same eight training seeds) is verified true in the artefacts (`results_ablation(_stress).csv`, `ab_credit.json`, `ab_energy_management.json`, `ab_observation.json` — all 17 intervals recomputed and correct), but the sentence's "against A ... and ..." construction names two baselines once and attaches them to every arm. A reader reconciling arms to baselines gets the wrong map.
- **Status:** CONFIRMED (as a wording defect; the numbers behind every interval it summarizes are verified correct).

### F11 — [minor, CONFIRMED] Dropped relative pronoun in the abstract section (garbled)
- **File:line:** `Mlawn-midsem-tex.tex:460`.
- **Quote:** `"The residual is also consistent with causes the arms do not test --- the possibility that the rule was tuned against the evaluation scenes, the limit of a decentralised policy class --- and we do not claim to have excluded them."`
- **Objection:** "consistent with causes the arms do not test" is missing a "that"/comma construction ("causes *that* the arms do not test"); the same sentence at `:2821` is correctly written "with causes that these arms do not test". Cosmetic, in a high-visibility abstract-adjacent position.
- **Status:** CONFIRMED.

---

## Clean bill — checked and correct

**Recomputed, exact match (artefact → paper):**
1. Main comparison: MAPPO CK 0.674±0.060 (σ_SD over 8 seeds), Reactive-local 0.972, Reactive 0.953/1.000/0.753, Greedy 0.784/0.965/0.066, Fixed 0.372/1.000/0.000, Independent DQN 0.381±0.069, Masked PPO local-critic 0.625±0.054, argmax 0.418, oracle 1.000.
2. Gap 0.298 CI [0.248, 0.349] (paired over 8 seeds, `results_scenarios.csv`-independent comparison CSV).
3. Ablation table: no-undercoverage +0.097 CI [+0.020, +0.174] p=0.020 n=8, and all sibling intervals.
4. Stress-ablation table: all 12 row CK values recomputed exactly (Full 0.303 … VanillaMAPPO 0.484); paired intervals no-reserve −0.190 [−0.277, −0.104]; no-mask +0.050 [+0.006, +0.094]; whole-design −0.181 [−0.255, −0.107]; all zero-inclusive intervals including the ±0.000 double-rounded display of [−0.000, +0.000].
5. Energy arms A–D variant-minus-full intervals and repair arm +0.050 [−0.015, +0.115]; credit arm +0.035 [−0.009, +0.079] (paper's sign convention −0.035 [−0.079, +0.009] internally consistent).
6. Budget arm +0.086 [+0.036, +0.135] p=0.004; budget sweep 0.588/0.624/0.674.
7. Observation arms B +0.008 [−0.121, +0.137]; C +0.034 [−0.033, +0.102]; identity + independent-agent claims.
8. Map resolution: G=0/4/8 → 0.640/0.643/0.651; spreads 9.0/10.6/10.3 m; largest difference 0.011.
9. Alternative deployment: ('N5R45' − 'N8R35') +0.083 [+0.017, +0.149] p=0.021; learned 0.757 vs 0.674.
10. Scenario matrix Table `tab:results_scen`: all 9 row means (S1–S9 × M/R/RL × CK & SC) recomputed exact; 34 of 34 deficits negative, min −0.598 (S6), max −0.080 (S2) — caption macros correct (the figure is the only stale element, F1).
11. Claim audit: exactly 38 items, 34 PASS, 4 INFO, 0 FAIL = paper's 38/34/4/0.
12. Determinism: 170 values compared, 0 differing = "all 170 agreed exactly".
13. PHY equivalence: 24 rows, worst |Δ| = 0.012 dB = `\tokPhyDelta`.
14. Link budgets: 0.5 W = +27 dBm; noise −93.99 dBm; PL(61.0 m) → margin +43.24 ≈ +43.2 dB; PL(40.0 m) → +46.91 ≈ +46.9 dB (paper right; audit string drift is F7).
15. Probe table: receptions 500/500/0/0 and SNIR 46.96/19.97 dB per `phy_runtime_probe.json`; the 117 dB TP-sweep range (+27 → −90 dBm) arithmetically exact; "27.0 dB → 27.0 dB" and the open/closed-at-same-threshold observations match the artefact's checks.
16. Teaser/infeasibility pilot: mean rule CK 0.648, AG 1.000, SC 0.000, oracle 0.990 — body text and figure text use each number in the right place.
17. Corner transfer: cap 5.0 m, fraction 0.003068 → "0.31%", probability 9.34e-6 → "9.3e-6".
18. Dormancy probe: L0/L1 dormant_frac 0.0 at all thresholds 1e-3…1e-1; silent 9.4%–21.1%; dead 0; per-agent-only-dormant 0 — all as written.
19. Connectivity accounting: 4 disconnected transitions, 4 after active-set change, 0 teleport, 0 unexplained.
20. Feasibility: σ = NπR²/(KA) = 1.5033 at N=5, K=2, R=35, A=6400 m² → "1.50"; area bound 28.5 m; packing-corrected 29.97 → "30.0 m" (δ = π/(2√3) ≈ 0.907); N ≥ 4K = 8; 40×40 sub-square diameter 56.6 m < 70 m.

**Citations:**
21. All `\cite` keys resolve to `\bibitem`s; 44 bibitems present, none dangling.
22. `ceilings2026` (arXiv:2610.20823): the quoted sentence appears **verbatim** in its abstract ("we argue such ceilings should be computed before any learning experiment and quoted alongside every result"); the drone-mesh-interception description and the author are accurate.
23. `prime2026` (arXiv:2607.17922): "40–45% dormant for vanilla MAPPO" appears verbatim in its abstract ("holds dormant neuron fractions at 10–20% versus 40–45%"); authors (Qiu, He, Zhao, Masui) and ID correct.
24. `lee2026` (arXiv:2609.01930): the quoted 0% (0/10) and 33.33% figures genuinely appear in the paper (context caveat = F5, not a fabrication).
25. `fan2026` (arXiv:2603.16141): exists; the MILP-upper-bound framing of its evaluation is accurate (only the specific number is off, F3).
26. Standard-library citations were present and plausible (3GPP TR 36.777, IEEE 802.11-2016, alhourani2014, foerster2016/2018, kuba2022, dewitt2021, schulman-style PPO refs, etc.).

---

## Bottom line
Order of severity: dispatch order. F1 (stale figure vs its own caption) and F2 (unsupported 13.7 dB) must be fixed before submission; F3 is a one-row correction to the survey table; everything else is minor prose/annotation hygiene. **No evidence of fabricated results — every number that claims to come from an artefact did come from that artefact, except the standalone figure under F1.**
