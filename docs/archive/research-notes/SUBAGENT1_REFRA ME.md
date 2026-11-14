# Subagent 1 - Paper Thesis Reframe (first-principles, 2026-10-30)

From ses_e770378a9ffeaFRMbc0H9t912n (Mercury 3, read-only).

## Reframed thesis

The paper's defensible core is a rigorous feasibility certification of MARL for persistent K-coverage, not a performance win:

> Under a pre-registered, converged, 5-seed protocol with a certified network-in-the-loop simulator, a hand-designed reactive rule equals or beats MAPPO in all five stress regimes (best case: tie in multi-failure, delta = -0.003; otherwise rule wins by 0.09-0.35 CK), and the residual gap to the oracle ceiling is governed by coverage/energy geometry, not communication.

Inverts "learning beats rule" into "certifying where learning does NOT help, and why."

## Surviving / dropped contributions

Survives (rebuilt):
- C1 network certificate -> reframed as a NEGATIVE scope result: at 80 m, PDR ~0.998, range margin 22x, so network is not the binding constraint. Network-realism is not where headroom lives.
- C4 evaluation methodology -> becomes the CENTERPIECE making negative results trustworthy (pre-registration, converged budgets, headroom gate, rliable IQM, disjoint train/tune/test). Precedent: Henderson et al. 2018, Jordan et al. 2020.
- NEW positive mechanism finding: stress regimes prevent the entropy collapse that kills nominal MAPPO (collapse at ep 675; none under stress).

Dropped / demoted:
- C3 credit -> report as null result (p=0.66/0.68), not a headline.
- Residual MAPPO -> cautionary negative: BC-init strong alone (CK 0.8-0.9) but PPO fine-tuning drives entropy to 0, degenerate CK=0.4500.
- C2 topology-conditioned model -> never run; move to future work, not a contribution.

## Proposed outline (6 pages IEEE)

1. Introduction - feasibility certification + null-result study; scope boundary up front.
2. System model - Dec-POMDP, K-coverage, charging, failure, connectivity; packing bound N>=4K.
3. Evaluation methodology (C4) - pre-registration, converged budgets, headroom gate, rliable, disjoint splits. Headline: all 5 regimes pass headroom gate (ceiling - best rule >= 0.10).
4. Network-realism certificate (C1) - OMNeT++/INET co-sim, PDR(d) model, network not binding (PDR 0.998 @ 80 m; 22x range margin).
5. Main result - MAPPO vs reactive rule, 5 regimes: rule >= MAPPO in 4/5, tie in multi-failure. Table: rule 0.68-0.74; MAPPO 0.37-0.71.
6. Mechanism diagnosis - entropy collapse, stress preventing collapse, residual degeneracy, C3 null.
7. Discussion/related work - where learning could still matter (larger swarms, network-bound regimes, long-horizon delayed effects).
8. Conclusion.

Abstract headline numbers: rule wins/tie in 5/5 regimes; residual MAPPO degenerate at 0.4500; C3 p=0.66; network PDR 0.998; stress eliminates collapse.

## Risks

1. Reviewer rejects "negative result as contribution" -> lead with C4 methodology, precedent citations, one clean falsifiable claim with scope boundary, "where learning still wins" section.
2. Baseline unfairness (rule has ideal info vs learner partial) -> publish rule fully, tune under same protocol, state information advantage, add fair-information variant.
3. Generalizability overreach (single simulator) -> frame as certification case study at defined operating point; anchor with packing bound; bound C1 to studied scale (N=16, one channel, 0.1s interval).
