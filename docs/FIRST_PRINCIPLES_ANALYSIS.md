# FIRST-PRINCIPLES ANALYSIS OF THE INNOVATION PORTFOLIO

Mode: FULL (novel problem, high cost of error, architecture decision)

## Stage 1 - Reframe
Goal: publish a research paper. The current report is a methodological paper
(certification + corrected protocol). To be research-level publishable it needs
an ALGORITHMIC contribution that (a) is novel, (b) has measurable impact,
(c) is tested under the certified protocol.

## Stage 2 - Expose assumptions
- ASSUMPTION: the learner fails on small_battery because it never saw depletion
  (cost to test: low - curriculum experiment running).
- ASSUMPTION: the learner fails on clustered because it can't perceive the full
  swarm (cost: medium - needs attention, not yet implemented).
- ASSUMPTION: energy-aware shaping will help small_battery without hurting
  nominal (cost: low - experiment running).
- ASSUMPTION: difference credit helps (cost: low - diff2 running, preliminary
  +0.007).
- ASSUMPTION: the "learning does not help" thesis is still defensible on at
  least one regime (currently small_battery -0.064, clustered -0.038).
- UNKNOWN: whether any single innovation closes both failure modes.

## Stage 3 - Ground truths (irreducible constraints)
1. Physics: a UAV at 1m/s over 80m field, 2000 steps = 400s, battery depletes
   only under stress (B_max=15kJ). Energy is NOT the binding constraint on
   nominal; it IS on small_battery (B_max=15kJ, E_reserve=1kJ).
2. Information: the policy is shared and decentralized; it sees only local obs.
   The global state (which sensors are uncovered) is available only via the
   critic during training. The reactive rule gets the EXACT deficit set.
3. Feasibility: N>=4K=8 is the hard lower bound; the oracle is 1.000.
4. Compute: 200 episodes x 2000 steps ~ 50 min per seed on CPU. 3 seeds per
   config is the minimum for a citable mean.

## Stage 4 - Invert (what guarantees failure)
- Training on nominal only -> zero-shot failure on stress regimes (already
  observed: small_battery -0.064).
- Not reporting the random baseline on the SAME config -> "below random"
  false claim (already retracted).
- Comparing train-CK to eval-CK -> false comparisons (already fixed).
- Claiming a gain that doesn't exclude zero -> reviewer rejection.
- A single "does learning beat the rule" number hides regime dependence.

## Stage 5 - Reconstruct (candidate approaches)
Approach A: "Certification + corrected protocol" (current paper). Methodological.
  Novelty: medium. Publishability: needs a venue that values methodology (e.g.,
  IEEE TMC, IEEE IoT Journal). Risk: reviewers ask "where's the algorithm?"

Approach B: "Energy-aware curriculum MARL" (innovations 1+2+4). Algorithmic.
  Novelty: medium-high (curriculum over battery stress is uncommon).
  Testable: yes, running now. Risk: may not close small_battery.

Approach C: "Graph-attention MARL with feasibility-aware planning" (innovations
  6+10). Algorithmic. Novelty: high. Testable: needs implementation (1-2 days).
  Risk: implementation complexity, may not improve.

Approach D: "Hybrid belief + attention" (innovations 6+7 from HBRL paper).
  Novelty: high. Testable: needs LGCP + attention (2-3 days). Risk: too much.

## Stage 6 - Verify
Falsifier for Approach B: if curriculum+energy shaping does NOT improve
small_battery (still -0.06), then the "energy management" hypothesis is wrong
and we need a different mechanism (e.g., explicit recharge planning).

Cheapest empirical check: the running experiment (3 seeds, ~2.5h). If it
fails, pivot to Approach C.

Reversibility: all experiments are additive (new config flags, new .pt files);
nothing is deleted. Checkpoints preserved.

## Stage 7 - Artifact
Decision: run Approach B first (in flight). If it closes small_battery, combine
with diff credit (already +0.007) and test the combined config on all
regimes. If it fails, pivot to Approach C (graph attention) for the spread
start regime.

The publishable story either way:
- If B works: "MARL beats tuned rules on persistent UAV coverage once
  correctly trained, and the certification framework tells you which regimes
  still fail."
- If B fails: "even corrected, learning fails on energy management; the
  certificate identifies the regime and the mechanism (no depletion in
  training)."
Both are honest, novel, and use the certificate as the contribution.
EOF
echo done