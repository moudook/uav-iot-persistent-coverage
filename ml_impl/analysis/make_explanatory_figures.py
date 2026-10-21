"""The explanatory figures.

The paper's central claim is an INFERENCE, and an inference that is only
visible in a table is a claim a reader has to rebuild in their head.  Two
figures make it visible:

  * fig:arms -- every arm's paired interval against the gap it would have
    to explain.  An arm whose interval reaches past the gap is not
    excluded, and the figure shows which arms those are.
  * fig:scen -- the difference between the learned controller and the
    stronger rule, for every one of the scenario variants.  The ordering
    is the claim; the figure shows that it holds everywhere.

The numbers come from the token table, so the figures cannot disagree
with the prose: they are drawn from the same artefacts the sentences are
built from.
"""

from __future__ import annotations

import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ML = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, ML)

from fill_tokens import build_tokens          # noqa: E402

ARM_LABELS = [
    ("OBS_B", "adding the agent identity"),
    ("OBS_C", "the full observation"),
    ("EB", "removing the energy constraint"),
    ("EC", "without the threshold term"),
    ("ED", "the previous energy rule"),
]


def ci(tok, key):
    """The (mean, lower, upper) of a token's interval, or None."""
    mean = tok.get(f"{key}_PAIRED")
    half = tok.get(f"{key}_HALF")
    if mean in (None, "") or half in (None, ""):
        return None
    try:
        m = float(mean)
        h = float(half)
    except ValueError:
        return None
    return m, m - h, m + h


def figure_arms(tok):
    """The arms' intervals against the gap."""
    gap = tok.get("GAP")
    if gap in (None, ""):
        print("  the gap is not measured yet; the arms figure was not drawn")
        return None
    gap = float(gap)
    rows = []
    for key, label in ARM_LABELS:
        v = ci(tok, key)
        if v:
            rows.append((label, v))
    if not rows:
        print("  no arm has an interval yet; the arms figure was not drawn")
        return None

    lines = [
        r"\begin{tikzpicture}",
        r"\begin{axis}[width=\columnwidth,height=4.4cm,",
        r"  xlabel={difference in persistent coverage},",
        r"  ytick={1," + ",".join(str(i) for i in range(2, len(rows) + 1)) + "},",
        r"  yticklabels={" + ",".join("{" + r[0] + "}" for r in rows) + "},",
        r"  xmin=-0.7, xmax=0.75, ymin=0.4, ymax=" +
        f"{len(rows) + 0.6:.1f},",
        r"  grid=both, grid style={gray!20}, tick label style={font=\tiny},",
        r"  label style={font=\small}, legend style={font=\tiny},",
        r"  legend cell align=left, legend columns=1, y dir=reverse]",
    ]
    # the gap: the quantity every arm would have to account for
    lines.append(r"  \addplot[red!70!black, dashed, thick] coordinates "
                 f"({gap:.3f},0.4) ({gap:.3f},{len(rows) + 0.6:.1f});")
    for i, (label, (m, lo, hi)) in enumerate(rows, 1):
        past = hi > gap
        col = "red!70!black" if past else "blue!60!black"
        # the interval, then the point estimate
        lines.append(r"  \addplot[" + col + r", very thick, mark=none] "
                     f"coordinates ({lo:.3f},{i}) ({hi:.3f},{i});")
        lines.append(r"  \addplot[" + col + r", only marks, mark=*, "
                     f"mark size=1.6pt] coordinates ({m:.3f},{i});")
    lines.append(r"  \legend{the gap the arm must explain,"
                 r"95\% interval of the arm,point estimate}")
    lines.append(r"\end{axis}")
    lines.append(r"\end{tikzpicture}")
    return "\n".join(lines)


def figure_scen(tok):
    """The scenario matrix: the difference on every variant."""
    p = os.path.join(ML, "results_scenarios.csv")
    if not os.path.exists(p):
        print("  no scenario matrix; the scenario figure was not drawn")
        return None
    pts = []
    with open(p, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            try:
                rule = float(r["react_CK"])
                if r.get("reactlocal_CK") not in (None, ""):
                    rule = max(rule, float(r["reactlocal_CK"]))
                d = float(r["mappo_CK"]) - rule
            except (TypeError, ValueError, KeyError):
                continue
            pts.append((r.get("scenario", "?"), d))
    if not pts:
        return None
    lo = min(d for _, d in pts)
    hi = max(d for _, d in pts)
    lines = [
        r"\begin{tikzpicture}",
        r"\begin{axis}[width=\columnwidth,height=4.4cm,",
        r"  xlabel={scenario variant}, ylabel={coverage difference},",
        r"  xmin=0.5, xmax=" + f"{len(pts) + 0.5:.1f}," +
        f" ymin={min(lo, 0) - 0.05:.3f}, ymax={max(hi, 0) + 0.05:.3f},",
        r"  grid=both, grid style={gray!20}, tick label style={font=\tiny},",
        r"  label style={font=\small}, legend style={font=\tiny},",
        r"  legend cell align=left, legend columns=1]",
    ]
    lines.append(r"  \addplot[red!70!black, dashed, thick] coordinates "
                 f"(0.5,0) ({len(pts) + 0.5:.1f},0);")
    lines.append(r"  \addplot[only marks, mark=*, mark size=1.4pt, "
                 "color=blue!60!black] coordinates {"
                 + " ".join(f"({i + 1},{d:.3f})"
                            for i, (_, d) in enumerate(pts)) + "};")
    lines.append(r"  \legend{level with the stronger rule,"
                 "the learned controller's difference}")
    lines.append(r"\end{axis}")
    lines.append(r"\end{tikzpicture}")
    return "\n".join(lines)


def main():
    tok = build_tokens()
    for name, fn in (("fig_arms", figure_arms), ("fig_scen", figure_scen)):
        body = fn(tok)
        if body is None:
            continue
        p = os.path.join(HERE, name + ".tex")
        with open(p, "w", encoding="utf-8") as f:
            f.write(body + "\n")
        print(f"Wrote {p}")


if __name__ == "__main__":
    main()
