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
import math
import os
import re
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
    """The STRONGEST rule's coverage, for the reference line.

    The figure's reference has to be the rule the paper's GAP is measured
    against -- the stronger of the two rules -- because that is the number
    a reader compares the curve with.  The privileged heuristic is weaker
    (it is given the exact set of under-covered sensors, but it may only
    act locally), and a curve drawn against it would understate the
    shortfall the paper is about.
    """
    import csv
    p = os.path.join(ML, "results_main.csv")
    if not os.path.exists(p):
        return None, "the strongest rule"
    best, name = None, "the strongest rule"
    with open(p, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            m = r.get("model")
            if m not in ("Reactive", "Reactive-local"):
                continue
            try:
                v = float(r["CK"])
            except (TypeError, ValueError, KeyError):
                continue
            if best is None or v > best:
                best = v
                name = ("the unprivileged reactive rule"
                        if m == "Reactive-local" else
                        "the privileged reactive heuristic")
    return best, name


def theme_bootstrap():
    """The guard that loads analysis/theme.tex exactly once.

    It is imported from draft_figures so that the learning curve and the
    three explanatory figures cannot disagree about the theme, or about
    the fallback path it is found at.
    """
    try:
        from draft_figures import THEME_BOOTSTRAP
        return THEME_BOOTSTRAP
    except Exception:                                        # pragma: no cover
        return ""


def nice_ticks(lo, hi, step=0.1):
    """Round tick values inside [lo, hi], with no signed zero."""
    out = []
    k = math.ceil(lo / step - 1e-9)
    while k * step <= hi + 1e-9:
        v = round(k * step, 10)
        if abs(v) < step / 1000.0:
            v = 0.0
        out.append(v)
        k += 1
    return out


def words(n):
    """A small count as a word, so the legend reads as prose."""
    small = ["zero", "one", "two", "three", "four", "five", "six", "seven",
             "eight", "nine", "ten", "eleven", "twelve"]
    return small[n] if 0 <= n < len(small) else str(n)


def short_ref(name):
    """The reference's name, short enough for a one-line legend strip.

    The legend sits in a strip above a full-column axis, so its two
    entries have to share one line; "the unprivileged reactive rule" does
    not (the strip alone was wider than the 3.5in column).  The adjective
    that the figure turns on -- privileged or not -- is kept, and the
    caption says what the rule does.
    """
    return re.sub(r"\breactive\s+", "", name).strip()


def main():
    runs = histories()
    if not runs:
        print("no training history yet; the figure was not written")
        return 1
    ref, ref_name = reference()
    n_ep = max(x for run in runs for x, _ in run)

    # the axis takes the range the data needs, not a fixed 0.2--1.0: the
    # curves sit around 0.6-0.8 and the reference at 0.97, so a 0.2 floor
    # wasted a third of the canvas
    vals = [y for run in runs for _, y in run]
    lo = min(vals + ([ref] if ref is not None else []))
    hi = max(vals + ([ref] if ref is not None else []))
    ymin = math.floor((lo - 0.03) * 10) / 10.0
    ymax = min(1.0, math.ceil((hi + 0.02) * 10) / 10.0)

    def build(wfrac):
        """The fragment, with the axis at `wfrac' of the column width."""
        width = (r"width=\columnwidth" if wfrac >= 0.999
                 else f"width={wfrac:.2f}\\columnwidth")
        lines = [
            theme_bootstrap(),
            r"\begin{tikzpicture}",
            r"\begin{axis}[" + width + r", height=4.6cm,",
            r"  xmin=1, xmax=" + str(n_ep) + r", ymin=" + f"{ymin:.2f}"
            + r", ymax=" + f"{ymax:.2f},",
            r"  xtick={1,5,10,15,20,25}, ymajorgrids,",
            r"  ytick={" + ",".join(f"{t:g}" for t in
                                   [v for v in nice_ticks(ymin, ymax, 0.2)
                                    if v <= ymax - 0.02])
            + r"},",
            r"  xlabel={training episode}, ylabel={persistent coverage},",
            r"  uavaxis, uavlegend, legend columns=2,",
            r"]",
        ]
        if ref is not None:
            # the reference line is a LEVEL, not a series: it is the
            # theme's reference grey, dashed, and it is kept out of the
            # legend's plot list so that the strip can be ordered by hand
            lines.append(r"  \addplot[draw=uavref, line width=1.3pt,"
                         r" dash pattern=on 4pt off 2pt, forget plot]"
                         r" coordinates {(1," + f"{ref:.3f}" + ") ("
                         + str(n_ep) + "," + f"{ref:.3f}" + ")};")
        # the runs are one family, so they are one hue at N weights: the
        # colour says "these are the training runs", the weight says
        # which.  They are all `forget plot'; the strip names the family
        # once, which is what the figure had before (a legend of eight
        # identical run numbers told the reader nothing).
        shades = ["uavblue!25", "uavblue!40", "uavblue!55", "uavblue!70",
                  "uavblue!85", "uavblue"]
        for i, run in enumerate(runs):
            c = shades[i % len(shades)]
            style = (r"  \addplot[color=%s, line width=0.9pt, mark=none,"
                     r" forget plot] coordinates {" % c)
            style += " ".join("(%d,%.3f)" % (x, y) for x, y in run) + "};"
            lines.append(style)
        # the strip: the family, then the reference
        lines.append(r"  \addlegendimage{color=uavblue!55, line width=0.9pt}")
        if ref is not None:
            lines.append(r"  \addlegendimage{draw=uavref, line width=1.3pt,"
                         r" dash pattern=on 4pt off 2pt}")
            lines.append(r"  \legend{{the " + words(len(runs))
                         + r" training runs},{" + short_ref(ref_name)
                         + r"}}")
        else:
            lines.append(r"  \legend{{the " + words(len(runs))
                         + r" training runs}}")
        lines.append(r"\end{axis}")
        lines.append(r"\end{tikzpicture}")
        return "\n".join(lines) + "\n"

    # the theme's `scale only axis' makes the measured width exactly
    # linear in the axis width, so the fit below lands on the column in
    # two or three compiles
    from draft_figures import fit_and_render
    fit_and_render("fig_learning_curve", lambda f: (build(f), None))
    print(f"Wrote {OUT} ({len(runs)} training runs)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
