# Subagent 10 - Evolutionary / CEM / Black-Box Optimization (first-principles, 2026-10-30)

From ses_e76ee63e0ffeHRn7DV2UchjSU2 (Mercury 3, read-only).

## Reframed problem
LL: a controller whose per-episode CK on the fixed 5-scene protocol beats the reactive rule (0.740 single_pad; 0.716 small_battery) and is robust across seeds. Central paradox: the signal that matters is whole-episode (energy/return cycles decide coverage), yet every gradient learner converts that long-horizon signal into collapse or null credit (C3 null; BC-init PPO fell 0.818->0.45; MAPPO 0.60-0.75). PPO's failure is not representational - BC proves good policies exist in this exact network class. The failure is in the update rule, not the policy class.

## Ground truths
- [FACT] Env is deterministic given seed; eval is a function of (policy, scene), seeded and paired (repro_probe.py, README section 5).
- [FACT] bc_actor.pt (MLP 57->128->128->6, ~24.7k params) scores ~0.8-0.98; PPO fine-tune from it collapses (residual logs).
- [FACT] MAPPO-from-scratch: nominal mean 0.674, per-seed 0.60-0.75; single_pad seeds 0.36-0.75.
- [REASONED] Fitness noise is the classic ES killer; here it is near-eliminated by deterministic sim + common random numbers per seed.

## Why black-box search should win
ES/CEM optimizes exactly f(theta)=episode return - no critic, bootstrapping, value-normalization fragility (C8-class issues vanish), no gradient through rare return events. Updates are rank-based and elitist, so the incumbent can never regress below the BC start - an impossibility for the PPO that collapsed below its own init. Prior art: Salimans 2017 (ES rivals RL, long horizons, sparse rewards, scalar-only communication = perfect for 6 cores). GASS 2018 (ES/CEM solving cooperative multi-agent UAV swarm combat with sparse rewards). Drones 2024 (ES pre-training beats REINFORCE on UAV-swarm policies). Stulp & Sigaud 2012 (CEM/CMA-ES as policy-improvement backbone). Difference from closest art: evolutionary fine-tuning from a BC warm start under a strict paired-eval protocol vs a strong handwritten rule, in persistent K-coverage with charging/failure.

Full CMA-ES is infeasible at d~25k (O(d^2) covariance); use diagonal/separable CEM (O(d) memory), exactly the OpenAI-ES regime.

## Recommendation (portfolio)
- Best bet - CEM-from-BC: mean = bc_actor.pt weights; diagonal Gaussian per-layer sigma_0~0.05; lambda=48, elite mu=10, elitism, sigma halves on stagnation; fitness = team-reward sum (Eq. 28) over 1 CRN eval seed per candidate for selection; top-5 elites re-evaluated on the full 5-scene protocol; report CK/AG/SC. Action masking unchanged; trained the protocol's seeded-sampling eval (argmax degenerates under sharing).
- Cheap option - do first: evaluate the existing BC actor alone under the strict 5-scene protocol per scenario (~1 h). It may already clear the bar; sets the baseline for CEM's marginal gain.
- High-variance arm - CEM-from-scratch (larger sigma, restarts): isolates whether BC init is load-bearing or merely speed.

## Stress test / premortem
Top risks: (1) fitness noise from sampled actions swamps ranking - mitigated by CRN + same eval seed per generation; (2) sigma too small -> no gain, too large -> averages away structure - adaptive halving + elitism; (3) symmetric-observation degeneracy - agent ID already in obs; (4) CEM finds a local optimum above BC but below rule - that is the falsification case.

## TEST (cheapest decisive)
Scenarios: single_pad, then small_battery. 30 generations, lambda=48, 6 parallel workers (~6-8 h, same scale as existing runs). Success: best-elite median CK on the 5-scene protocol >= 0.78 AND >= BC-init CK + 0.03, with AG/SC not below the rule's.

## KILL RULE
Kill after 30 generations if best-elite median CK < max(rule CK, BC CK + 0.03); or if no elite exceeds BC-init fitness by one eval-spread by generation 10; or if elitism still regresses (harness bug).

## CONFIDENCE
- [FACT] Deterministic paired eval; BC scores; PPO collapse; MAPPO spread - all read from artefacts.
- [REASONED] ES/CEM avoids the exact failure modes observed (critic/credit/value fragility): Salimans 2017, GASS 2018, Drones 2024.
- [SPECULATIVE] A >=0.03 improvement over BC via <=30 generations of fine-tuning is achievable - precisely what TEST falsifies.
- Sources: Salimans et al. 2017 (ES), GASS 2018 (cooperative UAV swarm), Drones 2024 (ES pre-training), Stulp & Sigaud 2012 (CEM/CMA-ES as policy improvement).
