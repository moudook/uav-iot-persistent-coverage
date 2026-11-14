# 00 — MATHEMATICAL & SCIENTIFIC AUDIT

**File audited:** `Project1/Mlawn-midsem-tex.tex` (805 lines, IEEEtran, 9-page PDF)
**Date:** 29 September 2026
**Verdict:** The paper is **structurally strong and mathematically honest**, but it
contains **one fatal parameter error** that makes the stated objective physically
unachievable, plus **several notation collisions** and **3 weaker modelling problems**.

Fix the CRITICAL item before submission. The rest are improvements.

---

## PART 1 — THE FATAL FINDING

### 1.1 `R_cov = 15 m` makes `K`-coverage impossible for *every* controller

**The claim in the paper (Eq. 12–16, Sec. III-F):**

> "The primary service condition is $n_d(t)\ge K$ for all $d$ whenever the
> geometry and available fleet make it feasible."

and Table IV sets $R_{\mathrm{cov}} = 15$ m, $M = 20$, $N = 5$, $K = 2$,
$|\Omega| = 100\times 100 = 10\,000$ m$^2$.

**The counting bound.** For $K$-coverage of a region of area $A$ by $N$ sensing
disks of radius $r$, coverage of all $M$ sensors at level $K$ requires $K\cdot M$
distinct (sensor, UAV) incidence pairs. Each UAV supplies at most $\pi r^2$ of
covered area, hence at most $M\pi r^2/A$ sensors. Summing over $N$ UAVs:

$$\underbrace{N\cdot \pi r^2}_{\text{area available}} \;\ge\; \underbrace{K\cdot A}_{\text{area required}}
\qquad\Longleftrightarrow\qquad
r \;\ge\; \sqrt{\frac{KA}{\pi N}} .$$

**Substituting the paper's values:**

$$r \;\ge\; \sqrt{\frac{2 \times 10\,000}{\pi \times 5}} \;=\; \sqrt{1273.24} \;=\; \mathbf{35.68\ \text{m}}$$

The paper uses **15 m** — short by a factor of **2.38×**.

**Direct consequence (computed, not estimated):**

| Quantity | Value |
|---|---|
| Coverage area required, $KA$ | $20\,000$ m² |
| Coverage area supplied, $N\pi R_{\mathrm{cov}}^2$ | $3\,534$ m² |
| Ratio | **0.177** |
| Expected coverage slots, $N\cdot(M/A)\pi R_{\mathrm{cov}}^2$ | 7.07 |
| Coverage slots required, $KM$ | 40 |
| **Fraction of requirement achievable** | **17.7 %** |

**What this means for the report.** With these parameters, $n_d(t)\ge K$ is
**never** satisfiable. Not by MAPPO, not by a heuristic, not by an omniscient
optimal controller. The reward's dominant term $\lambda_O U_t$ is therefore
permanently pinned near its maximum, the agent receives essentially a constant
gradient, and the entire coverage-learning experiment produces no signal.
Every baseline will score the same. This is the single most likely reason an
examiner would reject the report after reading Table IV.

**Packing-corrected bound.** The counting bound ignores that coverage disks
overlap. Densest packing of congruent disks has density
$\delta = \pi/(2\sqrt3) \approx 0.9069$, so:

$$r \;\ge\; \sqrt{\frac{KA}{\delta\,\pi N}} \;=\; \sqrt{\frac{20\,000}{0.9069\,\pi\times 5}} \;=\; \mathbf{37.47\ \text{m}}$$

**Best case does not save it.** Even with a perfectly uniform sensor grid
(5×4, spacing 20 × 25 m), one UAV with $r=15$ m covers at most **1** sensor, so
the swarm supplies 5 slots against 40 required. The problem is not a placement
failure — it is geometrically impossible.

**Fix:** set $R_{\mathrm{cov}} \ge 40$ m (see Part 4 for the recommended set).

---

## PART 2 — NOTATION COLLISIONS (fix these; an examiner will spot them)

### 2.1 `$a_i$` means two different things — CRITICAL

| Location | Usage | Meaning |
|---|---|---|
| Eq. 2 (policy) | $a_i(t)\sim\pi_\theta(a_i\mid \mathbf{o}_i(t))$ | the **action** |
| Eq. 16 | $P_i(t)=P_{\mathrm{hover}}\mathbb 1[\mathbf{a_i}=\mathrm{Hover}]+\dots$ | the **action** |
| Eq. 12 | $a_i(t)=\mathbb 1[G_t-i\ \text{is disconnected}]$ | **articulation-point indicator** |
| Eq. 13 | $\mathrm{Crit}_t=\frac{1}{|V_t^{act}|}\sum_i a_i(t)$ | uses the indicator |

Eq. 13 is built on the indicator meaning while Eq. 2 and Eq. 16 use the action
meaning. This is a genuine ambiguity, not a style issue.

**Fix:** rename the articulation indicator. Suggested:

$$\kappa_i(t) \;=\; \mathbb 1\!\left[G_t^{-i}\ \text{is disconnected}\right],
\qquad
\mathrm{Crit}_t=\frac{1}{|V_t^{\mathrm{act}}|}\sum_{i\in V_t^{\mathrm{act}}}\kappa_i(t)$$

Note also that $\kappa$ then does not collide with the future use of
$\kappa(G)$ for vertex connectivity, which appears in earlier drafts — pick one.
The report already uses $\rho_i$ for the *local* proxy, which is the right
distinction, so keeping $\kappa_i$ for the *global* one is consistent.

### 2.2 `$\gamma$` is safe, but check `$\lambda$`

The report uses $\gamma$ for the discount factor (Eq. 3) and $\lambda_E,\lambda_D,
\lambda_W,\lambda_R,\lambda_C$ for objective weights, and $\lambda$ for the GAE
parameter (Table VI). **This is internally consistent** — no collision — but note
that $\lambda$ (GAE) and $\lambda_\bullet$ (rewards) look alike. Add one sentence
distinguishing them, or rename GAE's to $\lambda_{\mathrm{GAE}}$.

*(This was a real collision in the earlier Beamer version of the deck, where
`\gamma` doubled as a charging-cost coefficient. That is fixed.)*

### 2.3 `$\mathcal{V}_t^{\mathrm{act}}$` is used but never defined

Eq. 11 and Eq. 13 sum over $\mathcal{V}_t^{\mathrm{act}}$ (the set of *active*
UAVs). The text says "A failed UAV is removed from the active set" but never
writes the set formally. Add:

$$\mathcal{V}_t^{\mathrm{act}} \;=\; \bigl\{\, i \in \{1,\dots,N\} \;:\; F_i(t)=0 \,\bigr\},
\qquad
\mathcal{V}_t^{\mathrm{act}}\subset \mathcal{V}_t^{\mathrm{act}}\cup\{N+1\}$$

### 2.4 `$S$` is overloaded with the objective sum index

`$S$` is the number of charging pads (Sec. III-A, $\mathbf{Q}_t\in\{0,1\}^{S}$).
In Eq. 30 the sums $\sum_s \sum_s$ use lowercase $s$ as a *pad index*, which is
fine, but make sure the text never writes $S$ when it means the pad count in the
same sentence as the objective.

### 2.5 Two different coverage quantities, both named confusingly

| Symbol | Eq. | Meaning |
|---|---|---|
| $C_t$ | 10 | instantaneous *soft* score, $\min(n_d/K,1)$ averaged |
| $C_K$ | Table VIII | *hard* fraction of sensor-slots with $n_d\ge K$ |

These are not the same and the names are close. Suggest $C_t^{\mathrm{soft}}$ and
$C_K^{\mathrm{hard}}$, or state the relationship explicitly. Note $C_t=1 \iff
n_d\ge K\ \forall d$, so $C_t\le C_K$ always — worth one sentence.

---

## PART 3 — VERIFIED CORRECT (do not touch)

I checked these carefully. They are right.

| Eq. | Statement | Verdict |
|---|---|---|
| 1 | Dec-POMDP tuple $\langle N,\mathcal S,\{\mathcal A_i\},\{\mathcal O_i\},\mathcal T,R,\gamma\rangle$ | ✅ correct |
| 2 | Objective $\max_\pi \mathbb E_\pi[\sum_{t=0}^{T-1}\gamma^t R_t]$ | ✅ correct |
| 4 | $o_i(t)=[\mathbf p_i,\mathbf v_i,b_i,\mathcal N_i,C_i^{local},\rho_i,\tau_i^{return},E_i^{pad}]$ | ✅ correct |
| 5 | $x_{id}(t)=\mathbb 1[\|\mathbf p_i-\mathbf q_d\|_2\le R_{cov}]$ | ✅ correct |
| 6 | $n_d(t)=\sum_{i\in V^{act}} x_{id}(t)$ | ✅ correct |
| 7 | $C_t=\frac1M\sum_d \min(n_d/K,1)$ | ✅ correct |
| 8 | $U_t=\frac1M\sum_d\mathbb 1[n_d<K]$ | ✅ correct |
| 9 | $G_t=(V_t,E_t),\ E_t=\{(i,j):\|\mathbf p_i-\mathbf p_j\|_2\le R_{comm}\}$ | ✅ correct |
| 11 | $a_i(t)=\mathbb 1[G_t-i \text{ disconnected}]$ | ✅ correct *math* (bad symbol, §2.1) |
| 14 | $E_i(t+1)=\mathrm{clip}(E_i(t)-P_i(t)\Delta t+P_{ch,i}\Delta t,\,0,B^{max})$ | ✅ correct |
| 15 | $E_i^{req}=E_i^{pad}+E_i^{rejoin}+E^{reserve}$ | ✅ correct |
| 17 | $c_{is}=\alpha\tilde d_{is}+\beta\tilde q_s+\mu\tilde u_i$ | ✅ correct; **normalised tildes are good practice** |
| 18 | Hungarian assignment with $\sum_s y_{is}\le1,\ \sum_i y_{is}\le1$ | ✅ correct LAP |
| 21 | Safety $\|\mathbf v_i\|\le v_{max},\ \mathbf p_i\in\Omega,\ \|\mathbf p_i-\mathbf p_j\|\ge d_{safe}$ | ✅ correct |
| 23 | $\tau_f=\inf\{\tau\ge0: n_d(t_f+\tau)\ge K\ \forall d\}$ | ✅ correct |
| 25 | $J_{out}(\pi)=\mathbb E_\pi[\sum\gamma^t U_t]$ | ✅ correct |
| 28 | Team reward $r_t=-(\lambda_O U_t+\lambda_E E_t+\dots)$ | ✅ correct, and **sign-consistent** with the max-return objective |
| 31 | GAE $\hat A_t=\sum_{l=0}^{T-t-1}(\gamma\lambda)^l\delta_{t+l}$ | ✅ correct |
| 33 | Clipped PPO actor loss | ✅ correct form |
| 34 | Critic loss with $\hat R_t=\hat A_t+V_\phi(\mathbf s_t)$ | ✅ correct |

**Sign consistency — worth stating explicitly in the report.** The paper minimises
$J_{out}$ (Eq. 25) but the RL *maximises* return, and Eq. 28 negates the reward.
This is internally consistent, but an examiner may pause on it. Add one line:
*"Since the learner maximises expected return while the control objective is a
minimisation, the team reward is the negated weighted cost (Eq. 28); the
multi-objective problem of Eq. 26 and the RL objective are therefore equivalent
up to sign."* That sentence removes the ambiguity entirely.

---

## PART 4 — MODELLING WEAKNESSES (worth fixing, not fatal)

### 4.1 Endurance is only ~6 minutes — the energy regime is never exercised

$$t_{\text{move}}=\frac{B^{max}}{P_{\mathrm{move}}+P_{\mathrm{comm}}}
=\frac{30\,000}{75+10}=352.8\ \text{s}=5.9\ \text{min}$$

The return threshold lands at

$$E^{req}\approx \underbrace{2404}_{\text{corner}\to\text{corner}}+
\underbrace{1700}_{\text{rejoin}}+\underbrace{3000}_{\text{10\% reserve}}
=7104\ \text{J}=24\%\ B^{max},\qquad\text{so } b_i<0.76 .$$

So the agent only ever operates in the top 76 % of the battery window, and the
"energy-critical" behaviour the reward is designed to shape is rarely visited.
With $T=2000$ steps at $\Delta t=1$ s, a UAV gets roughly **5–6 recharge cycles per
episode** — enough to matter, but the dynamics are heavily dominated by transit.

**Recommended:** $B^{max}=60$ kJ, $P_{\mathrm{move}}=75$ W, $P_{\mathrm{comm}}=10$ W
→ endurance 11.8 min, return threshold 17 %, giving ~3 cycles per 2000-step episode.

### 4.2 Charging is ~6× too fast

`0.01 battery fraction / step` at $\Delta t=1$ s means a full 0→1 charge takes
**100 s**, versus 353 s of flight. Real Li-ion at 1C takes ~60 min. Charging
contention is therefore almost free, which undercuts one of the paper's five
claimed contributions.

**Recommended:** `0.001 battery fraction / step` at $\Delta t=1$ s → 1000 s
(16.7 min) full charge; charge/flight ratio 1.42, close to a real 1C pack.
(Matches `mei2026`'s 0.547 coverage / 38-slot outage scale, which is a useful
comparability point.)

### 4.3 $\Delta t = 1$ s is too coarse relative to $R_{\mathrm{cov}}$

At $v_{max}=5$ m/s and $\Delta t=1$ s a UAV moves 5 m per step, so with
$R_{\mathrm{cov}}=15$ m the coverage disk is only **6 control steps** across its
diameter. The 6-way discrete action space is then dominated by moves that change
which sensors are covered very little — a weak credit-assignment signal.

**Rule of thumb:** choose $\Delta t$ so that
$$\frac{2R_{\mathrm{cov}}}{v_{max}\Delta t}\;\ge\;10
\qquad\Longleftrightarrow\qquad
\Delta t \;\le\; \frac{2R_{\mathrm{cov}}}{10\,v_{max}} .$$

With the corrected $R_{\mathrm{cov}}=35$ m and $v_{max}=5$ m/s this gives
$\Delta t\le1.4$ s, so the existing 1 s is **acceptable once $R_{\mathrm{cov}}$ is
fixed**. No change needed. (The problem was $R_{\mathrm{cov}}$, not $\Delta t$.)

### 4.4 The Dec-POMDP is claimed but not argued

Sec. III-B states the Dec-POMDP tuple but never says *why* it is not an MDP. The
report should state explicitly that partial observability is inherent: each UAV
cannot observe $s_t$, so the controller is a Dec-POMDP by construction, and
decentralised execution additionally forbids access to the joint action. One
paragraph, and it strengthens the contribution claim.

### 4.5 No complexity analysis

A one-line complexity result strengthens the scalability contribution and is
trivial to prove:

- **Actor inference:** $O(1)$ per agent per step, since $o_i$ is fixed-size
  (top-$K_n$ neighbours with masking). Total $O(N)$.
- **Critic (training only):** $O(N+M)$ per step, since $s_t$ is linear in the
  number of agents and sensors.
- **Hungarian charging step:** $O(r^3)$ in the number of concurrent charge
  requests $r$ (typically $r\le N$), executed once per slot.
- **Graph recomputation:** $O(N^2)$ brute force, or $O(N\log N)$ with a spatial
  hash; articulation-point detection is $O(|V|+|E|)$ via Tarjan.

Because the actor is $O(1)$ per agent, the *deployed* policy cost is independent
of $N$. That is the formal argument for the scalability claim in Table VIII, and
it is currently asserted but not shown.

### 4.6 Connectivity is enforced by masking, but the paper is careful — keep that

Sec. III-H correctly notes that connectivity cannot be *guaranteed* from one-hop
observations, and the paper says so. This is the right call and a strength. Make
sure the reward's $\lambda_C$ term and the local proxy $\rho_i$ are presented as
a *soft* mechanism, with connectivity as an evaluation metric rather than a
claimed invariant. The report already does this — preserve it.

### 4.7 "Numerical performance claims are intentionally deferred"

This is honest and defensible, but a mid-semester report with **zero** numbers is
a risk. Minimum viable addition: run the **heuristic baselines only** (no MARL
needed) and report Table VIII metrics for 3–5 seeds. Baselines are cheap:

| Baseline | Effort | Expected runtime |
|---|---|---|
| Fixed formation + threshold recharge | trivial | minutes |
| Greedy lowest-battery recharge | trivial | minutes |
| Reactive reconfiguration | small | ~1 h |

Even three heuristic rows with mean ± std makes the report concrete and directly
tests the feasibility fix in Part 5.

---

## PART 5 — CORRECTED PARAMETER SET

Computed by Monte-Carlo and counting bounds (`parameter_search.py`,
`scenario_compare.py` in this folder). Define the surplus ratio

$$\sigma \;=\; \frac{\text{expected coverage slots}}{\text{required slots}}
=\frac{N\,(M/A)\,\pi R_{\mathrm{cov}}^2}{KM}$$

$\sigma\ge 1$ is necessary; $\sigma \gtrsim 1.5$ leaves room for movement and a
failure. $P(\text{connected})$ is the Monte-Carlo probability that a random
geometric graph on $N$ uniform points is connected.

### Recommendation — Scenario S-E (primary)

| Parameter | Paper | **Recommended** | Why |
|---|---|---|---|
| $\Omega$ | $100\times100$ m | **$80\times80$ m** | keeps radii physically plausible |
| $M$ | 20 | **20** | unchanged |
| $N$ / $N_R$ | 5 / 1 | **5 / 1** | unchanged |
| $K$ | 2 | **2** | unchanged |
| $R_{\mathrm{cov}}$ | 15 m | **35 m** | $\sigma = 1.50$ — feasible with slack |
| $R_{\mathrm{comm}}$ | 40 m | **45 m** | $P(\text{conn}) = 0.63$, $P(\text{conn}\mid\text{failure}) = 0.56$ |
| $v_{max}$ | 5 m/s | **5 m/s** | unchanged |
| $d_{\mathrm{safe}}$ | 5 m | **5 m** | unchanged |
| $\Delta t$ | 1 s | **1 s** | $\ge 14$ steps across $2R_{\mathrm{cov}}$ — fine |
| $B^{\mathrm{max}}$ | 30 kJ | **60 kJ** | 11.8 min endurance |
| $P_{\mathrm{hover}}/P_{\mathrm{move}}/P_{\mathrm{comm}}$ | 50/75/10 W | **50/75/10 W** | unchanged |
| charge increment | 0.01/step | **0.001/step** | 16.7 min full charge, ratio 1.42 |
| $S$ (pads) | 2 | **2** | unchanged |
| $T$ | — | **2000 steps** | ~3 recharge cycles per episode |

With $R_{\mathrm{cov}}=35$ m the coverage disk is 60 % of the region area, so a
UAV sees ~10 of 20 sensors on average — genuinely partial coverage, not trivial.

**Failure-tolerance check.** After losing one UAV, $\sigma$ falls to
$4\cdot(M/A)\pi R_{\mathrm{cov}}^2/(KM) = 1.20$ — still above 1. The reserve is
therefore a *safety factor* rather than the only route to feasibility, which is
exactly the claim the paper wants to make. $P(\text{connected})$ drops from 0.63
to 0.56, so the reserve demonstrably helps connectivity too.

### Alternative — Scenario S-C (if you want connectivity to be the hard constraint)

$|\Omega|=60\times60$ m, $R_{\mathrm{cov}}=30$ m, $R_{\mathrm{comm}}=40$ m:
$\sigma = 1.96$ (coverage is comfortable) but $P(\text{conn}) = 0.86$ falling to
$0.78$ after a failure. Use this if the story you want is "coverage is solvable,
connectivity is what breaks."

### What NOT to do

Increasing $N$ to fix $R_{\mathrm{cov}}=15$ m requires $N\ge 29$ (counting) or
$N\ge 32$ (packing-corrected). That destroys the scalability argument and makes
a 30-agent swarm intractable to train. Reducing $M$ below 4 makes the problem
trivial. Increasing $|\Omega|$ makes it strictly worse.

---

## PART 6 — CHECKLIST BEFORE SUBMISSION

**Must fix:**
- [ ] Set $R_{\mathrm{cov}}\ge 35$ m and state the counting bound in the paper.
      Add a one-sentence feasibility argument to Sec. III-F:
      *"K-coverage is reachable under the stated fleet only if
      $R_{\mathrm{cov}}\ge\sqrt{KA/(\pi N)}$; Table IV satisfies this."*
- [ ] Rename the articulation indicator to avoid clashing with the action
      (§2.1) and propagate through Eqs. 12, 13, 16.
- [ ] Fix reference `chen2025` → author is **Zhuang** Chen, not Z. Chen
      (see `09_REFERENCES_VERIFIED.md`).

**Strongly recommended:**
- [ ] Define $\mathcal{V}_t^{\mathrm{act}}$ formally.
- [ ] Add the sign-consistency sentence between Eq. 26 and Eq. 28.
- [ ] Fix `$B^{\mathrm{max}}$` to 60 kJ and the charge rate to 0.001/step.
- [ ] Run the three heuristic baselines and fill in at least a few rows of
      Table VIII. Zero numbers is the biggest remaining risk.
- [ ] Add the one-paragraph justification of *why Dec-POMDP* (§4.4).
- [ ] Add the complexity paragraph (§4.5).

**Optional polish:**
- [ ] Distinguish $C_t$ (soft) from $C_K$ (hard) by name.
- [ ] Rename GAE's $\lambda$ to $\lambda_{\mathrm{GAE}}$.
- [ ] Change `qiu2019` to the peer-reviewed ICC 2020 version
      (doi `10.1109/ICC40277.2020.9149258`).
- [ ] Change `mathew2015` title to "**Multirobot** Rendezvous Planning…"
      (IEEE-exact form).
- [ ] Mark `sun2025` explicitly as an arXiv preprint.

**Do not change (already correct and honest):**
- The refusal to claim connectivity guarantees from local observations (§4.6).
- The refusal to assign artificial recovery times to unrecovered failures (§III-I).
- The deferral of numerical claims *if* you add baseline numbers.
- The "survey-derived gap statement, not a claim that no related component has
  ever appeared" hedge in Sec. II-C. This is exactly the right epistemic framing.
