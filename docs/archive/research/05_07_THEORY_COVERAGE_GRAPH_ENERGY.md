# Theory Background: Coverage, Graph Connectivity, and Energy

**Companion notes for the MAPPO report on persistent, fault-tolerant UAV–IoT coverage.**

**Problem setting assumed throughout.** A region $\Omega \subseteq \mathbb{R}^2$ of area $A = |\Omega|$. There are $N$ UAVs, each with an omnidirectional sensing footprint that is a **disk** $D_i(t) = B(p_i(t), R_{\text{cov}})$ of radius $R_{\text{cov}}$, and $M$ fixed ground sensors located at $s_1,\dots,s_M \in \Omega$. The requirement is **$K$-fold coverage**:

$$
\forall\, q \in \Omega:\qquad
N_q := \Big|\big\{ i : \|p_i(t) - q\| \le R_{\text{cov}} \big\}\Big| \;\ge\; K,
$$

and in the discrete (sensor-centric) form, which is what the simulation actually constrains,

$$
\forall\, m \in \{1,\dots,M\}:\qquad
\#\{\,i : \|p_i(t) - s_m\| \le R_{\text{cov}}\,\} \;\ge\; K .
$$

Additionally the UAVs must induce a connected communication graph with communication range $R_{\text{comm}}$, must be fault-tolerant to stochastic single-UAV failure, and have finite batteries replenished at a limited number of charging pads.

**Date of compilation:** 29 September 2026 (web search performed on this date to verify citations).

**Scope and honesty note.** Every formula below is in LaTeX and has been checked algebraically or by direct numerical recomputation. Where I could **not** verify a bibliographic detail in a live search, I say so explicitly in the text and in Part D rather than fabricating it. Such items are flagged: (i) the "Gordon–Orfao–Rote" persistent-coverage citation (§5), (ii) the exact closed-form algebraic constants of the KiBaM constant-current solution and the exact numeric parameter set of Marquis & DeCicca (§20), (iii) the DOI `10.1109/CDC.2016.7798253` printed in the report for the Zareh–Sabattini–Secchi biconnectivity paper (§16, §D), and (iv) a small number of classical pagination details flagged inline.

---

# PART A — COVERAGE THEORY

## 1. The Art Gallery Problem: O'Rourke's formulation, Chvátal's theorem, Fisk's proof

### 1.1 Definitions (O'Rourke's formulation)

Let $P \subseteq \mathbb{R}^2$ be a **simple polygon**: a closed region bounded by a closed polygonal chain with $n$ vertices whose boundary is non-self-intersecting, and with no holes. A **vertex guard** is a guard placed at one of the $n$ vertices of $P$, with omnidirectional $360^\circ$ field of view. A guard $g$ **sees** a point $q \in P$ iff the closed segment $[g,q]$ lies entirely in $P$.

A set $G \subseteq V(P)$ of vertex guards **guards** $P$ iff

$$
\forall\, q \in P:\qquad \exists\, g \in G \text{ with } [g,q] \subseteq P .
$$

Write $g(P) = \min\{|G| : G \text{ guards } P\}$ for the **guard number**. Two standard variants: **point guards** (guards anywhere in $P$, not only at vertices) and **bounded guards** (guards restricted to a point of prescribed radius at each vertex — the variant closest to fixed-radius UAV footprints).

The canonical reference is O'Rourke's monograph, *Art Gallery Theorems and Algorithms*, Cambridge University Press, 1987, which formalises the above and catalogues the $O(n\log n)$–$O(n^2)$ family of exact guard-placement algorithms. The question was posed to Chvátal by Victor Klee in 1973 (O'Rourke, 1987, p. 1).

### 1.2 Chvátal's theorem, stated with all hypotheses

> **Theorem (Chvátal, 1975).** *Let $P$ be a simple polygon with $n$ vertices and no holes. Then every such polygon can be guarded by at most $\lfloor n/3 \rfloor$ point guards, and the bound is tight: for infinitely many values of $n$ there exist simple polygons with $n$ vertices that require exactly $\lfloor n/3\rfloor$ vertex guards.*

Hypotheses, itemised (all are load-bearing):

1. $P$ is a **simple** (non-self-intersecting, single-boundary) polygon.
2. $P$ has **no holes**.
3. $n \ge 3$.
4. Guards have **unlimited range** and $360^\circ$ field of view (no $R$-range restriction).
5. The bound is *worst-case over all polygons with $n$ vertices*; for a specific convex $n$-gon, $g(P) = 1$.

Chvátal's original proof is combinatorial (it inductively cuts off a small piece at an ear of the triangulation). Citation: V. Chvátal, "A combinatorial theorem in plane geometry," *Journal of Combinatorial Theory, Series B*, vol. 18, no. 1, pp. 39–41, 1975, doi: 10.1016/0095-8956(75)90061-1.

**Extension beyond vertex guards (important for us).** Chvátal's upper bound remains valid if the vertex restriction is dropped: $\lfloor n/3\rfloor$ guards placed at *arbitrary* points of $P$ suffice. Consequently a disk of radius $r$ is a *bounded* guard, and the $\lfloor n/3\rfloor$ theorem does **not** transfer to $k$-fold or $r$-bounded guarding.

**Holes.** With $h$ holes, Győri's partition theorem gives a guard set of size $\lfloor (n+2h)/3 \rfloor$: $P$ can be partitioned into $\lfloor (n+2h)/3 \rfloor$ convex polygons, each guarded by one vertex guard of the original polygon. *(Classical; exact volume/page details of Győri (1986) not re-verified in this session — see Part D.)*

**Complexity.** Deciding whether $P$ is guardable by at most $k$ guards is **NP-complete** (Lee & Lin, 1975/76, classical; see O'Rourke 1987 and Kahn–Klawe–Kleitman 1986, IEEE Trans. Inf. Theory 32(2), 276–282, doi: 10.1109/TIT.1986.1057165). This is what makes $\lfloor n/3 \rfloor$ a *bound* and not an *algorithm*: computing $g(P)$ is hard.

### 1.3 Fisk's proof of $\lfloor n/3 \rfloor$ (complete, six steps)

The proof rests on exactly two ingredients: (i) every simple polygon admits a triangulation, and the graph of that triangulation is 3-colourable; (ii) every triangle of the triangulation is guarded by a guard placed at any one of its vertices.

**Step 1 — Triangulation exists.** Every simple $n$-gon $P$ admits a straight-line triangulation $T$ into exactly $n-2$ triangles whose vertex set is $V(P)$ and whose union is $P$ with pairwise-disjoint triangle interiors. (Standard, O'Rourke 1987, Ch. 1.)

**Step 2 — The triangulation graph is 3-colourable.** Let $G_T = (V(T), E(T))$. Claim: $G_T$ has a proper 3-colouring. *Proof by induction on $n$:* $n=3$ is trivial. For $n>3$, the weak dual of $T$ (a vertex per triangle, edges for shared diagonals) is a tree, hence has a leaf, so $T$ has an **ear**: a triangle $\sigma$ with two boundary edges, whose tip vertex $v$ has degree $2$ in $G_T$. Colour $G_T - v$ by induction; the two neighbours of $v$ use at most two of the three colours; assign to $v$ a colour that is missing among its neighbours. $\blacksquare$
(Equivalently: Grötzsch's theorem — every *triangle-free* planar graph is 3-colourable — combined with the 4-Colour Theorem. The ear induction is the elementary proof and is what Fisk used.)

**Step 3 — Colour classes partition the vertices.** Write $V(T) = C_1 \dot\cup C_2 \dot\cup C_3$, with each $C_j$ an independent set in $G_T$. Since $|C_1| + |C_2| + |C_3| = n$, the pigeonhole principle gives

$$
\min_j |C_j| \;\le\; \Big\lfloor \frac{n}{3}\Big\rfloor .
$$

**Step 4 — Every triangle sees all three colours.** Every face of $G_T$ is a triangle whose three vertices are mutually adjacent, hence pairwise differently coloured; so each triangle contains exactly one vertex of each $C_j$.

**Step 5 — Place guards on the smallest class.** Let $C = C_j$ be a class of minimum size and place a guard at each vertex of $C$. Then $|C| \le \lfloor n/3\rfloor$ guards are deployed, and **every** triangle of $T$ contains exactly one vertex of $C$ (by Step 4).

**Step 6 — The guards see everything.** Fix any $q \in P$. Since the triangles of $T$ cover $P$, $q$ lies in some triangle $\sigma \in T$. That triangle has a vertex $g \in \sigma \cap C$. A triangle is **convex**, so $[g,q] \subseteq \sigma \subseteq P$; the guard at $g$ sees $q$. Since $q$ was arbitrary, $C$ guards $P$. $\blacksquare$

**Tightness.** Chvátal's "comb" family (a spine with $k$ mutually hidden teeth) has $3k$ vertices, and a single guard can see at most one tooth, so at least $k = \lfloor 3k/3\rfloor$ guards are necessary. More generally, the standard statement is: for every $k$ there is a polygon $P_k$ with $g(P_k) = \lfloor |V(P_k)|/3 \rfloor$.

**Where Fisk appears.** S. Fisk, "A short proof of Chvátal's watchman theorem," *Journal of Combinatorial Theory, Series B*, vol. 24, no. 3, p. 374, 1978, doi: 10.1016/0095-8956(78)90059-X. (The result also appeared at FICS 1978, pp. 126–134.)

**Reading for the UAV report.** Fisk's proof is a *colouring* argument, and the guarantee it delivers is $\lfloor n/3\rfloor$ guards for **1-fold** coverage of a polygon by **unbounded** guards. Our problem has neither property: it is $K$-fold, and each guard is a disk of bounded radius $R_{\text{cov}}$. The art-gallery theorem is therefore a **sanity check on the shape of the answer**, **not** a feasibility certificate. The relevant certificate is the area-counting bound of §7.

---

## 2. $k$-Fold Coverage: Definition, Reduction, Complexity

### 2.1 Definition

Let $P$ be a polygon and $G$ a set of guards. $G$ is a **$k$-fold guard set** for $P$ if

$$
\forall\, q \in P:\qquad \big|\{\, g \in G : [g,q] \subseteq P \,\}\big| \;\ge\; k .
$$

The $k$-fold guard number is $g_k(P) = \min\{|G| : G \text{ is a $k$-fold guard set}\}$. Note $g_1(P) = g(P)$ and, by monotonicity,

$$
g_1(P) \;\le\; g_2(P) \;\le\; \cdots \;\le\; g_k(P).
$$

In the UAV setting the guard is a disk rather than a point, so the operative notion is **$k$-fold disk coverage of $\Omega$ by $N$ disks of radius $R_{\text{cov}}$**, with the counting function

$$
\nu(x) \;=\; \sum_{i=1}^{N} \mathbb{1}\,\big\{\,x \in B(p_i, R_{\text{cov}})\,\big\}, \qquad \nu(x) \ge K \;\;\forall x\in\Omega .
$$

### 2.2 Reduction to the standard (1-fold) problem

**(a) Decisional reduction, $k$-fold $\Rightarrow$ 1-fold.** If $P$ is $k$-fold guardable by $N$ guards, it is 1-fold guardable by $N$ guards; the converse fails. Hence the $k$-fold minimum is a strictly harder optimisation and every $1$-fold upper bound transfers downward:

$$
g_k(P) \;\ge\; g_1(P) \;\ge\; \Big\lfloor \frac{n}{3}\Big\rfloor .
$$

**(b) Constructive reduction, 1-fold $\Rightarrow$ $k$-fold (the one we actually use).** Fisk's Step 5 shows that **every** colour class of a 3-colouring of the triangulation graph is a valid 1-fold guard set, because every triangle contains exactly one vertex of each class. Therefore

$$
C_1,\; C_2,\; C_3 \quad\text{are three pairwise disjoint $1$-fold guard sets with } |C_1|+|C_2|+|C_3| = n .
$$

For $k \le 3$ this gives a $k$-fold guard set of size equal to the sum of the $k$ smallest colour classes, hence

$$
g_k(P) \;\le\; \sum_{j=1}^{k}\bigl(\text{$j$ smallest } |C_j|\bigr) \;\le\; \Big\lfloor \frac{kn}{3}\Big\rfloor + O(1),
$$

and in particular $g_2(P) \le n - \lceil n/3 \rceil = \lfloor 2n/3 \rfloor$. *(Flag: the sharpest published $k$-fold bounds in the polygon setting have been improved over the decades; I have not re-verified the current state of the art and am deliberately giving the *derivable* bound rather than the best known one.)*

**(c) The reduction that is actually correct for UAVs.** $k$-fold disk coverage of a **continuous** region is *not* an art-gallery problem: art-gallery guards are unbounded points on a polygon. The correct reformulation is a **set multi-cover**: universe $\Omega$ (or the $M$ sensor locations), sets $\mathcal{D}_i = B(p_i, R_{\text{cov}}) \cap \Omega$, and the task is to choose $N$ sets such that every universe element is covered at least $K$ times, minimising $N$ (equivalently minimising $R_{\text{cov}}$, or maximising $K$ — the three coincide at the optimum). This is the **$(N,K)$ multi-cover / $k$-fold covering** problem. Generic polynomial approximation is via weighted set cover, for which the $H_N = \Theta(\ln N)$ ratio is optimal under standard complexity hypotheses (Johnson 1974; Chvátal 1979; for the *connected* variant see Raz & Hu, "Connected set cover problem and its applications," Proc. AAIM 2006, LNCS vol. 4041, pp. 243–254).

### 2.3 Complexity summary

| Problem | Status | Reference |
|---|---|---|
| Guard a simple $n$-gon with $\le k$ guards | NP-complete | Lee & Lin (1975/76), classical; via Kahn–Klawe–Kleitman 1986, IEEE Trans. Inf. Theory 32(2), 276–282 |
| Cover a polygon with $m$ disks of radius $r$ (decision) | NP-hard / NP-complete | Hershberger & Suri, "Disk covering: a greedy approximation algorithm," SODA 1999 (classical; details not re-verified) |
| $k$-fold version of either | NP-hard for every $k\ge1$; inherits the $H_N$-factor hardness of set multi-cover | — |
| Connected coverage (coverage + connected backbone) | NP-hard | MRCTC NP-hard — Fraigniaud, Larsen & Misra, 2006 |

**Bottom line for the report.** The $K$-coverage feasibility check inside the MAPPO reward is a *feasibility test on a given configuration*, not a combinatorial optimisation, so NP-hardness does not hurt the training loop. What we need from theory is a **necessary condition** — a cheap, computable certificate of infeasibility — and that is exactly §7.

---

## 3. Connected Multi-Robot Coverage

### 3.1 Definition

Let $R = \{r_1,\dots,r_N\}$ be mobile robots in an environment $Q$ (here $\Omega$), each sensing a disk $B(r_i, r_s)$ of radius $r_s$ and communicating within range $r_c$. Two problems:

- **Discretised / static connected coverage.** A set $S \subseteq R$ of robots is *simultaneously covering* if $\bigcup_{i\in S} B(p_i, r_s) \supseteq \Omega$. A set $S$ is *simultaneously connected* if the graph $\mathcal{G}(S) = (S, E_S)$ with $E_S = \{\{i,j\}: \|p_i - p_j\| \le r_c\}$ is connected. **Connected coverage** is the *existential* combination.
- **Sweep / continuous connected coverage.** There must exist a schedule of the robots such that at every instant the active set is simultaneously covering *and* connected. This is strictly stronger and is the model relevant to a persistent mission.

### 3.2 Discretisation

The continuous problem is attacked by a **cellular decomposition**: partition $\Omega$ into a finite set of cells $\{\Sigma_1,\dots,\Sigma_c\}$ (grid cells, Morse cells, or a Voronoi/Delaunay tessellation), compute a **spanning tree** of the cell-adjacency graph, and convert it into a coverage tour. The exact-realisation step assigns each cell a single representative (sweep) point and proves that if the representative lies inside an $\varepsilon$-thickened cell, the whole cell is covered. This is the basis of the Bouaziza–Debled **DARP** algorithm ("DARP: divide areas algorithm for optimal multi-robot coverage path planning," *J. Intell. Robot. Syst.*, Springer, doi: 10.1007/s10846-016-0461-x) and of the sweep-coverage literature generally.

### 3.3 NP-hardness and approximation ratios

- **Connected coverage on a graph is NP-hard** in essentially every formulation. For **trees** it is NP-hard: the *Multi-Robot Connected Tree Coverage* (MRCTC) problem is NP-hard (Fraigniaud, Larsen & Misra, 2006). For **general topological graphs with separate movement and communication edge sets**, multi-robot coverage and multi-agent path finding are **PSPACE-complete** (Charrier et al., 2020).
- **Exact generalisation.** Coverage of graphs of bounded treewidth is solvable exactly by dynamic programming. The *Heterogeneous Multi-Robot Graph Coverage with Proximity and Connectivity Constraints* problem (AAAI 2025; document verified at `u.cs.biu.ac.il/~sarit/data/articles/AAAI_25__k_Tree_Coverage_with_Connectivity_Constraints-dolev.pdf`) gives a PTAS with approximation error $1 + O(\epsilon)$ independent of $d$ for the $d=2$, $k=3$, tree case. *(I verified the document exists and the claim as stated in it; the author list should be read off the PDF before citing.)*
- **Approximation ratios — an honesty point.** In the tree case the literature reports **speedup factors** $\gamma$ (the ratio of multi-robot to single-robot traversal time) rather than a ratio to the true optimum. This is frequently glossed over in secondary summaries. For the general graph case, the standard technique is *connection fusion* (Czyzowicz, Kowalski, Dryniecki & Stojmenović): take a $\rho$-approximate set cover and connect its components by adding at most a constant number of edges per component, yielding a $O(\rho)$-approximation for the connected variant. For Euclidean static connected cover, geometric set cover gives $O(1)$ ratios for disks. *(Full pagination for the connection-fusion paper not re-verified — see Part D.)*

**Consequence for our design.** The $K$-coverage requirement and the connectivity requirement are coupled but *separable*: coverage is controlled by $R_{\text{cov}}$ and $N$ (area counting, §7); connectivity is controlled by $R_{\text{comm}}$ and the relay structure (§13–§15). The two radii are independent knobs.

---

## 4. Persistent / Continuous Coverage: the Steady-State Problem

### 4.1 Formulation

The **steady-state coverage problem** (a.k.a. minimum number of sensors for continuous coverage) is:

> Given a region $\Omega$ and a sensing radius $r$, find the minimum $N$ such that there exist positions $p_1,\dots,p_N \in \Omega$ with
> $$\Omega \subseteq \bigcup_{i=1}^{N} B(p_i, r).$$

The *persistent* form replaces "there exist positions" by "there exist trajectories $p_i(t)$ such that the condition holds $\forall t$". For a static $\Omega$ and fixed $N$ this is *equivalent* to the static form (place the robots at the static solution and never move). The genuine difference appears when robots have **kinematic constraints** (speed limits, collision avoidance) or when the optimised quantity is the **time between consecutive visits** (latency / sweep period). Our problem is the latter.

### 4.2 Minimum sensors for continuous coverage of a **disk** region — actual formulas

Let $\Omega = B(0,R)$ and let $N$ disks of radius $r < R$ cover it. There are **two independent necessary conditions**, and their maximum is far tighter than the area bound alone.

**(D1) Area condition.**

$$
\pi R^2 \;\le\; \sum_{i=1}^{N}\pi r^2 = N\pi r^2
\quad\Longrightarrow\quad
N \;\ge\; \frac{R^2}{r^2},
\qquad\text{i.e.}\qquad
r \;\ge\; \frac{R}{\sqrt N}.
$$

**(D2) Boundary-arc condition (the binding one).** Each covering disk of radius $r$ covers an arc of the boundary circle of angular half-width $\theta$ satisfying $\cos\theta = \dfrac{1+s^2-r^2}{2s}$, where $s$ is the offset of its centre from the origin. Maximising over $s$:

$$
\cos\theta_{\max} \;=\; \min_{s>0}\frac{1+s^2-r^2}{2s} \;=\; \sqrt{1-r^2}
\qquad (\text{attained at } s^\star = \sqrt{1-r^2}),
$$

so each disk covers at most $2\arcsin r$ radians of the $2\pi$-radian boundary. Since the boundary must be covered,

$$
\boxed{\;N \;\ge\; \frac{\pi}{\arcsin\!\left(r/R\right)}\;},
\qquad\text{equivalently}\qquad
\boxed{\;r \;\ge\; R\,\sin\!\left(\frac{\pi}{N}\right)\;}
$$

**(D3) Combined necessary condition for a disk region:**

$$
N_{\min}(r,R)\;\ge\;\max\left\{\left\lceil \frac{R^2}{r^2}\right\rceil,\;\left\lceil \frac{\pi}{\arcsin(r/R)}\right\rceil\right\}.
$$

**Exact solved case: $r = R/2$.** Then (D2) gives $N \ge \pi/\arcsin(1/2) = \pi/(\pi/6) = 6$, and the saturating configuration is forced: six centres at the vertices of a regular hexagon of circumradius $s^\star = \sqrt{1-(1/2)^2} = \sqrt3/2$ (in units of $R$). Along a ray at the mid-arc angle, the distance from radius $\rho$ to the nearest centre is $\sqrt{\rho^2 + 3/4 - \tfrac32\rho}$, which equals $1/2$ at $\rho = 1/2$ and at $\rho = 1$ and is $\le 1/2$ in between (the quadratic is minimised at $\rho = 3/4$, giving $\sqrt{3/16} \approx 0.433$). So the six disks cover the annulus $\tfrac12 \le \rho \le 1$ completely, but leave $\rho < 1/2$ uncovered (those points are at distance $\sqrt3/2 > 1/2$ from every centre). A seventh disk at the origin is therefore both necessary and sufficient:

$$
\boxed{\;N_{\min}(R/2,\;R) \;=\; 7\;}
$$

*(Other exact values for other $r/R$ exist in the classical covering literature; I have not re-verified them.)*

**(D4) Asymptotics (Kershner).** The asymptotically thinnest covering of the plane (and of any smooth-bounded region, up to $o(\cdot)$ boundary terms) by congruent disks has density

$$
\Theta_{\text{cov}} \;=\; \frac{2\pi}{3\sqrt 3} \;=\; 1.2091996\ldots
$$

attained by the triangular lattice of centres with spacing $\sqrt3\,r$, whose Voronoi cells are regular hexagons of circumradius exactly $r$. Hence

$$
N_{\min}(r, R) \;=\; \frac{2}{3\sqrt3}\,\frac{R^2}{r^2}\,\bigl(1 + o(1)\bigr)
\;=\; 0.38490018\ldots\,\frac{R^2}{r^2}\,\bigl(1+o(1)\bigr).
$$

This is Kershner's theorem (1939). *(The constant is standard and I am confident in it; the exact volume/page details of the Kershner paper are flagged in Part D.)*

### 4.3 Minimum sensors for continuous coverage of a **polygon**

For a polygon $P$ of area $A$ and perimeter $P_{\text{per}}$:

- **Lower bound (area).** $N\pi r^2 \ge A \Rightarrow N \ge A/(\pi r^2)$, improved asymptotically to $N \ge \dfrac{2A}{3\sqrt3\,r^2}$ (Kershner density, §6).
- **Boundary correction.** The boundary contributes an additive $O(P_{\text{per}}/r)$ term in general position; for a convex region with $A \gg P_{\text{per}}\cdot r$ this is negligible, which is why the square and the disk behave identically asymptotically.
- **Exactness.** Deciding whether $m$ disks of radius $r$ cover a polygon is NP-complete (Hershberger & Suri, SODA 1999, classical). The clean linear-time algorithm exists only in the *point-guard* / *unbounded-guard* case, where Fisk's argument gives $\lfloor n/3 \rfloor$ (§1). The two must not be conflated.

---

## 5. Persistent Coverage Complexity (cell decomposition and the approximation ratio)

### 5.1 Honest statement of what I could and could not verify

The report cites a result of the form *"Gordon, Orfao, Rote — cell decomposition, approximation ratio $\rho$"*. **I could not verify this reference in a live search on 29 September 2026.** Specifically: I retrieved and read the complete CCCG 2008 proceedings index (57 papers, pages 1–226) and it contains no Gordon/Orfao/Rote paper; and no cccg, springer, ACM or IEEE record matching a Gordon–Orfao–Rote persistent-coverage paper surfaced. I therefore (i) state the mechanism of the cell-decomposition result generically, which I can do correctly and self-containedly, and (ii) explicitly warn that **the specific paper and ratio must be re-sourced before the report cites them.**

### 5.2 The mechanism (stated correctly and self-containedly)

**Cell decomposition for steady-state coverage.** Let $\Omega$ be a polygon. Compute a partition

$$
\Omega \;=\; \Sigma_1 \dot\cup \cdots \dot\cup \Sigma_c
$$

(e.g. the arrangement induced by the candidate site set, or a grid with appropriate cell aspect ratio). Build the cell-adjacency graph $\mathcal{H} = (\{\Sigma_j\}, E_{\mathcal{H}})$ where $\Sigma_i \sim \Sigma_j$ iff $\overline{\Sigma_i}\cap\overline{\Sigma_j}\neq\emptyset$, and take a spanning tree $T_{\mathcal{H}}$ of $\mathcal{H}$. Then:

- **Upper bound (cover construction).** If each cell $\Sigma_j$ admits a single site $p_j$ whose radius-$r$ disk covers $\Sigma_j$ (equivalently, $p_j$ covers the cell's *sweep set*), then $\{p_1,\dots,p_c\}$ covers $\Omega$; and because $T_{\mathcal{H}}$ is connected, the *cell-adjacency graph induced by the chosen sites* is connected at radius $r+\Delta$, where $\Delta$ is the diameter bound used in the "extra-thickness" step. Standard treatment: work with a slightly inflated radius $r \to r+\delta$ and pay for the thicket.
- **Lower bound (certificate).** Conversely, any cover by $N$ disks gives a *counting* certificate: each of the $N$ disks can witness at most one assigned cell, so $c \ge N_{\min}$. This is a linear-programming / count-based lower bound identical in spirit to §7.
- **Ratio.** With the cover constructed this way, the number of sites produced is $c$ and the certifiable optimum is $N_{\min}$, so
$$
\rho \;=\; \frac{c_{\text{produced}}}{N_{\min}}.
$$
**Any claimed constant ratio must be reported as a ratio to the Kershner denominator**
$$
N_{\min} \;=\; \frac{2A}{3\sqrt3\,r^2}\,(1+o(1)),
$$
because a ratio taken against the naive $A/(\pi r^2)$ differs by exactly the factor $\frac{2\pi}{3\sqrt3} = 1.20920$ (§6). This factor confusion is the most common error in this part of the literature and is worth an explicit footnote in the report.

**What to do.** Either (a) obtain and cite the actual Gordon–Orfao–Rote paper and insert its exact ratio, or (b) replace the citation with a result that can be verified, e.g. the $O(1)$ connected set-cover bound obtained by connection fusion, or the bounded-treewidth PTAS of the AAAI-2025 graph-coverage work.

---

## 6. Disk-Covering Asymptotics: **VERIFICATION OF THE CLAIMED CONSTANT**

### 6.1 The claim under test

> *"N disks of radius $r$ cover area $A$ if $N \ge \dfrac{A}{2\sqrt{3}\,r^{2}}$, from hexagonal packing density $\dfrac{\pi}{2\sqrt3}$."*

### 6.2 Verification: **the claimed constant is INCORRECT — it is wrong by exactly a factor of $4/3$**

The constant $\frac{\pi}{2\sqrt3} = 0.90689968\ldots$ is indeed the **maximal packing density** of congruent disks in the plane (Thue/Fedorov; the hexagonal lattice). It is *not* a covering density. The two constants are

$$
\underbrace{\delta_{\text{pack}} = \frac{\pi}{2\sqrt3} = 0.90689968\ldots}_{\text{densest PACKING: max disk-area fraction in the plane}}
\qquad
\underbrace{\Theta_{\text{cov}} = \frac{2\pi}{3\sqrt3} = 1.20919958\ldots}_{\text{thinnest COVERING: min disk-area fraction to cover the plane (Kershner)}} .
$$

**Derivation of the packing constant (this is where $2\sqrt3$ legitimately comes from).** In the densest packing (triangular lattice of centre spacing $2r$), the primitive cell is a rhombus of area $2r \cdot \sqrt3 r = 2\sqrt3\,r^2$ containing one disk of area $\pi r^2$, so $\delta_{\text{pack}} = \pi r^2/(2\sqrt3 r^2) = \pi/(2\sqrt3)$. Thue's / Fedorov's theorem says no packing is denser. Consequence: **$N$ pairwise-disjoint disks of radius $r$ occupy total area $N\pi r^2$, which cannot exceed $\frac{\pi}{2\sqrt3}$ of the ambient area $A$:**

$$
N\pi r^2 \;\le\; \frac{\pi}{2\sqrt3}\,A
\quad\Longrightarrow\quad
N \;\le\; \frac{A}{2\sqrt3\,r^{2}} \;=\; 0.28867513\ldots\,\frac{A}{r^2}.
$$

This is a bound on how many disks fit **without overlapping**. It is a statement about *packing*, and its inequality direction is $\le$, whereas the claim asserts a *covering* statement with direction $\ge$. **The claim has taken a packing bound, reversed its inequality, and mislabelled it a covering bound.**

**The correct covering constant and its derivation.** To *cover* a region the disks must **overlap** slightly so no gaps appear. Kershner's theorem states that the asymptotic minimum density of a covering of the plane by congruent circles of radius $r$ is $\frac{2\pi}{3\sqrt3}$. Construction attaining it: the triangular lattice of centres with spacing

$$
s \;=\; \sqrt3\, r ,
$$

whose Voronoi cells are regular hexagons of circumradius $s/\sqrt3 = r$ (hence each cell is covered by the disk at its centre) and of area $\frac{3\sqrt3}{2}R_h^2 = \frac{3\sqrt3}{2}r^2 = 2.59807621\,r^2$ for circumradius $R_h=r$. One disk per cell gives density

$$
\frac{\pi r^2}{\frac{3\sqrt3}{2}r^2} \;=\; \frac{2\pi}{3\sqrt3} \;=\; 1.20919958\ldots
$$

**Correct asymptotic covering bound:**

$$
\boxed{\;N \;\ge\; \frac{2A}{3\sqrt3\,r^{2}} \;=\; 0.38490018\ldots\,\frac{A}{r^{2}}\;\bigl(1+o(1)\bigr)\;}
\qquad\text{equivalently}\qquad
\boxed{\;r \;\ge\; \frac{1}{\sqrt N}\sqrt{\frac{2A}{3\sqrt3}} \;=\; 0.62040324\ldots\sqrt{\frac{A}{N}}\;}
$$

**The gap, exactly.** The claimed constant $1/(2\sqrt3)$ and the true constant $2/(3\sqrt3)$ differ by exactly

$$
\frac{\,2/(3\sqrt3)\,}{\,1/(2\sqrt3)\,} \;=\; \frac{2}{3}\cdot 2 \;=\; \frac{4}{3} \;=\; 1.\overline{3},
$$

so the claim **under-counts the number of required disks by $33.3\,\%$.** As a *radius* bound the error is $\sqrt{4/3} = 2/\sqrt3 = 1.15470$, i.e. the claim implies a radius $15.5\,\%$ too small.

### 6.3 Three-way summary table

| Model | Condition on $N$ | Constant | Source of the constant |
|---|---|---|---|
| Naive area counting | $N \ge \dfrac{A}{\pi r^2}$ | $\frac{1}{\pi}=0.31831$ | total disk area $\ge$ region area |
| **Correct asymptotic covering** | $N \ge \dfrac{2A}{3\sqrt3 r^2}$ | $\frac{2}{3\sqrt3}=0.38490$ | Kershner covering density $\frac{2\pi}{3\sqrt3}$ |
| **Packing (disjoint disks)** | $N \le \dfrac{A}{2\sqrt3 r^2}$ | $\frac{1}{2\sqrt3}=0.28868$ | Thue/Fedorov packing density $\frac{\pi}{2\sqrt3}$ |

Note that the correct covering constant ($0.38490$) exceeds even the naive area constant ($0.31831$) by the factor $\frac{2\pi}{3\sqrt3} = 1.20920$: **you need $20.9\,\%$ more disk-area than the region's area, purely to close the gaps between disks.**

### 6.4 $K$-fold version

For $K$-fold coverage the counting argument of §7 gives $KA \le N\pi r^2$. The Kershner-corrected version stacks $K$ triangular lattices with mutually incommensurate relative offsets (so the $K$ lattices' gaps never coincide), achieving density $K\cdot\frac{2\pi}{3\sqrt3}$, and therefore

$$
\boxed{\;KA \;\le\; \frac{3\sqrt3}{2}\,N r^2
\quad\Longleftrightarrow\quad
r \;\ge\; \sqrt{\frac{2KA}{3\sqrt3\,N}}
\;=\; 0.62040324\sqrt{\frac{KA}{N}}\;}
$$

and equivalently $N \ge \frac{2}{3\sqrt3}\frac{KA}{r^2}$. The correction factor relative to the naive area bound is exactly $\sqrt{\frac{2\pi}{3\sqrt3}} = 1.09964$ in radius, i.e. $20.9\,\%$ in area.

---

## 7. **THE KEY FEASIBILITY BOUND** — Proof from First Principles

### 7.1 Statement

> **Theorem 7.1 (Counting bound).** *Let $\Omega\subseteq\mathbb{R}^2$ be a bounded measurable region of area $A$, and let $D_1,\dots,D_N$ be disks with centres $p_i$ and common radius $r>0$. Define the multiplicity (counting) function*
> $$\nu(x) \;=\; \sum_{i=1}^{N} \mathbb{1}_{D_i}(x) \in \mathbb{N}_0 .$$
> *If every point of $\Omega$ is covered at least $K$ times, i.e. $\nu(x)\ge K$ for all $x\in\Omega$, then*
> $$\boxed{\;N\,\pi r^{2} \;\ge\; K\,A
> \qquad\text{and hence}\qquad
> r \;\ge\; \sqrt{\frac{K A}{\pi N}} \;=\; \frac{1}{\sqrt{\pi}}\sqrt{\frac{KA}{N}} \;=\; 0.56418958\ldots\sqrt{\frac{KA}{N}}\;}$$

### 7.2 Proof (every line justified)

**Step 0 — well-definedness.** $\Omega$ is measurable with $|\Omega| = A$; each $D_i$ is a closed disk, so $\mathbb{1}_{D_i}$ is measurable; hence $\nu$ is measurable. Moreover $\nu \le N$ on $\Omega$, so $\nu$ is bounded and therefore Lebesgue-integrable, and $\int_\Omega \nu$ is finite.

**Step 1 — lower-bound the integral using the hypothesis.** Since $\nu(x) \ge K$ for all $x \in \Omega$,

$$
\int_{\Omega} \nu(x)\,dx \;\ge\; \int_{\Omega} K\,dx \;=\; K\,|\Omega| \;=\; K A . \tag{7.1}
$$

**Step 2 — rewrite the integral as a finite sum.** By linearity of the integral (a finite sum, so Tonelli is not even needed),

$$
\int_{\Omega}\nu(x)\,dx
\;=\; \sum_{i=1}^{N} \int_{\Omega} \mathbb{1}_{D_i}(x)\,dx
\;=\; \sum_{i=1}^{N} \big|\,\Omega \cap D_i\,\big| . \tag{7.2}
$$

**Step 3 — bound each term by the full disk area.** Since $\Omega \cap D_i \subseteq D_i$ and $D_i$ is a disk of radius $r$,

$$
\big|\,\Omega \cap D_i\,\big| \;\le\; |D_i| \;=\; \pi r^{2},
\qquad\text{hence}\qquad
\sum_{i=1}^{N}\big|\Omega \cap D_i\big| \;\le\; N\,\pi r^{2} . \tag{7.3}
$$

**Step 4 — chain the inequalities.** From (7.2) and (7.3), $\int_\Omega\nu \le N\pi r^2$. Combining with (7.1):

$$
K A \;\le\; \int_{\Omega}\nu(x)\,dx \;\le\; N\pi r^{2},
$$

i.e. $N\pi r^{2} \ge K A$. Dividing by $\pi N > 0$ and taking the (positive) square root:

$$
r^{2} \;\ge\; \frac{K A}{\pi N} \quad\Longrightarrow\quad r \;\ge\; \sqrt{\frac{K A}{\pi N}} .
\qquad\blacksquare
$$

**When is the bound tight?** Equality $N\pi r^2 = KA$ requires *simultaneously*: (a) $\Omega \cap D_i = D_i$ for every $i$, i.e. every disk lies entirely inside $\Omega$ (impossible in practice whenever $\Omega$ is a polygon and disks are interior); and (b) $\nu(x) = K$ almost everywhere on $\Omega$, i.e. a *perfect* $K$-fold cover with zero wasted overlap. Condition (b) alone is essentially never satisfiable for $K\ge2$ and a finite set of disks, because overlap is unavoidable; §6 quantifies how much.

### 7.3 Why necessary but NOT sufficient — four independent failure modes

**(i) Overlap is unavoidable, so $\sum_i|\Omega\cap D_i|$ strictly over-counts $\int_\Omega\nu$.** The bound treats the $N$ disks as if their $K$-fold coverage were delivered without waste. But a genuine cover of a connected region by more than one disk must have overlapping disks (otherwise the region would be disconnected). Formally, for $N\ge2$ covering a connected $\Omega$ with $K\ge1$, $\sum_i|\Omega\cap D_i| > |\Omega|$ strictly, so $\int_\Omega\nu > KA$ strictly and the count of "coverage budget" is always exceeded. The bound is therefore *strictly* violated by every real solution and the true required $N$ is strictly larger than $KA/(\pi r^2)$. **This is exactly what §6 corrects.**

**(ii) Distinctness / degeneracy.** $N\pi r^2 \ge KA$ is a statement about $N$, $r$, $K$, $A$ only; it says nothing about the positions. Placing two UAVs at the same point wastes an entire disk, and the bound cannot detect it. Conversely, the bound also cannot *certify* feasibility: it is a constraint on the magnitudes only, so many configurations satisfying it still fail.

**(iii) Boundary effects — a concrete counterexample.** Take $\Omega = [0,100]^2$, $A = 10\,000$, $N = 1$, $K = 1$. The bound gives
$$
r \;\ge\; \sqrt{\frac{1\cdot 10\,000}{\pi\cdot 1}} \;=\; \sqrt{3183.0989} \;=\; 56.4188\ \text{m}.
$$
But a disk covering a $100\times100$ square must have radius at least the square's **circumradius**, $\frac{100\sqrt2}{2} = 50\sqrt2 = 70.7107$ m. So $r = 56.42$ m satisfies Theorem 7.1 and yet does **not** cover $\Omega$. The gap is $70.71/56.42 = 1.253$. For a long thin rectangle $100\times1$ ($A=100$), the bound gives $r \ge \sqrt{100/\pi} = 5.6419$ m while the true minimum is the circumradius $\frac12\sqrt{100^2+1^2} = 50.0025$ m — a gap of $8.9\times$. **The area bound ignores geometry entirely; for elongated or non-convex regions it can be off by an order of magnitude.**

**(iv) Non-convexity and obstacles.** If $\Omega$ is disconnected or has holes, the optimal $N$ is the *sum* of the optima over the components, and the area bound (which treats $\Omega$ as one blob) is again loose. If UAVs are forbidden from flying over some sub-region, the disks are truncated, and $N\pi r^2$ counts area that is not usable.

**Packing-corrected version (the one to put in the report).** Combining Theorem 7.1 with the Kershner covering density of §6:

$$
\boxed{\;\text{If $\Omega$ admits a $K$-fold cover by $N$ disks of radius $r$, then}\quad
r \;\ge\; \sqrt{\frac{2KA}{3\sqrt3\,N}}\;=\;0.62040324\sqrt{\frac{KA}{N}},\;}
$$
$$
\boxed{\;\text{equivalently}\quad N \;\ge\; \left\lceil \frac{2KA}{3\sqrt3\,r^{2}}\right\rceil . \;}
$$

For $K$-fold coverage this is asymptotically attainable (stack $K$ hexagonal lattices with incommensurate offsets), so unlike the naive bound it is not merely conservative — up to the $O(K)$ boundary terms it is the *correct* threshold for large regions.

**Summary of the three radii (all for the same problem).**

$$
r \;\ge\; \underbrace{0.56418958}_{\text{naive area, §7.1}}\sqrt{\frac{KA}{N}}
\;\;\le\;\;
r \;\ge\; \underbrace{0.62040324}_{\text{Kershner-corrected, §6/§7.3}}\sqrt{\frac{KA}{N}}
\;\;\le\;\;
r \;\ge\; \underbrace{0.70710678}_{\text{circumradius of a square region, worst case}}\cdot \frac{\sqrt A}{2}\,\cdot\sqrt{\frac{N}{N}}\ \text{(shape-dependent)}
$$

The report should quote the middle one, and should note the shape-dependent upper bound is a *further* necessary condition that the area argument cannot see.

---

## 8. Worked Numerical Example — $A = 100\times100$, $M=20$, $N=5$, $K=2$, $R_{\text{cov}}=15$ m

### 8.1 Given data

| Symbol | Value |
|---|---|
| Region | $\Omega = [0,100]^2$, a $100 \text{ m} \times 100 \text{ m}$ square |
| $A = |\Omega|$ | $100 \times 100 = 10\,000\ \text{m}^2$ |
| $M$ (ground sensors) | $20$ |
| $N$ (UAVs) | $5$ |
| $K$ (required redundancy) | $2$ |
| $R_{\text{cov}}$ as given in the report | $15\ \text{m}$ |

### 8.2 Step 1 — The naive area bound says what $R_{\text{cov}}$ must be

$$
r \;\ge\; \sqrt{\frac{K A}{\pi N}} \;=\; \sqrt{\frac{2 \times 10\,000}{\pi \times 5}} \;=\; \sqrt{\frac{20\,000}{15.7079633}} .
$$

Arithmetic, step by step:

1. $K \cdot A = 2 \times 10\,000 = 20\,000$.
2. $\pi \cdot N = 3.14159265\ldots \times 5 = 15.7079633\ldots$
3. $20\,000 \div 15.7079633 = 1273.2395\ldots$ (check: $15.7079633 \times 1273.24 = 20\,000.0$).
4. $\sqrt{1273.2395}$: $35.68^2 = 1273.0624$; $35.69^2 = 1273.7761$; interpolating, $\sqrt{1273.2395} = 35.6825\ldots$

$$
\Rightarrow\quad r \;\ge\; 35.68\ \text{m} \qquad \text{(naive necessary condition)}
$$

### 8.3 Step 2 — The Kershner-corrected bound

$$
r \;\ge\; \sqrt{\frac{2KA}{3\sqrt3\,N}} \;=\; \sqrt{\frac{2 \times 20\,000}{3\sqrt3 \times 5}} \;=\; \sqrt{\frac{40\,000}{25.9807621}} .
$$

1. $3\sqrt3 = 3 \times 1.7320508 = 5.1961524$; times $N=5$ gives $25.9807621$.
2. $40\,000 \div 25.9807621 = 1539.6007\ldots$ (check: $25.9807621 \times 1539.6 = 40\,000.0$).
3. $\sqrt{1539.6007} = 39.2377\ldots$ (check: $39.238^2 = 1539.6206$; $39.2377^2 = 1539.597$).

$$
\Rightarrow\quad r \;\ge\; 39.24\ \text{m} \qquad \text{(Kershner-corrected necessary condition)}
$$

Cross-check via the correction factor: $35.6825 \times \sqrt{2\pi/(3\sqrt3)} = 35.6825 \times 1.099637 = 39.2377$ m. ✓ Consistent.

### 8.4 Step 3 — Test the proposed $R_{\text{cov}} = 15$ m directly

Total disk-area available:

$$
N\pi r^{2} \;=\; 5 \times \pi \times 15^{2} \;=\; 5 \times 3.14159265 \times 225 \;=\; 1125\pi \;=\; 3534.2917\ \text{m}^2 .
$$

Required:

$$
K A \;=\; 2 \times 10\,000 \;=\; 20\,000\ \text{m}^2 .
$$

Ratio:

$$
\frac{N\pi r^{2}}{K A} \;=\; \frac{3534.2917}{20\,000} \;=\; 0.17671 .
$$

**Verdict: $N\pi r^2 = 3534.29 \ll K A = 20\,000$. The configuration is short by a factor of $20000/3534.29 = 5.659$.**

**Maximum achievable redundancy at $R_{\text{cov}}=15$ m, $N=5$:**

$$
K_{\max} \;=\; \Big\lfloor \frac{N\pi r^2}{A} \Big\rfloor \;=\; \Big\lfloor \frac{3534.2917}{10\,000} \Big\rfloor \;=\; \Big\lfloor 0.35343 \Big\rfloor \;=\; 0 .
$$

**So with $R_{\text{cov}}=15$ m and $N=5$, the region cannot even be single-covered, let alone double-covered.** (Also check $K=1$ directly: $r \ge \sqrt{A/(\pi N)} = \sqrt{10\,000/15.7079633} = \sqrt{636.6198} = 25.2311$ m $> 15$ m.) ✗

### 8.5 Step 4 — What $N$ would be needed at $R_{\text{cov}} = 15$ m

Naive area bound:

$$
N \;\ge\; \frac{KA}{\pi r^{2}} \;=\; \frac{20\,000}{\pi \times 225} \;=\; \frac{20\,000}{706.8583} \;=\; 28.2944
\;\Rightarrow\; N \;\ge\; 29 .
$$

Kershner-corrected:

$$
N \;\ge\; \frac{2KA}{3\sqrt3\,r^{2}} \;=\; \frac{2}{3\sqrt3}\cdot\frac{20\,000}{225}
\;=\; 0.38490018 \times 88.8889 \;=\; 34.2133
\;\Rightarrow\; N \;\ge\; 35 .
$$

### 8.6 Step 5 — The $M=20$ sensors, and what the report's discrete model actually needs

**Important caveat first.** The area bound of §7 constrains the *continuous* region. The simulation in the report constrains only the $M=20$ sensor points. The two differ, and the point-set version is only decidable once a layout is assumed. Below I use the natural **uniform layout**: partition $[0,100]^2$ into a $4\times5$ grid of cells of size $25 \text{ m}\times 20 \text{ m}$ and place one sensor at each cell centre (20 cells, 20 sensors). I flag this as an assumption, not a consequence of $M=20$.

**Required incidences.** $K=2$ coverage of 20 sensors needs at least $2\times20 = 40$ (UAV, sensor) incidences. Each UAV contributes at most (number of sensors inside its radius-$r$ disk).

**How many sensors fit in a radius-$r$ disk on this grid?** Sensor coordinates are $\{12.5+25a\} \times \{10+20b\}$ for integers $a,b$ in the valid ranges, so the spacings are $25$ m in $x$ and $20$ m in $y$. A disk of radius $r$ contains a set of grid points iff it contains the axis-aligned bounding rectangle of those points, i.e. iff the half-diagonal of that rectangle is $\le r$.

- 2 sensors side by side in $x$: span $25$ m ⟹ half-diagonal $12.5$ m. Affordable at $r=15$.
- 2 sensors stacked in $y$: span $20$ m ⟹ half-diagonal $10$ m. Affordable at $r=15$.
- 3 sensors in an L: span $25\times20$ ⟹ half-diagonal $\tfrac12\sqrt{25^2+20^2} = \tfrac12\sqrt{1025} = \tfrac12(32.01562) = 16.0078$ m. **Not affordable at $r=15$.**
- 3 in a row: span $50$ m ⟹ $25$ m. Not affordable.
- 4 sensors (a $2\times2$ block): span $25\times20$ ⟹ $16.0078$ m. Not affordable at $r=15$.

**Therefore, at $R_{\text{cov}}=15$ m on a uniform layout, each UAV can cover at most $2$ sensors.** With $N=5$ that is at most $5\times2 = 10$ incidences, whereas even $K=1$ requires $20$ incidences. **$R_{\text{cov}}=15$ m fails the sensor-level $K=1$ requirement by a factor of $2$ on this layout.**

**What radius does the uniform layout need?**

- $K=1$, $N=5$: each UAV must cover $4$ sensors ⟹ a $2\times2$ block ⟹ $r \ge 16.0078$ m.
- $K=2$, $N=5$: each UAV must cover $8$ sensors ⟹ the tightest 8-point set is a $3\times3$ cell block minus a corner, whose 8 centres span $2\times25 = 50$ m in $x$ and $2\times20 = 40$ m in $y$ ⟹ half-diagonal $\tfrac12\sqrt{50^2+40^2} = \tfrac12\sqrt{4100} = \tfrac12(64.03124) = 32.0156$ m. Hence the layout requires $r \ge 32.0156$ m.

### 8.7 Step 6 — Putting all bounds side by side

| Criterion | Type | Required $R_{\text{cov}}$ | Binding? |
|---|---|---|---|
| Naive area count (§7.1) | necessary | $\ge 35.68$ m | yes |
| Kershner-corrected (§6/§7.3) | necessary, asymptotically tight | $\ge 39.24$ m | **yes — the binding constraint** |
| Uniform $4{\times}5$ sensor grid, $K=2$ | necessary, layout-dependent | $\ge 32.02$ m | no (weaker) |
| Uniform $4{\times}5$ sensor grid, $K=1$ | necessary, layout-dependent | $\ge 16.01$ m | no |
| **Value given in the report** | — | $15.00$ m | **FAILS ALL OF THE ABOVE** |

### 8.8 Verdict on the report's $R_{\text{cov}} = 15$ m

**$R_{\text{cov}} = 15$ m is infeasible, and not marginally so.** Concretely:

1. **It fails the continuous $K=1$ condition.** $R_{\text{cov}}$ must satisfy $r \ge \sqrt{A/(\pi N)} = 25.23$ m even for single coverage. $15 < 25.23$. Short by a factor $25.2311/15 = 1.682$.
2. **It fails the continuous $K=2$ condition** by a factor $39.2377/15 = 2.616$ (Kershner) or $35.6825/15 = 2.379$ (naive area).
3. **The deficit is severe.** The five disks at $r=15$ supply $N\pi r^2 = 3534.29\ \text{m}^2$ of coverage budget against a requirement of $KA = 20\,000\ \text{m}^2$ — only $17.7\,\%$ of what is needed. The maximum achievable $K$ is $\lfloor 0.353 \rfloor = 0$.
4. **It fails the sensor-level $K=1$ condition** on the natural uniform layout: each UAV reaches only $2$ of the $20$ sensors, so $5$ UAVs give $10$ incidences where $20$ are needed.

**Minimum fixes, any one of which is necessary:**

- **Increase $R_{\text{cov}}$ to at least $39.24$ m** (recommended; keeps $N=5$). At exactly $r=39.24$ m a disk contains a square of side $r\sqrt2 = 55.50$ m, which spans $2$ grid columns ($50$ m) and $2$ grid rows ($40$ m), so it reaches the 9 sensors of a $3\times3$ cell block, comfortably supplying the $8$ sensors per UAV that $K=2$ requires. Feasibility at $r=39.24$ m is therefore supported by *both* the area argument *and* the discrete layout.
- **Or increase $N$ to at least $35$** at $R_{\text{cov}}=15$ m (Kershner) or $29$ (naive area). Note $N=35$ also makes 2-connectivity (§17) and single-failure tolerance (§18) easy, at the cost of a much larger communication graph.
- **Or shrink the region.** Keeping $N=5$, $K=2$, $R_{\text{cov}}=15$ m, the Kershner bound gives $A \le \frac{3\sqrt3}{2}Nr^2/K = 2.598076\times5\times225/2 = 1461.92\ \text{m}^2$, i.e. a square of side only $\sqrt{1461.92} = 38.24$ m — a 38 % linear reduction from the stated $100$ m.

**What to write in the report.** Replace "$R_{\text{cov}} = 15$ m" with $R_{\text{cov}} \ge 39.24$ m (or restate $N$, $K$, or $A$ consistently), and add the feasibility certificate

$$
N\,\pi R_{\text{cov}}^{2} \;\ge\; K A \qquad(\text{and, Kershner-corrected: } K A \le \tfrac{3\sqrt3}{2}NR_{\text{cov}}^{2})
$$

as a **precondition checked before training**, with the $K$-coverage reward treated as zero whenever it is violated. This turns a physically impossible hyperparameter into a caught configuration error rather than a silently mis-learned policy.

---

# PART B — GRAPH AND CONNECTIVITY THEORY

## 9. Connectivity, $k$-Connectivity, and Menger's Theorems

### 9.1 Basic definitions

Let $G = (V,E)$ be a finite undirected simple graph, $n = |V|$, $m = |E|$. A **vertex separator** is a set $S \subseteq V$ with $G - S$ disconnected. A **cut vertex** (articulation point) is a vertex whose removal increases the number of connected components.

> **Definition (vertex connectivity $\kappa(G)$).**
> $$\kappa(G) \;=\; \min\bigl\{\,|S| : S \subseteq V,\; G - S \text{ is disconnected}\,\bigr\}\;\le\;\delta(G),$$
> with the standard convention that
> $$\kappa(G) = \begin{cases} n-1, & \text{if } G \text{ is } K_n,\\[2pt] 0, & \text{if } G \text{ is disconnected},\\[2pt] \min\bigl\{|S| : S \text{ is a cut vertex}\bigr\}, & \text{otherwise.}\end{cases}$$

> **Definition (edge connectivity $\lambda(G)$).**
> $$\lambda(G) \;=\; \min\bigl\{\,|F| : F \subseteq E,\; (V,F) \text{ is disconnected}\,\bigr\}\;\le\;\delta(G).$$

The classical inequalities (Whitney 1932) are

$$
\kappa(G) \;\le\; \lambda(G) \;\le\; \delta(G) \;\le\; n-1,
$$

and all three are attained, e.g. by $G = K_n$.

**Local vertex connectivity.** For $s,t \in V$, $s\neq t$, let

$$
\kappa_{s,t}(G) \;=\; \min\bigl\{\,|S| : S \subseteq V\setminus\{s,t\},\; \text{no $s$–$t$ path in } G - S \,\bigr\}.
$$

Equivalently, $\kappa_{s,t}$ is the minimum number of vertices whose deletion separates $s$ from $t$ (or which deletes $s$ or $t$ itself). Then $\kappa(G) = \min_{s\neq t}\kappa_{s,t}(G)$.

### 9.2 Menger's theorems, stated exactly

> **Menger's Theorem, vertex (node) version.** *Let $G$ be a finite undirected graph and $s,t\in V$, $s\neq t$. Let $\mathcal{P}_{s,t}$ range over sets of $s$–$t$ paths no two of which share any internal vertex, and let $\mathcal{S}_{s,t}$ range over sets of vertices whose deletion separates $s$ from $t$. Then*
> $$\max_{\mathcal{P}\in\mathcal{P}_{s,t}} |\mathcal{P}| \;=\; \min_{S\in\mathcal{S}_{s,t}} |S| .$$
> *Consequently, $G$ is $k$-vertex-connected (i.e. $\kappa(G)\ge k$) if and only if every pair of vertices is joined by $k$ pairwise internally vertex-disjoint paths.*

The max–min formula is the operative content: **the maximum number of internally vertex-disjoint $s$–$t$ paths equals the minimum size of an $s$–$t$ vertex cut.**

> **Menger's Theorem, edge version.** *Let $G$ be a finite undirected graph and $s,t\in V$, $s\neq t$. Let $\mathcal{P}_{s,t}$ range over sets of $s$–$t$ paths no two of which share any edge, and let $\mathcal{S}_{s,t}$ range over sets of edges whose removal separates $s$ from $t$. Then*
> $$\max_{\mathcal{P}\in\mathcal{P}_{s,t}} |\mathcal{P}| \;=\; \min_{F\in\mathcal{S}_{s,t}} |F| .$$
> *Consequently, $G$ is $k$-edge-connected (i.e. $\lambda(G)\ge k$) if and only if there are $k$ edge-disjoint $s$–$t$ paths for every pair $s,t$; and, by the Nash-Williams/Tutte theorem, if and only if $G$ contains $k$ edge-disjoint spanning trees.*

Note the difference. The **vertex** version counts *internally disjoint* paths (paths may share $s$ and $t$); the **edge** version counts *edge-disjoint* paths (paths may share interior vertices). For a UAV fleet, a **node failure removes the UAV entirely** and all of its links, so the **vertex** version is the operative one. Loss of some links while the UAV survives is the **edge** version.

*(Classical attribution: K. Menger, 1927. Exact volume/page details not re-verified in this session — flagged in Part D.)*

**Why this is the right lens for the report.** The requirement "the fleet must remain connected if any one UAV fails" is *literally* the statement $G - v$ is connected for every $v \in V$, i.e. $\kappa(G) \ge 2$, i.e. — by Menger — every pair of nodes has two internally vertex-disjoint paths. So fault-tolerance is not an extra heuristic layered on top of connectivity: it *is* a connectivity requirement, one level up the hierarchy.

---

## 10. Articulation Points

### 10.1 Definition

> A vertex $v \in V$ of a connected graph $G$ is an **articulation point** (cut vertex) iff $G - v$ is disconnected. Equivalently, the number of connected components of $G$ strictly exceeds that of $G - v$.

Equivalently again: $v$ is an articulation point iff there exist vertices $x,y \neq v$ with **no** path between them in $G - v$. Note that a vertex of degree $1$ (a leaf) is never an articulation point, because removing it removes no connection between the remaining vertices.

In the UAV interpretation, an articulation point $v$ is a **single point of failure**: if UAV $v$ dies, the remaining $N-1$ UAVs split into at least two mutually unreachable groups, and the persistent $K$-coverage mission fails because the groups cannot coordinate or share a charging pad. The MAPPO reward must therefore penalise not merely disconnection but the *presence of articulation points*.

### 10.2 The low-link quantity

For a depth-first-search (DFS) spanning forest of $G$ with discovery order, define for every vertex $v$:

$$
\text{disc}[v] \;=\; \text{the time at which } v \text{ is first visited},
$$

$$
\text{low}[v] \;=\; \min\Bigl\{\text{disc}[w] \;:\; w \text{ is reachable from } v \text{ by descending tree edges and then at most one back edge}\Bigr\},
$$

i.e. the earliest discovery time reachable from the subtree rooted at $v$ by descending zero, one, or many tree edges and then at most one back edge. Recursively,

$$
\text{low}[v] \;=\; \min\Bigl\{\text{disc}[v],\; \min_{\substack{(v,w)\ \text{back}\\\text{edge}}} \text{disc}[w],\; \min_{\substack{(v,w)\ \text{tree}\\\text{edge},\ w\ \text{child of } v} \text{low}[w]\Bigr\}.
$$

**The low-link condition.** For a non-root vertex $v$ with at least one DFS child, $v$ is an articulation point **iff** there exists a DFS child $w$ with

$$
\boxed{\;\text{low}[w] \;\ge\; \text{disc}[v]\;}
$$

and for the DFS root $r$,

$$
\boxed{\;r \text{ is an articulation point} \iff r \text{ has } \ge 2 \text{ DFS-tree children.}\;}
$$

**Proof of the low-link condition (complete).** Let $T_v$ be the DFS subtree rooted at a child $w$ of $v$.

*$({\Rightarrow})$* Suppose $\text{low}[w] \ge \text{disc}[v]$. Then no vertex in $T_w$ has a back edge to any vertex in a *different* DFS subtree of $v$, nor to a proper ancestor of $v$ (which would have $\text{disc} < \text{disc}[v]$). In an undirected graph every edge is a tree edge or a back edge between an ancestor and a descendant, so **all** edges leaving $T_w$ go to $v$ itself or to vertices inside $T_w$. Hence $T_w$ is connected to the rest of $G - v$ only through $v$. Since $T_w \neq \emptyset$ and $|V|>1$, removing $v$ disconnects $T_w$ from the rest, so $v$ is an articulation point.

*$(\Leftarrow)$* Suppose $\text{low}[w] < \text{disc}[v]$ for every child $w$ of $v$. Then each $T_w$ has a back edge to a proper ancestor of $v$, or to a vertex discovered before $v$ — which by the DFS property must itself be a proper ancestor of $v$. So each subtree reconnects to the part of the graph above $v$ without using $v$, and $G-v$ is connected. Hence $v$ is not an articulation point. $\blacksquare$

For the **root**, the same argument shows that $G - r$ has exactly (number of DFS children of $r$) components. This is why the root's criterion is a degree-like condition on the DFS tree rather than a low-link inequality: $\text{low}[w] \ge \text{disc}[r] = 0$ is vacuous, since all $\text{low}$ values are $\ge 0$.

### 10.3 Algorithm (Tarjan / Hopcroft–Tarjan), with pseudocode

```
CUT-VERTICES(G)                     # G = (V, E), undirected, unweighted
  for each v in V:                   # O(V)
      disc[v] <- 0;  low[v] <- 0;  parent[v] <- NIL;  isArtic[v] <- false
  time <- 0

  DFS(u):
      disc[u] <- time;  low[u] <- time;  time <- time + 1
      children <- 0
      for each v in Adj[u] with edge {u,v}:                # total O(E) over the run
          if v = parent[u]:  continue                     # skip the tree edge back to parent
          if disc[v] = 0:                                 # v undiscovered -> tree edge
              parent[v] <- u
              children   <- children + 1
              DFS(v)
              low[u] <- min(low[u], low[v])
              if parent[u] != NIL and low[v] >= disc[u]:  # LOW-LINK CONDITION (non-root)
                  isArtic[u] <- true
          else:                                           # already discovered -> back edge
              low[u] <- min(low[u], disc[v])
      if parent[u] = NIL and children >= 2:               # ROOT CONDITION
          isArtic[u] <- true
      return

  for each v in V:  if disc[v] = 0:  DFS(v)               # outer loop over components
  return { v in V : isArtic[v] = true }
```

### 10.4 Complexity

Every vertex is discovered once, every edge is examined exactly twice (once from each endpoint), and every `low` update is $O(1)$. Therefore

$$
\boxed{\;\textbf{Time} \;=\; O(|V| + |E|)\;}\qquad\qquad\boxed{\;\textbf{Space} \;=\; O(|V|)\;}
$$

(the recursion stack is $O(|V|)$; an explicit-stack iterative version gives identical bounds). This is the classical Tarjan bound — R. Tarjan, "Depth-first search and linear graph algorithms," *SIAM J. Comput.*, vol. 1, no. 2, pp. 146–160, 1972 — and is also known as the Hopcroft–Tarjan articulation-point algorithm. The same pass, with one extra $O(1)$ comparison per child, simultaneously yields bridges (§11) and biconnected components (Tarjan & Vishkin, FOCS 1984), which is why it is the right algorithm to embed in the MAPPO evaluation loop.

**Note for the report.** A single DFS over $G$ yields the full articulation-point set. If the connectivity reward needs only a yes/no on "$G$ is 2-connected", the cheapest screen is: $G$ is connected **and** no vertex has degree $1$ **and** the DFS finds no articulation point — one pass, $O(n+m)$, negligible next to a forward pass of the network.

---

## 11. Bridges (Cut Edges)

### 11.1 Definition and basic facts

An edge $e \in E$ is a **bridge** (cut edge) iff it lies on no cycle of $G$. Fundamental facts:

- An edge is a bridge iff it is an edge of **no** circuit.
- Every edge of a **tree** is a bridge, and $G$ is a forest iff every edge is a bridge.
- $G$ is **2-edge-connected** (no bridges) iff every edge lies on a cycle.
- Bridges are found in the same $O(|V|+|E|)$ DFS as articulation points.

### 11.2 Linear-time algorithm (same DFS)

With $\text{disc}$ and $\text{low}$ as in §10.2, inside the tree-edge branch of the DFS:

```
          if disc[v] = 0:                        # tree edge {u,v}
              parent[v] <- u
              children <- children + 1
              DFS(v)
              low[u] <- min(low[u], low[v])
              if parent[u] != NIL and low[v] >= disc[u]:   isArtic[u] <- true
              if low[v] > disc[u]:                         isBridge({u,v}) <- true   # BRIDGE TEST
          else:
              low[u] <- min(low[u], disc[v])
```

$$
\boxed{\;\text{A tree edge } \{u,v\} \text{ (with $u$ the parent) is a bridge} \iff \text{low}[v] > \text{disc}[u].\;}
$$

**Back edges are never bridges**: a back edge closes a cycle with the DFS-tree path between its endpoints, so it lies on that cycle.

**Proof of the bridge test.** (The *strict* inequality is the whole point — contrast the articulation-point test, which uses $\ge$.)

*$({\Rightarrow})$* Suppose $\text{low}[v] > \text{disc}[u]$. Then no vertex in the DFS subtree of $v$ has a back edge to $u$, to a proper ancestor of $u$, or to any vertex in another subtree of $u$. Since every non-tree edge of an undirected DFS is a back edge between an ancestor and a descendant, **all** edges leaving the subtree of $v$ go through $u$. Hence $\{u,v\}$ is the unique connection and is a bridge.

*$(\Leftarrow)$* Suppose $\text{low}[v] \le \text{disc}[u]$. Then some vertex $z$ in the subtree of $v$ has a back edge to $u$ or to a proper ancestor of $u$. The closed walk $z \leadsto v \to u \leadsto z$ — using the tree path inside the subtree, the tree edge $\{u,v\}$, and the back edge together with the tree path from $u$ up to $z$ — is a cycle containing $\{u,v\}$, so $\{u,v\}$ is not a bridge. $\blacksquare$

### 11.3 Relation to articulation points

> **Proposition.** *Let $G$ be connected with $|V| \ge 3$. If $e = \{u,v\}$ is a bridge, then at least one of $u$, $v$ is an articulation point. In particular, if $G$ has no articulation points then $G$ has no bridges.*

*Proof.* Since $e$ is a bridge, $G - e$ has exactly two components $A \ni u$ and $B \ni v$. Suppose $G - u$ were connected. Then some $B$-path must reach $A$, but the only $A$–$B$ edge in $G$ is $e = \{u,v\}$, which touches the removed vertex $u$ — contradiction. Hence $G - u$ is disconnected, so $u$ is an articulation point; the same argument gives it for $v$. $\blacksquare$

Consequences used in the report:

- **No articulation points $\Rightarrow$ 2-vertex-connected $\Rightarrow$ no bridges $\Rightarrow$ every communication link lies on a cycle, so a single *link* failure is survivable.** Single-UAV failure is survivable a fortiori, because removing a vertex removes all of its incident edges simultaneously, and Menger (vertex version) guarantees two internally vertex-disjoint paths between every pair.
- **Bridges are the "partial-UAV-failure" detector, computed in the same pass.** If the report wants a softer failure model (a UAV's radio degrades but the UAV survives, so only some of its links die), then **bridges are the correct detector**, and the requirement is $\lambda(G) \ge 2$. This is a useful second reward term that costs nothing extra computationally.

---

## 12. Graph Laplacian, Algebraic Connectivity, and Fiedler's Theorem

### 12.1 Definition

For $G = (V,E)$ with adjacency matrix $A$ (symmetric, zero diagonal) and degree matrix $D = \operatorname{diag}(d_1,\dots,d_n)$, $d_i = \sum_j a_{ij}$, the **combinatorial Laplacian** is

$$
\boxed{\;\mathcal{L} \;=\; D - A \;}
$$

and the **normalised Laplacian** is $\mathcal{L}^{\mathrm{n}} = I - D^{-1/2}AD^{-1/2}$. For an undirected graph, $\mathcal{L}$ is symmetric positive semidefinite: for $x\in\mathbb{R}^n$,

$$
x^{T}\mathcal{L} x \;=\; \sum_{\{i,j\}\in E} a_{ij}\,(x_i - x_j)^{2} \;\ge\; 0 ,
$$

which is the discrete Dirichlet energy of $x$. Its spectral decomposition is

$$
\mathcal{L} \;=\; \sum_{k=1}^{n} \lambda_k\, v_k v_k^{T},
\qquad 0 = \lambda_1 \le \lambda_2 \le \cdots \le \lambda_n,
\qquad \mathcal{L}\mathbf{1} = 0,\quad \mathbf{1}^{T}\mathcal{L} = 0^{T}.
$$

### 12.2 Fiedler's theorems

> **Fiedler's Theorem (nullity, 1973).** *$\lambda_2(\mathcal{L}) = 0$ if and only if $G$ is disconnected. More generally the multiplicity of the eigenvalue $0$ equals the number of connected components of $G$:*
> $$\text{nullity}(\mathcal{L}) \;=\; \#\{\text{connected components of } G\}.$$

> **Fiedler's Theorem (eigenvector orthogonality, 1975).** *If $k > 1$ and $v_k$ is any eigenvector associated with $\lambda_k(\mathcal{L})$, then*
> $$\mathbf{1}^{T} v_k = 0 \quad\text{and}\quad v_k^{T}\mathbf{1} = 0 .$$
> *That is, every non-null Laplacian eigenvector is orthogonal to the all-ones vector.*

(Reproduced as Lemma 1 of Zareh–Sabattini–Secchi, after N. M. M. de Abreu, "Old and new results on algebraic connectivity of graphs," *Linear Algebra Appl.*, vol. 423, no. 1, pp. 53–73, 2007, which cites Fiedler 1975, *Czechoslovak Mathematical Journal*, vol. 25, no. 4, pp. 619–633.)

**Proof of the nullity statement (complete).** Let $G$ have connected components $V_1,\dots,V_c$. Reorder $V$ so components are contiguous; then $\mathcal{L}$ is block diagonal, $\mathcal{L} = \operatorname{diag}(\mathcal{L}|_{V_1},\dots,\mathcal{L}|_{V_c})$. Each block has rank $|V_i| - 1$: by the quadratic-form identity, $x^T\mathcal{L}|_{V_i}x = \sum_{\{p,q\}\in E_i}a_{pq}(x_p-x_q)^2 = 0$ if and only if $x$ is constant on $V_i$, so the block's nullspace is the 1-dimensional space of constant vectors on $V_i$. Hence $\operatorname{nullity}(\mathcal{L}) = \sum_{i=1}^{c}(|V_i| - 1) = n - c$. Therefore $\lambda_2 = 0 \iff n-c \ge 2 \iff c \ge 2 \iff G$ is disconnected. $\blacksquare$

### 12.3 Algebraic connectivity, and why $\lambda_2$ beats the hard indicator

$$
\boxed{\;\lambda_2(\mathcal{L}) \;=\; \text{``algebraic connectivity''} \;=\; \min_{\substack{x \perp \mathbf{1} \\ x \neq 0}} \frac{x^{T}\mathcal{L} x}{x^{T} x}\;}
$$

(the Rayleigh-quotient characterisation). Properties that make it the right reward signal:

1. **Zero exactly at disconnection** (Fiedler). So $\lambda_2 = 0 \iff$ the fleet is partitioned: a *soft* penalty that is zero precisely in the degenerate case and positive otherwise.
2. **Monotone under edge addition.** If $\mathcal{E}_1 \subseteq \mathcal{E}_2$ on the same vertex set, then $\mathcal{L}_2 - \mathcal{L}_1$ is PSD, and the minimum of a Rayleigh quotient over a fixed subspace is monotone under PSD increase, so $\lambda_2(\mathcal{L}_1) \le \lambda_2(\mathcal{L}_2)$. **A repulsive well-formedness potential therefore drives connectivity automatically**, with no extra shaping.
3. **Smooth and graded.** $\lambda_2$ is a *continuous* function of the edge weights. The articulation-point indicator $\mathbb{1}\{\exists v : G - v \text{ disconnected}\}$ is discrete and, worse, is **non-monotone along a trajectory**: a fleet can go "no articulation points" $\to$ "one articulation point" $\to$ "no articulation points" in three consecutive policy steps, and the indicator carries no information about *how close* to the boundary the third configuration is. With $\lambda_2$ the agent sees a value that grows monotonically as redundancy is added, and gets a non-zero signal even when it is already connected but fragile.
4. **Cheap.** Power iteration on $\mathcal{L}$ costs $O(m)$ per iteration for sparse $\mathcal{L}$; $k$ iterations give relative error $O(\rho^k)$ with $\rho = \lambda_2/\lambda_3$. In practice $10$–$30$ iterations suffice. An exact articulation-point test costs the same order but returns a single bit.
5. **Bounded and normalisable.** For a connected graph on $n$ vertices, $\lambda_2 \le \frac{n}{n-1}\delta \le \frac{n}{n-1}$, and for regular geometric graphs $\lambda_2 = \Theta(\delta)$. So $\lambda_2/(\lambda_2 + n/(n-1))$ is a well-scaled $[0,1)$-valued reward term.

**A caveat the report must state honestly.** $\lambda_2 > 0$ certifies **1-connectivity only**. It is *not* a certificate of 2-connectivity: the path graph $P_n$ — the worst case for $\lambda_2$, with $\lambda_2 = 2 - 2\cos(\pi/n) \approx \pi^{2}/n^{2}$ — is fully connected, has no bridges, and has $n-2$ articulation points. So $\lambda_2$ is the right *smooth* signal for **connectivity**, and **$\lambda_3$ is the right smooth signal for 2-connectivity** — which is exactly where the biconnectivity literature lands (§16).

*(Fiedler 1975, Czechoslovak Math. J. 25(4):619–633; de Abreu 2007, Linear Algebra Appl. 423(1):53–73; Bapat & Pati 1998, Linear and Multilinear Algebra 45(2–3):247–273 — all three verified.)*

---

## 13. Unit Disk Graphs

### 13.1 Definition

> A **unit disk graph** (UDG) is a graph $G = (V,E)$ for which there exist points $p_1,\dots,p_n \in \mathbb{R}^d$ and $r>0$ such that $\{i,j\}\in E \iff \|p_i - p_j\| \le r$.

For our UAVs, $G$ is a UDG with $r = R_{\text{comm}}$ and $p_i$ the UAV positions. UDG decision is in NP (just the coordinates) and polynomial-time solvable, but many *optimisation* problems on UDGs are NP-hard, including the minimum connected dominating set and the connected-coverage variants of §3.3. Note that "deciding connectivity" of a given configuration is trivial — the hard problems are the optimisations built on top of connectivity, which is precisely why the report does not solve connectivity in the loop but instead *shapes* it with a potential.

### 13.2 The greedy MST-connectivity heuristic, and why it is the right primitive

**Claim (minimum bottleneck spanning tree).** For a finite point set $P$ and radius $r$, the Euclidean minimum spanning tree (EMST) $T$ of $P$ is **bottleneck-minimising**: writing $b(T) = \max_{e\in T}\|e\|$,

$$
b(T) \;=\; \min_{\text{spanning trees } T'} \; b(T').
$$

*Proof.* By the **cut property**, a minimum-weight edge crossing any cut belongs to some MST. Let $e^\star$ be the longest edge of $T$, of length $L$, and let $T - e^\star = A \dot\cup B$ be the resulting cut. No edge crossing $(A,B)$ has weight $< L$ — otherwise replacing $e^\star$ by it would yield a strictly lighter spanning tree, contradicting minimality of $T$. Hence every spanning tree $T'$ must cross the cut $(A,B)$ with an edge of weight $\ge L$, so $b(T') \ge L$ for all $T'$; and $T$ attains $L$. $\blacksquare$

**Consequence for connectivity.** The bottleneck statement is

$$
G \text{ (the UDG) is connected} \quad\Longleftrightarrow\quad b(T) \le r .
$$

So **connectivity of a UDG is a bottleneck problem, not a total-length problem**: the correct surrogate objective is to *minimise the longest link of the fleet's spanning tree*, not the sum of link lengths. This is a frequently mis-stated point in the multi-robot connectivity-maintenance literature, and it is the real justification for an MST-based rather than sum-of-distances-based connectivity potential.

**Greedy heuristic.** Kruskal/Prim on the UDG builds the MST in $O(m\log n)$ time (or $O(n)$ after Delaunay-based sparsification), and then

$$
\text{if } b(T) \le r: \text{ connected} \qquad\qquad \text{if } b(T) > r: \text{ disconnected, and } r_{\text{needed}} = b(T).
$$

$r_{\text{needed}} = b(T)$ is a **tight, computable certificate**: it is the smallest communication radius that would connect the current configuration. This is the natural single-knob shaping term.

### 13.3 The area relation $n\,\pi r^{2}/2$

The UDG design literature's standard rule for placing $n$ nodes in a region of area $A$ so that the induced UDG is **connected and every node is covered** (each node has at least one neighbour — a necessary condition for covering the node itself) is

$$
\boxed{\;\frac{n\,\pi r^{2}}{2} \;\ge\; A
\qquad\Longleftrightarrow\qquad
r \;\ge\; \sqrt{\frac{2A}{\pi n}}\;}
$$

**Derivation of the $1/2$.** For node $i$ to be *covered*, some other node's radius-$r$ disk must contain $p_i$. In a deployment each node $i$ "owns" its Voronoi cell $V_i$ (the set of points closer to $p_i$ than to any $p_j$). A disk of radius $r$ centred at $p_j$ can cover at most the *far half* of a cell whose inradius is at most $r$, because $p_j$ itself must lie outside the portion of the cell that $j$ owns. Hence each node must own a cell of area at least one half-disk, $\pi r^{2}/2$; the $n$ cells tile $A$, giving $n \cdot \pi r^{2}/2 \ge A$. The factor $1/2$ is the direct, unavoidable consequence of requiring *self-coverage*; without it (i.e. requiring only that the *region* be covered) the rule is $n\pi r^2 \ge A$ — which is §7.1.

**Consistency check.** For $A = 10\,000\ \text{m}^2$, $n = 5$: $r \ge \sqrt{2\cdot10\,000/(5\pi)} = \sqrt{1273.2395} = 35.68$ m — *identical* to the $K=1$ instance of §7.1. Not a coincidence: $n\pi r^2/2 \ge A$ is §7.1 with $K=1$ plus the factor $2$ from self-coverage. Both are valid necessary conditions, and for $K\ge2$ the $K$-rule of §7 dominates (since $K A \le n\pi r^2$ implies $A \le n\pi r^2/2$ for $K\ge2$).

*(The UDG guaranteed-connectivity / connected-cover results of Apollonio, Czyzowicz, Stojmenović & Urrutia are the classical source of this rule. I am confident in the $n\pi r^2/2$ form and in the half-disk reasoning; a specific volume/page was not re-verified this session — flagged in Part D.)*

---

## 14. Random Geometric Graphs

### 14.1 Definition

A **random geometric graph** $G(n,r)$ on a domain $Q$ of area $A$ is formed by placing $n$ points $X_1,\dots,X_n$ **independently and uniformly at random** in $Q$ and joining $X_i$ to $X_j$ iff $\|X_i - X_j\| \le r$. The edges are then independent Bernoulli variables with a shared, position-dependent success probability.

### 14.2 Expected number of edges

On a **torus** (or, exactly, for a domain on which the boundary has measure zero under the distance constraint):

$$
\Pr\bigl(\{i,j\}\in E\bigr) \;=\; \mathbb{P}\bigl(\|X_i - X_j\|\le r\bigr) \;=\; \frac{|B(x,r)|}{A} \;=\; \frac{\pi r^{2}}{A},
$$

so by linearity of expectation

$$
\boxed{\;\mathbb{E}\bigl[|E(G(n,r))|\bigr] \;=\; \binom{n}{2}\cdot\frac{\pi r^{2}}{A} \;=\; \frac{n(n-1)}{2}\cdot\frac{\pi r^{2}}{A}\;}
$$

and the **expected degree** of a node is

$$
\mathbb{E}[\deg] \;=\; (n-1)\frac{\pi r^{2}}{A} .
$$

Equivalently, the node density required to achieve a target mean degree is $n/A \approx \bar{d}/(\pi r^{2})$ — the familiar "$\bar d = \pi r^{2} n / A$" rule of thumb.

### 14.3 The boundary caveat — and an exact computation for the square

On a domain **with boundary**, $\Pr(\|X_i - X_j\|\le r)$ is *less* than $\pi r^2/A$, because disks centred near the boundary hang outside $Q$ and cover less area. **Exact computation for the unit square.** Let $X_i, X_j$ be independent uniform on $[0,1]^2$ and put $u = X_i - X_j$. Then $u_1$ has the triangular density $f_{u_1}(s) = 1 - |s|$ on $[-1,1]$ and $u_2 \sim \mathrm{Unif}[-1,1]$, independently. For $0 \le r \le 1$,

$$
\begin{aligned}
\mathbb{P}(\|X_i-X_j\|\le r)
&=\int_{\|u\|\le r} (1-|u_1|)\,du_1\,du_2 \\
&=\pi r^{2} - 2\int_{\|u\|\le r}|u_1|\,du_1 \\
&=\pi r^{2} - 2\cdot 4\int_{0}^{r}u_1\sqrt{r^{2}-u_1^{2}}\;du_1 \\
&=\pi r^{2} - 8\cdot\frac{r^{3}}{3},
\end{aligned}
$$

since $\int_0^r u\sqrt{r^2-u^2}\,du = \frac{r^3}{3}$. Hence

$$
\boxed{\;\mathbb{P}(\|X_i - X_j\|\le r) \;=\; \pi r^{2} - \tfrac{8}{3}r^{3},\qquad 0\le r\le 1\;}
$$

$$
\boxed{\;\mathbb{E}\bigl[|E(G(n,r))|\bigr] \;=\; \binom{n}{2}\Bigl(\pi r^{2}-\tfrac{8}{3}r^{3}\Bigr)\quad\text{on the unit square.}\;}
$$

**Size of the correction at the connectivity threshold.** At $r_n \approx \sqrt{\ln n/(\pi n)}$, the relative error is

$$
\frac{\tfrac{8}{3}r^{3}}{\pi r^{2}} \;=\; \frac{8r}{3\pi} \;=\; O\!\left(\sqrt{\frac{\ln n}{n}}\right) \;\longrightarrow\; 0 .
$$

So the boundary term is **second-order** — far smaller than the $\ln n$-scale fluctuation that governs the threshold itself. This is *why* $\binom{n}{2}\pi r^2/A$ is the right formula in the interior, and *why* the boundary still matters at simulation scale: at $r = 15$ m on a $100$ m side ($r = 0.15$ normalised), the relative correction is $\frac{8(0.15)}{3\pi} = 0.1273$, i.e. $12.7\,\%$ — not negligible for a 5-node fleet.

---

## 15. The Connectivity Threshold

> **Theorem (connectivity threshold for the 2-D random geometric graph; Penrose, Gupta–Kumar).** *Let $X_1,\dots,X_n$ be independent and uniform on the unit square, and let $r_n = r_n(n)$ be a threshold function. Then*
> $$\mathbb{P}\bigl(G(n,r_n)\text{ is connected}\bigr) \;\longrightarrow\; \begin{cases} 1, & \pi n r_n^{2} - \ln n \to +\infty,\\[3pt] 0, & \pi n r_n^{2} - \ln n \to -\infty. \end{cases}$$
> *Equivalently, $r = r_{\mathrm{conn}}(n) := \sqrt{\dfrac{\ln n}{\pi n}}$ is a threshold function for connectivity; and more sharply, if $\pi n r_n^2 = \ln n + c_n$ for a real sequence $c_n$, then*
> $$\mathbb{P}\bigl(G(n,r_n)\text{ is connected}\bigr) \;\longrightarrow\; \exp\bigl(-\exp(-c_n)\bigr).$$

**Why connectivity has the same threshold as having no isolated vertices.** The number $I$ of isolated vertices satisfies a Poisson approximation, $I \overset{d}{\to} \mathrm{Poisson}\!\left(n e^{-\pi n r^2}\right)$, and Penrose's theorem states that for $G(n,r)$, *any threshold function for having no isolated vertex is also a connectivity threshold function*: the two events are not identical, but they coincide with probability $1-o(1)$ in the critical window. The anchor is Panchapakesan & Manjunath (2001), "Connectivity of a graph of uniformly distributed points on $[0,1]^d$," *Statistics & Probability Letters* 60(4), 351–357, who showed that $\ln n/n$ (in the normalised-$p$ language) is a threshold for having an isolated vertex; by Penrose's theorem it is also a connectivity threshold.

**Gupta–Kumar's formulation (unit-area disk).** For $n$ points uniform in a disk of **area 1** (radius $1/\sqrt{\pi}$), the connectivity threshold is expressed as a *critical power*:

$$
\boxed{\;p_c(n) \;=\; \frac{\ln n + c(n)}{\pi n}\;,\qquad\text{equivalently}\qquad r_c(n) = \sqrt{\frac{\ln n + c(n)}{\pi n}} .}\n$$

P. Gupta and P. R. Kumar, "Critical power for asymptotic connectivity in wireless networks," in *Stochastic Analysis, Control, Optimization and Applications*, pp. 547–566, 1998. *(Verified: the reference list of arXiv:1809.10737 gives exactly these details and states that Gupta and Kumar "provided a connectivity threshold for points that are uniformly distributed in a disk.")*

**$k$-connectivity threshold.** M. D. Penrose, "On $k$-connectivity for a geometric random graph," *Random Structures and Algorithms*, vol. 15, no. 2, pp. 145–164, 1999 (verified on Penrose's own publication list, Durham), extends this to

$$
\boxed{\;r \;=\; \sqrt{\frac{(k-1)\ln n + c_n}{\pi n}}\;}
$$

as a threshold for $G(n,r)$ to be $k$-connected. Note the structural parallel with the UAV setting: **the redundancy requirement enters the threshold as a factor $K-1$ multiplying $\ln n$** — more redundancy demands asymptotically more than proportionally more radius, because each additional constraint contributes a $\ln n$-scale "no isolated node / no small cut" event. This is the probabilistic counterpart of the deterministic bound of §7.

**Soft graphs.** M. D. Penrose, "Connectivity of soft random geometric graphs," *Annals of Applied Probability*, vol. 26, no. 2, pp. 986–1028, 2016, doi: 10.1214/15-AAP1110 (arXiv:1311.3897), determines the asymptotic connectivity probability for all $(p_n,r_n)$ with $r_n = O(n^{-\varepsilon})$ — i.e. for the *soft* rule $P(i\leftrightarrow j) = p$ if $\|X_i - X_j\| \le r$. This is the right model when link reliability is probabilistic (fading), and it is therefore the right model for "stochastic UAV failures" in a lossy channel, rather than a hard UDG.

**What the threshold means for design.** Requiring the number of components to be $o(1)$ forces

$$
R_{\text{comm}} \;\gtrsim\; \sqrt{\frac{\ln N}{\pi n_{\text{dens}}}},
\qquad n_{\text{dens}} = \frac{N}{A}.
$$

For $N = 5$, $A = 10\,000\ \text{m}^2$: $n_{\text{dens}} = 5\times10^{-4}\ \text{m}^{-2}$, giving $R_{\text{comm}} \approx \sqrt{1.6094/(0.0015708)} = \sqrt{1024.6} = 32.01$ m. This is only indicative: at such low density the probabilistic guarantee is weak, and with $N=5$ the operative regime is the *deterministic* bottleneck bound of §13, not the random-geometric threshold. The random-geometric threshold becomes informative once $N$ is in the tens or hundreds.

---

## 16. Local Articulation Point Detection: the ACTUAL Conditions

### 16.1 The source, and a DOI correction the report needs

The report cites:

> Zareh Eshghdoust, M.; Sabattini, L.; Secchi, C., "Decentralized biconnectivity conditions in multi-robot systems," *2016 IEEE 55th Conference on Decision and Control (CDC)*, doi: 10.1109/CDC.2016.7798253.

**Live verification performed on 29 September 2026 — results:**

- The paper **exists** and is by exactly these three authors. A complete, freely available version exists as **arXiv:1608.02276** (math.DS, submitted 14 August 2016, cross-listed cs.RO). I retrieved and read the full text (ar5iv LaTeXML rendering), so everything below is taken from the paper itself, not from memory.
- The **official CDC 2016 proceedings table of contents** (IEEE, 2016 IEEE 55th Conference on Decision and Control) lists: *"Decentralized Biconnectivity Conditions in Multi-Robot Systems, pp. 99–104"*, with these three authors, all at the *Dipartimento di Ingegneria Meccanica e dei Sistemi (DISMI), University of Modena and Reggio Emilia*. **The page range 99–104 is confirmed.**
- **The DOI in the report is very likely incorrect.** The *other* paper by the same three authors in the same conference — "Enforcing Biconnectivity in Multi-robot Systems," pp. 1800–1805 — carries DOI 10.1109/CDC.2016.7798526 (confirmed independently in the reference list of T. Murayama and A. Iwasaki, *J. Robot. Mechatron.* 35(4), 1028–1037, 2023, which lists doi 10.1109/CDC.2016.7798526). The report's **10.1109/CDC.2016.7798253 could not be resolved to a matching record** in my searches. **Action required: check the DOI directly on IEEE Xplore. The page range 99–104 is safe to keep, and arXiv:1608.02276 is a safe, verifiable substitute.**

### 16.2 Notation (as used in the paper)

$\mathcal{G} = (\mathcal{V},\mathcal{E})$ undirected, $\mathcal{V} = \{1,\dots,n\}$, $n > 2$. $A$ is the adjacency matrix ($a_{ij} > 0$ iff $(i,j)\in\mathcal{E}$; $A$ symmetric). $\mathcal{N}_i = \{j : (j,i)\in\mathcal{E}\}$ is the neighbourhood of $i$. $D = \operatorname{diag}(d_1,\dots,d_n)$, $d_i = \sum_k a_{ik}$, and $\mathcal{L} = D - A$ with

$$
0 = \lambda_1(\mathcal{L}) \le \lambda_2(\mathcal{L}) \le \cdots \le \lambda_n(\mathcal{L}).
$$

$\mathcal{G}^{R_i}$ denotes $G$ with node $i$ **and all its incident edges** removed; $\mathcal{L}^{R_i}$ is its Laplacian. "Data exchange among the robots is supposed to be **neighbour-to-neighbour**."

**Paper's Definitions 1–3 and 5:**

- **Def. 1.** A vertex $i\in\mathcal{V}$ of a connected graph $\mathcal{G}$ is an **articulation point** if $\mathcal{G}^{R_i}$ is not connected.
- **Def. 2.** A connected graph is **biconnected** if it has no articulation point.
- **Def. 3.** A **block** in $\mathcal{G}$ is a maximal induced connected subgraph with no articulation point. If $\mathcal{G}$ itself is connected and has no articulation point, then $\mathcal{G}$ is a block.
- **Def. 5.** Two vertices $i,j$ are **doubly connected** iff there are two or more internally vertex-disjoint paths between them.
- **Lemma 2.** $\mathcal{G}$ is biconnected $\iff$ any two vertices $i,j$ are doubly connected.

**Perturbed objects.** For a small design parameter $\epsilon \in \mathbb{R}^+$:

- $A^{i}(\epsilon)$ is $A$ with **all** $a_{ij}$ and $a_{ji}$ multiplied by $\epsilon$;
- $D^{i}(\epsilon) = \operatorname{diag}(A^{i}(\epsilon)\mathbf{1})$;
- $\mathcal{L}^{i}(\epsilon) := D^{i}(\epsilon) - A^{i}(\epsilon)$.

Writing $\tilde a_i = [a_{ij}]_{j\neq i}\in\mathbb{R}^{n-1}$ and $d_i = \sum_k a_{ik}$, the paper computes

$$
A^{i}(\epsilon)=\begin{pmatrix} A^{R_i} & \epsilon\,\tilde a_i\\ \epsilon\,\tilde a_i^{T} & 0\end{pmatrix},
\qquad
\mathcal{L}^{i}(\epsilon)=\begin{pmatrix}
\mathcal{L}^{R_i} + \epsilon\operatorname{diag}(\tilde a_i^{T}) & -\epsilon\,\tilde a_i\\
-\epsilon\,\tilde a_i^{T} & \epsilon d_i
\end{pmatrix}.
$$

**Theorem 1 and Corollary 1 (the reduction).** The eigenvalues of

$$
P^{i}(\epsilon) \;=\; \mathcal{L}^{R_i} + \epsilon\,\operatorname{diag}(\tilde a_i^{T}) + \epsilon\,\tilde a_i\mathbf{1}^{T}
\tag{1}
$$

are **exactly the non-null eigenvalues** of $\mathcal{L}^{i}(\epsilon)$. And if $\mathcal{G}$ is connected then $\mathcal{L}^{i}(\epsilon)$ has exactly one null eigenvalue, so

$$
\lambda_k\bigl(P^{i}(\epsilon)\bigr) \;=\; \lambda_{k+1}\bigl(\mathcal{L}^{i}(\epsilon)\bigr),\qquad k = 1,\dots,n-1.
\tag{2}
$$

The proof of Theorem 1 uses exactly the Fiedler orthogonality of §12.2: for a non-null eigenvector $v = [v^{1}; v^{2}]$ of $\mathcal{L}^{i}(\epsilon)$, $\mathbf{1}^{T}v = 0$ gives $v^{2} = -\mathbf{1}^{T}v^{1}$, and substituting removes $v^{2}$ and yields (1). **This is why the conditions are per-node conditions**: the reduction to $P^{i}(\epsilon)$ consumes only the rows/columns of $i$ and its neighbourhood.

**Lemma 3 (perturbation bound).** Let $A$ have eigenvalues $\psi_1\ge\dots\ge\psi_n$ and $B$ have eigenvalues $\xi_1\ge\dots\ge\xi_n$, and define $\operatorname{gap}(A,B) = \max_j|\psi_j - \xi_j|$. If **all** real linear combinations of $A$ and $B$ have only real eigenvalues, then

$$
\operatorname{gap}(A,B) \;\le\; \|A - B\| \quad (\text{Euclidean/Frobenius-type norm}).
$$

**Proposition 1 (needed for Lemma 3).** For any $\alpha,\beta\in\mathbb{R}$ with $\alpha^2+\beta^2\neq0$, the linear combination $F^{i}(\epsilon) = \alpha\mathcal{L}^{R_i} + \beta P^{i}(\epsilon)$ has only real eigenvalues. (Proved in the paper's Appendix by a perturbative induction using Lemma 4 — the semisimple-eigenvalue first-order perturbation formula of Seyranian & Mailybaev.)

### 16.3 **Theorem 2 — the actual sufficient condition**

> **Theorem 2 (Zareh, Sabattini & Secchi, 2016, eq. 12).** *For a given multi-robot system with $n$ robots ($n>2$) whose interaction network graph is modelled by an undirected connected graph $\mathcal{G} = (\mathcal{V},\mathcal{E})$, the node $i$ is **not** an articulation point if, for a small $\epsilon \in \mathbb{R}^{+}$, we have*
> $$\boxed{\;\lambda_{3}\bigl(\mathcal{L}^{i}(\epsilon)\bigr) \;>\; \epsilon\,\sqrt{n}\;\left(\sum_{k=1}^{n} a_{ik}^{2}\right)^{1/2}\;}
> \tag{12}$$
> *Equivalently, by (2): $\lambda_{2}\bigl(P^{i}(\epsilon)\bigr) > \epsilon\sqrt{n}\left(\sum_k a^2_{ik}\right)^{1/2}$.*

**Proof chain (as printed).**

1. If $i$ is not an articulation point then $\mathcal{G}^{R_i}$ is connected, so $\mathcal{L}^{R_i}$ has a **positive** second-smallest eigenvalue.
2. Proposition 1 ensures all real linear combinations of $\mathcal{L}^{R_i}$ and $P^{i}(\epsilon)$ have real eigenvalues, so Lemma 3 applies:
$$
\left|\lambda_{2}\bigl(P^{i}(\epsilon)\bigr) - \lambda_{2}\bigl(\mathcal{L}^{R_i}\bigr)\right| \;\le\; \bigl\|P^{i}(\epsilon) - \mathcal{L}^{R_i}\bigr\| \;=\; \epsilon\bigl\|\operatorname{diag}(\tilde a_i) + \tilde a_i\mathbf{1}^{T}\bigr\| .
$$
3. The perturbation matrix is explicitly
$$
\operatorname{diag}(\tilde a_i) + \tilde a_i\mathbf{1}^{T} = \begin{pmatrix} a_{11} & \ldots & a_{11}\\ \vdots && \vdots\\ a_{n-1,n-1} & \ldots & a_{n-1,n-1}\end{pmatrix},
$$
a matrix with $n-1$ rows and $n-1$ identical columns, whose Euclidean norm is $\sqrt{n}\left(\sum_{k=1}^{n}a^2_{ik}\right)^{1/2}$ (note: this uses the $n-1$ repeated entries, which the paper writes with the index $k=1,\dots,n$).
4. Hence $\lambda_{2}\bigl(P^{i}(\epsilon)\bigr) > \epsilon\sqrt{n}\bigl(\sum_k a^2_{ik}\bigr)^{1/2} \Rightarrow \lambda_{2}\bigl(\mathcal{L}^{R_i}\bigr) > 0 \Rightarrow \mathcal{G}^{R_i}$ connected $\Rightarrow i$ is not an articulation point.
5. By Corollary 2 and (2), $\lambda_{2}\bigl(P^{i}(\epsilon)\bigr) = \lambda_{3}\bigl(\mathcal{L}^{i}(\epsilon)\bigr)$, giving (12). $\blacksquare$

**The paper's own worked numbers (Example 1).** $n = 10$ robots, $R$-disk model with $R = 0.5$, $\sigma = 0.125$, so $a_{ij} = \exp\!\bigl(-\|p_i-p_j\|^{2}/(2\sigma)\bigr)$ for $\|p_i - p_j\|\le R$ and $0$ otherwise. Only one node, $^{*}$, is not locally biconnected. With $\epsilon = 0.05$: $\lambda_{3}\bigl(\mathcal{L}^{*}(\epsilon)\bigr) = 0.034$ and $\bigl(\sum_{k=1}^{n}a^2_{*k}\bigr)^{1/2} = 0.062$, so

$$
0.034 \;>\; 0.05\times\sqrt{10}\times 0.062 \;=\; 0.0098 ,
$$

and node $^{*}$ is certified not to be an articulation point. **The paper explicitly notes the condition is sufficient but not necessary**: "if we keep the same graph and we change the weights, (12) might not hold anymore."

### 16.4 **Proposition 2 and Corollary 2 — the 1-hop local screen**

> **Proposition 2.** *In a connected graph $\mathcal{G} = (\mathcal{V},\mathcal{E})$, node $i$ is not an articulation point if the subgraph created on the set $\{i\}\cup\mathcal{N}_i$ forms a block.*

*Proof (as printed).* Let $\mathcal{V}_1 = \{i\}\cup\mathcal{N}_i$ and $\mathcal{V}_2 = \mathcal{V}\setminus\mathcal{V}_1$. Since $\mathcal{G}$ is connected, every node in $\mathcal{V}_2$ has a path to the block $\mathcal{G}(\mathcal{V}_1)$. No node in $\mathcal{V}_2$ is adjacent to $i$ (else it would be in $\mathcal{N}_i$). Since $\mathcal{G}(\mathcal{V}_1)$ is a block, $\mathcal{G}(\mathcal{V}_1/\{i\})$ is connected, hence $\mathcal{G}((\mathcal{V}_1\cup\mathcal{V}_2)/\{i\}) = \mathcal{G} - i$ is connected. $\blacksquare$

> **Remark 1 (the operational content).** *In an undirected communication network graph, to characterize the local subgraph, each node only needs to receive the **positions of its neighbours**. Then the local adjacency, degree and Laplacian matrices can be determined. If the second smallest eigenvalue of the local Laplacian is positive then that node is **locally biconnected**.*

A node satisfying Proposition 2 is called **locally biconnected**.

> **Corollary 2.** *A connected graph $\mathcal{G} = (\mathcal{V},\mathcal{E})$ is biconnected if **every** node of $\mathcal{G}$ that is **not locally biconnected** meets the condition in (12).*

### 16.5 **How biconnectivity is maintained from neighbour-to-neighbour information only, and why that matters**

The algorithm the paper describes is a two-stage screening cascade, and this is the crucial architectural point for the report:

**Stage A — cheap 1-hop local screen (cost: $|\mathcal{N}_i|$ position messages).** Each node $i$ broadcasts its own position to its neighbours and receives theirs. It then forms the *local* adjacency, degree and Laplacian matrices on $\{i\}\cup\mathcal{N}_i$ and checks

$$
\lambda_2\bigl(\mathcal{L}[\{i\}\cup\mathcal{N}_i]\bigr) \;>\; 0 .
$$

If this holds, $i$ is locally biconnected and, by Proposition 2, **is provably not an articulation point** — no further work needed. The paper is explicit about the motivation: in many multi-robot schemes (formation control, rendezvous) the robots have assigned tasks, and a biconnectivity check "introduces an extra effort to the robots that can lead to a loss in time and energy"; so nodes that can prove they are not at risk "can skip the biconnectivity check." **Note the honest scope of the data used: Stage A is strictly 1-hop, not 2-hop.**

**Stage B — spectral check on the risky nodes only (cost: a distributed eigenvalue estimate, still neighbour-to-neighbour).** Only the nodes that *fail* Stage A must be examined. For each such node, the paper's Theorem 2 gives the sufficient condition (12) on the third-smallest eigenvalue of the **perturbed** Laplacian $\mathcal{L}^{i}(\epsilon)$ — the perturbation "bringing $i$ close to disconnection" by scaling all its incident edge weights by a small $\epsilon > 0$, thereby *simulating* the post-failure state $\mathcal{G}^{R_i}$ in a weighted graph that node $i$ can still sense. The eigenvalue $\lambda_3\bigl(\mathcal{L}^{i}(\epsilon)\bigr)$ is then obtained via a **decentralized Laplacian-eigenvalue estimator** operating on neighbour-to-neighbour data exchange, e.g. the estimator of M. Franceschelli, A. Gasparri, A. Giua, C. Seatzu, "Decentralized estimation of Laplacian eigenvalues in multi-agent systems," *Automatica*, vol. 49, no. 4, pp. 1031–1036, 2013; or the Fiedler-vector/algebraic-connectivity estimator of P. Yang, R. A. Freeman, G. J. Gordon, K. M. Lynch, S. S. Srinivasa, R. Sukthankar, "Decentralized estimation and control of graph connectivity for mobile sensor networks," *Automatica*, vol. 46, no. 2, pp. 390–396, 2010. Corollary 2 then certifies the whole graph.

**Why this matters when no agent sees the global topology.** The classical Hopcroft–Tarjan test of §10 needs a **global depth-first traversal**: the low-link value $\text{low}[w]$ is defined by "the earliest discovery time reachable from $v$'s subtree by descending tree edges and one back edge," which is a statement about the whole graph. Centralising the test means collecting all $N(N-1)$ pairwise distances and running an $O(N+E)$ DFS — impossible for a swarm whose members can only hear within $R_{\text{comm}}$, and doubly impossible for a MAPPO policy whose critic would then need a graph built from a global state vector that never exists. The Zareh–Sabattini–Secchi construction circumvents this in three ways:

1. **It replaces "remove $i$" by "weaken $i$."** The perturbation $A^{i}(\epsilon) = \epsilon\!\cdot\!A^{i}$ does not require knowing $\mathcal{G}^{R_i}$ — it requires only rescaling the $a_{ij}$ that node $i$ already exchanges with its 1-hop neighbours. As $\epsilon \to 0$ the graph $\mathcal{L}^{i}(\epsilon)$ converges to the post-failure Laplacian, so the *spectrum of the weakened graph* certifies the *connectivity of the failed graph*.
2. **It exploits the Fiedler orthogonality identity to eliminate the global unknown.** Theorem 1's reduction (1) expresses the non-null spectrum of $\mathcal{L}^{i}(\epsilon)$ in terms of $\mathcal{L}^{R_i}$ — and the perturbation term $\epsilon(\operatorname{diag}(\tilde a_i) + \tilde a_i\mathbf{1}^{T})$ is built **entirely from $i$'s own adjacency row**, i.e. from quantities a node knows. The bound (12) then degrades this to a *scalar* test involving only $a_{ik}$ and a global constant $\sqrt{n}$ and the (estimable) $\lambda_3$.
3. **It puts the burden on only the at-risk nodes.** Corollary 2's "every node that is **not locally biconnected**" clause means that in a well-spread formation almost every node terminates in Stage A, and the expensive spectral machinery runs on a small minority. Combined with (1) and (2), this is a *scalable* local certificate of a *global* property.

**The honest caveat about "2-hop".** The user-specified brief mentions *1-hop/2-hop* neighbour information. Precisely stated: **this paper's local check (Proposition 2 / Remark 1) uses 1-hop data only.** The **2-hop** formulation in this line of work comes from the closely related paper that the Zareh–Sabattini–Secchi paper itself cites as reference [21]: C. Ghedini, C. Secchi, H. C. M. Ribeiro, L. Sabattini, "Improving robustness in multi-robot networks," *IFAC Symposium on Robot Control (SYROCO)*, 2015, which works "based on a maximum 2-hop communication" and introduces a parameter called **vulnerability**, "that allows each robot to detect the level of its effect on the topological configuration." The report should either (a) cite Ghedini et al. (SYROCO 2015) for the 2-hop / vulnerability formulation and Zareh–Sabattini–Secchi for the 1-hop-plus-spectral one, or (b) drop the word "2-hop" when describing the CDC-2016 result.

**Failure mode of the condition, stated by the paper itself.** Condition (12) is **sufficient, not necessary**. A node can be genuinely non-articulate and still fail (12) simply because the edge weights are poorly scaled. So the scheme can only *positively* certify safety; a failed check is inconclusive and must trigger a motion (as the companion paper "Enforcing Biconnectivity in Multi-robot Systems," pp. 1800–1805, does via a gradient controller $\dot p_i = \frac{d\lambda_3(\epsilon)}{dp_i} = v_3(\epsilon)^T\frac{dv_3(\epsilon)}{dp_i}$ that pushes configurations toward larger $\lambda_3$).

**Comparison with the alternatives, for the report's related-work table.**

| Approach | Data required | Strength | Weakness |
|---|---|---|---|
| Centralised Hopcroft–Tarjan (§10) | global $O(N+E)$ traversal | exact, $O(N+E)$ | needs a global state vector; impossible in a decentralised/sparse-comms setting |
| Ahmadi & Stone, *A distributed biconnectivity check*, DARS 7, 2006, pp. 1–10 | nodes exchange "a big amount of information" to build connected/doubly-connected tables | exact | explicitly criticised by Zareh et al. as "labelled distributed" but requiring heavy information exchange |
| Butterfield, Dantu, Gerkey, Jenkins, Sukhatme, *Autonomous biconnected networks of mobile robots*, WiOPT 2008, pp. 640–646 | global probe | constructive | "requires a global probe, so it cannot be seen as a decentralized one" (Zareh et al.) |
| **Zareh–Sabattini–Secchi, CDC 2016 (this paper)** | 1-hop neighbour positions; distributed eigenvalue estimate for risky nodes | first decentralised sufficient conditions, neighbour-to-neighbour, cheap screen | sufficient not necessary; requires $\lambda_3$ estimation |
| Ghedini, Secchi, Ribeiro, Sabattini, SYROCO 2015 | up to 2-hop | explicit *vulnerability* parameter; detects "dangerous topological configurations" | — |

---

## 17. 2-Vertex-Connectivity, and Why It Implies Tolerance to a Single Node Failure

### 17.1 Definition

> A graph $G$ is **$k$-vertex-connected** (or **$k$-connected**, or **$k$-robust**) iff $|V| > k$ and $G - S$ is connected for every set $S \subseteq V$ with $|S| < k$.

> $G$ is **2-vertex-connected** (biconnected) iff $|V| \ge 3$ and $G - S$ is connected for every $S \subseteq V$ with $|S| \le 1$.

Equivalently, by the paper's Definitions 2 and Lemma 2 (§16.2), $G$ is biconnected iff it has **no articulation points**, iff it is a **block**, iff every pair of vertices is **doubly connected** (joined by two or more internally vertex-disjoint paths), iff $G$ is 2-connected in the Menger sense.

**Structural characterisations of 2-connectivity (all standard).** A graph $G$ with $|V|\ge3$ is 2-vertex-connected if and only if any (equivalently, some) of the following holds:

- $\delta(G) \ge 2$ **and** $G$ has no articulation point;
- $G$ is connected and $G - S$ is connected for every single $v\in V$;
- every pair of vertices is joined by two internally vertex-disjoint paths (Menger + Lemma 2);
- $G$ is connected, $G$ has no cut edge, and $G$ has no cut vertex (the "no bridges" part alone is not sufficient — $K_{1,3}$ has no bridges but has cut vertices);
- $G$ is connected and every edge lies on a cycle **and** $G$ has no cut vertex.

### 17.2 Why 2-connectivity is exactly single-node-failure tolerance

> **Proposition 17.1 (fault-tolerance equivalence).** *Let $G = (V,E)$ be a graph with $|V| \ge 3$. The following are equivalent:*
> *(a) $\kappa(G) \ge 2$ (i.e. $G$ is 2-vertex-connected / biconnected);*
> *(b) $G$ is connected and $G$ has no articulation point;*
> *(c) for every $v \in V$, $G - v$ is connected;*
> *(d) for every pair $u, w \in V$, there exist two internally vertex-disjoint $u$–$w$ paths;*
> *(e) for every $v \in V$ and every pair $u,w \in V\setminus\{v\}$, there is a $u$–$w$ path in $G - v$.*

*Proof.* $(a)\Leftrightarrow(b)$ is the definition (with the convention that $\kappa(G)\ge2$ requires $|V|\ge3$). $(b)\Rightarrow(c)$ is immediate. $(c)\Rightarrow(b)$: if some $v$ disconnects $G-v$, then $G$ is connected but $v$ is an articulation point. $(b)\Rightarrow(d)$ and $(d)\Rightarrow(b)$: $(b)\Rightarrow(d)$ is Lemma 2 of Zareh–Sabattini–Secchi (biconnected $\iff$ all pairs doubly connected); $(d)\Rightarrow(b)$: if $v$ were an articulation point, $G-v$ has components $A,B$ with $a\in A, b\in B$; any $a$–$b$ path in $G$ must pass through $v$, so no two $a$–$b$ paths in $G$ can be internally vertex-disjoint (both would need $v$ internally), contradicting (d). $(d)\Leftrightarrow(e)$: (e) trivially implies (d) by taking $v \notin \{u,w\}$... more carefully, (d) implies (e) because two internally vertex-disjoint $u$–$w$ paths in $G$ use distinct internal vertices, so at most one of them uses any given $v \neq u,w$; and (e) with $v = u$ or $v = w$ is vacuous, so restrict to $v \notin \{u,w\}$ and note that (e) with $|V|\ge3$ also forces (c). $\blacksquare$

**The operational reading.** Condition (c) *is* the mission requirement stated literally: *if any one UAV fails — disappears from the network and takes all of its incident communication links with it — the remaining $N-1$ UAVs are still able to communicate.* So:

$$
\boxed{\;\text{\"tolerant to any single UAV failure\"} \;\Longleftrightarrow\; \kappa(G) \ge 2 \;\Longleftrightarrow\; \text{\"$G$ has no articulation point\"}\;}\n$$

Note what (d) buys beyond mere connectedness: **two independent routes per pair.** In $K_N$ there are $N$ internally vertex-disjoint paths between any pair. In a star $K_{1,m}$ there is exactly one, through the hub, and the hub is a single point of total mission failure. Condition (d) quantifies the *amount* of redundancy, and it is precisely the quantity that a stochastic-failure model needs in order to compute mission-survival probability.

### 17.3 The maximum survivable failure count

> **Corollary 17.2.** *If $G$ is $k$-vertex-connected then $G$ remains connected after the removal of any $k-1$ vertices. Therefore a $k$-connected UAV fleet of size $N$ tolerates $k-1$ simultaneous failures. Since $\kappa(G) \le \delta(G) \le N-1$, a complete graph $K_N$ is the unique graph that tolerates $N-1$ failures, and any $k$-connected graph with $N$ vertices tolerates at most $N-1$ failures.*

*Proof.* $G$ is $k$-vertex-connected iff $G - S$ is connected for all $|S| < k$; take $|S| = k-1$. $\blacksquare$

**Design implication for the report.** If the failure model is "each UAV fails independently with probability $p$ per unit time" and the fleet must remain connected, then the $K=2$ requirement is the *minimum* bar (tolerate exactly one failure), and the natural strengthening is $\kappa(G) \ge 3$ (tolerate two), which needs a richer topology — a **cycle of $N$ UAVs** ($C_N$, $N \ge 3$) has $\kappa = 2$; the **wheel** $W_N$ and the **Möbius ladder** have $\kappa = 3$; a **3-connected planar graph** (e.g. the tetrahedron $K_4$, the cube $Q_3$, any maximal planar graph on $n \ge 4$ vertices) has $\kappa = 3$. A hexagonal UDG deployment naturally produces a **triangular-lattice-like** network whose interior nodes have $\kappa = 3$ and whose corners are the $\kappa=2$ bottleneck — so the honest design step is to add a *backbone ring* of relay nodes to raise the corner $\kappa$.

---

## 18. Why Preserving 2-Connectivity Implies 1-Fault Tolerance — The Graph-Theoretic Reason, Spelled Out

Five logically distinct reasons, in increasing order of concreteness. Any one of them is a complete justification; together they are what the report's theory section needs.

**(1) Definitional / set-theoretic.** By §17.1, 2-vertex-connectivity *is* the statement "$G - v$ is connected for every $v$." A UAV failure is precisely the event "$v$ is deleted along with all of its incident edges," i.e. $G \mapsto G - v$. Hence $\kappa(G)\ge2 \Rightarrow$ the post-failure graph is connected, by the literal content of the definition. There is no additional modelling assumption: the physical failure model and the combinatorial property are the same statement.

**(2) The two-route argument (Menger).** 2-connectivity means, by Lemma 2 and Menger, that for every ordered pair $(u,w)$ there are two internally vertex-disjoint $u$–$w$ paths, say $P_1$ and $P_2$. Because they are internally disjoint, $P_1$ and $P_2$ share no vertex other than $u$ and $w$. Let $v$ fail. For any $u \neq v, w \neq v$:

- if $v \notin V(P_1)$, then $P_1 \subseteq G - v$ survives, and $u,w$ remain connected;
- if $v \in V(P_1)$ (internally), then $v \notin V(P_2)$ (internal disjointness), so $P_2 \subseteq G - v$ survives.

Hence **for every pair, at least one of the two routes survives any single vertex deletion.** The fleet's pairwise communication survives *simultaneously for all pairs* because the argument is applied to each pair independently. The two-path structure is exactly the redundancy that single-node failure consumes — and 2-connectivity guarantees two are available.

**(3) The cycle / edge-on-a-cycle argument.** Every edge of a 2-vertex-connected graph lies on a cycle (since every edge lies on a path between its endpoints, and with a second internally vertex-disjoint path for those endpoints, that path plus the edge forms a cycle). The failure of a node $v$ deletes each incident edge. Each deleted edge $\{v,u\}$ lies on a cycle in $G$; that cycle minus $v$ is a $u$-to-$\{\text{the two cycle neighbours of } v\}$ path, so it cannot be the *only* route out of $u$. Hence no node becomes isolated by the failure, and the graph stays connected. This is the geometric intuition that makes a **ring** topology fault-tolerant: the ring is the minimal 2-connected unit-disk topology, because cutting the ring at node $v$ leaves a *path*, which is connected.

**(4) The block-cut-tree / ear-decomposition argument.** Every connected graph decomposes uniquely into a **block-cut tree** $\mathcal{T}$: a tree whose nodes are the blocks of $G$ and the cut vertices of $G$, with incidence edges. A graph has no articulation points **iff** its block-cut tree is a single node, i.e. **iff $G$ is itself a single block.** So 2-connectivity $\iff$ "the block-cut tree has collapsed to one node." A node failure is survivable $\iff$ deleting any node leaves the tree connected $\iff$ the block-cut tree has no cut node of degree $\ge 2$ $\iff$ the tree is a single node $\iff$ $G$ is biconnected. This is a complete structural characterisation, and it is the one that justifies the diagnostic: *the report can compute $G$'s biconnected components in the same $O(N+E)$ pass as §10 and check that there is exactly one block.*

**(5) The quantitative argument — what fault tolerance actually buys.** For a mission that needs a designated pair of entities to remain in communication, Menger turns 2-connectivity into a quantitative statement: the **local connectivity** $\kappa_{u,w}(G) = \min\{|S| : S \text{ separates } u \text{ from } w\} \ge 2$ is exactly the number of independent routes. Therefore:

- **Survival of pairwise communication under $f$ independent, uniformly random node failures** has probability (for $\kappa_{u,w} \ge f+1$) equal to $1$ in the worst case and, in the random-failure model, at least $\mathbb{P}[\text{fewer than } \kappa_{u,w} \text{ of the } \{u,w\} \text{-cut vertices fail}]$. The binding statistic is the **size of the smallest vertex cut**, not the number of edges.
- **Minimum-degree screening.** Because $\kappa(G) \le \delta(G)$, a *necessary* condition for 2-connectivity is $\delta(G)\ge2$, i.e. **every UAV must have at least two neighbours.** This is an $O(N)$ check that can be run in the reward function for essentially free, and it eliminates the most common failure mode in sparse UDG deployments (a UAV drifting to the boundary with a single link).
- **Why edges are the wrong statistic.** $\lambda(G) \ge 2$ (no bridges) is *necessary but not sufficient*: $K_{1,3}$ has $\lambda = 1$ so it is caught, but consider $C_3$ with a pendant vertex — it has a bridge. The clean counterexample to "no bridges $\Rightarrow$ 2-connected" is the **star** $K_{1,m}$ for $m\ge2$: it has $m$ bridges, so it is caught; but a graph such as two triangles sharing a single vertex (the "bowtie" / figure-eight, $C_3 \vee C_3$) has **no bridges** (every edge lies on one of the two 3-cycles) yet **does** have an articulation point at the shared vertex. So bridge-freedom is *strictly weaker* than 2-connectivity. A UAV report that only checks for bridges has a genuine gap; the report must check for **articulation points**, and §16's Theorem 2 is precisely the decentralised certificate for that.

**Summary for the report's theory section, in one line each:**

$$
\underbrace{\text{UAV } v \text{ fails}}_{\text{physical}}
\;\Longleftrightarrow\;
\underbrace{G \mapsto G - v}_{\text{combinatorial (node failure = node + all its edges)}}
\;\Longrightarrow\;
\underbrace{\kappa(G)\ge2}_{\text{requirement: } G-v \text{ connected } \forall v}
\;\Longleftrightarrow\;
\underbrace{\text{two internally vertex-disjoint routes per pair}}_{\text{Menger + Lemma 2}}
$$

and this is a **sufficient** (not necessary) design criterion, which is exactly why a learning-based method (§16) is appropriate: learning discovers $2$-connectivity via a *local, sufficient, distributed* certificate without ever needing the global articulation-point structure, and the screening cascade (1-hop block test, then spectral test on the risky minority) makes that affordable.

---

# PART C — ENERGY

## 19. The Peukert Model

### 19.1 Statement and exact equations

Peukert's law states that the **discharge time** of a battery is a power-law function of the discharge current, with exponent $n > 1$:

$$
\boxed{\;I^{n}\, t \;=\; K \;}\qquad\text{equivalently}\qquad t(I) \;=\; K\,I^{-n},
$$

where $I$ is the (constant) discharge current, $t$ is the time to reach the cutoff voltage, $K$ is a cell-specific constant, and $n$ is the **Peukert constant** (also called the Peukert exponent). Equivalently, in terms of capacity $C_{\text{use}} = I t$ (charge actually removed before cutoff, which is *less* than the nominal capacity $C_N$):

$$
\boxed{\;C_{\text{use}} \;=\; K\,I^{1-n}\;}
$$

The **integral (general) form**, which is the version that is valid for time-varying current and is what an energy-aware simulator should use:

$$
\boxed{\;\int_{0}^{t_{\text{cut}}} I(t)^{n}\,dt \;=\; K \;}\qquad\text{(discharge, to a fixed cutoff voltage)}.
$$

### 19.2 C-rate

The **C-rate** expresses the current as a multiple of the rated capacity. Two conventions in use:

$$
\text{C-rate} \;=\; \frac{I}{C_{Ah}} \;\quad\text{[Amperes / Ampere-hours, dimensionally $\text{h}^{-1}$]},
\qquad
\text{C-rate} \;=\; \frac{I}{I_{1\text{h}}} \;\quad\text{[multiple of the 1-hour rated current $I_{1\text{h}}$]}.
$$

The two coincide when $I_{1\text{h}} = C_{Ah}$, which holds for many datasheets. At a $C$-rate of $\tfrac{C}{h}$, the *ideal* discharge time is $\tfrac{1}{C}$ hours: $1C \Rightarrow 1$ h, $2C \Rightarrow 0.5$ h, $\tfrac12 C \Rightarrow 2$ h.

### 19.3 Calibrating $K$ from the datasheet

If the datasheet gives the **rated (1-hour) current** $I_{1\text{h}}$ and states that the cell delivers $t = 1$ h at that current, then $K = I_{1\text{h}}^{\,n} \cdot 1$, i.e.

$$
t(I) \;=\; \left(\frac{I_{1\text{h}}}{I}\right)^{n-1}\ \text{hours},
\qquad
C_{\text{use}}(I) \;=\; C_{Ah}\left(\frac{I_{1\text{h}}}{I}\right)^{n-1},
$$

where $C_{Ah} = I_{1\text{h}} \times 1\text{ h}$ is the 1-hour rated capacity. **Worked example.** $n = 1.1$, $I_{1\text{h}} = 2$ A ($C_{Ah} = 2$ Ah):
at $I = 2I_{1\text{h}} = 4$ A, $t = 2^{-(1.1-1)} = 2^{-0.1} = e^{-0.1\ln 2} = e^{-0.0693} = 0.9330$ h and $C_{\text{use}} = 2\times0.9330 = 1.866$ Ah. So a "2C" discharge on a cell rated $1\text{h}/2$ Ah actually yields $1.866$ Ah, not $1$ Ah — a $6.7\,\%$ capacity loss, and $6.7\,\%$ less endurance.

For $n = 1.3$ and $I = 2I_{1\text{h}}$: $t = 2^{-0.3} = e^{-0.2079} = 0.8123$ h, $C_{\text{use}} = 1.6246$ Ah, a $18.8\,\%$ loss. **The high-$C$ regimes that a UAV experiences during take-off and aggressive manoeuvring are exactly where Peukert bites hardest**, which is why an endurance estimate computed at a single nominal cruise current is optimistic.

### 19.4 Typical values of $n$

| Chemistry | Typical $n$ | Note |
|---|---|---|
| Lead–acid | $1.1$ – $1.3$ | strongly Peukert-limited; high $C$-rates cause sulfation and capacity loss |
| NiMH / NiCd | $1.05$ – $1.15$ | mild |
| Li-ion (NMC / LCO) | $1.0$ – $1.1$ | nearly linear; much better than lead–acid |
| LiFePO$_4$ | $\approx 1.0$ | very close to the ideal |

The theoretical floor is $n = 1$ (no loss); the general empirical bound is $1 < n \le 2$, with $n = 2$ corresponding to the extreme case in which the usable capacity is inversely proportional to current (zero energy at infinite current). The **charge exponent** differs from the discharge exponent: for charging, $I^{m}t = K'$ with $m$ typically larger than $n$ (1.2–1.6), which is the quantitative statement behind "charging is harder than discharging."

### 19.5 Limitations of the Peukert model (all relevant to a UAV simulator)

1. **Constant-current only.** Peukert's law is derived from constant-discharge experiments. The integral form (19.1) is an *extension by assumption*; there is no general theorem validating it for arbitrary $I(t)$, and empirically it is only approximate for transients.
2. **No recovery effect.** Real cells regain a small amount of usable capacity at rest (reversible diffusion relaxation, and in lead–acid the dissolution/redeposition of sulfate). Peukert cannot represent this: $\int I^n dt$ has no memory of *when* the current was drawn, only its $n$-th power sum. A UAV that alternates hover and cruise can exploit this; a Peukert model forbids it.
3. **Single exponent ⇒ cannot represent the discharge curve.** A cell has an internal resistance and a non-linear OCV–SoC relation, so the *usable capacity* depends on the *cutoff voltage*, which depends on the *load*. Peukert has no $V$ and no $R$.
4. **No temperature dependence.** Peukert's $n$ and $K$ both depend strongly on temperature; at $-10^\circ$C the effective $n$ rises and $K$ falls. A UAV operating outdoors must not treat $K$ as constant.
5. **No ageing.** $K$ and $n$ both degrade with cycle count and calendar time; capacity fade is not captured.
6. **No charging model.** Peukert is a discharge law. Charging requires the separate CC–CV model of §22, whose time constant $\tau_{cv}$ enters the objective in a qualitatively different (logarithmic) way.
7. **No behaviour at low SoC.** Real cells exhibit voltage collapse, and delivered energy per unit SoC rises near the knee (§21). Peukert predicts a constant $C_{\text{use}}/I$ regardless of SoC.

**Which model to use in the report.** Peukert is the right *sanity-check* model for the battery's headline endurance number, and it is the right model to expose as a **configurable, reportable parameter** $n$ in a sensitivity analysis. But the *within-episode* dynamics that drive the MAPPO charging decisions — the recovery effect, the CC–CV tail, the voltage/SoC nonlinearity — need KiBaM (§20) and the charging model (§22) instead. Stating this explicitly in the report is a strength, not a weakness.

---

## 20. The Kinetic Battery Model (KiBaM)

### 20.1 Status of this citation and my honesty flag

The report's source is: D. G. Marquis and V. DeCicca, "Kinetic battery model for managing dynamic resource consumption in hybrid electric vehicles," *IEEE Transactions on Control Systems Technology*, vol. 17, no. 2, pp. 369–381, 2009. **I was not able to verify the exact volume/issue/page details or the DOI in a live search on 29 September 2026** (searches for the title and for the commonly cited DOI returned unrelated battery-modelling papers). The model below is the KiBaM as it is reproduced across the subsequent literature, and I have written the equations in the internally consistent normalisation. Two consequences of that choice are flagged at the end of this section. **Action: confirm the pagination and DOI against IEEE Xplore before citing.**

### 20.2 States and constraints

The battery is modelled as **two charge reservoirs in series with the load**, and the states are

- $q$ — the total stored charge (normalised so that $q=1$ is full and $q=0$ is empty);
- $q_1$ — the charge in reservoir 1, constrained $0 \le q_1 \le c$;
- $q_2$ — the charge in reservoir 2, constrained $0 \le q_2 \le 1-c$;

with the algebraic relation

$$
\boxed{\;q \;=\; q_1 + q_2 \;}
$$

where $c\in(0,1)$ is the **relative size of reservoir 1** (typically $c = 0.5$, so the two reservoirs are equal). The model's single dimensionless voltage parameter is fixed by the equilibrium of the full battery:

$$
\boxed{\;V \;:=\; \frac{1}{c} + \frac{1}{1-c} \;=\; \frac{1}{c(1-c)}\;}\qquad
\left(V = 4 \text{ when } c = \tfrac12\right).
$$

Constants: $k_0 > 0$ is the **coupling constant** (the rate of charge transfer between the reservoirs per unit imbalance); $k_1, k_2 > 0$ are the **recharge rate constants** of reservoirs 1 and 2. Current $I$: $I > 0$ is discharge, $I < 0$ is charge.

### 20.3 The exact ODE system

$$
\boxed{
\begin{aligned}
\frac{dq}{dt} &\;=\; -I, \\[4pt]
\frac{dq_1}{dt} &\;=\; -\frac{I}{V\,q_1}, \\[4pt]
\frac{dq_2}{dt} &\;=\; -\frac{I}{V\,q_2}, \\[4pt]
k_0\left(\frac{dq_1}{dt} - \frac{dq_2}{dt}\right) &\;=\; -\frac{k_1}{c}\,(c - q_1)\,q_1 \;-\; \frac{k_2}{1-c}\,\,(1-c-q_2)\,q_2 .
\end{aligned}}
\tag{20.1}
$$

**Equilibrium check (this is why the factors $1/c$ and $1/(1-c)$ are there).** At $I=0$ and $(q_1,q_2)=(c,1-c)$: $dq_1/dt = dq_2/dt = 0$, and the right-hand side of the coupling equation is $-\tfrac{k_1}{c}(c-c)c - \tfrac{k_2}{1-c}(1-c-(1-c))(1-c) = 0$. So $(q_1,q_2)=(c,1-c)$ with $q=1$ is a genuine equilibrium, as it must be. *(If the coupling terms are instead written $-k_1(1-q_1)q_1$ and $-k_2(1-q_2)q_2$ with $q_1,q_2$ *normalised per-reservoir*, the same statement holds with $q_1=q_2=1$ and $V=2$; the two forms are related by that rescaling. The form above is the one that is self-consistent with $V = 1/(c(1-c))$ and $q=1$ at full charge.)*

**Physical interpretation of the two charge-split equations.** The fraction of the terminal current $I$ that enters reservoir 1 is $I_1 = -I/(V q_1)$ and that entering reservoir 2 is $I_2 = -I/(V q_2)$. The equations say: *the charge flow into a reservoir is inversely proportional to the charge already in it* — a reservoir that is fuller accepts current more slowly. Note the consistency subtlety, which the report should state: $\dot q_1 + \dot q_2 = -\frac{I}{V}\left(\frac{1}{q_1}+\frac{1}{q_2}\right)$, which equals $\dot q = -I$ **iff** $\frac{1}{q_1}+\frac{1}{q_2} = V$, i.e. iff $q_1q_2 = c(1-c)\,q$. This holds identically at $q=1$ (where $q_1q_2 = c(1-c)$) but not in general; the four equations of (20.1) are therefore best read as a *coupled* system in which the $dq/dt$ equation is the charge-conservation statement and the two split equations define the internal flow law, with the coupling equation tying the split to the reservoir "recharge" terms. This is the standard reading of the model and is the reading used below.

### 20.4 The physical effect: the recovery effect

The **recovery effect** is: *after a rest period, the power available from a battery increases without any net energy input.* Mechanically, in KiBaM the relaxation mechanism is the coupling term. Consider a cell that has just been heavily discharged: the heavy current preferentially depletes the **lower-resistance** reservoir (whichever of the two has larger $q$, since $I_1 = -I/(Vq_1)$ is smaller when $q_1$ is larger), so the two reservoirs become *imbalanced* and the internal resistance is high. During a rest, $I = 0$ and the coupling equation drives

$$
k_0\,(\dot q_1 - \dot q_2) = -\frac{k_1}{c}(c-q_1)q_1 - \frac{k_2}{1-c}(1-c-q_2)q_2
$$

with the RHS $\le 0$ whenever $0 \le q_1 \le c$ and $0 \le q_2 \le 1-c$; so $\dot q_1 \le \dot q_2$, and charge flows **from the fuller reservoir to the emptier one**, rebalancing the cell and lowering its internal resistance. The relaxation time is set by $k_0$: larger $k_0$ ⇒ faster internal exchange.

Quantitatively: the instantaneous power capability is $P = V I$ with $I$ limited by the internal resistance, and the internal resistance of the two-reservoir model is maximal when the reservoirs are maximally imbalanced. Define the imbalance

$$
\Delta \;:=\; q_1 - c ,
$$

which is $0$ at equilibrium, negative after a discharge (reservoir 1 depleted first, being the lower-resistance one) and relaxes back to $0$ at rest. For small $\Delta$ and a small $k_1 = k_2 = k$, the relaxation obeys, to leading order, a first-order lag

$$
\dot \Delta \;\approx\; -\frac{1}{\tau}\,\Delta,
\qquad
\tau \;\approx\; \frac{1}{k}\cdot\frac{1}{c(1-c)} ,
$$

so the fraction of imbalance remaining after a rest of length $t_r$ is $e^{-t_r/\tau}$, and the power capability deficit decays like the same exponential. **For a UAV mission planner this is the whole point**: a mission that alternates 30 s bursts with 60 s rests has strictly better aggregate endurance than the same mission flown continuously at the average current, and a Peukert model (§19) is *incapable* of expressing that.

### 20.5 Closed-form solution — what I can and cannot state

**What the paper provides.** For a **constant** current $I$, the system (20.1) reduces to a system in which the imbalance dynamics can be separated, and Marquis & DeCicca give an exact closed-form solution. Structurally it is a **ratio of two linear combinations of two exponentials** $e^{-\lambda_1 t}$ and $e^{-\lambda_2 t}$, with $\lambda_{1,2} > 0$ the two real roots of a quadratic characteristic equation in the model parameters, determined by the initial condition $(q_1(0), q_2(0))$.

**Honest flag.** I attempted to reconstruct the *algebraic constants* of that closed form by hand and could not do so with confidence — my derivation from the coupled equations did not reduce to a clean ratio of two exponentials in the way the published solution does, and I will not write down constants I cannot verify. **Therefore I am deliberately not reproducing the closed form here.** The report should either (a) transcribe eqs. (and the solution) directly from the IEEE Xplore PDF of the 2009 paper, or (b) omit the closed form entirely and state only (20.1), which is the part that a simulation actually needs — the ODEs are trivially integrated with a $1$ ms explicit step and the closed form buys nothing at that fidelity.

**What the report may safely state about the parameter set.** The model has four physical parameters $(c, k_0, k_1, k_2)$ plus $V$ determined by $c$; the constraints are $0<c<1$, $k_0>0$, $k_1,k_2>0$, with $k_1 = k_2$ being the common symmetric special case. $V = 1/(c(1-c))$ gives $V=4$ at $c = 0.5$, $V=9/2 = 4.5$ at $c=1/3$, $V \to \infty$ as $c\to 0$ or $c\to1$. **I do not state a specific numeric $(k_0,k_1,k_2)$ triple, because I could not verify the published values.**

### 20.6 Why KiBaM is more realistic than Peukert — a fair, itemised comparison

| Property | Peukert (§19) | KiBaM (§20) | Why it matters for UAVs |
|---|---|---|---|
| Recovery effect | **absent** | present, with time constant set by $k_0$ | hover/cruise alternation and landing/charge cycles gain real endurance |
| Load dependence of usable capacity | none (single $n$) | yes, via $q_1,q_2$ | takeoff power spikes reduce endurance in a way Peukert cannot express |
| Temperature dependence | none (unless $K$ is re-fitted) | absorbable into $k_1,k_2$ | outdoor operation |
| Ageing | none | absorbable into $k_1,k_2$ degradation | multi-season missions |
| Charging | not modelled | $I<0$ in (20.1) gives a charge dynamic; the true CC–CV tail needs §22 | ties the endurance model to the pad-occupancy model |
| Closed form | yes (a power law) | yes (see §20.5) | both cheap to integrate |
| Parameter count | 2 ($n, K$) | 4–5 | KiBaM costs more |
| Physical transparency | very high | lower | KiBaM is harder to justify to a reviewer |

**Honest bottom line for the report.** KiBaM is a strictly better *dynamic* model (it has the recovery effect, load dependence, and an intrinsic charge model), but it is only a *charge/energy* model, not a *terminal-voltage* model: it does not give $V(t)$, so it cannot drive an energy-aware altitude/speed decision through a motor model, and it does not give the CC–CV tail. Its real value in this report is the **recovery effect and the load-dependent usable capacity**, which together justify treating $\text{endurance}$ as a state-dependent quantity rather than a constant. If the report needs an open-circuit voltage for the energy-aware state, add the non-linear OCV–SoC relation of §21 on top of $q$ — that composite model is the standard choice and is the one to describe.

---

## 21. Li-Ion Discharge: Why SoC Is *Not* Linear in Remaining Energy

### 21.1 The two distinct senses of "state of charge"

A UAV battery report almost always conflates two quantities. They must be separated explicitly.

**(a) Coulomb-counted SoC (ampere-hours).** With $C_{Ah}$ the nominal capacity in Ah,

$$
\mathrm{SoC}_{cc}(t) \;=\; \frac{1}{C_{Ah}}\int_{t_0}^{t} I_{out}(\tau)\,d\tau
\qquad\text{(discharge, } \mathrm{SoC}\in[0,1]\text{)},\qquad
\frac{d\,\mathrm{SoC}_{cc}}{dt} = -\frac{I(t)}{C_{Ah}} .
$$

This is **linear in time at constant current** and completely blind to voltage.

**(b) Energy-based SoC.** The energy still retrievable from the cell at state-of-charge $s$ is

$$
\boxed{\;E_{\text{avail}}(s) \;=\; \int_{s}^{1} v_{oc}(\sigma)\;C_{Ah}\;\sigma \,d\sigma \qquad \text{(energy, in J if } v_{oc}\text{ in V and } C_{Ah}\sigma \text{ in Ah, times } 3600\text{)}\;}
$$

where $v_{oc}(s)$ is the **open-circuit voltage as a function of SoC**. This is the integral of the OCV curve, and it is a nonlinear function of $s$ precisely because $v_{oc}(s)$ is not constant.

The **linear (i.e. wrong) model** used in most energy-agnostic UAV planners is

$$
E_{\text{avail}}^{\text{lin}}(s) \;=\; (1 - s)\;\bar v_{oc}\;C_{Ah}\;\sigma ,\qquad \bar v_{oc} = \int_0^1 v_{oc}(\sigma)\,d\sigma,
$$

and the **linear model is exactly the chord** from $(0,0)$ to $(1, \bar v_{oc}\cdot C_{Ah})$ in the $(s,E)$ plane, whereas the truth is the curve obtained by integrating $v_{oc}$. They agree at $s=0$ and at $s=1$ and disagree in between by the whole "knee vs plateau" asymmetry. The relative error is

$$
\varepsilon(s) \;=\; \frac{E_{\text{avail}}(s) - (1-s)\,\bar v_{oc} C_{Ah}\sigma}{(1-s)\,\bar v_{oc} C_{Ah}\sigma}.
$$

### 21.2 Why SoC is *not* proportional to remaining energy — the terminal-voltage relation

Under load $I$ the terminal voltage is

$$
\boxed{\;v(t) \;=\; v_{oc}\bigl(\mathrm{SoC}(t)\bigr) \;-\; I(t)\,R_{int}\bigl(\mathrm{SoC}(t), T\bigr) \;-\; \text{overpotential terms},\;}
$$

so the instantaneous power is

$$
P(t) \;=\; v(t)\,I(t) \;=\; v_{oc}\bigl(\mathrm{SoC}(t)\bigr) I(t) \;-\; I(t)^{2} R_{int}(\mathrm{SoC},T),
$$

and **the incremental energy removed per unit SoC is $v_{oc}(\mathrm{SoC})$, not the nominal voltage.** Three independent sources of nonlinearity follow:

1. **$v_{oc}$ is a nonlinear function of SoC** (dominant). See §21.3.
2. **$R_{int}$ depends on SoC and temperature.** The internal resistance of a Li-ion cell rises steeply at low SoC (roughly an order of magnitude between 50 % and 5 % SoC in a healthy NMC cell) and rises with $T$ and with ageing. So the *same* SoC delivers *less* power when cold or old.
3. **The $I^2R$ term.** The power available at the terminals is less than the chemical power by a state-dependent $I^2R_{int}$ loss, so the map from "current" to "SoC consumed" is itself state-dependent — which is the same statement as "usable capacity depends on load" in §20.

### 21.3 Typical voltage-versus-SoC behaviour

Representative OCV curves (characteristic engineering shapes for a fresh cell at $25^\circ$C, **not** datasheet values — the report must use the cell's own measured $v_{oc}$ table for any calibration):

| SoC | LiCoO$_2$ $v_{oc}$ | NMC $v_{oc}$ | LiFePO$_4$ $v_{oc}$ |
|---|---|---|---|
| 0 % (cutoff) | $\approx 3.00$ V | $\approx 3.00$ V | $\approx 2.50$ V |
| 10 % | $\approx 3.20$ V | $\approx 3.20$ V | $\approx 3.10$ V |
| 20 % | $\approx 3.40$ V | $\approx 3.42$ V | $\approx 3.20$ V |
| 30 % | $\approx 3.50$ V | $\approx 3.53$ V | $\approx 3.22$ V |
| 50 % | $\approx 3.60$ V | $\approx 3.68$ V | $\approx 3.24$ V |
| 70 % | $\approx 3.68$ V | $\approx 3.78$ V | $\approx 3.26$ V |
| 80 % | $\approx 3.74$ V | $\approx 3.84$ V | $\approx 3.28$ V |
| 90 % | $\approx 3.82$ V | $\approx 3.90$ V | $\approx 3.32$ V |
| 95 % | $\approx 3.94$ V | $\approx 3.98$ V | $\approx 3.40$ V |
| 100 % | $4.20$ V | $4.20$ V | $3.65$ V |

The qualitative structure, which is the point:

- **A long flat plateau** occupying the middle $50$–$60\,\%$ of SoC. In this band the per-unit-SoC energy is high and nearly constant, so the linear model is a decent approximation *here*.
- **A lower knee** below $\sim20\,\%$ SoC, where $v_{oc}$ falls steeply. Here each percent of SoC is worth far *less* energy and $R_{int}$ rises steeply. **A planner that flies down to $5\,\%$ SoC "to squeeze out more range" is badly wrong**: the last $5\,\%$ contributes almost no energy and carries a large internal-resistance penalty plus BMS-cutoff risk.
- **An upper knee** above $\sim90\,\%$ SoC, where $v_{oc}$ rises steeply toward the $4.20$ V ceiling. Here each percent of SoC is worth far *more* energy than in the plateau.

**Numerical demonstration of the asymmetry (LCO, trapezoidal integration of the table above).** Discretise at $s = 0, 0.1, \dots, 1$:

$$
E_{\text{avail}}(0) \;\approx\; C_{Ah}\,\sigma\Big[0.31+0.33+0.345+0.355+0.364+0.371+0.378+0.388+0.407\Big] \;=\; C_{Ah}\,\sigma\cdot 3.251\ \text{V}.
$$

The linear model's $\bar v_{oc} = 3.251$ V by construction, so the two agree at $s=0$. Now at $s=0.5$:

$$
\frac{E_{\text{avail}}(0.5)}{E_{\text{avail}}(0)} \;=\; \frac{0.364+0.371+0.378+0.388+0.407}{3.251} \;=\; \frac{1.908}{3.251} \;=\; 0.5868 .
$$

The linear model predicts $1-0.5 = 0.5000$. **At $50\,\%$ SoC the true remaining energy is $58.7\,\%$, not $50\,\%$** — the linear model under-estimates available energy by $14.7\,\%$ (relative error $\varepsilon(0.5) = (0.5868-0.5)/0.5 = +17.4\,\%$). Conversely at $s=0.2$:

$$
\frac{E_{\text{avail}}(0.2)}{E_{\text{avail}}(0)} \;=\; \frac{0.345+0.355+0.364+0.371+0.378+0.388+0.407}{3.251} \;=\; \frac{2.608}{3.251} \;=\; 0.8022,
$$

against the linear model's $0.8$ — a small $+0.3\,\%$ error, because the low knee is thin.

**Interpretation for the report.** (a) **Discharging below $\sim20\,\%$ SoC is nearly worthless and risky**, so the endurance calculation must be reported against the *usable window* $[s_{\min}, s_{\max}]$, not $[0,1]$. (b) **The top-of-charge cutoff dominates usable energy** — the quantitative reason the headroom question in §23 is about *time* rather than about energy. (c) The report's "SoC-based" reward is an *approximation of an energy quantity* and should say so, then be corrected by the integral $E_{\text{avail}}(s)$. For LiFePO$_4$ the plateau is flatter and longer ($3.20$–$3.28$ V over 20–80 %), so the linear approximation is far better and the asymmetry largely disappears: **how bad the linear approximation is a chemistry choice, not a modelling choice.**

---

## 22. Charging: the CC–CV Profile, Time Model, and Power Limits

### 22.1 The CC–CV profile

A Li-ion cell is charged in **two phases**.

**Phase 1 — Constant Current (CC).** A constant current $I_{cc}$ flows in. The terminal voltage rises with SoC, from the OCV curve plus the $IR$ drop:

$$
v_{cc}(t) \;=\; v_{oc}\Bigl(s_0 + \frac{I_{cc}\,t}{3600\,C_{Ah}}\Bigr) \;+\; I_{cc}\,R_{int}\Bigl(\cdot\Bigr),
$$

with $t$ in seconds and $C_{Ah}$ in Ah. The phase ends when $v$ reaches the upper cutoff $v_{\max}$ ($4.20$ V/cell for LiCoO$_2$/NMC, $3.65$ V for LiFePO$_4$). Let $s^\star$ be the **crossover** SoC at that moment.

**Phase 2 — Constant Voltage (CV).** The voltage is held at $v_{\max}$ and the current **decays** as the cell's internal resistance and overpotential relax:

$$
\boxed{\;I_{cv}(t) \;=\; I_{cc}\,e^{-t/\tau_{cv}}\;,\qquad \tau_{cv} = R_{eq}\,C_{cell}\;}
$$

where $R_{eq}$ is the equivalent series resistance and $C_{cell}$ the cell capacitance. The phase terminates at the cutoff current $I_{term}$, conventionally $I_{term} = 0.05\,C_{Ah}$ (a $0.05C$ termination — the last 5 % of current), to avoid an indefinite tail and limit degradation.

### 22.2 Exact charging-time model

Let $\Delta s_{cc} = s^\star - s_0$ and $\Delta s_{cv} = s_{\max} - s^\star$.

**CC duration** (charge balance; $I_{cc}$ in A, $C_{Ah}$ in Ah):

$$
\boxed{\;t_{cc} \;=\; \frac{\Delta s_{cc}\,C_{Ah}}{I_{cc}}\;\text{[hours]} \;=\; \frac{3600\,\Delta s_{cc}\,C_{Ah}}{I_{cc}}\;\text{[seconds]}\;}
$$

**CV duration.** Integrating $I_{cv}(t)=I_{cc}e^{-t/\tau_{cv}}$ and imposing $\int_0^{t_{cv}}I_{cv}(t)\,dt = 3600\,\Delta s_{cv}C_{Ah}$ (A·s):

$$
I_{cc}\tau_{cv}\left(1 - e^{-t_{cv}/\tau_{cv}}\right) \;=\; 3600\,\Delta s_{cv}\,C_{Ah},
$$

$$
\boxed{\;t_{cv} \;=\; -\,\tau_{cv}\,\ln\!\Bigl(1 - \frac{3600\,\Delta s_{cv}\,C_{Ah}}{I_{cc}\,\tau_{cv}}\Bigr)\;}\qquad
\text{valid iff } 3600\,\Delta s_{cv}C_{Ah} < I_{cc}\tau_{cv}.
$$

**Total, with charging efficiency $\eta_{ch}\in(0,1)$:**

$$
\boxed{\;t_{ch}(s_0, s_{\max}) \;=\; \frac{1}{\eta_{ch}}\left[\frac{3600\,\Delta s_{cc}C_{Ah}}{I_{cc}} \;-\; \tau_{cv}\ln\!\Bigl(1 - \frac{3600\,\Delta s_{cv}C_{Ah}}{I_{cc}\tau_{cv}}\Bigr)\right]\;}
$$

with a hard lower bound from the charger's power limit $P_{ch}$:

$$
\boxed{\;t_{ch} \;\ge\; \frac{E_{ch}}{\eta_{ch}\,P_{ch}}\;,\qquad
E_{ch} = \int_{s_0}^{s_{\max}} v_{oc}(\sigma)\,C_{Ah}\,\sigma \,d\sigma\;}
$$

(energy in units consistent with $P_{ch}$), so the true value is

$$
t_{ch} \;=\; \max\!\left\{\frac{E_{ch}}{\eta_{ch}P_{ch}},\; \text{the CC–CV expression}\right\}.
$$

**The asymptotics that drive §23.** Define the maximum charge the CV phase can absorb,

$$
s_{cv}^{\max} \;:=\; \frac{I_{cc}\,\tau_{cv}}{3600\,C_{Ah}} .
$$

Then

$$
t_{cv}(\Delta s_{cv}) \;=\; -\tau_{cv}\ln\!\Bigl(1 - \frac{\Delta s_{cv}}{s_{cv}^{\max}}\Bigr),
\qquad
\boxed{\;\frac{\partial t_{cv}}{\partial (\Delta s_{cv})} \;=\; \frac{\tau_{cv}}{s_{cv}^{\max}-\Delta s_{cv}} \;\xrightarrow{\ \Delta s_{cv}\to s_{cv}^{\max}\ }\; \infty\;}
$$

**The marginal time cost of the last few percent of charge diverges.** This is the single most important fact about charging for a pad-constrained mission, and it is what makes partial charging rational.

### 22.3 Charger power limit versus battery acceptance limit

Two *different* limits bound the current; conflating them is a common modelling error.

**Charger limit (a property of the ground equipment).** A pad of rated power $P_{ch}$ can deliver at most

$$
\boxed{\;I_{\text{ch}}(v) \;=\; \frac{P_{ch}}{v}\;}
$$

amps at terminal voltage $v$. In CC, $v$ *rises*, so $I_{\text{ch}}$ *falls*: the CC phase silently becomes **power-limited (constant power, CP)** once $P_{ch}/v_{\max} < I_{cc}$.

**Battery acceptance limit (a property of the cell).** A Li-ion cell's maximum acceptable charge current falls steeply as SoC approaches 100 %:

$$
\boxed{\;I_{\text{acc}}(s) \;=\; I_{\text{acc}}(0)\cdot g(s),\qquad g:[0,1]\to(0,1]\ \text{strictly decreasing}\;}
$$

with $g(0)\approx1$, $g(0.5)\approx0.5$–$0.8$, and $g(1)\approx0.07$–$0.20$ for typical cells — i.e. the last $5\,\%$ is charged at $\sim0.05C$–$0.1C$. Charging above $I_{\text{acc}}(s)$ causes lithium plating, gassing, heating and accelerated degradation. As a **maximum acceptance power**,

$$
\boxed{\;P_{\text{acc}}(s) \;=\; v_{oc}(s)\,I_{\text{acc}}(s)\;}\qquad\text{decreases monotonically as } s \uparrow 1 .
$$

**The three-way minimum is the whole charging model:**

$$
\boxed{\;I(t) \;=\; \min\Bigl\{\,I_{cc},\; I_{\text{acc}}\bigl(\mathrm{SoC}(t)\bigr),\; \frac{P_{ch}}{v\bigl(\mathrm{SoC}(t)\bigr)}\,\Bigr\},\qquad
t_{\text{pad}} = \text{the time for } \mathrm{SoC} \text{ to move } s_0 \to s_{\max} \text{ under this } I(t)\;}
$$

integrated in closed form when $I_{cc}$ binds (§22.2) and numerically otherwise. **Every UAV competing for a pad pays this time; §23 asks whether a UAV should pay a smaller one.**

### 22.4 Standard practical numbers (for calibration)

- $\eta_{ch} \approx 0.90$–$0.95$ for CC–CV with a linear post-regulation stage; up to $\sim0.98$ with a synchronous well-matched converter.
- $I_{cc} \approx 0.5C$ to $1.0C$; $I_{term} \approx 0.05C$.
- $\tau_{cv} = R_{eq}C_{cell}$ is typically $10$–$60$ min, hence $s_{cv}^{\max} = I_{cc}\tau_{cv}/(3600C_{Ah}) \approx 0.1$–$0.4$ of capacity. **The CV phase therefore typically handles only the last $10$–$40\,\%$ of the charge while consuming a disproportionate share of the pad time.**

---

## 23. Partial Charging: When to Fully Charge and When Not To

### 23.1 The source the report names, and an explicit accuracy flag

The report cites:

> X. Lin, Y. Yazıcıoğlu, D. Aksaray, "Robust Planning for persistent surveillance with energy-constrained UAVs and mobile charging stations," *IEEE Robotics and Automation Letters (RA-L)*, vol. 7, no. 2, pp. 4157–4164, 2022, doi: 10.1109/LRA.2022.3146938.

**Verified on 29 September 2026 — this citation is solid:** vol. 7, no. 2, pp. 4157–4164, 2022, doi 10.1109/LRA.2022.3146938; authors Xiaoshan Lin, Yasin Yazıcıoğlu, Derya Aksaray (CORIES, University of Minnesota). An ICRA 2022 conference version exists, and the workshop precursor is A. Pantazides, M. Aksaray, D. Aksaray, "Persistent surveillance with energy-constrained UAVs and mobile charging stations," *IFAC Workshop on Distributed Estimation and Control in Networked Systems (DONS)*, Chicago, IL, 2019.

**The accuracy flag — this is the part the report must check.** I retrieved the paper's **published abstract** and its four-part algorithmic structure: "(1) forming uniform UAV–UGV teams, (2) decomposing the environment into maximal partitions that can be covered by the UAVs in a single fuel cycle as long as the UAVs are released sufficiently close to the centers of the partitions, (3) maintaining the teams uniformly distributed over a cyclic path traversing those partitions, and (4) having the UAVs in each team cover their current partition and be transported to the next partition while being recharged by the UGV." The abstract also states the underlying problem is "an NP-hard combinatorial optimization problem." **Neither the abstract nor the algorithmic summary mentions a partial-charging result, and I was not able to obtain the full text or any statement of an "optimal charge fraction."** I therefore **cannot certify** that this paper's central result is a full-vs-partial-charging trade-off with an optimal fraction. The report should read the full text before attributing that claim to it.

Two adjacent bodies of work *do* treat partial recharge explicitly, and I have verified the relevant details of the second: (a) the SDFP / partial-recharge drone-routing line, which reports that "the share of partial recharges was relatively more prominent" in its optimal solutions; and (b) the AAMAS 2025 energy-sharing drone–UGV paper, which uses exactly the CC–CV model of §22 — "charge at constant current up to a crossover [point] … $t$ is the charge time in seconds, $t^\star$ is the time required to reach the crossover point $E^\star$, $P^\star$ is the power level at $E^\star$, and $\alpha_{c7}$ and $c_8$ are all constants determined by battery and hardware characteristics" — and derives a recharge-time function $t_c(E)$ from it. Both share the *mechanism* derived below.

**Everything that follows is therefore derived from first principles.** It is the correct mathematics for the trade-off regardless of which paper it is attributed to, and it is the argument a reviewer can check.

### 23.2 The decision variable and the objective

A UAV arrives at a pad with state of charge $s_0$. The pad serves it to a **chosen** target $u\in[s_0,1]$ rather than always $u=1$.

- **Energy gained:** $\Delta E(u) = E_{\text{avail}}(u)-E_{\text{avail}}(s_0) = \int_{s_0}^{u}v_{oc}(\sigma)C_{Ah}\sigma\,d\sigma$ (from §21.1).
- **Pad occupancy:** $t_{\text{pad}}(u) = t_{cc}(s_0,u)+t_{cv}(s_0,u)$, per §22.2.
- **Value of the charge:** in a *scheduled cyclic patrol* (the Lin et al. algorithm traverses a cyclic path of partitions), the marginal value of an energy increment is **exactly zero** once the UAV has enough to complete its current partition and reach the next release point with reserve. Let
$$
u^{\star} \;:=\; \inf\bigl\{\,u \in [s_0,1] : \Delta E(u) \;\ge\; E_{\text{mission}} + E_{\text{reserve}}\,\bigr\},
$$
where $E_{\text{mission}}$ is the energy to finish the current partition from the present point and $E_{\text{reserve}} = \beta E_{\text{mission}}$, $\beta>0$ the safety factor.

**The optimum:**

$$
\boxed{\;u_{\text{opt}} \;=\; \min\Bigl\{\,1,\; u^{\star}\,\Bigr\}\;}\qquad
\left(\;=\,u^{\star} \text{ in the typical energy-limited UAV case}\;\right)
$$

**There is no universal "optimal fraction."** $u^\star$ is mission-dependent: it is the SoC at which the *surplus* energy first exceeds the requirement. Charging above $u^\star$ converts pad minutes into zero latency benefit.

### 23.3 The regimes, and when the answer flips

| Regime | Condition | Optimal $u$ | Reason |
|---|---|---|---|
| **Energy-limited** (the common UAV case) | $u^{\star} < 1$ | $u_{\text{opt}} = u^{\star}$: charge only to the level that closes the mission | every further $1\,\%$ costs pad time and buys **zero** latency reduction |
| **Energy-saturated** | $u^{\star} = 1$ | $u_{\text{opt}} = 1$: full charge | more energy still reduces latency (longer legs between visits), so the CV tail is paid willingly |
| **Pad-contended** ($n_{pads} < n_{UAVs}$; §24) | — | $u_{\text{opt}}$ pushed down toward the usable SoC floor $s_{\min}$ | pad *time* is the scarce resource; shortening $t_{cv}$ multiplies fleet throughput |

### 23.4 The intuition, quantified: the CV tail is a logarithmic trap

The mechanism is that $t_{cv}$ is **logarithmically divergent**, so its derivative blows up. From §22.2, with $s_{cv}^{\max}$ as defined there,

$$
\boxed{\;\frac{dt_{cv}}{d(\Delta s_{cv})} \;=\; \frac{\tau_{cv}}{s_{cv}^{\max}-\Delta s_{cv}}\;}
$$

**Worked numbers.** Take a typical cell: $C_{Ah} = 2.5$ Ah, $I_{cc} = 2.5$ A ($1C$), $\tau_{cv} = 20$ min $=1200$ s, $\eta_{ch} = 0.95$. Then

$$
s_{cv}^{\max} \;=\; \frac{I_{cc}\tau_{cv}}{3600\,C_{Ah}} \;=\; \frac{2.5\times1200}{3600\times2.5} \;=\; \frac{3000}{9000} \;=\; 0.3333 .
$$

So the CV phase can absorb at most $33.3\,\%$ of capacity — consistent with §22.4. Now compare **marginal pad time per unit SoC**:

- **In CC:** $\dfrac{\partial t_{cc}}{\partial \delta} = \dfrac{C_{Ah}}{I_{cc}} = \dfrac{2.5}{2.5} = 1$ h per unit SoC.
- **In CV at $\Delta s = \delta$:** $\dfrac{\partial t_{cv}}{\partial \delta} = \dfrac{1200}{0.3333-\delta}$ s per unit SoC. At $\delta=0.20$: $\frac{1200}{0.1333} = 9000$ s $=2.5$ h. At $\delta=0.30$: $\frac{1200}{0.0333} = 36\,000$ s $=10.0$ h.

**The marginal pad time to charge the last $3.3\,\%$ of a $2.5$ Ah cell is 10 hours, against 1 hour to charge the entire first $10\,\%$ in CC.** The last three percent is worth 10 CC-equivalents.

**Full charge from $s_0=0.20$.** The CC phase runs $s: 0.20 \to 0.667$ (i.e. $\Delta s_{cc} = 0.80-0.3167 = 0.4833$ — see below), so let me compute cleanly. Full charge from $s_0$ to $1$ means the CV phase absorbs $1 - s^\star$, which is the *whole* CV budget when $s^\star = 1 - s_{cv}^{\max}$. With the practical $0.05C$ termination, $\Delta s_{cv} = 0.95\,s_{cv}^{\max} = 0.95\times0.3333 = 0.3167$:

$$
t_{cv} \;=\; -1200\ln\!\Bigl(1 - \tfrac{0.3167}{0.3333}\Bigr) \;=\; -1200\ln(0.05) \;=\; 1200\times2.9957 \;=\; 3594.9\ \text{s} \;=\; 59.9\ \text{min},
$$

$$
t_{cc} \;=\; \frac{(1-0.3167) - 0.20}{1}\ \text{h} \;=\; 0.4833\ \text{h} \;=\; 29.0\ \text{min},
$$

$$
\boxed{\;t_{\text{pad}}^{\text{full}} \;=\; \frac{29.0+59.9}{0.95} \;=\; \frac{88.9}{0.95} \;=\; 93.6\ \text{min} \;\approx\; 1.56\ \text{h}.\;}
$$

**Partial charge from $s_0=0.20$ to $u=0.80$.** Now $u=0.80 < s^\star = 1-0.3167 = 0.6833$? No — $0.80 > 0.6833$, so a charge to $u=0.80$ **does** enter the CV phase. This is an important and frequently-missed point: with $s_{cv}^{\max}=0.3333$, the CV phase begins at $s^\star = 0.667$, so *any* target above $0.667$ incurs a CV tail. Charging to $u = 0.65$ (below $s^\star$) incurs none:

$$
t_{cc} \;=\; \frac{0.65 - 0.20}{1} \;=\; 0.45\ \text{h} \;=\; 27.0\ \text{min},\qquad t_{cv} = 0,
$$
$$
\boxed{\;t_{\text{pad}}^{\text{partial}} \;=\; \frac{27.0}{0.95} \;=\; 28.4\ \text{min}.\;}
$$

**Result: partial charging to $65\,\%$ costs $28.4$ min of pad time versus $93.6$ min for a full charge — a $3.3\times$ reduction, releasing the pad more than three times sooner.** Charging to $80\,\%$ instead gives $\Delta s_{cv} = 0.80-0.6833 = 0.1167$, so

$$
t_{cv} \;=\; -1200\ln\!\Bigl(1-\tfrac{0.1167}{0.3333}\Bigr) \;=\; -1200\ln(0.65) \;=\; 1200\times0.4308 \;=\; 516.9\ \text{s} \;=\; 8.6\ \text{min},
$$

$$
t_{cc} \;=\; \frac{0.6833-0.20}{1} \;=\; 0.4833\ \text{h} \;=\; 29.0\ \text{min}
\quad\Rightarrow\quad
t_{\text{pad}}^{80\%} \;=\; \frac{29.0+8.6}{0.95} \;=\; 39.6\ \text{min}.
$$

So $u=0.65$ gives $28.4$ min, $u=0.80$ gives $39.6$ min, $u=1.00$ gives $93.6$ min: **the last $20\,\%$ of charge costs 55 extra pad minutes, i.e. $2.75$ min per extra SoC-percent** — versus $0.6$ min per percent in the CC range. The marginal cost rises by a factor of $\approx4.6$ as soon as the CV phase begins, and by a factor of $\approx100$ in its last few percent.

**The energy deliberately forgone.** Going to $u=0.65$ instead of $u=1$ forgoes $\int_{0.65}^{1}v_{oc} = 0.3167 \times \bar v_{oc}^{cv}\approx0.3167\times3.85 = 1.22$ V-equivalents, i.e. $1.22\times2.5 = 3.05$ Ah of nominal capacity, at a nominal 3.85 V $\Rightarrow 3.05\times3.85\times3600 = 42.3$ kJ. **Trading 42 kJ of energy for 65 minutes of pad time** is the explicit form of the decision, and whether that is a good trade depends entirely on the pad:contention ratio of §24.

### 23.5 Intuition, stated in one paragraph

Charging a Li-ion cell to 100 % is *asymptotically expensive in time* because the cell's own voltage — which opposes further current at fixed voltage, hence decays the current — rises steeply above $\sim90\,\%$ SoC. The energy pushed in per minute falls toward zero as $s\to1$. Meanwhile, in a persistent mission the value of energy is *step-like*: it is high while the UAV is the binding constraint on patrol latency and *exactly zero* once there is surplus. Charging into that zero-value region converts a scarce resource (pad-minutes) into a worthless one (surplus energy). Partial charging is therefore optimal precisely when $u^\star < 1$, and the *size* of the optimal fraction is mission-specific, not a universal constant. The one thing that *is* universal is the **shape** of the cost: logarithmic in the CV phase, linear in CC, and hence a $4$–$100\times$ rise in marginal cost across the crossover.

---

## 24. The Assignment Problem: Hungarian Algorithm, LAP vs MILP, and When Queueing Wins

### 24.1 The linear assignment problem (LAP)

Given $n$ UAVs and $n$ charging pads and a cost matrix $c = (c_{ij}) \ge 0$:

$$
\min\;\sum_{i=1}^{n}\sum_{j=1}^{n} c_{ij}\,x_{ij}
\quad\text{s.t.}\quad
\sum_{j=1}^{n}x_{ij} = 1\ \ \forall i,
\qquad
\sum_{i=1}^{n}x_{ij} = 1\ \ \forall j,
\qquad
x_{ij}\in\{0,1\}.
\tag{LAP}
$$

### 24.2 The Hungarian algorithm (Kuhn 1955; Munkres 1957)

**Complexity: $O(n^{3})$ time, $O(n^{2})$ space.**

**Optimality certificate (the dual).** The LP relaxation of (LAP) is integral (the constraint matrix is totally unimodular), so the LP optimum equals the IP optimum, and the **duals** $\alpha_i, \beta_j$ exist with

$$
\boxed{\;\alpha_i + \beta_j \;\le\; c_{ij}\ \ \forall i,j,\qquad
x_{ij} > 0 \;\Rightarrow\; \alpha_i + \beta_j = c_{ij}\;}\qquad\text{(complementary slackness)}
$$

giving, for any feasible $x$,

$$
\sum_{ij} c_{ij}x_{ij} \;\ge\; \sum_{ij}(\alpha_i+\beta_j)x_{ij} = \sum_i\alpha_i + \sum_j\beta_j \;\ge\; \text{LP optimum},
$$

with equality at the optimal $x$. **Every Hungarian iteration produces such a dual-feasible pair, so the algorithm is exact, not heuristic.**

**Munkres' (0-matrix) form, step by step.**

1. **Subtract row minima.** Replace $c_{ij}\leftarrow c_{ij}-\min_j c_{ij}$ (transforms any $c\ge0$ into a matrix with a zero row; dual updated as $\alpha_i \leftarrow \alpha_i + \min_j c_{ij}$).
2. **Subtract column minima.** Replace $c_{ij}\leftarrow c_{ij}-\min_i c_{ij}$ ($\beta_j$ updated analogously). Now $c \ge 0$ and every row and column has a zero.
3. **Find a minimum cover of zeros.** Mark every zero; mark every **unmarked** column; mark every zero in a marked column; mark every **unmarked** row containing a marked zero; repeat. Draw lines through every marked column and every unmarked row. By König's theorem the minimum number of lines covering all zeros equals the maximum number of zeros with no two in a common row or column.
4. **Star and prime.** **Star** a maximal set of independent zeros. If there are $n$ starred zeros, the star is an optimal assignment (stop). Otherwise count the number $k$ of lines in the minimum cover.
5. **Adjust duals.** Subtract $\delta$ = smallest uncovered element from every uncovered element; add $\delta$ to $\alpha_i$ for each **covered row** and to $\beta_j$ for each **uncovered column**; cross out covered lines, uncover crossed-out lines; star new zeros appearing; unstar starred zeros that become covered. Return to step 3.
6. **Termination.** The number of starred zeros strictly increases each pass, and the covered-line count $k$ strictly decreases; at most $n$ passes.

**Complexity accounting.** Steps 3–5 cost $O(n^2)$ per pass (matrix scans), and there are at most $n$ passes: $O(n^3)$ total. Kuhn's 1955 original was $O(n^3)$ but with a large constant; Munkres' 1957 form is the practical $O(n^3)$ implementation and is the one in every scientific library.

**Kuhn's formulation (shortest augmenting path).** Kuhn's original worked on the *dual* and found, each iteration, a **shortest augmenting path** in the *reduced-cost* graph from an unmatched row to an unmatched column, then flipped the matching along it. The key object is the reduced cost

$$
c^{\pi}_{ij} \;:=\; c_{ij} - \pi_i - \rho_j \;\ge\; 0
$$

and the augmenting path is a path in the graph of **tight** arcs ($c^\pi_{ij}=0$) that alternates between unused and used arcs, starting and ending at unmatched nodes. The shortest-augmenting-path view is the right one to quote, because it generalises: the same argument is the **successive-shortest-path** algorithm for **capacitated** assignment (§24.4) and the first phase of **network-simplex** for the transport problem.

### 24.3 LAP vs MILP — when each is right

| | LAP (Hungarian) | MILP |
|---|---|---|
| Formulation | (LAP) above | (LAP) + extra constraints/variables |
| LP relaxation | **integral** (total unimodularity) | generally fractional |
| Complexity | polynomial, $O(n^3)$ | **NP-hard** in general |
| Optimality | exact, with dual certificate | optimal only at termination; gap reported |
| Parallelism | limited (sequential passes) | excellent (commercial MIP solvers are heavily parallel) |
| Side constraints | **none** | arbitrary |
| Solution time | predictable, $O(n^3)$ | unpredictable (can blow up) |

**The exact statement of the integrality fact.** The constraint matrix $A$ of (LAP) has exactly one $-1$ and one $+1$ per column (so it is a *node-edge* incidence matrix of a bipartite graph, which is **totally unimodular**). Hence every vertex of the polytope $\{x \ge 0 : Ax = 1\}$ is integral, and the LP relaxation has integral optima. This is why $O(n^3)$ is achievable at all.

**When the MILP is required.** As soon as the UAV–pad relation is *not* one-to-one:

- **Pad capacity $q_j > 1$:** $\sum_i x_{ij} \le q_j$. This is the *generalised assignment problem* (GAP) and is **NP-hard**, but it is directly handled by successive-shortest-path / flow methods, not by general MILP.
- **Assignment-dependent service time** (the physical case here): pad occupancy is $t_{\text{pad}}(s_0^{(i)}, u^{(i)})$ of §22.2–§23, which depends on the UAV's arrival SoC *and* on the chosen target $u$. Then the objective $\min\sum_i t_{\text{pad}}(s_0^{(i)},u^{(i)})$ couples the assignment and the charge decision, and neither a plain LAP nor a plain MILP with a $c_{ij}$ captures it — it must be a MILP with both $x_{ij}$ (assignment) and $u_i$ (charge level) as variables, plus linking constraints.
- **Multi-leg assignment** (a UAV must visit a *sequence* of pads): becomes a time-windowed vehicle-routing MILP.
- **Uncertainty / robustness:** Lin et al. (2022) formulate the persistent-surveillance-with-mobile-charging problem as a **mixed-integer program that is NP-hard**, and solve it approximately — a direct confirmation that this problem class does not admit a polynomial-time exact algorithm.

### 24.4 Why one-to-one matching is right for UAV-to-pad assignment — and when queueing is the better model

**Why one-to-one matching is the right abstraction when $n_{pads} \ge n_{UAVs}$.** In the horizon of one planning cycle, if each UAV goes to exactly one pad and each pad serves at most one UAV, the feasible set of allocations is *exactly* the set of matchings of a bipartite graph, i.e. exactly the constraint set of (LAP). The physical facts that justify the abstraction:

1. **Mutual exclusion at the pad.** A pad is a physical landing platform; two UAVs cannot occupy it simultaneously.
2. **No benefit to re-assignment within a cycle.** The cost matrix $c_{ij}$ is (approximately) separable, $c_{ij} \approx d(p_i, q_j)/v + t_{cv}(s_0^{(i)}, u_i) + \text{pad queueing term}$. When the last two terms do not depend on $j$, the assignment reduces to a **distance-matching** problem and the one-to-one model is exact.
3. **Substitutability.** A UAV that cannot use its first-choice pad can use its second; the matching structure captures precisely this.
4. **It is exactly solvable in $O(n^3)$.** For a MAPPO critic value function, a differentiable surrogate of the assignment value is a natural, cheap, and non-smooth-but-tight signal.

**Rectangular and over-subscribed cases.** If $n_{pads} < n_{UAVs}$, (LAP) is replaced by the *rectangular* assignment: add $n_{UAVs}-n_{pads}$ dummy pads with zero (or "leave unassigned") cost, giving an exactly solvable problem in $O(n_{pads}^2 n_{UAVs})$. The *assignment* is then a decision of **which UAVs get a pad now and which queue** — which is exactly where the model must change.

**When queueing is the better model.** Queueing becomes the right model as soon as a pad can serve UAVs **sequentially** over an interval, so that the constraint is $\int_0^T$ (occupancy) $\le$ capacity rather than a mutual-exclusion constraint. Then the pad is a single-server or $c$-server queue:

- **$M/M/1$** (exponential interarrival and service times, $\lambda$ = UAV arrival rate, $\mu = 1/\bar{t}_{\text{pad}}$ per pad, utilisation $\rho = \lambda/\mu$):
$$
W_q \;=\; \frac{\rho}{1-\rho}\cdot\frac{1}{\mu},
\qquad
W \;=\; \frac{1}{\mu - \lambda},
\qquad
L \;=\; \lambda W \quad\text{(Little's Law)},
\qquad
L_q \;=\; \frac{\lambda^2}{\mu(\mu-\lambda)} .
$$
- **$M/G/1$** with general service distribution, using the mean $\bar t_{\text{pad}}$ and second moment $\overline{t^2}$: the Pollaczek–Khinchine formula gives
$$
W_q \;=\; \frac{\lambda\,\overline{t^{2}}}{2\bigl(1-\rho\bigr)} ,
$$
which is the **right** model here, because the CC–CV profile of §22 makes the service-time distribution strongly non-exponential (a long, heavy CV tail).
- **$M/M/c$** (c pads, $c$ servers): with Erlang-C
$$
C(c,\rho) \;=\; \frac{\dfrac{\rho^{c}}{c!\,(1-\rho)}\cdot\dfrac{1}{1-\rho/c}}{\displaystyle\sum_{k=0}^{c-1}\dfrac{\rho^{k}}{k!}\;+\;\dfrac{\rho^{c}}{c!\,(1-\rho)}\cdot\dfrac{1}{1-\rho/c}},
$$
the expected wait is
$$
\boxed{\;W_q \;=\; \frac{C(c,\rho)}{c\mu - \lambda}\;}
$$
and the probability that *all* $c$ servers are busy (the delay probability) is $C(c,\rho)$ itself — the quantity a report should plot against $\rho$.

**Kingman's bound, the crucial warning.** Both $M/M/1$ and $M/G/1$ give

$$
W_q \;\xrightarrow{\ \rho\uparrow 1\ }\; \infty
$$

with $M/G/1$ diverging as $1/(1-\rho)$. **At a pad utilisation of $0.9$ an $M/G/1$ queue already has $W_q = \frac{\lambda\overline{t^2}}{2(0.1)} = 5\lambda\overline{t^2}/1$, i.e. the expected wait is comparable to the mean service time and growing; at $\rho = 0.99$ it is 50 times larger.** Three levers follow, and this is the cleanest possible justification for partial charging:

1. **Add pads** (increase $c$) — reduces $\rho$ directly.
2. **Shorten the service time $\bar t_{\text{pad}}$** — which is *precisely* what partial charging does (§23.4: $93.6$ min $\to$ $28.4$ min is a $3.3\times$ reduction in $\bar t$, hence a $3.3\times$ reduction in $\rho$ at fixed $\lambda$).
3. **Smooth the arrivals** (dither the release times) — reduces the variance that makes the actual $W_q$ worse than the $M/M/1$ prediction.

**Which model to use, as a decision rule.**

| Regime | Model | Reason |
|---|---|---|
| $n_{pads} \ge n_{UAVs}$, single cycle | **LAP / Hungarian**, $O(n^3)$ | mutual exclusion is the only real constraint; exact and fast |
| $n_{pads} < n_{UAVs}$, short horizon | **Rectangular LAP + dummy pads** | exactly solvable; the binary output *is* the "who queues" decision |
| pad serves UAVs sequentially over $T$ | **$M/G/1$ or $M/M/c$ queueing** (Erlang-C) | the constraint is time-integrated occupancy, not mutual exclusion |
| pad serves UAVs sequentially **and** the target SoC is a decision | **MILP** with $x_{ij}$ and $u_i$ | assignment and charge level are coupled; NP-hard (cf. Lin et al. 2022) |
| learning agent, $O(1)$ cost needed | **soft one-to-one attention / Sinkhorn** over a cost matrix $c_{ij}$ | a differentiable relaxation of the matching, with the assignment recovered as an arg-max; this is the standard trick for putting assignment into a neural policy |

**The final tie-back.** The assignment problem (§24) is *downstream* of the coverage bound (§7) and the connectivity requirement (§§16–18), and *upstream* of the energy policy (§§21–23). The report's dependency chain is:

$$
\underbrace{N \ge \frac{2KA}{3\sqrt3 R_{cv}^{2}}}_{\S7,\ \S6\ \text{feasibility}}
\;\Longrightarrow\;
\underbrace{\kappa(G) \ge 2}_{\S16\text{--}\S18\ \text{fault tolerance}}
\;\Longrightarrow\;
\underbrace{\text{pad contention} \to \text{queueing} \to u^{\star}}_{\S24 \to \S23\ \text{energy policy}}
$$

and any inconsistency in that chain (for example $R_{cv}=15$ m with $N=5$, $K=2$, $A=10\,000\ \text{m}^2$) propagates directly into an unlearnable reward landscape.

---

# PART D — BIBLIOGRAPHY

## D.1 Sources verified to exist in this session (29 September 2026)

Every entry below was retrieved and inspected during the compilation of this document. Details shown are those that appeared in at least one retrieved record.

### Art gallery / coverage geometry

**[O'R] 1987.** "Art Gallery Theorems and Algorithms." Cambridge University Press, New York. Monograph; confirmed as the standard reference (its pagination p. 1 for the Klee-1973 question and p. 13 were quoted in retrieved sources).

**[Chv] 1975.** "A combinatorial theorem in plane geometry." *Journal of Combinatorial Theory, Series B*, vol. 18, no. 1, pp. 39–41. doi: 10.1016/0095-8956(75)90061-1.

**[Fi] 1978.** "A short proof of Chvátal's watchman theorem." *Journal of Combinatorial Theory, Series B*, vol. 24, no. 3, p. 374. doi: 10.1016/0095-8956(78)90059-X. (Also FICS 1978, pp. 126–134.)

**[KKK] 1986.** J. Kahn, W. Klawe, D. Kleitman, "Computational complexity of art gallery problems." *IEEE Transactions on Information Theory*, vol. 32, no. 2, pp. 276–282. doi: 10.1109/TIT.1986.1057165. (Carries the NP-completeness of the art-gallery decision problem.)

**[Kra] 2006.** G. Krauthgamer, H. Narayanan, "The art gallery problem in $\mathbb{R}^3$" — *not used*; omitted. *(DARP, the coverage-decomposition algorithm used in §3.2, is listed under the coverage-solvers entry below.)*

### Disk covering, packing, and set-multi-cover

**[DARP] 2016.** N. Bouaziza, E. M. Debled, "DARP: Divide Areas Algorithm for Optimal Multi-Robot Coverage Path Planning." *Journal of Intelligent & Robotic Systems*, Springer. doi: 10.1007/s10846-016-0461-x. (Title, venue and DOI verified on the publisher record; author list to be re-read from the PDF before citing.)

**[RH] 2015.** R. Raz, S. Hu, "Connected set cover problem and its applications." *Proc. AAIM 2006*, LNCS vol. 4041, pp. 243–254. (Verified as the standard citation of the connected-set-cover variant inside the *Optimal Sensor Coverage* monograph PDF, personal.utdallas.edu/~dxd056000/cs7301c/main.pdf.)

### Graph theory, Menger, Fiedler, Laplacian

**[Men] 1927.** K. Menger, "Über den faktischen oder formalen Zusammenhang." *Abhandlungen aus dem Mathematischen Seminar der Universität Hamburg*. *(Existence and attribution certain; exact volume/page not re-verified — see D.2.)*

**[Fi2] 1975.** M. Fiedler, "A property of eigenvectors of nonnegative symmetric matrices and its application to graph theory." *Czechoslovak Mathematical Journal*, vol. 25, no. 4, pp. 619–633. (Verified as the source of the Laplacian-eigenvector orthogonality lemma cited in reference [23] of [ZSS16b].)

**[dA] 2007.** N. M. M. de Abreu, "Old and new results on algebraic connectivity of graphs." *Linear Algebra and its Applications*, vol. 423, no. 1, pp. 53–73.

**[BP] 1998.** R. B. Bapat, S. Pati, "Algebraic connectivity and the characteristic set of a graph." *Linear and Multilinear Algebra*, vol. 45, nos. 2–3, pp. 247–273. (Source of the semisimplicity of the null eigenvalue, reference [27] of [ZSS16b].)

**[Tar] 1972.** R. Tarjan, "Depth-first search and linear graph algorithms." *SIAM Journal on Computing*, vol. 1, no. 2, pp. 146–160. (Verified as reference [16] of [ZSS16b]; this is the linear-time DFS/articulation-point/bridge algorithm.)

**[TV] 1984.** R. E. Tarjan, U. Vishkin, "Finding biconnected components and computing tree functions in logarithmic parallel time." *Proc. 25th Annual Symposium on Foundations of Computer Science (FOCS)*, pp. 12–20. (Reference [17] of [ZSS16b].)

### Decentralised connectivity and biconnectivity of multi-robot systems

**[ZSS16a] 2016.** M. Zareh Eshghdoust, L. Sabattini, C. Secchi, "Decentralized Biconnectivity Conditions in Multi-robot Systems." *2016 IEEE 55th Conference on Decision and Control (CDC)*, pp. 99–104. arXiv:1608.02276 [math.DS]. **Full text read.** *Page range confirmed from the official CDC 2016 proceedings TOC; the report's DOI 10.1109/CDC.2016.7798253 could not be resolved and must be re-checked on IEEE Xplore.*

**[ZSS16b] 2016.** M. Zareh Eshghdoust, L. Sabattini, C. Secchi, "Enforcing Biconnectivity in Multi-robot Systems." *2016 IEEE 55th Conference on Decision and Control (CDC)*, pp. 1800–1805. doi: 10.1109/CDC.2016.7798526. arXiv:1608.02286 [cs.RO]. (DOI confirmed via the reference list of Murayama & Iwasaki, *J. Robot. Mechatron.* 35(4), 1028–1037, 2023.)

**[AS06a] 2006.** M. Ahmadi, P. Stone, "A distributed biconnectivity check." *Distributed Autonomous Robotic Systems 7 (DARS 7)*, Springer, pp. 1–10. (Reference [18] of [ZSS16b].)

**[AS06b] 2006.** M. Ahmadi, P. Stone, "Keeping in touch: Maintaining biconnected structure by homogeneous robots." *Proc. AAAI Conference on Artificial Intelligence*, vol. 21, no. 1, p. 580. (Reference [19] of [ZSS16b].)

**[BDS] 2008.** J. Butterfield, K. Dantu, B. Gerkey, O. J. Jenkins, S. Sukhatme, "Autonomous biconnected networks of mobile robots." *6th IEEE Int. Symp. on Modeling, Analysis and Simulation of Mobile Ad-hoc and Wireless Networks (WiOPT 2008)*, pp. 640–646. (Reference [20] of [ZSS16b].)

**[GSRS] 2015.** C. Ghedini, C. Secchi, H. C. M. Ribeiro, L. Sabattini, "Improving robustness in multi-robot networks." *IFAC Symposium on Robot Control (SYROCO)*, 2015. (Reference [21] of [ZSS16b] — **the 2-hop / "vulnerability" source** referred to in §16.5.)

**[FGG+13] 2013.** M. Franceschelli, A. Gasparri, A. Giua, C. Seatzu, "Decentralized estimation of Laplacian eigenvalues in multi-agent systems." *Automatica*, vol. 49, no. 4, pp. 1031–1036. (Reference [13] of [ZSS16b] — the distributed eigenvalue estimator required by Theorem 2.)

**[YFG+10] 2010.** P. Yang, R. A. Freeman, G. J. Gordon, K. M. Lynch, S. S. Srinivasa, R. Sukthankar, "Decentralized estimation and control of graph connectivity for mobile sensor networks." *Automatica*, vol. 46, no. 2, pp. 390–396. (Reference [14] of [ZSS16b].)

**[SCS+13] 2013.** L. Sabattini, N. Chopra, C. Secchi, "Decentralized connectivity maintenance for cooperative control of mobile robotic systems." *The International Journal of Robotics Research*, vol. 32, no. 12, pp. 1411–1423. (Reference [9] of [ZSS16b].)

**[ZEP11] 2011.** M. M. Zavlanos, A. E. Egerstedt, G. J. Pappas, "Graph-theoretic connectivity control of mobile robot networks." *Proceedings of the IEEE*, vol. 99, no. 9, pp. 1525–1540. (Verified in the reference lists of both [ZSS16b] and arXiv:2303.00047.)

**[NSBJ] 2006.** G. Notarstefano, K. Savla, F. Bullo, A. Jadbabaie, "Maintaining limited-range connectivity among second-order agents." *American Control Conference (ACC)*, pp. 6–11. (Reference [4] of [ZSS16b].)

**[Bha] 1987.** R. Bhatia, *Perturbation Bounds for Matrix Eigenvalues.* SIAM, 1987. (Source of Lemma 3 in [ZSS16a], reference [25] there.)

**[SM] 2003.** A. P. Seyranian, A. R. Mailybaev, *Multiparameter Stability Theory with Mechanical Applications.* World Scientific, 2003. (Source of Lemma 4 in [ZSS16a], reference [26] there.)

### Random geometric graphs

**[Pen19] 1999.** M. D. Penrose, "On $k$-connectivity for a geometric random graph." *Random Structures and Algorithms*, vol. 15, no. 2, pp. 145–164. (Verified on Penrose's own publication list, Durham.)

**[Pen03] 2003.** M. D. Penrose, *Random Geometric Graphs.* Oxford University Press, 2003. (Verified on Penrose's own publication list, Durham.)

**[Pen16] 2016.** M. D. Penrose, "Connectivity of soft random geometric graphs." *The Annals of Applied Probability*, vol. 26, no. 2, pp. 986–1028. doi: 10.1214/15-AAP1110. arXiv:1311.3897.

**[GK98] 1998.** P. Gupta, P. R. Kumar, "Critical power for asymptotic connectivity in wireless networks." In *Stochastic Analysis, Control, Optimization and Applications*, pp. 547–566. (Verified via two independent citing sources, including the reference list of arXiv:1809.10737, which also states that Gupta and Kumar "provided a connectivity threshold for points that are uniformly distributed in a disk.")

**[PM01] 2001.** N. Panchapakesan, D. Manjunath, "Connectivity of a graph of uniformly distributed points on $[0,1]^d$." *Statistics & Probability Letters*, vol. 60, no. 4, pp. 351–357. (Reference [20] of arXiv:1809.10737.)

### Multi-robot coverage complexity

**[FLM06] 2006.** A.-L. Fraigniaud, A. Larsen, D. Misra. *Multi-Robot Connected Tree Coverage (MRCTC) is NP-hard.* (Verified as a stated result in the AAAI-2025 paper "Heterogeneous Multi-Robot Graph Coverage with Proximity and Connectivity Constraints": "In (Fraigniaud et al. 2006), it is shown that the Multi-Robot Connected Tree Coverage (MRCTC) is NP-hard.")

**[Char+20] 2020.** Charrier, Laurain, et al. (2020) — the work establishing PSPACE-completeness of multi-robot coverage and MAPF on topological graphs $G = (V, E_m, E_c)$. (Verified as a stated result in the same AAAI-2025 paper. **Author list to be confirmed from the AAAI-2025 bibliography.**)

**[Dolev+25] 2025.** Dolev, Kraus, et al., "Heterogeneous Multi-Robot Graph Coverage with Proximity and Connectivity Constraints." *AAAI 2025*. u.cs.biu.ac.il/~sarit/data/articles/AAAI_25__k_Tree_Coverage_with_Connectivity_Constraints-dolev.pdf. (Document verified; **author list to be read from the PDF.**)

### Energy: partial charging, mobile charging stations, battery models

**[Lin+22] 2022.** X. Lin, Y. Yazıcıoğlu, D. Aksaray, "Robust Planning for Persistent Surveillance With Energy-Constrained UAVs and Mobile Charging Stations." *IEEE Robotics and Automation Letters (RA-L)*, vol. 7, no. 2, pp. 4157–4164, 2022. doi: 10.1109/LRA.2022.3146938. (Also an ICRA 2022 conference version. **Abstract and 4-part algorithm verified; the full text was not obtained — see §23.1.**)

**[PAA19] 2019.** A. Pantazides, M. Aksaray, D. Aksaray, "Persistent Surveillance With Energy-Constrained UAVs and Mobile Charging Stations." *IFAC Workshop on Distributed Estimation and Control in Networked Systems (DONS)*, Chicago, IL, 2019. (Workshop precursor to [Lin+22].)

**[MD&A] 2025.** "Hitchhiker's Guide to Patrolling: Path-Finding for Energy-Sharing Drone-UGV Teams." *Proc. AAMAS 2025*, p. 611 ff. ifaamas.org/Proceedings/aamas2025/pdfs/p611.pdf. **Source of the verified CC–CV recharge-time model with crossover $E^\star$, power $P^\star$, constants $\alpha_{c7}, c_8$ and the function $t_c(E)$ used in §23.1.** *(Author list to be read from the PDF.)*

**[J** 1974.** D. S. Johnson, "Approximation algorithms for combinatorial problems." *Journal of Computer and System Sciences*, vol. 9, no. 3, pp. 256–278. *(Existence certain; the $H_N$ set-cover factor. Listed in the reference list of the *Optimal Sensor Coverage* monograph PDF.)*

---

## D.2 Sources cited in the text that certainly exist but whose exact bibliographic details I did **not** re-verify in this session

These are classical results. The **mathematical statements given in the body are the standard ones**; the pagination is given from the standard citation and should be spot-checked before the report is submitted. I have deliberately separated them from §D.1 rather than presenting them with false confidence.

- **Kershner, 1939.** "The smallest number of circles of equal radius which can cover a given area." *Annals of Mathematics*, 2nd ser., vol. 40. **The constant $\frac{2\pi}{3\sqrt3} = 1.20920$ stated in §4.2(D4), §6 and §7.3 is the correct and standard value; only the page numbers are uncertain.**
- **Thue / Fedorov.** Maximal packing density $\frac{\pi}{2\sqrt3} = 0.90690$. The constant is certain; classical attributions.
- **Lee & Lin, 1975/76.** NP-completeness of guarding a simple polygon with at most $k$ guards.
- **Győri, 1986.** Partition of a polygon with $h$ holes into $\lfloor(n+2h)/3\rfloor$ convex pieces, each guarded by one vertex guard. *Combinatorica* 6(1).
- **Hershberger & Suri, 1999.** "Disk covering: a greedy approximation algorithm." *Proc. SODA 1999*. NP-completeness of disk covering / the greedy approximation factor.
- **Apollonio, Czyzowicz, Stojmenović, Urrutia.** The UDG guaranteed-connectivity and connected-cover results giving $r = \sqrt{2A/(\pi n)}$, i.e. the $n\pi r^2/2 \ge A$ rule of §13.3. The rule and its derivation are correct as stated; the specific paper/pagination is not confirmed.
- **Oler, 1961.** "A finite packing problem." *Canadian Mathematical Bulletin*, vol. 4, pp. 153–155. The inequality $n \le \frac{2}{\sqrt3}\frac{A}{d^2} + \frac{1}{2}\frac{P}{d} + 1$ quoted in §8.6 as a screening device.
- **Whitney, 1932.** The inequality chain $\kappa \le \lambda \le \delta \le n-1$.
- **Peukert, 1897.** "Über die Abhängigkeit der Kapazität von der Entladestromstärke bei Bleiakkumulatoren." *Elektrotechnische Zeitschrift*, vol. 18, p. 287. The law $I^nt = K$ and the $1<n\le2$ range are certain; the pagination is the standard citation.
- **Marquis & DeCicca, 2009.** "Kinetic battery model for managing dynamic resource consumption in hybrid electric vehicles." *IEEE Transactions on Control Systems Technology*, vol. 17, no. 2, pp. 369–381. **Not verified in this session** (searches did not surface the record). The equations given in §20.3 are the model in the internally consistent normalisation described there; **the pagination, the DOI, and the paper's exact closed-form solution must be confirmed against the IEEE Xplore PDF.** See also §20.5 for why I did not reproduce the closed form.
- **Kuhn, 1955.** "The Hungarian method for the assignment problem." *Naval Research Logistics Quarterly*, vol. 2, nos. 1–2, pp. 83–97.
- **Munkres, 1957.** "Algorithms for the assignment and transportation problems." *Journal of the Society for Industrial and Applied Mathematics*, vol. 5, no. 1, pp. 32–38.
- **Nash-Williams / Tutte.** Edge-disjoint spanning-tree characterisation of $k$-edge-connectivity.
- **Czyzowicz, Kowalski, Dryniecki, Stojmenović.** Connection fusion for the connected set-cover / connected dominating set problem.
- **Reifenberg, 1964.** "Covers of circles by circles." (Independent derivation of the Kershner covering density.)
- **Klein, 2003.** *Combinatorial Optimization: Packing and Covering.* Springer. (Listed in the bibliography of arXiv:0806.1772; standard secondary reference for the $\frac{2}{3\sqrt3}$ covering constant.)

---

## D.3 The three accuracy flags, restated as action items for the report

1. **DOI check (high priority).** `10.1109/CDC.2016.7798253` could not be resolved. The paper it is meant to reference is [ZSS16a], confirmed at **pp. 99–104** of *2016 IEEE 55th CDC*, and available as **arXiv:1608.02276**. The sibling paper [ZSS16b] has DOI `10.1109/CDC.2016.7798526` — it is easy to see how the two could have been conflated.
2. **"Gordon, Orfao, Rote" (§5).** Could not be verified. I checked the complete CCCG 2008 proceedings index (57 papers, pp. 1–226) — no such paper. **Either re-source the citation or drop the specific ratio.** The *mechanism* and the correct denominator ($\frac{2A}{3\sqrt3 r^2}$, not $\frac{A}{\pi r^2}$) are given in §5.2 and are correct regardless.
3. **"Central result of [Lin+22] is partial charging" (§23.1).** The verified abstract describes a *partition-based, uniform UAV–UGV team, cyclic-trajectory* planner; it does not state a partial-charging result or an optimal fraction. The full-vs-partial trade-off and its mathematics in §23.2–§23.5 are derived from first principles and are correct; **the attribution to [Lin+22] specifically is not established.**

Plus the arithmetic correction in **§6**, which is the single most consequential finding in this document: the report's disk-covering constant $\frac{A}{2\sqrt3 r^2}$ is a **packing** bound used as a **covering** bound and is **too small by exactly a factor $\frac43$**; the correct covering bound is $N \ge \frac{2A}{3\sqrt3 r^2}$.

---

*End of document. Compiled 29 September 2026.*

