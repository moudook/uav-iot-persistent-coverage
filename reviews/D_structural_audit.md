# Structural & Citation Audit

## Summary (150 words)
Automated audit of the full TeX source: all 44 \cite{} keys resolve to 44 \bibitem entries, with no dead references; all 10 figures and 20 tables are referenced via \ref{}; all 46 \ref{} targets resolve. No pending macros found. However, 40 \label{} entries are orphaned (equations/sections never referenced), including sec:litsurvey and sec:coverage. Bibliography formatting appears consistent. Claims of novelty ("we are not aware of work coupling all five elements") are hedged and supported by near-miss table. No obvious paraphrase without citation detected in sampled sections. Main structural issues are unreferenced labels and a few sections never cited. No blocker-level citation defects found.

## Issues
1. file:line Mlawn-midsem-tex.tex:~637, text "\label{eq:decpomdp}", severity minor, SUSPECTED - orphaned label never referenced.
2. file:line ~753, text "\label{eq:Ct}", severity minor, SUSPECTED.
3. file:line ~758, text "\label{eq:Ut}", severity minor, SUSPECTED.
4. file:line ~710, text "\label{eq:actions}", severity minor, SUSPECTED.
5. file:line ~516, text "\label{sec:litsurvey}", severity minor, SUSPECTED - section never referenced.
6. file:line ~739, text "\label{sec:coverage}", severity minor, SUSPECTED.
7. file:line ~594, text "\label{fig:arch}" referenced yes - OK.
8. (remaining orphaned labels listed in aggregate) severity minor.

## Checked and found correct
- All 44 cite keys resolve to bibitems; no dead bibitems.
- All 10 figures referenced.
- All 20 tables referenced.
- No pending macros.
- Bibliography author/year formatting consistent in sampled entries.
- Novelty claims hedged with corpus bounds.
Return same content.