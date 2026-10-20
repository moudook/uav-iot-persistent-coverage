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

MARKERS = ["%% MAIN", "%% OBS", "%% ENERGY", "%% ABL", "%% SCEN"]


def read_blocks(path):
    if not os.path.exists(path):
        return {m.strip(): "" for m in MARKERS}
    raw = open(path, encoding="utf-8").read()
    parts = re.split(r"^%%\s*(MAIN|OBS|ENERGY|ABL|SCEN)\s*$", raw,
                     flags=re.M)
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
    for script in ("make_tables.py", "fill_tokens.py"):
        r = subprocess.run([sys.executable,
                            os.path.join(HERE, script)],
                           capture_output=True, text=True)
        print(r.stdout.strip() or r.stderr.strip())
    tables = open(TABLES, encoding="utf-8").read()
    blocks = read_blocks(TEXT)

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
            raise SystemExit(f"table {name} was not generated")
        return tparts[name]

    section = f"""
\\section{{Results}}
\\label{{sec:results}}

All experiments use the corrected, feasible configuration $N=8$, $K=2$,
$R_{{\\mathrm{{cov}}}}=35$\\,m on an $80\\times80$\\,m field
(Section~\\ref{{sec:feasibility}}), the clustered initial deployment and the
2000-step episode of Section~\\ref{{sec:parameters}}.  Every controller is
evaluated on the same scenes with the same seeds, and the rule baselines and
the learned controllers are trained on the same budget.  The teleporting
placement oracle reaches $CK=1.000$ on this configuration; it is the
ceiling against which every coverage number below is meant to be read, and
it is what makes the comparison meaningful: a number without a ceiling
cannot distinguish a weak controller from an infeasible configuration.

Two things are true of this configuration, and we report both.  First, the
task is not hard at the parameters the project specifies: a deterministic
reactive heuristic that assigns UAVs to uncovered sensors reaches
$CK=0.947$ while maintaining full connectivity.  Second, the learned
controller does not reach that figure, and the ablations below identify
why.  The limiting factor is neither the content of the observation nor the
energy model, but the credit assignment of a parameter-shared actor trained
on a team reward.

{tab('tab:results_main')}

{blocks['%% MAIN']}

\\subsection{{What the local observation must contain}}
\\label{{sec:results_obs}}

The observation of Eq.~\\eqref{{eq:obs}} is the interface between the
framework's communication assumption and the shared policy, and the claim
that parameter sharing requires the observation to identify the agent is
testable.  Table~\\ref{{tab:results_obs}} compares three observations under
identical seeds, budget and evaluation scenes: the observation of
Eq.~\\eqref{{eq:obs}} as originally written; the same observation plus a
one-hot agent identity; and that plus the broadcast coverage-map summary.

{tab('tab:results_obs')}

{blocks['%% OBS']}

\\subsection{{Energy management, and the reward that was missing it}}
\\label{{sec:results_energy}}

The step-level diagnostic of the learned policy produced a surprising
number: it stranded \\emph{{all eight}} UAVs in nearly every episode, while
the reactive heuristic stranded $0.7$.  A stranded UAV has an empty pack
away from a charging pad; it can no longer fly, it leaves the swarm, and it
stops covering.  The obvious reading is that the controller has failed at
energy management, and the obvious fix is a reward term that prices the
consequence of an empty pack.  Table~\\ref{{tab:results_energy}} tests that
reading with two controlled arms: the same policy with a pack that cannot
run out, and the same policy without the threshold-violation term of
Table~\\ref{{tab:reward}}.

{tab('tab:results_energy')}

{blocks['%% ENERGY']}

\\subsection{{Component ablation}}
\\label{{sec:results_abl}}

{tab('tab:results_abl')}

{blocks['%% ABL']}

{tab('tab:results_ablstress')}

\\subsection{{Scenario matrix}}
\\label{{sec:results_scen}}

{tab('tab:results_scen')}

{blocks['%% SCEN']}

"""

    src = open(args.tex, encoding="utf-8").read()
    start = src.find("\\section{Results}")
    end = src.find("\\subsection{Claim Audit and Physical-Layer Validation}")
    if start < 0 or end < 0 or end < start:
        raise SystemExit("could not locate the Results section")
    new = src[:start] + section.lstrip("\n") + src[end:]
    with open(args.tex, "w", encoding="utf-8") as f:
        f.write(new)
    print(f"Results section replaced in {args.tex}")

    if not args.no_compile:
        for _ in range(3):
            subprocess.run(["pdflatex", "-interaction=nonstopmode",
                            os.path.basename(args.tex)], cwd=PROJ,
                           capture_output=True, text=True)
        log = open(os.path.join(PROJ, "Mlawn-midsem-tex.log"),
                   encoding="utf-8", errors="ignore").read()
        undef = len(re.findall(r"undefined", log))
        pages = re.findall(r"Output written on .*?\((\d+) pages", log)
        print(f"undefined references: {undef}; pages: "
              f"{pages[0] if pages else '?'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
