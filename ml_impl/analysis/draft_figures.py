"""
The three EXPLANATORY figures, drafted from the token table.

Each figure is a self-contained pgfplots fragment (the body of a
tikzpicture) that the author can drop into a `figure' environment, plus a
PNG preview rendered from a standalone document.

  fig_arms   -- the central claim as a picture: every controlled arm's 95%
                 paired interval against the gap it would have to explain.
  fig_budget -- the training-budget sweep against the same gap.
  fig_scen   -- the scenario matrix: the learned controller against the
                 stronger rule on every variant.

Every number is read AT RUN TIME from the token table (analysis/
fill_tokens.py, function build_tokens) or from the artefact the table is
built from, so a figure cannot disagree with the prose: they are drawn
from the same measurement.  Nothing measured is typed into this file.

Run:  python analysis/draft_figures.py            (write fragments + PNGs)
      python analysis/draft_figures.py --no-render (fragments only)
"""

from __future__ import annotations

import math
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ML = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)
if ML not in sys.path:
    sys.path.insert(0, ML)

from fill_tokens import build_tokens, sample_std      # noqa: E402

# the one-column width of the paper (IEEEtran conference), in TeX points
COL_PT = 3.5 * 72.27

# THE VISUAL LANGUAGE lives in analysis/theme.tex: the palette, the axis
# (one spine left and bottom, dashed light gridlines, small dark tick
# labels, a bold axis label), the boxed legend strip across the top, the
# round-capped interval bar, the hatched primary bar, the reference band
# and the panel label.  A figure names a style; it never names a colour or
# a line weight of its own, so the four figures in the paper and the two in
# the report cannot drift apart.
#
# theme.tex is \input by the paper's preamble when the author has added
# the line, and it is bootstrapped by the fragment itself when they have
# not, so the paper compiles either way.
THEME_BOOTSTRAP = (
    "% the shared theme: the paper may also \\input it in its preamble\n"
    "\\ifdefined\\uavtheme\\else\n"
    "  \\IfFileExists{ml_impl/analysis/theme.tex}"
    "{\\input{ml_impl/analysis/theme.tex}}{%\n"
    "  \\IfFileExists{theme.tex}{\\input{theme.tex}}{%\n"
    "  \\errmessage{the figures need ml_impl/analysis/theme.tex}}}\n"
    "\\fi"
)
UAVBLUE, UAVCYAN, UAVGREEN = "uavblue", "uavcyan", "uavgreen"
UAVORANGE, UAVRED, UAVPURPLE = "uavorange", "uavred", "uavpurple"
UAVREF, UAVINK, UAVMUTED = "uavref", "uavink", "uavmuted"
UAVWHITE = "uavwhite"

# the verdict of an arm, as a colour: the primary blue when the interval
# stays below the gap, the accent orange when it does not
BELOW_COLOUR, PAST_COLOUR = UAVBLUE, UAVORANGE


# ----------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------
def num(tok, name):
    """A token's value as a float, or None if it is absent or not a number."""
    v = tok.get(name)
    if v in (None, ""):
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def req(tok, name):
    """A token's value as a float, or a clear failure."""
    v = num(tok, name)
    if v is None:
        raise SystemExit(f"the token {name} is missing or not a number "
                         f"(value: {tok.get(name)!r}); the figure was not "
                         f"drawn")
    return v


def sgn(x, nd=3):
    """A signed number, as the paper prints it."""
    return f"{x:+.{nd}f}"


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


def axis(opts, body):
    """An axis environment: the options, closed, and then the body."""
    return ("\\begin{axis}[" + "\n".join(opts) + "]\n" + body
            + "\\end{axis}")


def fragment(opts, body):
    """A self-contained themed fragment: the theme, then the picture."""
    return (THEME_BOOTSTRAP + "\n\\begin{tikzpicture}\n"
            + axis(opts, "\n".join(body) + "\n") + "\n\\end{tikzpicture}")


# ----------------------------------------------------------------------
# FIGURE 1: the arms' intervals against the gap
# ----------------------------------------------------------------------
# (token prefix, the short name on the axis, the long name for the report)
ARMS = [
    ("OBS_B", r"obs.\,B: identity", "adding the agent identity"),
    ("OBS_C", r"obs.\,C: full obs.", "the full observation"),
    ("EB", r"energy\,B: no constraint", "removing the energy constraint"),
    ("EC", r"energy\,C: no threshold", "without the threshold term"),
    ("ED", r"energy\,D: prev.\ rule", "the previous energy rule"),
    ("CREDIT", r"credit: per-agent critic", "the per-agent local critic"),
]
# the group boundary: the two observation arms, then the three energy arms,
# then the credit arm
OBS_COUNT = 2
ENERGY_COUNT = 3


def figure_arms(tok, wfrac=1.0):
    """The central claim as a picture: the arms' intervals vs the gap."""
    gap = req(tok, "GAP")
    arms = []
    for key, short, long_ in ARMS:
        mean = num(tok, f"{key}_PAIRED")
        half = num(tok, f"{key}_HALF")
        if mean is None or half is None:
            print(f"  [arms] {key} has no paired interval in the token "
                  f"table; it is left out of the figure")
            continue
        arms.append(dict(key=key, short=short, long=long_, mean=mean,
                         half=half, lo=mean - half, hi=mean + half,
                         # the paper's rule: an explanation is EXCLUDED only
                         # if the arm that tests it has an upper confidence
                         # limit below the gap
                         excluded=(mean + half) < gap))
    if not arms:
        raise SystemExit("no arm has a paired interval; nothing was drawn")

    n = len(arms)
    lo_all = min(a["lo"] for a in arms)
    hi_all = max(a["hi"] for a in arms)
    xmin = math.floor((lo_all - 0.03) * 10) / 10.0
    xmax = max(math.ceil((hi_all + 0.04) * 10) / 10.0, round(gap + 0.11, 3))
    ymin, ymax = 0.35, n + 0.65

    opts = [
        (r"  width=\columnwidth" if wfrac >= 0.999
         else f"  width={wfrac:.2f}\\columnwidth") + ",height=4.9cm,",
        f"  xmin={xmin:.3f}, xmax={xmax:.3f}, ymin={ymin:.2f}, "
        f"ymax={ymax:.2f},",
        "  xtick={" + ",".join(f"{t:g}" for t in nice_ticks(xmin, xmax, 0.2))
        + "}, xmajorgrids,",
        "  ytick={" + ",".join(str(n - i) for i in range(n)) + "},",
        "  yticklabels={"
        + ",".join("{" + a["short"] + "}" for a in arms) + "},",
        r"  xlabel={difference in persistent coverage},",
        r"  uavaxis,",
        # the strip is dense (five entries): at the theme's \scriptsize it
        # would be wider than the column, so this figure drops it to \tiny,
        # as the paper's own figures did before
        r"  uavlegend, legend columns=3, legend style={font=\tiny},",
    ]
    body = []
    # the gap's own 95% interval, as a band: every arm's upper limit lies
    # below the band as well as below the point estimate
    half = num(tok, "GAP_HALF")
    if half is not None:
        body.append(f"  \\addplot[uavband] coordinates "
                    f"{{({gap - half:.3f},{ymin:.2f}) ({gap + half:.3f},{ymin:.2f})"
                    f" ({gap + half:.3f},{ymax:.2f}) ({gap - half:.3f},{ymax:.2f})"
                    f"}} \\closedcycle;")
    # the gap: the quantity every arm would have to account for, drawn as
    # the level line of the figure.  It is kept out of the legend's image
    # list, because the legend draws its own image for it.
    body.append(f"  \\addplot[uavlevel, forget plot] coordinates "
                f"{{({gap:.3f},{ymin:.2f}) ({gap:.3f},{ymax:.2f})}};")
    for i, a in enumerate(arms):
        y = n - i
        col = BELOW_COLOUR if a["excluded"] else PAST_COLOUR
        # the horizontal interval, in the pgfplots idiom for an interval
        # plot: the point is the paired mean and the error value is the
        # half-width of the 95% interval, so the bar, its round caps and
        # the marker all come from ONE plot command.  The bar style is the
        # theme's (thick, round caps, no end marks, a filled marker).
        # `forget plot' keeps these out of the legend, which is drawn from
        # the \addlegendimage list below: an unlabelled plot would take the
        # first legend entry and shift every label by one.
        body.append(f"  \\addplot[uavintervalx, color={col}, forget plot, "
                    f"mark options={{fill={col},draw=white,line width=0.5pt}}]"
                    f" coordinates "
                    f"{{({a['mean']:.3f},{y}) +- ({a['half']:.3f},0)}};")
    # the separators between the groups of arms
    for boundary, after in ((OBS_COUNT, "the observation arms"),
                            (OBS_COUNT + ENERGY_COUNT, "the energy arms")):
        if boundary < n:
            ysep = n - boundary + 0.5
            body.append(f"  \\draw[uavsep] "
                        f"(axis cs:{xmin:.3f},{ysep:.2f}) -- "
                        f"(axis cs:{xmax:.3f},{ysep:.2f});")
    # the legend: the things the picture draws, as a strip across the top
    body.append(r"  \addlegendimage{color=" + BELOW_COLOUR
                + r", line width=2.6pt, line cap=round}")
    body.append(r"  \addlegendimage{color=" + PAST_COLOUR
                + r", line width=2.6pt, line cap=round}")
    body.append(r"  \addlegendimage{only marks, mark=*, mark size=2.4pt, "
                r"color=" + UAVBLUE + r", mark options={fill=" + UAVBLUE
                + r",draw=white,line width=0.5pt}}")
    body.append(r"  \addlegendimage{draw=" + UAVINK
                + r", line width=0.9pt}")
    if half is not None:
        body.append(r"  \addlegendimage{area legend, fill=uavband, "
                    r"draw=uavband}")
    body.append(r"  \legend{{below the gap},{past the gap},"
                r"{paired mean},"
                + (r"{the gap " + f"{gap:.3f}" + r"},{gap 95\% CI}"
                   if half is not None else r"{the gap " + f"{gap:.3f}" + r"}")
                + "}")
    # the point estimate of each arm, above its bar
    for i, a in enumerate(arms):
        y = n - i
        body.append(f"  \\node[anchor=south, font=\\scriptsize, "
                    f"text={UAVINK}] at "
                    f"(axis cs:{a['mean']:.3f},{y + 0.19:.2f}) "
                    f"{{${sgn(a['mean'])}$}};")
    # the value of the gap is carried by the legend strip, not by a label
    # inside the plot: the band is too narrow for type that could be read,
    # and a label at the top of the band would sit on the first row
    frag = fragment(opts, body)
    for a in arms:
        a["verdict"] = "excluded" if a["excluded"] else "not excluded"
        a["margin"] = gap - a["hi"]
    return frag, arms


# ----------------------------------------------------------------------
# FIGURE 2: the training-budget sweep
# ----------------------------------------------------------------------
def budget_rows():
    """The training-budget sweep, from the artefact the table reads."""
    import json
    p = os.path.join(HERE, "ab_budget.json")
    if not os.path.exists(p):
        raise SystemExit("ab_budget.json is missing; the budget figure was "
                         "not drawn")
    rows = json.load(open(p, encoding="utf-8"))
    rows = sorted(rows, key=lambda r: int(r["episodes"]))
    out = []
    for r in rows:
        per = [float(x) for x in (r.get("per_seed_CK") or [])]
        if not per:
            raise SystemExit(f"the budget row for {r['episodes']} episodes "
                             f"has no per-seed values; the figure was not "
                             f"drawn")
        out.append(dict(
            episodes=int(r["episodes"]),
            mean=float(r["CK"]),
            # the SAMPLE standard deviation: the paper's convention is that
            # every spread comes from sample_std (the artefact's CK_std
            # field is a POPULATION standard deviation, which is what the
            # paper's own audit complains about)
            sd=sample_std(per),
            n=len(per)))
    return out


def figure_budget(tok, wfrac=1.0):
    """The training-budget sweep, with the seed spread and the paired gain."""
    gap = req(tok, "GAP")
    rule = req(tok, "BEST_RULE_CK")
    rule_name = tok.get("BEST_RULE_NAME", "the strongest rule")
    paired = req(tok, "BUDGET_PAIRED")
    ci = tok.get("BUDGET_PAIRED_CI", "")
    frac = tok.get("BUDGET_FRAC", "")
    rows = budget_rows()
    eps = [r["episodes"] for r in rows]
    cks = [r["mean"] for r in rows]
    sds = [r["sd"] for r in rows]
    nseed = rows[0]["n"]

    xmin, xmax = min(eps) - 3.0, max(eps) + 4.5
    ymin = min(c - s for c, s in zip(cks, sds)) - 0.07
    # the top of the axis is the band the rule's name is written in, so
    # that the label never sits on the 1.0 gridline
    ymax = rule + 0.062
    arrow_x = max(eps) + 1.4
    lab_x = arrow_x + 1.7
    yticks = [y for y in nice_ticks(ymin, ymax) if y <= rule - 0.025]

    opts = [
        (r"  width=\columnwidth" if wfrac >= 0.999
         else f"  width={wfrac:.2f}\\columnwidth") + ",height=4.9cm,",
        f"  xmin={xmin:.2f}, xmax={xmax:.2f}, ymin={ymin:.3f}, "
        f"ymax={ymax:.3f},",
        "  xtick={" + ",".join(str(e) for e in eps) + "}, ymajorgrids,",
        "  ytick={" + ",".join(f"{y:g}" for y in yticks)
         + "},",
        r"  xlabel={training episodes}, ylabel={persistent coverage},",
        r"  uavaxis,",
        r"  uavlegend, legend columns=2,",
    ]
    body = []
    # the rule the gap is measured against: the reference level, in the
    # reference grey, so the one series the figure is about stays blue
    body.append(f"  \\addplot[draw={UAVREF}, line width=1.3pt] coordinates "
                f"{{({xmin:.2f},{rule:.3f}) ({xmax:.2f},{rule:.3f})}};")
    # the sweep, with the seed-to-seed spread
    coords = " ".join(
        f"({e},{c:.3f}) +- (0,{s:.4f})" for e, c, s in zip(eps, cks, sds))
    body.append(r"  \addplot[color=" + UAVBLUE + r", line width=1.1pt, mark=*,"
                r" mark size=2.3pt, mark options={fill=" + UAVBLUE
                + r", draw=white, line width=0.5pt},"
                r" error bars/y dir=both, error bars/y explicit,"
                r" error bars/error bar style={line width=0.8pt, color="
                + UAVBLUE + r"},"
                r" error bars/error mark=|,"
                r" error bars/error mark options={rotate=90, mark size=2.4pt,"
                r" line width=0.8pt, color=" + UAVBLUE + r"}]"
                r" coordinates {" + coords + "};")
    body.append(r"  \legend{{the strongest rule},{the learned controller}}")
    # the gap that is left at the longest budget
    body.append(f"  \\draw[{UAVINK}, line width=0.8pt, <->] "
                f"(axis cs:{arrow_x:.2f},{cks[-1]:.3f}) -- "
                f"(axis cs:{arrow_x:.2f},{rule:.3f});")
    body.append(f"  \\node[rotate=90, anchor=south, font=\\scriptsize"
                f"\\bfseries, text={UAVINK}] at "
                f"(axis cs:{lab_x:.2f},{cks[-1]:.3f}) "
                f"{{gap {gap:.3f}}};")
    # the rule's name, above its line, in the band reserved for it
    body.append(f"  \\node[anchor=south west, font=\\scriptsize, "
                f"text={UAVMUTED}] at "
                f"(axis cs:{xmin + 0.4:.2f},{rule + 0.012:.3f}) "
                f"{{{rule_name} ({rule:.3f})}};")
    # the paired gain over the range the sweep covers
    txt = (f"training over {eps[0]}--{eps[-1]} episodes: "
           f"$\\Delta={sgn(paired)}$")
    if ci:
        txt += f"\\\\95\\% CI {ci}"
    if frac:
        txt += f" --- {frac}\\% of the gap"
    txt += f"\\\\bars: $\\pm 1$ s.d. over the {nseed} training seeds"
    # the annotation sits BELOW the reference line, so that the rule's
    # line does not run through the text
    body.append(f"  \\node[anchor=north west, font=\\scriptsize, align=left, "
                f"text={UAVINK}, fill={UAVWHITE}, inner sep=2pt, "
                f"draw=none] at "
                f"(axis cs:{xmin + 0.4:.2f},{rule - 0.030:.3f}) {{{txt}}};")
    frag = fragment(opts, body)
    return frag, dict(rows=rows, gap=gap, rule=rule, rule_name=rule_name,
                       paired=paired, ci=ci, frac=frac, nseed=nseed)


# ----------------------------------------------------------------------
# FIGURE 3: the scenario matrix
# ----------------------------------------------------------------------
def scenario_points():
    """The learned controller's deficit against the stronger rule, per variant."""
    import csv
    p = os.path.join(ML, "results_scenarios.csv")
    if not os.path.exists(p):
        raise SystemExit("results_scenarios.csv is missing; the scenario "
                         "figure was not drawn")
    pts, groups = [], []
    with open(p, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            try:
                rule = float(r["react_CK"])
                if r.get("reactlocal_CK") not in (None, ""):
                    rule = max(rule, float(r["reactlocal_CK"]))
                d = float(r["mappo_CK"]) - rule
            except (TypeError, ValueError, KeyError):
                continue
            s = r.get("scenario", "?")
            if not groups or groups[-1][0] != s:
                groups.append([s, len(pts), len(pts)])
            groups[-1][2] = len(pts) + 1
            pts.append(dict(idx=len(pts) + 1, scen=s,
                             var=r.get("variant", "?"), d=d,
                             question=r.get("question", "")))
    return pts, groups


def figure_scen(tok, wfrac=1.0):
    """The scenario matrix: the deficit on every single variant."""
    pts, groups = scenario_points()
    if not pts:
        raise SystemExit("the scenario matrix is empty; nothing was drawn")
    wins = int(tok.get("SCEN_WINS", "0"))
    losses = int(tok.get("SCEN_LOSSES", str(len(pts))))
    ties = int(tok.get("SCEN_TIES", "0"))
    n = len(pts)
    ds = [p["d"] for p in pts]
    ymin = min(min(ds) - 0.03, -0.05)
    ymax = 0.075
    xmin, xmax = 0.3, n + 0.7

    opts = [
        (r"  width=\columnwidth" if wfrac >= 0.999
         else f"  width={wfrac:.2f}\\columnwidth") + ",height=4.6cm,",
        f"  xmin={xmin:.2f}, xmax={xmax:.2f}, ymin={ymin:.3f}, "
        f"ymax={ymax:.3f},",
        "  xtick={" + ",".join(f"{0.5 * (g[1] + g[2]):g}" for g in groups)
         + "},",
        "  xticklabels={" + ",".join(g[0] for g in groups) + "},",
        "  ytick={" + ",".join(f"{y:g}" for y in nice_ticks(ymin, ymax))
         + "}, ymajorgrids,",
        r"  xlabel={scenario (each marker is one variant)},"
        r" ylabel={persistent coverage difference},",
        r"  uavaxis,",
    ]
    body = []
    # the separators between the scenarios
    for g in groups[:-1]:
        x = g[2] + 0.5
        body.append(f"  \\draw[uavsep] "
                    f"(axis cs:{x:.2f},{ymin:.3f}) -- "
                    f"(axis cs:{x:.2f},{ymax:.3f});")
    # the level line: level with the stronger rule
    body.append(f"  \\addplot[uavlevel, forget plot] coordinates "
                f"{{({xmin:.2f},0) ({xmax:.2f},0)}};")
    # the variants
    body.append(r"  \addplot[only marks, mark=*, mark size=2.3pt, color="
                + UAVBLUE + ", mark options={fill=" + UAVBLUE
                + ", draw=white, line width=0.5pt}] coordinates {"
                + " ".join(f"({p['idx']},{p['d']:.3f})" for p in pts) + "};")
    # the two labels that carry the point of the figure: both sit in the
    # narrow band ABOVE the level line, which no marker can reach, and
    # they are short enough not to meet in the middle
    body.append(f"  \\node[anchor=south east, font=\\scriptsize, "
                f"text={UAVMUTED}] at "
                f"(axis cs:{xmax - 0.3:.2f},0.018) "
                f"{{level with the rule}};")
    body.append(f"  \\node[anchor=south west, font=\\scriptsize\\bfseries, "
                f"text={UAVINK}] at "
                f"(axis cs:{xmin + 0.3:.2f},0.018) "
                f"{{{losses} of {n} variants behind}};")
    frag = fragment(opts, body)
    return frag, dict(pts=pts, groups=groups, wins=wins, losses=losses,
                       ties=ties, n=n)


# ----------------------------------------------------------------------
# the standalone renderers
# ----------------------------------------------------------------------
PREAMBLE = r"""\documentclass[10pt]{article}
\usepackage[paperwidth=4.3in,paperheight=5.2in,margin=0.4in]{geometry}
\usepackage{amsmath}
\usepackage{tikz}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
%% the project's palette and styles: the SAME file the paper and the
%% report input, so a preview cannot look different from the paper
\input{theme}
\pagestyle{empty}
\setlength{\parindent}{0pt}
\begin{document}
\newsavebox{\figbox}
\sbox{\figbox}{\input{%s}}
\typeout{FIGWIDTH=\the\wd\figbox}
\noindent\usebox{\figbox}
\end{document}
"""


def crop_png(png, pdf, dpi=150, margin=8):
    """Crop the rendered page to the figure, so the preview shows the
    figure and not the page."""
    try:
        import numpy as np
        import pymupdf
    except Exception:                                        # pragma: no cover
        return
    doc = pymupdf.open(pdf)
    page = doc[0]
    pix = page.get_pixmap(dpi=dpi)
    img = np.frombuffer(pix.samples, dtype=np.uint8)
    img = img.reshape(pix.height, pix.width, pix.n)[:, :, :3]
    nonwhite = (img < 245).any(axis=2)
    rows = np.where(nonwhite.any(axis=1))[0]
    cols = np.where(nonwhite.any(axis=0))[0]
    if not len(rows) or not len(cols):
        return
    sc = 72.0 / dpi
    rect = pymupdf.Rect(max(0, cols[0] - margin) * sc,
                        max(0, rows[0] - margin) * sc,
                        min(pix.width, cols[-1] + margin) * sc,
                        min(pix.height, rows[-1] + margin) * sc)
    page.get_pixmap(dpi=dpi, clip=rect).save(png)


def compile_tex(doc, timeout=180):
    """Run pdflatex on `doc`; return (ok, log)."""
    base = os.path.basename(doc).replace(".tex", "")
    for stale in (base + ".pdf", base + ".log", base + ".aux"):
        p = os.path.join(HERE, stale)
        if os.path.exists(p):
            os.remove(p)
    try:
        subprocess.run(["pdflatex", "-interaction=nonstopmode", "-file-line-error",
                        base + ".tex"], cwd=HERE, capture_output=True,
                       text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return False, "pdflatex timed out"
    logp = os.path.join(HERE, base + ".log")
    log = open(logp, encoding="utf-8", errors="replace").read() \
        if os.path.exists(logp) else ""
    ok = "Output written on" in log
    return ok, log


def natural_width(log):
    m = re.search(r"FIGWIDTH=([0-9.]+)pt", log)
    return float(m.group(1)) if m else None


def render(name, body, do_render=True):
    """Write the fragment, render it, and report the natural width."""
    frag = os.path.join(HERE, name + ".tex")
    with open(frag, "w", encoding="utf-8") as f:
        f.write(body + "\n")
    if not do_render:
        return None
    doc = os.path.join(HERE, "render_" + name + ".tex")
    with open(doc, "w", encoding="utf-8") as f:
        f.write(PREAMBLE % (name + ".tex"))
    ok, log = compile_tex(doc)
    if not ok:
        print(f"  [render] {name} did not compile:")
        print("\n".join(log.splitlines()[-20:]))
        return None
    w = natural_width(log)
    over = re.findall(r"Overfull \\hbox \(([0-9.]+)pt", log)
    pages = re.search(r"Output written on .*\((\d+) pages?", log)
    if pages and int(pages.group(1)) > 1:
        print(f"  [render] {name}: the preview ran to "
              f"{pages.group(1)} pages")
    if w is not None:
        print(f"  [render] {name}: natural width {w:.1f}pt "
              f"({w / 72.27:.2f}in) against a 3.50in column"
              + ("  <-- TOO WIDE" if w > COL_PT + 1.0 else ""))
    if over:
        print(f"  [render] {name}: overfull hboxes {over}")
    pdf = doc.replace(".tex", ".pdf")
    png = os.path.join(HERE, name + ".png")
    if os.path.exists(png):
        os.remove(png)
    subprocess.run(["pdftoppm", "-png", "-r", "150", "-singlefile",
                    os.path.basename(pdf), os.path.basename(name)],
                   cwd=HERE, capture_output=True, text=True)
    if os.path.exists(png):
        crop_png(png, pdf)
        print(f"Wrote {png}")
    else:
        print(f"  [render] {name}: the PNG was not produced")
    return w


def fit_and_render(name, builder, do_render=True):
    """Render, and fit the axis to the column.

    The axis width is fitted, not guessed: the fragment is boxed, its
    natural width is measured (the measurement is the width the figure
    will have in the column), and the part of that width which does not
    scale with the axis (the tick labels and the legend strip) is
    removed.  The axis is then given the width that makes the whole
    picture sit just inside the 3.5in column, so a figure fills the
    column and is never overfull by even a point.
    """
    target = COL_PT - 2.0
    wfrac = 1.0
    info = None
    for _ in range(6):
        body, info = builder(wfrac)
        w = render(name, body, do_render)
        if w is None:
            return info
        if w <= target and w >= target - 4.0:
            return info
        # the width that does not scale with the axis: the theme's
        # `scale only axis' makes the relation exactly linear
        fixed = max(0.0, w - COL_PT * wfrac)
        if fixed >= target - 6.0:
            # what is left is the legend strip or the tick labels: they
            # already fill the column, and narrowing the axis further
            # would only shrink the plot
            if w <= COL_PT:
                return info
        want = min(1.0, max(0.30, (target - 1.0 - fixed) / COL_PT))
        want = math.floor(want * 100) / 100.0
        if abs(want - wfrac) < 0.005:
            return info
        print(f"  [render] {name}: {w:.1f}pt against a {COL_PT:.1f}pt "
              f"column; retrying at width={want:.2f}\\columnwidth")
        wfrac = want
    return info


def main():
    do_render = "--no-render" not in sys.argv
    tok = build_tokens()

    arms = fit_and_render("fig_arms", lambda f: figure_arms(tok, f),
                           do_render)
    print("  [arms] gap {:.3f}".format(req(tok, "GAP")))
    for a in arms:
        print("    {:6s} {:>7s}  95% CI [{:+.3f}, {:+.3f}]  {}"
              .format(a["key"], sgn(a["mean"]), a["lo"], a["hi"],
                      a["verdict"]))

    bud = fit_and_render("fig_budget", lambda f: figure_budget(tok, f),
                          do_render)
    print("  [budget] sweep " + tok.get("BUDGET_SWEEP", "?"))
    print("    paired {:+}  CI {}  ({}% of the gap {:.3f})".format(
        bud["paired"], bud["ci"], bud["frac"], bud["gap"]))

    scen = fit_and_render("fig_scen", lambda f: figure_scen(tok, f),
                           do_render)
    print("  [scen] {} variants: {} ahead, {} behind, {} level".format(
        scen["n"], scen["wins"], scen["losses"], scen["ties"]))

    # the renderer's intermediate files are noise: the standalone .tex, the
    # PDF and the PNG are what is worth keeping
    for name in ("fig_arms", "fig_budget", "fig_scen"):
        for ext in (".aux", ".log", ".out"):
            p = os.path.join(HERE, "render_" + name + ext)
            if os.path.exists(p):
                os.remove(p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
