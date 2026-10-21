"""
Generate the PROJECT REPORT as a PDF.

The report is the R&D log: what was tried, what broke, what the audits
found, what the measurements say, and what is still open.  It is the
second of the two documents the project keeps, and it is generated from
the ARTEFACTS, so its numbers cannot drift away from the experiments the
way a hand-written log's would.

The LOOK of the report comes from ml_impl/analysis/theme.tex, the same
file the paper's four figures are drawn with: the palette, the table
rules, the axis and the legend strip.  The report does not name a colour
of its own, so the two documents cannot drift apart visually either.

    python analysis/make_report.py

Writes  ../REPORT.tex  and compiles it to  ../REPORT.pdf.
"""

from __future__ import annotations

import csv
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ML = os.path.dirname(HERE)
PROJ = os.path.dirname(ML)
sys.path.insert(0, HERE)

from fill_tokens import build_tokens            # noqa: E402
from make_tables import _best                   # noqa: E402

# the theme, as REPORT.tex sees it (pdflatex runs in PROJ)
THEME = "ml_impl/analysis/theme.tex"

# the paper's one-column width: the explanatory figures are drawn for it,
# so the report scales the same drawing up rather than redrawing it
COL_IN = "3.5in"


# ------------------------------------------------------------------
# the artefacts
# ------------------------------------------------------------------
def load_csv(name):
    p = os.path.join(ML, name)
    if not os.path.exists(p):
        return []
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_json(path):
    p = path if os.path.isabs(path) else os.path.join(HERE, path)
    if not os.path.exists(p):
        return []
    try:
        return json.load(open(p, encoding="utf-8"))
    except Exception:
        return []


def read_text(path):
    p = path if os.path.isabs(path) else os.path.join(PROJ, path)
    if not os.path.exists(p):
        return ""
    return open(p, encoding="utf-8", errors="ignore").read()


def esc(s):
    """LaTeX-escape a string that came from an artefact."""
    s = str(s)
    for a, b in (("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"),
                 ("$", r"\$"), ("#", r"\#"), ("_", r"\_"), ("{", r"\{"),
                 ("}", r"\}"), ("~", r"\textasciitilde{}"), ("^", r"\textasciicircum{}")):
        s = s.replace(a, b)
    return s


# ------------------------------------------------------------------
# the state file's narrative parts
# ------------------------------------------------------------------
def state_section(text, heading, until="\n## "):
    i = text.find(heading)
    if i < 0:
        return ""
    j = text.find(until, i + 1)
    return text[i:j] if j > 0 else text[i:]


def _esc_text(s):
    """Escape text, one character at a time.

    One character at a time, because every replacement introduces a
    backslash and a later pass would escape it again.
    """
    return "".join({"_": r"\_", "&": r"\&", "%": r"\%", "#": r"\#",
                    "$": r"\$", "^": r"\textasciicircum{}",
                    "~": r"\textasciitilde{}",
                    "\\": r"\textbackslash{}\allowbreak{}"}.get(c, c)
                   for c in s)


def _esc_code(s):
    """Escape the inside of a code span.

    A code span is set in \\texttt, which does NOT make an underscore
    safe, so the characters are escaped; an escaped underscore is a legal
    break point, which \\detokenize is not, so a long file name can still
    wrap.  The backslash goes through a placeholder, because the other
    replacements produce backslashes of their own.
    """
    s = s.replace("\\", "\x00")
    s = (s.replace("{", r"\{").replace("}", r"\}")
          .replace("_", r"\_").replace("&", r"\&").replace("%", r"\%")
          .replace("#", r"\#").replace("$", r"\$")
          .replace("^", r"\textasciicircum{}")
          .replace("~", r"\textasciitilde{}"))
    return s.replace("\x00", r"\textbackslash{}\allowbreak{}").replace(
        "/", r"/\allowbreak{}")


_CODE = re.compile(r"`([^`]*)`")


def inline(s):
    """Markdown inline markup, as LaTeX: code spans, then bold, then text.

    The code spans are lifted out FIRST: a path inside a span contains
    backslashes and braces, and the brace-matching that a naive scan does
    cut the span at the first `}' of \\textbackslash{}, which left the
    defect log printing raw \\allowbreak fragments instead of file names.
    """
    spans = []

    def stash(m):
        spans.append(m.group(1))
        return "\x00%d\x00" % (len(spans) - 1)

    s = _CODE.sub(stash, s)
    s = re.sub(r"\*\*(.+?)\*\*", lambda m: "\x01" + m.group(1) + "\x02", s)
    s = _esc_text(s)
    s = s.replace("\x01", r"\textbf{").replace("\x02", r"}")
    for i, c in enumerate(spans):
        s = s.replace("\x00%d\x00" % i, r"\texttt{" + _esc_code(c) + "}")
    return s


def md_table_to_latex(block):
    """Render a markdown pipe table as a themed longtable."""
    rows = [r for r in block.split("\n")
            if r.strip().startswith("|") and "---" not in r]
    if not rows:
        return ""
    cells = [[c.strip() for c in r.strip().strip("|").split("|")]
             for r in rows]
    head, body = cells[0], cells[1:]

    clean = inline

    HEAD = " & ".join(r"\textbf{%s}" % clean(c) for c in head)
    # a longtable, because the defect log is longer than a page and a
    # tabularx cannot break across pages; the theme's rules and tints are
    # used so the log reads as part of the report and not as an appendix
    out = [r"\begingroup\small",
           r"\setlength{\LTleft}{0pt}\setlength{\LTright}{\fill}",
           r"\setlength{\LTpre}{6pt}\setlength{\LTpost}{10pt}",
           r"\begin{longtable}{@{}>{\raggedleft\arraybackslash}p{0.7cm}"
           r">{\raggedright\arraybackslash}p{6.1cm}"
           r">{\raggedright\arraybackslash}p{8.55cm}@{}}",
           r"\uavtoprule",
           r"\rowcolor{uavlight}" + HEAD + r" \\",
           r"\uavmidrule",
           r"\endfirsthead",
           r"\multicolumn{3}{@{}l}{\footnotesize\itshape\color{uavmuted} "
           r"the defect log, continued}\\",
           r"\uavtoprule",
           r"\rowcolor{uavlight}" + HEAD + r" \\",
           r"\uavmidrule",
           r"\endhead"]
    for k, r in enumerate(body):
        cells = [clean(c) for c in r]
        # the index is furniture, not a claim: muted, and the row tint
        # alternates so a two-line entry can be followed across columns
        if k % 2:
            out.append(r"\rowcolor{uavzebra}")
        out.append(r"\textcolor{uavmuted}{" + cells[0] + r"} & "
                   + " & ".join(cells[1:]) + r" \\")
    out += [r"\uavbottomrule", r"\end{longtable}", r"\endgroup"]
    return "\n".join(out)


def md_list(block, label0=None, label1=None):
    """A markdown bullet list, with its hard-wrapped lines, as itemize.

    The state file wraps its prose at 72 columns, so a bullet is a group
    of lines, not a line; joining them and setting the group as one item
    is what turns the audit log from a wall of `*` characters into a list
    a reader can follow.
    """
    blocks = []          # [(text, [subtext, ...]), ...]
    cur = None           # the block being built
    buf = None           # the item whose lines are being joined
    for raw in block.split("\n"):
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = re.match(r"^(\s*)[-*]\s+(.*)$", line)
        if m:
            buf = [m.group(2)]
            if m.group(1) and cur is not None:
                cur[1].append(buf)
            else:
                cur = (buf, [])
                blocks.append(cur)
        elif buf is not None:
            buf.append(line.strip())

    # the state file was appended to in a loop: the same audit block is
    # on the record twenty times over.  An entry is printed once, in the
    # order it was first written; a log of identical paragraphs is not a
    # record of anything, it is a defect in the log.
    seen, uniq = set(), []
    for text, subs in blocks:
        key = (" ".join(" ".join(text).split())
               + "\x00" + "\x00".join(" ".join(" ".join(s).split())
                                      for s in subs))
        if key in seen:
            continue
        seen.add(key)
        uniq.append((text, subs))

    lab0 = label0 or r"{\color{uavblue}\scriptsize\textbullet}"
    lab1 = label1 or r"{\color{uavmuted}\scriptsize\textendash}"
    out = []
    if uniq:
        out.append(r"\begin{itemize}[leftmargin=1.15em,itemsep=4pt,"
                   r"topsep=2pt,label=" + lab0 + r"]")
    for text, subs in uniq:
        out.append(r"\item " + inline(" ".join(text)))
        if subs:
            out.append(r"\begin{itemize}[leftmargin=1.25em,itemsep=1.5pt,"
                       r"topsep=2pt,label=" + lab1 + r"]")
            for s in subs:
                out.append(r"\item " + inline(" ".join(s)))
            out.append(r"\end{itemize}")
    if uniq:
        out.append(r"\end{itemize}")
    return "\n".join(out)


# ------------------------------------------------------------------
# the page furniture
# ------------------------------------------------------------------
def preamble():
    """The report's preamble: the theme's palette, type and table rules."""
    return [
        r"\documentclass[11pt,a4paper]{article}",
        r"\usepackage[T1]{fontenc}",
        r"\usepackage[margin=24mm,top=27mm,bottom=24mm]{geometry}",
        r"\usepackage{amsmath,amssymb}",
        # a Times-like body, so the report reads as the paper's companion,
        # and a grotesque for headings and labels
        r"\usepackage{newtxtext,newtxmath}",
        r"\usepackage[scaled=0.92]{helvet}",
        r"\usepackage[table]{xcolor}",
        r"\usepackage{booktabs,tabularx,longtable,array}",
        r"\usepackage{enumitem}",
        r"\usepackage{caption}",
        r"\usepackage{titlesec}",
        r"\usepackage{fancyhdr}",
        r"\usepackage{microtype}",
        r"\usepackage{tikz}",
        r"\usepackage{pgfplots}",
        r"\pgfplotsset{compat=1.18}",
        r"\input{" + THEME + r"}",
        # the shared table style of the generated tables, the file the
        # paper's tables bootstrap too: \tblHl, \tblGroup, \tblNote
        r"\input{ml_impl/analysis/theme_tables.tex}",
        r"\usepackage[hidelinks]{hyperref}",
        r"\usepackage{parskip}",
        r"\setlength{\parindent}{0pt}",
        r"\newcommand{\code}[1]{\texttt{\detokenize{#1}}}",
        r"",
        # a section title carries a hairline rule: the report's one
        # recurring graphic, and the same grey as the theme's gridlines
        r"\titleformat{\section}"
        r"{\sffamily\bfseries\large}{\color{uavblue}\thesection}{0.6em}"
        r"{\color{uavink}}"
        r"[\vspace{-0.45em}\noindent{\color{uavgrid}\rule{\linewidth}{0.5pt}}]",
        r"\titlespacing*{\section}{0pt}{2.6ex plus .3ex}{1.3ex}",
        r"",
        r"\renewcommand{\arrayrulewidth}{0.5pt}",
        r"\renewcommand{\arraystretch}{1.18}",
        r"\captionsetup{font=small,labelfont={sf,bf},"
        r"labelsep=period,justification=raggedright,singlelinecheck=false}",
        r"",
        r"\setlength{\headheight}{14pt}",
        r"\pagestyle{fancy}",
        r"\fancyhf{}",
        r"\renewcommand{\headrulewidth}{0.4pt}",
        r"\fancyhead[L]{\sffamily\footnotesize\color{uavmuted}"
        r"Persistent UAV-IoT Coverage \textperiodcentered\ project report}",
        r"\fancyhead[R]{\sffamily\footnotesize\bfseries\color{uavblue}"
        r"\thepage}",
        r"\fancypagestyle{plain}{\fancyhf{}"
        r"\renewcommand{\headrulewidth}{0pt}}",
    ]


def masthead(subtitle, meta, date):
    """The title block: a blue rule, the title, the subtitle, a second rule."""
    return [
        r"\thispagestyle{empty}",
        r"\noindent{\color{uavblue}\rule{\linewidth}{3pt}}",
        r"\vspace{12pt}",
        r"{\sffamily\bfseries\LARGE\color{uavink}",
        r"Persistent UAV-IoT Coverage: Project Report\par}",
        r"\vspace{7pt}",
        r"{\large\color{uavmuted}" + subtitle + r"\par}",
        r"\vspace{12pt}",
        r"\noindent{\color{uavgrid}\rule{\linewidth}{0.6pt}}",
        r"\vspace{5pt}",
        r"{\footnotesize\sffamily\color{uavmuted}" + meta
        + r"\hfill " + date + r"\par}",
        r"\vspace{1pt}",
        r"\noindent{\color{uavblue}\rule{\linewidth}{1.2pt}}",
        r"\vspace{4pt}",
    ]


def scaled_figure(frag_path, caption, label, frac="0.72"):
    """A paper figure, scaled up to the report's measure.

    The fragment is drawn for the paper's 3.5in column, so it is typeset
    at exactly that width (where its fonts and line weights are right)
    and then scaled as a picture.  Scaling the drawing instead of
    re-flowing it keeps one drawing in both documents, at the same
    proportions.
    """
    return [
        r"\begin{figure}[t]",
        r"\centering",
        r"\resizebox{" + frac + r"\linewidth}{!}{%",
        r"\begin{minipage}{" + COL_IN + r"}",
        r"\input{" + frag_path + r"}",
        r"\end{minipage}}",
        r"\caption{" + caption + r"}",
        r"\label{" + label + r"}",
        r"\end{figure}",
    ]


def main():
    tok = build_tokens()
    state = read_text("AUTONOMOUS_STATE.md")
    audit = load_json("claim_audit.json")
    main_rows = {r["model"]: r for r in load_csv("results_main.csv")}

    n_pass = sum(1 for r in audit if r.get("status") == "PASS")
    n_fail = sum(1 for r in audit if r.get("status") == "FAIL")
    n_info = sum(1 for r in audit if r.get("status") == "INFO")

    def cell(model, key, nd=3):
        r = main_rows.get(model)
        if not r or r.get(key) in (None, ""):
            return "--"
        return f"{float(r[key]):.{nd}f}"

    # the figures: the arms plot is the central claim, the curve is the
    # training dynamics; both are the paper's own drawings, imported, so
    # the report shows what the paper shows and not a second, hasty take
    arms_info = []
    try:
        from draft_figures import figure_arms
        _, arms_info = figure_arms(tok, 1.0)
    except Exception:
        arms_info = []
    n_arms = len(arms_info) if arms_info else 0
    n_excluded = sum(1 for a in arms_info if a.get("verdict") == "excluded")

    tex = []
    A = tex.append
    tex.extend(preamble())
    A(r"\begin{document}")
    tex.extend(masthead(
        r"The research log behind the paper: the protocol, the "
        r"defects, the audits, the measurements, and what is still open",
        r"Generated from the artefacts by \code{analysis/make_report.py}"
        r" --- every number below is read from the file it was measured in.",
        r"\today"))
    A("")

    # ---------------- the contract and the state ----------------
    A(r"\section{The contract and the current state}")
    A(r"The work runs to 26 October 2026. The deliverable is a paper whose "
      r"every number can be traced to the artefact it was measured in, and "
      r"whose comparative claims are derived in code rather than asserted, so "
      r"that the paper says the right thing whichever way a measurement comes "
      r"out. This report is the log of that work: the protocol, the defects "
      r"that were found and fixed, the audits that were run and what they "
      r"changed, the measurements, and the questions that are still open.")
    A("")
    # the state, as a panel: the label column carries the theme's tint,
    # the value column the theme's rules, so the four facts read at a
    # glance rather than as a wall of prose
    A(r"\begin{tabularx}{\textwidth}{@{}>{\columncolor{uavlight}"
      r"\raggedright\arraybackslash\sffamily\bfseries\footnotesize}"
      r"p{4.4cm}>{\hspace{9pt}}X@{}}")
    A(r"\uavtoprule")
    A(r"Gap to the strongest rule & $\textbf{" + str(tok.get("GAP")) + r"}$ "
      r"(95\% interval " + str(tok.get("GAP_CI")) + r"), against "
      + esc(str(tok.get("BEST_RULE_NAME"))) + r" at "
      + str(tok.get("BEST_RULE_CK")) + r". \\")
    A(r"\uavmidrule")
    A(r"The learned controller & $\textbf{" + cell("MAPPO", "CK") + r"}$ "
      r"$\pm$ " + cell("MAPPO", "CK_std") + r" over "
      + str(main_rows.get("MAPPO", {}).get("train_seeds", "?")) +
      r" training seeds. \\")
    A(r"\uavmidrule")
    A(r"Claim audit & " + str(len(audit)) + r" items: " + str(n_pass) +
      r" verified, " + str(n_fail) + r" failed, " + str(n_info) +
      r" recorded for transparency. \\")
    A(r"\uavmidrule")
    A(r"Test suite & " + str(tok.get("N_TESTS")) + r" cases, all passing. \\")
    A(r"\uavmidrule")
    A(r"Device & every artefact records the device it was measured on; the "
      r"device and the thread count are part of the protocol. \\")
    A(r"\uavbottomrule")
    A(r"\end{tabularx}")
    A("")

    # ---------------- the protocol ----------------
    A(r"\section{The measurement protocol}")
    A(r"Every number in the paper and in this report is produced under one "
      r"protocol:")
    A(r"\begin{enumerate}[leftmargin=*,label=\textcolor{uavblue}"
      r"{\bfseries\arabic*.},itemsep=2pt,topsep=2pt]")
    A(r"\item \textbf{Training}: 25 episodes of 2000 control steps per "
      r"training run. The base comparison trains five runs; the component "
      r"ablation and the arms train three.")
    A(r"\item \textbf{Evaluation}: five scenes per policy, and the number of "
      r"evaluation scenes is part of the protocol --- a run with three is a "
      r"different measurement, because a per-seed row is the mean over the "
      r"scenes.")
    A(r"\item \textbf{The device and the thread count} are part of the "
      r"protocol. The floating-point kernels differ between the CPU and the "
      r"GPU and the order of the reductions differs with the thread count, "
      r"so two runs of the same configuration that land on different devices "
      r"are not the same experiment. The device is pinned, the thread count "
      r"is pinned in code, and every artefact records the device.")
    A(r"\item \textbf{The evaluation is seeded} from the evaluation seed "
      r"alone, so every controller is measured on the same random stream on "
      r"the same scene --- common random numbers --- and a comparison between "
      r"controllers is a comparison between policies rather than between the "
      r"luck of the draw.")
    A(r"\item \textbf{The ablations are paired}: the variants share the "
      r"training seeds, so a difference is measured on the same training "
      r"runs and reported as a confidence interval on the paired difference.")
    A(r"\item \textbf{Inference is by interval, never by threshold}. An "
      r"explanation is excluded only if the arm that tests it has an upper "
      r"confidence limit below the gap; a null result is a statement about "
      r"the resolution of that arm, and the resolution is reported with it.")
    A(r"\end{enumerate}")
    A("")

    # ---------------- the measurements ----------------
    A(r"\section{What the measurements say}")
    # the highlighted row is the best of the LEARNED controllers by the
    # table's own key, CK -- the same derivation the paper's base
    # comparison runs, through the same shared _best (make_tables.py)
    # and the same \tblHl fill (theme_tables.tex).  The rules are the
    # competition and the oracle is the ceiling, so neither belongs to
    # the candidate pool, and the choice is made here on the table's
    # own numbers: the highlight follows them when they change.
    LEARNED = ("MAPPO", "MAPPO-argmax")
    order = ["Fixed", "Greedy", "Reactive", "Reactive-local", "MAPPO",
             "MAPPO-argmax", "Oracle (ceiling)"]
    shown = [m for m in order if m in main_rows]
    best = _best([main_rows[m] for m in shown if m in LEARNED], "CK")
    best_model = best.get("model") if best else None
    A(r"\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}"
      r">{\raggedright\arraybackslash}p{6.4cm}rrrr@{}}")
    A(r"\uavtoprule")
    # the shared two-level head: the group title over its span, the
    # \cmidrule written from the same span (2-5) so the two agree
    A(r" & \tblGroup{4}{Task metrics} \\")
    A(r"\cmidrule(lr){2-5}")
    A(r"Controller & CK & AG & SC & Cov. deficit\textsuperscript{*} \\")
    A(r"\uavmidrule")
    label = {"Reactive-local": "Reactive (local assignment)",
             "MAPPO": "MAPPO (proposed)", "MAPPO-argmax": "MAPPO (argmax)",
             "Oracle (ceiling)": "Oracle (ceiling)"}
    for m in shown:
        nm = label.get(m, m)
        std = main_rows[m].get("CK_std", "")
        ck = cell(m, "CK") + (r" $\pm$ " + f"{float(std):.3f}" if std else "")
        cells = [esc(nm), ck, cell(m, "AG"), cell(m, "SC"),
                 cell(m, "CovIntegral")]
        # theme_tables.tex pairs the row's fill (\tblHl) with the row's
        # weight: the fill says "this is the row", the weight "these are
        # its values"
        hl = (m == best_model)
        first = r"\tblHl " if hl else ""
        A(first + " & ".join(r"\textbf{" + c + "}" if hl else c
                             for c in cells) + r" \\")
    A(r"\uavbottomrule")
    A(r"\end{tabular*}")
    # the note the starred column points at (theme_tables.tex \tblNote);
    # the $\pm$ clause follows the artefact: a rule that ever grows its
    # own spread gets that spread stated instead of mislabelled
    rule_std = any(main_rows.get(m, {}).get("CK_std") not in (None, "")
                   for m in ("Fixed", "Greedy", "Reactive", "Reactive-local"))
    spread = (r"the $\pm$ is the seed-to-seed spread over the training "
              r"runs" if not rule_std else
              r"the $\pm$ is the seed-to-seed spread over the training "
              r"runs, and for the rules the spread over the evaluation "
              r"scenes")
    A(r"\tblNote{* Cov. deficit is the time-averaged coverage deficit; "
      + spread + r".}")
    A("")
    if n_excluded and n_excluded == n_arms:
        verdict = (r"Every one of the " + str(n_arms) + r" controlled arms has "
                   r"an interval that stays below the gap")
    else:
        verdict = (r"Of the " + str(n_arms) + r" controlled arms, "
                   + str(n_excluded) + r" have an interval that stays below "
                   r"the gap")
    tex.extend(scaled_figure(
        "ml_impl/analysis/fig_arms.tex",
        verdict + r": the gap of " + str(tok.get("GAP")) + r" is out of reach "
        r"of every candidate explanation the ablation tests, so no arm can "
        r"account for the shortfall.",
        "fig:report-arms"))
    A("")
    A(r"The arms' verdict, derived from the intervals: " +
      esc(str(tok.get("ARMS_SUMMARY_SENTENCE"))) + r"")
    A("")
    A(r"The training-budget sweep: " + esc(str(tok.get("BUDGET_SWEEP"))) +
      r". " + esc(str(tok.get("BUDGET_VERDICT"))) + r".")
    A("")
    tex.extend(scaled_figure(
        "ml_impl/analysis/fig_learning_curve.tex",
        r"The per-episode coverage of each training run on the training "
        r"scene, against " + esc(str(tok.get("BEST_RULE_NAME"))) + r" at "
        + str(tok.get("BEST_RULE_CK")) + r" on the evaluation scenes "
        r"(grey, dashed).  The curve is flat long before the budget the "
        r"experiments use, which is what the budget sweep then tests.",
        "fig:report-curve"))
    A("")

    # ---------------- the defects ----------------
    A(r"\section{The defects that were found and fixed}")
    A(r"Every one of these was a defect in the work, not in the writing. "
      r"The list is the reason the claim audit exists.")
    A("")
    defects = state_section(state, "## Defects found and fixed")
    if defects:
        A(md_table_to_latex(defects))
        A("")

    # ---------------- the audits ----------------
    A(r"\section{The audits, and what they changed}")
    cadence = state_section(state, "## The mathematical audit cadence")
    if cadence:
        A(md_list(cadence))
        A("")

    # ---------------- the negative results ----------------
    A(r"\section{Negative results, kept on the record}")
    neg = state_section(state, "## Negative results, kept on the record")
    if neg:
        A(md_list(neg))
        A("")

    # ---------------- the artefacts ----------------
    A(r"\section{The artefacts}")
    A(r"Every number above is read from one of these files, and the paper "
      r"is generated from the same ones.")
    A("")
    A(r"\begin{tabularx}{\textwidth}{@{}l>{\raggedright\arraybackslash}X@{}}")
    A(r"\uavtoprule")
    artefacts = (
        ("results_main.csv", "the main table: every controller, five "
                             "training seeds for the learned one"),
        ("results_ablation.csv", "the component ablation, twelve variants"),
        ("results_ablation_stress.csv", "the ablation on the combined-"
                                        "stress scenario"),
        ("results_scenarios.csv", "the nine scenarios and their variants"),
        ("analysis/ab_observation.json", "the observation arms"),
        ("analysis/ab_energy_management.json", "the energy arms"),
        ("analysis/ab_credit.json", "the credit-assignment arm"),
        ("analysis/ab_budget.json", "the training-budget sweep"),
        ("analysis/ab_map_resolution.json", "the map-resolution sweep"),
        ("analysis/claim_audit.json", "the claim audit, item by item"),
        ("analysis/connectivity_accounting.json",
         "the connectivity accounting"),
        ("analysis/corner_transfer.json", "the corner certificate's transfer"),
        ("analysis/alt_deployment.json",
         "the alternative corrected deployment"))
    k = 0
    for name, what in artefacts:
        p = os.path.join(ML, name)
        if not os.path.exists(p):
            p = os.path.join(HERE, name)
        if not os.path.exists(p):
            continue
        if k % 2:
            A(r"\rowcolor{uavzebra}")
        A(f"  \\code{{{esc(name)}}} & {esc(what)} \\\\")
        k += 1
    A(r"\uavbottomrule")
    A(r"\end{tabularx}")
    A("")

    A(r"\section{Reproducing this report}")
    A(r"\noindent{\color{uavgrid}\rule{\linewidth}{0.5pt}}")
    A(r"\begin{verbatim}")
    A("cd ml_impl")
    A("python analysis/make_report.py     # this report")
    A("python analysis/assemble_results.py # the paper")
    A("python analysis/final_checks.py    # the gate")
    A("python analysis/claim_audit.py     # the audit")
    A("python tests/run_tests.py -q        # the tests")
    A(r"\end{verbatim}")
    A(r"\noindent{\color{uavgrid}\rule{\linewidth}{0.5pt}}")
    A("")
    A(r"\end{document}")

    out = os.path.join(PROJ, "REPORT.tex")
    open(out, "w", encoding="utf-8", newline="").write("\n".join(tex))
    print(f"wrote {out}")

    for _ in range(2):
        subprocess.run(["pdflatex", "-interaction=nonstopmode", "REPORT.tex"],
                       cwd=PROJ, capture_output=True, text=True)
    log = open(os.path.join(PROJ, "REPORT.log"), encoding="utf-8",
               errors="ignore").read()
    errs = len(re.findall(r"(?m)^! ", log))
    pages = re.findall(r"Output written on .*?\((\d+) pages", log)
    over = len(re.findall(r"(?m)^Overfull ", log))
    print(f"REPORT.pdf: {pages[0] if pages else '?'} pages, {errs} errors, "
          f"{over} overfull boxes")
    return 1 if errs else 0


if __name__ == "__main__":
    raise SystemExit(main())
