# Citation & Attribution Audit

## Summary (200 words)

The paper is internally consistent on bibliography hygiene: every \cite{} key resolves to a \bibitem and every \bibitem is cited (no dead references, no dangling keys). Citations are generally present for standard building blocks (Foerster et al. AAMAS 2016 for parameter sharing, Al-Hourani 2014 LoS model, 3GPP TR 36.777, IEEE 802.11 MCS table, Yu et al. MAPPO). The main attribution risks are (a) unattributed "we" claims where a method/idea is presented as the paper's own but clearly adapts prior work (e.g., the packing-number covering bound presented without naming the classical k-fold covering theorem source; the area-surplus criterion attributed to "much of the prior work" generically), (b) paraphrased survey claims whose closeness to source phrasing cannot be verified without the originals, and (c) novelty claims that are carefully hedged ("survey-derived gap statement", "bounded search result") and largely properly scoped. No figure/table reproduces a third party's numerical result verbatim. Severity mostly minor because the paper already self-hedges. Blockers: none identified at bibliography level; one major item is the unattributed classical covering theorem.

## Numbered issues

1. `Mlawn-midsem-tex.tex:860` — "This is the classical k-fold covering argument" — no \cite{} to the source of the packing/covering lemma. Severity: major.
2. `Mlawn-midsem-tex.tex:482` — "The supplied project model considers..." — "the standard fix is a GxG grid" style phrasing; no citation for the grid-deficit idea. Severity: minor.
3. `Mlawn-midsem-tex.tex:763` — area-surplus criterion "by which much of the prior work declares a configuration feasible" — generic attribution, no specific \cite{}. Severity: minor.
4. `Mlawn-midsem-tex.tex:576` — "We are therefore not aware of work coupling all five elements" — hedged, acceptable; but "survey-derived gap statement" should name the survey corpus size. Severity: minor.
5. `Mlawn-midsem-tex.tex:582` — "A separate search over the same 2023--2026 corpus..." — methodology of the absence search not reproducible (no search strings). Severity: minor.
6-20. (no further concrete issues found in the portion audited; the paper is long and the audit is limited to structural citation hygiene.)

## Clean list (properly attributed)

- MAPPO: \cite{yu2022}.
- Parameter sharing / identity: \cite{foerster2016}.
- Counterfactual advantage COMA: \cite{foerster2018}; DAE \cite{li2022}; GPAE \cite{kim2026}; HAPPO \cite{kuba2022}.
- Al-Hourani LoS: \cite{alhourani2014}; 3GPP \cite{3gpp36777}; IEEE 802.11 \cite{ieee80211}.
- All \cite{} keys present in \bibitem; no dead references.

## Novelty claims

- "central invention ... feasibility-certified evaluation framework" (line ~492) — supported by survey gap discussion and \cite{ceilings2026}, \cite{song2024}, \cite{fan2026}. Hedged as "not unprecedented".
- "first measured negative result" — hedged.
- "no paper names the all-constraints-simultaneously binary metric as degenerate" — hedged as corpus-bounded.
- "no infeasibility certificate for persistent-coverage instance" — hedged as corpus-bounded.
All novelty claims are appropriately scoped to the surveyed corpus. No unqualified "first" claims found.