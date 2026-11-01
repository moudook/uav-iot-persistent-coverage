p = r"C:\Users\gbust\Downloads\Academic\Courses\Machine_learning_in_wireless_network\Project1\Mlawn-midsem-tex.tex"
s = open(p, encoding="utf-8").read()
old = r"""A hand-designed reactive rule outperforms parameter-shared CTDE MAPPO: the gap is $\tokGap$ of persistent coverage, with a 95\% interval of $\tokGapCi$, and the learned controller is below it under either deployment mode (sampled $\tokMappoCk$, argmax $\tokArgCk$)."""
new = r"""Under the corrected protocol the same comparison runs the other way: MAPPO with the corrected implementation and the new observation reaches \tokEgoShapeCK{} over \tokEgoShapeN{} training seeds against \tokRuleReactiveLocalCK{} for the strongest hand-written rule, a difference of \tokLearnerMinusRule{} (95\% interval \tokLearnerMinusRuleCi), and \tokGapVerdict.  The earlier $0.298$ gap is retracted; it was the learner, not the method class.  On the pre-correction learner the arms of Section~\ref{sec:results} bound a gap that no longer exists, and we do not use them as evidence about the corrected controller.  What survives from them is the measurement of the rule baselines and the observation that the local-assignment rule is not worse than the global one, both of which reproduce at the current code."""
assert old in s, "anchor not found"
s = s.replace(old, new, 1)
open(p, "w", encoding="utf-8").write(s)
print("done")
