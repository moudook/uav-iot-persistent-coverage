p = r"C:\Users\gbust\Downloads\Academic\Courses\Machine_learning_in_wireless_network\Project1\Mlawn-midsem-tex.tex"
s = open(p, encoding="utf-8").read()

old1 = r"""Applied to a controlled experimental setup, the framework shows that a hand-designed reactive rule outperforms parameter-shared CTDE MAPPO on this task, and it bounds the reason with controlled arms.  \tokArmsSummarySentence\ \tokCreditResidualShort\,.  Reporting that result, with the experiments that support it and the resolution at which each arm was measured, is more useful to a reader than a favourable number whose provenance has not been examined."""
new1 = r"""Applied to a controlled experimental setup, the first version of this work reported that a hand-designed reactive rule outperforms parameter-shared CTDE MAPPO on this task, and it bounded the reason with controlled arms.  That number is retracted in Section~\ref{sec:second_sprint}: it came from a learner whose entropy bonus was sign-flipped and whose update ran 25 gradient steps per run, and from a protocol that compared a policy in training against a rule at rest.  Under the corrected protocol the learner is ahead of the strongest rule by \tokLearnerMinusRule{} (95\% interval \tokLearnerMinusRuleCi), and \tokGapVerdict.  Reporting that sequence --- the failure, its cause, and the correction --- is more useful to a reader than a favourable number whose provenance has not been examined."""
assert old1 in s
s = s.replace(old1, new1, 1)

old2 = r"""    \item A \emph{measured negative result}: on the configuration the paper's own certificate declares feasible, a hand-designed reactive rule outperforms parameter-shared CTDE MAPPO by $\tokGap$ of persistent coverage (95\% interval $\tokGapCi$), and the four single-factor arms bound how much of that gap each of them can account for."""
new2 = r"""    \item A \emph{measured result, corrected}: on the configuration the paper's own certificate declares feasible, the first version of this work reported that a hand-designed reactive rule outperforms parameter-shared CTDE MAPPO by $\tokGap$ of persistent coverage (95\% interval $\tokGapCi$).  That number is retracted; under the corrected protocol the learner is ahead of the strongest rule by \tokLearnerMinusRule{} (95\% interval \tokLearnerMinusRuleCi), and \tokGapVerdict.  The four single-factor arms bound how much of the pre-correction gap each of them can account for, and are not evidence about the corrected controller."""
assert old2 in s
s = s.replace(old2, new2, 1)

open(p, "w", encoding="utf-8").write(s)
print("done")
