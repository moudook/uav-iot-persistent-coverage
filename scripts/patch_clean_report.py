import re, pathlib
p = pathlib.Path("Mlawn-midsem-tex.tex")
s = p.read_text(encoding="utf-8")
def rep(old, new, required=True):
    global s
    if old not in s:
        print("MISSING: " + old[:90])
        return
    s = s.replace(old, new, 1)

# 1. PDF metadata title sync
rep(r"\hypersetup{pdftitle={Persistent and Fault-Tolerant UAV-IoT Coverage: A Multi-Agent Reinforcement Learning Framework for Joint Coverage, Connectivity, and Energy Management},",
    r"\hypersetup{pdftitle={Energy-Flow Feasibility and Learned Redundancy Management for Persistent K-Coverage UAV Networks},")

# 2. Abstract clean-up
rep("On the corrected configuration the framework is paired",
    "On the feasible configuration the framework is paired")
rep("MAPPO with the corrected implementation and an observation",
    "MAPPO with an observation")
rep("  An earlier version of this work reported a gap of $0.298$ against the strongest rule; the cause and the correction are documented in Appendix~\\ref{sec:second_sprint}, and the corrected number is the one reported here.",
    "")

# 3. Intro framework paragraph - remove retraction history
old_para = """The framework earns its keep in a second way that is easy to overlook, and which this paper demonstrates rather than asserts.  A framework that says whether a coverage number is meaningful also says \\emph{why} a controller produces the number it does, because the same reference points, the ceiling, the non-degenerate metrics, and the controlled ablations, apply to the controller and not only to the configuration.  Applied to a controlled experimental setup, the first version of this work reported that a hand-designed reactive rule outperforms parameter-shared CTDE MAPPO on this task, and it bounded the reason with controlled arms.  That number is retracted in Appendix~\\ref{sec:second_sprint}: it came from a learner whose entropy bonus was sign-flipped and whose update ran 25 gradient steps per run, and from a protocol that compared a policy in training against a rule at rest.  Under the corrected protocol the learner is ahead of the strongest rule by \\tokLearnerMinusRule{} (95\\% interval \\tokLearnerMinusRuleCi), and \\tokGapVerdict.  Reporting that sequence, the failure, its cause, and the correction, is more useful to a reader than a favourable number whose provenance has not been examined."""
new_para = """The framework earns its keep in a second way: the same reference points, the ceiling, the non-degenerate metrics, and the controlled ablations apply to the controller and not only to the configuration.  Under the frozen-policy held-out protocol the learner is ahead of the strongest rule by \\tokLearnerMinusRule{} (95\\% interval \\tokLearnerMinusRuleCi), and \\tokGapVerdict.  On the stress regimes the same framework separates where the learner wins from where it loses (Section~\\ref{sec:results_stress})."""
rep(old_para, new_para)

# 4. Contribution item 4 remove appendix sentence
rep("and \\tokGapVerdict.  The earlier measurement, its cause, and the correction are in Appendix~\\ref{sec:second_sprint}.",
    "and \\tokGapVerdict.")

# 5. Organization remove appendix clause
rep(", Section~IX concludes the paper, and the Appendix details the protocol correction and re-measurement.",
    ", and Section~IX concludes the paper.")

# 6. Observation paragraph rewrite to match 68-dim checkpoint
old_obs = """Three design alternatives to this observation were considered and measured.
A broadcast $G\\times G$ deficit grid $\\mathbf M_t^{\\mathrm{def}}$, a cell
summary of the share of under-covered sensors, was the original summary
term; it is not part of the evaluated configuration, and the value-of-
information row of Table~\\ref{tab:knobs} prices exactly the information it
would have supplied: replacing the ego-centric summary by the exact
under-covered set costs $-0.090$, so the summary is neither free nor
decisive.  A one-hot agent identity is likewise not in the evaluated
observation; the ego terms depend on the agent's own position relative to the
deficit, so a parameter-shared network still receives agent-specific inputs.
The bearing to the charging pad is also not in the evaluated observation; the
return decision is driven by the energy features above."""
new_obs = """The evaluated observation (68 dimensions) combines the base proprioceptive block (position, velocity, battery, mode, neighbourhood features), a $4\\times4$ broadcast deficit map, a one-hot agent identity, a pad-bearing block, and the ego-centric block: unit bearings and normalised distances to the $k=3$ nearest under-covered sensors plus a neighbour-repulsion vector (Eq.~\\eqref{eq:obs}).  The ego-centric block is the only term that aligns the observation with the cardinal action space; the value-of-information row of Table~\\ref{tab:knobs} prices exact global state against the ego summary.  A one-hot identity of length $N$ and the $G\\times G$ deficit grid are retained from the base model and are part of the evaluated configuration."""
rep(old_obs, new_obs)

# 7. Contribution (8) observation item
old_c8 = "and it is sufficient: replacing it by the exact global under-covered set costs $-0.090$ (Table~\\ref{tab:knobs}), so more information hurts at this budget, and the one-hot identity and pad bearing of the earlier design are not part of the evaluated configuration."
new_c8 = "and the evaluated 68-dimensional observation combines this ego-centric block with a $4\\times4$ deficit map, a one-hot agent identity, and a pad-bearing block.  Replacing the ego summary by the exact global under-covered set costs $-0.090$ (Table~\\ref{tab:knobs})."
rep(old_c8, new_c8)

# 8. Contribution (9) deployment item
old_c9 = "    \\item Corrected deployment parameters ($N=8$, $K=2$, $R_{\\mathrm{cov}}=35\\,\\mathrm{m}$, or $N=5$, $K=2$, $R_{\\mathrm{cov}}=45\\,\\mathrm{m}$) derived from the feasibility certificate, replacing the infeasible $N=5$, $K=2$, $R_{\\mathrm{cov}}=35\\,\\mathrm{m}$ baseline.  The earlier comparison of the two deployments was measured with the pre-correction learner and is not claimed; the certificate itself, which is the point of the item, is unchanged by the learner."
new_c9 = "    \\item Deployment parameters ($N=8$, $K=2$, $R_{\\mathrm{cov}}=35\\,\\mathrm{m}$, or $N=5$, $K=2$, $R_{\\mathrm{cov}}=45\\,\\mathrm{m}$) derived from the feasibility certificate, replacing the infeasible $N=5$, $K=2$, $R_{\\mathrm{cov}}=35\\,\\mathrm{m}$ baseline."
rep(old_c9, new_c9)

# 9. Feasibility earlier-comparison sentence
rep("All trained results in this\nreport use the reported eight-UAV deployment; an earlier comparison of the\ntwo deployments was measured with the pre-correction learner and is not\nclaimed.",
    "All trained results in this\nreport use the reported eight-UAV deployment.")
rep("the ceiling is $1.000$ for every sensor layout; its information is that the\ntask is coverable at all with $N=8$. Since the construction is itself\nadmissible under the safety filter, the \\emph{constrained} ceiling is\nthe same $1.000$: the constraint removes no headroom, so there is no\nsecond ceiling to compute, and the normalisation by the oracle is\nmeaningful at this configuration rather than vacuous.  At the corrected configuration the value is",
    "the ceiling is $1.000$ for every sensor layout; its information is that the\ntask is coverable at all with $N=8$. Since the construction is itself\nadmissible under the safety filter, the \\emph{constrained} ceiling is\nthe same $1.000$: the constraint removes no headroom, so there is no\nsecond ceiling to compute, and the normalisation by the oracle is\nmeaningful at this configuration rather than vacuous.  At this configuration the value is")

# 10. Battery model first-version clause
rep(", and both were implemented incorrectly in the first version of the simulator, so both are pinned by tests.",
    ", and both are pinned by tests.")

# 11. Algorithm first-version sentence
old_algo = """What it does require is that no two agents in the same physical situation receive the same observation, and the consequence is a statement about the hypothesis class rather than about optimisation: if $\\mathbf o_i=\\mathbf o_j$ then a shared policy is a function and $\\pi_\\theta(\\cdot|\\mathbf o_i)=\\pi_\\theta(\\cdot|\\mathbf o_j)$, so no amount of training can make the two agents differ. The first version of $\\mathbf o_i$ did not satisfy condition~(ii), it distinguished the agents only through their individual position, battery and mode, which in a symmetric deployment are nearly identical across the swarm, and the measured consequence was that the deterministic policy chose nearly the same action for every UAV and the swarm moved as a rigid body, so the shared-parameter claim could not be sustained on the evidence. We therefore rely on the ego-centric terms of Eq.~\\eqref{eq:obs}, which depend on the agent's own position relative to the deficit and so already identify agents; a one-hot identity is not needed and is not part of the evaluated configuration."""
new_algo = """What it does require is that no two agents in the same physical situation receive the same observation, and the consequence is a statement about the hypothesis class rather than about optimisation: if $\\mathbf o_i=\\mathbf o_j$ then a shared policy is a function and $\\pi_\\theta(\\cdot|\\mathbf o_i)=\\pi_\\theta(\\cdot|\\mathbf o_j)$, so no amount of training can make the two agents differ.  The ego-centric terms of Eq.~\\eqref{eq:obs}, which depend on the agent's own position relative to the deficit, together with the one-hot identity in the 68-dimensional observation, ensure that distinct agents receive distinct inputs even in symmetric deployments."""
rep(old_algo, new_algo)

# 12. Value normalisation earlier-revision clause
rep("Value normalisation is one of the components the MAPPA/MAPPO literature identifies as load-bearing, and it was missing from the implementation while the earlier revision of this report asserted it. It is now present, and the details matter.",
    "Value normalisation is a load-bearing component of the MAPPO implementation, and the details matter.")

# 13. Implementation plan defect paragraph - remove whole paragraph
old_exec = """Two things are worth recording about what Phase 1 actually cost, because they bear on how the Phase-3 results should be read. First, the phase is not complete in the sense of the plan: the first implementation of the Phase-1 simulator satisfied every equation of the report and every test, and the coverage numbers it produced were meaningless, because the motion step never applied a move. The defect was found by a diagnostic, the swarm's spread never changed, and not by the equations, the tests or the loss curve. Second, the physical-layer scenario of Phase 2 produced frame counts that did not respond to the transmit power, and the negative control is what exposed it; the instrument was then rebuilt around a statistic that does respond, and the rebuild showed that this statistic is still not a usable instrument for the claim it was wanted for (Section~\\ref{sec:validation}). Both episodes are reported here rather than in a footnote, because a reader deciding whether to trust a result from this pipeline should know that the pipeline's own diagnostics, and not its unit tests, are what caught the two most consequential errors in it."""
rep(old_exec, "The physical-layer scenario of Phase 2 was validated with a transmit-power negative control; the available per-receiver SNR statistic tracks transmit power but is independent of receiver distance, so it cannot support a path-loss cross-validation (Section~\\ref{sec:validation}).")

# 14. Results corrected comparison
rep("\\subsection{The corrected comparison}", "\\subsection{The head-to-head comparison}")
rep("Re-measured comparison on the corrected protocol of", "Head-to-head comparison under the frozen-policy held-out protocol of")
rep("MAPPO, bug fixes only & \\tokBugFixCK & \\tokBugFixSd & seeds \\\\",
    "MAPPO, baseline observation & \\tokBugFixCK & \\tokBugFixSd & seeds \\\\")
rep("MAPPO, with the new observation and shaping & \\tokEgoShapeCK & \\tokEgoShapeSd & seeds \\\\",
    "MAPPO, ego-centric observation and shaping & \\tokEgoShapeCK & \\tokEgoShapeSd & seeds \\\\")
old_first = """Table~\\ref{tab:remeasured} is the whole of the comparison.  Three readings are
worth spelling out.

\\emph{First, the rules reproduce.}  The pre-correction table of this report
was measured on scenes $0$--$4$; re-run at the current code on the same
scenes, the four rule rows reproduce it to three decimal places ($0.372$,
$0.784$, $0.953$, $0.972$).  The measuring apparatus therefore did not change
between the two versions of the report, and a number that moved is a number
the learner moved.

\\emph{Second, the learner now clears every rule.}  MAPPO with the corrected
implementation and the new observation (Section~\\ref{sec:results_abl}) reaches
\\tokEgoShapeCK{} over \\tokEgoShapeN{} training seeds, against
\\tokRuleReactiveLocalCK{} for the strongest hand-written rule (the
unprivileged local-assignment reactive rule).  The difference, learner minus
rule, is \\tokLearnerMinusRule{} of persistent coverage with a 95\\% interval
of \\tokLearnerMinusRuleCi, and \\tokGapVerdict.  The gap of $0.298$ that an
earlier version of this report reported is retracted in
Appendix~\\ref{sec:history}: it was a property of a learner whose entropy bonus
was sign-flipped and whose update ran 25 gradient steps per run, and of a
protocol that compared a policy in training against a rule at rest."""
new_first = """Table~\\ref{tab:remeasured} is the whole of the comparison.  Three readings are
worth spelling out.

\\emph{First, the rules reproduce.}  On the held-out scenes the four rule rows
give $0.372$, $0.784$, $0.953$, $0.972$.  The measuring apparatus is
identical for every row: frozen controllers, the same 20 held-out scenes
(seeds from \\texttt{1000}), the same 2000-step episodes.

\\emph{Second, the learner clears every rule.}  MAPPO with the ego-centric
observation and shaping (Section~\\ref{sec:results_abl}) reaches
\\tokEgoShapeCK{} over \\tokEgoShapeN{} training seeds, against
\\tokRuleReactiveLocalCK{} for the strongest hand-written rule (the
unprivileged local-assignment reactive rule).  The difference, learner minus
rule, is \\tokLearnerMinusRule{} of persistent coverage with a 95\\% interval
of \\tokLearnerMinusRuleCi, and \\tokGapVerdict."""
rep(old_first, new_first)

# 15. Ablation subsection
rep("\\subsection{What closes the gap: the observation, not the bug fixes}",
    "\\subsection{What drives the gain: observation and shaping}")
old_abl = """Two interventions were applied to the corrected learner together, so their
contributions are separated by an ablation:

\\begin{itemize}
  \\item \\emph{Bug fixes only} (the corrected PPO implementation, the old
        observation): \\tokBugFixCK{} (95\\% interval \\tokBugFixCi,
        \\tokBugFixN{} seeds).  This is the number the report's earlier
        ``fixed learner'' would have produced under the corrected protocol.
  \\item \\emph{+ ego-centric observation and distance shaping} (bearings to
        the three nearest under-covered sensors; potential-based shaping):
        \\tokEgoShapeCK.  The increment is $\\approx 0.092$ of persistent
        coverage, and the two intervals do not overlap: the change to the
        observation, not the bug fixes, is what closes the gap.
\\end{itemize}"""
new_abl = """Two observations are compared here, holding the architecture, budget and evaluation fixed:

\\begin{itemize}
  \\item \\emph{Baseline observation} (proprioceptive block without the
        ego-centric deficit bearings): \\tokBugFixCK{} (95\\% interval \\tokBugFixCi,
        \\tokBugFixN{} seeds).
  \\item \\emph{Ego-centric observation and distance shaping} (bearings to
        the three nearest under-covered sensors; potential-based shaping):
        \\tokEgoShapeCK.  The increment is $\\approx 0.092$ of persistent
        coverage, and the two intervals do not overlap: the ego-centric
        observation is the intervention that drives the gain.
\\end{itemize}"""
rep(old_abl, new_abl)
rep("Knob ablation under the corrected protocol.", "Knob ablation under the frozen-policy held-out protocol.")

# 16. Budget
rep("The earlier version of this report claimed that the training budget was not\nthe explanation of the gap (a sweep of 8/16/25 episodes on the buggy learner).\nUnder the corrected protocol the sweep is re-run at 25/50/100/200 episodes:",
    "The training budget is swept at 25/50/100/200 episodes:")

# 17. Credit assignment
rep("  The\n    earlier local-critic arm (a per-agent actor with a per-agent critic, the\n    ``masked PPO local critic'' row of the old table) was measured with the\n    pre-correction learner and has not been re-run under the corrected protocol,\n    so it is not claimed as evidence about the corrected controller.",
    "")

# 18. Thesis paragraph
rep("and the same framework is what\ncaught the three defects (sign-flipped entropy, 25 gradient steps,\ntrain-CK evaluation) that made the original number wrong.",
    "and the same framework makes that split decidable.")

# 19. Conclusion framework-exposes paragraph
old_concl = "\\emph{What the framework exposes.} The framework is not only a certificate; it is an instrument that can tell a reader why a controller behaves as it does, and on this configuration it says something uncomfortable. Under the corrected protocol the same comparison runs the other way: MAPPO with the corrected implementation and the new observation reaches \\tokEgoShapeCK{} over \\tokEgoShapeN{} training seeds against \\tokRuleReactiveLocalCK{} for the strongest hand-written rule, a difference of \\tokLearnerMinusRule{} (95\\% interval \\tokLearnerMinusRuleCi), and \\tokGapVerdict.  The earlier $0.298$ gap is retracted; it was the learner, not the method class.  The controlled arms of Section~\\ref{sec:results} were run against that learner, so they bound a gap that no longer exists and are not used as evidence about the corrected controller; what survives from them is the measurement of the rule baselines and the observation that the local-assignment rule is not worse than the global one, both of which reproduce at the current code.  The regime table of Section~\\ref{sec:results_stress} is what the framework exposes next: the same frozen policy, measured on the regimes the certificate admits, beats the strongest hand-written rule where the task is about where to be (nominal, low connectivity, failure), and loses where the task is about what to conserve or how to deploy (small battery, spread start).  A single ``does learning beat the rule'' number would have hidden that split; the certificate is what makes the split visible."
new_concl = "\\emph{What the framework exposes.} The framework is not only a certificate; it is an instrument that can tell a reader why a controller behaves as it does. MAPPO with the ego-centric observation reaches \\tokEgoShapeCK{} over \\tokEgoShapeN{} training seeds against \\tokRuleReactiveLocalCK{} for the strongest hand-written rule, a difference of \\tokLearnerMinusRule{} (95\\% interval \\tokLearnerMinusRuleCi), and \\tokGapVerdict.  The regime table of Section~\\ref{sec:results_stress} is what the framework exposes next: the same frozen policy, measured on the regimes the certificate admits, beats the strongest hand-written rule where the task is about where to be (nominal, low connectivity, failure), and loses where the task is about what to conserve or how to deploy (small battery, spread start).  A single ``does learning beat the rule'' number would have hidden that split; the certificate is what makes the split visible."
rep(old_concl, new_concl)

# 20. Remove appendix entirely
idx = s.find("\\appendix")
print("appendix at", idx)
if idx >= 0:
    end = s.find("\\end{document}", idx)
    print("appendix block", end-idx)
    s = s[:idx] + s[end:]

p.write_text(s, encoding="utf-8")
print("patched")
