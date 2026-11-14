# Reviewer B — Adversarial first reader (orchestrator's own review, after proxy models failed)

## Reviewer's summary verdict

This paper's central claim — "feasibility-certified evaluation" — is a geometric
covering bound ($N \ge 4K$) that says how many UAVs the region needs, not a
certificate that the policy's coverage is feasible. The policy is *measured*
against that bound, and the measurement shows it losing to a reactive heuristic
by 0.298 of persistent coverage. The "negative result" framing is the paper's
most honest move, but it is set up so the heuristic holds an information advantage
(the exact deficit set) the learned policy lacks (a 4x4 map), and the budget
(25 episodes x 2000 steps) is small enough that "lost" may mean "not yet
trained" rather than "cannot win." The paper is careful, self-aware, and
methodologically serious; it is also, in several places, claiming more than it
measures. A strong revise, not a reject, if the certificate is honestly
renamed and the information asymmetry is quantified.

## Findings (ranked)

1. **blocker** — `Mlawn-midsem-tex.tex:492,499,2669` — "feasibility-certified evaluation framework" / "A feasibility certificate". The certificate is a covering bound on $N$ for $K$-coverage, not a statement that the policy's coverage is feasible or certified. The policy is measured against it. CONFIRMED (read the definition at 849-860 and the audit at 2669).

2. **major** — `Mlawn-midsem-tex.tex:2067,2106` — "the identity raises the number of distinct actions a policy takes from 1.84 to 2.43 out of eight". Post-fix measurements: arm A 1.84, arm B 2.43, arm C 1.85. The map summary reverses the specialisation gain; the sentence as written implies the full progression. SUSPECTED (the fix is in flight; verify against ab_observation.json after re-run).

3. **major** — `Mlawn-midsem-tex.tex:2099-2102` — information asymmetry. The reactive heuristic is given the exact deficit set; the policy gets a 4x4 coverage-map summary. The paper acknowledges this ("part of the gap ... is a difference of information rather than of control") but does not quantify how much of the 0.298 gap is explained by it. CONFIRMED (read the observation section).

4. **major** — `Mlawn-midsem-tex.tex:1725-1730` (main table) — missing baselines: no random policy (analysis/random_baseline.py exists but has never been executed), no IL/BC policy, no single-agent PPO with a central controller, no greedy-with-memory. If any of these beat MAPPO, the paper's story changes. CONFIRMED (random_baseline.py unexecuted per GROUND_TRUTH).

5. **major** — `Mlawn-midsem-tex.tex:2809-2817` — "Fault-Tolerant" variant is never exercised in the headline run; the "no-reserve" row is vacuous on the base config (reserves never deplete). CONFIRMED (GROUND_TRUTH known-unfixed).

6. **major** — `Mlawn-midsem-tex.tex:1534` and `results_text.tex` — Vanilla row mislabelled; Independent-DQN epsilon ~= 0.91 at 20 episodes undisclosed. CONFIRMED (GROUND_TRUTH).

7. **minor** — `Mlawn-midsem-tex.tex:2147` (fixed) — dropped clause. CONFIRMED (fixed this session).

8. **minor** — `Mlawn-midsem-tex.tex:1266` area — W_t/D_t definitions vs Table IV. SUSPECTED (did not re-derive).

9. **minor** — `Mlawn-midsem-tex.tex:2817` — limitations section walks back the abstract's "feasibility-certified" framing; the abstract should be narrowed to match. SUSPECTED.

10. **minor** — `Mlawn-midsem-tex.tex:492` — "multi-agent reinforcement learning" in the abstract; the paper's headline result is that MARL loses. The abstract should lead with the negative result, not the method. SUSPECTED.

## Top 3 in full

1. **blocker — feasibility certificate overclaim.** The paper's first contribution is "a feasibility certificate: a rigorous covering bound on the number of UAVs required for K-coverage." That bound (N >= 4K) is real and proved, but it bounds the *region*, not the *policy*. Calling the evaluation "feasibility-certified" implies the policy's coverage is certified, which it is not: the policy is measured against a geometric necessary condition. A reviewer who reads Section III and the abstract side by side will notice. Fix: rename to "feasibility-aware evaluation" or "evaluation against a feasibility bound," and state explicitly that the certificate is a property of the instance, not of the controller. Evidence: 492, 499, 849-860, 2669.

2. **major — the negative result may be a budget artefact.** The learned policy is trained for 25 episodes of 2000 steps and evaluated against a reactive heuristic that is given the exact deficit set. The paper's own budget sweep (8 -> 16 -> 25 episodes) shows the coverage still rising (+0.026, +0.041, the last resolved at 2.8 SE) and the sweep's own interval upper bound (0.118) is below the gap (0.298), so more training does not close it *over that range* — but the paper does not show the curve flattening, and the heuristic's information advantage (exact deficit vs 4x4 map) is never quantified. A reviewer will ask: "would a compute-matched MAPPO with the same deficit information still lose?" The paper cannot answer. Fix: either give the policy the exact deficit set in one arm (a like-for-like ablation) or state the information asymmetry as a quantified upper bound on the gap it can explain. Evidence: 1902, 1908, 2099-2102, 2365.

3. **major — missing random baseline.** `analysis/random_baseline.py` exists and has never been executed. A paper whose headline is "learned policy loses to a heuristic" must show it beats random; without that row the lower bound on the claim is missing. Fix: run it (cheap, no training) and add the row. Evidence: GROUND_TRUTH known-unfixed; file exists.
