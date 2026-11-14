# 02 — FEASIBILITY ANALYSIS AND CORRECTED PARAMETERS

**This document is the highest-value thing in the folder.** It contains a proof
that the parameter table in `Mlawn-midsem-tex.tex` makes the stated objective
physically unachievable, and a corrected table that fixes it.

Scripts: `feasibility_check.py`, `parameter_search.py`, `scenario_compare.py`
(all in this folder, all runnable, all outputs reproduced below).

---

## 1. THE ERROR

`Mlawn-midsem-tex.tex`, Table IV:

| Parameter | Value |
|---|---|
| Operating region $\Omega$ | $100\times100$ m$^2$ |
| IoT sensors $M$ | 20 |
| Active UAVs $N$ | 5 |
| Coverage radius $R_{\mathrm{cov}}$ | **15 m** |
| Coverage target $K$ | 2 |

The paper's Sec. III-F states the primary service condition as
$n_d(t)\ge K$ for all $d$, and Sec. III-M states the objective as minimising
expected under-coverage $J_{\mathrm{out}}$.

**These are incompatible.** With $R_{\mathrm{cov}}=15$ m the swarm *cannot*
satisfy $K=2$ for any controller.

---

## 2. THE COUNTING BOUND

**Theorem.** If $N$ UAVs each covering a disk of radius $R_{\mathrm{cov}}$
achieve $K$-coverage of all $M$ sensors uniformly distributed in a region of
area $A$, then necessarily

$$N\,\pi R_{\mathrm{cov}}^{2}\;\ge\;K\,A
\qquad\Longleftrightarrow\qquad
\boxed{\;R_{\mathrm{cov}}\;\ge\;\sqrt{\frac{KA}{\pi N}}\;}$$

**Proof.** $K$-coverage of all $M$ sensors requires at least $KM$ incidence
pairs with $x_{id}=1$, hence $\sum_{d=1}^{M} n_d \ge KM$. The sensor field has
density $\sigma_d = M/A$. A UAV at position $\mathbf p$ covers a disk of area
$\pi R_{\mathrm{cov}}^2$, containing on average $\sigma_d\pi R_{\mathrm{cov}}^2$
sensors. Summing over $N$ UAVs, $\mathbb{E}[\sum_d n_d] = N(M/A)\pi R_{\mathrm{cov}}^2$.
Requiring this to reach $KM$:

$$\frac{N(M/A)\pi R_{\mathrm{cov}}^2}{KM}\;\ge\;1
\iff
\frac{N\pi R_{\mathrm{cov}}^2}{A}\;\ge\;K
\qquad\blacksquare$$

**Packing-corrected form.** Disks cannot tile the plane. The densest packing of
congruent disks has density

$$\delta=\frac{\pi}{2\sqrt3}\approx0.9069$$

so a stricter necessary condition is

$$R_{\mathrm{cov}}\;\ge\;\sqrt{\frac{KA}{\delta\,\pi N}}$$

---

## 3. EVALUATION ON THE PAPER'S PARAMETERS

$$R_{\mathrm{cov}}\;\ge\;\sqrt{\frac{2\times 10\,000}{\pi\times 5}}
=\sqrt{1273.24}=\mathbf{35.68\ \text{m}}
\qquad\text{(counting)}$$

$$R_{\mathrm{cov}}\;\ge\;\sqrt{\frac{20\,000}{0.9069\,\pi\times 5}}
=\mathbf{37.47\ \text{m}}
\qquad\text{(packing-corrected)}$$

The paper uses **15 m** — **2.38× too small**.

| Quantity | Value |
|---|---|
| Area required, $KA$ | 20 000 m² |
| Area supplied, $N\pi R_{\mathrm{cov}}^2$ | 3 534 m² |
| **Ratio** | **0.177** |
| Expected coverage slots | 7.07 |
| Required slots, $KM$ | 40 |
| **Fraction achievable** | **17.7 %** |

### 3.1 Even single-coverage fails

The theory document (`05_07_...md` §8) sharpens this: the *maximum* coverage
level attainable is

$$K_{\max}=\left\lfloor \frac{N\pi R_{\mathrm{cov}}^2}{KA}\right\rfloor
=\left\lfloor\frac{3534.29}{20000}\right\rfloor=\mathbf{0}$$

So the configuration cannot even **single-cover** all 20 sensors. Best-case
coverage of the *entire region* would need

$$R_{\mathrm{cov}}\;\ge\;\sqrt{\frac{KA}{N\pi}}\bigg|_{K=1}=35.68\ \text{m},$$

and the binding requirement at $K=2$ (accounting for discrete sensor placement)
is **39.24 m**.

### 3.2 Best case does not rescue it

Uniform sensor grids, $R_{\mathrm{cov}}=15$ m:

| Grid | $M$ | Spacing | Max sensors per UAV | Max slots | Need | Verdict |
|---|---|---|---|---|---|---|
| 5×4 | 20 | 20×25 m | 1 | 5 | 40 | INFEASIBLE |
| 4×5 | 20 | 25×20 m | 1 | 5 | 40 | INFEASIBLE |
| 4×4 | 16 | 25×25 m | 1 | 5 | 32 | INFEASIBLE |

One UAV covers at most **one** sensor. This is not a placement failure — it is
geometrically impossible.

---

## 4. WHY THIS MATTERS FOR THE REPORT

With the objective permanently unachievable:

1. $U_t$ is pinned near 1 for **every** policy.
2. The dominant reward term $\lambda_O U_t$ supplies a near-constant gradient.
3. MAPPO, MADDPG, greedy and fixed-formation baselines all score identically.
4. The "learning" part of the study becomes untestable.
5. Every table in Section VI becomes a table of noise.

**An examiner who computes $N\pi R^2 \ge KA$ will find this in about thirty
seconds.** It is the single highest-risk item in the report.

---

## 5. WHICH KNOB TO TURN

Four options, with the arithmetic:

### Option A — increase $R_{\mathrm{cov}}$ ✅ **RECOMMENDED**

| $R_{\mathrm{cov}}$ | expected slots | required | surplus $\sigma$ | verdict |
|---|---|---|---|---|
| 15 m | 7.07 | 40 | 0.18 | infeasible (current) |
| 25 m | 19.63 | 40 | 0.49 | infeasible |
| 35 m | 38.48 | 40 | 0.96 | infeasible (just barely) |
| **36 m** | 40.72 | 40 | **1.02** | feasible at the bound |
| 40 m | 50.27 | 40 | 1.26 | feasible |
| 45 m | 63.62 | 40 | 1.59 | feasible |
| 50 m | 78.54 | 40 | 1.96 | feasible |

The coverage radius is the *natural* knob: it is the physical sensing range of
the UAV, and increasing it does not fight the rest of the design.

### Option B — increase $N$ ❌ REJECT

$$N\;\ge\;\frac{KM}{(M/A)\pi R^2}=\frac{40}{1.414}=28.3
\qquad\text{(packing-corrected: }31.2\text{)}$$

A 29–32 UAV swarm. This (a) destroys the scalability contribution, (b) makes
centralised-critic training intractable, and (c) negates the whole point of
decentralised execution.

### Option C — reduce $M$ ❌ REJECT

At $N=5$, $K=2$, $R_{\mathrm{cov}}=15$ m: $M_{\max}=3$. Too trivial.

### Option D — increase $|\Omega|$ ❌ REJECT

Makes it strictly worse: $\sigma\propto 1/A$.

---

## 6. CONNECTIVITY FEASIBILITY

**Expected edges** in a random geometric graph on $N$ uniform points:

$$\mathbb{E}\bigl[\lvert E\rvert\bigr]=\binom{N}{2}\frac{\pi R_{\mathrm{comm}}^2}{A}$$

For $N=5$, $R_{\mathrm{comm}}=40$ m, $A=10^4$ m²: $\mathbb{E}[|E|]=5.03$, versus
$N-1=4$ needed for connectivity. Marginal. Monte-Carlo says $P(\text{connected})$
is only **0.18** — the paper's own configuration is *usually disconnected*.

**Connectivity threshold radius** (Penrose 1997, $\mathbb{E}[|E|]\sim\tfrac12n\ln n$):

| $N$ | $r_n$ | paper's $R_{\mathrm{comm}}$ |
|---|---|---|
| 5 | 45.6 m | 40 m — **below threshold** |
| 6 | 42.2 m | 40 m |
| 10 | 34.2 m | 40 m — above |
| 20 | 25.9 m | 40 m — well above |

**So both parameters are wrong in the same direction** — coverage too small,
connectivity too small. The configuration is simultaneously infeasible on C1 and
usually failing on C2.

---

## 7. SCENARIO COMPARISON

$\sigma$ = expected coverage slots / required slots (want $\gtrsim1.5$).
$P(\text{conn})$ = Monte-Carlo probability the graph is connected, 8 000 trials.

| scenario | $\|\Omega\|$ | $M$ | $R_{\mathrm{cov}}$ | $R_{\mathrm{comm}}$ | $\sigma$ | $P(\text{conn})$ | $P(\text{conn}\mid$fail$)$ | disk/$\Omega$ |
|---|---|---|---|---|---|---|---|---|
| **S-A as-written** | 10 000 | 20 | 15 | 40 | **0.18** | 0.18 | 0.17 | 7 % |
| S-B bigger radius | 10 000 | 20 | 40 | 50 | 1.26 | 0.46 | 0.40 | 50 % |
| **S-C smaller region** | 3 600 | 20 | 30 | 40 | **1.96** | **0.86** | **0.78** | 79 % |
| S-D smaller region 2 | 3 600 | 20 | 35 | 45 | 2.67 | 0.95 | 0.91 | 107 % |
| **S-E mid ⭐** | 6 400 | 20 | 35 | 45 | **1.50** | **0.63** | **0.56** | 60 % |
| S-F mid alt | 6 400 | 16 | 35 | 45 | 1.50 | 0.63 | 0.56 | 60 % |

Note S-D has $\text{disk}/\Omega=107\%$ — one UAV's coverage disk is larger than
the region, which makes coverage trivial and is not a good scenario.

**S-E is the best choice.** Both constraints are non-trivial:
- $\sigma=1.50$: coverage needs work but is achievable
- $P(\text{conn})=0.63$: connectivity is genuinely marginal
- one UAV's disk is 60 % of the region: partial coverage, not trivial
- after a failure $\sigma'=1.20$ and $P(\text{conn})=0.56$: the reserve helps
  both constraints measurably

---

## 8. RECOMMENDED PARAMETER TABLE

Replace Table IV in the paper with this:

| Parameter | Symbol | Value |
|---|---|---|
| Operating region | $\Omega$ | $80\times80$ m$^2$ |
| Active UAVs | $N$ | 5 |
| Reserve UAVs | $N_R$ | 1 |
| IoT sensors | $M$ | 20 |
| Coverage target | $K$ | 2 |
| Coverage radius | $R_{\mathrm{cov}}$ | **35 m** |
| Communication radius | $R_{\mathrm{comm}}$ | **45 m** |
| Control interval | $\Delta t$ | 1 s |
| Maximum speed | $v_{\max}$ | 5 m/s |
| Safety distance | $d_{\mathrm{safe}}$ | 5 m |
| Battery capacity | $B^{\mathrm{max}}$ | **60 kJ** |
| Hover power | $P_{\mathrm{hover}}$ | 50 W |
| Move power | $P_{\mathrm{move}}$ | 75 W |
| Communication power | $P_{\mathrm{comm}}$ | 10 W |
| Charging pads | $S$ | 2 |
| Charge increment | — | **0.001 per step** |
| Episode length | $T$ | 2000 steps |

Bold entries are the three changes from the current table plus one addition.

### Feasibility check for the new table

$$N\pi R_{\mathrm{cov}}^2=5\pi(35)^2=19\,242\ \text{m}^2\;\ge\;KA=2\times6\,400=12\,800\ \text{m}^2
\qquad\checkmark\ (\sigma=1.50)$$

$$R_{\mathrm{cov}}=35\ \text{m}\;\ge\;\sqrt{\frac{2\cdot6\,400}{0.9069\,\pi\cdot5}}=29.98\ \text{m}\quad\checkmark$$

### Endurance and charging

| Config | Flight (85 W) | Charge 0→1 | ratio | Return at |
|---|---|---|---|---|
| **current** 30 kJ, 0.01/step | 353 s = 5.9 min | 100 s = 1.7 min | **0.28** | 24 % |
| **recommended** 60 kJ, 0.001/step | 706 s = 11.8 min | 1000 s = 16.7 min | **1.42** | 17 % |
| reference 120 kJ, 0.0005/step | 1412 s = 23.5 min | 2000 s = 33.3 min | 1.42 | 13 % |

Real Li-ion at 1C charges in ~60 min against a ~10 min quadrotor endurance →
ratio ≈ 6. The current 0.28 is ~20× too fast; 1.42 is the same order and
conservative. Use the recommended row.

### Time-step resolution

Rule of thumb: at least 10 control steps across the coverage diameter,

$$\frac{2R_{\mathrm{cov}}}{v_{max}\Delta t}\;\ge\;10$$

With $R_{\mathrm{cov}}=35$ m, $v_{max}=5$ m/s, $\Delta t=1$ s: **14 steps** ✓.
So $\Delta t=1$ s is fine — it was $R_{\mathrm{cov}}=15$ m that broke it
(6 steps). No change needed to $\Delta t$.

---

## 9. THE SENTENCE TO ADD TO THE PAPER

Put this in Sec. III-F, immediately after the service condition:

> **Feasibility.** Persistent $K$-coverage is achievable only when the sensing
> radius is large enough for the fleet. A necessary condition is obtained by
> comparing the area available for coverage with the area required: $N$ disks of
> radius $R_{\mathrm{cov}}$ supply $N\pi R_{\mathrm{cov}}^2$, while $K$-coverage
> of a region of area $A$ requires $KA$. Hence $R_{\mathrm{cov}} \ge
> \sqrt{KA/(\pi N)}$; accounting for the $\pi/(2\sqrt3)\approx0.907$ packing
> density of congruent disks gives $R_{\mathrm{cov}} \ge \sqrt{KA/(\delta\pi N)}$.
> Substituting the parameters of Table IV ($A=6400$ m$^2$, $M=20$, $N=5$,
> $K=2$) yields $R_{\mathrm{cov}} \ge 28.5$ m (counting) and $30.0$ m
> (packing-corrected), both satisfied by the chosen $R_{\mathrm{cov}}=35$ m. The
> resulting surplus ratio $\sigma = N\pi R_{\mathrm{cov}}^2/(KA) = 1.50$ leaves
> margin for movement error and for a single-UAV failure, after which
> $\sigma = 1.20$ still exceeds 1.

This is four lines of prose, one equation, and it converts the report's biggest
weakness into a demonstration of rigour. **It is the single best value-for-effort
edit in the entire report.**

---

## 10. REPRODUCING

```powershell
cd Project1\research
python feasibility_check.py     # proves the current table is infeasible
python parameter_search.py      # tests each knob, derives R_cov >= 35.68 m
python scenario_compare.py      # compares 6 scenarios, Monte-Carlo connectivity
```

All three run in under a minute on CPU. Include the outputs as an appendix so
the numbers in the paper are reproducible — that is worth marks on its own.
