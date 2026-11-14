# Mathematical Reference: MARL Theory, Coverage Theory, Graph/Connectivity Theory, and Energy Modelling

**Compiled:** 29 September 2026
**Purpose:** Rigorous reference for a report on multi-agent reinforcement learning for persistent, fault-tolerant UAV-IoT coverage.

**Notation:** $\mathcal{S}$ state space, $\mathcal{A}$ action space, $N$ agents, $M$ observation dimension, $P$ polygon complexity, $r$ sensor range, $K$ coverage multiplicity, $n$ vertex count, $V$ number of vertices, $E$ edges, $\lambda$ GAE/decay parameter, $\delta$ trust-region radius, $\epsilon$ PPO clip, $\gamma$ discount.

**Verification status.** Every theorem, constant and equation was checked against primary sources (arXiv full text, publisher PDFs, journal TOC pages) during compilation. **Three items could not be verified and are flagged in place with ⚠:** §15 (Orden & López-Polo complexity constants), §17 (Gordon–Orfao–Rote 1999 — see warning), §31 (Lin et al. / Liu et al. partial-charging specifics). Treat those three as *report-author assertions requiring primary-source confirmation*.

---

# PART A — MARL THEORY

## A.1 MDP and Dec-POMDP

### A.1.1 Markov Decision Process

**Definition A.1 (MDP).** $\mathcal{M}=\langle\mathcal S,\mathcal A,P,R,\gamma\rangle$ with $\mathcal S$ finite state space, $\mathcal A$ finite action space, $P:\mathcal S\times\mathcal A\times\mathcal S\to[0,1]$ transition kernel with $\sum_{s'}P(s'|s,a)=1$, $R(s,a,s')$ expected reward, $\gamma\in[0,1)$ discount.

**Definition A.2 (policy).** $\pi:\mathcal S\to\Delta(\mathcal A)$; $\pi^\star\in\arg\max_\pi J(\pi)$.

**Definition A.3 (value functions).**
$$V^\pi(s)=\mathbb E_\pi\!\left[\textstyle\sum_{t\ge0}\gamma^t r_{t+1}\,\Big|\,s_0=s\right],\quad Q^\pi(s,a)=\mathbb E_\pi\!\left[\textstyle\sum_{t\ge0}\gamma^t r_{t+1}\,\Big|\,s_0=s,a_0=a\right].$$

**Derivation (Bellman expectation).** Condition on $(s_0,a_0)=(s,a)$ and split the return at $t=1$:
$$V^\pi(s)=\sum_a\pi(a|s)\sum_{s'}P(s'|s,a)\big[r(s,a)+\gamma V^\pi(s')\big],$$
$$\boxed{\;Q^\pi(s,a)=\sum_{s'}P(s'|s,a)\left[r(s,a)+\gamma\sum_{a'}\pi(a'|s')Q^\pi(s',a')\right].\;}$$

---

### A.1.2 Dec-POMDP

**Definition A.4 (Dec-POMDP; Bernstein, Zilberstein 1996; Oliehoek & Amato 2016).**
$$\mathcal D=\Big\langle \mathcal I,\mathcal S,\{\mathcal O_i\},\{\mathcal A_i\},P,\{R_i\},O,\gamma\Big\rangle,$$
with $\mathcal I=\{1,\dots,N\}$; **global** transition kernel $P:\mathcal S\times\prod_i\mathcal A_i\times\mathcal S\to[0,1]$; rewards $R_i:\mathcal S\times\prod_j\mathcal A_j\times\mathcal S\to\mathbb R$ (fully cooperative: $R_i\equiv R$, one team reward); observation function $O:\mathcal S\times\prod_i\mathcal A_i\times\prod_i\mathcal O_i\to\Omega$ with samples $o_i\sim O(\cdot|s,\mathbf a)$; $\gamma$.

**Joint spaces.** $\mathcal O=\prod_{i=1}^N\mathcal O_i$, $\mathcal A=\prod_{i=1}^N\mathcal A_i$. For continuous actions $a_i\in\mathbb R^M$ the joint action is $\mathbf a\in\mathbb R^{NM}$; for discrete actions $|\mathcal A|=|\mathcal A_i|^N$ — **exponential in $N$**.

**Definition A.5 (decentralised policy class).**
$$\pi^{\mathrm{dec}}=\Big\{\boldsymbol\pi:\ \exists\pi_i\ \text{Markov with}\ \boldsymbol\pi(\mathbf a|s)=\prod_{i=1}^N\pi_i(a_i|o_i)\Big\}.$$

**Definition A.6 (history / observation).** $h_i^t:=(o_i^0,a_i^0,o_i^1,a_i^1,\dots,a_i^{t-1},o_i^{t-1})$.

### Why decentralized execution changes the problem — formal

**Proposition A.7 (effective kernel seen by agent $i$).** With the other policies $\pi_j$ ($j\ne i$) frozen,
$$\bar P_i(s'|s,o_i)=\sum_{\mathbf a^{-i}\in\prod_{j\ne i}\mathcal A_j}\Big[\prod_{j\ne i}\pi_j(a_j|o_j)\Big]\,P(s'|s,a_i,\mathbf a^{-i}).$$

**Proposition A.8 (non-stationarity).** If agent $j$ updates $\pi_j^{(k)}\to\pi_j^{(k+1)}$, then in general $\bar P_i^{(k)}\ne\bar P_i^{(k+1)}$, so $V^{(k)}$ no longer equals $V^{\pi_i^{(k)},\boldsymbol\pi^{-i,(k)}}$. The Bellman operator
$$(\mathcal T^{\pi_i,(k)}V)(s)=\sum_a\pi_i(a|s)\sum_{s'}\bar P_i^{(k)}(s'|s,a)\big[r+\gamma V(s')\big]$$
is **not the same operator across iterations** — the $\gamma$-contraction argument of A.3 fails.

**Exact dynamic-programming cost.** $\bar P_i$ requires a sum over $\prod_{j\ne i}|\mathcal A_j|$ terms, so exact DP is $O(\prod_i|\mathcal A_i|)$ per state. The remedy is a **factored, centralised critic**, not a joint $Q$.

**Example A.9 (2×2 common-reward matrix game — minimal non-stationarity demo).** $R=\begin{pmatrix}1&0\\0&1\end{pmatrix}$. With $\pi_1(1)=\pi_2(1)=\varepsilon$, $J(\varepsilon,\varepsilon)=2\varepsilon^2$. Each agent's greedy best response is to play row/column 1, so simultaneous greedy updates cycle $(1,1)\to(1,2)\to(2,1)\to(2,2)\to(1,1)$ — **non-convergence**. A centralised $V$ breaks the symmetry and has a unique joint optimum at $(1,1)$ where $J=1$.

---

### A.1.3 Joint belief states

**Definition A.10 (belief).** $b^t:\mathcal S\to[0,1]$, $\sum_s b^t(s)=1$, the posterior $\Pr(s_t\mid\mathbf h^t)$.

**Notation convention (used throughout Parts A–D).** $\mathcal S$ denotes the **global** state space, and $s$ is a global state. Where this document writes $\mathbf s=(s^1,\dots,s^N)\in\mathcal S^N$ (A.1.3, A.3), it means either (i) $\mathcal S\equiv\mathcal S^N$ with **factorised** dynamics $P(\mathbf s'|\mathbf s,\mathbf a)=\prod_i P^i(s'^{i}|s,\mathbf a)$ and **localised** observations $O(\mathbf o|\mathbf s,\mathbf a)=\prod_i O_i(o_i|s,a_i)$ — the standard Dec-POMDP assumption, needed for the belief factorisation to be exact — or (ii) $\mathbf s$ is a *sufficient statistic / encoding* of $s\in\mathcal S$ (e.g. a permutation-invariant aggregation such as a DeepSets/attention encoding). Statements requiring the genuine global state (e.g. the PDL of A.3, which is defined on $(\mathcal S,\mathcal A)$) are read with the true $\mathcal S$; statements requiring a *product* structure (belief factorisation, the vectorised critic input of A.11.2) are read with (i). **The two are not interchangeable** — writing $\sum_s b(s)$ while simultaneously assuming $\mathcal S=\mathcal S^N$ silently changes the dimension of the sum from $|\mathcal S|$ to $|\mathcal S|^N$.

**Definition A.11 (local/decentralised belief).** $b_i^t(s)=\Pr(s_t=s\mid h_i^t)$ — the quantity actually available to agent $i$. Generally $b_i^t\ne b^t$ and $b_i^t$ is **not computable from $h_i^t$ alone** when other agents' observations carry information about $s_t$.

**Definition A.12 (Nash equilibrium in belief space).** $\boldsymbol\pi^\star=(\pi_1^\star,\dots,\pi_N^\star)$ satisfies $J(\pi_i',\pi_{-i}^\star)\le J(\pi_i^\star,\pi_{-i}^\star)$ for all $i$ and all decentralised $\pi_i'$.

**Complexity (the formal justification for all of MARL).** Dec-POMDP is **PEXP-complete** (Bernstein, Givan, Zilberstein 1994) — between NP and EXP. Hardness comes from (a) partial observability forcing belief maintenance over $\mathcal S$ and (b) decentralisation forcing the policy onto local histories whose count grows as $\sum_i(|\mathcal O_i||\mathcal A_i|)^t$.

---

## A.2 POMDP belief update equations

**Definition A.13 (POMDP).** $\langle\mathcal S,\mathcal A,P,R,\gamma,\mathcal O,O\rangle$, with policy $\pi(a|b)$ on beliefs.

**Prediction step** (belief update given known action $a_t$):
$$\boxed{\;\bar b_{t+1}(s')=\sum_{s\in\mathcal S}P(s'|s,a_t)\,b_t(s)\;}$$

**Correction step** (sensor update given observation $o_{t+1}$):
$$\boxed{\;b_{t+1}(s')=\frac{O(o_{t+1}|s',a_t)\,\bar b_{t+1}(s')}{\sum_{\tilde s\in\mathcal S}O(o_{t+1}|\tilde s,a_t)\,\bar b_{t+1}(\tilde s)}\;}$$

**Joint / factorised form.** With $\mathbf s'\in\mathcal S^N$, $\mathbf o_{t+1}\in\prod_i\mathcal O_i$, and *decentralised* $O(\mathbf o|s,\mathbf a)=\prod_iO_i(o_i|s,a_i)$:
$$\bar b_{t+1}(\mathbf s')=\sum_{\mathbf s}P(\mathbf s'|\mathbf s,\mathbf a_t)b_t(\mathbf s),\qquad b_{t+1}(\mathbf s')=\frac{\prod_iO_i(o_i^{t+1}|s',a_i)\,\bar b_{t+1}(\mathbf s')}{\sum_{\tilde{\mathbf s}}\prod_iO_i(o_i^{t+1}|\tilde s,a_i)\bar b_{t+1}(\tilde{\mathbf s})}.$$

**Proposition A.14 (sufficiency of the belief).** $\Pr(s_{t+1}\mid h^{t+1})=\Pr(s_{t+1}\mid b_{t+1},a_{t+1})$, so value functions live on beliefs:
$$V^\pi(b)=\sum_a\pi(a|b)\sum_o\sum_{s'}O(o|s',a)\,T(s'|b,a)\,Q^\pi(s',a).$$

**What MAPPO actually does instead (important honesty point).** Modern MARL does **not** maintain $b^t$. Two substitutes:
1. **Observation-history concatenation** (SMAC/GRF practice): input is $o_i^t$ plus previous $k$ observations (approximating $h_i^{t-k:t}$) plus agent-ID one-hot $\mathbf e_i\in\{0,1\}^N$; the network *implicitly learns* the belief filter.
2. **RNN actor/critic:** recurrent state $c_i^t=f(o_i^{t-1},a_i^{t-1},c_i^{t-1})$ trained so that $c_i^t\approx b_i^t$.

**Link to GAE (precise).** The $\lambda$-return below is a *biased, truncated* estimate of the true advantage. This is what makes the GAE derivation (A.6) the correct estimator for the belief-free setting.

---

## A.3 CTDE

**Definition A.15 (CTDE; Lowe et al. 2017; Foerster et al. 2018).** A scheme is **Centralized Training with Decentralized Execution** if there exist (i) during **training**, a centralised critic $V_\phi(s^1,\dots,s^N,a^1,\dots,a^{N-1})$ or $V_\phi(s^1,\dots,s^N)$ using information unavailable at execution (true states, other agents' observations/actions); and (ii) during **execution**, a decentralised actor $\pi_\theta(a_i|o_i)$ depending only on $o_i$. The critic is **discarded at deployment**, so the executed policy class is exactly $\pi^{\mathrm{dec}}$.

**Objective.** $\max_\theta \mathbb E\big[\sum_t\gamma^t\min(r_t(\theta)\hat A_t^{\mathrm{clip}}(\theta),\,r_t(\theta)\hat A_t)\big]$ subject to $\theta$ being executable with only $o_i$.

### Why CTDE works — the precise argument

Write $\mathcal S$ for the **joint/global** state space, $\mathcal A=\mathcal A^N$, and define
$$\rho^{\boldsymbol\pi}_t(s)=(1-\gamma)\sum_{k\ge t}\gamma^{k-t}\Pr_{\boldsymbol\pi}(s_k=s),\qquad J(\boldsymbol\pi)=\mathbb E_{\boldsymbol\pi}\Big[\sum_{t\ge0}\gamma^t r_{t+1}\Big].$$

**Lemma A.15a (Performance Difference Lemma, joint form).** For any two Markov policies $\boldsymbol\pi,\tilde{\boldsymbol\pi}$ on $(\mathcal S,\mathcal A)$ with $Q^{\boldsymbol\pi},V^{\boldsymbol\pi}$ of $\boldsymbol\pi$,
$$\boxed{\;J(\tilde{\boldsymbol\pi})-J(\boldsymbol\pi)\;=\;\frac{1}{1-\gamma}\;\mathbb E_{s\sim\rho^{\boldsymbol\pi}}\;\mathbb E_{\mathbf a\sim\tilde{\boldsymbol\pi}(\cdot|s)}\big[\,A^{\boldsymbol\pi}(s,\mathbf a)\,\big]\;}$$
with the **joint** advantage $A^{\boldsymbol\pi}(s,\mathbf a)=Q^{\boldsymbol\pi}(s,\mathbf a)-V^{\boldsymbol\pi}(s)$, $Q^{\boldsymbol\pi}(s,\mathbf a)=r(s,\mathbf a)+\gamma\mathbb E_{s'}[V^{\boldsymbol\pi}(s')]$. **There is no sum over agents here** — the joint advantage appears exactly once.

*Proof.* Start from $Q^{\boldsymbol\pi}-\frac{1}{1-\gamma}V^{\boldsymbol\pi}$ and note it satisfies the Bellman equation for $\boldsymbol\pi$: $T^\pi r(s,\mathbf a)=Q^\pi(s,\mathbf a)-\frac1{1-\gamma}V^\pi(s)$. Hence, for $v(s,\mathbf a):=Q^{\boldsymbol\pi}(s,\mathbf a)-\frac1{1-\gamma}V^{\boldsymbol\pi}(s)$,
$$v(s,\mathbf a)=r(s,\mathbf a)+\gamma\,\mathbb E_{s'}\!\big[v(s',\mathbf a')\big]_{\mathbf a'\sim\tilde{\boldsymbol\pi}}\qquad\text{(Bellman equation of } \tilde{\boldsymbol\pi}\text{ applied to } v).$$
Iterate the $\tilde{\boldsymbol\pi}$-expectation $k$ times; by induction the remaining tail is $\gamma^k\mathbb E_{\tilde\pi}[v(s_k,\mathbf a_k)]$ with the $k=0$ base case just stated. Since $\|\mathbb E[v]\|_\infty<\infty$ for bounded $v$ and $0\le\gamma<1$, letting $k\to\infty$ gives
$$v(s,\mathbf a)=\mathbb E_{\tilde{\boldsymbol\pi}}\Big[\sum_{t=0}^{k-1}\gamma^t r_{t+1}\Big]+\gamma^k\mathbb E_{\tilde\pi}[v(s_k,\mathbf a_k)].$$
Taking $\mathbf a\sim\tilde{\boldsymbol\pi}(\cdot|s_0)$, dividing by $1-\gamma$ and letting $k\to\infty$:
$$\frac{Q^{\boldsymbol\pi}(s_0,\mathbf a_0)}{1-\gamma}-\frac{V^{\boldsymbol\pi}(s_0)}{1-\gamma}=\frac{1}{1-\gamma}\mathbb E_{\tilde\pi}\Big[\sum_{t\ge0}\gamma^t r_{t+1}\Big]=J(\tilde{\boldsymbol\pi}).$$
Left-hand side is $J(\boldsymbol\pi)+\frac1{1-\gamma}\big(Q^{\boldsymbol\pi}(s_0,\mathbf a_0)-V^{\boldsymbol\pi}(s_0)\big)=J(\boldsymbol\pi)+\frac1{1-\gamma}A^{\boldsymbol\pi}(s_0,\mathbf a_0)$, which rearranges to the boxed identity. $\blacksquare$

**Credit-assigned form (the version that actually needs a sum over $i$).** One may replace the joint $A^{\boldsymbol\pi}$ by **any** collection of terms $c_i(s,\mathbf a)$ satisfying
$$\sum_{i=1}^{N}c_i(s,\mathbf a)\equiv A^{\boldsymbol\pi}(s,\mathbf a)\qquad\text{for all }(s,\mathbf a),$$
and the lemma still holds with $\sum_i\mathbb E_{\tilde\pi}[c_i]$. Two honest instantiations:
- $c_i\equiv A^{\boldsymbol\pi}$ for a single index $i_0$ and $c_i\equiv0$ otherwise (degenerate but exact);
- an **orthogonal-projector decomposition**: let $L$ be the vector of per-agent score functions $\nabla_\theta\log\pi_\theta(a^i|s)$, and let $\boldsymbol\pi^{-i}$ denote the product of all other agents' policies. Since $\tilde\pi_i(a^i|s)=\pi_i(a^i|s)\frac{\tilde\pi_i(a^i|s)}{\pi_i(a^i|s)}$, we have exactly
$$\mathbb E_{\tilde\pi}\Big[\sum_{i=1}^{N}\nabla_{\theta^i}\log\pi_i(a^i|s)\cdot\nabla_{\theta^i}\log\frac{\tilde\pi_i(a^i|s)}{\pi_i(a^i|s)}\cdot c_i\Big]=\mathbb E_{\tilde\pi}\Big[\Big(\sum_i\nabla_{\theta^i}\log\pi_i(a^i|s)\Big)\cdot\sum_i c_i\Big]=\mathbb E_{\tilde\pi}\Big[\nabla_\theta\log\tilde\pi(\mathbf a|s)\cdot A^{\boldsymbol\pi}(s,\mathbf a)\Big],$$
where the last step uses the PDL. So the $c_i$ must be *constructed* to sum to the joint advantage (e.g. the HATRPO/HAPPO decomposition of Kuba et al. 2022, Lemma 1, which recursively peels off one agent's marginal advantage); one may not simply write $N$ copies of the same advantage.

**⚠ Common error.** Writing $J(\tilde{\boldsymbol\pi})-J(\boldsymbol\pi)=\frac{1}{1-\gamma}\sum_i\mathbb E[A_i]$ with $A_i$ all equal to the *same* team advantage inflates the RHS by a factor $N$ and is not a consequence of any theorem.

**The three genuine mechanisms.**
1. **Variance reduction (provable, unbiased).** For any baseline $b(s,\mathbf a_{-i})$ that does not depend on $a_i$, $\mathbb E_\pi[b\,\nabla\log\pi_i(a_i|s)]=0$, so subtracting it leaves the gradient unbiased (Proposition A.19 below), while
$$\operatorname{Var}_\pi(\hat A_b)=\mathbb E[A^2]-\mathbb E\big[\mathbb E(A\mid\text{baseline-info})^2\big].$$
A richer baseline-info (global state) increases the subtracted term and strictly decreases variance. This is the classical baseline-minimisation argument and it is the *real* reason CTDE helps.
2. **Partial mitigation of non-stationarity (heuristic).** The centralised critic absorbs other agents' policy movement into the function approximator, so the actor sees a less rapidly moving target. This is **not** a convergence guarantee.
3. **Zero benefit at execution.** The actor stays in $\pi^{\mathrm{dec}}$. Centralised information buys training-time variance reduction only.

### Assumptions of CTDE (each can fail in a UAV deployment)

| # | Assumption | Failure in UAV-IoT coverage |
|---|---|---|
| A1 | Simulator can supply global state + all observations/actions in training | No simulator in the real world; global state requires a latency-bounded central fabric, contradicting "decentralised execution" |
| A2 | Centralised critic is a fixed-dim function of global state | Global state has dim $O(NM)$; a fixed-size MLP critic degrades in $N$ (§A.11.3) |
| A3 | Decentralised policy is Markov in $o_i$ | Low-altitude occlusion $\Rightarrow$ $o_i$ is not a sufficient statistic; need history/RNN |
| A4 | Reward shared and **stationary** | Persistent coverage with SoC is a *non-stationary-in-time* MDP: $R$ depends on slowly varying battery state, so really $R(s,a,\tau)$. **Genuine gap** |
| A5 | No execution-time communication (or it is folded into $o_i$) | If agents talk at execution, the problem is a Dec-POMDP *with communication* (Oliehoek et al. 2016) with a richer policy class |
| A6 | Homogeneous agents share parameters | Heterogeneous fleets (different battery mass/payload) violate it; parameter sharing can be exponentially worse in the worst case (Kuba et al. 2022, Prop. 1) |

**Explicitly not a guarantee.** CTDE gives no monotonic improvement or convergence guarantee by itself. Guarantees come from combining CTDE with a trust region, and for a rigorous statement one must use either a **joint ratio** (TRPO) or the **centralised trust region over the product of independent ratios** (Sun et al. 2023). This distinction is the crux of A.8 and A.10.

---

## A.4 Policy gradients: REINFORCE and the log-derivative trick

### A.4.1 Setup

$g^\gamma(\theta):=\nabla_\theta J(\theta)$, $J(\theta)=\mathbb E_{\pi_\theta}[\sum_t\gamma^tr_{t+1}]=\int p_\theta(\tau)J(\tau)d\tau$ with $J(\tau)=\sum_{t\ge0}\gamma^tr_{t+1}$.

### A.4.2 The log-derivative identity

**Lemma A.16 (log-derivative trick / score function).** For differentiable density $p_\theta$ and integrable $f$:
$$\nabla_\theta\mathbb E_{X\sim p_\theta}[f(X)]=\int f(x)\nabla_\theta p_\theta(x)dx=\int f(x)p_\theta(x)\nabla_\theta\log p_\theta(x)dx=\mathbb E_{X\sim p_\theta}\big[f(X)\nabla_\theta\log p_\theta(X)\big].$$
*Proof.* Chain: $\nabla_\theta\int fp_\theta=\int f\nabla_\theta p_\theta$; then $\nabla_\theta p_\theta=p_\theta\cdot\nabla_\theta p_\theta/p_\theta=p_\theta\nabla_\theta\log p_\theta$ using $\nabla_\theta\log p_\theta=\nabla_\theta p_\theta/p_\theta$. $\square$

**Corollary A.17 (score of categorical policy).** For $\pi_\theta(a|s)=\mathrm{softmax}_\theta(f_\theta(s,\cdot))_a$:
$$\boxed{\;\nabla_\theta\log\pi_\theta(a|s)=\nabla_\theta f_\theta(s,a)-\sum_{\tilde a}\pi_\theta(\tilde a|s)\nabla_\theta f_\theta(s,\tilde a)\;}$$
For linear logits $f_\theta=\theta^\top\phi(s,a)$: $\nabla_\theta\log\pi_\theta(a|s)=\phi(s,a)-\sum_{\tilde a}\pi_\theta(\tilde a|s)\phi(s,\tilde a)$.

**Corollary A.18 (score of a diagonal Gaussian; used for UAV continuous control).** Let $\pi_\theta(a|s)=\prod_{j=1}^{M}\mathcal N\big(a_j;\,\mu_{\theta,j}(s),\ \sigma^2_{\theta,j}(s)\big)$ with $\mu_{\theta,j},\sigma_{\theta,j}>0$ depending on $s$. Then, componentwise,
$$\frac{\partial}{\partial\theta}\log\pi_\theta(a|s)=\sum_{j=1}^{M}\left[\underbrace{\frac{a_j-\mu_{\theta,j}(s)}{\sigma^2_{\theta,j}(s)}\,\nabla_\theta\mu_{\theta,j}(s)}_{\text{mean term}}\;+\;\underbrace{\left(\frac{(a_j-\mu_{\theta,j}(s))^2}{\sigma^2_{\theta,j}(s)}-1\right)\nabla_\theta\log\sigma_{\theta,j}(s)}_{\text{scale term}}\right].$$
*Derivation.* The $j$-th factor contributes $-\frac{(a_j-\mu_j)^2}{2\sigma_j^2}-\log\sigma_j$. Differentiate the first term with the chain rule: $\nabla_\theta\sigma_j^{-2}=-2\sigma_j^{-3}\nabla_\theta\sigma_j$, so
$\nabla_\theta\big[-\tfrac12(a_j-\mu_j)^2\sigma_j^{-2}\big]=\tfrac{(a_j-\mu_j)^2}{\sigma_j^2}\nabla_\theta\log\sigma_j+\frac{a_j-\mu_j}{\sigma_j^2}\nabla_\theta\mu_j$; and $\nabla_\theta[-\log\sigma_j]=-\nabla_\theta\log\sigma_j$. The two $\nabla_\theta\log\sigma_j$ terms combine to the coefficient $\big((a_j-\mu_j)^2/\sigma_j^2-1\big)$. $\square$

**Two corollaries used later.**
1. **With state-independent $\sigma$ (MAPPO's UAV velocity commands).** The scale term vanishes and the score reduces to the mean term, so $\nabla_\theta\log\pi_\theta(a|s)=\frac{a-\mu_\theta(s)}{\sigma^2}\odot\nabla_\theta\mu_\theta(s)$.
2. **Zero conditional mean (needed by Prop. A.21 and the TRPO bound).** $\mathbb E_{a\sim\pi_\theta(\cdot|s)}[\nabla_\theta\log\pi_\theta(a|s)]=0$, since for each $j$ the mean term has mean $0$ by symmetry of the Gaussian and the scale term has expectation $\frac{\mathbb E[(a_j-\mu_j)^2]}{\sigma_j^2}-1=\frac{\sigma_j^2}{\sigma_j^2}-1=0$.

**⚠ Common error.** The scale coefficient is $\frac{(a_j-\mu_j)^2}{\sigma_j^2}-1$ — it contains **no** $\log$ of any residual. Expressions such as $\log\frac{a_j-\mu_j}{\sigma_j}$ arise from integrating a Gaussian score and are not scores.

### A.4.3 REINFORCE — full derivation

Using Lemma A.16 with $X=\tau$: $g^\gamma(\theta)=\mathbb E_\theta\big[J(\tau)\nabla_\theta\log p_\theta(\tau)\big]$. Factor $p_\theta(\tau)=\prod_t\pi_\theta(a_t|s_t)P(s_{t+1}|s_t,a_t)$; the $P$ terms are $\theta$-independent and $\log$ of a product is a sum, so $\nabla_\theta\log p_\theta(\tau)=\sum_{t\ge0}\nabla_\theta\log\pi_\theta(a_t|s_t)$. Therefore
$$g^\gamma(\theta)=\mathbb E_\theta\Big[\Big(\sum_{t\ge0}\gamma^tr_{t+1}\Big)\Big(\sum_{t\ge0}\nabla_\theta\log\pi_\theta(a_t|s_t)\Big)\Big].$$
The expected score of a non-selected action vanishes ($\sum_a\pi(a|s)\nabla\log\pi(a|s)=\nabla\sum_a\pi(a|s)=0$), so
$$\boxed{\;g^\gamma(\theta)=\sum_{t\ge0}\gamma^t\,\mathbb E_\theta\big[r_{t+1}\nabla_\theta\log\pi_\theta(a_t|s_t)\big]\;}$$
— **REINFORCE** (Williams 1992). Sample estimate with horizon $T$: $g^\gamma\approx\sum_{t<T}\gamma^tr_{t+1}\nabla_\theta\log\pi_\theta(a_t|s_t)$.

**Variance.** Grows as $O(T^2)$ in the horizon (each of $T$ score terms times a partial return of order $T$; $O(T^2)$ cross-terms). This motivates $V/Q/A$ entirely.

### A.4.4 Baseline property (unbiasedness)

**Proposition A.19 (baseline invariance).** For any $b(s)$ depending on state only,
$$\mathbb E_{\pi_\theta}\Big[\sum_t\gamma^tb(s_t)\nabla_\theta\log\pi_\theta(a_t|s_t)\Big]=\sum_t\gamma^t\mathbb E\big[b(s_t)\underbrace{\mathbb E_{a_t\sim\pi}\nabla_\theta\log\pi(a_t|s_t)}_{=\nabla_\theta\sum_a\pi(a|s)=0}\big]=0.$$
Hence the estimator with $(r_{t+1}-b(s_t))$ is **unbiased**. The same holds for a baseline $b(s,\mathbf a_{-i})$ independent of $a_i$ — the multi-agent CTDE version. This is the entire justification for actor–critic: $V_\phi$ is a *learned* state-only baseline.

---

## A.5 Value, Q, advantage $A=Q-V$

**Definition A.20.** $A^\pi(s,a):=Q^\pi(s,a)-V^\pi(s)$.

**Decomposition intuition.** $Q^\pi(s,a)=\underbrace{V^\pi(s)}_{\text{state quality}}+\underbrace{A^\pi(s,a)}_{\text{action quality}}$; the first term is $a$-independent and carries no information about *which action to take*.

**Proposition A.21 (formal justification).** $\mathbb E_{a\sim\pi(\cdot|s)}\big[V^\pi(s)\nabla_\theta\log\pi_\theta(a|s)\big]=V^\pi(s)\nabla_\theta\sum_a\pi_\theta(a|s)=0.$
Hence $Q^\pi$ and $A^\pi$ give the **same expected gradient** (both equal a baseline plus an $a$-independent constant), but $A^\pi$ has strictly lower variance. $\square$

**Exact relationship to the TD residual.** $A^\pi(s_t,a_t)=r_{t+1}-V^\pi(s_t)+\gamma V^\pi(s_{t+1})-V^\pi(s_t)=\delta^\pi_t$ with $\delta^\pi_t:=r_{t+1}+\gamma V^\pi(s_{t+1})-V^\pi(s_t)$. When $V=V^{\pi,\gamma}$ is exact, $\delta^\pi_t$ is an **unbiased** one-step estimator of $A^{\pi,\gamma}$:
$$\mathbb E_{s_{t+1}}[\delta_t]=\mathbb E\big[r_{t+1}+\gamma V^{\pi,\gamma}(s_{t+1})\big]-V^{\pi,\gamma}(s_t)=Q^{\pi,\gamma}(s_t,a_t)-V^{\pi,\gamma}(s_t)=A^{\pi,\gamma}(s_t,a_t).$$
(Verified verbatim: Schulman et al. 2016, Eq. 10.)

**Multi-agent.** For a shared team reward, $A^{\boldsymbol\pi}(s,\mathbf a)=Q^{\boldsymbol\pi}(s,\mathbf a)-V^{\boldsymbol\pi}(s)$; MAPPO computes **one** $A^{\boldsymbol\pi}$ and reuses it for every agent's ratio — a deliberate choice, replaced by the joint decomposition of Kuba et al. (2022) in HATRPO/HAPPO (A.9.5).

---

## A.6 GAE — full derivation, bias–variance, TD($\lambda$) equivalence

**Reference:** Schulman, Moritz, Levine, Jordan, Abbeel, *High-Dimensional Continuous Control Using Generalized Advantage Estimation*, ICLR 2016, arXiv:1506.02438 (earlier: NIPS 2015, "Generalized Advantage Estimation for Policy Gradients").

### A.6.1 Construction

**Definition A.22 ($k$-step estimator).** With the reward-indexing convention fixed throughout A.1–A.12 as $r_{t+1}$ = reward received on the transition $s_t\to s_{t+1}$,
$$\hat A^{V,k}_t:=\sum_{l=0}^{k-1}\gamma^l\delta^V_{t+l},\qquad \boxed{\;\delta^V_t:=r_{t+1}+\gamma V(s_{t+1})-V(s_t)\;}$$
(Schulman et al. 2016 write $\delta^V_t=r_t+\gamma V(s_{t+1})-V(s_t)$ with the *other* convention $r_t$ = reward on $s_t\to s_{t+1}$; the two are the same formula with the index shifted by one, and mixing them is the usual source of off-by-one GAE implementations.)

**Derivation (telescoping).** Expanding: $\hat A^{V,k}_t=\sum_{l<k}\gamma^lr_{t+l}+\gamma^kV(s_{t+k})-V(s_t)$, because the $\gamma^lV(s_{t+l+1})$ terms cancel against the $\gamma^{l+1}V(s_{t+l+1})$ of the next summand. $\square$

**Definition A.23 (GAE).** For $\lambda\in[0,1]$: $\hat A^{\mathrm{GAE}(\gamma,\lambda)}_t:=(1-\lambda)\sum_{k\ge1}\lambda^{k-1}\hat A^{V,k}_t$.

**Full derivation of the closed form.** Swap the order of summation and collect by $\delta^V_{t+l}$. For fixed $l$, the contributing values of $k$ are $k=l+1,l+2,\dots$, so
$$\sum_{k=l+1}^\infty\lambda^{k-1}\gamma^{l}=\gamma^{l}\sum_{j\ge0}\lambda^{l+j}=\gamma^l\frac{\lambda^{l}}{1-\lambda}=\frac{(\gamma\lambda)^l}{1-\lambda}.$$
Hence, cancelling $(1-\lambda)$:
$$\boxed{\;\hat A^{\mathrm{GAE}(\gamma,\lambda)}_t=\sum_{l=0}^\infty(\gamma\lambda)^l\,\delta^V_{t+l}\;}$$
(Schulman et al. 2016, Eq. 16 — verified.)

**Boundary cases.** $\lambda=1$: $\hat A_t=\sum_{l\ge0}\gamma^l\delta^V_{t+l}=\sum_{l\ge0}\gamma^lr_{t+l}-V(s_t)$ — MC return minus baseline, **unbiased for any $V$**, high variance. $\lambda=0$: $\hat A_t=\delta^V_t$ — one-step TD residual, **biased unless $V=V^{\pi,\gamma}$**, low variance.

**Resulting estimator.** $\hat g^{\mathrm{GAE}}=\mathbb E\big[\sum_t\nabla_\theta\log\pi_\theta(a_t|s_t)\sum_{l\ge0}(\gamma\lambda)^l\delta^V_{t+l}\big]$; unbiased iff $\lambda=1$.

### A.6.2 Bias–variance as a function of $\lambda$ — two *distinct* effects

Schulman et al. 2016 §3 stress that $\gamma$ and $\lambda$ play different roles; conflating them is the usual error.

1. **$\gamma<1$ biases the gradient estimate regardless of $V$ accuracy.** Reason: $g^\gamma\ne g$ — the discounted objective is a *different* objective. Also $\gamma$ sets the scale of $V^{\pi,\gamma}$: for per-step reward of order $R$, $V\approx R/(1-\gamma)$, which inflates advantage magnitudes and gradient scale.
2. **$\lambda<1$ biases only when $V$ is inaccurate.** Writing $\varepsilon_t:=V^{\pi,\gamma}(s_t)-V(s_t)$ and $\delta^\pi_t:=r_{t+1}+\gamma V^{\pi,\gamma}(s_{t+1})-V^{\pi,\gamma}(s_t)=A^{\pi,\gamma}(s_t,a_t)$:
$$\hat A^{\mathrm{GAE}}_t-A^{\pi,\gamma}(s_t,a_t)=\sum_{l\ge0}(\gamma\lambda)^l\big(\delta^V_{t+l}-\delta^\pi_{t+l}\big),$$
so the bias is an exponentially-weighted average of the value errors:
$$\mathrm{Bias}\asymp\sum_{l\ge0}(\gamma\lambda)^l\varepsilon_{t+l}.$$

**Monotone statements (rigorous).** $\lambda\uparrow1\Rightarrow$ variance $\uparrow$, bias $\to0$. $\lambda\downarrow0\Rightarrow$ variance $\downarrow$, bias $\uparrow$. Effective bootstrap horizon: weights $(\gamma\lambda)^l$ decay with time constant $\approx(1-\gamma\lambda)^{-1}$, so $\lambda\approx1-\frac{1-\gamma}{\gamma}k$ gives an effective $k$-step backup. Empirically (MuJoCo): best $\lambda\in[0.9,0.99]$, best $\gamma\approx0.99$; **$\lambda=0$ is disastrous in high dimensions**, **$\lambda=1$ is very noisy**. MAPPO defaults: $\gamma=0.99$, $\lambda=0.95$.

### A.6.3 TD($\lambda$) equivalence theorem

> **Theorem A.24 (λ-return minus $V$ = GAE).** Define the $n$-step bootstrapped return and the $\lambda$-return by
> $$G_t^{(n)}=\sum_{l=0}^{n-1}\gamma^{l}r_{t+l}+\gamma^{n}V(s_{t+n}),\qquad G_t^\lambda=(1-\lambda)\sum_{n=1}^{\infty}\lambda^{n-1}G_t^{(n)} .$$
> Then, **identically as random variables**,
> $$\boxed{\;G_t^\lambda-V(s_t)=\hat A^{\mathrm{GAE}(\gamma,\lambda)}_t=\sum_{l=0}^{\infty}(\gamma\lambda)^l\delta^V_{t+l}\;}$$

*Proof.* (i) **Telescoping identity.** By the derivation above, $\hat A^{V,n}_t=\sum_{l=0}^{n-1}\gamma^{l}\delta^V_{t+l}$, and separately
$$\sum_{l=0}^{n-1}\gamma^{l}r_{t+l+1}+\gamma^{n}V(s_{t+n})-V(s_t)=\sum_{l=0}^{n-1}\gamma^{l}\big(r_{t+l+1}+\gamma V(s_{t+l+1})-V(s_{t+l})\big)=\sum_{l=0}^{n-1}\gamma^{l}\delta^V_{t+l}.$$
Hence
$$G_t^{(n)}-V(s_t)=\Big[\sum_{l=0}^{n-1}\gamma^{l}r_{t+l+1}+\gamma^{n}V(s_{t+n})\Big]-V(s_t)=\hat A^{V,n}_t. \tag{A.24.1}$$
(ii) Substitute (A.24.1) into the $\lambda$-return definition:
$$G_t^\lambda-V(s_t)=(1-\lambda)\sum_{n\ge1}\lambda^{n-1}\hat A^{V,n}_t\overset{\text{Def. A.23}}{=}\hat A^{\mathrm{GAE}(\gamma,\lambda)}_t. \qquad\blacksquare$$
Note that the identity holds **pointwise on trajectories**, not merely in expectation — this is an algebraic rewriting, which is why GAE is exactly the $\lambda$-return advantage and not merely similar to it.

**Independent check via the λ-return recursion.** With $G_t^{(0)}=V(s_t)$ and $G_t^{(n)}=r_{t+1}+\gamma G_{t+1}^{(n-1)}$,
$$\begin{aligned}
G_t^\lambda&=(1-\lambda)\sum_{n\ge1}\lambda^{n-1}G_t^{(n)}\\
&=(1-\lambda)\sum_{n\ge1}\lambda^{n-1}\Big(r_{t+1}+\gamma G^{(n-1)}_{t+1}\Big)
=r_{t+1}+\gamma(1-\lambda)\sum_{m\ge0}\lambda^{m}G^{(m)}_{t+1}\qquad(m:=n-1)\\
&=r_{t+1}+\gamma(1-\lambda)\Big[\sum_{m\ge1}\lambda^{m-1}G^{(m)}_{t+1}+\sum_{m\ge0}\lambda^mG^{(m)}_{t+1}-\sum_{m\ge1}\lambda^{m-1}G^{(m)}_{t+1}\Big]\\
&=r_{t+1}+\gamma(1-\lambda)\Big[\underbrace{\frac{G^\lambda_{t+1}}{1-\lambda}}_{m\ge1\ \text{part}}+\underbrace{\lambda\frac{G^\lambda_{t+1}}{1-\lambda}}_{m\ge1\ \text{part}}-\sum_{m\ge1}\lambda^{m-1}G^{(m)}_{t+1}\Big]\\
&=r_{t+1}+\gamma\big[G^\lambda_{t+1}-(1-\lambda)V(s_{t+1})\big].
\end{aligned}$$
Now set $A^\lambda_t:=G^\lambda_t-V(s_t)$. The recursion gives
$$A^\lambda_t=r_{t+1}+\gamma\big[A^\lambda_{t+1}+V(s_{t+1})\big]-\gamma(1-\lambda)V(s_{t+1})-V(s_t)=r_{t+1}+\gamma A^\lambda_{t+1}+\lambda\gamma V(s_{t+1})-V(s_t)=\delta^V_t+\gamma\lambda A^\lambda_{t+1}.$$
This is **exactly the GAE recursion** (A.6.4), so unrolling from $A^\lambda_{N}\to0$ gives $A^\lambda_t=\sum_{l\ge0}(\gamma\lambda)^l\delta^V_{t+l}$. $\square$

**Why the reindexing step is legitimate** (the one place people go wrong): $\sum_{m\ge0}\lambda^mG^{(m)}_{t+1}=\lambda\sum_{m\ge0}\lambda^mG^{(m)}_{t+1}$ would be wrong; the correct statement is that the $m\ge1$ part of $\sum_{m\ge0}\lambda^mG^{(m)}$ equals $\lambda\cdot G^\lambda/(1-\lambda)$ while the $m=0$ term contributes $\lambda^0V(s_{t+1})=V(s_{t+1})$. Hence $\sum_{m\ge0}\lambda^mG^{(m)}_{t+1}=\frac{\lambda}{1-\lambda}G^\lambda_{t+1}+V(s_{t+1})$, and multiplying by $(1-\lambda)$ gives $\lambda G^\lambda_{t+1}+(1-\lambda)V(s_{t+1})$, which is the third line above.

**The precise statement, and the widespread misstatement.** TD($\lambda$) *estimates the value function* $G^\lambda\to V^{\pi}$ (biased for $\lambda<1$, variance $\to0$ as $\lambda\to0$); GAE *estimates the advantage* $G^\lambda-V\to A^\pi$ (unbiased at $\lambda=1$, variance $\to0$ as $\lambda\to0$). Schulman et al. 2016 §4: *"The construction we used above is closely analogous to the one used to define TD(λ) […] however TD(λ) is an estimator of the value function whereas here we are estimating the advantage function."* Note the parameter roles differ: TD($\lambda$) bootstraps with discount $\gamma$ and trace decay $\lambda$; GAE uses the **single** effective factor $\gamma\lambda$, so $\lambda_{\mathrm{TD}}$ and $\lambda_{\mathrm{GAE}}$ are not interchangeable numerically.

**Interpretation (the point to make in a report).** TD($\lambda$) estimates $V$; GAE estimates $A$ **with the same weighting**. So "use GAE with $\lambda$" = "use a TD($\lambda$) backup, applied to the advantage instead of the value." Verbatim (Schulman et al. 2016): *"The construction we used above is closely analogous to the one used to define TD($\lambda$) […] however TD($\lambda$) is an estimator of the value function whereas here we are estimating the advantage function."*

**⚠ Do not conflate GAE with potential-based reward shaping (Ng–Harada–Russell).** They *look* alike and it is tempting to write "GAE is potential-based shaping with $\Phi=V$, discount $\gamma\lambda$," but that is **false**, and the difference is instructive:
- PBRS with potential $\Phi$ and discount $\tilde\gamma$ produces the *reward* $\tilde r_{t+1}=r_{t+1}+\tilde\gamma\Phi(s_{t+1})-\Phi(s_t)$. For $\tilde\gamma=\gamma$ and $\Phi=V$ this is $r_{t+1}+\gamma V(s_{t+1})-V(s_t)$ — a reward whose structure matches $\delta^V$ but whose *discounted return is unchanged in value*: by the Ng–Harada–Russell result, $J_{\tilde r}(\pi)=J_r(\pi)-\frac{1}{1-\gamma}\mathbb E[\Phi(s_0)]$, so the shaping **does not bias the objective for any $\lambda$**. That is the whole point of PBRS.
- GAE instead forms a $\gamma\lambda$-weighted sum of $\delta^V$'s. Setting $\tilde\gamma=\gamma\lambda\ne\gamma$ would break PBRS's policy-invariance requirement, and no potential makes the GAE *return* policy-invariant; GAE is a **variance-reduction estimator of the gradient**, not a redefinition of the objective.

The correct one-line relationship: the GAE recursion $\hat A_t=\delta^V_t+\gamma\lambda\hat A_{t+1}$ and the λ-return recursion $G^\lambda_t=r_{t+1}+\gamma G^\lambda_{t+1}-\gamma(1-\lambda)V(s_{t+1})$ differ only in where $\hat A$ sits relative to the baseline $V$; **subtracting $V$ from a TD($\lambda$) quantity yields GAE** (proved in A.6.3). No reward-shaping claim is needed, and none is correct.

### A.6.4 Finite-episode form (what is implemented)

$$V(H_N)=0,\qquad \delta^V_t=R_{t+1}+\gamma V(H_{t+1})-V(H_t),\qquad \hat A^{\mathrm{GAE}(\gamma,\lambda)}_t=\sum_{l=0}^{N-t-1}(\gamma\lambda)^l\delta^V_{t+l}.$$
Computed by the **reverse-time recurrence**:
```text
for t = T-1, ..., 0:  adv[t] = delta[t] + gamma*lam*(1-done[t+1])*adv[t+1]
                     ret[t] = adv[t] + value[t]     # value-normalized variant, §A.9.4
```
Cost $O(T)$ per environment step — **no extra asymptotic cost** over the forward pass. This is the computational reason GAE is used universally.

---

## A.7 TRPO — full math

**Reference:** Schulman, Wolski, Dhariwal, Radford, Klimov, *Trust Region Policy Optimization*, ICML 2015, arXiv:1502.05477 (original 2013 version arXiv:1305.5991, using natural gradients / CG with Fisher-vector products).

### A.7.1 The theory

**PDL.** $J(\tilde\pi)-J(\pi)=\frac{1}{1-\gamma}\mathbb E_{s\sim\rho^\pi}\big[\sum_a\tilde\pi(a|s)A^\pi(s,a)\big]$.
*Proof sketch.* Substitute $A^\pi=Q^\pi-V^\pi$ and use $\mathbb E_{\tilde\pi}[A^\pi(s,a)]=Q^{\tilde\pi}(s,a)-V^\pi(s)$; the recursion $V^\pi=\mathbb E_\pi[Q^\pi]$ telescopes against the visit distribution. $\square$

**Definition A.25a (Surrogate value function).** The Fisher information matrix is
$$F_\theta:=\mathbb E_{s\sim\rho^{\theta_{\rm old}},\mathbf a\sim\pi_{\theta_{\rm old}}}\Big[\nabla_\theta\log\pi_{\theta_{\rm old}}(\mathbf a|s)\,\nabla_\theta\log\pi_{\theta_{\rm old}}(\mathbf a|s)^\top\Big].$$
Note $F\succeq0$ automatically (it is a covariance of scores) and, since $\mathbb E[\nabla_\theta\log\pi]=0$ (Prop. A.21), $\mathbb E[F]$ has a **zero eigenvalue along the constant direction**: for softmax over linear logits with feature dim $m<|\mathcal A|$, $F=\mathbb E_s\big[\Phi^\top\mathrm{Cov}_{a\sim\pi}(\phi(s,a))\Phi\big]$ is singular, so TRPO works in the subspace orthogonal to the null space. Let $x:=\nabla_\theta\log\pi_{\theta_{\rm old}}(\mathbf a|s)$ (a *random* column vector, not a matrix) and write
$$g:=\mathbb E_s[x],\qquad s^\star:=\sqrt{\frac{\delta}{g^\top F^{-1}g}}\,F^{-1}g .$$
(On the subspace where $F$ is invertible; otherwise project $g$ onto $\mathrm{null}(F)^\perp$ first. This is why implementations add a small damping term $\epsilon\mathbb I$.)

> **Theorem A.25b (TRPO lower bound; Schulman et al. 2015, Thm 4 / Lemma 6).** There exist constants $C$ depending only on $\gamma$ and the reward bound (with $|r|\le R_{\max}$) such that for every policy $\tilde\pi$,
> $$J(\tilde\pi)\;\ge\;\frac{1}{1-\gamma}\;\mathbb E_{s\sim\rho^{\theta_{\rm old}}}\mathbb E_{\mathbf a\sim\pi_{\theta_{\rm old}}}\!\big[\hat A^{\theta_{\rm old}}(s,\mathbf a)\,\big]\;+\;\frac{1}{1-\gamma}\;\mathbb E_s\big[x^\top F^{-1}x\big]\;-\;\frac{C}{1-\gamma}\;\mathbb E_s\big[x^\top F x\big].$$

*Derivation.* (i) By the PDL with $\tilde\pi$,
$$J(\tilde\pi)-J(\pi_{\theta_{\rm old}})=\frac{1}{1-\gamma}\mathbb E_{s}\mathbb E_{\mathbf a\sim\pi_{\theta_{\rm old}}}\big[A^{\pi_{\rm old}}(s,\mathbf a)\big],$$
and by definition $\mathbb E_{\pi_{\rm old}}[A^{\pi_{\rm old}}]=0$, so the first term vanishes identically — a lower bound on the improvement must come from the *second-order* part.
(ii) The key Taylor expansion (Schulman et al. 2015, Lemma 3) is for the **surrogate** objective $L(\theta)=\mathbb E_s[x^\top(\theta-\theta_{\rm old})]$, using the "score" analogue of $f$-divergence results:
$$L(\theta)-L(\theta_{\rm old})=\mathbb E\!\left[\frac{1}{2}\Delta\theta^\top F\Delta\theta\right]+\mathbb E\!\left[\sum_{i\ge3}\frac{\Delta\theta^\top\nabla^{i-1}\pi_{\theta_{\rm old}}}{\|x\|}\;\frac{\Delta\theta^{i-1}}{i!}x\right],\qquad \Delta\theta:=\theta-\theta_{\rm old}.$$
The remainder is bounded by $\frac{C}{6}\mathbb E[(\Delta\theta^\top F\Delta\theta)^{3/2}]$-type terms, and is made $O(\Delta\theta^2)$ after multiplying by the advantage; the standard treatment (Schulman et al. 2015 Eq. 9 + the surrounding discussion) absorbs it into $\frac{C}{2}\mathbb E_s[x^\top F x]$ by the inequality $\mathbb E[\|F^{1/2}\Delta\theta\|^2\cdot\|F^{1/2}\Delta\theta\|]\le C\|F^{1/2}\Delta\theta\|^2$ valid inside a trust region.
(iii) For the maximiser $\Delta\theta^\star=\sqrt{\delta}\,F^{-1}g/\|F^{-1}g\|$, substitute directly: the gain term is
$$\mathbb E_s\big[(\Delta\theta^\star)^\top x\big]=\sqrt\delta\;\frac{g^\top F^{-1}g}{\sqrt{\delta/(g^\top F^{-1}g)}\cdot\|F^{-1}g\|}\Big|_{\rm exact}=\frac{\delta\,\big(g^\top F^{-1}g\big)}{\|F^{-1}g\|^2}\cdot\frac{\|F^{-1}g\|}{\sqrt\delta}\cdot\frac1{\sqrt\delta}\ \Rightarrow\ \sqrt\delta\,\|F^{-1/2}g\|,$$
and since $g=F(F^{-1}g)$, the quadratic penalty is $\frac{C}{2}\mathbb E_s[x^\top Fx]\cdot\frac{\delta}{g^\top F^{-1}g}=\frac{C\delta}{2}$. Net gain $=\sqrt\delta\,\|F^{-1/2}g\|-\frac{C\delta}{2}>0$ for $\delta<\frac{2}{C}\|F^{-1/2}g\|^{2}=\frac{2g^\top F^{-1}g}{C}$. Hence
$$\boxed{\;J\big(\pi_{\theta_{\rm old}+\Delta\theta^\star}\big)\;\ge\;J(\pi_{\theta_{\rm old}})\;+\;\frac{1}{1-\gamma}\Big(\sqrt\delta\,\big\|F^{-1/2}g\big\|-\tfrac{C\delta}{2}\Big)\;>\;J(\pi_{\theta_{\rm old}})\;}$$

**⚠ Corrections to the common malformed version of this theorem.** (i) $x$ is a *vector* $\nabla_\theta\log\pi(\mathbf a|s)$, and $F^{-1}$ is $|\theta|\times|\theta|$; the bound is $\mathbb E_s[x^\top F^{-1}x]-\frac{C}{2}\mathbb E_s[x^\top Fx]$, **not** $\mathbb E[x^\top F^{-1}x]-\frac{C}{2}\mathbb E[x^\top F^{-1}x]$ — the two $F$ occurrences must differ, and the dimensions only match with $F$ in the penalty. (ii) The constant multiplies $\mathbb E_s[x^\top Fx]$, i.e. the *Fisher quadratic form in the mean-field/Fisher metric*, not the KL. (iii) Substituting $\Delta\theta=C F^{-1}x$ pointwise (with $x$ random) does **not** give "gain $C$, penalty $C/2$"; the substitution must be made with the *deterministic* vector $g$ (or the mean of the score-weighted quantities), as done above. (iv) $C$ depends on $\gamma$ and the reward bound, not on $\theta$.

**This is the mathematical content of "monotonic improvement"**, and it is a guarantee over the *true* objective $J$ — not over the surrogate. It holds only in the region where the third-order remainder is controlled.

### A.7.2 The TRPO objective

$$\max_\theta\ L_{\mathrm{sur}}(\theta,\theta_{\mathrm{old}})=\mathbb E_{s\sim\rho^{\theta_{\mathrm{old}}},\mathbf a\sim\pi_{\theta_{\mathrm{old}}}}\big[r(\mathbf a|s)A^{\theta_{\mathrm{old}}}(s,\mathbf a)\big]$$
$$\text{s.t.}\quad \mathbb E_{s\sim\rho^{\theta_{\mathrm{old}}}}\big[D_{\mathrm{KL}}\big(\pi_{\theta_{\mathrm{old}}}(\cdot|s)\|\pi_\theta(\cdot|s)\big)\big]\le\delta.$$

**Remark (exact vs average KL — a real subtlety).** The bound A.25 is stated in terms of the *second-order Taylor quantity* $\mathbb E[x^\top Fx]$, not the average KL itself. The Bernstein–Fisher expansion $D_{\mathrm{KL}}(p_\theta\|p_{\theta_{\rm old}})=\frac12(\theta-\theta_{\rm old})^\top F(\theta-\theta_{\rm old})+O(\|\Delta\theta\|^3)$ (valid when the score has zero conditional mean) makes the KL constraint **equivalent to a trust region in the Fisher metric**; TRPO is therefore a natural-gradient method with step $\Delta\theta\propto F^{-1}\nabla L$. In practice Schulman et al. 2015 present both: constrain the **average** $\mathrm{KL}(\bar\pi\|\pi)$ plus a **cumulative** per-state penalty $\beta\sum_s\mathrm{KL}(\pi_{\rm old}(s)\|\pi_\theta(s))$ with backtracking line search, or constrain the **maximum** per-state KL.

### A.7.3 Solving it: conjugate gradient + Fisher-vector products

$\max_\Delta g^\top\Delta$ s.t. $\frac12\Delta^\top F\Delta\le\delta$ has solution $\Delta^\star=\sqrt{\frac{\delta}{g^\top F^{-1}g}}F^{-1}g$. Inverting $F\in\mathbb R^{|\theta|\times|\theta|}$ is infeasible. Lagrangian $\mathcal L=g^\top\Delta-\frac\alpha2(\Delta^\top F\Delta-\delta)$, $\nabla_\Delta\mathcal L=g-\alpha F\Delta=0\Rightarrow\Delta=\alpha^{-1}F^{-1}g$, with $\alpha=\sqrt{\delta/(g^\top F^{-1}g)}$.

**Algorithm (Schulman et al. 2015, Alg. 1–2).**
1. Batch of $N$ samples; $\hat g=\frac1N\sum_i\nabla\log\pi(\mathbf a_i|s_i)\hat A_i$; accumulator $\hat X=\frac1N\sum_i\nabla\log\pi_i\hat A_i\hat A_i^\top$.
2. **Fisher-vector product** $\hat Fv\approx\frac1N\sum_i\nabla\log\pi(\mathbf a_i|s_i)\big(\nabla\log\pi(\mathbf a_i|s_i)^\top v\big)$ — **one backward pass** suffices, because a Hessian–vector product with weights removed equals a gradient of a weighted log-likelihood.
3. Solve $Fx=g$ approximately by **conjugate gradient**, $K$ iterations (typically 10), using the FVP as operator.
4. $\hat s=\sqrt{\frac{\delta}{g^\top x}}$; step $\Delta x=\hat s x$.
5. Shrink $\hat s$ by $\alpha:=0.5$ until $\mathbb E_s[D_{\mathrm{KL}}]\le\delta$; then **line search** on the actual objective; accept.
6. Gradient step on $V_\phi$ with Huber loss on $(V_\phi(s_t)-\hat R_t)^2$.

**Cost:** $O(K)$ gradient-equivalent passes with $K\ll|\theta|$ — a small constant multiple of PPO's cost. This is exactly why PPO (first-order) is the practical default.

### A.7.4 Continuous control: closed-form KL

For $\pi_\theta(\mathbf a|s)=\mathcal N(\mu_\theta(s),\sigma_\theta^2\mathbb I)$ with **state-independent** $\sigma$:
$$D_{\mathrm{KL}}(\pi_{\rm old}\|\pi_\theta)=\frac12\sum_{j=1}^{M}\left[\log\frac{\sigma^2_{{\rm old},j}}{\sigma^2_{\theta,j}}+\frac{\sigma^2_{\theta,j}}{\sigma^2_{{\rm old},j}}-1\right].$$
With $\sigma$ held fixed during the update this reduces to the closed form
$$D_{\mathrm{KL}}=\frac12\sum_{j=1}^{M}\frac{(\mu_{\theta,j}-\mu_{{\rm old},j})^2}{\sigma_j^2},$$
— **no sampling, no FVP**. This is a large part of why continuous-control TRPO/PPO is cheap, and it is the formula to use for UAV velocity commands with fixed exploration noise. If $\sigma$ is state-dependent and updated, the full log-difference form above is required.

---

## A.8 PPO

**Reference:** Schulman, Wolski, Dhariwal, Radford, Klimov, *Proximal Policy Optimization Algorithms*, arXiv:1707.06347, 2017.

### A.8.1 From TRPO to first order

**Step 1 (importance weighting).** $r_t(\theta)=\pi_\theta(\mathbf a_t|s_t)/\pi_{\theta_{\rm old}}(\mathbf a_t|s_t)$.

**Step 2 (conservative objective).** TRPO's penalty relaxation is $\max_\theta L_{\rm sur}(\theta)-\beta D_{\mathrm{KL}}(\pi_{\rm old}\|\pi_\theta)$. Using $x\le\max(x,1+\epsilon)$ ("cap the improvement") and $\min(x,1+\epsilon)$ ("pessimistic"), PPO defines
$$\boxed{\;L^{\mathrm{CLIP}}(\theta)=\mathbb E_t\Big[\min\big(r_t(\theta)\hat A_t,\ \mathrm{clip}(r_t(\theta),1-\epsilon,1+\epsilon)\hat A_t\big)\Big]\;}$$

**Step 3 (why clipping is conservative — the full case analysis).** Put $u=r_t(\theta)$.

*Case $\hat A_t>0$ (good action; we want to raise its probability).* $\min(u\hat A,\mathrm{clip}(u)\hat A)=\hat A\min(u,1+\epsilon)$. For $u\le1+\epsilon$ the objective equals $u\hat A$ (ordinary surrogate, gradient flows, and the ratio may move *down* to $1-\epsilon$ without clipping). For $u>1+\epsilon$ it is **constant** — gradient **zero**. So for a good action, once the ratio exceeds $1+\epsilon$, the update is **cut off**.

*Case $\hat A_t<0$ (bad action; we want to lower its probability).* The $\min$ picks the more negative, $\hat A\max(u,1-\epsilon)$. For $u\ge1-\epsilon$ the objective equals $u\hat A$; for $u<1-\epsilon$ it is constant — **zero gradient**.

> **Proposition A.26 (pessimistic lower bound).** $L^{\mathrm{CLIP}}(\theta)\le L_{\rm sur}(\theta)$ for every $\theta$.
> *Proof.* Four cases: ($\hat A>0$, $u>1+\epsilon$): CLIP $=\hat A(1+\epsilon)<\hat A u=$ SUR. ($\hat A<0$, $u<1-\epsilon$): $\hat A<0$ and $1-\epsilon>u$ so $\hat A(1-\epsilon)<\hat A u=$ SUR. The other two cases give CLIP $=$ SUR. $\blacksquare$

> **Corollary A.27 (conservative policy update).** Maximising $L^{\mathrm{CLIP}}$ cannot raise the probability of a very bad action ($\hat A<0$) beyond ratio $1-\epsilon$, nor that of a very good action ($\hat A\ge0$) beyond $1+\epsilon$. Therefore a large $L_{\rm sur}$ can never be achieved by exploiting the surrogate's optimism: $L^{\mathrm{CLIP}}$ is PPO's surrogate for TRPO's KL constraint.

**Honest caveat that belongs in a rigorous report.** Clipping does **not** actually bound the ratio, because a minibatch's ratios can be shifted; the realised mean ratio can exceed $1+\epsilon$ (measured by Schulman et al. 2017, Fig. 1). Andrychowicz et al., *What Matters In On-Policy Reinforcement Learning*, ICLR 2021, shows the *implementation details* (minibatch size, epochs, gradient clipping, advantage normalisation, value loss, initialisation, LR schedule) matter as much as the clipping itself. PPO's guarantee should therefore be stated as **empirical stabilisation**, not a proven KL bound.

### A.8.2 KL early-stopping heuristic

**Definition A.28.** Schulman et al. 2017 §2: after each minibatch update, estimate the KL and terminate the epoch when $\mathbb E_s[D_{\mathrm{KL}}(\pi_{\theta_{\rm old}}\|\pi_\theta)]\ge\text{KL}_{\text{target}}$ (typically $\approx0.01$–$0.05$).
**Rationale:** the number of gradient steps is what actually drives drift from $\pi_{\rm old}$; clipping caps the *per-sample* penalty but the *aggregate* KL still grows with epochs. Early stopping directly controls the constraint TRPO enforces by construction.

**Estimating the KL from samples (the $k_1,k_2,k_3$ family; Schulman et al., arXiv:1506.02438, §2).** With $r_i=\pi_\theta(a_i|s_i)/\pi_{\theta_{\rm old}}(a_i|s_i)$ and $D:=D_{\mathrm{KL}}(\pi_{\theta_{\rm old}}\|\pi_\theta)=\mathbb E_{a\sim\pi_{\rm old}}[\log\pi_{\rm old}(a)-\log\pi_\theta(a)]$, the identity
$$D=\mathbb E_{a\sim\pi_{\rm old}}\big[-\log r(a)\big]$$
gives the **unbiased but high-variance** estimator $\hat D_1=\frac1N\sum_i[-\log r_i]$. The three standard low-variance alternatives are
$$\hat D_2=\frac1N\sum_i\big[r_i-1-\log r_i\big]\quad(\text{non-negative, second-order accurate}),$$
$$\hat D_3=\frac1N\sum_i\Big[\frac{1}{2}(r_i-1)^2\Big]\quad(\text{non-negative, unbiased to second order, lower variance still}),$$
$$\hat D_4=\frac1N\sum_i\Big[(r_i-1)-\log r_i+\tfrac12(r_i-1)^2\Big]=\frac1N\sum_i\Big[\tfrac32 r_i-2-\log r_i\Big].$$

**Non-negativity, checked.** The three corrections are all pointwise $\ge0$:
- $r-1-\log r\ge0$ for $r>0$, with equality only at $r=1$: let $f(r)=r-1-\log r$; $f(1)=0$, $f'(r)=1-\frac1r$, so $f'<0$ on $(0,1)$ and $f'>0$ on $(1,\infty)$, and $\lim_{r\to0^+}f(r)=+\infty$. $\square$
- $\frac12(r-1)^2\ge0$. $\square$
- For $\hat D_4$: $f_4(r)=\frac32r-2-\log r$, $f_4(1)=\frac32-2=\!-\frac12\neq0$! So $\hat D_4$ as written is **not** a KL estimator at $r=1$ and is **not** non-negative — it is negative for $1/3\le r<1$. The correctly normalised fourth-order estimator is
$$\hat D_4=\frac1N\sum_i\Big[(r_i-1)-\log r_i+\tfrac12(r_i-1)^2\Big]\ \text{**with the } \tfrac12(r-1)^2 \text{ term halved once more**},\ \text{i.e. } \hat D_4=\tfrac12\big(\hat D_2+\hat D_3\big)=\frac1N\sum_i\Big[r_i-1-\log r_i+\tfrac14(r_i-1)^2\Big],$$
which satisfies $\hat D_4(1)=0$ and $f_4'(1)=1-1+0=0$, $f_4''(1)=1+1+1/2>0$, so $f_4\ge0$ locally and globally by the same argument.

**Taylor check of accuracy order.** With $r=e^{-\varepsilon}$ ($\varepsilon>0$ small, $r$ small ⇒ $\pi_\theta\ll\pi_{\rm old}$):
$$-\log r=\varepsilon,\quad r-1-\log r=e^{-\varepsilon}-1+\varepsilon=\tfrac12\varepsilon^2-\tfrac16\varepsilon^3+O(\varepsilon^4),\quad \tfrac12(r-1)^2=\tfrac12(1-e^{-\varepsilon})^2=\tfrac12\varepsilon^2-\tfrac12\varepsilon^3+O(\varepsilon^4).$$
So $\hat D_1$ has error $O(\varepsilon)$, while $\hat D_2,\hat D_3$ are second-order accurate; averaging them ($\hat D_4$) is fourth-order accurate. **This is the content of "second-order accurate, always non-negative"** — accuracy in $\varepsilon$, not in the ratio.

**⚠ Correction to the draft version.** The estimator written as $-r+\log r+\frac12(r-1)^2=\frac32r-2-\log r$ is **not** a KL estimator: at $r=1$ it equals $-\frac12$ (should be $0$), and it is negative for $\frac13\le r<1$, so the early-stopping test $\hat D\ge\mathrm{KL}_{\text{target}}$ can trigger spuriously. The correct form is the average of the two non-negative second-order estimators.

### A.8.3 Full PPO algorithm (MAPPO variant)

```text
for iteration k:
  for actor i in parallel: execute pi_theta_old for T steps; collect (obs, act, logp, rew, val, done)
    compute GAE: adv[t] = delta[t] + gamma*lam*(1-done[t+1])*adv[t+1]
    optionally value-normalise: ret[t] = adv[t] + value[t]
  for epoch e = 1..E:
    for minibatch B:
      for i = 1..N: ratio_i = exp(logp_i(theta) - logp_i(theta_old))
        L_pi = mean_B( min(ratio_i*A_i, clip(ratio_i,1-eps,1+eps)*A_i) )
      L_v   = mean_B( max( (V_phi-ret)^2, (clip(V_phi,ret-eps_v,ret+eps_v)-ret)^2 ) )   # value clipping
      maximise L_pi - c_v * L_v
    compute approx KL; if KL > target: break
```

The **value clipping** term regresses $V_\phi$ against a *range* rather than a point, removing the incentive to move $V$ far in the wrong direction — critical in MARL where a badly scaled centralised critic poisons every agent's advantage (Mnih et al. 2016; Poplar; adopted in MAPPO).

### A.8.4 The multi-agent subtlety: independent ratios

**The problem.** MAPPO uses per-agent ratios $r_t^{(i)}=\pi_{\theta^i}(a_t^i|o_t^i)/\pi_{\theta^i_{\rm old}}(a_t^i|o_t^i)$, not the joint ratio $\prod_ir_t^{(i)}$. Standard TRPO analysis (needing joint KL $\sum_iD_{\mathrm{KL}}(\pi^i_{\rm old}\|\pi^i)$ and the joint ratio) **does not apply**.

> **Theorem A.29 (Sun, Harb, White, Abbasi-Yadkori, Krause, AAMAS 2023, arXiv:2202.00082 — "Trust Region Bounds for Decentralized PPO Under Non-stationarity", Thms 4.3 & 5.3).** Assuming the advantage function has converged to a fixed point (their Assumption 5.2), a **monotonic improvement** guarantee holds for the independent-ratio objective, provided the **centralised** trust region is enforced: if every independent ratio satisfies
> $$\lambda^k_j=\frac{\tilde\pi^j(a_k|s_k)}{\pi^j(a_k|s_k)}\in[1-\epsilon_j,\,1+\epsilon_j]\quad\forall k,j,$$
> then $$D_{\mathrm{TV}}^{\max}\big(\pi^k(\cdot|s),\tilde\pi^k(\cdot|s)\big)<\sum_{j=1}^N\epsilon_j,$$
> and this centralised trust region is what delivers the improvement. **In practice $N$ independent clip ranges of size $\epsilon$ induce a joint allowance $N\epsilon$, so the clip range must be scaled $\epsilon\asymp1/N$.** They also prove the IPPO and MAPPO surrogate objectives **coincide** at critic fixed points (via Lyu et al. 2021, Lemmas 1–2), so the centralised-vs-decentralised critic choice is *not* what makes MAPPO work.

**Independent confirmation (different angle).** CoPPO (Xiao et al., *Coordinated Proximal Policy Optimization*, arXiv:2305.12080) derives
$$J(\tilde{\boldsymbol\pi})\;\ge\;\tilde L_\pi(\tilde{\boldsymbol\pi})-\frac{4}{1-\gamma}\sqrt{\sum_{i=1}^{N}(1-\alpha_i)},$$
with per-agent gap parameters $\alpha_i$. The cross terms in $\mathbb E[\prod_ir_i]$ produce a contribution of order $\prod_i(1-\alpha_i)$, so when any $\alpha_i$ is bounded away from 1 the penalty scales **exponentially in $N$**. This is the quantitative version of "naive independent learners blow up."

---

## A.9 MAPPO (Yu et al. 2022)

**Reference:** Chao Yu, Akash Velu, Eugene Vinitsky, Jiaxuan Gao, Yu Wang, Alexandre Bayen, Yi Wu, *The Surprising Effectiveness of PPO in Cooperative, Multi-Agent Games*, **NeurIPS 2022** (arXiv:2103.01955v4). Code: `github.com/zoeyuchao/mappo`.

> **Definition A.30 (MAPPO).** PPO in the CTDE paradigm with a **centralised value function**: the critic $V_\phi$ takes the global state; the actor $\pi_\theta$ takes only the local observation. Design choices: (i) parameter sharing, (ii) centralised critic, (iii) value normalisation, (iv) carefully chosen global-state representation.
> Verbatim: *"$V_\phi(s)$ is used for variance reduction and is only utilized during training; hence, it can take as input extra global information not present in the agent's local observation, allowing PPO in multi-agent domains to follow the CTDE structure. […] we refer to PPO with centralized value function inputs as MAPPO."*

### A.9.1 Decentralised vs centralised — the exact split

| Component | Input | At execution? | Role |
|---|---|---|---|
| **Actor** $\pi_\theta(a_i|o_i)$ | local $o_i$ (+ agent-ID one-hot) | **Yes** | must be decentralised |
| **Critic** $V_\phi$ | **global** state: AS (agent-specific $[o_i,o_{-i}]$), EP (episode/return + agent ID + local obs), or CL (full concatenation) | **No — discarded** | baseline / variance reduction only |
| Actor optimiser | $\nabla_\theta L^{\mathrm{CLIP}}$ with $\hat A_t$ from GAE over centralised $V_\phi$ | No | training |
| Critic optimiser | $\nabla_\phi L_v$ on $\hat R_t$ | No | training |

The GAE residual is $\delta_t=r_{t+1}+\gamma V_\phi(s_{t+1})-V_\phi(s_t)$ with $V_\phi$ on **global** states, and the **same** $\hat A_t$ is reused for all $N$ agents' ratios.

### A.9.2 Parameter sharing

**Definition A.31.** One shared actor and one shared critic:
$$L_\pi(\theta)=\frac1N\sum_{i=1}^N\frac1{nB}\sum_b\min\big(r_b^{(i)}\hat A_b,\ \mathrm{clip}(r_b^{(i)},1-\epsilon,1+\epsilon)\hat A_b\big),$$
with the single shared $\theta$ inside every $r_b^{(i)}$. Agent identity injected as $\mathbf e_i\in\mathbb R^N$.

**Why it helps (three reasons).**
1. **Statistical strength:** effective dataset is $nB\cdot N$ samples, not $nB$. For $N$ UAVs with few samples each this is the difference between learning and not learning.
2. **Deployment efficiency:** a *single* on-board model — a $k\times$ reduction in memory/compute, decisive for small UAV payloads (§A.11).
3. **Implicit coordination regularisation:** gradients from all agents accumulate in the *same* weight vector, so a direction that helps one agent is shared by all.

**Reported finding (verbatim, Appendix C.2):** *"MAPPO with parameter sharing outperforms MAPPO without parameter sharing by a clear margin"* (median evaluation win rate on selected SMAC maps, 6 random seeds, MAPPO-Ind vs MAPPO).

**⚠ Precise ranking of the ablation effects — do not call parameter sharing "the biggest win."** Yu et al. 2022 §5 and App. C.2 report parameter sharing as a clear win **relative to MAPPO-Ind**, and it is the paper's *default* configuration. But the paper's own **most emphatic recommendation is value normalisation** ("never hurts training and often improves the final performance significantly", critical in MPE `spread`), and the report's own claim that *parameter sharing* is the single largest effect is an over-reading: the ablations are made relative to MAPPO's default, and the paper does not rank parameter sharing above value normalisation. The defensible statements are:
- parameter sharing > no parameter sharing, by a clear margin, on the tested SMAC maps, 6 seeds (App. C.2);
- value normalisation is the single most robust stabiliser across *all* benchmarks (Suggestion 1, §5);
- critic-state design (EP < CL < AS ≈ FP) is the second-largest effect (Suggestion 2);
- these three are **interacting**; the paper does not report a factorial decomposition, so no additive attribution of the total gain is available.

**Theoretical caution (must be stated).** Kuba et al. 2022 (Prop. 1) prove parameter sharing can yield an **exponentially worse** suboptimal outcome in a worst-case constructed game, because the shared gradient can be dominated by agents whose local optima conflict. It is an **inductive bias**, valid under homogeneity — true for a homogeneous UAV swarm, **false** for a heterogeneous fleet.

### A.9.3 The five factors that matter — exact reported findings (Yu et al. 2022 §5)

**Suggestion 1 — Value normalisation (strongest recommendation).**
*Verbatim suggestion:* *"Utilize value normalization to stabilize value learning."*
- **Method:** the value network regresses to **normalised** targets using a **running mean and standard deviation of the value targets**; when computing the GAE, the running average **de-normalises** the network output so advantages are on the correct scale.
- **Why (verbatim):** *"Through the training process of MAPPO, value targets can drastically change due to differences in the realized returns, leading to instability in value learning."*
- **Evidence:** in MPE `spread` (episode returns ranging below $-200$ to $0$) value normalisation is **critical**; it also positively affects several SMAC maps, either improving final performance or reducing training variance. Stated: value normalisation *"never hurts training and often improves the final performance significantly."*
- **Direct transfer to UAV work:** persistent coverage has wildly different reward scales across mission phases (well-charged vs low-SoC), so target standardisation is essential.

**Suggestion 2 — Critic input composition.**
*Verbatim:* *"When available, include both local, agent-specific features and global features in the value function input. Also check that these features do not unnecessarily increase the input dimension."*
- Ordering: **EP** (episode-return + agent ID + local obs) $<$ **CL** (all local observations concatenated) $<$ **AS** (agent-specific $[o_i,o_{-i}]$) $\approx$ **FP** (featured-pruned AS).
- Key result: **CL is ineffective, particularly in maps with many agents** — it inflates dimensionality without adding information. AS and FP are both strong; FP beats AS on some maps and wins where AS is subpar.
- Verbatim: *"the state dimensionality, agent-specific features, and global information are all important in forming an effective global state."*

**Suggestion 3 — Training data usage (epochs / minibatch / rollout).** Very sensitive. Reported: episode length 200 (SMAC), 25 PPO epochs, 5 minibatches, buffer 400 (MPE) / 5000 (SMAC) episodes, batch 32 (MPE) / 1 (SMAC), $\gamma=0.99$, $\epsilon=0.2$ (value & policy), lr $5\times10^{-4}$, value-loss coefficient $c_v=1$. The *number of gradient steps* per rollout controls trust-region drift, consistent with A.8.2.

**Suggestion 4 — Clipping strength.** Small $\epsilon$ (0.05) slows learning on hard maps (MMM2, 3s5z vs 3s6z) but gives **consistently high final performance and smaller standard deviation** in training curves — lower $\epsilon$ trades speed for stability. Large $\epsilon$ (0.2, 0.3, 0.5) still works well empirically; $\epsilon=0.2$ is the reported default. **Consistency note with theory:** Sun et al. 2023 (A.8.4) would predict $\epsilon\asymp1/N$ for *guaranteed* improvement; Yu et al. separately report that good $\epsilon$ values are *"highly sensitive to the number of agents."* The two are consistent once one reads Yu et al.'s large-$\epsilon$ results as indicating the **guarantee** is lost while **performance** is retained.

**Suggestion 5 — Value/policy clipping.** Using the same $\epsilon$ for both; keeping both is better than removing either.

**Other quotable findings.**
- **PPO is surprisingly strong in MARL:** PPO-based methods match or beat off-policy competitors (MADDPG, QMIX family) on SMAC, GRF, Hanabi, MPE, *"with minimal hyperparameter tuning and without any domain-specific algorithmic modifications or architectures"* (abstract).
- **Value clipping** stabilises the centralised critic.
- **Recurrent policy needed for partial observability** (MPE `comm`) — the one benchmark where they use agent-specific (non-shared) parameters.

### A.9.4 Sequential update order (HATRPO/HAPPO — *not* MAPPO)

This is a common confusion in reports: **MAPPO does not use a sequential update.** That is the design of the HATRPO/HAPPO family. Precise statement:

> **Theorem A.32 (Kuba, Chen, Wen, Wen, Sun, Wang, Yang, ICLR 2022, arXiv:2109.11251, Lemma 1 — Multi-Agent Advantage Decomposition).** In **any** cooperative Markov game, for any state $s$, any joint policy $\boldsymbol\pi$, and any permutation $i_1,\dots,i_N$,
> $$A_{\boldsymbol\pi}^{i_{1:N}}\big(s,\mathbf a^{i_{1:N}}\big)=\sum_{j=1}^{N}A_{\boldsymbol\pi}^{i_j}\big(s,\mathbf a^{i_{1:j-1}},a^{i_j}\big),$$
> i.e. the joint advantage decomposes **exactly** into a sum of per-agent advantages, each conditioning only on the actions of agents earlier in the order. **No decomposability assumption on $V$ or $Q$ is required** (unlike VDN, QMIX, Q-DPP).
> *Proof idea.* Induct on $N$; use $Q_{\boldsymbol\pi}(s,\mathbf a)=\mathbb E_{s'}[r+\gamma Q_{\boldsymbol\pi}(s',\mathbf a')]$ and $V_{\boldsymbol\pi}(s)=\mathbb E_{s'}[\mathbb E_{\mathbf a'\sim\boldsymbol\pi}[r+\gamma V(s')]]$; the inner term recurses. $\square$

> **Theorem A.33 (monotonic improvement, Kuba et al. 2022 Thm 2).** With $L_{\boldsymbol\pi}^{i_{1:m}}\big(\tilde\pi^{i_{1:m-1}},\tilde\pi^{i_m}\big)=\mathbb E\big[\tfrac{\tilde\pi^{i_m}}{\pi^{i_m}}A_{\boldsymbol\pi}^{i_m}\big]$, the sequential scheme
> $$\tilde\pi^{i_m}_{k+1}=\arg\max_{\pi^{i_m}}\Big\{L_{\boldsymbol\pi_k}^{i_{1:m}}\big(\tilde\pi^{i_{1:m-1}}_{k+1},\pi^{i_m}\big)-C\,D^{\max}_{\mathrm{KL}}\big(\pi^{i_m}_k,\pi^{i_m}\big)\Big\}$$
> satisfies $J(\boldsymbol\pi_{k+1})\ge J(\boldsymbol\pi_k)$ for all $k$. Each agent can always make its summand $\ge0$ by not updating ($\tilde\pi^{i_m}=\pi^{i_m}$), so positive updates accumulate.
> Also: the update order can be **randomised** each iteration without hurting convergence (and often helping it).

**Empirical findings of Kuba et al. 2022:** HATRPO/HAPPO *significantly outperform* IPPO, MAPPO and MADDPG on Multi-Agent MuJoCo and SMAC. They need **no parameter sharing** and **no decomposability** of the joint $Q$, and they show MAPPO/IPPO's reliance on parameter sharing can be **exponentially worse** in the worst case.

**MAPPO vs HATRPO/HAPPO.**

| | MAPPO | HATRPO / HAPPO |
|---|---|---|
| Ratios | **independent** $r^{(i)}$ | **sequential**, conditioned on prior agents' new policies |
| Critic | one centralised $V_\phi$ on global state | one **joint** advantage estimator for all agents (saves $N$ critics) |
| Parameter sharing | required in practice | **not** required (heterogeneous supported) |
| Monotonic improvement | only with independent-ratio theory (Sun et al. 2023) + small $\epsilon$ | **guaranteed** (Kuba et al. 2022) |
| Extra training info | global state | sequential action prefix $\mathbf a^{i_{1:m-1}}$ |
| Empirically (Kuba 2022) | strong on SMAC | stronger on MuJoCo, strong on SMAC |

**Recommendation for the report:** homogeneous UAVs + robustness goal ⇒ MAPPO, whose ablated design rules (A.9.3) are directly actionable. Heterogeneous fleet ⇒ HAPPO, which needs no parameter sharing, has a monotonic-improvement guarantee, and uses a single critic.

### A.9.5 Other 2023–2026 results

- **Li & He (2025)**, *Bridging Theory and Practice of MAPPO for Cooperative Multi-Agent Continuous Control* — theoretical analysis of MAPPO in continuous control; TRPO-augmented variant **removes the parameter-sharing requirement, supports heterogeneous agents, and uses a squashed Gaussian** for bounded actions. Directly applicable to UAV continuous action spaces with hard speed/acceleration envelopes.
- **Li & He (2023)**, *Multi-Agent Trust Region Policy Optimization*, IEEE TNNLS 35(9):12873–12887.
- **PRD-MAPPO (2024)**, *Assigning Credit with Partial Reward Decoupling in MAPPO* — soft attention restricting agent $i$'s advantage to a relevant set $\mathcal R_i(s_t)$:
$$\delta_{i,t}=\sum_{j\in\mathcal R_i(s_t)}r^{(j)}_t+\gamma V^i_\psi(s_{t+1},\mathbf a^i_{-t+1})-V^i_\psi(s_t,\mathbf a^i_{-t}).$$
Reports that PRD-MAPPO **avoids the gradient-variance spikes present in MAPPO** and reduces advantage computation from $O(M^2)$ to $O(M)$ critic calls. **Directly useful for UAV coverage:** the natural relevant set is the $k$ nearest neighbours in the coverage graph.
- **Constrained/safe MARL PPO (NeurIPS 2024)** — Lagrangian-constrained MARL PPO, for hard geo-fence/minimum-altitude constraints.

---

## A.10 Variance of the multi-agent gradient estimator; non-stationarity; recent theory

### A.10.1 Why naive independent learners diverge

**Definition A.34 (independent learner).** Agent $i$ at iteration $k$ updates with $\hat g_i^{(k)}=\frac1B\sum_{b}\nabla_{\theta^i}\log\pi_{\theta^i}(a_b^i|o_b^i)\hat A_b^i$, where $\hat A_b^i$ is estimated by a critic trained **only on agent $i$'s own data**, with no access to other agents' state/actions.

**(1) Non-stationary target (fundamental).** $Q^{\boldsymbol\pi_k}_i$ changes as others update. The iteration $\theta^i_{k+1}=\theta^i_k+\alpha_kg^i(\theta^i_k;\boldsymbol\pi_k)$ is stochastic approximation toward a *moving* sequence of fixed points $\arg\max_\theta J(\theta^i;\boldsymbol\pi_k)$ that are themselves moving. There is no contraction. Classical two-timescale actor–critic theory (Borkar 1997) requires the critic to converge to $Q^{\boldsymbol\pi_k}$ — but $\boldsymbol\pi_k$ changes every step, so the tracking error never vanishes.

**(2) Multiplicative variance growth.** From CoPPO (A.8.4): the joint improvement bound's error term scales as $\sqrt{\sum_{i=1}^N(1-\alpha_i)}$, arising from cross terms of order $\prod_i(1-\alpha_i)$ in $\mathbb E[\prod_ir_i]$. **Exponential in $N$** when any $\alpha_i<1$ is bounded away from 1.

**(3) The deadly triad (Sutton & Barto 2018 §3).** The conjunction of:
- **function approximation** (neural value function, limited capacity);
- **bootstrapping** (GAE/TD targets depend on the current estimate);
- **off-policy / non-stationary data** (targets generated by a joint policy that is being updated — in MARL the data distribution is non-stationary *by construction* because all agents update simultaneously).

Divergence mechanism: the Bellman operator is a $\gamma$-contraction in $\ell_\infty$ **for the true operator**; function approximation destroys this (empirically, spectral radius of the approximate operator $>1$ implies divergence), and off-policy/non-stationary data removes the sampling assumptions that make the update a descent method.

**Minimal demonstration:** Example A.9 — the $2\times2$ game oscillates forever with independent greedy updates; a centralised $V$ has a unique optimum at $(1,1)$ where $J=1$. **CTDE's only contribution is a correct, low-variance, low-bias signal about the joint effect of actions; it does not change the policy class.**

### A.10.2 The MAPPO variance argument — stated correctly

MAPPO computes **one** team advantage $\hat A_t$ per time step and reuses it for all $N$ agents. Decompose $\hat A_b=A_b^{\rm true}+\varepsilon_b$ with $\varepsilon_b$ the critic's estimation error, and write the shared-signal gradient estimator
$$\hat g=\frac{1}{BN}\sum_{b=1}^{B}\sum_{i=1}^{N}\nabla_{\theta^i}\log\pi_{\theta^i}(a_b^i|o_b^i)\big(A_b^{\rm true}+\varepsilon_b\big)=\hat g_{\rm signal}+\hat g_{\rm noise}.$$

**The correct comparison is against the IPPO-style estimator with per-agent advantages** $\hat A^i_b=A^i_b+\varepsilon^i_b$:
$$\hat g^{\rm IPPO}_{\rm noise}=\frac{1}{BN}\sum_{b}\sum_i\nabla_{\theta^i}\log\pi_i(a_b^i|o_b^i)\varepsilon^i_b .$$

**Case 1 — the critic errors are independent across agents** ($\mathbb E[\varepsilon_b^i\varepsilon_b^j]=0$ for $i\ne j$) and have equal variance $\sigma_\varepsilon^2$. The two noise terms are then both sums of $BN$ zero-mean terms with comparable per-term scale, so
$$\|\hat g_{\rm noise}\|^2_{\rm shared}\;\asymp\;\|\hat g^{\rm IPPO}_{\rm noise}\|^2\;\asymp\;\frac{NB\,\sigma_\varepsilon^2\,\mathbb E\|\nabla\log\pi\|^2}{(BN)^2},$$
i.e. the **relative** noise level is the same, and the only difference is the quality of the advantage itself: one critic with the *global* state has a **lower bias and lower variance** for the team advantage than $N$ independent local critics, because $A^{\boldsymbol\pi}(s,\mathbf a)=Q^{\boldsymbol\pi}-V^{\boldsymbol\pi}$ is a functional of the **joint** state-action pair, and $N$ local critics each see only $o_i$ and must average away the effect of the other $N-1$ agents' actions. The honest statement is therefore:

> MAPPO's shared advantage is a **bias/variance improvement in the advantage estimate**, obtained by conditioning $V$ on the full joint state. The *averaging over agents* contributes a factor $1/\sqrt N$ (the usual independent-average rate) **only if** the per-agent score terms were being averaged with independent noise — which they are not, because they all carry the *same* $\varepsilon_b$.

**Case 2 — the honest "shared signal" effect, and its correct order.** Because the same $\varepsilon_b$ is multiplied by $N$ score terms, the noise is coherent across $i$:
$$\hat g_{\rm noise}=\frac{1}{BN}\sum_{b}\varepsilon_b\,\underbrace{\Big(\sum_{i=1}^N \nabla_{\theta^i}\log\pi_i(a_b^i|o_b^i)\Big)}_{\textstyle =:\,G_b,\ \text{the joint score}},\qquad \mathbb E\,\|\hat g_{\rm noise}\|^2=\frac{\sigma_\varepsilon^2}{BN^2}\mathbb E\|G_b\|^2=\frac{\sigma_\varepsilon^2}{N\,B}\,\mathbb E\|G_b\|^2 .$$
Compare with IPPO: there the corresponding quantity is $\frac{1}{BN^2}\sum_{b,i}\mathbb E[\varepsilon^{i\,2}\|\nabla_i\|^2]$. So if $\mathbb E\|G_b\|^2\asymp N\,\mathbb E\|\nabla_i\|^2$ (scores roughly orthogonal across agents) the two coincide in order, while if the agents' scores are **correlated** (the genuinely cooperative regime, where they move together) $\mathbb E\|G_b\|^2$ grows like $N^2$ and the shared-signal estimator is *worse*, not better.

**⚠ The "$\mathbf{1/N}$ instead of $\mathbf{1/\sqrt N}$" claim is false.** Two errors: (i) averaging $N$ independent zero-mean terms reduces the standard deviation by $1/\sqrt N$, never $1/N$ — $1/N$ is the reduction in *variance*, not in the noise level; (ii) MAPPO's noise terms are *not* independent (the same $\varepsilon_b$ appears in all $N$ of them), so the standard $1/N$ variance-of-the-average argument does not apply at all. What MAPPO actually gains is a better *target* (global-state critic), not a magic $1/N$ averaging factor.

**The defensible, citable justification for a shared team advantage** is therefore:
1. **Bias reduction** (the real one): $V(s^1,\dots,s^N)$ conditions on the full joint state, so $A^{\boldsymbol\pi}$ is estimated without the partialling-out error that $N$ local critics incur. Formally, $\mathbb E[V^{\rm global}]\le\mathbb E[V^{\rm local}]$-style comparisons require a nested-information assumption, but the qualitative statement — the $A$ that is correct for the credit assignment is a joint functional, so estimate it jointly — is standard.
2. **Non-stationarity absorption** (A.10.1(1)): a single global critic is updated on the same batch, so all $N$ agents consume a *simultaneously refreshed* target rather than $N$ independently drifting ones.
3. **Practical**: $1$ critic forward pass per environment step instead of $N$, which is why MAPPO is affordable (see A.11.2).

### A.10.3 Recent theoretical results (2023–2026)

| Paper | Result | Relevance |
|---|---|---|
| **Kuba, Chen, Wen, Wen, Sun, Wang, Yang** (ICLR 2022), arXiv:2109.11251 | Multi-agent advantage decomposition (exact, no decomposability assumption) + sequential trust region ⇒ **monotonic improvement**; randomised agent order is fine | First rigorous multi-agent trust-region theory. HATRPO/HAPPO |
| **Sun, Harb, White, Abbasi-Yadkori, Krause** (AAMAS 2023), arXiv:2202.00082 | **Monotonic improvement for IPPO/MAPPO with independent ratios** if each ratio in $[1-\epsilon_j,1+\epsilon_j]$ and advantages converged. Joint TV trust region $=\sum_j\epsilon_j$. IPPO ≡ MAPPO objectives at critic fixed points | Direct justification for MAPPO's design and for the empirical finding that $\epsilon$ must scale with $N$ |
| **Xiao et al.** (2023), CoPPO, arXiv:2305.12080 | Approximate monotonic improvement for a theoretically-grounded joint objective; variance penalty $\sqrt{\sum_i(1-\alpha_i)}$ — multiplicative in $N$; interprets objective as **dynamic credit assignment** | Quantitative explanation of independent-learner blow-up |
| **Zhao, Yang, Wang, Lee** (ICML 2023), PMLR v202, *Local Optimization Achieves Global Optimality in MARL* | **First provably convergent multi-agent PPO** in cooperative Markov games with function approximation. Multi-agent PDL + **localized action value** as ideal descent direction; **sequential** per-agent updates. Rate $\frac{N}{1-\gamma}\log\frac{|\mathcal A|K}{1-\gamma}$ up to statistical errors from critic evaluation with $n$ samples, $K$ = iterations. Sample complexity **polynomial in $N$** — "breaking the curse of scalability". Requires only **single-policy concentrability** (weaker than prior bounds) | The strongest convergence guarantee for PPO-style multi-agent algorithms. The concrete error bound to cite |
| **Li & He** (2025) | Theoretical analysis of MAPPO in continuous control; TRPO-augmented variant removes parameter sharing, supports heterogeneity, **squashed Gaussian** for bounded actions | Directly applicable to UAV continuous control with hard speed limits |
| **PRD-MAPPO** (2024) | Attention-based relevant-set restriction; removes gradient-variance spikes; $O(M)$ critic calls | Actionable for UAV coverage with spatial neighbourhoods |
| **Constrained MARL PPO** (NeurIPS 2024) | Lagrangian-constrained MARL PPO | Hard coverage / geo-fence constraints |

**Honest closing statement for the report.** As of September 2026 there is **no** end-to-end convergence proof for *MAPPO as actually implemented* (parameter sharing + advantage normalisation + GAE + value clipping + multiple epochs + independent ratios, all interacting). What exists is: (i) **monotonic improvement** under an idealised trust-region assumption (Kuba et al.; Sun et al. with $\epsilon\asymp1/N$ and a converged advantage); (ii) **global convergence to the optimal decentralised policy at rate $\frac{N}{1-\gamma}\log\frac{|\mathcal A|K}{1-\gamma}$** for a *specific* multi-agent PPO with sequential updates and no parameter sharing (Zhao et al. 2023); (iii) everything else is empirical.

---

## A.11 Complexity: shared actor, centralised critic

Setup: $N$ agents; per-agent $o_i\in\mathbb R^M$; $a_i\in\mathbb R^{d_a}$; actor MLP $L_a$ layers width $H$ (input $M$ or $M+N$ with agent-ID one-hot); critic MLP $L_c$ layers width $H_c$, input $d_{\rm crit}$.

**FLOP convention.** A fully-connected layer (in $d_{\rm in}$, out $H$) costs $\approx2d_{\rm in}H$ MACs forward, the same backward; a forward+backward pass $\approx6d_{\rm in}H$ FLOPs.

### A.11.1 Actor: $O(1)$ per agent, $O(N)$ total — proof

**Claim.** With parameter sharing, per-agent actor inference cost is
$$C_{\rm actor}^{\rm agent}=\Theta\!\big(L_a\,(d_{\rm in}+L_aH)\big)=\Theta\big(L_aH(d_{\rm in}+H)\big),$$
**independent of $N$**; total over the team is $\Theta(N)$.

*Proof.* A parameter-shared actor performs **one** forward pass of the *same* network on the agent's own input. Weights are shared, so the parameter count $\Theta(L_a d_{\rm in}H+L_aH^2L_a+Hd_a)$ is independent of $N$ (except the $N$-dim agent-ID one-hot, contributing $\Theta(NH)$ parameters and $\Theta(NH)$ FLOPs to layer 1). Forward FLOPs:
$$\text{FLOPs}_{\rm fwd}=2Hd_{\rm in}+2(L_a-1)H^2+2Hd_a=\Theta\big(L_aH(d_{\rm in}+H)\big),$$
with no $N$ term other than the agent-ID input. $\square$

**The "3 orders of magnitude" argument.** Per-agent networks: total parameters $\Theta(NL_aH^2)$, storage $\Theta(NL_aH^2)$. Shared: parameters and storage $\Theta(L_aH^2)$, total FLOPs still $\Theta(NL_aH^2)$. For $N=100$, $L_a=3$, $H=256$: **$100\times$ storage reduction** — a shared actor fits an embedded autopilot budget where per-agent networks do not.

**Communication-free scaling.** The actor runs on-board with local $o_i$ only, so per-step execution communication is $\Theta(1)$. For very large $N$ replace the one-hot with a random/hash embedding $\mathbf e_i\in\mathbb R^{d_e}$, $d_e\ll N$, restoring $O(1)$ input dim.

### A.11.2 Critic: the $O(N+M)$ claim, stated exactly

**⚠ The unqualified phrase "centralised critic has $O(N+M)$ input" is false for MAPPO's actual state.** The three critic-state designs in the MAPPO paper are (Yu et al. 2022, §5 and App. C):

| Critic state | Concatenation | Input dim | Asymptotics |
|---|---|---|---|
| **AS** (*agent state*) | $[o_i^{\,1\dots k},o^i^{\,1\dots N-1}]$ — agent $i$'s own recent observations + **all other agents' current observations** | $kM+(N-1)M=\Theta(NM)$ | $\Theta(NM)$ |
| **EP** (*episode return*) | $[\mathbf R^i_t,\ i_t,\ o^i_t]$ — past episode returns, one-hot agent ID, own observation | $R_{\rm hist}+N+M$ | $\Theta(N+M)$ |
| **FP** (*future plan*) | $[\mathbf R^i_t,\ i_t,\ o^i_t,\ o^i_{t+1}] + $ future plan | $R_{\rm hist}+N+2M$ | $\Theta(N+M)$ |
| Local-only | $o^i_t$ | $M$ | $\Theta(M)$ |

**So $O(N+M)$ is the EP/FP row, not the AS/CL row.** MAPPO's recommended and most-used configuration is **AS with a discrete mask** (per-agent index selecting which others are within comms range) or **AS + discretised input**, which is where the $\Theta(NM)$ comes from.

**Per-call cost.** One forward pass of an $L_c$-layer, width-$H_c$ MLP on a $d$-dimensional input costs $\Theta(L_cH_c(d+H_c))=\Theta(L_cH_c\,d)$ for $d\gg H_c$. Hence $C_{\rm crit}=\Theta(L_cH_cNM)$ for AS, and $\Theta(L_cH_c(N+M))$ for EP/FP.

**Per iteration.** MAPPO performs **one** critic forward per collected timestep (the *same* global/agent state is reused for all $N$ agents, because all agents share one advantage). With $T$ steps and $K$ epochs of minibatch updates, the count is $T$ forward passes and $TK$ (mini)batches:
$$\boxed{\;\text{Critic} = \Theta\big(T\,L_cH_c\,NM\big)\quad(\text{AS}),\qquad \Theta\big(T\,L_cH_c(N+M)\big)\quad(\text{EP/FP})\;}$$
$$\boxed{\;\text{Actor} = \Theta\big(T\,N\,L_aH(M+N)\big)\;}$$
**⚠ The "$O(N^2M)$ total" figure in the earlier draft was wrong in its counting.** It assumed $N$ *distinct* critic inputs (one per agent) per timestep. MAPPO does **not** do that: it computes **one** $V$ from the (concatenated or agent-indexed) state and broadcasts it. The $N^2M$ figure corresponds to running $N$ *separate* $N$-input critics, which is the IPPO/"$N$ individual centralised critics" variant, not MAPPO. Both numbers should be reported, with the design they belong to named.

**Ratio (corrected).** $\frac{\text{Critic}}{\text{Actor}}=\Theta\!\left(\frac{L_cH_cNM}{N\,L_aH(M+N)}\right)=\Theta\!\left(\frac{L_cH_cM}{L_aH(M+N)}\right)$, which is **$O(1)$ in $N$** for the AS design. With $L_c=L_a=3$, $H_c=H=256$, $M=32$, $N\gg1$: $\approx\frac{32}{32+N}\approx0.28$ at $N=100$ — the critic is *not* asymptotically dominant. The genuine constraint is **input dimensionality and memory**, not FLOPs: a $32\times100=3200$-dim MLP input with $H_c=256$ allocates $3200\times256\approx8.2\times10^5$ weights in the first layer alone, and the network must be retrained whenever $N$ changes. This motivates Yu et al.'s **feature pruning / discretisation** of the AS state, and is the honest reason to state the complexity as a *memory and re-trainability* issue rather than a compute-dominance issue.

**Scaling limit and the natural fix for coverage.** With $d_{\rm crit}=\Theta(NM)$ the AS critic cannot be reused across swarm sizes. The domain-standard fix is a **permutation-invariant / factored critic**: a DeepSets or attention encoder $\rho\!\left(\sum_i\phi(o_i)\right)$ with $\phi:\mathbb R^M\to\mathbb R^{d_e}$ makes $d_{\rm crit}=\Theta(d_e)=\Theta(1)$ **for all $N$** and is exactly what makes the critic permutation-equivariant. For persistent coverage the natural factored critic is per-Voronoi-cell, $V(s)=\sum_{c}\psi_c(s|_{V_c})$ with $\psi_c$ acting on the agents in cell $c$, so cost is $\Theta(L_cH_cM)$ per step and the structure mirrors the cell decomposition of B.4.

**Scaling limit.** $d_{\rm crit}=\Theta(NM)$ is feasible up to $N\sim10^2$; beyond that use **mean-field / per-region / factored critics**. For coverage, a per-Voronoi-cell value function $V_{\phi_{\text{cell}}}(\text{cell}_i)$ is natural (each UAV's value depends mainly on its own cell and immediate neighbours), reducing $d_{\rm crit}$ to $\Theta(M)$.

### A.11.3 Summary table

Let $T$ = environment steps per iteration, $K$ = epochs, $B$ = batch size ($TK\ge T$ minibatch updates). $C_{\rm actor}=\Theta(L_aH(M+N))$ is the cost of **one** shared forward pass.

| Operation | Input dim | Cost of one call | Per iteration ($T$ steps) | Grows in $N$? |
|---|---|---|---|---|
| Actor inference (on-board, shared) | $M+N$ (one-hot) or $M+d_e$ | $\Theta(L_aH(M+N))$ | $\Theta(TN L_aH(M+N))$ at execution; $\Theta(TK L_aH(M+N))$ in training (batched) | **no** (if $d_e$ fixed) / yes via one-hot |
| Critic, **AS** state (MAPPO default) | $NM$ | $\Theta(L_cH_cNM)$ | $\Theta(TL_cH_cNM)$ | **yes**, $\Theta(NM)$ |
| Critic, **EP**/FP state | $N+M$ | $\Theta(L_cH_c(N+M))$ | $\Theta(TL_cH_c(N+M))$ | linearly in $N$ |
| Critic, $N$ separate AS critics (IPPO-style) | $NM$ each | $\Theta(L_cH_cNM)$ | $\Theta(TL_cH_cN^2M)$ | **yes**, $\Theta(N^2M)$ |
| Critic, factored/DeepSets/per-cell | $d_e$ or $M_{\rm cell}$ | $\Theta(L_cH_c M)$ | $\Theta(TL_cH_cM)$ | **no** |

**The three sentences to put in the report, each matching one row:**
1. **Actor is $O(1)$ per agent in $N$** provided agent identity enters as a fixed-size embedding ($d_e$) rather than an $N$-dimensional one-hot; with a one-hot it is $O(N)$ per agent and $O(N^2)$ total. State the assumption; do not claim $O(1)$ without it.
2. **A single centralised critic with the AS state is $O(NM)$ per step, i.e. $O(1)$ in $N$ relative to the $N$-critic variant's $O(N^2M)$** — this is the honest complexity win of CTDE: *one* global evaluation instead of $N$ per-agent ones. Its real cost is the $NM$-dimensional input, which is a memory/generalisability problem, not a FLOP problem.
3. **The $O(N+M)$ bound is the EP/FP critic state**, and it is the configuration that stays dimension-light; it is not what AS does.

**Communication feasibility check.** Decentralised execution: $\Theta(1)$ per step. Centralised training requires shipping all $N$ observations each control period: $\Theta(NM)$ values/frequency. At $N=100$, $M=32$, 4-byte floats, 1 Hz: $100\times32\times4\times1=12.8$ kB/s — trivially feasible over cellular/mesh backhaul. A useful sanity number for the report. **Caveat:** CTDE's centralisation here is a *training-time* abstraction; a real system needs this $\Theta(NM)$/step fabric to exist, which is exactly assumption A1 in the table of A.3 and the reason many deployments substitute a range-limited or hierarchical critic.

---

## A.12 Reward shaping: potential-based theorem (Ng, Harada, Russell 1999)

**Reference:** Andrew Y. Ng, Daishi Harada, Stuart Russell, *Policy invariance under reward transformations: Theory and application to reward shaping*, **ICML 1999**, pp. 278–287.

### A.12.1 The exact statement

Let $\mathcal M=\langle\mathcal S,\mathcal A,T,\gamma,R\rangle$ and $\mathcal M_0=\langle\mathcal S,\mathcal A,T,\gamma,R_0\rangle$ with $R_0=R+F$.

**Definition A.35 (potential-based shaping function).** $F:\mathcal S\times\mathcal A\times\mathcal S\to\mathbb R$ is **potential-based** if there exists $\Phi:\mathcal S\to\mathbb R$ such that for all $s\ne s'$, $a$, $s'$:
$$\boxed{\;F(s,a,s')=\gamma\,\Phi(s')-\Phi(s)\;}$$

> **Theorem A.36 (Ng–Harada–Russell 1999, Theorem 1 — exact statement).** Let any shaping reward function $F:\mathcal S\times\mathcal A\times\mathcal S\to\mathbb R$ be given. We say $F$ is a potential-based shaping function if there exists $\Phi:\mathcal S\to\mathbb R$ such that for all $s\ne s'$, $a$, $s'$: $F(s,a,s')=\gamma\Phi(s')-\Phi(s)$. Then:
> **(Sufficiency)** If $F$ is potential-based, then **every optimal policy in $\mathcal M_0=\langle\mathcal S,\mathcal A,T,\gamma,R_0\rangle$ will also be an optimal policy in $\mathcal M$** (and vice versa).
> **(Necessity)** If $F$ is **not** potential-based (i.e. no such $\Phi$ exists satisfying the equation), then there exist (proper) transition functions $T$ and a reward function $R:\mathcal S\times\mathcal A\to\mathbb R$ such that **no optimal policy in $\mathcal M_0$ is optimal in $\mathcal M$**.
> Verbatim scope note: *"this is the strongest possible theorem of this form"*; with no prior knowledge of $T$ and $R$, potential-based $F$ is **necessary and sufficient** for consistency.

> **Corollary A.37 (Ng et al., Corollary 2).** If $F(s,a,s')=\gamma\Phi(s')-\Phi(s)$ (and, if $\gamma=1$, that $\Phi(s')=0$), then for all $s,a$:
> $$Q^*_{M_0}(s,a)=Q^*_M(s,a)-\Phi(s),\qquad V^*_{M_0}(s)=V^*_M(s)-\Phi(s).$$

> **Remark A.38 (Ng et al., Remark 1).** These identities hold for **any** policy $\pi$, not only the optimal one: $Q^\pi_{M_0}(s,a)=Q^\pi_M(s,a)-\Phi(s)$, $V^{\pi}_{M_0}(s)=V^\pi_M(s)-\Phi(s)$. Hence potential-based shaping **preserves near-optimal policies**. (Some presentations additionally require $\|\Phi\|_\infty<\infty$, guaranteeing $V$ is well defined for infinite discounted problems.)

### A.12.2 Proof of sufficiency — step by step

**Step 0 — normalisation.** Replacing $\Phi(s)$ by $\Phi(s)-\Phi(s_0)$ for a constant $c$ changes $F$ by $\gamma c-c=-c(1-\gamma)$, a **constant** added to every reward, which does not change the optimal policy. Hence for $\gamma=1$ we may assume $\Phi(s_0)=0$ (Ng et al. fix this normalisation). (In the discounted case $\gamma<1$ this is unnecessary.)

**Step 1 — candidate.** Show $\tilde Q(s,a):=Q^*_{M_0}(s,a)-\Phi(s)$ is the optimal $Q$ of $\mathcal M$.

**Step 2 — verify the Bellman optimality equation of $\mathcal M$.**
$$\begin{aligned}
\mathbb E_{s'}\big[R_0(s,a,s')+\gamma\tilde Q(s',a')\big]
&=\mathbb E_{s'}\big[R(s,a,s')+F(s,a,s')+\gamma Q^{*}_{M_0}(s',a')-\gamma\Phi(s')\big]\\
&=\mathbb E_{s'}\big[R(s,a,s')+\underbrace{\gamma\Phi(s')-\Phi(s)}_{F(s,a,s')}+\gamma Q^{*}_{M_0}(s',a')-\gamma\Phi(s')\big]\\
&=\mathbb E_{s'}\big[R(s,a,s')-\Phi(s)+\gamma Q^{*}_{M_0}(s',a')\big]\\
&=\mathbb E_{s'}\big[R(s,a,s')-\Phi(s)+\gamma\big(Q^*_M(s',a')-\Phi(s')\big)\big]\\
&=\mathbb E_{s'}\big[R(s,a,s')+\gamma\max_{a'}\tilde Q(s',a')\big],
\end{aligned}$$
using the inductive hypothesis $Q^*_{M_0}=\tilde Q+\Phi$. This is precisely the Bellman optimality equation of $\mathcal M$ for $\tilde Q$. (The undiscounted case needs $s=s'$ treated separately — as Ng et al. note.)

**Step 3 — conclude by contraction.** $T^*$ is a $\gamma$-contraction on bounded functions, so it has a unique fixed point. $\tilde Q$ is a fixed point, hence $\tilde Q=Q^*_M$, i.e. $Q^*_{M_0}(s,a)=Q^*_M(s,a)-\Phi(s)$.

**Step 4 — policy invariance.** $\pi$ is optimal in $\mathcal M_0$ iff it maximises $Q^*_{M_0}$:
$$\pi\in\arg\max_\pi\mathbb E\big[Q^*_{M_0}(s_0,\pi(s_0))\big]\iff\pi\in\arg\max_\pi\mathbb E\big[Q^*_M(s_0,\pi(s_0))-\Phi(s_0)\big]\iff\pi\in\arg\max_\pi\mathbb E\big[Q^*_M(s_0,\pi(s_0))\big],$$
because $\Phi(s_0)$ is $\pi$-independent. So $\arg\max_\pi Q^*_{M_0}=\arg\max_\pi Q^*_M$ **as sets**. $\blacksquare$

### A.12.3 Proof of necessity (sketch, contrapositive)

Ng et al., Appendix A. If $F$ is not potential-based, there exist $s,a,s'$ with $F(s,a,s')\ne\gamma\Phi(s')-\Phi(s)$ for *every* candidate $\Phi$. Construct an MDP with a state $x$ having two actions: "stay" (reward 0 forever) and "go" (enters a trap $y$ with a one-time reward). $R$ is chosen so the *shaped* problem prefers "go" (because $F(x,\text{go},y)$ is large) while the *unshaped* problem prefers "stay". Key mechanism: with $n$ intermediate states, the telescoped sum of a potential-based $F$ over the path is bounded by $\Phi(\text{start})-\Phi(\text{end})$ — **independent of $n$** — whereas a non-potential $F$ can be arranged to accumulate $\Theta(n)$. So the shaped problem's total return flips sign relative to the unshaped one as $n$ varies, and no invariant guarantee is possible. $\square$

### A.12.4 Telescoping and no positive cycles

> **Corollary A.39 (telescoping).** For any trajectory $\tau=(s_0,a_0,s_1,\dots,s_T)$:
> $$\sum_{t=0}^{T-1}\gamma^tF(s_t,a_t,s_{t+1})=\gamma^T\Phi(s_T)-\Phi(s_0).$$
> *Proof:* $\sum_t\gamma^{t+1}\Phi(s_{t+1})-\sum_t\gamma^t\Phi(s_t)$ telescopes. $\square$

> **Corollary A.40 (no positive cycles).** For a closed cycle $s_0\to\cdots\to s_T=s_0$, the shaped contribution is $(\gamma^T-1)\Phi(s_0)$; for $\gamma=1$ it is **exactly 0**. Potential-based shaping **cannot** create a positive-reward cycle — exactly the pathology that naive shaping creates: Naive & Barto (1990) reward-for-progress produced agents that "rode a bicycle in tiny circles near the start state" (Randal, Åström & Barto 1998) or a soccer robot that "vibrated" next to the ball.

### A.12.5 Application: justifying a coverage-based shaping term

**Construction.** Unshaped mission reward:
$$R(s_t,\mathbf a_t)=\alpha\mathbb 1[\text{battery-constrained coverage requirement met at } t]-\alpha_{\rm fail}\mathbb 1[\text{SoC hits reserve floor}]-\alpha_{\rm coll}\mathbb 1[\text{collision}].$$
Sparse and delayed. Add the shaping
$$\boxed{\;F(s_t,\mathbf a_t,s_{t+1})=\gamma\Phi(s_{t+1})-\Phi(s_t),\qquad \Phi(s)=-\kappa\,\mathcal U(s)\;}$$
where $\mathcal U(s)$ is a **state-only** potential:
- **Coverage-deficit potential.** With multi-coverage count field $\mathcal C(s,x)$ and requirement $K$:
$$\mathcal U(s)=\int_{\mathcal R}\max\big(0,\ K-\mathcal C(s,x)\big)\,dx\ \ge 0 .$$
Since $\mathcal U$ is bounded on bounded $\mathcal R$, $\Phi$ is bounded and Theorem A.36 applies. As the swarm closes gaps $\mathcal U$ falls, so $\Phi$ rises and $F>0$ on improvement, $F<0$ on degradation. **The requirement that $\Phi$ depend on $s$ only, not on $(s,a,s')$, is the entire content of the theorem.**
- **Energy potential.** $\Phi_{\rm energy}(s)=-\lambda\,\mathrm{SoC}(s)$, so $F>0$ when SoC rises — the KiBaM-aware reward (Part D) made policy-invariant. It cannot make "sit on the pad forever" optimal, because the net effect is bounded and telescopes.
- **Connectivity potential.** $\Phi_{\rm conn}(s)=-\mu\lambda_2(s)$ (or $-\mu\times$#components of $G_R(s)$) from Part C, so $F$ rewards increases in algebraic connectivity and penalises fragmentation. This is the correct way to *bias* toward biconnectivity (C.27, C.28) without changing the optimal policy — the **hard** requirement must be enforced separately by a constrained-MARL Lagrangian (A.12.7).

**The claim to make in the report, stated precisely.**

> By Theorem A.36 (Ng, Harada & Russell 1999), adding $F(s,a,s')=\gamma\Phi(s')-\Phi(s)$ to the mission reward leaves the set of optimal policies invariant; by Corollary A.37 all $Q$- and $V$-functions are invariant up to the additive potential $\Phi(s)$. By Remark A.38 this holds for **all** policies, and since $\Phi$ depends only on $s$, the shaped objective is $J_{M_0}(\pi)=J_M(\pi)-\Phi(s_0)$, a **constant shift for every policy** — so $\nabla_\theta J_{M_0}=\nabla_\theta J_M$ identically. The shaping therefore cannot change what the optimal policy is; it can only change the finite-sample learning signal, by increasing the density of informative reward along near-optimal trajectories. Conversely, Theorem A.36 (necessity) says a non-potential term — e.g. a per-step bonus $b\cdot\mathbb 1[\text{moved closer to the nearest uncovered point}]$, which is a *state-action* function, not a difference of potentials — **can** and generically **will** produce a policy optimal for the shaped problem and suboptimal for the real one. Any coverage bonus in the report not of the form $\gamma\Phi(s')-\Phi(s)$ must therefore be justified as a change to the **task** (i.e. it *is* the reward), not as an auxiliary signal.

**Note on a checkable convention error.** Some papers use $F=\Phi(s')-\Phi(s)$ (undiscounted form) and call it "potential-inspired". Ng et al. explicitly warn this is **not** covered by Theorem 1 unless $\gamma=1$ (where the theorem carries the parenthetical "and, if $\gamma=1$, that $\Phi(s')=0$"). A report writing $F=\Phi(s')-\Phi(s)$ with $\gamma<1$ uses the potential-*inspired* form and **loses the guarantee**.

### A.12.6 GAE and potential-based shaping — the relationship, stated correctly

These are two different objects and **must not be identified**. (This corrects a common error; the accurate statement is given here in full.)

| | Potential-based shaping (A.12) | GAE (A.6) |
|---|---|---|
| What is constructed | a new **reward** $r_{t+1}+F(s_t,a_t,s_{t+1})$ | an **estimator** $\hat A_t$ of the advantage of the *unchanged* reward |
| Discount used | $\gamma$ (fixed by the MDP) | $\gamma\lambda$ (a tunable trace decay) |
| Effect on $J$ | $J_{M_0}(\pi)=J_M(\pi)-\Phi(s_0)$, invariant for **all** $\pi$ | none — $J$ is untouched; only $\hat g$'s bias/variance changes |
| Policy optimality | provably preserved (Thm A.36) | irrelevant; the objective is untouched |
| $\lambda$ or $\Phi$ role | $\Phi$ is a state-only bias | $\lambda$ interpolates bias ($\lambda\!\to\!1$) $\to$ variance ($\lambda\!\to\!0$) |

**The one true structural link.** The GAE recursion and the λ-return recursion are the *same recursion shifted by the baseline*:
$$\hat A^{\mathrm{GAE}}_t=\delta^V_t+\gamma\lambda\hat A^{\mathrm{GAE}}_{t+1}\quad\Longleftrightarrow\quad G^\lambda_t=r_{t+1}+\gamma G^\lambda_{t+1}-\gamma(1-\lambda)V(s_{t+1}),$$
and $G^\lambda_t-V(s_t)=\hat A^{\mathrm{GAE}}_t$ (Theorem A.24). That is: **GAE is a TD($\lambda$) backup applied to the advantage rather than the value.** No claim about potential-based reward shaping is involved, and none is correct.

**Why the tempting identification fails.** If one tries $\Phi=V$ and $\tilde\gamma=\gamma\lambda$ in $F(s,a,s')=\tilde\gamma\Phi(s')-\Phi(s)$, then the shaped reward is
$$\tilde r_{t+1}=r_{t+1}+\gamma\lambda V(s_{t+1})-V(s_t)=\delta^V_{t+1}+(\gamma\lambda-\gamma)V(s_{t+2}),$$
which is **not** $\delta^V_{t+1}$ and whose $\gamma\lambda$-discounted sum telescopes to $-\Phi(s_0)/(1-\gamma\lambda)$ plus the *unchanged* $J$ — not to $\hat A^{\mathrm{GAE}}$. Setting $\tilde\gamma\ne\gamma$ additionally destroys the policy-invariance guarantee of Theorem A.36 (which is stated for a fixed $\gamma$), so the identification is wrong twice over.

### A.12.7 When shaping is *not* the right tool: constrained MARL

A hard requirement such as "maintain $K$-fold coverage **at all times**" or "keep the communication graph 2-connected **at all times**" is a **constraint**, not a preference. Potential-based shaping provably cannot enforce it (it only re-ranks policies that already satisfy the underlying objective). The correct machinery is **CMDP with a Lagrangian**:
$$\max_\pi J_{\rm mission}(\pi)\quad\text{s.t. }J_{\mathcal C}(\pi)\le d,\qquad \mathcal L(\pi,\lambda)=J_{\rm mission}(\pi)-\lambda\big(J_{\mathcal C}(\pi)-d\big),\ \lambda\ge0,$$
with dual ascent $\lambda\leftarrow[\lambda+\eta(J_{\mathcal C}-d)]_+$. This is the framework of the NeurIPS 2024 constrained-MARL PPO line and is the mathematically correct way to impose the Part B/C feasibility conditions ($N\pi r^2\ge KA$, $\lambda_2>0$, $\lambda_3>0$) on the learned policy. **A report that uses only reward shaping to enforce a hard fault-tolerance constraint is making an error.** For a *hard* persistent-coverage constraint, prefer a safety layer (e.g. a CBF-CQL shield maintaining $\lambda_2\ge\lambda_2^{\min}$, §C.24) over reward.

---
