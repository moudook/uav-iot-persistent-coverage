P = r"C:\Users\gbust\Downloads\Academic\Courses\Machine_learning_in_wireless_network\Project1\Mlawn-midsem-tex.tex"
s = open(P, encoding="utf-8").read()

old = r"""Since the learner maximises expected return while the control objective of \eqref{eq:multiobjective} is a minimisation, the team reward of \eqref{eq:reward} is the negated weighted cost, and the two are equivalent up to sign."""
new = r"""Two potential-based shaping terms are added to the reward of \eqref{eq:reward}: a distance potential and an energy potential.  With potential $\Phi$, a shaping term of the form $\kappa(\Phi(s_t)-\gamma\Phi(s_{t+1}))$ is telescoping and therefore does not change the set of optimal policies; it only changes how fast they are found.  The distance potential is the mean over agents of the negative distance to the nearest under-covered sensor, normalised by the field diagonal, and is active with coefficient $\kappa=0.5$ in the evaluated configuration; it gives the policy a dense gradient towards the deficit before any coverage reward arrives.  The energy potential is the minimum battery fraction of the swarm, active with coefficient $\kappa_e=0.3$ only in the curriculum runs of Section~\ref{sec:results_innov}; it biases exploration towards recharging before a battery failure.  Both terms are computed from state alone, so the policy-invariance argument applies to each.

Since the learner maximises expected return while the control objective of \eqref{eq:multiobjective} is a minimisation, the team reward of \eqref{eq:reward} is the negated weighted cost, and the two are equivalent up to sign."""
assert s.count(old) == 1, "reward anchor not found"
s = s.replace(old, new, 1)
open(P, "w", encoding="utf-8").write(s)
print("reward shaping added")
