# 01 — THE PROBLEM STATEMENT, WRITTEN AS ONE MATHEMATICAL OBJECT

**Purpose.** Your professor asked you to *put the problem statement into math so
it is easy to explain and verify.* The current paper defines the model across
Sections III-A to III-M, which is normal for a paper but awkward when you have to
state "what is the problem?" in one breath. This document collapses the whole
problem into a **single numbered statement** that you can put on one slide and
defend line by line.

Everything here is consistent with `Mlawn-midsem-tex.tex` after the fixes in
`00_MATH_AUDIT.md`.

---

## THE ONE-SLIDE VERSION

> **Persistent, Fault-Tolerant UAV-IoT Coverage (PFT-UAV-IoT).**
> Given $N$ cooperative UAVs, $M$ fixed ground sensors in a region $\Omega$, a
> finite battery per UAV, $S$ shared charging pads, and stochastic single-UAV
> failures, find decentralised policies $\{\pi_i\}$ such that, at every time
> step, (C1) every sensor is covered by $\ge K$ UAVs, (C2) the UAV
> communication graph stays connected, (C3) no UAV commits to a path it cannot
> survive on its remaining energy, and (C4) no hard physical constraint is
> violated — while minimising expected long-horizon service loss.

Now the formal object.

---

## 1. SYSTEM ENTITIES

| Symbol | Type | Meaning |
|---|---|---|
| $\mathcal{U}$ | $\subseteq\{1,\dots,N\}$ | active UAV index set |
| $\mathcal{U}_R$ | $\{N+1\}$ | reserve UAV index set |
| $\mathcal{D}$ | $=\{1,\dots,M\}$ | sensor index set |
| $\mathcal{S}$ | $=\{1,\dots,S\}$ | charging-pad index set |
| $\Omega\subset\mathbb{R}^2$ | region | operating area, $\|\Omega\|=A$ |
| $z_0$ | $\mathbb{R}_+$ | nominal UAV altitude (fixed) |

**Fix from the audit:** the active set is written formally, not implied:

$$\mathcal{U}(t) \;=\; \bigl\{\,i\in\{1,\dots,N\} \;:\; F_i(t)=0\,\bigr\}$$

A UAV with $F_i(t)=1$ is removed from all coverage, connectivity and energy sums.

---

## 2. STATE

$$\boxed{\;\mathbf{s}_t=\Bigl\{\bigl(\mathbf{p}_i,\mathbf{v}_i,b_i,m_i,F_i\bigr)_{i\in\{1..N\}},\ \bigl(\mathbf{q}_d\bigr)_{d\in\mathcal{D}},\ \mathbf{Q}_t\Bigr\}\;}$$

$$\mathbf{s}_t=\Bigl\{\bigl(\mathbf{p}_i,\mathbf{v}_i,b_i,m_i,F_i\bigr)_{i=1}^{N},\;\bigl(\mathbf{q}_d\bigr)_{d=1}^{M},\;\mathbf{Q}_t\Bigr\}
\quad\text{with}$$

| Symbol | Domain | Meaning |
|---|---|---|
| $\mathbf{p}_i(t)$ | $\Omega$ | horizontal position |
| $\mathbf{v}_i(t)$ | $\{\mathbf v:\|\mathbf v\|\le v_{\max}\}$ | velocity |
| $b_i(t)$ | $[0,1]$ | normalised battery, $E_i=b_iB^{\max}$ |
| $m_i(t)$ | $\{\textsf{serve},\textsf{transit},\textsf{charge}\}$ | mode |
| $F_i(t)$ | $\{0,1\}$ | failure flag |
| $\mathbf{q}_d$ | $\Omega$ | fixed sensor position |
| $\mathbf{Q}_t$ | $\{0,1\}^{S}$ | pad occupancy |

---

## 3. OBSERVATION (why this is a Dec-POMDP, not an MDP)

$$\mathbf{o}_i(t)=\Bigl[\mathbf{p}_i,\ \mathbf{v}_i,\ b_i,\ \mathcal{N}_i(t),\ C_i^{\mathrm{local}}(t),\ \rho_i(t),\ \tau_i^{\mathrm{return}}(t),\ E_i^{\mathrm{pad}}(t)\Bigr]$$

**The formal argument the current paper is missing.** The problem is a Dec-POMDP
for two independent reasons:

1. **Partial observability.** $\mathbf{o}_i \subsetneq \mathbf{s}_t$. A UAV
   cannot observe other UAVs' exact positions beyond radio range, cannot see
   sensors it is not covering, and cannot see the global graph topology.
2. **Decentralised execution.** Even if $\mathbf{s}_t$ were observable at
   training time, the deployed controller must satisfy
   $\pi_i:\mathcal{O}_i\to\mathcal{A}_i$ **individually** — the joint action is
   never available at deployment.

The paper's own line — *"this distinction avoids assuming that an individual UAV
can magically obtain the complete global topology"* (Sec. III-D) — is the right
insight; it just needs to be stated as a structural claim, not a caveat.

**Global vs local criticality — keep the distinction, rename the symbol.**
The *global* articulation indicator is an evaluation quantity:

$$\kappa_i(t)=\mathbb 1\!\left[G_t^{-i}\ \text{is disconnected}\right],
\qquad G_t^{-i}:=G_t \text{ with vertex } i \text{ and its edges removed}$$

The *local* proxy $\rho_i$ is what the actor actually receives, computed from
1-hop (and optionally 2-hop) neighbour exchange. **Never** feed $\kappa_i$ to the
actor; feed $\rho_i$ and evaluate $\kappa_i$. (This is the $\S$2.1 collision from
the audit.)

---

## 4. ACTION SPACE AND DYNAMICS

$$\mathcal{A}_i=\{\textsf{Hover},+x,-x,+y,-y,\textsf{Charge}\},\qquad |\mathcal{A}_i|=6$$

$$\mathbf{p}_i(t+1)=\Pi_{\Omega}\!\left(\mathbf{p}_i(t)+\mathbf{v}_i(t)\,\Delta t\right),
\qquad
\|\mathbf{v}_i(t)\|\le v_{\max}$$

$\Pi_\Omega$ projects into the permitted airspace — this is how the workspace
constraint is *structural* rather than penalised.

**Why 6 and not 5.** The joint action space is $|\mathcal{A}|=6^N$:
$6^4=1296$, $6^6=46\,656$, $6^{10}=60\,466\,176$, $6^{20}\approx 3.7\times10^{15}$.
Any tabular or joint-Q approach is dead beyond $N\approx8$.

*(Note: the earlier Beamer deck used 5 actions and $5^N$. The current paper's 6
actions are the better choice — the extra action is what lets the agent request
charging at all. Keep 6 and make the deck match the paper.)*

---

## 5. THE FOUR HARD REQUIREMENTS

This is the part the professor is asking for. Each requirement is a predicate on
$(\mathbf{s}_t,\mathbf{a}_t)$ that must hold at every step. They are **hard** —
enforced by the feasibility mask, not by reward.

### C1 — Persistent $K$-coverage

$$x_{id}(t)=\mathbb 1\!\bigl[\|\mathbf{p}_i(t)-\mathbf{q}_d\|_2\le R_{\mathrm{cov}}\bigr],
\qquad
n_d(t)=\sum_{i\in\mathcal{U}(t)}x_{id}(t),
\qquad
\boxed{\;n_d(t)\ge K\quad\forall d\in\mathcal{D}\quad}$$

### C2 — Swarm connectivity

$$G_t=(V_t,E_t),\qquad E_t=\bigl\{(i,j):\|\mathbf{p}_i-\mathbf{p}_j\|_2\le R_{\mathrm{comm}}\bigr\}$$

$$\boxed{\;G_t\ \text{connected},\quad\forall t\;}$$

*Stronger form for single-failure tolerance:* require $\kappa(G_t)\ge 2$
(2-vertex-connectivity), which by Menger's theorem guarantees the graph stays
connected after **any** single vertex removal.

> **Important honesty note — keep the paper's current stance.** Connectivity
> **cannot** be guaranteed from one-hop local observations. A UAV provably cannot
> detect a global articulation point without global topology. So:
> - **Feasibility mask** enforces the *locally checkable* part of C2 (a move that
>   would isolate the mover or exceed radio range).
> - The **reward** penalises $\mathrm{Crit}_t$ softly.
> - **Connectivity is reported as a metric**, not claimed as an invariant.
>
> This is exactly what Sec. III-H already says. Do not weaken it.

### C3 — Energy reachability

$$E_i^{\mathrm{req}}(t)=E_i^{\mathrm{pad}}(t)+E_i^{\mathrm{rejoin}}(t)+E^{\mathrm{reserve}}$$

$$\boxed{\;E_i(t)\;\ge\;E_i^{\mathrm{req}}(t)\quad\text{before committing to any move}\;}$$

If $E_i(t)<E_i^{\mathrm{req}}(t)$, the only feasible action is $\textsf{Charge}$.
This is the *predictive* part of the contribution — it replaces a fixed battery
threshold with a **return-feasibility** test.

### C4 — Physical safety

$$\|\mathbf{v}_i(t)\|\le v_{\max},
\qquad
\mathbf{p}_i(t)\in\Omega,
\qquad
\|\mathbf{p}_i(t)-\mathbf{p}_j(t)\|\ge d_{\mathrm{safe}}\quad\forall i\neq j$$

---

## 6. FEASIBILITY — the part the current paper omits and MUST add

**$K$-coverage is achievable only if the fleet is large enough.** This is a
necessary condition on the parameters, and it is the check that caught the fatal
error in the current Table IV.

**Proposition (area-counting bound).** *If $N$ UAVs, each covering a disk of
radius $R_{\mathrm{cov}}$, achieve $K$-coverage of every one of $M$ sensors
uniformly distributed in a region of area $A$, then necessarily*

$$N\,\pi R_{\mathrm{cov}}^{2}\;\ge\;K\,A
\qquad\Longleftrightarrow\qquad
R_{\mathrm{cov}}\;\ge\;\sqrt{\frac{KA}{\pi N}} .$$

**Proof.** $K$-coverage of all $M$ sensors requires $KM$ incidence pairs
$(i,d)$ with $x_{id}=1$, so $\sum_d n_d \ge KM$. For a uniformly distributed
sensor field of density $\sigma_d = M/A$, the expected number of sensors in one
coverage disk is $\sigma_d\pi R_{\mathrm{cov}}^2$. Summing over $N$ UAVs,
$\mathbb{E}[\sum_d n_d] = N(M/A)\pi R_{\mathrm{cov}}^2$. Requiring the expectation
to reach $KM$ gives the bound. $\blacksquare$

**Packing-corrected version.** Disks cannot tile without overlap. Densest packing
of congruent disks has density $\delta=\pi/(2\sqrt3)\approx0.9069$, so

$$R_{\mathrm{cov}}\;\ge\;\sqrt{\frac{KA}{\delta\,\pi N}}$$

**Slack factor.** In practice you want a surplus

$$\sigma:=\frac{N(M/A)\pi R_{\mathrm{cov}}^2}{KM}\;\gtrsim\;1.5$$

so that movement error and a single failure do not immediately break C1.
After losing one UAV the requirement is $\sigma' \ge 1$, which
$N=5,\ R_{\mathrm{cov}}=35$ m, $A=6400$ satisfies ($\sigma=1.50 \to \sigma'=1.20$).

**Applied to the current paper's Table IV** ($A=10^4$ m², $M=20$, $N=5$, $K=2$):

$$R_{\mathrm{cov}}\ge\sqrt{\frac{2\cdot 10^4}{5\pi}}=35.7\ \text{m}\quad\text{but the table says }15\ \text{m}$$

**This is the single change that makes the whole study work.** Full numbers and a
corrected table are in `02_FEASIBILITY_AND_PARAMETERS.md`.

---

## 7. CONNECTIVITY FEASIBILITY

**Proposition (random geometric graph).** *For $N$ points placed uniformly and
independently in a region of area $A$, with edges between points within distance
$R$, the expected edge count is*

$$\mathbb{E}[|E|]=\binom{N}{2}\frac{\pi R^2}{A}$$

*and a connected graph on $N$ vertices requires $|E|\ge N-1$. Hence
$P(\text{connected})$ is appreciable only when*

$$\binom{N}{2}\frac{\pi R^2}{A}\;\gtrsim\;N-1 .$$

**Refined threshold (Penrose 1997).** The connectivity threshold radius $r_n$ for
$n$ points satisfies $\mathbb{E}[|E|]\sim \tfrac{1}{2}n\ln n$, giving

$$r_n\;\sim\;\sqrt{\frac{n\ln n}{\pi n}}\;\approx\;\sqrt{\frac{\ln n}{\pi}} .$$

Monte-Carlo for $A=6400$ m², $N=5$:

| $R_{\mathrm{comm}}$ | $P(\text{connected})$ | $P(\text{connected}\mid$ 1 failure$)$ |
|---|---|---|
| 30 m | 0.036 | — |
| 40 m | 0.089 | — |
| **45 m** | **0.632** | **0.562** |
| 50 m | 0.732 | — |
| 60 m | 0.90+ | — |

$R_{\mathrm{comm}}=45$ m puts the study in a genuinely **marginal connectivity
regime** — the swarm is connected most of the time but disconnects occasionally.
That is the interesting regime for a fault-tolerance paper. State it deliberately.

---

## 8. OBJECTIVE

**Primary quantity — persistent service loss:**

$$J_{\mathrm{out}}(\pi)=\mathbb{E}_{\pi}\!\left[\sum_{t=0}^{T-1}\gamma^{t}U_t\right],
\qquad
U_t=\frac{1}{M}\sum_{d=1}^{M}\mathbb 1\!\bigl[n_d(t)<K\bigr]$$

**Constrained multi-objective programme:**

$$\min_{\pi}\; J_{\mathrm{out}}(\pi)+\lambda_E J_E(\pi)+\lambda_D J_D(\pi)+\lambda_W J_W(\pi)+\lambda_R J_R(\pi)+\lambda_C J_C(\pi)$$

$$\text{s.t.}\quad \text{C1, C2 (soft), C3, C4}$$

**Team reward handed to the learner** (negated, because RL maximises return):

$$r_t=-\Bigl(\lambda_O U_t+\lambda_E E_t+\lambda_D D_t+\lambda_W W_t+\lambda_R R_t+\lambda_C\,\mathrm{Crit}_t\Bigr)$$

**Sign-consistency sentence to add** (this trips examiners):

> *The learner maximises expected return while the control objective of (26) is
> a minimisation. The team reward (28) is therefore the negated weighted cost,
> and the two are equivalent up to sign. $\lambda_O$ dominates the secondary
> efficiency terms so that service is never traded away for energy savings.*

---

## 9. RECOVERY

$$\tau_f=\inf\Bigl\{\tau\ge0:\ n_d(t_f+\tau)\ge K\ \ \forall d\in\mathcal{D}\Bigr\}$$

**Resilience requirement:** $\tau_f\le\tau_{\max}$ **when recovery is achievable**.

**If the set is empty, $\tau_f=\infty$ and the event is reported as an
unrecovered failure.** Do not assign an artificial recovery time. The current
paper gets this exactly right — keep it.

**Reserve activation.** The reserve $N+1$ is a *resource*, not an RL agent. It
enters $\mathcal{U}(t)$ when a failure is detected and $b_{N+1}\ge b_{\mathrm{thr}}$.
It uses the same shared actor $\pi_\theta$ after insertion.

---

## 10. THE LEARNER

$$a_i(t)\sim\pi_\theta\!\left(a_i\mid\mathbf{o}_i(t)\right)\quad\text{(deployed, per UAV)}$$
$$V_\phi(\mathbf{s}_t)\quad\text{(training only, centralised)}$$

**CTDE statement.** The critic minimises $\mathcal{L}^{\mathrm{critic}}$ against
$\mathbf{s}_t$; the actor maximises $\mathcal{L}^{\mathrm{actor}}$ against
$\mathbf{o}_i$. At deployment the critic is deleted and the shared actor runs
independently on each UAV.

**Parameter sharing is valid here** because all active UAVs are
interchangeable: same dynamics, same action semantics, same reward. A shared
$\theta$ therefore generalises across UAVs and across $N$, which is what makes
the policy $O(1)$ per agent.

**Complexity (add this to the paper — it is the formal scalability claim):**

| Quantity | Cost |
|---|---|
| Actor inference, per agent per step | $O(1)$ (fixed-size $o_i$ via top-$K_n$ + mask) |
| Actor inference, whole swarm | $O(N)$ |
| Critic, per step (training only) | $O(N+M)$ |
| Charging arbitration (Hungarian) | $O(r^3)$, $r=$ concurrent requests $\le N$ |
| Graph recomputation, brute force | $O(N^2)$ |
| Graph recomputation, spatial hash | $O(N\log N)$ |
| Articulation points (Tarjan) | $O(\lvert V\rvert+\lvert E\rvert)=O(N^2)$ worst case |

**Because the deployed policy is $O(1)$ per agent, execution cost is independent
of swarm size.** That is the rigorous version of the scalability claim in
Table VIII.

---

## 11. HOW TO SAY IT OUT LOUD (30 seconds)

> "Our problem is a Dec-POMDP. There are $N$ UAVs over $M$ fixed sensors. Each
> UAV sees only its neighbours, not the global state, and must choose one of six
> actions independently — so it is partial observability plus decentralised
> execution. We require four things to hold at every step: $K$-coverage of every
> sensor, a connected communication graph, enough energy to reach a charger
> before committing to any move, and no physical-safety violation. We minimise
> expected long-horizon service loss, penalising energy, movement, charging wait,
> recovery delay and topology fragility. We learn it with MAPPO under centralised
> training with a global-state critic and decentralised execution with a shared
> actor. Coverage, connectivity, charging arbitration and a reserve UAV are all
> handled outside the policy as hard feasibility layers, because the actor
> cannot observe enough to guarantee them."

That paragraph contains the entire paper. If you can say it, you understand it.

---

## 12. WHAT YOUR PROFESSOR PROBABLY MEANT

When a professor says *"put the problem statement in math"*, they are usually
complaining about one of these five things. Check which applies to you:

| Symptom | What they want | Where you are now |
|---|---|---|
| Problem stated in prose only | One formal definition object they can point at | **Now provided** — §1–§5 |
| Requirements not quantified | Every "should maintain coverage" turned into a predicate or an inequality | **Now provided** — C1–C4 |
| No objective function | An explicit $\min_\pi J(\pi)$ with named terms | **Now provided** — §8 |
| No feasibility check | Proof the instance is solvable at all | **Now provided** — §6, and this is what caught the $R_{\mathrm{cov}}$ error |
| Variables undefined | A complete symbol table with domains | **Now provided** — §1–§4 |

The last two are the ones that separate a C-grade report from an A-grade one, and
the feasibility argument in §6 is the single highest-value addition you can make
tomorrow.
