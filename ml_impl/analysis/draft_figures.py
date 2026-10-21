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

import csv
import json
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

# ----------------------------------------------------------------------
# the house style: the same pgfplots options the existing learning-curve
# figure uses, with the paper's own colour names
# ----------------------------------------------------------------------
COMMON = (
    r"  grid=both, grid style={gray!20}, tick label style={font=\tiny},"
    "\n"
    r"  label style={font=\small}, legend style={font=\tiny},"
    "\n"
    r"  legend cell align=left, clip=false,"
)
# the six colours the paper's preamble defines
UAVBLUE, UAVCYAN, UAVGREEN = "uavblue", "uavcyan", "uavgreen"
UAVORANGE, UAVRED, UAVPURPLE = "uavorange", "uavred", "uavpurple"


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


def floor_to(v, step):
    return int(v / step) * step


def ceil_to(v, step):
    import math
    return int(math.ceil(v / step)) * step


# ----------------------------------------------------------------------
# FIGURE 1: the arms' intervals against the gap
# ----------------------------------------------------------------------
# (token prefix, the short name on the axis, the long name for the report)
ARMS = [
    ("OBS_B", r"obs.\,B: identity", "adding the agent identity"),
    ("OBS_C", r"obs.\,C: full obs.", "the full observation"),
    ("EB", r"energy\,B: no constraint", "removing the energy constraint"),
    ("EC", r"energy\,C: no threshold", "removing the threshold term"),
    ("ED", r"energy\,D: prev.\ rule", "the previous energy rule"),
]


def figure_arms(tok):
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
    xmin = floor_to(lo_all - 0.03, 0.1)
    xmax = max(ceil_to(hi_all + 0.04, 0.1), round(gap + 0.11, 3))
    xt = [round(xmin + 0.1 * k, 3) for k in
          range(int(round((xmax - xmin) / 0.1)) + 1)]
    ymin, ymax = 0.35, n + 0.65

    L = []
    L.append(r"\begin{tikzpicture}")
    L.append(r"\begin{axis}[width=\columnwidth,height=5.7cm,")
    L.append(f"  xmin={xmin:.3f}, xmax={xmax:.3f}, "
             f"ymin={ymin:.2f}, ymax={ymax:.2f},")
    L.append("  xtick={" + ",".join(f"{t:g}" for t in xt) + "},")
    L.append("  ytick={" + ",".join(str(n - i) for i in range(n)) + "},")
    L.append("  yticklabels={"
             + ",".join("{" + a["short"] + "}" for a in arms) + "},")
    L.append(r"  xlabel={difference in persistent coverage "
             r"(arm $-$ its reference arm)},")
    L.append(COMMON)
    L.append(r"  legend style={font=\tiny, at={(0.5,-0.36)}, anchor=north, "
             r"legend columns=2}],")
    # the gap: the quantity every arm would have to account for
    L.append(f"  \\addplot[black, dashed, line width=1.1pt] coordinates "
             f"({gap:.3f},{ymin:.2f}) ({gap:.3f},{ymax:.2f});")
    for i, a in enumerate(arms):
        y = n - i
        col = UAVGREEN if a["excluded"] else UAVRED
        L.append(f"  \\addplot[color={col}, line width=2.4pt, mark=none, "
                 f"forget plot] coordinates "
                 f"({a['lo']:.3f},{y}) ({a['hi']:.3f},{y});")
        L.append(f"  \\addplot[only marks, mark=|, mark size=3.2pt, "
                 f"color={col}, forget plot] coordinates "
                 f"({a['lo']:.3f},{y}) ({a['hi']:.3f},{y});")
        L.append(f"  \\addplot[only marks, mark=*, mark size=1.7pt, "
                 f"color=black, mark options={{fill=white,draw=black,"
                 f"line width=0.5pt}}, forget plot] coordinates "
                 f"({a['mean']:.3f},{y});")
    # the legend: the three things the picture draws
    L.append(r"  \addlegendimage{color=" + UAVGREEN + r", line width=2.4pt}")
    L.append(r"  \addlegendimage{color=" + UAVRED + r", line width=2.4pt}")
    L.append(r"  \addlegendimage{only marks, mark=*, mark size=1.7pt, "
             r"color=black, mark options={fill=white,draw=black,"
             r"line width=0.5pt}}")
    L.append(r"  \addlegendimage{black, dashed, line width=1.1pt}")
    L.append(r"  \legend{95\% interval, upper limit below the gap,"
             r"95\% interval, upper limit past the gap,"
             r"paired mean,the gap the arm must explain}")
    # the point estimate of each arm, above its bar
    for i, a in enumerate(arms):
        y = n - i
        L.append(f"  \\node[anchor=south, font=\\tiny] at "
                 f"(axis cs:{a['mean']:.3f},{y + 0.17:.2f}) "
                 f"{{${sgn(a['mean'])}$}};")
    # the label of the gap line, above the plot
    L.append(f"  \\node[anchor=south, font=\\tiny] at "
             f"(axis cs:{gap:.3f},{ymax:.2f}) "
             f"{{the gap {gap:.3f}}};")
    L.append(r"\end{axis}")
    L.append(r"\end{tikzpicture}")

    for a in arms:
        a["verdict"] = ("excluded" if a["excluded"]
                        else "not excluded")
        a["margin"] = gap - a["hi"]
    return "\n".join(L), arms


# ----------------------------------------------------------------------
# FIGURE 2: the training-budget sweep
# ----------------------------------------------------------------------
def budget_rows():
    """The training-budget sweep, from the artefact the table reads."""
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
            raise SystemExit(f"the budget row for {r['episodes']} episodes has "
                             f"no per-seed values; the figure was not drawn")
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


def figure_budget(tok):
    """The training-budget sweep, with the seed spread and the paired gain."""
    gap = req(tok, "GAP")
    rule = req(tok, "BEST_RULE_CK")
    rule_name = tok.get("BEST_RULE_NAME", "the strongest rule")
    paired = req(tok, "BUDGET_PAIRED")
    ci = tok.get("BUDGET_PAIRED_CI", "")
    frac = tok.get("BUDGET_FRAC", "")
    lo_b, hi_b = tok.get("BUDGET_MIN"), tok.get("BUDGET_MAX")
    rows = budget_rows()
    eps = [r["episodes"] for r in rows]
    cks = [r["mean"] for r in rows]
    sds = [r["sd"] for r in rows]
    nseed = rows[0]["n"]

    xmin, xmax = min(eps) - 3.0, max(eps) + 4.5
    ymin = min(c - s for c, s in zip(cks, sds)) - 0.06
    ymax = rule + 0.07
    arrow_x = max(eps) + 1.7
    lab_x = arrow_x + 0.7

    L = []
    L.append(r"\begin{tikzpicture}")
    L.append(r"\begin{axis}[width=\columnwidth,height=5.6cm,")
    L.append(f"  xmin={xmin:.2f}, xmax={xmax:.2f}, "
             f"ymin={ymin:.3f}, ymax={ymax:.3f},")
    L.append("  xtick={" + ",".join(str(e) for e in eps) + "},")
    L.append("  ytick={" + ",".join(f"{y:g}" for y in
             [round(ymin + 0.1 * k, 1) for k in range(1, 8)]) + "},")
    L.append(r"  xlabel={training episodes}, ylabel={persistent coverage},")
    L.append(COMMON)
    L.append(r"  legend style={font=\tiny, at={(0.5,-0.30)}, anchor=north, "
             r"legend columns=1}],")
    # the rule the gap is measured against
    L.append(f"  \\addplot[black, dashed, line width=1.0pt] coordinates "
             f"({xmin:.2f},{rule:.3f}) ({xmax:.2f},{rule:.3f});")
    # the sweep, with the seed-to-seed spread
    coords = " ".join(
        f"({e},{c}) +- (0,{s:.4f})" for e, c, s in zip(eps, cks, sds))
    L.append(r"  \addplot[color=" + UAVBLUE + r", thick, mark=*, mark size=1.9pt,"
             r" mark options={fill=" + UAVBLUE + r"},"
             r" error bars/.cd, y dir=both, y explicit,"
             r" error bar style={line width=0.8pt, color=" + UAVBLUE + r"},"
             r" error mark options={rotate=90, mark size=3pt, line width=0.8pt,"
             r" color=" + UAVBLUE + r"}] coordinates {" + coords + "};")
    L.append(r"  \legend{the strongest rule,"
             r"the learned controller ($\pm 1$ s.d. over the "
             r"training seeds)}")
    # the gap that is left at the longest budget
    L.append(f"  \\draw[{UAVRED}, line width=0.9pt, <->] "
             f"(axis cs:{arrow_x:.2f},{cks[-1]:.3f}) -- "
             f"(axis cs:{arrow_x:.2f},{rule:.3f});")
    L.append(f"  \\node[rotate=90, anchor=south, font=\\tiny, text={UAVRED}] "
             f"at (axis cs:{lab_x:.2f},{(cks[-1] + rule) / 2:.3f}) "
             f"{{gap {gap:.3f}}};")
    # the rule's name, above its line
    L.append(f"  \\node[anchor=south west, font=\\tiny] at "
             f"(axis cs:{xmin + 0.4:.2f},{rule + 0.004:.3f}) "
             f"{{{rule_name} ({rule:.3f})}};")
    # the paired gain over the range the sweep covers
    txt = (f"training over {eps[0]}--{eps[-1]} episodes: "
           f"$\\Delta={sgn(paired)}$")
    if ci:
        txt += f"\\\\95\\% CI {ci}"
    if frac:
        txt += f" --- {frac}\\% of the gap"
    L.append(f"  \\node[anchor=north west, font=\\tiny, align=left] at "
             f"(axis cs:{xmin + 0.4:.2f},{rule - 0.012:.3f}) {{{txt}}};")
    L.append(r"\end{axis}")
    L.append(r"\end{tikzpicture}")
    return "\n".join(L), dict(rows=rows, gap=gap, rule=rule,
                              rule_name=rule_name, paired=paired, ci=ci,
                              frac=frac, lo=lo_b, hi=hi_b, nseed=nseed)


# ----------------------------------------------------------------------
# FIGURE 3: the scenario matrix
# ----------------------------------------------------------------------
def scenario_points():
    """The learned controller's deficit against the stronger rule, per variant."""
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


def figure_scen(tok):
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
    ymax = 0.05
    xmin, xmax = 0.3, n + 0.7

    L = []
    L.append(r"\begin{tikzpicture}")
    L.append(r"\begin{axis}[width=\columnwidth,height=5.0cm,")
    L.append(f"  xmin={xmin:.2f}, xmax={xmax:.2f}, "
             f"ymin={ymin:.3f}, ymax={ymax:.3f},")
    centres = [0.5 * (g[1] + g[2]) for g in groups]
    L.append("  xtick={" + ",".join(f"{c:g}" for c in centres) + "},")
    L.append("  xticklabels={" + ",".join(g[0] for g in groups) + "},")
    L.append("  ytick={" + ",".join(f"{y:g}" for y in
             [round(ymin + 0.1 * k, 1) for k in range(1, 6)]) + "},")
    L.append(r"  xlabel={scenario (each marker is one variant)},"
             r" ylabel={coverage difference (learned $-$ rule)},")
    L.append(COMMON)
    # the separators between the scenarios
    for g in groups[:-1]:
        x = g[2] + 0.5
        L.append(f"  \\draw[gray!45, line width=0.4pt] "
                 f"(axis cs:{x:.2f},{ymin:.3f}) -- "
                 f"(axis cs:{x:.2f},{ymax:.3f});")
    # the level line
    L.append(f"  \\addplot[{UAVRED}, dashed, line width=1.0pt] coordinates "
             f"({xmin:.2f},0) ({xmax:.2f},0);")
    # the variants
    L.append(r"  \addplot[only marks, mark=*, mark size=1.8pt, color="
             + UAVBLUE + ", mark options={fill=" + UAVBLUE + "}] coordinates {"
             + " ".join(f"({p['idx']},{p['d']:.3f})" for p in pts) + "};")
    # the two labels that carry the point of the figure
    L.append(f"  \\node[anchor=south east, font=\\tiny, text={UAVRED}] at "
             f"(axis cs:{xmax - 0.2:.2f},0.004) "
             f"{{level with the stronger rule}};")
    L.append(f"  \\node[anchor=south west, font=\\tiny, text={UAVRED}] at "
             f"(axis cs:{xmin + 0.2:.2f},0.004) "
             f"{{{losses} of the {n} variants behind}};")
    L.append(r"\end{axis}")
    L.append(r"\end{tikzpicture}")
    return "\n".join(L), dict(pts=pts, groups=groups, wins=wins,
                              losses=losses, ties=ties, n=n)


# ----------------------------------------------------------------------
# the standalone renderers
# ----------------------------------------------------------------------
PREAMBLE = r"""\documentclass[10pt]{article}
\usepackage[paperwidth=4.3in,paperheight=3.4in,margin=0.4in]{geometry}
\usepackage{amsmath}
\usepackage{tikz}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\definecolor{uavblue}{RGB}{37,99,235}
\definecolor{uavcyan}{RGB}{8,145,178}
\definecolor{uavgreen}{RGB}{22,163,74}
\definecolor{uavorange}{RGB}{234,88,12}
\definecolor{uavred}{RGB}{220,38,38}
\definecolor{uavpurple}{RGB}{124,58,237}
\pagestyle{empty}
\setlength{\parindent}{0pt}
\begin{document}
\newsavebox{\figbox}
\sbox{\figbox}{\input{%s}}
\typeout{FIGWIDTH=\the\wd\figbox}
\noindent\usebox{\figbox}
\end{document}
"""


def render(name, body, do_render=True):
    """Write the fragment, render it, and check it against the column width."""
    frag = os.path.join(HERE, name + ".tex")
    with open(frag, "w", encoding="utf-8") as f:
        f.write(body + "\n")
    print(f"Wrote {frag}")
    if not do_render:
        return None
    doc = os.path.join(HERE, "render_" + name + ".tex")
    with open(doc, "w", encoding="utf-8") as f:
        f.write(PREAMBLE % (name + ".tex"))
    for stale in (doc.replace(".tex", ".pdf"),
                  doc.replace(".tex", ".log"),
                  doc.replace(".tex", ".aux")):
        if os.path.exists(stale):
            os.remove(stale)
    p = subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
         os.path.basename(doc)],
        cwd=HERE, capture_output=True, text=True)
    log = ""
    if os.path.exists(doc.replace(".tex", ".log")):
        log = open(doc.replace(".tex", ".log"), encoding="utf-8",
                   errors="replace").read()
    if p.returncode != 0 or "Output written on" not in log:
        print(f"  [render] {name} did not compile:")
        print("\n".join(log.splitlines()[-25:]))
        return None
    m = re.search(r"FIGWIDTH=([0-9.]+)pt", log)
    width_pt = float(m.group(1)) if m else float("nan")
    col_pt = 3.5 * 72.27          # IEEEtran's one-column width
    over = re.findall(r"Overfull \\hbox \(([0-9.]+)pt", log)
    print(f"  [render] {name}: natural width {width_pt:.1f}pt "
          f"({width_pt / 72.27:.2f}in) against a 3.50in column"
          + ("  <-- TOO WIDE" if width_pt > col_pt + 0.5 else ""))
    if over:
        print(f"  [render] {name}: overfull hboxes {over}")
    pdf = doc.replace(".tex", ".pdf")
    png = os.path.join(HERE, name + ".png")
    for stale in (png,):
        if os.path.exists(stale):
            os.remove(stale)
    subprocess.run(["pdftoppm", "-png", "-r", "150", "-singlefile",
                    os.path.basename(pdf), os.path.basename(png[:-4])],
                   cwd=HERE, capture_output=True, text=True)
    if os.path.exists(png):
        print(f"Wrote {png}")
    else:
        print(f"  [render] {name}: the PNG was not produced")
    return width_pt


def main():
    do_render = "--no-render" not in sys.argv
    tok = build_tokens()

    body, arms = figure_arms(tok)
    render("fig_arms", body, do_render)
    print("  [arms] gap {:.3f}".format(req(tok, "GAP")))
    for a in arms:
        print("    {:6s} {:>7s}  95% CI [{:+.3f}, {:+.3f}]  {}"
              .format(a["key"], sgn(a["mean"]), a["lo"], a["hi"],
                      a["verdict"]))

    body, bud = figure_budget(tok)
    render("fig_budget", body, do_render)
    print("  [budget] sweep " + tok.get("BUDGET_SWEEP", "?"))
    print("    paired {:+}  CI {}  ({}% of the gap {:.3f})".format(
        bud["paired"], bud["ci"], bud["frac"], bud["gap"]))

    body, scen = figure_scen(tok)
    render("fig_scen", body, do_render)
    print("  [scen] {} variants: {} ahead, {} behind, {} level".format(
        scen["n"], scen["wins"], scen["losses"], scen["ties"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
