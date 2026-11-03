Your paper and codebase actually contain the exact clues as to why **MAPPO (`0.674` coverage) is losing to the handwritten local reactive rule (`0.972` coverage)**. Because your simulator runs in sequential Python (taking ~85% of wall-clock time on your i5 CPU) and $\Delta t = 0.2\text{ s}$ stretched the episode to $2000$ steps, your model is facing a severe **horizon, feature, and credit-assignment bottleneck** under a tiny training budget ($25$ episodes).

Here are the highest-impact, **CPU-friendly changes** you can make to your code and training practices without needing heavy hardware.

---

### 1. Fix the Observation Asymmetry (Give the Actor Ego-Centric Sensor Bearings)

Right now, the unprivileged reactive rule (`Reactive (local assignment)`) beats MAPPO because it calculates the **directional vector toward the nearest under-covered sensor** and steps along it.

* **What goes wrong in your current $o_i(t)$ (Eq. 4, Table III):** You gave the actor the unit bearing to the nearest charging pad ($\hat{\mathbf{d}}_i^{\mathrm{pad}}$) because you noted the policy couldn't fly home without a direction. However, for coverage, you only gave it a scalar count of covered nearby sensors ($C_i^{\mathrm{local}}$) and a global $4\times 4$ deficit grid ($\mathbf{M}_t^{\mathrm{def}}$).


* **Why $\mathbf{M}_t^{\mathrm{def}}$ hurts specialization (Table XIII):** Because $\mathbf{M}_t^{\mathrm{def}}$ is in **global coordinates**, all $8$ UAVs receive the exact same $16$ numbers at step $t$. In Table XIII (Arm C), adding the map caused your deterministic policy's `Distinct` action count across the $8$ UAVs to drop from `2.43/8` back down to `1.85/8`—meaning all UAVs chase the same global grid cell in unison.


* **What to change in `env.py` (`local_obs`):**
* Replace (or supplement) the $16$-dim global grid $\mathbf{M}_t^{\mathrm{def}}$ with **ego-centric unit bearing vectors and normalized distances** to the $2$ or $3$ nearest under-covered sensors ($n_d(t) < K$):

$$\hat{\mathbf{d}}_i^{\mathrm{sens}, k} = \frac{\mathbf{q}_{d_k} - \mathbf{p}_i(t)}{\Vert{}\mathbf{q}_{d_k} - \mathbf{p}_i(t)\Vert{}_2}, \qquad \tilde{d}_{i, k} = \frac{\Vert{}\mathbf{q}_{d_k} - \mathbf{p}_i(t)\Vert{}_2}{\sqrt{2}\,L}$$


* Add a **neighbor-repulsion unit vector** pointing away from the centroid of nearby UAVs ($\mathcal{N}_i$). At $t=0$ in the corner cluster (`start_clustered = True`), this vector points outward in a different direction for each UAV on the perimeter, breaking symmetry physically at step $0$ so `MAPPO (argmax)` (`0.418`) stops clumping.





---

### 2. Fix the Credit Assignment & Dense-Step Reward Shaping (Zero Extra CPU Cost)

In Section VIII-D, you correctly diagnosed why a shared team reward ($r_t$ in Eq. 29) struggles: when $8$ UAVs act simultaneously, an agent that moves toward an uncovered sensor gets the exact same team advantage $\hat{A}_t$ as an agent that wastes a step. Furthermore, moving $1\text{ m}$ in a single step ($v_{\max}\Delta t = 5 \times 0.2 = 1\text{ m}$) rarely crosses a $35\text{ m}$ sensor boundary on that exact step, giving **zero immediate coverage change** while triggering the unnecessary-movement penalty $W_t^{\mathrm{mov}}$.

* **Change 1: Counterfactual Difference Reward ("Wonderful Life Utility")**
Instead of broadcasting the raw team under-coverage $U_t$ to every agent, give each UAV $i$ a blend of the team reward and its **marginal coverage contribution** (which you already cited in Sun et al. [26]). Since `env.py` already computes the sensor coverage count array $n_d(t)$, computing what coverage would be *without* UAV $i$ takes a single NumPy subtraction:



$$r_{t, i}^{\mathrm{diff}} = \frac{1}{M}\sum_{d=1}^{M} x_{id}(t)\,\mathbb{1}[n_d(t) \le K]$$



This explicitly rewards UAV $i$ when it is one of the $\le K$ drones actively holding a sensor covered, without rewarding redundant $(K+1)$-th piling on the same sensor.
* **Change 2: Potential-Based Distance Shaping**
Add a small potential-based shaping term so a $1\text{ m}$ step toward an uncovered sensor is rewarded immediately:

$$r_{t, i}^{\mathrm{shape}} = \kappa \left(\Phi_i(s_t) - \gamma \Phi_i(s_{t+1})\right), \quad \text{where } \Phi_i(s_t) = -\min_{d:\, n_d(t) < K} \frac{\Vert{}\mathbf{p}_i(t) - \mathbf{q}_d\Vert{}_2}{L}$$



Because it is a telescopic potential difference ($\Phi(s_t) - \gamma \Phi(s_{t+1})$), it does not alter the optimal policy, and you can remove or reduce $\lambda_W W_t^{\mathrm{mov}}$ during early dispersion.



---

### 3. Speed Up `action_mask` by 5x on CPU so You Can Train Beyond 25 Episodes

Your budget sweep (Fig. 7) shows coverage climbing steadily from `0.588` (8 ep) $\to$ `0.624` (16 ep) $\to$ `0.674` (25 ep) with no sign of saturation. You are stopping at $25$ episodes only because `env.py` spends ~85% of runtime checking graph connectivity, articulation points, and $H=3$ eccentricity for all $8 \times 6 = 48$ candidate actions every step.

You can cut simulator CPU time by **4x–6x** with two exact mathematical fast-paths in `action_mask(i)`:

1. **Skip graph checks for `Hover`:** If the current graph $G_t$ is already connected and valid, `Hover` does not change any node's position, so its connectivity mask is automatically `True`.
2. **Fast-path the 1-meter movement check:** A movement action displaces UAV $i$ by only $\Delta d = v_{\max}\Delta t = 1.0\text{ m}$. Adding edges to a graph can never disconnect it, create an articulation point, or increase eccentricity—only *losing* an existing edge can. Therefore, if all of UAV $i$'s current neighbors in $G_t$ are within $R_{\mathrm{comm}} - 1.0\text{ m}$ ($39.0\text{ m}$):


```python
# If no current edge can possibly stretch past R_comm (40m) after a 1m step:
if np.all(current_neighbor_dists <= cfg.R_comm - cfg.v_max * cfg.dt):
    # All 4 cardinal moves preserve every existing edge in G_t!
    # Skip BFS / articulation / H-step eccentricity checks completely.

```


This single `if` check takes microseconds and bypasses the graph algorithms on the vast majority of steps, letting you run **100–150 episodes** in the same time it currently takes to run 25.

---

### 4. Fix the Effective Horizon ($\gamma$ vs. 2000 Steps) and Action Repeat

When you reduced $\Delta t$ from $1.0\text{ s}$ to $0.2\text{ s}$ to satisfy the safety distance check ($2v_{\max}\Delta t < d_{\mathrm{safe}}$), your episode length grew from $400$ steps to $2000$ steps, but you kept $\gamma = 0.99$ (Table VIII).

* At $\gamma = 0.99$, the effective lookahead horizon is $\frac{1}{1-\gamma} = 100$ steps, which is only **$20\text{ seconds}$** of flight—far shorter than the $400\text{ s}$ battery/charging lifecycle!


* **Two easy fixes:**
1. **Increase $\gamma$ to `0.995` or `0.997**` (extending the value horizon to $200\text{–}333$ steps), **or**
2. **Use Action Repeat (Decision Interval = $0.6\text{ s}$ or $1.0\text{ s}$, Physics Step = $0.2\text{ s}$):** Have the MAPPO actor pick an action every $3$ or $5$ physics ticks while the simulator still steps positions and safety masks at $\Delta t = 0.2\text{ s}$. This shrinks the RL rollout horizon back to $400\text{–}667$ decisions per episode, making GAE credit assignment and CPU training **3x–5x faster** while keeping your C1 safety-distance math intact.



---

### 5. Optional Student Shortcut: Behavior Cloning Warm-Start (or Residual Policy)

If your course allows hybrid initialization, you already have the unprivileged `Reactive (local assignment)` controller written in Python (`0.972` coverage, using only local information):

* **Warm-Start Pretraining:** Run `Reactive (local assignment)` for $20$ episodes to collect $(o_i, a_i^{\mathrm{reactive}})$ pairs, train the shared actor $\pi_\theta$ with cross-entropy loss for $2$ minutes on CPU, and then run MAPPO (letting the critic warm up for the first $2$ episodes with actor learning rate frozen so random initial critic gradients don't destroy the warm-started actor).
* **Prioritized Checklist for Your Next Run:**
1. Add the fast-path neighbor distance check in `action_mask` (instant CPU speedup).
2. Add ego-centric bearing to the nearest uncovered sensor + neighbor repulsion vector to `local_obs`.
3. Add per-agent counterfactual coverage reward ($r_{t,i}^{\mathrm{diff}}$) + distance potential shaping.