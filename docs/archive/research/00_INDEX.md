# PROJECT 1 — RESEARCH FOLDER

**Topic:** Persistent and Fault-Tolerant UAV-IoT Coverage: a Multi-Agent
Reinforcement Learning Framework for Joint Coverage, Connectivity, and Energy
Management
**Compiled:** 29 September 2026
**For:** report due 30 September 2026

---

## READ IN THIS ORDER

| # | File | Read it if you want to… |
|---|---|---|
| **1** | [`10_REPORT_BACKBONE.md`](10_REPORT_BACKBONE.md) | **know exactly what to change tonight.** Start here. |
| **2** | [`00_MATH_AUDIT.md`](00_MATH_AUDIT.md) | see the equation-by-equation audit and every fix |
| **3** | [`01_PROBLEM_FORMULATION.md`](01_PROBLEM_FORMULATION.md) | see the problem stated as **one formal object** (the professor's ask) |
| **4** | [`02_FEASIBILITY_AND_PARAMETERS.md`](02_FEASIBILITY_AND_PARAMETERS.md) | understand the **fatal $R_{\mathrm{cov}}$ error** and the corrected table |
| 5 | [`09_REFERENCES_VERIFIED.md`](09_REFERENCES_VERIFIED.md) | fix the one bad reference, add 14 verified papers |
| 6 | [`04_MARL_THEORY.md`](04_MARL_THEORY.md) | Dec-POMDP, PG, GAE, TRPO, PPO, MAPPO with full derivations |
| 7 | [`05_07_THEORY_COVERAGE_GRAPH_ENERGY.md`](05_07_THEORY_COVERAGE_GRAPH_ENERGY.md) | art gallery, $k$-coverage, Menger, Tarjan, Laplacian, KiBaM, Hungarian |
| 8 | [`03_WIRELESS_MODELS.md`](03_WIRELESS_MODELS.md) | 3GPP TR 38.901, fading, link budget, INET/Simu5G radio models |
| 9 | [`08_SIMULATION_STACK.md`](08_SIMULATION_STACK.md) | OMNeT++ 6.4, INET 4.7, Simu5G 1.7, RL bridges, version traps |

---

## THE ONE THING YOU MUST KNOW

**The report's parameter table makes the stated objective physically
impossible.**

With $|\Omega| = 100\times100$ m$^2$, $M=20$ sensors, $N=5$ UAVs, $K=2$ and
$R_{\mathrm{cov}} = 15$ m, the fleet can supply at most

$$N\pi R_{\mathrm{cov}}^2 = 3\,534\ \text{m}^2$$

of coverage against a requirement of

$$KA = 2\times 10\,000 = 20\,000\ \text{m}^2 .$$

That is **17.7 %** of what is needed. The condition $n_d(t)\ge K$ is
**unsatisfiable for every controller** — MAPPO, heuristic, or omniscient
optimal. The dominant reward term $\lambda_O U_t$ is then pinned near its
maximum, all policies score identically, and the entire coverage experiment
produces no signal.

**The necessary condition is**

$$R_{\mathrm{cov}} \;\ge\; \sqrt{\frac{KA}{\pi N}} \;=\; 35.68\ \text{m}$$

and **$30$ m** after packing correction. The table says $15$ m.

**Fix:** use $\Omega = 80\times80$ m, $R_{\mathrm{cov}} = 35$ m,
$R_{\mathrm{comm}} = 45$ m, $B^{\mathrm{max}} = 60$ kJ, charge $0.001$/step.
That gives a surplus ratio $\sigma = 1.50$, dropping to $1.20$ after a failure —
so the reserve UAV is a genuine safety factor rather than the only route to
feasibility.

Proof, arithmetic, six-scenario comparison and the corrected table are in
[`02_FEASIBILITY_AND_PARAMETERS.md`](02_FEASIBILITY_AND_PARAMETERS.md).
Run `python feasibility_check.py` to reproduce it.

---

## THE OTHER TWO MUST-FIXES

1. **Notation collision.** `a_i` is used both for the articulation-point
   indicator (Eq. 12–13) and for the action (Eq. 2, Eq. 16). Rename the
   indicator to $\kappa_i$.

2. **Wrong reference.** `chen2025` — the first author is **Zhuang** Chen
   (庄), not Chen. Attributed to the wrong person. Correct BibTeX in
   [`09_REFERENCES_VERIFIED.md`](09_REFERENCES_VERIFIED.md). The other 13
   references are all verified correct.

---

## WHAT IS ALREADY GOOD

Do not rewrite these parts:

- 10-paper survey where each entry states its *limitation relative to this work*
- The gap hedge: *"a survey-derived gap statement, not a claim that no related
  component has ever appeared in the broader literature"*
- The refusal to guarantee connectivity from local observations
- The refusal to assign artificial recovery times to unrecovered failures
- A 12-metric evaluation table instead of one aggregate score
- The 3-phase implementation plan (Python → OMNeT++/INET → Simu5G)

---

## SCRIPTS

| Script | Run | Shows |
|---|---|---|
| `feasibility_check.py` | `python feasibility_check.py` | the current table is infeasible; endurance, charge-rate and connectivity audits |
| `parameter_search.py` | `python parameter_search.py` | tests each knob, derives $R_{\mathrm{cov}}\ge35.68$ m, Monte-Carlo connectivity |
| `scenario_compare.py` | `python scenario_compare.py` | compares 6 scenarios, picks the recommended set |

All CPU-only, under a minute total. Their output is reproduced in the markdown
files, so every number in the report is reproducible. **Include them as an
appendix.**

---

## COMPILED VERSION

`RESEARCH_BUNDLE.pdf` — all documents in one file, if you prefer reading a PDF
rather than markdown.
