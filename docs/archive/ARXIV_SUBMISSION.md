# arXiv submission pack

## Files
- `Mlawn-midsem-tex.pdf` — the compiled paper (32 pages, 574 KB)
- `Mlawn-midsem-tex.tex` — the source (optional, for the arXiv LaTeX upload)

## Submission form

**Title (150 chars):**
`Persistent and Fault-Tolerant UAV-IoT Coverage: A Multi-Agent Reinforcement Learning Framework for Joint Coverage, Connectivity, and Energy Management`

**Authors (4):**
- Himanshu Nagwanshi — CS24BT055@iitdh.ac.in
- Surya Prakash S — CS23BT068@iitdh.ac.in
- Harsh Varshney — cs23bt004@iitdh.ac.in
- Gaddam Viswaijeth — CS23BT076@iitdh.ac.in
- Affiliation: Department of Computer Science and Engineering, Indian Institute of Technology Dharwad, Dharwad, India

**Primary category:** `cs.MA` — Multiagent Systems
**Secondary categories:** `cs.RO` (Robotics), `cs.LG` (Machine Learning)

**Comments (≤400 chars):**
`32 pages, IEEEtran, 20 tables, 10 figures, 134 tests, 38-item claim audit (0 failed). An arXiv preprint. The companion artefacts, the audit and the assembly are runnable from the same repository tree.`

**License:** CC BY 4.0 (recommended for preprints)

**Abstract (<=1920 chars -- this is 1855):**

UAV swarms can provide temporary wireless coverage for Internet-of-Things deployments where fixed infrastructure is unavailable, damaged or insufficient, but persistent operation couples coverage, inter-UAV connectivity, battery depletion, charging contention and UAV failures. This paper formulates the problem of maintaining at least K UAVs over every ground sensor while preserving a connected swarm, and models it as a cooperative Dec-POMDP. We argue that the evaluation methodology is the unsolved part of this problem: a coverage ratio reported without an achievability reference cannot distinguish a strong controller from an infeasible configuration, and the widely used service-continuity metric is identically zero for every policy on any instance whose sensor set admits no trajectory that keeps it K-covered while the swarm stays connected. We therefore introduce a feasibility-certified evaluation framework that derives a rigorous lower bound on the fleet size needed for K-coverage of a bounded region, supplies a teleporting placement oracle as an achievability ceiling, and replaces the degenerate joint-constraint metric with non-degenerate time-averaged and refresh-time metrics. Applied to the project report's own configuration, the bound shows that configuration to be provably infeasible for the region requirement, and the conventional area-surplus criterion certifies nothing. On the corrected configuration the framework is paired with a CTDE MAPPO controller with parameter-shared actors, a hard connectivity feasibility mask, a reserve-UAV recovery mechanism, charging arbitration and PHY-derived links. A hand-designed reactive rule outperforms the learned controller by a gap of 0.309 of persistent coverage (95% interval [0.261, 0.358]); the gap is to the unprivileged reactive rule, the stronger of the two rules, at 0.972.

**Submission checklist:**
- [ ] Upload `Mlawn-midsem-tex.pdf` as the primary file
- [ ] Paste the title, authors, affiliation, abstract, category, keywords above
- [ ] Tick "this is an arXiv preprint" (it is a preprint, not a journal submission)
- [ ] Confirm the author list matches the paper's author block
- [ ] Confirm the abstract is under 1920 characters (1855 above)
- [ ] Confirm the title length (150 chars — arXiv truncates the listing; shorter form (90 chars): "Persistent UAV-IoT Coverage: A Feasibility-Certified Evaluation Framework"). Your call.
- [ ] Confirm the PDF's metadata carries the title and author (it does, as of the last build)
- [ ] Confirm the companion report (REPORT.pdf) is NOT uploaded (it is the midsem deliverable, not part of the preprint)

**Open questions for the user:**
1. Title length: 150 chars is long; arXiv truncates the listing. Shorter form (90 chars): "Persistent UAV-IoT Coverage: A Feasibility-Certified Evaluation Framework". Your call.
2. arXiv allows a "review" or "comment" field — leave blank, or add "Companion report available on request".
3. The 5 reviewers' reports (wireless ✓, MARL ✓, statistics ✓, reproducibility ⏳, adversarial ⏳) are in `C:\Users\gbust\AppData\Local\Temp\opencode\` — read them before the final submission. The MARL reviewer's finding #2 (the missing random-policy baseline) was measured and added; #1 (the budget) is being re-measured now. The statistics reviewer's finding #10 (the budget arm) is being addressed by the convergence ladder (8/16/25/50/100/250 episodes).
4. The re-measurement of the whole matrix (the charger fix) is running; the assembly + gate + arXiv pack will be regenerated once it lands.