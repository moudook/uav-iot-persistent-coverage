# Subagent 2 - Algorithm Proposal (first-principles, 2026-10-30)

From ses_e770378a7ffe8r56wiPA2wT39u (Mercury 3, read-only).

## Reframe
Goal: a controller whose time-averaged K-coverage exceeds 0.74 (single_pad) / 0.716 (small_battery), on same 2000-step episodes. Central paradox: hand rule already near ceiling (oracle ~1.0, headroom 0.29-0.63); simulator near-deterministic and geometry-driven, so pure learning has little to discover and everything to destroy. Binding difficulty is stability near a strong solution, not acquisition.

## Key facts
- Charging and serve->return are physics-forced (env.py 1125-1142): the policy does not decide when to return, only where to fly. Action relevance mostly spatial allocation.
- BC alone scores 0.8-0.9; PPO fine-tuning crashes to CK=0.45 with entropy->0. A good policy exists and is destroyed by PPO. Highest-information result in repo.
- C3 per-agent credit null (p~0.66/0.68) -> credit assignment likely not the binding bottleneck.
- Performance strictly bounded by action mask (connectivity/energy/articulation); rule and learner share it, so gap is control quality, not feasibility.
- ASSUMPTION: the rule's edge partly stems from information privilege (global uncovered set). Compare learned policies to reactive_local, not global reactive, else comparison conflates info asymmetry with control.
- UNKNOWN: whether entropy-collapse is root cause or symptom of noisy critic under 400k steps (PREREG target 2e6).

## Failure modes
- Fine-tuning with tiny entropy bonus (ent_coef=0.01) lets policy trust noise-degraded value estimates -> degenerate fixed schedule.
- Team reward + shared actor -> all agents imitate each other (symmetric action collapse).
- 2000-step horizon concentrates credit in critic that must predict joint-state dependence, injecting noise into every advantage.

## Candidates
A. KL-anchored residual fine-tuning (RECOMMENDED): keep BC policy as reference pi_BC; add forward-KL trust region (or line-searched KL cap) + explicit entropy floor when fine-tuning with PPO. ANCHOR/KL-anchored offline->online recipe; documented fix for RLFT entropy collapse. Assumes collapse is binding failure and good behavior already in pi_BC. Cost: small change to MAPPO.update + reuse bc_actor.pt; ~1h/seed. Falsifier: if hard KL cap cannot hold entropy > 0.2 or CK >= 0.75, the anchor itself is faulty.

B. Value decomposition (QMIX/VDN/QTRAN): factorized joint value gives per-agent advantage. Assumes coordination bottleneck - but C3 null suggests otherwise. Cost: new learner + off-policy replay, sample-hungry, more engineering. Falsifier: if A beats reactive, B dominated; if A fails, B worth a run.

C. Model-predictive lookahead (CEM over joint actions using exact simulator): env deterministic and fully known; rollouts directly optimize coverage gain. Assumes model fidelity and acceptable compute. Cost: 8 agents x ~6 actions per step with SINR/connectivity physics -> dominates runtime. Falsifier: if perfect-model MPC also cannot beat reactive, reactive is near-optimal under the mask and there is nothing to learn. Useful as ceiling probe, not primary claim.

## Recommendation: Candidate A
Justification: targets empirically confirmed failure (PPO destroying a policy that already beats reactive), reuses existing assets, cheapest, and the only candidate whose success directly converts "BC >= reactive" into "learned >= reactive". B lost on evidence (C3 null) and cost; C is a planning benchmark, not a learning result.

## Cheapest falsifiable test
- Hypothesis: KL-anchored (forward-KL capped, entropy floor) PPO fine-tuning of bc_actor.pt holds CK >= 0.78 and ends entropy > 0.2 on single_pad, beating reactive_local.
- Setup: single_pad, 5 seeds, 200 ep x 2000 steps (~1h/seed, parallelizable ~1h wall on 6 cores).
- Success: mean CK >= 0.78 and entropy > 0.2; superiority over reactive/reactive_local via paired per-seed comparison.
- Kill rule: if by episode 100 CK < 0.75 or entropy < 0.1, stop -> falsifies collapse-as-bottleneck; escalate to B or C. Same 5 seeds for clean A vs rule comparison.
