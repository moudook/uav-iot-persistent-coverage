"""
The learning curve, as a figure.

The audit asked for a learning curve to answer the compute-asymmetry
objection: a hand-designed rule embeds a human's solution while the
learner gets a fixed budget, and the reader is entitled to see whether the
curve had flattened at that budget.  The curves are the per-episode coverage
of each training run, which the base stage saves, and the reference line is
the reactive heuristic's coverage on the same scenes.

Run:  python analysis/make_figures.py
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ML = os.path.dirname(HERE)
OUT = os.path.join(HERE, "fig_learning_curve.tex")


def histories():
    """The per-episode coverage of every training run, in seed order."""
    per_seed = []
    for s in range(8):
        p = os.path.join(ML, "hist_base_s%d.json" % s)
        if not os.path.exists(p):
            break
        try:
            h = json.load(open(p, encoding="utf-8"))
        except Exception:
            break
        cks = [(int(r.get("episode", i)) + 1, float(r["CK"]))
               for i, r in enumerate(h) if "CK" in r]
        if cks:
            per_seed.append(cks)
    if per_seed:
        return per_seed
    # only if there are no per-run histories at all: the first run's
    p = os.path.join(ML, "hist_base.json")
    if not os.path.exists(p):
        return []
    h = json.load(open(p, encoding="utf-8"))
    cks = [(int(r.get("episode", i)) + 1, float(r["CK"]))
           for i, r in enumerate(h) if "CK" in r]
    return [cks] if cks else []


def reference():
    """The reactive heuristic's coverage, for the reference line."""
    import csv
    p = os.path.join(ML, "results_main.csv")
    if not os.path.exists(p):
        return None
    with open(p, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r.get("model") == "Reactive":
                return float(r["CK"])
    return None


def main():
    runs = histories()
    if not runs:
        print("no training history yet; the figure was not written")
        return 1
    ref = reference()
    n_ep = max(x for run in runs for x, _ in run)
    lines = [
        r"\begin{tikzpicture}",
        r"\begin{axis}[width=\columnwidth,height=5.0cm,",
        r"  xlabel={training episode}, ylabel={persistent coverage},",
        r"  xmin=1, xmax=" + str(n_ep) + r", ymin=0.2, ymax=1.02,",
        r"  xtick={1,5,10,15,20,25}, ytick={0.4,0.6,0.8,1.0},",
        r"  grid=both, grid style={gray!20}, tick label style={font=\tiny},",
        r"  label style={font=\small}, legend style={font=\tiny},",
        r"  legend cell align=left, legend columns=1]",
    ]
    if ref is not None:
        # the reference line KEEPS its legend entry; the training runs do
        # not, so the legend lists the reference and then one line per run
        lines.append(r"  \addplot[black, dashed, thick]"
                     r" coordinates {(1," + f"{ref:.3f}" + ") ("
                     + str(n_ep) + "," + f"{ref:.3f}" + ")};")
    for i, run in enumerate(runs):
        cols = ["blue!60!black", "red!60!black", "green!50!black",
                "orange!80!black", "violet!70!black", "cyan!50!black"]
        c = cols[i % len(cols)]
        style = r"  \addplot[color=%s, thick, mark=none, forget plot] coordinates {" % c
        style += " ".join("(%d,%.3f)" % (x, y) for x, y in run) + "};"
        lines.append(style)
    # a legend built by hand, so the reference line is named
    lines.append(r"  \legend{reactive heuristic (reference)," +
                 ", ".join("training run %d" % (i + 1) for i in range(len(runs)))
                 + "}")
    lines.append(r"\end{axis}")
    lines.append(r"\end{tikzpicture}")
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Wrote {OUT} ({len(runs)} training runs)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
