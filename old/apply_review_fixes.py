import re

P = r"C:\Users\gbust\Downloads\Academic\Courses\Machine_learning_in_wireless_network\Project1\Mlawn-midsem-tex.tex"
s = open(P, encoding="utf-8").read()

def rep(old, new, tag, count=1):
    global s
    n = s.count(old)
    assert n == count, f"[{tag}] expected {count} occurrence(s), found {n}"
    s = s.replace(old, new, count)

# ---------------------------------------------------------------- E2: restored claim-audit subsection
anchor = "\\subsection{History of this measurement}"
assert anchor in s
audit = r"""\subsection{Claim audit and physical-layer validation}
\label{sec:validation}

Every non-measurement claim of this paper --- the physical model, the
feasibility bounds, the protocol statements and the determinism claims --- is
recomputed by an automated claim audit that records, for each statement, the
artefact or derivation that supports it: \tokAuditItems{} items, of which
\tokAuditPass{} pass, \tokAuditInfo{} are informational, and \tokAuditFail{}
fail.  The audit does not cover the measurements of this paper; those are the
artefacts themselves.

The physical-layer claim is the one that is audited most carefully, because
its cheap version would be a runtime cross-validation and its honest version
is an algebraic equivalence.  The Python reference PHY and INET's
\texttt{BreakpointPathLoss} implement the same function to $\tokPhyDelta$~dB
over $\tokPhyRows$ (distance, exponent) points, and that equivalence is what
is claimed.  A runtime path-loss cross-validation was attempted with a
transmit-power negative control: the available per-receiver SNR statistic
tracks the transmit power exactly but is independent of the receiver's
distance, so it cannot support such a cross-validation, and the negative
control is what exposed it.  A dedicated 802.11 physical-layer scenario runs
to completion in the OMNeT++/INET co-simulation and produces scalar and vector
outputs; the instrument it provides, and the reason it cannot measure what we
would like it to measure, are recorded with the scenario.

"""
s = s.replace(anchor, audit + anchor, 1)

# ---------------------------------------------------------------- E3: energy-results ref
rep(
    "the cost of charging contention in the energy results of Section~\\ref{sec:results_energy} is a lower bound",
    "the cost of charging contention in the small-battery stress regime (Table~\\ref{tab:stress}) is a lower bound",
    "E3 energy ref",
)

# ---------------------------------------------------------------- E4: Local Observation rewrite
obs_new_start = r"""At deployment, UAV $i$ observes its own state, four neighbour slots, a small
tail of derived quantities, and an ego-centric summary of the coverage deficit:
"""
obs_old_start = "At deployment, UAV $i$ uses only locally available information, plus three\nbroadcast quantities:"
assert obs_old_start in s
s = s.replace(obs_old_start, obs_new_start, 1)

# replace the equation block (the old eq 4)
old_eq = """\\begin{equation}
\\begin{split}
\\mathbf o_i(t)=\\bigl[&\\mathbf p_i,\\mathbf v_i,b_i,\\mathcal N_i,C_i^{\\mathrm{local}},\\rho_i,\\tau_i^{\\mathrm{return}},\\
&E_i^{\\mathrm{pad}},\\mathbf 1_i,\\hat{\\mathbf d}_i^{\\mathrm{pad}},\\mathbf M_t^{\\mathrm{def}}\\bigr].
\\end{split}
\\label{eq:obs}
\\end{equation}"""
new_eq = """\\begin{equation}
\\begin{split}
\\mathbf o_i(t)=\\bigl[&\\mathbf p_i,\\mathbf v_i,b_i,\\mathcal N_i,C_i^{\\mathrm{local}},\\rho_i,\\tau_i^{\\mathrm{return}},\\
&E_i^{\\mathrm{pad}},\\{\\hat{\\mathbf u}_{i,j},d_{i,j}\\}_{j=1}^{k},\\mathbf r_i\\bigr].
\\end{split}
\\label{eq:obs}
\\end{equation}"""
rep(old_eq, new_eq, "E4 eq", 1)

# replace the explanatory paragraph that followed the equation
old_para = """Here $\\mathcal N_i$ is the set of nearby UAVs, $C_i^{\\mathrm{local}}$ is the number of nearby sensors currently covered, $\\rho_i$ is a locally computed bridge-risk estimate, $\\tau_i^{\\mathrm{return}}$ is the estimated time until the return threshold is reached, $E_i^{\\mathrm{pad}}$ is the estimated energy needed to reach a feasible charging pad, $\\mathbf 1_i\\in\\{0,1\\}^{N}$ is the agent's own identity, and $\\hat{\\mathbf d}_i^{\\mathrm{pad}}$ is the unit bearing to the nearest charging pad (whose range is carried by $E_i^{\\mathrm{pad}}$). The last term, $\\mathbf M_t^{\\mathrm{def}}\\in\\mathbb R^{G^2}$, is the broadcast deficit summary: a $G\\times G$ grid over the region in which cell $(g_x,g_y)$ holds the share of all $M$ sensors that lie in that cell and are currently under-covered, $n_d(t)<K$. Normalising by $M$ rather than by the cell population makes the value global, so the agent learns both where the deficit is and how large it is, and the encoding is independent of $M$. The base configuration uses $G=4$, and the resolution sweep of Section~\\ref{sec:results_obs} measures $G\\in\\{0,4,8\\}$."""
new_para = """Here $\\mathcal N_i$ is the set of nearby UAVs, $C_i^{\\mathrm{local}}$ is the number of nearby sensors currently covered, $\\rho_i$ is a locally computed bridge-risk estimate, $\\tau_i^{\\mathrm{return}}$ is the estimated time until the return threshold is reached, and $E_i^{\\mathrm{pad}}$ is the estimated energy needed to reach a feasible charging pad.  The final block is the ego-centric deficit summary: for the $k=3$ sensors nearest to $i$ whose coverage is below the required level ($n_d(t)<K$), the agent receives the unit bearing $\\hat{\\mathbf u}_{i,j}$ and the normalised distance $d_{i,j}$; $\\mathbf r_i$ is a repulsion vector away from the centroid of the UAVs in communication range, which keeps a shared policy from collapsing all agents onto the same deficit.  Both are computable from local information under the communication model of Section~\\ref{sec:radio}, so the observation is decentralised and has fixed size independent of $M$."""
rep(old_para, new_para, "E4 para1", 1)

# replace the identity/pad-bearing paragraph and the third-term paragraph
old_para2 = """Two properties of this observation are not cosmetic, and both are load-bearing for the shared-parameter design of Section~\\ref{sec:mappo}. The first is the identity. Parameter sharing is sound only when each agent's own observation identifies it, so that a shared network can still specialise~\\cite{foerster2016}; the first version of $\\mathbf o_i$ did not satisfy this condition, and the consequence was measurable rather than theoretical: in a symmetric deployment every agent received an almost identical input, the deterministic policy collapsed to nearly the same action for all of them, and the swarm translated as a rigid body without ever dispersing. The implication is specific to an action space of displacements, which is the one used here: identical displacements translate the configuration rigidly and so freeze its shape. In an action space whose symbols index agent-local targets, the same symbol would send different agents to different places, and dispersion would be possible after all. The second is the bearing to the charger. Without it the observation carries the \\emph{cost} of the flight to a pad but not its \\emph{direction}, and a learned policy cannot express the return at all. We assume that the infrastructure which owns the charging pads also broadcasts their positions, which is a communication assumption rather than an oracle.

A third term --- a broadcast summary of where the coverage deficit is ---
was added a priori, on the argument that an agent which knows how many
sensors it covers but not which are deficient has no gradient signal for
deployment. The measurement of Section~\\ref{sec:results_obs} does not
settle that argument for the better: \\tokMapModelSentence.  The summary
is therefore kept in Eq.~\\eqref{eq:obs} and reported as a null result
rather than quietly dropped, and we keep the argument in the record
because it was reasonable, and because the measurement is more useful to a
reader than the argument would have been."""
new_para2 = """Three design alternatives to this observation were considered and measured.
A broadcast $G\\times G$ deficit grid $\\mathbf M_t^{\\mathrm{def}}$ --- a cell
summary of the share of under-covered sensors --- was the original summary
term; it is not part of the evaluated configuration, and the value-of-
information row of Table~\\ref{tab:knobs} prices exactly the information it
would have supplied: replacing the ego-centric summary by the exact
under-covered set costs $-0.090$, so the summary is neither free nor
decisive.  A one-hot agent identity is likewise not in the evaluated
observation; the ego terms depend on the agent's own position relative to the
deficit, so a parameter-shared network still receives agent-specific inputs.
The bearing to the charging pad is also not in the evaluated observation; the
return decision is driven by the energy features above."""
rep(old_para2, new_para2, "E4 para2+3", 1)

# update Table obs rows: replace identity / pad-bearing / deficit-grid rows
old_rows = """Identity & $\\mathbf 1_i$ & One-hot agent index; required for a shared network to specialise. \\\\
Pad bearing & $\\hat{\\mathbf d}_i^{\\mathrm{pad}}$ & Unit vector to the nearest charging pad; required to fly home. \\\\
Deficit summary & $\\mathbf M_t^{\\mathrm{def}}$ & Broadcast $G\\times G$ grid of the under-covered share of each cell; $G=4$ in the base configuration, and $G=0$ removes it. \\\\"""
new_rows = """Deficit bearings & $\\{\\hat{\\mathbf u}_{i,j},d_{i,j}\\}_{j=1}^{k}$ & Unit bearing and normalised distance to the $k=3$ nearest under-covered sensors; decentralised, fixed size. \\\\
Repulsion & $\\mathbf r_i$ & Away from the centroid of nearby UAVs; prevents the swarm from collapsing onto one deficit. \\\\"""
rep(old_rows, new_rows, "E4 table rows", 1)

# ---------------------------------------------------------------- E5: intro CONTRIB bullet
old_contrib = """    \\item A \\emph{measured specification of what a shared policy's observation must contain}: the agent's own identity and a bearing to the charging pad are the two terms the controlled comparisons examine, and at 8 training seeds they do not settle the question about the coverage.  In the component ablation, the identity changes persistent coverage by +0.008, an interval [-0.121, +0.137] that includes zero, so at this budget what it demonstrably buys is the ability to specialise, and without it the deter"""
# we only have the prefix; find the full bullet
i0 = s.index("A \\emph{measured specification of what a shared policy's observation must contain}")
i1 = s.index("CONTRIB\n    \\item Corrected deployment parameters", i0)
old_bullet = s[i0:i1]
new_bullet = r"""A \emph{measured specification of what a shared policy's observation must contain}: an ego-centric summary of the coverage deficit --- unit bearings and normalised distances to the $k=3$ nearest under-covered sensors, plus a neighbour-repulsion vector --- is what the evaluated controller receives, and it is sufficient: replacing it by the exact global under-covered set costs $-0.090$ (Table~\ref{tab:knobs}), so more information hurts at this budget, and the one-hot identity and pad bearing of the earlier design are not part of the evaluated configuration.
"""
s = s[:i0] + new_bullet + s[i1:]

# ---------------------------------------------------------------- E6: budget bullets
old_b1 = """  \\item      25 episodes: $0.830$ ($n=3$) at 25 episodes,      50 episodes: $0.868$ ($n=3$) at 50,     100 episodes: $0.933$ ($n=3$)
        at 100,     200 episodes: $0.947$ ($n=3$) at 200 (each the mean over three seeds, frozen
        evaluation).
  \\item The increasing budget buys +0.117 of persistent coverage
        over the range, and over the range 25 to 200 episodes the mean evaluation coverage moves by +0.117."""
new_b1 = """  \\item 25 episodes: $0.830$ ($n=3$); 50 episodes: $0.868$ ($n=3$);
        100 episodes: $0.933$ ($n=3$); 200 episodes: $0.947$ ($n=3$);
        each the mean over three training seeds of the frozen-policy evaluation.
  \\item The budget is load-bearing: the mean evaluation coverage moves by
        $+0.117$ over the range 25 to 200 episodes, monotonically."""
rep(old_b1, new_b1, "E6 budget", 1)

# ---------------------------------------------------------------- E7: credit section grammar + tail
old_cr = """$0.959$ (95\\% interval $[0.956, 0.963]$) against $0.952$, with the difference-credit arm is not separated from the team reward at this resolution.  The
earlier local-critic arm (a per-agent actor with a per-agent critic, the
``masked PPO local critic'' row of the old table) is re-run under the fixed

"""
new_cr = """$0.959$ (95\\% interval $[0.956, 0.963]$) against $0.952$: the difference-credit arm is not separated from the team reward at this resolution.  The
earlier local-critic arm (a per-agent actor with a per-agent critic, the
``masked PPO local critic'' row of the old table) was measured with the
pre-correction learner and has not been re-run under the corrected protocol,
so it is not claimed as evidence about the corrected controller.
"""
rep(old_cr, new_cr, "E7 credit", 1)

# ---------------------------------------------------------------- E8: stress table rename + caption
rep("clustered start & 0.997 & 0.959 & -0.038 & 0.003",
    "spread start & 0.997 & 0.959 & -0.038 & 0.003", "E8 stress row", 1)
old_cap = "\\caption{Stress regimes (zero-shot).  Every row is the frozen-policy\nevaluation on the same held-out scenes, with the configuration of the regime\napplied."
new_cap = "\\caption{Stress regimes (zero-shot).  Every row is the frozen-policy\nevaluation on the same 5 held-out scenes (seeds 1000--1004), with the\nconfiguration of the regime applied."
rep(old_cap, new_cap, "E8 stress caption", 1)

# ---------------------------------------------------------------- E9: innovation table anchor sd + combined row
rep("anchor (ego+shape) & 0.765 & -- & 5 \\\\",
    "anchor (ego+shape) & 0.765 & 0.081 & 5 \\\\", "E9 anchor sd", 1)
rep("+ intrinsic + curriculum + energy + R\\&F & 0.834 & 0.068 & 1 \\\\",
    "+ intrinsic + curriculum + energy + R\\&F & 0.834 & 0.068 & 1 \\\\\n+ difference credit + curriculum + energy + R\\&F & 0.816 & 0.131 & 1 \\\\",
    "E9 combined row", 1)

# ---------------------------------------------------------------- E10: conclusion status-log paragraph removal, retractions into Sec IX
old_log = r"""\emph{Correction and re-measurement (Nov 2026).} A super-intelligent review identified a sign-flipped entropy term ($+c_2 H$ instead of $-c_2 H$) and severe under-training (25 gradient steps total, no PPO epochs) in the learner, which together explain the reported collapse at episode 675 and the flat budget curve. Part-1 fixes are applied (entropy sign, separate optimisers and grad clipping, 10 PPO epochs with KL early stop, clipped value loss, orthogonal init, active-agent masking, EMA direction). Re-measured under the corrected protocol of Section~\ref{sec:protocol} the learner reaches \tokEgoShapeCK{} over \tokEgoShapeN{} seeds against \tokRuleReactiveLocalCK{} for the strongest rule, a difference of \tokLearnerMinusRule{} (95\% interval \tokLearnerMinusRuleCi), and \tokGapVerdict. The earlier ``credit assignment drives collapse'' reading and the $0.860$ random-baseline figure are retracted; the latter was measured with the wrong configuration. The network is not the binding constraint at 80~m scale (PDR $\approx 0.998$, range margin $22\times$). The paper's thesis is being reframed from ``learning beats the rule'' to ``certifying where learning does not help,'' with the feasibility-certification methodology (C4) as the centrepiece contribution.
"""
assert old_log in s, "conclusion log not found"
s = s.replace(old_log, "", 1)

old_sec9 = r"""\emph{What this does to the rest of the results section.}  The controlled arms of Section~\ref{sec:results} were run against the broken learner, so they bound the explanation of a gap that no longer exists.  They are not evidence about the corrected controller, and we do not use them as such.  What survives from them is the measurement of the rule baselines and the observation that the local-assignment rule is not worse than the global one, both of which reproduce at the current code."""
new_sec9 = r"""\emph{What this does to the rest of the results section.}  The controlled arms of Section~\ref{sec:results} were run against the broken learner, so they bound the explanation of a gap that no longer exists.  They are not evidence about the corrected controller, and we do not use them as such.  What survives from them is the measurement of the rule baselines and the observation that the local-assignment rule is not worse than the global one, both of which reproduce at the current code.  Two further measurements from that version are retracted with it: the ``credit assignment drives collapse'' reading, and the $0.860$ random-baseline figure, which was measured with the wrong configuration."""
rep(old_sec9, new_sec9, "E10 sec9", 1)

# ---------------------------------------------------------------- dead macro refs -> real tables
rep(r"Table~\ref{tab:results_energy} says so",
    r"Table~\ref{tab:knobs} says so", "E11 tab energy", 1)
rep(r"Table~\ref{tab:results_obs}.",
    r"Table~\ref{tab:knobs}.", "E11 tab obs", 1)

open(P, "w", encoding="utf-8").write(s)
print("ALL EDITS APPLIED")
