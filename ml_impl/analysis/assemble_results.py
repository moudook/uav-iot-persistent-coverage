"""
Assemble the Results section of the paper from the artefacts and the text.

The section is built from three sources:
  * analysis/tables.tex      -- the tables, generated from the CSVs
  * analysis/results_text.tex -- the prose, in blocks separated by %% markers
  * the rest of the .tex      -- everything else, untouched

The old Results section (from \\section{Results} up to the
\\subsection{Claim Audit and Physical-Layer Validation} heading) is replaced
wholesale, so the paper cannot contain a mixture of old and new numbers.

Run:  python analysis/assemble_results.py [--tex PATH]
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ML = os.path.dirname(HERE)
PROJ = os.path.dirname(ML)

TEX = os.path.join(PROJ, "Mlawn-midsem-tex.tex")
TABLES = os.path.join(HERE, "tables.tex")
TEXT = os.path.join(HERE, "results_text_filled.tex")

MARKERS = ["%% CONTRIB", "%% MAIN", "%% OBS", "%% ENERGY", "%% ABL",
           "%% ABLSTRESS", "%% CREDIT", "%% SCEN"]

# A region of the paper that is replaced wholesale from the template, so
# that a number which comes from an experiment can live outside the Results
# section without being typed by hand.  The markers stay in the .tex, so the
# file is still a complete, compilable paper on its own.
REGIONS = {
    "%% CONTRIB": ("%% BEGIN CONTRIB", "%% END CONTRIB"),
}


def replace_region(src, begin, end, body):
    """Replace the text between the two markers with `body`."""
    i = src.find(begin)
    j = src.find(end)
    if i < 0 or j < 0 or j < i:
        return src, False
    return src[:i + len(begin)] + "\n" + body + "\n" + src[j:], True


MACRO_BEGIN = "%% BEGIN TOKEN MACROS"
MACRO_END = "%% END TOKEN MACROS"


def write_token_macros(src, tok, missing):
    """Write the macro definitions for every token into the paper.

    The hand-written prose refers to a number by its macro (\tokGap), and
    the definitions are written here, from the token table, on every
    assembly.  The number therefore regenerates whenever the artefact
    changes, which is the whole point: a value written into the source
    would freeze at whatever the first assembly found.

    A token with no value becomes a visible marker, so an incomplete
    paper is impossible to miss.
    """
    from fill_tokens import macro_name

    lines = []
    for name in sorted(tok):
        value = str(tok[name])
        # A token's VALUE can quote another token (the contribution bullet
        # quotes the identity arm's interval).  In the prose the two are
        # substituted in sequence, but a macro's body is expanded where it
        # is USED, so the nested token would survive into the paper.  The
        # values are therefore resolved before the definitions are
        # written.
        for _ in range(4):
            if "@@" not in value:
                break
            for inner in sorted(tok):
                value = value.replace(f"@@{inner}@@", str(tok[inner]))
        lines.append(f"\\newcommand{{\\{macro_name(name)[1:]}}}"
                     f"{{{value}}}")
    for name in sorted(missing):
        esc = name.replace("_", r"\_")
        lines.append(f"\\newcommand{{\\{macro_name(name)[1:]}}}"
                     f"{{\\mbox{{\\textbf{{[pending: {esc}]}}}}}}")
    # A macro the PROSE uses but the table does not have yet is the
    # same case: the experiment that measures it has not finished.
    # Without this the paper would not compile, because an undefined
    # control sequence is an error, and the error is much harder to
    # read than a marker.
    used = set(re.findall(r"\\(tok[A-Za-z]+)", src))
    defined = {macro_name(n)[1:] for n in tok}
    for mac in sorted(used - defined):
        lines.append(f"\\newcommand{{\\{mac}}}"
                     f"{{\\mbox{{\\textbf{{[pending: {mac}]}}}}}}")
    body = ("\n% The numbers that come from an experiment.  These definitions are\n"
            "% written by analysis/assemble_results.py from the artefact table,\n"
            "% so the prose cannot drift away from the measurement.\n"
            + "\n".join(lines))
    return replace_region(src, MACRO_BEGIN, MACRO_END, body)


def read_blocks(path):
    if not os.path.exists(path):
        return {m.strip(): "" for m in MARKERS}
    raw = open(path, encoding="utf-8").read()
    parts = re.split(r"^%%\s*(CONTRIB|MAIN|OBS|ENERGY|ABL|ABLSTRESS|CREDIT|SCEN)\s*$",
                     raw, flags=re.M)
    blocks = {}
    for i in range(1, len(parts), 2):
        blocks["%% " + parts[i]] = parts[i + 1].strip("\n")
    for m in MARKERS:
        blocks.setdefault(m, "")
    return blocks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tex", default=TEX)
    ap.add_argument("--no-compile", action="store_true")
    args = ap.parse_args()

    # regenerate the tables and fill the prose tokens
    for script in ("make_tables.py", "make_figures.py",
                   "fill_tokens.py"):
        r = subprocess.run([sys.executable,
                            os.path.join(HERE, script)],
                           capture_output=True, text=True)
        print(r.stdout.strip() or r.stderr.strip())
    tables = open(TABLES, encoding="utf-8").read()
    blocks = read_blocks(TEXT)

    # the token table: the ONLY source of a number that comes from an
    # experiment, for the prose blocks, for the section preamble and for
    # the rest of the paper
    from fill_tokens import build_tokens, fill
    tok = build_tokens()

    # split the tables into named pieces
    tparts = {}
    for m in re.finditer(r"\\begin\{table\}\[t\].*?\\end\{table\}", tables,
                         flags=re.S):
        chunk = m.group(0)
        lm = re.search(r"\\label\{([^}]+)\}", chunk)
        if lm:
            tparts[lm.group(1)] = chunk

    def tab(name):
        if name not in tparts:
            # the artefact has not been produced yet; leave a marker rather
            # than a wrong number, and say so loudly
            print(f"WARNING: table {name} is missing from the artefacts")
            return (f"% WARNING: the table {name} has not been generated; "
                    f"re-run run_all.py")
        return tparts[name]

    section = r"""
\section{Results}
\label{sec:results}

All experiments use the corrected, feasible configuration $N=8$, $K=2$,
$R_{\mathrm{cov}}=35$\,m on an $80\times80$\,m field
(Section~\ref{sec:feasibility}), the clustered initial deployment and the
2000-step episode of Section~\ref{sec:parameters}.  Every controller is
evaluated on the same scenes with the same seeds, and the rule baselines and
the learned controllers are trained on the same budget.  The teleporting
placement oracle reaches $CK=1.000$ on this configuration; it is the
ceiling against which every coverage number below is meant to be read, and
it is what makes the comparison meaningful: the oracle establishes that
the configuration is coverable, so a controller that falls short of it
falls short as a controller and not because the instance was infeasible.

Two things are true of this configuration, and we report both.  First, the
task is not hard at the parameters the project specifies: a deterministic
reactive heuristic that assigns UAVs to uncovered sensors reaches
$CK=@@REACT_CK@@$ while maintaining full connectivity.  Second, the learned
controller does not reach that figure, and the arms below bound how much
of the gap each candidate explanation can account for.  Three candidate
explanations can be tested with controlled arms --- the content of the
observation, the energy model, and the credit assignment of the team
reward --- and the arms are reported whichever way they come out, with
the resolution at which each was measured.

Before those arms, one measurement of what the framework is \emph{for},
because it is the claim the framework makes first.  On the report's
original configuration, $N=5$, $K=2$, $R_{\mathrm{cov}}=35$\,m, which
Section~\ref{sec:feasibility} proves infeasible for the region
requirement, the same reactive heuristic reaches $CK=@@INF_CK@@$ with
connectivity availability $@@INF_AG@@$ --- over the @@INF_N@@ scenes of
that configuration --- while the service-continuity metric is $@@INF_SC@@$.
A reader with no achievability reference would read that coverage ratio as
a reasonably good controller and the joint metric as a controller that
never achieves the requirement, and neither reading would say whether the
zero is the controller's fault or the instance's.  The teleporting oracle
on the same scenes reaches $@@INF_ORACLE@@$, so the twenty sensors
themselves are coverable and this shortfall is a controller shortfall; it
is the \emph{certificate} that says the region is not coverable at all, and
it is the certificate that makes the reading decidable.  That is what the
framework contributes here, and it is why the results below are on a
configuration the certificate admits.

__TAB_MAIN__

__BLOCK_MAIN__

__FIG_CURVE__

\subsection{What the local observation must contain}
\label{sec:results_obs}

The observation of Eq.~\eqref{eq:obs} is the interface between the
framework's communication assumption and the shared policy, and the claim
that parameter sharing requires the observation to break the permutation
symmetry is testable.  Table~\ref{tab:results_obs} compares three
observations under identical seeds, budget and evaluation scenes: the local
observation alone; that observation plus the one-hot agent identity; and that
plus the broadcast coverage-map summary and the bearing to the charging
pad, which is the configuration the paper proposes.

__TAB_OBS__

__BLOCK_OBS__

\subsection{Energy management, and the reward that was missing it}
\label{sec:results_energy}

The step-level diagnostic of the learned policy produced a surprising
number: it stranded \emph{all eight} UAVs in nearly every episode, while
the reactive heuristic stranded $0.7$.  A stranded UAV has an empty pack
away from a charging pad; it can no longer fly, it leaves the swarm, and it
stops covering.  The obvious reading is that the controller has failed at
energy management, and the obvious fix is a reward term that prices the
consequence of an empty pack.  Table~\ref{tab:results_energy} tests that
reading with four controlled arms: the same policy with a pack that cannot
run out, the same policy without the threshold-violation term of
Table~\ref{tab:reward}, and the same policy under the earlier energy rule
of the safety filter.

__TAB_ENERGY__

__BLOCK_ENERGY__

\subsection{Component ablation}
\label{sec:results_abl}

__TAB_ABL__

__BLOCK_ABL__

__TAB_ABL_STRESS__

__BLOCK_ABL_STRESS__

\subsection{The credit assignment, and the cheapest test of it}
\label{sec:results_credit}

The diagnosis of Sections~\ref{sec:results_obs} and
\ref{sec:results_energy} points at one mechanism: with a shared team
reward every agent receives the same advantage, so the gradient cannot
distinguish an agent whose action helped from one whose action was
irrelevant.  The literature calls this the credit-assignment problem, and
the remedies are known: the counterfactual advantage of COMA, the
difference-based estimator of DAE, the per-agent value iteration of GPAE, and
the advantage decomposition of HAPPO/HATRPO~\cite{foerster2018,li2022,kim2026,kuba2022}.
None of them has been evaluated on a persistent-coverage task, and the
question of whether the credit assignment is what limits a
parameter-shared controller in that setting appears to be open.

Table~\ref{tab:results_credit} is the cheapest test of it that does not
require implementing a new algorithm, and it is worth being exact about
what it does and does not change.  The two arms differ in the learner that
produces the advantage.  Arm~A is the proposed method: a parameter-shared
actor with a centralised critic, so every agent receives the same broadcast
team advantage.  Arm~B keeps the same simulator, the same observation, the
same action mask, the same team reward and the same episode budget, and
replaces the learner with a per-agent actor and a per-agent local critic.
Nothing else changes.

What that does and does not change is worth stating plainly, because it
bounds the conclusion.  With a team reward $r_t$ broadcast to every agent,
the advantage is $r_t+\gamma V(o')-V(o)$.  Giving each agent its own
value function re-centres and re-scales that expression per agent, so the
advantage is no longer a single shared number, but it cannot decompose it,
because the advantage's dependence on the other agents enters only through
the aggregate reward and through the observation, which are symmetric in
the other agents.  Redistribution of credit requires a per-agent reward, a
joint-action critic, or a counterfactual baseline.

__TAB_CREDIT__

__BLOCK_CREDIT__

\subsection{Scenario matrix}
\label{sec:results_scen}

__TAB_SCEN__

__BLOCK_SCEN__

"""

    fig_lines = []
    fig_path = os.path.join(HERE, "fig_learning_curve.tex")
    if os.path.exists(fig_path):
        fig_lines = [r"\begin{figure}[t]", r"\centering", r"\small"]
        fig_lines.append(open(fig_path, encoding="utf-8").read().strip())
        fig_lines.append(r"\caption{The per-episode persistent coverage of")
        fig_lines.append(r"each training run of the proposed controller, on the")
        fig_lines.append(r"training scene, against the reactive heuristic's coverage")
        fig_lines.append(r"on the evaluation scenes.  The curves have flattened over")
        fig_lines.append(r"the budget the experiments use, but only on the scene the")
        fig_lines.append(r"policy trains on; the budget sweep below is what says")
        fig_lines.append(r"whether that carries over to unseen scenes, and it does")
        fig_lines.append(r"not resolve it.  The per-episode values are on the training")
        fig_lines.append(r"scene and are therefore not the deployed performance.}")
        fig_lines.append(r"\label{fig:learningcurve}")
        fig_lines.append(r"\end{figure}")
    else:
        print("WARNING: the learning-curve figure was not generated")
    fig = "\n".join(fig_lines)

    section = (section
               .replace("__FIG_CURVE__", fig)
               .replace("__TAB_MAIN__", tab('tab:results_main'))
               .replace("__TAB_OBS__", tab('tab:results_obs'))
               .replace("__TAB_ENERGY__", tab('tab:results_energy'))
               .replace("__TAB_ABL__", tab('tab:results_abl'))
               .replace("__TAB_ABL_STRESS__", tab('tab:results_ablstress'))
               .replace("__TAB_CREDIT__", tab('tab:results_credit'))
               .replace("__TAB_SCEN__", tab('tab:results_scen'))
               .replace("__BLOCK_MAIN__", blocks['%% MAIN'])
               .replace("__BLOCK_OBS__", blocks['%% OBS'])
               .replace("__BLOCK_ENERGY__", blocks['%% ENERGY'])
               .replace("__BLOCK_ABL__", blocks['%% ABL'])
               .replace("__BLOCK_ABL_STRESS__", blocks['%% ABLSTRESS'])
               .replace("__BLOCK_CREDIT__", blocks['%% CREDIT'])
               .replace("__BLOCK_SCEN__", blocks['%% SCEN']))

    # the section's own tokens (the preamble quotes the reactive
    # heuristic's coverage) are filled from the same table
    section, leftover = fill(section, tok)

    src = open(args.tex, encoding="utf-8").read()
    start = src.find("\\section{Results}")
    end = src.find("\\subsection{Claim Audit and Physical-Layer Validation}")
    if start < 0 or end < 0 or end < start:
        raise SystemExit("could not locate the Results section")

    # The Results section is replaced only when every token in it can be
    # filled: a section that still contains a literal token is a draft with
    # a hole in it, and the hole is marked.
    if leftover:
        print("WARNING: the Results section keeps its previous text because "
              f"these tokens are not yet filled: {', '.join(leftover)}")
    else:
        src = src[:start] + section.lstrip("\n") + src[end:]

    # The same discipline applies to the REST of the paper: a number that
    # comes from an experiment is written as a token, so the Introduction
    # and the Conclusion cannot drift away from the Results.  The tokens are
    # filled from the same artefact table the prose blocks were filled from.
    src, leftover = fill(src, tok)

    # the marked regions outside the Results section
    for name, (begin, end) in REGIONS.items():
        body, missing = fill(blocks[name], tok)
        src, ok = replace_region(src, begin, end, body)
        if not ok:
            raise SystemExit(f"could not locate the {begin} region in the paper")

    src, leftover = fill(src, tok)

    # The hand-written prose refers to a number by its MACRO, and the macro
    # definitions are written here, from the same table, on every run.  The
    # definitions are therefore regenerated whenever the artefact changes,
    # and the prose cannot drift away from the measurement.  (Filling the
    # tokens in the source instead would freeze the values: an assembly
    # would consume the token, and every later assembly would leave the
    # number where the first one put it.)
    src, ok = write_token_macros(src, tok, leftover)
    if not ok:
        raise SystemExit("could not locate the token-macro region in the paper")

    src, leftover = fill(src, tok)
    if leftover:
        # a token that cannot be filled becomes a visible marker, so that
        # the source is always a paper that compiles and the
        # incompleteness is impossible to miss
        print("WARNING: these tokens are not yet filled and are marked in "
              f"the paper: {', '.join(leftover)}")
        for name in leftover:
            # the token's name carries underscores, which are not legal in
            # LaTeX text mode, so they are escaped
            esc = name.replace("_", r"\_")
            src = src.replace(f"@@{name}@@",
                              r"\textbf{[pending: " + esc + r"]}")

    with open(args.tex, "w", encoding="utf-8") as f:
        f.write(src)
    print(f"Results section replaced in {args.tex}")
    if leftover:
        raise SystemExit("the paper is incomplete: see the tokens above")

    if not args.no_compile:
        for _ in range(3):
            subprocess.run(["pdflatex", "-interaction=nonstopmode",
                            os.path.basename(args.tex)], cwd=PROJ,
                           capture_output=True, text=True)
        log = open(os.path.join(PROJ, "Mlawn-midsem-tex.log"),
                   encoding="utf-8", errors="ignore").read()
        # only ACTUAL undefined references: the string "undefined" also
        # occurs in the font warnings, and counting those would report a
        # reference problem that does not exist
        undef = len(re.findall(r"Reference `[^\']*' on page \d+ undefined",
                                log))
        undef += len(re.findall(r"there were undefined references", log))
        errors = re.findall(r"^! .*$", log, flags=re.M)
        overfull = re.findall(r"^Overfull .*$", log, flags=re.M)
        pages = re.findall(r"Output written on .*?\((\d+) pages", log)
        print(f"undefined references: {undef}; overfull boxes: "
              f"{len(overfull)}; pages: "
              f"{pages[0] if pages else '?'}")
        if errors:
            print("LATEX ERRORS:")
            for e in errors[:10]:
                print("   ", e)
            raise SystemExit("the paper does not compile cleanly")
        if undef:
            print("NOTE: undefined references remain -- check the labels")
        if overfull:
            print("NOTE: overfull boxes:")
            for o in overfull[:10]:
                print("   ", o)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
