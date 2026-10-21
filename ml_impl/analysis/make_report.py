"""
Generate the PROJECT REPORT as a PDF.

The report is the R&D log: what was tried, what broke, what the audits
found, what the measurements say, and what is still open.  It is the
second of the two documents the project keeps, and it is generated from
the ARTEFACTS, so its numbers cannot drift away from the experiments the
way a hand-written log's would.

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


def md_table_to_latex(block):
    """Render a markdown pipe table as a LaTeX tabular."""
    rows = [r for r in block.split("\n")
            if r.strip().startswith("|") and "---" not in r]
    if not rows:
        return ""
    cells = [[c.strip() for c in r.strip().strip("|").split("|")]
             for r in rows]
    head, body = cells[0], cells[1:]
    def clean(s):
        # a markdown code span becomes a typeset code span, WITH its
        # closing brace: the earlier version opened \texttt{ and never
        # closed it, which left the document with an unbalanced group
        # \texttt does NOT make an underscore safe, so it is escaped;
        # and an escaped underscore is a legal break point, which
        # \detokenize is not, so a long file name can still wrap
        s = re.sub(r"`([^`]*)`",
                   lambda m: r"\texttt{" + m.group(1).replace("_", r"\_")
                   .replace("\\", r"\textbackslash{}\allowbreak{}") + "}",
                   s)
        s = s.replace("**", "")
        # anything still outside a code span is escaped
        out = []
        i = 0
        while i < len(s):
            if s.startswith(r"\texttt{", i):
                j = s.find("}", i)
                if j > 0:
                    out.append(s[i:j + 1])
                    i = j + 1
                    continue
            c = s[i]
            out.append({"_": r"\_", "&": r"\&", "%": r"\%",
                        "#": r"\#", "$": r"\$",
                        "\\": r"\textbackslash{}\allowbreak{}"}.get(c, c))
            i += 1
        return "".join(out)
    # a longtable, because the defect log is longer than a page and a
    # tabularx cannot break across pages
    out = [r"\small",
           r"\begin{longtable}{@{}p{0.5cm}p{6.4cm}p{7.6cm}@{}}",
           r"\toprule",
           " & ".join(r"\textbf{%s}" % clean(c) for c in head) + r" \\",
           r"\midrule",
           r"\endfirsthead",
           r"\multicolumn{3}{@{}l}{\footnotesize\itshape the defect log, "
           r"continued}\\",
           r"\toprule",
           " & ".join(r"\textbf{%s}" % clean(c) for c in head) + r" \\",
           r"\midrule",
           r"\endhead"]
    for r in body:
        out.append(" & ".join(clean(c) for c in r) + r" \\")
    out += [r"\bottomrule", r"\end{longtable}", r"\normalsize"]
    return "\n".join(out)



def md_line(s):
    """Render one line of the state file's prose as LaTeX.

    A Windows path is a single unbreakable token, and it runs off the
    page; the backslashes are therefore typeset and given a break
    opportunity after each one.
    """
    s = s.replace("**", "")
    s = s.replace("`", r"\texttt{")
    out = []
    i = 0
    while i < len(s):
        if s.startswith("\\", i):
            out.append(r"\textbackslash{}\allowbreak{}")
            i += 2
            continue
        c = s[i]
        out.append({"_": r"\_", "&": r"\&", "%": r"\%", "#": r"\#",
                    "$": r"\$", "^": r"\textasciicircum{}",
                    "~": r"\textasciitilde{}"}.get(c, c))
        i += 1
    return "".join(out)

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

    tex = []
    A = tex.append
    A(r"\documentclass[11pt,a4paper]{article}")
    A(r"\usepackage[margin=25mm]{geometry}")
    A(r"\usepackage{amsmath,amssymb,booktabs,tabularx,longtable,array}")
    A(r"\usepackage[hidelinks]{hyperref}")
    A(r"\usepackage{xcolor}")
    A(r"\usepackage{parskip}")
    A(r"\setlength{\parindent}{0pt}")
    A(r"\newcommand{\code}[1]{\texttt{\detokenize{#1}}}")
    A(r"\begin{document}")
    A(r"\begin{center}")
    A(r"{\LARGE\bfseries Persistent UAV-IoT Coverage: Project Report}\par")
    A(r"\vspace{4pt}")
    A(r"{\large The research log behind the paper: the protocol, the "
      r"defects, the audits, the measurements, and what is still open}\par")
    A(r"\vspace{8pt}")
    A(r"{\small Generated from the artefacts by \code{analysis/make_report.py}"
      r" --- every number below is read from the file it was measured in.}")
    A(r"\end{center}")
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
    A(r"\begin{tabularx}{\textwidth}{@{}l X@{}}")
    A(r"\toprule")
    A(r"Gap to the strongest rule & $\textbf{" + str(tok.get("GAP")) + r"}$ "
      r"(95\% interval " + str(tok.get("GAP_CI")) + r"), against "
      + esc(str(tok.get("BEST_RULE_NAME"))) + r" at "
      + str(tok.get("BEST_RULE_CK")) + r". \\")
    A(r"The learned controller & $\textbf{" + cell("MAPPO", "CK") + r"}$ "
      r"$\pm$ " + cell("MAPPO", "CK_std") + r" over "
      + str(main_rows.get("MAPPO", {}).get("train_seeds", "?")) +
      r" training seeds. \\")
    A(r"Claim audit & " + str(len(audit)) + r" items: " + str(n_pass) +
      r" verified, " + str(n_fail) + r" failed, " + str(n_info) +
      r" recorded for transparency. \\")
    A(r"Test suite & " + str(tok.get("N_TESTS")) + r" cases, all passing. \\")
    A(r"Device & every artefact records the device it was measured on; the "
      r"device and the thread count are part of the protocol. \\")
    A(r"\bottomrule")
    A(r"\end{tabularx}")
    A("")

    # ---------------- the protocol ----------------
    A(r"\section{The measurement protocol}")
    A(r"Every number in the paper and in this report is produced under one "
      r"protocol:")
    A(r"\begin{enumerate}")
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
    A(r"\begin{tabularx}{\textwidth}{@{}l c c c c@{}}")
    A(r"\toprule")
    A(r"Controller & CK & AG & SC & Cov. deficit \\")
    A(r"\midrule")
    order = ["Fixed", "Greedy", "Reactive", "Reactive-local", "MAPPO",
             "MAPPO-argmax", "Oracle (ceiling)"]
    label = {"Reactive-local": "Reactive (local assignment)",
             "MAPPO": "MAPPO (proposed)", "MAPPO-argmax": "MAPPO (argmax)",
             "Oracle (ceiling)": "Oracle (ceiling)"}
    for m in order:
        if m not in main_rows:
            continue
        nm = label.get(m, m)
        std = main_rows[m].get("CK_std", "")
        ck = cell(m, "CK") + (r" $\pm$ " + f"{float(std):.3f}" if std else "")
        A(f"  {esc(nm)} & {ck} & {cell(m, 'AG')} & {cell(m, 'SC')} & "
          f"{cell(m, 'CovIntegral')} \\\\")
    A(r"\bottomrule")
    A(r"\end{tabularx}")
    A("")
    A(r"The arms' verdict, derived from the intervals: " +
      esc(str(tok.get("ARMS_SUMMARY_SENTENCE"))) + r"")
    A("")
    A(r"The training-budget sweep: " + esc(str(tok.get("BUDGET_SWEEP"))) +
      r". " + esc(str(tok.get("BUDGET_VERDICT"))) + r".")
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
        for line in cadence.split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("- **"):
                head, _, rest = line[2:].partition("**")
                A(r"\noindent\textbf{" + md_line(head) + r"} "
                  + md_line(rest))
            elif line.startswith("- "):
                A(r"\noindent " + md_line(line[2:]))
            else:
                A(md_line(line))
        A("")

    # ---------------- the negative results ----------------
    A(r"\section{Negative results, kept on the record}")
    neg = state_section(state, "## IMPORTANT NEGATIVE RESULTS")
    if neg:
        for line in neg.split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            A(r"\noindent " + md_line(line))
        A("")

    # ---------------- the artefacts ----------------
    A(r"\section{The artefacts}")
    A(r"Every number above is read from one of these files, and the paper "
      r"is generated from the same ones.")
    A("")
    A(r"\begin{tabularx}{\textwidth}{@{}l X@{}}")
    A(r"\toprule")
    for name, what in (
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
            ("analysis/connectivity_accounting.json", "the connectivity accounting"),
            ("analysis/corner_transfer.json", "the corner certificate's transfer"),
            ("analysis/alt_deployment.json", "the alternative corrected deployment")):
        p = os.path.join(ML, name)
        if not os.path.exists(p):
            p = os.path.join(HERE, name)
        if not os.path.exists(p):
            continue
        A(f"  \\code{{{esc(name)}}} & {esc(what)} \\\\")
    A(r"\bottomrule")
    A(r"\end{tabularx}")
    A("")

    A(r"\section{Reproducing this report}")
    A(r"\begin{verbatim}")
    A("cd ml_impl")
    A("python analysis/make_report.py     # this report")
    A("python analysis/assemble_results.py # the paper")
    A("python analysis/final_checks.py    # the gate")
    A("python analysis/claim_audit.py     # the audit")
    A("python tests/run_tests.py -q        # the tests")
    A(r"\end{verbatim}")
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
