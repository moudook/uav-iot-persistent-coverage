# Old Report vs New Report — What Changed (with page citations)

**Old:** `OLD_REPORT/OLD_MIDSEM_REPORT.pdf` (10 pp) — cited as **[O p.X]**
**New:** `Mlawn-midsem-tex.pdf` (33 pp) — cited as **[N p.X]**

Page numbers refer to the internal "Page X of Y" markers in the PDFs (old: "-- n of 10 --", new: "-- n of 33 --").

---

## The one-sentence change

> Old report: "We propose MAPPO for persistent UAV-IoT coverage. Numerical performance claims are intentionally deferred until the proposed experiments are completed" **[O p.1, IX p.9–10]**.
> New report: "Applied to a controlled experimental setup, the framework shows that a hand-designed reactive rule outperforms parameter-shared CTDE MAPPO on this task, and it bounds the reason with controlled arms" **[N p.2]** — gap = **0.298** of persistent coverage, 95% CI **[0.248, 0.349]** **[N p.1, 2, 20–21, 30]**.

---

## 1. The headline: the paper is reframed

| | Old | New |
|---|---|---|
| Framing | MARL framework proposal **[O p.1]** | **Feasibility-certified evaluation methodology** — "the central invention of this work" **[N p.2]** |
| Claims | None "deferred until the experiments are executed" **[O p.9]** | Measured with CIs **[N pp.20–28]** + automated claim audit, 38 items, 0 failing **[N p.1, 28]** |
| Central invention | The MAPPO controller **[O pp.1, 6]** | Certificate + oracle + non-degenerate metrics **[N pp.2, 9, 30]** |
| Tone | "A feasibility certificate has to be a covering argument" — absent; proposal optimism **[O pp.1, 9]** | "the framework is the difference between a number and a measurement" **[N p.2]** |

## 2. Completely new content (nothing comparable in the old report)

- **Feasibility certificate — new Sec. III-G** **[N pp.8–10, audited N p.29]**. Packing lemma **[N p.8]**: A cannot be K-covered by fewer than K·P(A,R) discs. Region instance **N ≥ 4K = 8** (four corners of the 80×80 m square are >2Rcov = 70 m apart) **[N p.9]**; bound is exactly tight (4K-disc construction) **[N p.9]**; sensor-set packing over 30 random draws: mean P = 2.133 → N ≥ 4.27, **N=5 excluded in 4/30 draws (13%)** **[N p.9, 28–29]**.
- **Area surplus certifies nothing** — σ = 1.503 passes at N=5 yet the config is infeasible; "an area is not a covering" **[N pp.2, 9, 28]** (the old report *believed* σ = 1.50 certified feasibility: "both satisfied by the chosen Rcov = 35 m … margin for a single-UAV failure" **[O p.4]**).
- **Teleporting placement oracle** (achievability ceiling; oracle = 1.000 at N=8, 0.990 at N=5) **[N pp.4, 9, 20, 21]**; normalisation is the identity here but carries the "coverable at all" information **[N p.9]**.
- **Degeneracy theorem for service continuity**: F = ∅ ⟹ SC(π) = 0 ∀π (Eq. 13) **[N p.9]**; non-degenerate replacements: time-averaged coverage deficit (= 1 − CK exactly) and **maximum refresh time** **[N pp.9, 19]** (old report listed SC as a headline metric without noting this: "Fraction of mission time … Measures end-to-end persistent service" **[O p.8, Table IX]**).
- **Full Results section VIII** (old had none):
  - Base comparison table **[N pp.20–21]**: Fixed 0.372 / Greedy 0.784 / Reactive 0.953 / Reactive-local 0.972 / Indep. DQN 0.381 / Masked PPO (local critic) 0.625 / MAPPO 0.674 ± 0.060 / MAPPO argmax 0.418 / Oracle 1.000.
  - The negative result and the 0.298 gap **[N pp.2, 20–21, 30]**; privilege test (local rule *beats* privileged 0.972 vs 0.953, so the gap is not an information artefact) **[N p.21]**.
  - Controlled arms with per-arm CI upper limits below the gap (identity +0.008 [−0.121, +0.137]; full obs +0.034 [−0.033, +0.102]; no energy constraint +0.010 [−0.056, +0.075]; no threshold −0.018 [−0.047, +0.011]; prev. rule −0.050 [−0.115, +0.015]; margins +0.161…+0.287) **[N pp.2–3, 23, 24–25, 30–31]**.
  - **Budget sweep** 8/16/25 episodes → 0.588/0.624/0.674, paired +0.086 [+0.036, +0.135] ≈ 29% of the gap; budget excluded over the tested range, not beyond it **[N pp.21–22, 26, 31]**.
  - **Component ablation** base **[N pp.25–26]** (only under-coverage term +0.097 [+0.020, +0.174] resolvable; criticality/degraded-service terms inert because the filter already enforces them — explained **[N pp.25–26]**) and stress S8 **[N pp.26–27]** (reserve UAV −0.190; action mask +0.050; vanilla MAPPO −0.181).
  - **Credit assignment, cheapest test** per-agent actor + local critic: 0.639 vs 0.674, paired −0.035 [−0.079, +0.009]; what it does/does not change stated precisely **[N pp.15–16, 23, 26–27, 30]**.
  - **Observation experiment** without identity the deterministic policy takes 1.84/8 distinct actions and the swarm barely disperses (Foerster's condition (ii), measured) **[N pp.15, 22–23]**; deficit-map resolution G ∈ {0,4,8} makes no coverage difference (null result, reported) **[N pp.7, 23, 30]**.
  - **Scenario matrix** S1–S9, learned controller behind the stronger rule in **34/34 variants** (deficits −0.080 … −0.598) **[N pp.19, 27–28]** (old scenario *plan*: Table X **[O p.9]**).
  - **Connectivity-availability accounting**: all 4 disconnections follow a UAV leaving the active set, 0 unexplained **[N pp.20–21, 31]**; filter-leak probe **[N p.23]**.
- **Radio model — new Sec. III-I** **[N pp.10–11]**: Al-Hourani LoS **[N p.10]**, blended log-distance path loss, 802.11 OFDM MCS gate at 6.5 Mbit/s; coverage count = geometry ∧ radio (Eq. 19) **[N pp.10–11]**. Old report was purely geometric: "the inter-UAV communication graph … ∥pi − pj∥2 ≤ Rcomm" **[O pp.3–4]** with PHY fading explicitly abstracted **[O p.6]**.
- **OMNeT++/INET Phase-2 executed** (old: only a plan diagram, "Phase 2 adds wireless-network behaviour… Phase 3 introduces PHY-aware communication" **[O p.7, Fig. 5]**): phases executed/authenticated as audit trail **[N p.18]**; Python-PHY = INET `BreakpointPathLoss` to **0.012 dB** over 24 (distance, exponent) points **[N pp.28–29, 30]**; **negative-control story** — first MAC-frame observable was caught by a 60 dB Ptx control, rebuilt min-SNIR probe tracks Ptx (27 dB → 27 dB) but not distance, so **no runtime PHY cross-validation is claimed** **[N pp.18, 28–30]**; probe table (receptions 500→0 over 117 dB Ptx sweep) **[N pp.29–30, Table XIX]**.
- **Claim audit infrastructure** `claim_audit.py`: 38 items (34 verified, 4 transparency, 0 fail); determinism items R1/T1; scenario matrix re-run twice, 170/170 values identical **[N pp.18, 28–29]**.
- **Plasticity probe** (dormant/silent/dead neurons, per-agent gradient decomposition): 0% dormant in both hidden layers vs 40–45% reported for vanilla MAPPO; 9–21% gradient-silent **[N p.30, Table XX]**.
- **Safety-filter forensics**: stranding diagnostic — under the previous energy rule the policy strands 5.7/8 UAVs vs the rule's 0.4; traced to a mask defect, repaired (5.7 → 0.4, returns 105 → 543) **[N pp.23–24]** (cf. old safety-mask description **[O pp.4–5]**, which had no such analysis).
- **Simulator bug confessions**: motion step never applied moves (caught by a spread diagnostic, not tests/loss) **[N p.18]**; the paper's Phase-2 frame counts also caught pre-report **[N p.18]**.
- **Methodology subdivisions new in Sec. III**: exhaustion ≠ failure distinction **[N pp.12–13]**; the energy mask one-sidedness **[N p.12]**; the sink-not-a-vertex assumption **[N p.10]**; parameter-consistency audit (600 s endurance, 3.6 C charge rate, braking 25 m vs dsafe 5 m, mean degree 3.63/7) **[N pp.13–14, 28]**.

## 3. Changed configuration / design decisions

| Parameter / choice | Old | New | Why (cite) |
|---|---|---|---|
| Active UAVs N | 5 **[O p.3, Table VI]** | **8** **[N pp.2, 9, 13, Table VII]** | Feasibility certificate N ≥ 4K = 8 **[N p.9]** |
| Episode length T | 10,000 steps (2000 s) **[O p.3, Table VI]** | **2,000 steps (400 s)** **[N pp.2, 13, 31]** | At 400 steps the pack never depleted and charging/reserve never fired; at 2000 the energy constraint binds (213 returns, 0.4 stranding/ep) **[N p.13]** |
| Initial deployment | (unspecified / normal start) | **connected corner cluster covering only 3/20 sensors** **[N pp.2, 13]** | A centred ring already covers 17/20 → CK ≥ 0.85 for a do-nothing controller; pre-deployed kept as S9 **[N p.13]** |
| Reward weights | λD=0.50, λC=0.20 **[O p.5, Table IV]** | **λD=2.00, λC=0.50** **[N p.12–13, Table V]** | Degraded-service & connectivity raised so they don't drown under coverage **[N p.13]** |
| Team reward terms | 6 terms **[O pp.5, Eq. 23]** | **7 terms — new λB term** Bt (mean fractional shortfall below return threshold) **[N pp.12, 13, Eq. 29, Table V]** | A consumption-only signal gives no reason to turn back: flight to pad = 0.0016 of pack vs the late team-level consequence **[N p.13]** |
| Numerically inert terms noted | (none) | energy term ≤ 5×10⁻⁵; threshold-term scale mismatch ×7 stated **[N p.13]** | "the scalings are much weaker than the table's layout suggests" |
| Local observation oi | 8 features **[O p.3, Eq. 4, Table II]** | **11 features** (+ one-hot identity 1i, pad bearing d̂i, G×G broadcast deficit summary Mdef, G=4) **[N pp.6–7, Eq. 4, Table III]** | Identity needed for parameter sharing to specialise **[N pp.7, 15]**; bearing needed to fly home **[N p.7]** |
| Connectivity mask | generic connectivity-preservation mask "masked in normal operation" **[O pp.4, 6]** | **H = 3-step eccentricity lookahead** + joint projection; explicit analysis of what the rule does/doesn't forbid (chain/ring examples), mask at logit level, no-leak/no-restriction measurement **[N pp.15–17]** | Makes the filter's guarantee precise (filter-level, not policy-level) **[N p.12]** |
| Comparisons table | promises MAD-DDQN, POGS-QMIX, MAHPPO-AM, Vanilla MAPPO **[O pp.7–8, Tables VIII/IX]** | **new "Evaluated" yes/no column**: POGS-QMIX explicitly *not* re-implemented; learned baselines are family implementations, not reproductions **[N pp.18–19, Table IX]** | Anti-overclaim honesty |

## 4. Research question and contributions rewritten

- **Old RQ** **[O p.1]**: "Can a decentralized MAPPO policy maintain persistent K-coverage and swarm connectivity…?" — open.
- **New RQ** **[N p.2]**: same **plus** "…and can its performance be certified against a rigorous achievability bound rather than reported as an unscaled coverage ratio?"
- **Contributions**: old = **4** (unified model, MAPPO CTDE framework, literature synthesis, metric protocol) **[O p.1]** → new = **11** (adds feasibility certificate, achievability ceiling, measured negative result, PHY-derived links, non-degenerate protocol, observation-content specification, corrected deployments N=8/Rcov=35 or N=5/Rcov=45 — the latter **measured** at +0.083 for the learned controller **[N pp.2–3, 9]**, negative-control methodology) **[N pp.2–3]**.
- **New near-miss positioning**: Trotta et al. [15] (no failure model/no K-multiplicity/no learned policy) **[N pp.4–5, Table II pp.5–6]**; IRADA Zhang et al. [44] — the closest near-miss (4 of 5 elements, reward-driven not learned) **[N pp.4, 5]**; Shi et al. [18] closest published competitor **[N pp.4–5]**; the "no infeasibility certificate for persistent coverage in our corpus" and "no paper names the degenerate binary metric" bounded-absence claims **[N pp.4–5]**; credit-assignment line (COMA [22], DAE [23], GPAE [24], HAPPO/HATRPO [25], wonderful-life-utility [26]) **[N pp.4–5, 15]**.

## 5. Length, figures, tables

- 10 pp **[O]** → 33 pp **[N]**; ~5 figures **[O Figs. 1–5]** → ~10 figures + ~20 tables. Old architecture/coupling/state-machine/pipeline figures reappear as **N Figs. 2, 3, 4, 5** **[N pp.6, 10, 11, 15]** (old: **O Figs. 1, 2, 3, 4** **[O pp.2, 4, 5, 6]**). Entirely new figures: the 3-panel argument **N Fig. 1 [p.1]**, budget sweep **N Fig. 7 [p.22]**, learning curves **N Fig. 8 [p.23]**, arms-vs-gap **N Fig. 9 [p.24]**, scenario matrix **N Fig. 10 [p.27]**, staged plan N Fig. 6 [p.17] (old Fig. 5 [O p.7]).
- New tables old report lacks: base comparison (XII) **[N p.20]**, observation (XIII) **[N p.23]**, energy (XIV) **[N p.24]**, ablations (XV, XVI) **[N pp.25–26]**, credit (XVII) **[N p.26]**, scenario matrix (XVIII) **[N p.27]**, PHY probe (XIX) **[N p.29]**, plasticity (XX) **[N p.30]**.
- **Results-metrics reporting honesty** (old Table IX **[O p.8]** vs new Table X **[N pp.18–19]**): new table annotates SC as degenerate and adds deficit/refresh-time rows; Sec. VI-a states which metrics are **not** reported and why **[N p.19]**.

## 6. What survived essentially unchanged

- Title, authors **[O p.1 / N p.1]**; Dec-POMDP formulation Eq. (1)–(2) **[O p.3 / N p.6]**; global state Eq. (3) (new: added critic-side note that the state does not carry nd(t) directly **[N p.6]**); six-action space Eq. (5) **[O p.3 / N p.7]**; K-coverage Eqs. (7)–(10) **[O p.3 / N p.7]**; communication graph Eq. (11)/(14) **[O p.4 / N p.10]**; battery model Eq. (14)/(20) & power Eq. (15)/(21) **[O p.5 / N p.10]**; return threshold Eq. (16)/(22) **[O p.5 / N p.10]**; charging arbitration Eqs. (17)–(18)/(23)–(24) **[O p.5 / N p.12]**; safety constraints Eq. (19)/(25) **[O p.5 / N p.12]**; failure/recovery Eq. (20)/(26) **[O p.5 / N p.12]**; primary objective & team reward Eqs. (21)–(23)/(27)–(29) **[O pp.5–6 / N p.12]**; MAPPO machinery Eqs. (24)–(29)/(30)–(35) **[O pp.6–7 / N pp.15–16]**; Algorithm 1 **[O p.7 / N p.17]**; Hungarian arbitration, reserve mechanism wording; fixed/greedy/reactive baselines **[O pp.7–8 / N p.18]**; scenario list S1–S8 (**S9 added** for initial deployment) **[O p.9 / N p.19]**; system parameters Bmax 30 kJ, Pmove 75 W, Ptx 0.5 W, etc. **[O p.3, Table VI / N p.13, Table VII]**; three-phase plan retained — but now "not as a description of a plan but as an audit trail" **[O p.7 Fig.5 / N p.18]**.
- Unchanged *first-order* feasibility area analysis also reappears in the new report — but inverted in role: now presented as the bare area-count vs. the covering bound **[N p.8]** (old: presented as the feasibility check itself **[O p.4]**).

---

### TL;DR for the committee

The old report was the **plan** **[O pp.1–10]**; the new report is the **execution plus the lesson**: the original N=5 configuration was infeasible (proved, **[N pp.8–9]**), the plan's joint metric was degenerate (proved, **[N p.9]**), the learned controller loses to a hand-written rule by 0.298 with every cheap explanation ruled out by paired controlled arms (**[N pp.20–25]**), and everything is machine-audited so every number traces to an artefact (**[N pp.18, 28–29]**). The strongest original ideas that are new: the feasibility certificate and the negative-control discipline for physical-layer claims (**[N pp.28–30]**).
