# 10 — REPORT BACKBONE: WHAT TO WRITE, IN WHAT ORDER

**Read this last, after the other documents.** It tells you what the final report
should contain and exactly which edits to make to `Mlawn-midsem-tex.tex`.

Current state: 805 lines, 9 pages, IEEEtran, 14 references, 8 sections. The
structure is already good. **You are not rewriting — you are fixing three things
and adding four.**

---

## 1. HONEST ASSESSMENT OF WHAT YOU HAVE

**Already strong — do not touch:**
- Literature survey with 10 papers, each with a stated *limitation relative to
  your work* (not just a summary)
- The research-gap hedge: *"a survey-derived gap statement, not a claim that no
  related component has ever appeared in the broader literature"* — this is
  exactly right epistemically. Examiners reward it.
- The refusal to guarantee connectivity from local observations
- The refusal to assign artificial recovery times to unrecovered failures
- The staged 3-phase implementation plan
- A metric table that reports 12 separate quantities instead of one aggregate

**Broken — must fix:**
1. $R_{\mathrm{cov}}=15$ m makes the objective impossible (Section 2 below)
2. `a_i` means two different things (articulation indicator vs action)
3. Reference `chen2025` attributes the paper to the wrong person

**Missing — high value:**
4. A feasibility argument (proves you thought about whether the instance works)
5. Any numerical results at all
6. Complexity analysis for the scalability claim

---

## 2. THE THREE EDITS

### Edit 1 — Table IV parameter fix

Replace these values:

| Parameter | Current | **New** |
|---|---|---|
| Operating region $\Omega$ | $100\times100$ m | **$80\times80$ m** |
| Coverage radius $R_{\mathrm{cov}}$ | 15 m | **35 m** |
| Communication radius $R_{\mathrm{comm}}$ | 40 m | **45 m** |
| Battery capacity $B^{\mathrm{max}}$ | 30 kJ | **60 kJ** |
| Charge increment | 0.01/step | **0.001/step** |

and add two rows: `Episode length T = 2000 steps`, `Charging pads S = 2`.

**Why each:**
- $R_{\mathrm{cov}}$: 15 → 35 m makes $\sigma=1.50$ instead of 0.18. **Mandatory.**
- $|\Omega|$: 100→80 m keeps the coverage disk at a physically sensible 60 % of
  the region instead of 7 %. Without this, $R_{\mathrm{cov}}=35$ m would need a
  100 m region where the disk is 38 % — also fine actually, but 80 m gives better
  connectivity behaviour.
- $R_{\mathrm{comm}}$: 40 → 45 m puts $P(\text{connected})=0.63$, a genuinely
  marginal regime worth studying. 40 m gives 0.18 — usually disconnected, so
  connectivity would dominate everything and swamp the other four objectives.
- $B^{\mathrm{max}}$: 30 → 60 kJ gives 11.8 min endurance instead of 5.9 min, so
  agents actually reach the energy-critical regime the reward targets.
- charge rate: 0.01 → 0.001/step gives a 16.7 min charge against 11.8 min flight
  (ratio 1.42) instead of 1.7 min against 5.9 min (ratio 0.28). Real Li-ion is
  ~60 min charge on a ~10 min quadrotor.

### Edit 2 — rename the articulation indicator

Global search-and-replace, because `a_i` is overloaded:

| Eq. | From | To |
|---|---|---|
| 12 | $a_i(t)=\mathbb 1[G_t-i\ \text{is disconnected}]$ | $\kappa_i(t)=\mathbb 1[G_t^{-i}\ \text{is disconnected}]$ |
| 13 | $\sum_{i} a_i(t)$ | $\sum_{i} \kappa_i(t)$ |
| 16 | $\mathbb 1[\mathbf{a_i}=\mathrm{Hover}]$ | $\mathbb 1[\mathbf{a}_i=\mathrm{Hover}]$ |

Also add $G_t^{-i}:=G_t$ with vertex $i$ removed, and use $G_t^{-i}$ in Eq. 12
instead of $G_t-i$ for typesetting consistency.

And define the active set formally, right after Eq. 3:

$$\mathcal{U}(t)=\{\,i\in\{1,\dots,N\}:F_i(t)=0\,\}$$

### Edit 3 — fix the reference

`chen2025` → `zhuang2025`, first author **Zhuang Chen**, pages 856–861. Full
BibTeX in `09_REFERENCES_VERIFIED.md`. Verify the DOI resolves in a browser; if
not, drop the reference — you have 13 other verified ones.

---

## 3. THE FOUR ADDITIONS

### Addition 1 — Feasibility argument (Sec. III-F) — HIGHEST VALUE

Insert after the service condition $n_d(t)\ge K$. The exact paragraph is in
`02_FEASIBILITY_AND_PARAMETERS.md` §9. It is four lines of prose and one
equation, and it converts the report's biggest weakness into a demonstration of
rigour.

**This is the best value-for-effort edit in the report.**

### Addition 2 — Why Dec-POMDP (Sec. III-B)

The paper states the Dec-POMDP tuple but never argues the problem is not an MDP.
Add two sentences:

> The problem is a Dec-POMDP for two independent reasons. First, observability
> is partial: $\mathbf{o}_i \subsetneq \mathbf{s}_t$, since a UAV cannot observe
> peers beyond radio range, sensors it does not cover, or global topology.
> Second, execution is decentralised: even with global observability at training
> time, the deployed controller must satisfy $\pi_i:\mathcal{O}_i\to\mathcal{A}_i$
> individually, so the joint action $\mathcal{A}=\mathcal{A}_1\times\cdots\times
> \mathcal{A}_N$ with $|\mathcal{A}|=6^N$ is never available at deployment.

### Addition 3 — Complexity (Sec. III-M or IV)

The scalability claim in Table VIII is currently asserted. Make it rigorous in
five lines:

| Quantity | Cost |
|---|---|
| Actor inference, per agent per step | $O(1)$ — $o_i$ is fixed-size via top-$K_n$ + mask |
| Actor inference, whole swarm | $O(N)$ |
| Critic (training only) | $O(N+M)$ |
| Charging arbitration (Hungarian) | $O(r^3)$, $r$ = concurrent requests $\le N$ |
| Graph recomputation | $O(N^2)$ brute force, $O(N\log N)$ with spatial hash |
| Articulation points (Tarjan) | $O(\lvert V\rvert+\lvert E\rvert)$ |

> Because the observation is fixed-size, the deployed policy costs $O(1)$ per
> agent regardless of swarm size. Execution cost is therefore independent of $N$,
> which is the formal basis for the scalability metric in Table VIII.

### Addition 4 — At least some numbers

Zero numbers is the biggest remaining risk. The three heuristic baselines need
**no learning** and are cheap:

| Baseline | Implementation | Runtime |
|---|---|---|
| Fixed formation + threshold recharge | ~30 lines | seconds |
| Greedy lowest-battery recharge | ~40 lines | seconds |
| Reactive reconfiguration | ~80 lines | ~1 h |

Run all three on 5 seeds under the corrected parameters, fill in 4–5 rows of
Table VIII with mean ± std. This alone converts the report from a proposal into
a study. MAPPO results can remain future work — that is a legitimate position
*if* baselines are present.

**Suggested appendix:** the three scripts in this folder, with their output. It
makes every number in the paper reproducible, which is worth marks by itself.

---

## 4. TARGET STRUCTURE

Keep the current section order. It is already correct for an IEEE conference
paper.

```
I.   Introduction
       goal, gap, research question, 4 contributions
II.  Literature Survey
       Table I: 10 papers, each with "limitation relative to this work"
       Sec. II-C: research gap  <- RESTRUCTURE as a capability matrix
III. System Model
       A. Architecture (Fig. 1)
       B. Dec-POMDP formulation         <- ADD why-Dec-POMDP paragraph
       C. Global state
       D. Local observation
       E. Action space and motion
       F. Persistent K-coverage         <- ADD feasibility paragraph
       G. Connectivity model
       H. Battery model
       I. Charging coordination
       J. Safety constraints
       K. Failure and recovery
       L. Objective and reward          <- ADD sign-consistency sentence
       M. Parameters and scope          <- REPLACE Table IV
       N. Complexity                    <- NEW
IV.  Proposed ML Algorithm
       A. CTDE MAPPO, B. Feasibility mask, C. Failure-aware execution,
       D. Algorithm 1, E. Training protocol, F. Hyperparameters
V.   Comparison Models                <- ADD A1, A5, A9 from ref verification
VI.  Performance Metrics
VII. Experimental Design Matrix
VIII. Results                          <- NEW (heuristic baselines only)
```

---

## 5. WHAT TO SAY WHEN THEY ASK

**"Is the problem actually solvable?"**
> Yes, and I show the condition. $K$-coverage of area $A$ by $N$ sensing disks
> needs $N\pi R_{\mathrm{cov}}^2 \ge KA$, so $R_{\mathrm{cov}} \ge
> \sqrt{KA/(\pi N)}$. For my parameters that is 28.5 m counting, 30.0 m
> packing-corrected, and I use 35 m — a surplus ratio of 1.50, dropping to 1.20
> after a failure. My original value of 15 m gave a ratio of 0.18, which means
> the objective was unachievable; I found that by checking feasibility.

*(Saying this unprompted is worth more than any single section of the report.)*

**"Why MAPPO and not QMIX?"**
> MAPPO keeps a centralised critic during training and a shared actor at
> deployment, so the action space stays linear in $N$ per agent. QMIX's
> monotonic factorisation assumes the team $Q$ decomposes additively over agents;
> coverage, connectivity and charging contention are coupled non-additively
> through shared sensors and shared pads, so that assumption does not hold.
> Also, the action mask for the return-energy constraint makes the feasible set
> state-dependent, which is awkward for a monotonic decomposition.

**"How do you guarantee connectivity?"**
> I don't, and I don't claim to. A UAV provably cannot detect a global
> articulation point from one-hop observations. So the mask enforces the locally
> checkable part — the move doesn't isolate the mover — the reward penalises
> articulation count softly through $\lambda_C$, and connectivity is *reported as
> a metric*, not asserted as an invariant.

**"Why is the reserve a resource and not an agent?"**
> Deterministic activation and assignment. Making it an agent would add a
> seventh actor to a problem where the joint action space is already $6^N$, for a
> role that is a single binary decision. The reserve uses the same shared actor
> once it is inserted, so it does not need its own policy.

**"Your results show no improvement."**
> I report heuristic baselines only. The contribution at this stage is the
> formulation, the feasibility analysis, and the evaluation protocol. The MAPPO
> experiments are specified in Section VII but not yet run, and I would rather
> defer the claim than state an unsupported one.

---

## 6. FINAL CHECKLIST

**Do these three, then submit:**
- [ ] `R_{\mathrm{cov}}` 15 → 35 m, `$\Omega$` 100 → 80 m,
      `R_{\mathrm{comm}}` 40 → 45 m, `B^{max}` 30 → 60 kJ, charge 0.01 → 0.001
- [ ] `a_i` (articulation) → `$\kappa_i$` everywhere; define `$\mathcal{U}(t)$`
- [ ] `chen2025` → `zhuang2025`, author Zhuang Chen, pp. 856–861

**Then, in priority order:**
- [ ] Add the feasibility paragraph (Sec. III-F) — 15 minutes, biggest payoff
- [ ] Add the why-Dec-POMDP paragraph (Sec. III-B) — 5 minutes
- [ ] Add the sign-consistency sentence (Sec. III-L) — 2 minutes
- [ ] Add the complexity table (Sec. III-N) — 15 minutes
- [ ] Run the three heuristic baselines, fill in 4–5 rows of Table VIII
- [ ] Add A1 (Shi et al. TMC 2025) and A9 (Scherer & Rinner 2016) to related work
- [ ] Restructure the gap statement as a capability matrix

**Leave alone — these are already right:**
- The two honesty disclaimers (connectivity guarantee, unrecovered failures)
- The "survey-derived gap statement" hedge
- The 12-metric evaluation table
- The 3-phase implementation plan
- The "numerical claims deferred" position *if* you add baseline numbers

---

## 7. WHERE EVERYTHING IS

| File | What it is |
|---|---|
| `00_MATH_AUDIT.md` | Equation-by-equation audit + all fixes |
| `01_PROBLEM_FORMULATION.md` | The problem as one formal object (professor's ask) |
| `02_FEASIBILITY_AND_PARAMETERS.md` | The $R_{\mathrm{cov}}$ proof + corrected table |
| `03_WIRELESS_MODELS.md` | 3GPP TR 38.901, fading, link budget, INET/Simu5G radio models |
| `04_MARL_THEORY.md` | Dec-POMDP, PG, GAE, TRPO, PPO, MAPPO derivations |
| `05_07_THEORY_COVERAGE_GRAPH_ENERGY.md` | Art gallery, $k$-coverage, Menger, Tarjan, Laplacian, KiBaM, Hungarian |
| `08_SIMULATION_STACK.md` | OMNeT++ 6.4, INET 4.7, Simu5G 1.7, RL bridges, version traps |
| `09_REFERENCES_VERIFIED.md` | 14 refs checked + 14 new verified papers |
| `10_REPORT_BACKBONE.md` | This file |
| `feasibility_check.py` | Proves the current table is infeasible |
| `parameter_search.py` | Tests each knob, derives the minimum $R_{\mathrm{cov}}$ |
| `scenario_compare.py` | Compares 6 scenarios with Monte-Carlo connectivity |
