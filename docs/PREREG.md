# PREREG — pre-registration for the network-in-the-loop sprint

Written before main experiments. Commit hash recorded at the bottom.

## Hypotheses
- H1: Under converged budgets, a tuned rule (ideal info) still beats MAPPO (team reward) on persistent K-coverage in the nominal regime (headroom gate R6: ceiling - best rule >= 0.10 required for a "main" result).
- H2: Policies trained with topology-conditioned information keep K-coverage and connectivity better in closed-loop OMNeT++ than policies trained under ideal information and under i.i.d. loss (CALF-style), because they learn to protect the links that carry their own information.
- H3: C3 credit (K-coverage marginal + connectivity criticality + delivery criticality) improves over team reward, and is distinguishable from Sun 2023's WLU (age-based, 1-coverage, no connectivity).
- H4: Residual/rule-anchored MAPPO (rule prior + PPO fine-tuning) is never worse than the rule, so any gain is attributable to learning.

## Metrics (primary)
- Persistent K-coverage C_K (time-averaged fraction of sensors with >=K coverage, serviceable links only).
- Service continuity SC (binary; reported but not primary due to degeneracy on infeasible instances).
- Sensor->sink PDR and end-to-end delay (first-class metric for C1).
- Connectivity: connected-component count, articulation-point count, mean node degree.
- Energy: stranded UAVs, charging contention events, mean battery.

## Seeds
- Main methods: >=10 seeds.
- Ablations: >=5 seeds.
- Disjoint TRAIN / TUNE / TEST scene seeds (R4).

## Budgets
- Target >=2e6 env steps per seed for main methods (R3).
- Convergence criterion: IQM of last 10% of training within 1 bootstrap SE of previous 10%, OR hit pre-registered max budget.
- Throughput measured: 231.8 steps/sec single env (2026-10-25). Vectorized target: 32-128 parallel envs.

## Analysis
- rliable IQM with stratified-bootstrap 95% CIs.
- Paired comparisons where possible; report effect sizes.
- Sanity ordering: random < hover < rule <= oracle ceiling (R9).

## Stopping rules
- Kill on NaN, entropy collapse before 10% budget, diverging value loss.
- Headroom gate: only report a regime as "main" if ceiling - best tuned rule >= 0.10.

## Deviations log
(none yet)

---
Commit hash: (to be recorded after first commit of this file)
---
