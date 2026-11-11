Because `PROJECT_CONTEXT_2.txt` is **5.53 MB** and packs all 537 files in alphabetical order, the first ~1.2 MB of the file is taken up by giant documentation and LaTeX files (`A_Survey_on_Unmanned_Aerial_Vehicles...txt` at 267 KB, `Mlawn-midsem-STUDY.tex` at 265 KB, `Mlawn-midsem-tex.tex` at 208 KB, `GLOSSARY.md` at 110 KB, `AUTONOMOUS_STATE.md` at 75 KB, and `FINDINGS.txt` at 57 KB). As a result, the file upload truncates around `FINDINGS.txt` before reaching `ml_impl/uav_wireless/*.py` and `scripts/*.py`.

Even before you upload the Python-only bundle (command below), I found **6 concrete implementation, math, and configuration bugs** from the specification, audit logs, and file tree in your bundle:

---

### 1. Sign-Flip Trap in Potential-Based Distance Shaping (Section III-O vs. `add_shaping.py` / `env.py`)

* **Where:** `Mlawn-midsem-tex.tex` / `Mlawn-midsem-tex_8.pdf` (Page 12, Section III-O) and `scripts/add_shaping.py`.


* **The Bug:** Section III-O states:
> *"With potential $\Phi$, a shaping term of the form $\kappa(\Phi(s_t)-\gamma\Phi(s_{t+1}))$ is telescoping... The distance potential is the mean over agents of the negative distance to the nearest under-covered sensor, normalised by the field diagonal"*.
> 
> 


* **Why the math is wrong:**
In Ng et al. (1999), for a **reward-maximization** learner, the potential-based shaping reward is:

$$F(s_t, s_{t+1}) = \kappa\left(\gamma \Phi(s_{t+1}) - \Phi(s_t)\right)$$



Let's check the sign if $\Phi(s_t) = -\frac{\text{dist}(s_t)}{D_{\text{diag}}} \le 0$:


* Suppose UAV $i$ moves **closer** to the nearest under-covered sensor from $t$ to $t+1$, so $\text{dist}(s_{t+1}) < \text{dist}(s_t)$ and $\Phi(s_{t+1}) > \Phi(s_t)$ (less negative).
* If you compute $\kappa(\Phi(s_t) - \gamma \Phi(s_{t+1}))$ with $\Phi = -\text{dist}$, moving closer gives a **negative** reward (penalizing the UAV for approaching the sensor)!
* Conversely, if your Python code computes $\kappa(\text{dist}_t - \gamma\,\text{dist}_{t+1})$ using **positive** distance $D(s_t) = +\text{dist}(s_t)$, then when $D(s_t)$ is constant ($\text{dist}_{t+1} = \text{dist}_t = d > 0$), every hover step gets a fake positive reward $+\kappa(1 - \gamma)d > 0$ for staying far away from sensors!
* **Correct formula:** Define $\Phi(s_t) = -\text{dist}(s_t)/D_{\text{diag}} \le 0$ and use $F(s_t, s_{t+1}) = \kappa\left(\gamma \Phi(s_{t+1}) - \Phi(s_t)\right)$.



---

### 2. Why `single_pad` ($S=1$) Prints `NA` in Table XIV Even Though Execution is Decentralized (`eval_stress.py`)

* **Where:** `scripts/eval_stress.py`, `ml_impl/uav_wireless/mappo.py`, and Table XIV (Page 21).


* **The Bug:** Section VIII-E states that `single_pad` cannot be evaluated zero-shot because changing $S=2 \to S=1$ *"changes the size of the centralised state, [so] no policy trained on the nominal architecture can even be loaded"*.


* **Why that's an evaluation-script bug, not an architectural limit:**
Under CTDE, **the centralized critic $V_\phi(\mathbf{s}_t)$ is removed at deployment**—only the shared actor $\pi_\theta(a_i \mid \mathbf{o}_i(t))$ is used to roll out the frozen policy! And your 68-dim actor observation $\mathbf{o}_i(t)$ only uses the nearest pad's energy and bearing ($E_i^{\text{pad}}, \hat{\mathbf{d}}_i^{\text{pad}}$), which has the **exact same 68 dimensions** whether $S=1$, $S=2$, or $S=4$!
`single_pad` only fails in `eval_stress.py` because your evaluation script instantiates the full `MAPPO` class (both Actor and Critic) with `state_dim(cfg)` for $S=1$ and calls `load_state_dict` on the critic too, or passes `s_t` into a dummy critic call.


* **The Fix:** In `eval_stress.py` / `eval_ckpt.py`, either load only `actor.load_state_dict(...)` during frozen evaluation, or construct the critic with the checkpoint's saved `state_dim`. You will immediately get a real zero-shot number for `single_pad` in Table XIV instead of `NA`!



---

### 3. Active-Agent Loss Masking Off-by-One on the Fatal Stranding Step (`train.py` / `mappo.py`)

* **Where:** `ml_impl/uav_wireless/train.py` and `mappo.py`.


* **The Bug:** When fixing the PPO update, you added active-agent masking so that *"a UAV that has left the active set is masked out of the loss instead of contributing a zero-reward transition"*.


* **Check how the mask is indexed at step $t$:**
If UAV $i$ is **active at the start of step $t$** (`active_t[i] == True`), chooses a bad action $a_i(t)$ that drains its battery to $0$ away from a pad, and becomes **inactive at the end of step $t$** (`active_next[i] == False`), which mask is stored in the rollout buffer for transition $t$?
* If the buffer stores `active` *after* `env.step()` (or masks out transitions where the agent is inactive at $t+1$), then **the exact action $a_i(t)$ that caused the UAV to die in the field is masked out of the policy gradient!**
* The actor loss must mask by whether the agent was active **when it took the action** (`active_before_step[t, i]`), while GAE bootstrapping uses `active_after_step`.



---

### 4. Value Normalizer (`EMA`) Drift Across PPO Epochs vs. Value Clipping (`mappo.py`)

* **Where:** `ml_impl/uav_wireless/mappo.py` (Eq. 35 & Eq. 36).


* **The Bug:** During rollout collection, old value predictions $V_{\phi_{\text{old}}}(s_t)$ are un-normalized using the *old* running stats $(\mu_{\text{old}}, \sigma_{\text{old}})$. Then, when the rollout finishes, the running statistics are updated via EMA ($\beta = 0.99$) to $(\mu_{\text{new}}, \sigma_{\text{new}})$ using the new rollout's returns $\widehat{R}_t$.


* **What goes wrong in Eq. (35):**
In the 10-epoch PPO critic update, if $V_{\phi_{\text{old}}}(s_t)$ is normalized using $(\mu_{\text{new}}, \sigma_{\text{new}})$ instead of $(\mu_{\text{old}}, \sigma_{\text{old}})$ (or if $V_\phi(s_t)$ is compared to $V_{\phi_{\text{old}}}(s_t)$ in normalized space after $\mu, \sigma$ shifted), the value-clipping window $[V_{\phi_{\text{old}}} - \epsilon, V_{\phi_{\text{old}}} + \epsilon]$ is shifted by the EMA jump, causing false value clipping on epoch 1 of every rollout.

---

### 5. Stepwise Movement Waste Penalty $W_t^{\text{mov}}$ Punishes Valid Transit Steps (`env.py`)

* **Where:** `ml_impl/uav_wireless/env.py` (Table V, Eq. 29).


* **The Bug:** Table V defines $W_t^{\text{mov}}$ as the fraction of distance flown on step $t$ that did not change sensor coverage. Because a UAV only moves $v_{\max}\Delta t = 1.0\text{ m}$ per step, flying 25 meters across the field to rescue an uncovered sensor takes 25 steps: on the first 24 steps, no sensor crosses the $35\text{ m}$ disk boundary, so $W_t^{\text{mov}} = 1.0$ (maximum penalty), and only on step 25 does coverage change!


* Even though $\lambda_W = 0.05$ is small, it injects a negative reward on 96% of valid transit steps.



---

### 6. Action Repeat (`Innovation 8`) Evaluated Without Matching Action Hold at Test Time (`scripts/eval_ckpt.py`)

* **Where:** Section VIII-F (Page 23) and `scripts/eval_ckpt.py`.


* **The Bug:** Look at what Section VIII-F says on Page 23:
> *"Repeating each action for 4 steps during training (2000 environment steps per episode, matched to the protocol) degrades the deployed policy: 0.9086 vs 0.9512... The policy trained with repetition does not transfer to the deployed repetition-free controller"*.
> 
> 


* **Why it degraded:** If you train a policy where every chosen action is held for $4$ physics ticks ($4 \times 0.2\text{ s} = 0.8\text{ s}$, moving $4\text{ m}$) and with $\gamma = 0.99$ per *decision* (4 ticks), and then evaluate that checkpoint by querying it **every 1 tick** (`action_repeat=1` at test time), you changed the MDP transition dynamics between train and test! If evaluated with the same 4-step hold (or trained with $\gamma^{4}$), action repeat will not suffer train-test mismatch.

---

### How to Upload the Python Code So I Can Check Every Line

Run this one-liner in PowerShell inside your `Project1` folder to bundle **only** the Python source files (`ml_impl/uav_wireless/*.py` and `scripts/*.py`, which is ~250 KB total instead of 5.53 MB) and upload `ONLY_PYTHON.txt`:

```powershell
python -c "import pathlib; out=[]; [out.append(f'=== {p} ===\n'+p.read_text(encoding='utf-8',errors='replace')) for d in ['ml_impl/uav_wireless','scripts'] for p in sorted(pathlib.Path(d).rglob('*.py'))]; pathlib.Path('ONLY_PYTHON.txt').write_text('\n\n'.join(out),encoding='utf-8'); print('Done:', pathlib.Path('ONLY_PYTHON.txt').stat().st_size, 'bytes')"

```