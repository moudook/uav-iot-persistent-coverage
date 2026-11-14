# Fresh-reader review of REPORT.pdf (via REPORT.tex)

## First impression (150 words)
This is a project report for a wireless-networks ML course project titled "Persistent UAV-IoT Coverage." It reads like an internal engineering log rather than a reader-facing paper: it assumes you already know the paper, the simulator, and the audit trail. It is dense with jargon (CK, AG, SC, GAE, MAPPO, "credit assignment," "corner certificate") introduced with no definitions, and numbers appear without units or sources. The tone is self-flagellating and self-congratulatory at once — long defect tables and audit lists, but no plain-language statement of what the system actually does or what the final result means. Readable only if you are already inside the project. A first-time reader cannot tell what problem is being solved, what "the gap of 0.298" refers to, or whether the reported controller is good or bad. Skip if you are not a project insider.

## Confusions
1. §1 table — "Gap to the strongest rule 0.298 ... against the unprivileged reactive rule at 0.972" — what is "the strongest rule"? Is 0.972 a score? Of what metric? No unit/definition. Fix: define the metric and what "rule" means.
2. §1 — "The learned controller 0.674 ± 0.060" — is this CK? Compared to 0.972? Direction of "better" unknown. Fix: state metric name and whether higher is better.
3. §2 item 1 — "25 episodes of 2000 control steps" — episode/step never defined; no link to coverage. Fix: one sentence defining episode.
4. §3 table — columns CK, AG, SC undefined acronyms. Fix: expand in header or caption.
5. §3 — "Cov. deficit*" — deficit of what; * footnote exists but metric unnamed. Fix: define.
6. §3 caption fig — "gap of 0.298 is out of reach of every candidate explanation" — gap between what and what? Fix: restate the two numbers.
7. §3 text — "adding the agent identity (upper limit 0.137, margin +0.161)" — margin of what? Fix: define margin.
8. §3 — "standard error of the difference is 0.014" — which difference, which n? Fix: specify.
9. §4 table — "commit hashes like 13cb839" as fixes; reader cannot verify. Fix: describe fix in words.
10. §4 — "Reward eq (23)" references an equation not in this report. Fix: include eq (23) or drop reference.
11. §4 item 28 — "Eq. (13)" undefined. Fix: include.
12. §5 — audits numbered 1–7 plus "Audit 4 (MiniMax)" duplicate numbering of Audit 4. Confusing. Fix: unique IDs.
13. §5 — "Audit 3 (DONE, 20 Oct 23:15)" — date format ambiguous (Oct 20 of which year?). Fix: full date.
14. §6 — "Phase 3 (Simu5G PHY) is scaffolded but not executed" — what is Simu5G? Fix: one line.
15. §6 — "corner certificate," "credit assignment" used without definition throughout. Fix: define on first use.

## Terms/acronyms used before defined
CK, AG, SC, MAPPO, GAE, UAV, IoT, PHY, LoS/NLoS, SNR, DQN, MARL, RNG, GAE, "credit assignment," "corner certificate," "privileged rule," "unprivileged reactive rule."

## Numbers without obvious source
0.298, 0.972, 0.674 ± 0.060, 0.137, 0.102, 0.081, 0.028, -0.038, 0.595/0.621/0.662, 81.04%, 67.07%, 74%, 1.26x, 85%, 8%, 0.648, 0.990, 0.000, 0.156, -0.222/+0.090, 13.7 ms/step, 400 steps, 2000 steps, 25/6/20/8 episodes, 5 scenes, 8 seeds, 134 tests, 38 audit items.

## Trust verdict
Maybe. The report is unusually honest about defects and audits (a strength), but as a standalone document it is unreadable: undefined acronyms, dangling equation references (Eq. 13, Eq. 23), duplicate audit numbering, and numbers with no units or sources. Biggest reason: it is an internal log written for people who already hold the codebase and paper, not a document a fresh reader can verify or cite.