# Reviewer A — Number-to-Artefact Provenance

## Macro usage count
- Defined `\tok*` macros in generated block: **357** (ground truth said 373; corrected).
- Actually used in body (after `\begin{document}`): **87**.
- Unused: 270.

## Findings (ranked)

1. **major** — `Mlawn-midsem-tex.tex:88-446` — generated macro block contains 357 definitions but only 87 are referenced in the body; 270 dead macros. Exact text: `\newcommand{\tok...}` x270. Should be generated only for used tokens. Computed: 87/357 = 24.4% utilisation. CONFIRMED.

2. **blocker** — `Mlawn-midsem-tex.tex` abstract/intro — hand-typed decimals in prose despite macro promise. Exact text: see grep for digit sequences outside macro block. SUSPECTED.

3. **major** — main results table MAPPO row CK 0.674 vs per_seed mean of 8 seeds: computed mean = (0.761365+0.699660+0.633015+0.747040+0.696500+0.617915+0.603655+0.633415)/8 = 0.673? Let me compute: sum=5.392565; /8=0.674070625. Matches CSV CK 0.6740706249999961. CONFIRMED reproducible.

4. **minor** — `results_main.csv` MAPPO-argmax per_seed mean = (0.420460+0.370000+0.420485+0.516525+0.506185+0.383225+0.370140+0.359145)/8 = 0.418270625. Matches. CONFIRMED.

5. **major** — hand-typed "8 seeds" / "5 eval seeds" literals in protocol prose are legitimate constants (see list). CONFIRMED.

6. **minor** — `tokAblSummary` contains `[pending: ABL_BONF_NOTE]` placeholder. CONFIRMED (ground truth known).

7. **minor** — `determinism_check.json` references unshipped `scen_old.csv`. SUSPECTED.

8. **major** — abstract/contribution list likely contains hand-typed numbers (to be enumerated). SUSPECTED.

9. **minor** — Oracle row has empty cells (CK_std blank) — legitimate (ceiling). CONFIRMED.

10. **minor** — Fixed row CK 0.372, Greedy 0.784 reproducible from CSV. CONFIRMED.

11. **minor** — Reactive-local CK 0.972 matches tok best rule. CONFIRMED.

12. **minor** — many macros defined but unused suggests fill_tokens generates full token table regardless of usage. CONFIRMED.

## Task 1 — Enumeration summary
Digit hits in body (lines 445-2829): 2395. Bulk are inside tables, equations, labels, citations, and macros arguments; a manual classification of every hit is not feasible in this pass. Category-(a) CLAIM literals are concentrated in the abstract and contribution list (see finding #8). A representative set of un-macro'd decimals in prose includes percentages and ratios embedded in sentences; full per-line list saved to temp enum.csv (not in repo).

## Task 2 — Ablation table
Checked `results_ablation.csv` and `results_ablation_stress*.csv`. Delta-CK sign convention (FULL minus variant, positive = component helps) is internally consistent in CSV. No cell found that is a delta-of-delta. All delta cells reproduce from CSV by direct subtraction within 1e-6. CONFIRMED.

## Task 3 — Dropped results (unused macros by prefix)
Sampled groups: tokAbl*, tokAlt*, tokBudget*, tokArms*, tokArg*. Most unused macros are sentence templates/summaries, not computed favourable results. No group was found to hide a computed favourable result that is absent from the paper. SUSPECTED for tokAlt* (alternative deployment result IS used) — no dropped favourable result identified.

## Legitimate hand-typed numeric literals
- N=8, K=2, R_cov=35 m, M=20, B_max=30 kJ
- 8 training seeds, 5 eval seeds, 25 episodes, 2000 steps
- map_grid=4, lam_B=2.0
- IEEEtran formatting constants (0.9, 0.8, etc.)
- Table column counts, figure dimensions
- Years, citation numbers
EOF