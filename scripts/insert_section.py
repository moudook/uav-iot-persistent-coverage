"""Insert the filled second-sprint section into the report.

Run AFTER scripts/make_midsem_numbers.py has regenerated midsem_numbers.tex
so that all \\tok* macros used in the section are defined.
"""
import re
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEX = os.path.join(ROOT, "Mlawn-midsem-tex.tex")
DRAFT = os.path.join(ROOT, "docs", "second_sprint_draft.tex")

def main():
    s = open(TEX, encoding="utf-8").read()
    draft = open(DRAFT, encoding="utf-8").read()

    # fill the two placeholders that could not be templated
    verdict = (r"\emph{What the corrected measurement says.}  Two things changed "
               r"at once, and Table~\ref{tab:remeasured} separates them.  Fixing "
               r"the implementation alone moves the learner from the "
               r"pre-correction $0.674$ to \tokBugFixCK{} (95\% interval "
               r"\tokBugFixCi, \tokBugFixN{} seeds).  Changing the observation "
               r"and adding the shaping term moves it to \tokEgoShapeCK{} "
               r"(\tokEgoShapeCi, \tokEgoShapeN{} seeds).  The strongest "
               r"hand-written rule, the unprivileged local-assignment reactive "
               r"rule, reaches \tokRuleReactiveLocalCK.  The difference, "
               r"learner minus rule, is \tokLearnerMinusRule{} of persistent "
               r"coverage with a 95\% interval of \tokLearnerMinusRuleCi, and "
               r"\tokGapVerdict.  The gap of $0.298$ that the first version of "
               r"this report reported is therefore not a property of the method "
               r"class; it was the learner.")
    survives = (r"\emph{What this does to the rest of the results section.}  "
                r"The controlled arms of Section~\ref{sec:results} were run "
                r"against the broken learner, so they bound the explanation of "
                r"a gap that no longer exists.  They are not evidence about the "
                r"corrected controller, and we do not use them as such.  What "
                r"survives from them is the measurement of the rule baselines "
                r"and the observation that the local-assignment rule is not "
                r"worse than the global one, both of which reproduce at the "
                r"current code.")
    draft = draft.replace("{{VERDICT}}", verdict, 1)
    draft = draft.replace("{{WHAT_SURVIVES}}", survives, 1)
    if "{{VERDICT}}" in draft or "{{WHAT_SURVIVES}}" in draft:
        raise SystemExit("unfilled placeholders remain")

    anchor_start = r"\section{Second sprint: super-intelligent review and re-measurement}"
    anchor_end = r"\section{Conclusion}"
    i = s.index(anchor_start)
    j = s.index(anchor_end)
    # keep the heading from the draft itself; drop the old heading
    s2 = s[:i] + draft + "\n\n" + s[j:]
    open(TEX, "w", encoding="utf-8").write(s2)
    print("inserted; report length", len(s2))


if __name__ == "__main__":
    main()
