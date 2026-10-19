# 09 — REFERENCE VERIFICATION

**Checked:** 29 September 2026, by web search + Crossref + arXiv + publisher records.
**Result: 13 of 14 references are real and correctly cited. One has a wrong author
name. No fabricated references found.**

A fabricated or misattributed reference is the fastest way to lose marks. Fix
`chen2025` before you submit.

---

## PART 1 — VERIFICATION TABLE

| # | Key | Verdict | Action |
|---|---|---|---|
| 1 | `liu2018` | ✅ VERIFIED | none |
| 2 | `qiu2019` | ✅ VERIFIED | optional: use ICC 2020 version |
| 3 | `yu2022` | ✅ VERIFIED | none |
| 4 | `omoniwa2022` | ✅ VERIFIED | none |
| 5 | `zareh2016` | ✅ VERIFIED | optional: full surname is Eshghdoust |
| 6 | `basu2004` | ✅ VERIFIED | none |
| 7 | `mathew2015` | ✅ VERIFIED | title: use "**Multirobot**" |
| 8 | `arribas2023` | ✅ VERIFIED | none |
| 9 | `jiang2024` | ✅ VERIFIED | none |
| 10 | `khan2025` | ✅ VERIFIED | none |
| 11 | `sun2025` | ✅ VERIFIED — genuine | mark as arXiv preprint |
| 12 | `chen2025` | ❌ **WRONG AUTHOR** | `Z. Chen` → **`Z. Zhuang`** |
| 13 | `carvalho2026` | ✅ VERIFIED — genuine | none |
| 14 | `mei2026` | ✅ VERIFIED — genuine | none |

---

## PART 2 — THE ONE ERROR TO FIX

### `chen2025` — the first author is **Zhuang**, not Chen

The paper is real, but the name is being misattributed. ICCCS 2025 lists the
authors in Given-Name-Surname order, so "Chen Zhuang" (庄) has surname **Zhuang**.
Writing "Z. Chen" attributes the paper to a different person.

**Corrected BibTeX:**

```bibtex
@inproceedings{zhuang2025marl,
  author    = {Zhuang Chen and Yuxiang Huang and Chaoyi Zhu and Wuyang Zhou},
  title     = {Multi-Agent Reinforcement Learning Based Trajectory Design for
               UAV-Assisted Emergency Wireless Communication},
  booktitle = {2025 10th International Conference on Computer and
               Communication Systems (ICCCS)},
  address   = {Chengdu, China},
  publisher = {IEEE},
  year      = {2025},
  pages     = {856--861},
  doi       = {10.1109/ICCCS65393.2025.11069505}
}
```

> **Caveat.** Existence, authorship and page range (856–861) were confirmed from
> the ICCCS 2025 programme and proceedings table of contents, but the DOI string
> could not be independently resolved (IEEE Xplore blocks automated queries).
> **Open the DOI in a browser before submitting.** If it does not resolve, drop
> the reference rather than risk it — you have 13 other verified refs.

### Cosmetic fixes

```diff
- N. Mathew, S. L. Smith, and S. L. Waslander, ``Multi-robot rendezvous planning
- for recharging in persistent tasks,'' IEEE Transactions on Robotics, ...
+ N. Mathew, S. L. Smith, and S. L. Waslander, ``Multirobot rendezvous planning
+ for recharging in persistent tasks,'' IEEE Transactions on Robotics, ...
```
IEEE's published title is one word. "Multi-robot" is the preprint form.

### Two optional upgrades

```bibtex
% qiu2019 — replace the preprint with the peer-reviewed version
@inproceedings{qiu2020,
  author    = {Jin Qiu and Jiangbin Lyu and Liqun Fu},
  title     = {Placement Optimization of Aerial Base Stations With Deep
               Reinforcement Learning},
  booktitle = {IEEE International Conference on Communications (ICC)},
  pages     = {1--6}, year = {2020},
  doi       = {10.1109/ICC40277.2020.9149258}
}

% zareh2016 — formal first-author surname
author = {Zareh Eshghdoust and Lorenzo Sabattini and Claudio Secchi}
```

### Note on `sun2025`

This is a **genuine arXiv preprint** (arXiv:2509.23905, 28 Sep 2025) and the
**MAHPPO-AM** acronym is correctly attributed — the paper explicitly defines
"multi-agent hybrid proximal policy optimization with action masking
(MAHPPO-AM)" and uses it throughout. But it has **no peer-reviewed version**.

If your course requires peer-reviewed sources, either mark it `[preprint]` in
the text or pair it with one of A2/A3 below.

---

## PART 3 — ADDITIONAL VERIFIED PAPERS TO STRENGTHEN RELATED WORK

All confirmed to exist. **A1 and A9 are the two you most need.**

### A1 — ⭐ The closest published competitor. Add this.

> R. Shi, X. Yu, Y. Wang, Y. Tian, Z. Liu, W. Wu, X.-P. Zhang, and M. M. Veloso,
> "Symmetry-Informed MARL: A Decentralized and Cooperative UAV Swarm Control
> Approach for Communication Coverage," *IEEE Transactions on Mobile Computing*,
> vol. 24, no. 9, pp. 8039–8056, Sep. 2025. doi: **10.1109/TMC.2025.3553285**

**Why it matters.** This is the peer-reviewed work closest to your problem:
permutation/equivariant-network MARL for decentralised UAV swarm communication
coverage. It explicitly benchmarks against *both* `liu2018` and `yu2022` — the
same two papers you build on. **Omitting it is the most conspicuous gap in your
related-work section.** Cite it, and position your work against it: they do
coverage only; you add persistent $K$-redundancy, connectivity criticality,
charging contention and failure recovery.

### A9 — ⭐ Foundational for your novelty claim. Add this.

> J. Scherer and B. Rinner, "Persistent multi-UAV surveillance with energy and
> communication constraints," *IEEE Int. Conf. Automation Science and
> Engineering (CASE)*, pp. 1225–1230, 2016. doi: **10.1109/COASE.2016.7743546**

**Why it matters.** This is the canonical formulation of **persistent coverage
subject to both energy/recharge feasibility AND a maintained multi-hop connection
to a base station** — i.e. literally your "connected persistent coverage"
problem statement. If your contribution claim is "persistent coverage +
connectivity + energy", **this is the paper you must cite and differentiate
from.** Not citing it invites a "you did not acknowledge the prior art" comment.

### A2 — CTDE-MAPPO for large cellular UAV swarms

> N. D. M. Quang, R. Chong, Z. Wei, C. Liu, and D. W. K. Ng, "Game-Theoretic
> Multi-Agent Reinforcement Learning for Swarm Trajectory Planning in Low-Altitude
> Wireless Networks," arXiv: **2606.16386**, 2026.

Useful because it explicitly argues why value-decomposition methods (QMIX) are
unsuited to non-decomposable congestion coupling. That argument is relevant to
your choice of a *policy-gradient* MAPPO over a value-based baseline.

### A3 — Beyond vanilla MAPPO

> P. Zhang and G. Li, "A cooperative dynamic target search approach for
> multi-UAV systems utilizing the MAPPO algorithm," *Discover Artificial
> Intelligence*, vol. 5, art. 153, 2025. doi: **10.1007/s44163-025-00411-9**

Attention-augmented MAPPO (AS-MAPPO) head-to-head vs plain MAPPO and MADDPG.
Good for showing you know what the MAPPO variant literature looks like.

### A4 — Joint trajectory + communication + power

> C. Wang, C. Wei, Z. Yin, K. Jin, and X. Li, "Collaborative planning of
> multi-UAV trajectories and communication strategies considering channel
> resource constraints," *Chinese Journal of Aeronautics*, 2025.
> doi: **10.7527/S1000-6893.2025.31837**

End-to-end MAPPO for trajectories + association + power. Recent and
communication-facing — matches your Phase 2/3 direction.

### A5 — Energy-constrained coverage planning (strongest recent baseline)

> D. Datsko, F. Nekovář, R. Pěnička, and M. Saska, "Energy-Aware Multi-UAV
> Coverage Mission Planning With Optimal Speed of Flight," *IEEE Robotics and
> Automation Letters*, vol. 9, no. 3, pp. 2893–2900, Mar. 2024.
> doi: **10.1109/LRA.2024.3358581** — code: `github.com/ctu-mrs/EnergyAwareMCPP`

The first multi-UAV coverage method to enforce **battery-capacity constraints
during planning**, validated in a real two-UAV flight. This is the baseline an
examiner is most likely to name. Cite it.

### A6 — UAV+UGV charging rendezvous

> M. S. Mondal, S. Ramasamy, J. D. Humann, J. M. Dotterweich, and
> P. A. Bhounsule, "Deep Reinforcement Learning Enabled Persistent Surveillance
> with Energy-Aware UAV-UGV Systems," *IEEE Transactions on Intelligent
> Vehicles*, vol. 11, no. 8, pp. 914–929, 2026. doi: **10.1109/TIV.2026.3696943**

Jointly plans UAV surveillance routes and UGV recharging rendezvous with a
transformer DRL policy. Directly relevant to your charging subproblem.

### A7 — Scalability of MARL coverage

> X. Chen *et al*., "Transformer-based reinforcement learning for scalable
> multi-UAV area coverage," *IEEE Trans. Intelligent Transportation Systems*,
> vol. 25, p. 10062, 2024. doi: **10.1109/TITS.2024.3358010**

Answers the obvious examiner question about your swarm size.

### A8 — The canonical continuous-coverage UAV paper

> H. Shakhatreh, A. Khreishah, J. Chakareski, H. B. Salameh, and I. Khalil,
> "On the Continuous Coverage Problem for a Swarm of UAVs," *2016 IEEE 37th
> Sarnoff Symposium*, pp. 130–135, 2016. doi: **10.1109/SARNOF.2016.7846742**

The theoretical ancestor of the continuous/persistent coverage problem. Older
than your 2024–26 window but indispensable for the framing.

### A10 — k-connectivity restoration for drone swarms

> O. Ceylan, Z. A. Dagdeviren, M. Challenger, and O. Dagdeviren, "Design and
> Analysis of k-Connectivity Restoration Algorithms for Fault-Tolerant Drone
> Swarms in Harsh Civil Environments," *Drones*, vol. 10, no. 1, art. 16, 2026.
> doi: **10.3390/drones10010016** — code: `github.com/netosresearch-ege/DAKRA`

The natural successor to your `basu2004` and `zareh2016` citations, and it
explicitly critiques existing k=1 RL-based restoration work. Strong for your
fault-tolerance section.

### A11 — k-connectivity via IP model

> M. Aşçı, Z. A. Dagdeviren, V. K. Akram, H. U. Yıldız, O. Dağdeviren, and
> B. Tavlı, "Enhancing Drone Network Resilience: Investigating Strategies for
> k-Connectivity Restoration," *Applied Sciences*, 2025.

> **Caveat:** the paper and author list were confirmed but **no DOI could be
> retrieved**. Check MDPI before citing.

### A12 — Persistent emergency comms, fleet-size minimisation

> C. Liu, X. Xin, Y. Dai, and D. Xu, "Cost Optimization of UAV Swarm Network for
> Persistent Emergency Communication," *IEEE Trans. Green Communications and
> Networking*, vol. 10, pp. 1734–1748, 2026.

Minimises UAV count while guaranteeing continuous multi-hop backhaul under energy
constraints. A strong **non-RL optimality reference** — good for arguing your
learned policy is competitive with combinatorial methods.

### A13 — Spare-drone fleet sizing (foundational)

> E. Hartuv, N. Agmon, and S. Kraus, "Scheduling spare drones for persistent task
> performance under energy constraints," *AAMAS 2018*, pp. 532–540.
> doi: **10.65109/YXEM5998**

The combinatorial core of "how many UAVs + how many chargers". Underpins
`arribas2023` and much of the 2026 literature.

### A14 — Mobile charging stations (standard reference)

> X. Lin, Y. Yazcoglu, and D. Aksaray, "Robust Planning for Persistent
> Surveillance With Energy-Constrained UAVs and Mobile Charging Stations,"
> *IEEE Robotics and Automation Letters*, vol. 7, no. 2, pp. 4157–4164, 2022.
> doi: **10.1109/LRA.2022.3146938**

The standard reference for mobile charging stations in persistent missions.
Full partial-charging analysis is in `05_07_THEORY_COVERAGE_GRAPH_ENERGY.md`
Part C.23.

---

## PART 4 — REVISED SURVEY STRUCTURE

Your current Table I groups 10 papers by *component*. An examiner looking for
a research gap wants to see the *intersection* clearly. Restructure as a
**capability matrix**:

| Paper | Cov | Conn | Energy | Charge | Fault | Persist | RL |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| liu2018 | ✓ | ✓ | ✓ | | | | ✓ |
| qiu2019 | ✓ | | | | | | ✓ |
| omoniwa2022 | ✓ | ✓ | ✓ | | | | ✓ |
| zareh2016 | | ✓ | | | ✓ | | |
| basu2004 | | ✓ | | | ✓ | | |
| mathew2015 | | | ✓ | ✓ | | ✓ | |
| arribas2023 | | | ✓ | ✓ | | ✓ | |
| jiang2024 | | | ✓ | | ✓ | | ✓ |
| khan2025 | ✓ | | | | | | ✓ |
| mei2026 | ✓ | | ✓ | ✓ | | ✓ | ✓ |
| **Scherer & Rinner (A9)** | ✓ | ✓ | ✓ | ✓ | | ✓ | |
| **Shi et al. (A1)** | ✓ | | | | | | ✓ |
| **Ceylan et al. (A10)** | | ✓ | | | ✓ | | |
| **This work** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

**The gap sentence that falls out of the matrix** — and it is defensible because
every cell was verified:

> *Scherer & Rinner (2016) come closest by coupling persistent coverage with both
> energy and connectivity, but they treat service locations as planned rather
> than reconfigured after failure. Shi et al. (2025) give decentralised
> communication coverage with symmetry-informed MARL, but without persistent
> redundancy, charging contention or failure recovery. Ceylan et al. (2026)
> solve $k$-connectivity restoration combinatorially, without learned coverage
> or energy management. No surveyed work simultaneously models (i) persistent
> $K$-coverage, (ii) communication-graph criticality, (iii) contested charging
> pads, (iv) failure-triggered reserve recovery, and (v) decentralised motion
> execution. That intersection is the target of this work.*

This is exactly the hedging your current Sec. II-C already does well
(*"a survey-derived gap statement, not a claim that no related component has ever
appeared"*). Keep that framing — it is the mark of honest scholarship.
