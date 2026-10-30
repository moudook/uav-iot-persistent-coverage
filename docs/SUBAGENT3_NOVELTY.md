# Subagent 3 - Novelty & Positioning Audit (first-principles, 2026-10-30)

From ses_e770378a4ffe7LTySeXP3Rqcp2 (Mercury 3, read-only). URLs verified live.

## Verified landscape
- TAG-MAPPO (arXiv 2602.10029): real. Topology-aware graph MAPPO, 3D UAV aerial-ground networks under node failure; graph attention + permutation-invariant random observation shuffling; self-healing restores >90% coverage in 15 steps; ~50% fewer handoffs. Positive result.
- Fan et al., "Communication-Aware MARL for Decentralized Cooperative UAV Deployment" (DroneConnect, arXiv 2603.16141): real, SINGLE CLOSEST THREAT. Graph-based MARL under CTDE, partial observability, intermittent P2P connectivity as SNR-threshold connectivity graph conditioned on channel model; compares against MILP offline oracle upper bound; +12% coverage over MAPPO.
- CALF (arXiv 2603.12543): real but mis-framed in NOVELTY.md - general Communication-Aware Learning Framework for Distributed RL (training under delay/jitter/packet-loss), not coverage MARL with failure. Closest textual match to "train under network models" but not UAV/K-coverage specific.
- RayNet (arXiv 2302.04519): OMNeT++ + Ray/RLlib platform (infrastructure, not a verdict).
- Isaac-Net / "Network-in-the-Loop at Scale" (arXiv 2610.02370, Oct 2026): explicitly occupies the term "network-in-the-loop" (GPU-batched 5G NR for massively parallel robot learning).
- FlyNetSim (arXiv 1808.04967): ns-3 + ArduPilot, no RL loop.

## Novelty verdict per contribution
- C1 (network-in-the-loop, OMNeT++/INET co-sim): Incremental as platform (RayNet, Isaac-Net exist). Novelel as verdict: certifying ideal-observation assumptions hold at 80 m scale (PDR 0.9975, 22x margin, MAC contention negligible) is a real, defensible negative/sanity result. "Network-in-the-loop" brand is taken (Isaac-Net).
- C2 (topology-conditioned information model + training): NOT novel / weak. Fan et al. (SNR-threshold connectivity graph) and TAG-MAPPO already live in this space.
- C3 (redundancy/criticality credit): NOT supported; own data show no significant gain (p~0.66/0.68). Retract as headline.
- C4 (feasibility certification evaluation: packing bound + oracle ceiling + headroom gate + rliable): THE GENUINELY NOVEL CONTRIBUTION. "Oracle ceiling / headroom" language circulates in LLM evals but not as formal feasibility + significance gating method for MARL coverage with energy/failure constraints. Combined with honest null result, publishable and hard to scoop.

## Recommended positioning & venue
Lead with C4 + honest null result. Story: "a disciplined method for deciding whether a MARL coverage result is meaningful (packing-bound feasibility, oracle ceiling, headroom gate, rliable stats), applied to UAV-IoT K-coverage where an INET co-simulation certificate proves radio is not binding, and converged MARL variants do not beat a well-tuned reactive rule."

Venues in order:
1. IEEE INFOCOM / WCNC / Globecom (INFOCOM stretch, WCNC achievable)
2. IEEE IoT-J (fast, tolerant of honest framing)
3. ML venue/workshop (ICML/NeurIPS RL-Evaluation/AI4Sys) if re-centered on method.

Do NOT target pure ML conference on strength of C1-C3.

## Top novelty threats & differentiation
1. Fan et al. (2603.16141): same graph/communication-aware MARL + oracle-upper-bound comparison but POSITIVE result. Differentiate: (a) we certify via OMNeT++/INET packet-level realism, not analytical SINR graph; (b) persistent K-coverage with battery/recharging/failure reserve; (c) our oracle is a provable packing/ceiling bound, and headline is verified null result, not a 12% gain.
2. TAG-MAPPO (2602.10029): topology-aware resilience, positive self-healing. Differentiate: learned policies fail to beat tuned rule under energy/failure stress; casts doubt on transferability of such claims.
3. CALF (2603.12543) + Isaac-Net (2610.02370): they show training under network models helps in their settings. Differentiate: in OUR certified regime network is provably not binding, so communication-aware training cannot help - cleaner falsifiable claim.

## Proposed title + abstract
Title: "Certifying Feasibility and Reporting Null Results for Fault-Tolerant Persistent K-Coverage MARL: An OMNeT++/INET Network Certificate"

Abstract: MARL is widely claimed to solve persistent K-coverage with UAV-IoT swarms under energy, charging, and failure constraints. We ask a prior question: is the problem even feasible, and are the simulation's information assumptions valid, such that an RL comparison is meaningful? We contribute (i) a feasibility-certification evaluation: packing bound, oracle ceiling, headroom gate, and rliable statistics that decide whether an RL result is analytically possible and statistically non-degenerate; and (ii) a network certificate from OMNeT++/INET co-simulation showing at 80 m mission scale IEEE 802.11 radio is not the binding constraint (PDR 0.9975, ~22x range margin). Under this certified regime, converged MAPPO and its credit-assignment, behavior-cloning, and topology/communication-aware variants do not beat a well-tuned reactive rule; stress regimes merely prevent collapse. The contribution is not a better learner but a falsifiable method for knowing when coverage-MARL results are meaningful, plus a rigorously supported null result.
