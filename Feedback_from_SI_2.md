# Review: why MAPPO isn't beating your reactive rule, and what to change

I read both attachments and the relevant parts of `mappo.py`, `train.py` and `env.py`. Your evaluation framework is careful work, and the feasibility certificate, paired intervals and claim audit are more rigorous than most student projects. The learner, though, hasn't had the same engineering. Several basic PPO implementation issues are big enough to explain most of the gap. That means the paper's current conclusion, that the residual is "consistent with the credit assignment of a shared team reward," is premature. Most of what you measured is an under-trained policy with an entropy bug. Credit assignment is probably a real second-order issue, but you can't see it yet.

The good news is that most of the fixes are cheap.

## Part 1: Bugs and implementation problems (fix first, hours of work)

### 1.1 The entropy bonus has the wrong sign

In `MAPPO.update()`:

```python
ent = -(p * logp.clamp(min=-1e8)).sum(-1)   # positive entropy H
...
loss = actor_loss + self.ent_coef * ent + self.vf_coef * critic_loss + 0.01 * adv_l2
```

`ent` is positive entropy, and you minimise `loss`. So this term penalises entropy instead of rewarding it. The standard form is `actor_loss - ent_coef * ent`.

This bug matches three things in your own logs:
- The G1 run (1000 episodes) collapses to entropy 0.093 at episode 675, and coverage falls from 0.82 to 0.35.
- Residual MAPPO (behaviour cloning init at 97% accuracy) collapses to entropy 0.000 and CK 0.450 on every seed.
- At 25 updates the bug barely matters, because there are too few steps for it to act, so entropy stays at 1.2–1.5.

Your memos read the collapse as "the shared team reward drives the policy toward determinism." The simpler explanation is that the loss was explicitly pushing it there. Fix this before re-reading any earlier conclusion.

### 1.2 "25 episodes" is only 25 gradient steps

`train_mappo` calls `agent.update(B)` once per episode, and `update()` takes a single `opt.step()` on the whole batch. There are no PPO epochs and no minibatches. So your headline result, the 8/16/25-episode budget sweep and every ablation arm were trained with 8, 16 or 25 gradient steps in total. Each step is clipped to grad-norm 0.5 at lr 3e-4. That is barely past initialisation.

Two pieces of your own evidence support this:
- **Argmax is far worse than sampling** (0.418 vs 0.674). A trained policy usually does as well or better under argmax. When sampling wins by 0.256, the policy is close to uniform. The sampled 0.674 is largely a masked random walk diffusing out of the corner cluster. Argmax then collapses to one preferred direction, which is the "rigid body" behaviour you saw.
- **The random-policy baseline was never run.** `analysis/random_baseline.py` exists but has no results. Run uniform-random-over-feasible-actions first. I expect it lands near 0.6, which would mean the learned policy is about as good as random. That is the most important diagnostic you don't have.

This also changes how to read your arms. The identity, observation, energy and local-critic arms could not show an effect because almost no learning happened in any of them. The narrow intervals tell you about an untrained network, not about those components.

PPO is meant to reuse each rollout several times. A standard update looks like this:

```python
def update(self, batch, epochs=10, n_minibatch=4):
    # flatten (T, N, ...) -> (T*N, ...); precompute normalised adv once
    idx = np.arange(T * N)
    for _ in range(epochs):
        np.random.shuffle(idx)
        for mb in np.array_split(idx, n_minibatch):
            # actor loss, critic loss, entropy on minibatch mb
            loss = actor_loss - ent_coef * ent          # note the minus
            self.actor_opt.zero_grad(); actor_loss_total.backward()
            clip_grad_norm_(self.actor.parameters(), 0.5); self.actor_opt.step()
            # separate critic step (see 1.3)
        if approx_kl > 0.02: break                       # early stop on KL
```

Also stop waiting for a full 2000-step episode before every update. Use rollouts of 400–500 steps and bootstrap at the cut, which your truncation handling already supports. That gives 4–5 updates per episode, each with about 10 epochs.

### 1.3 Smaller loss and optimizer problems

- **Shared optimizer and joint gradient clipping.** Actor and critic share one Adam optimizer and one `clip_grad_norm_(..., 0.5)` over all parameters. Critic gradients are usually much larger, so the joint clip shrinks the actor's update further. Use separate optimizers and clip each network separately. MAPPO's reference code does this.
- **The value loss doesn't match the paper.** The paper (Eq. 35) describes MAPPO's clipped value loss, `max(unclipped, clipped)`. The code uses plain MSE plus an ad hoc `0.01 * (new_val - old_val)²` term. Either implement the clipped form (or Huber loss) or correct the paper.
- **The EMA is backwards.** `_ret_mean = (1-b)*_ret_mean + b*batch_mean` with b = 0.99 puts 99% of the weight on the new batch, so there is effectively no smoothing. That is the opposite of what the paper says.
- **Inactive agents are in the loss.** Failed and exhausted UAVs get a zero observation and a hover-only mask. Their samples add nothing to the gradient but dilute the mean. Mask them out with an `active[t, i]` weight.
- **Return mode.** Check whether the environment overrides movement for UAVs in return or charge mode. If it does, the recorded actions don't match what was executed, and those samples should also be excluded.
- **Per-agent advantage normalisation does nothing.** Every agent receives an identical advantage, so normalising each agent over its own history gives identical results. Your code comment already notes this.
- **Initialisation.** Use orthogonal init with gain 0.01 on the policy head (the MAPPO/CleanRL default), and consider LayerNorm on the inputs. Both are trivial and usually help stability.

## Part 2: Training process (days of work, cheap compute)

### 2.1 Train on many layouts, not one

Each training run uses one fixed scene, set by its seed, and is evaluated on 5 unseen scenes. So you are measuring generalisation from a single sensor layout, while the rule needs no training at all. Resample sensor positions every episode (domain randomisation). Keep separate validation and test seed sets, choose checkpoints on validation, and report on test.

### 2.2 Compute budget

At about 8 ms per step on CPU, one 2000-step episode takes roughly 17 s. A reasonable budget fits on your machine:

| Budget | Env steps | Approx. time on one core | Notes |
|---|---|---|---|
| Current | 50k (25 episodes) | ~7 min | 25 gradient steps total |
| Recommended dev run | 0.5–1M | 1–2.5 h | with epochs and minibatches |
| Final run | 2M | ~4.5 h | 6 seeds in parallel overnight |

Two ways to stretch it further:
- **Develop with 2–3 seeds and a cheap configuration.** Save 8 seeds for the final table. Right now every iteration costs the full 8-seed protocol, which is why progress has been slow.
- **Profile the environment.** Most of the step time is the H-step BFS connectivity check, run for every candidate action of every agent. Vectorising it with numpy or `scipy.sparse.csgraph`, or caching distance matrices, could give 2–5×. Running 4–6 environment copies in worker processes for one seed also beats running everything sequentially.

### 2.3 Sanity check on a tiny problem

Before scaling up, train on something like N = 3, K = 1, 6 sensors, a 40 m field and 300-step episodes. If MAPPO can't reach the oracle there in about 30 minutes, the pipeline is still broken. Log approximate KL, clip fraction, explained variance of the critic, and entropy. Those four numbers would have exposed 1.1 and 1.2 immediately.

### 2.4 Keep the best checkpoint

G1 peaked at 0.82 at episode 500 before collapsing. Evaluate on validation scenes every N updates and keep the best policy. Once the entropy sign is fixed, the collapse should mostly go away, but checkpoint selection is good practice either way.

## Part 3: Modelling changes (likely the biggest gains once Part 1 is fixed)

### 3.1 Give the policy the information the "unprivileged" rule uses

`Reactive (local assignment)` reads the coverage count of every sensor within 2·R_cov and steers toward the nearest under-covered one. The policy gets a scalar count of locally covered sensors and a 4×4 deficit grid where each sensor contributes 1/M = 0.05. It never learns where the nearest under-covered sensor is. So the comparison isn't information-matched, even though the paper says it is.

Add, for the k = 3–5 nearest sensors within 2·R_cov:
- the relative position (dx, dy) / R_cov;
- the deficit (K − n_d) / K;
- a flag for "I am one of the K covering this sensor."

This is the same information the local rule uses, so it's fair. It also lets the policy learn "stay, I'm critical here" against "leave, this sensor is over-covered." Rescale the grid summary too, for example as a binary or count per cell instead of dividing by M.

### 3.2 Per-agent credit with difference rewards

A local critic can't fix credit assignment, and your paper correctly says why. A per-agent reward can, and for coverage it's cheap to compute exactly. The difference reward for agent i is:

D_i(t) = C_t − C_t^(−i)

This is the coverage lost if agent i vanished. Only sensors that agent i covers contribute, each adding (min(n_d, K) − min(n_d − 1, K)) / (K·M). Then use:

r_i = r_team + β·D_i, with β around 1.

Pair it with a per-agent value: a centralised critic V(s, one-hot i), or a critic over (s, o_i). This is the "per-agent signal rather than a better team signal" your conclusion identifies, and it's about 20 lines of code.

### 3.3 Shorten the decision horizon

Each action moves a UAV 1 m. With γ = 0.99 and λ = 0.95, credit flows back about 20 decisions (20 m) through a noisy shared reward, and the policy needs dozens of consistent decisions to cross the field. Two options:
- **Action repeat:** hold each action for 4–5 sub-steps, still checking the mask every sub-step and stopping if a move becomes infeasible, and lower γ to about 0.97. This also cuts policy calls.
- **Target-based macro-actions:** for example {hold, go to the j-th nearest deficient sensor (j = 1..3), go to the least-covered nearby grid cell, return to pad}, with `_move_toward` doing the low-level motion. Your paper already notes that agent-local targets avoid the rigid-body problem. The policy can then match the rule just by learning to pick option 1, and it beats the rule if it learns when to hold, when to yield a contested sensor, and when to charge early. I think this is the most realistic route to actually outperforming the heuristic.

### 3.4 Behaviour cloning, done properly

Your behaviour-cloning attempt failed mainly because of the entropy bug, plus three smaller problems:
- **Too little data.** 3 seeds × 500 steps only covers early-episode states. Collect full 2000-step episodes on many layouts, and add DAgger-style relabelling: roll out the cloned policy and have the rule label the states it visits.
- **No critic warm-up.** Pre-train the critic on rollouts of the cloned policy before any policy updates. A random critic produces garbage advantages that immediately wreck the cloned policy.
- **No anchor to the cloned policy.** Fine-tune at lr ≈ 1e-4 with an annealed KL or cross-entropy term toward the cloned actions, as in DAPG.

Alternatively, use a residual policy: execute the rule's action unless the learned head overrides it.

### 3.5 What you probably don't need

Attention or graph networks over neighbours, recurrent policies, and switching to HAPPO or QMIX are not needed yet. A 2×128 MLP is fine at N = 8. Revisit architecture only after Parts 1–3.1 are done.

## Recommended order

| # | Change | Expected impact | Effort | Compute |
|---|---|---|---|---|
| 1 | Fix entropy sign | High (removes collapse) | Minutes | None |
| 2 | Run random baseline | Diagnostic, essential | Minutes | Minutes |
| 3 | PPO epochs and minibatches, shorter rollouts, KL early stop | Very high | 1–2 h | None extra |
| 4 | Separate optimizers, mask inactive agents, orthogonal init, correct value loss | Medium | 1–2 h | None |
| 5 | Tiny-environment sanity check and diagnostic logging | Diagnostic | 2 h | 30 min |
| 6 | 0.5–2M-step budget, checkpoint selection | High | Low | Hours (overnight) |
| 7 | Randomise layouts per episode | High for unseen scenes | Low | Same |
| 8 | Local sensor features in the observation | High | ~Half a day | Same |
| 9 | Difference rewards with a per-agent critic | Medium–high | ~1 day | Same |
| 10 | Action repeat or macro-actions | High; also cuts compute | 1–2 days | Lower |
| 11 | Behaviour cloning with critic warm-up and KL anchor | Medium | 1 day | Low |

Items 1–7 alone may bring MAPPO close to the rule. Items 8–10 are what can plausibly push it past.

## Notes on the paper

- **Hold the arXiv submission.** The central negative result, and the arms "bounding" the gap, rest on 25 gradient steps and a sign-flipped entropy term. Re-run after Part 1. If MAPPO still trails the rule after proper training, that becomes a meaningful result; right now it isn't.
- **Small inconsistencies to fix:**
  - The arXiv pack's abstract says the gap is 0.309; the PDF says 0.298.
  - The paper describes clipped value loss and β = 0.99 smoothing, but the code does something else for both.
  - Table VIII's ε = 0.95 and λ = 0.05 look swapped or mis-set.
  - The paper says the reward's D term is a joint service violation; the code uses it for connectivity loss only.
- **Rebalance your time.** `AUTONOMOUS_STATE.md` repeats the same audit block dozens of times, and much of the sprint went into measurement and audit machinery. That rigor is valuable, but the next week is better spent on the learner itself. Basic RL diagnostics (KL, entropy, explained variance, random baseline) would have caught the two main bugs on day one.