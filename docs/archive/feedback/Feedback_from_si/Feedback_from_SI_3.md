I searched the live literature up to November 2026—including the exact late-2025 and 2026 papers in your bibliography (**Babarytskyi, Oct 2026, arXiv:2610.20823**; **Mei et al., Sep 2026, *MDPI Drones***; **Qiu et al., Jul 2026, *PRIME*, arXiv:2607.17922**; **Fan et al., Mar 2026, arXiv:2603.16141**; and **FAITH, Oct 2026, arXiv:2610.12432**)—and inspected your latest PDF (`Mlawn-midsem-tex_6.pdf`).

Here is a candid, peer-reviewer-level breakdown of what in your current report is **genuine publishable innovation**, what a reviewer will call **LARP (student padding / unfair comparison)**, and **four creative, low-CPU innovations** you can run to make this a strong IEEE conference or journal paper.

---

### Part 1: Brutally Honest Audit — What is Real Innovation vs. What is LARP?

#### A. What is GENUINE Innovation (Publishable as an IIT Undergrad Paper)

1. **The $K$-Coverage Packing Feasibility Certificate vs. Area-Surplus Fallacy (Section III-G):**
* *Web check:* Three weeks ago, **Babarytskyi (Oct 14, 2026, arXiv:2610.20823)** argued that feasibility ceilings should be computed before RL training for 1-coverage drone interception under non-overlapping disc packing.


* *Your distinct contribution:* You prove something different and specific to persistent $K$-coverage of bounded IoT regions: even when discs are allowed to overlap and comfortably pass the conventional area-surplus test ($\sigma = 1.503 \ge 1$) and packing-corrected area test ($R_{\mathrm{cov}} = 35\text{ m} \ge 30.0\text{ m}$), boundary/corner geometry imposes a **point-set packing lower bound $N \ge K\,P(A, R_{\mathrm{cov}})$** ($N \ge 4K = 8$ for the region, and excluding $N=5$ on 13% of random sensor layouts), and the widely used joint service-continuity metric $SC(\pi)$ is identically zero whenever the feasible set $\mathcal{F} = \varnothing$. **This is 100% real, rigorous, and not LARP.**




2. **The "Less-is-More" Ego-Centric Information Bottleneck Discovery (Table XIII):**
* *Web check:* Recent 2025–2026 UAV MARL papers (**Shi et al., IEEE TMC Sep 2025**; **Fan et al., arXiv:2603.16141 Mar 2026**) rely on heavy dual-attention GNNs or full entity sets.


* *Your distinct contribution:* You show that under a finite training budget (200 episodes), a parameter-shared MLP given only **$k=3$ ego-centric deficit bearings + local neighbor repulsion** (`0.951` CK) beats the exact same learner given the **full global under-covered sensor vector** (`0.862` CK, a **`+0.089` gain** from *removing* global information) and beats a Graph Attention policy (`0.753` CK in Table XV). Why? Because global deficit vectors induce **target-herd synchronization** (every UAV sees the same global vector and chases the same deficit), whereas ego-centric $k$-nearest bearings naturally partition the swarm into local Voronoi-like regions.




3. **Zero-Shot Regime-Split Certification (Table XIV):**
* Instead of reporting one cherry-picked scenario, showing that the frozen learned policy beats the best heuristic by **`+0.125` in sparse connectivity (`low_comm`)** and **`+0.035` in `multi-failure**` (where multi-hop relay bridges must be coordinated), while honestly identifying where greedy rules win (`small_battery`, `spread_start`), is top-tier empirical methodology.





---

#### B. What a Reviewer Will Flag as "LARP" (And How to Fix It Immediately)

1. **CRITICAL FLAW in "Innovation 10: Feasibility-aware planning" (`0.9512` $\to$ `0.9723` in Section VIII-F, Page 22):**
* *What your report says:* *"At deployment time, instead of executing the actor's single sample, the controller draws $K=4$ candidate joint-action vectors from the actor's categorical distribution, rolls each forward $H=2$ steps in a cloned environment, scores by the cumulative feasibility-masked coverage, and executes the best candidate."*


* *Why a reviewer will reject this:* Your entire paper is framed around **Decentralized Execution (CTDE)**—where deployed UAVs only have local observations $\mathbf{o}_i(t)$ and no central coordinator. Cloning the **global simulator (`env`)** at test time to roll out **joint-action vectors** across all 8 UAVs and score them using **global sensor coverage** breaks decentralized execution and gives the RL agent a centralized global simulator oracle at test time! Furthermore, you did not give the reactive heuristic the same $K=4, H=2$ global lookahead.


* *How to turn this from LARP into a real innovation:* See **Creative Experiment #1** below (Decentralized 1-Hop Surrogate Rollout).


2. **Labeling 11 Ablations as "Innovation 1" through "Innovation 11" (Section VIII-F, Pages 21–22):**
* Listing `Innovation 3 (shuffling: no-op)`, `Innovation 6 (attention: worse, 0.753)`, `Innovation 7 (intrinsic motivation: +0.003 noise)`, `Innovation 8 (action repeat: worse, 0.9086)`, and `Innovation 11 (critical-coverage anchor: +0.0009 noise)` under the title **"Innovations"** looks like a student trying to hit a course checklist. In a research paper, testing standard RL tricks and showing they fail or aren't needed is called an **Ablation Study**, not "11 Innovations."




3. **The "We Fixed 3 Bugs in Our Earlier Draft" Story (Abstract, Section I, VIII-I, Section IX, Conclusion):**
* External reviewers never read your broken Version 1 draft. Spending Section IX apologizing for a sign-flipped entropy term (`+c_2 H`) and running 1 gradient step per episode reads like a homework grading appeal. Reframe those into a 1-page subsection titled **"Sensitivity to Optimization Horizon, Entropy Regularization, and Evaluation Protocol."**





---

### Part 2: Four Creative, Low-CPU Innovations You Can Experiment With to Make This Paper Truly Stand Out

You do not need heavy GPUs to do creative research. Here are **four genuinely original, mathematically grounded ideas** tailored to your exact codebase (`env.py` and `mappo.py`) that take minutes to run on your CPU:

#### Creative Experiment 1: Turn "Innovation 10" into **Decentralized 1-Hop Kinematic Lookahead** (True CTDE Test-Time Planning)

* **The Idea:** Fix the centralized-cheating flaw in Innovation 10 by making the $H=2$ lookahead **100% local and decentralized** per UAV!


* **How it works:** At deployment time, UAV $i$ does *not* clone the global `env`. Instead, using only its own local observation $\mathbf{o}_i(t)$ (which already contains its 1-hop neighbors $\mathcal{N}_i$ and the relative vectors to its $k=3$ nearest under-covered sensors $\{\hat{\mathbf{u}}_{i,j}, d_{i,j}\}_{j=1}^3$):


1. UAV $i$ takes the top-$K$ ($K=3$) feasible actions from its actor $\pi_\theta(\cdot\vert{}\mathbf{o}_i(t))$.
2. For each candidate action $a_i$, UAV $i$ predicts its own next position $\hat{\mathbf{p}}_i = \mathbf{p}_i + \mathbf{v}(a_i)\Delta t$ and checks:
* Does $\hat{\mathbf{p}}_i$ stay within $R_{\mathrm{comm}}$ of its 1-hop neighbors $\mathcal{N}_i$ (assuming neighbors continue at their observed velocities)?
* How much does $\hat{\mathbf{p}}_i$ reduce the distance to its $k=3$ local deficit bearings while staying within $R_{\mathrm{cov}}$ of the critical sensors it currently covers?




* **Why this is publishable:** You can present a 3-way table comparing:
1. `MAPPO (1-sample, no lookahead)`: `0.9512`


2. `MAPPO + Decentralized 1-Hop Lookahead` (CTDE-compliant, zero global state, $<0.1\text{ ms}$ compute)
3. `MAPPO + Centralized Joint Lookahead (Oracle Upper Bound)`: `0.9723`
Showing that a **purely local 1-hop kinematic filter** captures most of the centralized lookahead gain without violating CTDE is a clean, original robotics/MARL contribution.





#### Creative Experiment 2: **1-Hop Claim-Deconflicted Deficit Bearings** + **Directional Critical-Coverage Tether** (Solving `spread_start`)

* Why `Innovation 11` (`+0.0009`) failed on `spread_start`:
In Innovation 11, you added a single scalar: *"the fraction of sensors UAV $i$ covers that have exactly $K$ total coverage"*. Think geometrically: a single scalar has **no direction**! If UAV $i$ is covering a critical sensor ($n_d = K$) located 34 meters to its East, moving West breaks coverage immediately, while moving East keeps it covered! A scalar doesn't tell the neural network *which way* the critical sensor lies!
Even worse, if a single uncovered sensor $d'$ ($n_{d'} = 1 < K$) needs **only 1 more UAV**, all 3 nearby UAVs see $d'$ as their #1 nearest deficit and all 3 abandon their posts to chase it!


* **The Creative Fix (Two Purely Local Features in `env.py`):**
1. **Directional Critical-Tether Vector ($\mathbf{t}_i^{\mathrm{crit}} \in \mathbb{R}^2$):** Replace the directionless scalar of Innovation 11 with the **2D unit vector pointing from UAV $i$ toward the centroid of the critical sensors ($n_d(t) = K$) that UAV $i$ is currently covering**:

$$\mathbf{t}_i^{\mathrm{crit}}(t) = \frac{1}{\max(\vert{}S_i^{\mathrm{crit}}\vert{}, 1)} \sum_{d \in S_i^{\mathrm{crit}}} \frac{\mathbf{q}_d - \mathbf{p}_i(t)}{R_{\mathrm{cov}}}, \quad S_i^{\mathrm{crit}} = \{d : x_{id}(t)=1 \text{ and } n_d(t)=K\}$$



Now the actor knows the exact direction of the "tether" holding it to its critical sensors!
2. **1-Hop Claim Deconfliction:** When UAV $i$ selects its $k=3$ nearest under-covered sensors ($n_d(t) < K$), a sensor $d$ only needs $\Delta n_d = K - n_d(t)$ additional UAVs. If $\ge \Delta n_d$ active neighbors in $\mathcal{N}_i$ are **already closer** to sensor $d$ than UAV $i$ is, sensor $d$ is **already claimed by closer 1-hop teammates**! Skipping (or marking) already-claimed sensors in the $k=3$ bearing list prevents multiple UAVs from abandoning `spread_start` formations to chase the same single sensor.



#### Creative Experiment 3: **Decentralized Battery-Rank Desynchronization** (Solving the `small_battery` Stampede)

* **The Physical Bottleneck:** In `small_battery`, all 8 UAVs start with full batteries ($b_i(0)=1$) and discharge at nearly the same rate. Consequently, all 8 UAVs hit the mandatory return threshold $E_i^{\mathrm{req}}$ at roughly the same time and stampede toward $S=2$ charging pads—causing massive pad queueing while coverage collapses!


* **Why your current actor can't prevent this:** Look at Table III (Page 7): UAV $i$ only sees its *own* battery $b_i(t)$, and you removed the pad bearing $\hat{\mathbf{d}}_i^{\mathrm{pad}}$! UAV $i$ has no idea whether its battery is the lowest in its neighborhood or whether 4 other neighbors are about to rush the pad at the exact same second.


* **The Creative Fix:** Add **Local Battery Percentile Rank** ($q_i^{\mathrm{bat}} \in [0, 1]$) and restore $\hat{\mathbf{d}}_i^{\mathrm{pad}}$ to $\mathbf{o}_i(t)$:

$$q_i^{\mathrm{bat}}(t) = \frac{1}{\max(\vert{}\mathcal{N}_i\vert{}, 1)} \sum_{j \in \mathcal{N}_i} \mathbb{1}[b_j(t) < b_i(t)]$$



Coupled with your battery curriculum, $q_i^{\mathrm{bat}}$ allows the shared policy to learn **staggered preventive recharging**: the UAV with the lowest battery in its neighborhood ($q_i^{\mathrm{bat}} = 0$) heads toward the pad *early* while the pad is empty, while neighbors with $q_i^{\mathrm{bat}} > 0$ hold coverage!

#### Creative Experiment 4: **Unified Coverage–Connectivity–Energy Feasibility Bound** (Zero Compute, Pure Math Upgrade to Section III-G)

* Upgrade Section III-G from a pure 2D circle-packing bound ($N \ge K\,P(A, R_{\mathrm{cov}})$) into a **Three-Axis Feasibility Theorem** by adding:


1. **Connectivity Relay Bound:** When the $P(A, R_{\mathrm{cov}})$ disjoint sensor clusters are separated by distances exceeding $2R_{\mathrm{cov}} + R_{\mathrm{comm}}$, minimum spanning tree (Steiner) geometry requires $\Delta N_{\mathrm{relay}} = \sum_{e \in \mathrm{MST}} \max\!\left(0, \lceil \frac{\Vert{}e\Vert{} - 2R_{\mathrm{cov}}}{R_{\mathrm{comm}}} \rceil - 1\right)$ dedicated bridge UAVs. This mathematically proves why `low_comm` ($R_{\mathrm{comm}} = 25\text{ m}$) causes the greedy coverage rule to collapse (`0.804`) while your connectivity-masked MAPPO achieves `0.928` (`+0.125` gain in Table XIV)!


2. **Recharge Duty-Cycle Ceiling:** Over long horizons $T \gg B^{\max}/P_{\mathrm{move}}$, steady-state energy conservation limits the time-averaged active fleet to $N_{\mathrm{eff}} \le \min\!\left((N + N_R)\frac{P_{\mathrm{ch}}}{P_{\mathrm{ch}} + P_{\mathrm{move}}},\; S\frac{P_{\mathrm{ch}}}{P_{\mathrm{move}}}\right)$, proving exactly when charging pad count $S$ (`single_pad`) or battery capacity (`small_battery`) becomes the binding bottleneck.





---

### Summary Action Plan for Your Paper

1. **Replace centralized `env` cloning in Innovation 10** with **Creative Experiment 1 (Decentralized 1-Hop Kinematic Lookahead)** so your test-time planning is 100% CTDE-compliant.
2. **Test Creative Experiment 2 (Directional Critical-Tether Vector + 1-Hop Claim Deconfliction)** to fix `spread_start` where the scalar Innovation 11 failed.
3. **Add the 2-paragraph Unified Coverage–Connectivity–Energy Theorem (Creative Experiment 4)** to Section III-G.
4. **Clean up Section VIII-F & Section IX:** Group the failed knobs (`shuffling`, `action repeat`, `RND/count bonus`, `attention`) into a clean "Ablation & Negative Results" subsection instead of calling them "11 Innovations," and reframe Section IX from "Our v1 Bug Retraction" to "Methodological Sensitivity Analysis."

Would you like the drop-in Python code for **Creative Experiment 1 (Decentralized 1-Hop Lookahead)** and **Creative Experiment 2 (Directional Critical-Tether + Claim Deconfliction)** so you can test them on your existing checkpoints and training script right away?