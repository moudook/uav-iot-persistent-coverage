# Paper Outline (G5 prep, 2026-10-26)

## Title
"The Swarm Is Its Own Network: Network-in-the-Loop MARL for Persistent Fault-Tolerant K-Coverage in UAV-IoT"

## Abstract (problem -> idea -> method -> 2-3 headline numbers)
- Problem: persistent K-coverage UAV-IoT with charging, failures, connectivity. Existing MARL assumes perfect info.
- Idea: network-in-the-loop evaluation + topology-conditioned training.
- Method: OMNeT++/INET co-sim, information channel model, C3 credit, residual MAPPO.
- Numbers: (TBD from experiments)

## Contributions (at most 4)
- C1: Network-in-the-loop evaluation (OMNeT++/INET co-sim, PDR/delay as first-class metric)
- C2: Topology-conditioned information model + training (delivery/age as function of topology)
- C3: Redundancy- and criticality-aware credit (K-coverage marginal, connectivity criticality, delivery criticality)
- C4: Fair, falsifiable evaluation (converged, tuned, headroom-gated, rliable stats)

## Sections
1. Introduction (problem, gap, contributions)
2. System model (Dec-POMDP, coverage, connectivity, energy, charging, failure)
3. Feasibility-certified evaluation (packing bound, oracle ceiling, non-degenerate metrics) [from midsem]
4. Network-in-the-loop (C1): OMNeT++/INET co-sim, trajectory replay, Step A measurements
5. Information channel model (C2): fit delivery/age vs topology, training under it
6. Learning (C3 + residual): per-agent credit, rule-anchored MAPPO, ablations
7. Experiments: headroom-gated regimes, converged budgets, rliable stats, sanity ordering
8. Results: (a) learning wins, (b) rules win but topology-aware narrows gap, (c) no advantage
9. Conclusion

## Status
- G0: done
- G1: done (entropy collapse found)
- G2: Step A partial (sim runs), Step B not started
- G3: single_pad done, small_battery+low_comm running, failure+multi_failure not started
- C3: implemented, smoke tested
- Residual MAPPO: BC training done (97% acc), PPO fine-tune smoke tested
- Paper: outline only
---
