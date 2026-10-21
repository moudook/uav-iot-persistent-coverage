"""
The TEASER figure for the first page: one picture that carries the paper's
argument in three panels.

  (a) the FEASIBILITY CERTIFICATE -- the published configuration is provably
      infeasible for K-covering the region (the covering bound needs
      N >= 4K), while the conventional area-surplus criterion, which the
      same configuration satisfies, certifies nothing;
  (b) the CONTROLLER -- the CTDE MAPPO with its hard feasibility layer
      (connectivity mask, reserve UAV, charging arbitration), measured
      against the hand-designed rule and against the achievability ceiling;
  (c) the RESULT -- the controlled arms against the gap, every arm's upper
      confidence limit below the gap.

Every number is read AT RUN TIME from the token table (analysis/
fill_tokens.py, function build_tokens) or from the artefact the table is
built from, so the teaser cannot disagree with the prose: the three
panels are drawn from the same measurements the tables and the sentences
are.  Nothing measured is typed into this file.

Outputs
  analysis/fig_teaser.tex   the drop-in pgfplots/TikZ fragment
  analysis/fig_teaser.png   the rendered preview (looked at before shipping)

Run:  python analysis/make_teaser.py
      python analysis/make_teaser.py --no-render   (fragment only)
"""

from __future__ import annotations

import csv
import json
import math
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ML = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)
if ML not in sys.path:
    sys.path.insert(0, ML)

from fill_tokens import build_tokens                       # noqa: E402

# The scratch directory: the standalone renderer's .tex/.pdf/.log live
# here, never in the project tree.
SCRATCH = os.path.join(tempfile.gettempdir(), "opencode")

# ----------------------------------------------------------------------
# the layout, in centimetres.  The figure spans both columns, so the
# natural width of the fragment is the text width of the paper.
# ----------------------------------------------------------------------
TEXT_W_CM = 7.16 * 2.54          # 7.16 in, the IEEEtran conference width
PLOT_H = 3.60                    # the height of every plot rectangle
W_A = 4.55                       # panel (a): the area-surplus plot
W_B = 4.75                       # panel (b): the controller schematic
W_C = 4.95                       # panel (c): the arms' intervals
LAB_A = 0.95                     # room for panel (a)'s y label and ticks
LAB_C = 1.60                     # room for panel (c)'s arm names
GAP = 0.40                       # between the panels
LEFT = 0.15                      # the content is centred in the text width
# pgfplots anchors an axis at the OUTER bounding box of its description
# (its axis title, but not its tick labels), so the plot rectangle starts
# this far to the right of the `at' coordinate.  The two values below are
# CALIBRATED from the rendered PDF by the fitting loop in main(), not
# guessed: the loop measures where the plot rectangles actually landed and
# corrects them.
AXIS_SHIFT_A = 0.95
AXIS_SHIFT_C = 0.47

X_A = LEFT + LAB_A - AXIS_SHIFT_A
X_B = LEFT + LAB_A + W_A + GAP
X_C = X_B + W_B + GAP + LAB_C - AXIS_SHIFT_C
CONTENT_W = X_C + W_C + AXIS_SHIFT_C

TITLE_Y = 3.90                   # the panel titles
STRIP_Y = 4.75                   # the legend strip
# The legend strip is inset from the picture's bounding box, so that its
# frame, its swatches and its last label all sit inside the canvas with a
# margin: the frame is drawn 2.5pt outside the node's box, so the node
# goes STRIP_INSET from the left edge and the box is shortened to match.
STRIP_INSET = 10.5               # pt, from the picture's left edge

BLUE, CYAN, GREEN = "uavblue", "uavcyan", "uavgreen"
ORANGE, RED, PURPLE = "uavorange", "uavred", "uavpurple"
GREY = "uavgray"

# the arms of the controlled comparison: the token prefix and the short
# name on the axis (the same names the paper's own figure uses)
ARMS = [
    ("OBS_B", r"identity"),
    ("OBS_C", r"full obs."),
    ("EB", r"no constraint"),
    ("EC", r"no threshold"),
    ("ED", r"prev.\ rule"),
    ("CREDIT", r"local critic"),
]


# ----------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------
def num(tok, name):
    """A token's value as a float, or None."""
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
                         f"(value: {tok.get(name)!r}); the teaser was not "
                         f"drawn")
    return v


def load_json_ml(name):
    p = os.path.join(ML, name)
    if not os.path.exists(p):
        return None
    return json.load(open(p, encoding="utf-8"))


def load_json(name):
    p = os.path.join(HERE, name)
    if not os.path.exists(p):
        return None
    return json.load(open(p, encoding="utf-8"))


def main_row(model):
    """One row of the main results table, by model name."""
    p = os.path.join(ML, "results_main.csv")
    if not os.path.exists(p):
        return None
    with open(p, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r.get("model") == model:
                return r
    return None


def hatched(x0, y0, x1, y1, color=BLUE, indent="  "):
    """A hatched bar: the fill, white hatch lines, the outline.

    The hatch is drawn by hand rather than with TikZ's `patterns' library,
    because a library cannot be loaded from the body of a document: the
    fragment has to compile inside the paper's preamble as it stands.
    """
    h = y1 - y0
    step = max(h * 0.9, 0.10)
    n = int((x1 - x0) / step) + 2
    o = [f"{indent}\\begin{{scope}}"]
    o.append(f"{indent}  \\clip ({x0:.3f},{y0:.3f}) rectangle ({x1:.3f},{y1:.3f});")
    o.append(f"{indent}  \\fill[{color}] ({x0:.3f},{y0:.3f}) rectangle "
             f"({x1:.3f},{y1:.3f});")
    o.append(f"{indent}  \\foreach \\t in {{"
             + ",".join(f"{i * step:.3f}" for i in range(n)) + "}{")
    # The hatch is drawn inside a scope whose origin is the box's own
    # left edge, so the coordinates are relative to it.  A macro named
    # \x0 would not work: TeX ends a control word at the first
    # non-letter, so "\x0" is the control sequence "\x" followed by the
    # digit 0, and the macro is undefined.
    o.append(f"{indent}    \\draw[white, line width=0.35pt] "
             f"(\\t,{y0:.3f}) -- (\\t+{h:.3f},{y1:.3f});")
    o.append(f"{indent}  }}")
    o.append(f"{indent}\\end{{scope}}")
    o.append(f"{indent}\\draw[{color}, line width=0.4pt] ({x0:.3f},{y0:.3f}) "
             f"rectangle ({x1:.3f},{y1:.3f});")
    return "\n".join(o)


def sgn(x, nd=3):
    return f"{x:+.{nd}f}"


# ----------------------------------------------------------------------
# the data, all of it read at run time
# ----------------------------------------------------------------------
def gather():
    """Every number the teaser draws, with the artefact it came from."""
    tok = build_tokens()
    d = {}

    # --- panel (a): the feasibility certificate -----------------------
    feas = load_json_ml("results_feasibility.json")
    if feas is None:
        raise SystemExit("results_feasibility.json is missing; the teaser "
                         "was not drawn")
    cfg = feas["config"]
    rb = feas["region_bound"]
    sur = feas["surplus"]
    ps = feas["packing_survey"]

    d["K"] = int(cfg["K"])
    d["R_cov"] = float(cfg["R_cov"])
    d["area"] = float(sur["field_area_m2"])
    d["side"] = float(cfg["side"])
    d["N_pub"] = int(rb["N_available"])
    d["N_bound"] = int(rb["N_required_for_corners"])
    d["corners_disjoint"] = bool(rb["corner_discs_disjoint"])
    d["sigma_pub"] = float(sur["surplus_sigma"])
    # the area surplus as a function of the fleet size, from the same
    # parameters the artefact uses:  sigma = N pi R^2 / (K |Omega|)
    d["sigma"] = (lambda n: n * math.pi * d["R_cov"] ** 2
                  / (d["K"] * d["area"]))
    if abs(d["sigma"](d["N_pub"]) - d["sigma_pub"]) > 1e-9:
        raise SystemExit("the area surplus recomputed from the artefact "
                         "does not match the artefact's own value")
    # the fleet size at which the area criterion starts to accept
    d["N_area"] = d["K"] * d["area"] / (math.pi * d["R_cov"] ** 2)
    # the sensor-set bound: measured over the random draws
    d["pack_seeds"] = int(ps["seeds"])
    d["pack_mean"] = float(ps["packing_size_mean"])
    d["pack_n_mean"] = float(ps["N_required_mean"])
    d["pack_n_max"] = int(ps["N_required_max"])
    d["pack_excl"] = int(ps["seeds_excluded"])
    d["pack_excl_pct"] = 100.0 * float(ps["seeds_excluded_fraction"])
    d["pack_excl_pct"] = int(round(d["pack_excl_pct"]))

    # --- panel (b): the controller and its references -----------------
    d["gap"] = req(tok, "GAP")
    d["gap_ci"] = tok.get("GAP_CI", "")
    d["gap_half"] = num(tok, "GAP_HALF")
    d["gap_n"] = tok.get("GAP_N", "")
    d["ck_ours"] = req(tok, "MAPPO_CK")
    d["ck_ours_sd"] = num(tok, "MAPPO_CK_STD")
    d["ck_ours_seeds"] = tok.get("MAPPO_N_SEEDS", "")
    d["rule_name"] = tok.get("BEST_RULE_NAME", "the hand-designed rule")
    d["ck_rule"] = req(tok, "BEST_RULE_CK")
    d["mask_h"] = int(cfg["mask_horizon"])
    d["pads"] = int(cfg["n_pads"])
    d["episode_steps"] = tok.get("EPISODE_STEPS", "")
    d["episode_seconds"] = tok.get("EPISODE_SECONDS", "")
    d["episodes"] = tok.get("ABL_EPISODES", "")
    d["seeds"] = tok.get("ABL_SEEDS", "")
    # the achievability ceiling, as the main results table reports it
    orow = main_row("Oracle (ceiling)")
    if orow is None:
        raise SystemExit("the achievability ceiling is missing from "
                         "results_main.csv; the teaser was not drawn")
    d["ck_oracle"] = float(orow["CK"])
    # the CORRECTED configuration, from the artefact that measured it
    alt = load_json("alt_deployment.json")
    rep = None
    for r in (alt or []):
        if r.get("arm") == "reported":
            rep = r
    if rep is None:
        raise SystemExit("the corrected deployment is missing from "
                         "alt_deployment.json; the teaser was not drawn")
    d["n_corrected"] = int(rep["N"])
    d["r_corrected"] = float(rep["R_cov"])
    # the metrics on the infeasible instance
    d["inf_ck"] = num(tok, "INF_CK")
    d["inf_sc"] = num(tok, "INF_SC")
    d["inf_oracle"] = num(tok, "INF_ORACLE")

    # --- panel (c): the controlled arms -------------------------------
    arms = []
    for key, short in ARMS:
        mean = num(tok, f"{key}_PAIRED")
        half = num(tok, f"{key}_HALF")
        if mean is None or half is None:
            print(f"  [teaser] the arm {key} has no paired interval in the "
                  f"token table; it is left out of the picture")
            continue
        arms.append(dict(key=key, short=short, mean=mean, half=half,
                         lo=mean - half, hi=mean + half,
                         excluded=(mean + half) < d["gap"]))
    if not arms:
        raise SystemExit("no arm has a paired interval; the teaser was not "
                         "drawn")
    d["arms"] = arms
    return tok, d


# ----------------------------------------------------------------------
# panel (a): the two criteria disagree
# ----------------------------------------------------------------------
def panel_a(d):
    """The area-surplus criterion and the covering bound, on one axis."""
    xmin, xmax = 2.8, 9.3
    ymin, ymax = 0.0, 3.05
    xs = [3, 4, 5, 6, 7, 8, 9]
    ys = [d["sigma"](n) for n in xs]

    o = []
    o.append(f"\\begin{{axis}}[at={{({X_A:.2f}cm,0cm)}}, anchor=south west,")
    o.append(f"  scale only axis, width={W_A:.2f}cm, height={PLOT_H:.2f}cm,")
    o.append(f"  xmin={xmin:.2f}, xmax={xmax:.2f}, ymin={ymin:.2f}, "
             f"ymax={ymax:.2f},")
    o.append("  xtick={3,4,5,6,7,8,9}, ytick={0,1,2,3},")
    o.append(r"  xlabel={fleet size $N$}, ylabel={area surplus $\sigma$},")
    o.append(r"  axis x line*=bottom, axis y line*=left, grid=both, "
             r"grid style={gray!20},")
    o.append(r"  tick label style={font=\tiny}, label style={font=\small},")
    o.append(r"  clip=false, enlargelimits=false,]")

    # the band in which the two criteria disagree: the area count accepts
    # (sigma >= 1) and the covering bound excludes (N < 4K)
    o.append(f"  \\addplot[draw=none, fill={RED}!8, forget plot] "
             f"coordinates {{({d['N_area']:.3f},{ymin:.2f}) "
             f"({d['N_bound'] - 0.001:.3f},{ymin:.2f}) "
             f"({d['N_bound'] - 0.001:.3f},{ymax:.2f}) "
             f"({d['N_area']:.3f},{ymax:.2f})}} \\closedcycle;")
    # the area criterion's own threshold
    o.append(f"  \\addplot[gray!65, dashed, line width=0.9pt, forget plot] "
             f"coordinates {{({xmin:.2f},1) ({xmax:.2f},1)}};")
    # the covering bound
    o.append(f"  \\addplot[{RED}, dashed, line width=1.1pt, forget plot] "
             f"coordinates {{({d['N_bound']},{ymin:.2f}) "
             f"({d['N_bound']},{ymax:.2f})}};")
    # the area surplus as a function of the fleet size
    coords = " ".join(f"({n},{y:.4f})" for n, y in zip(xs, ys))
    o.append(f"  \\addplot[color={BLUE}, thick, mark=*, mark size=1.7pt, "
             f"mark options={{fill={BLUE}}}, forget plot] coordinates "
             f"{{{coords}}};")
    # the published configuration: accepted by the area count, excluded by
    # the bound
    o.append(f"  \\addplot[only marks, mark=o, mark size=2.6pt, "
             f"color={RED}, mark options={{fill=white, line width=1.1pt}}, "
             f"forget plot] coordinates "
             f"{{({d['N_pub']},{d['sigma_pub']:.4f})}};")
    # the corrected configuration, on the bound
    o.append(f"  \\addplot[only marks, mark=*, mark size=2.4pt, "
             f"color={BLUE}, mark options={{fill={BLUE}}}, forget plot] "
             f"coordinates {{({d['N_bound']},"
             f"{d['sigma'](d['N_bound']):.4f})}};")

    # the labels
    o.append(f"  \\node[anchor=north west, font=\\tiny, align=left] at "
             f"(axis cs:{d['N_pub'] + 0.08:.2f},{d['sigma_pub'] - 0.06:.3f}) "
             f"{{published\\\\$\\sigma={d['sigma_pub']:.3f}$}};")
    o.append(f"  \\node[anchor=south east, font=\\tiny] at "
             f"(axis cs:{d['N_bound'] - 0.08:.2f},"
             f"{d['sigma'](d['N_bound']) + 0.06:.3f}) "
             f"{{corrected $N={d['N_bound']}$}};")
    o.append(f"  \\node[rotate=90, anchor=south, font=\\tiny, text={RED}] at "
             f"(axis cs:{d['N_bound']},1.05) "
             f"{{$N\\geq 4K={d['N_bound']}$}};")
    # the area criterion's own threshold: the label sits just above the
    # dashed line and clear of the axis, because the curve leaves no room
    # below the line at the left-hand end
    o.append(f"  \\node[anchor=south west, font=\\tiny] at "
             f"(axis cs:{xmin + 0.18:.2f},1.25) {{$\\sigma=1$}};")
    o.append(f"  \\node[anchor=south west, font=\\tiny] at "
             f"(axis cs:{d['N_area'] + 0.10:.2f},{ymax - 0.06:.2f}) "
             f"{{the two criteria disagree}};")
    o.append(f"  \\node[anchor=north west, font=\\tiny, align=left] at "
             f"(axis cs:{xmin + 0.06:.2f},0.52) "
             f"{{sensor set: $N\\geq {d['pack_n_mean']:.2f}$ on average\\\\"
             f"$N={d['N_pub']}$ excluded in {d['pack_excl_pct']}\\% of "
             f"{d['pack_seeds']} draws}};")
    o.append("\\end{axis}")
    return "\n".join(o)


# ----------------------------------------------------------------------
# panel (b): the controller, and what it is measured against
# ----------------------------------------------------------------------
def panel_b(d):
    """The CTDE controller schematic and the reference set."""
    scale = 4.20                       # cm per unit of persistent coverage
    x0 = 0.05
    w_ours = scale * d["ck_ours"]
    w_rule = scale * d["ck_rule"]
    x_ours = x0 + w_ours
    x_rule = x0 + w_rule
    x_ora = x0 + scale * d["ck_oracle"]

    o = []
    o.append(f"\\begin{{scope}}[shift={{({X_B:.2f}cm,0cm)}}]")
    # ---- the loop: observation, shared actor, executed action --------
    o.append(r"  \node[box, fill=" + CYAN + r"!10, draw=" + CYAN + r","
             r" minimum width=1.10cm, minimum height=0.46cm]"
             r" (obs) at (0.60,3.30) {obs.\ $\mathbf o_i$};")
    o.append(r"  \node[box, fill=" + PURPLE + r"!10, draw=" + PURPLE + r","
             r" minimum width=1.80cm, minimum height=0.46cm]"
             r" (actor) at (2.35,3.30) {shared actor $\pi_\theta$};")
    o.append(r"  \node[box, fill=" + GREY + r"!8, draw=" + GREY + r","
             r" minimum width=1.50cm, minimum height=0.46cm]"
             r" (act) at (4.10,3.30) {action $a_i$};")
    o.append(r"  \draw[arr] (obs.east) -- node[above, font=\tiny] "
             r" {$\mathbf o_i$} (actor.west);")
    o.append(r"  \draw[arr] (actor.east) -- (act.west);")
    # ---- the training-only critic and the hard feasibility layer -----
    o.append(r"  \node[box, dashed, fill=" + PURPLE + r"!7, draw=" + PURPLE
             + r", minimum width=1.80cm, minimum height=0.62cm,"
             r" inner sep=1pt]"
             r" (crit) at (0.95,2.45) {centralized critic\\$V_\phi(\mathbf s_t)$"
             r"\\(training only)};")
    o.append(r"  \draw[darr] (crit.north) -- (1.55,3.03);")
    o.append(r"  \node[box, fill=" + RED + r"!8, draw=" + RED + r","
             r" minimum width=2.70cm, minimum height=0.62cm, inner sep=1pt]"
             r" (hard) at (3.40,2.45) {hard layer (not learned)\\"
             r"connectivity mask $H{=}" + str(d["mask_h"]) + r"$\\reserve UAV\\"
             r"charging arbitration};")
    o.append(r"  \draw[arr] (hard.north west) -- (2.60,3.03);")

    # ---- the corrected configuration this is all measured on ---------
    o.append(rf"  \node[anchor=north west, font=\tiny] at (0.05,2.02) "
             rf"{{corrected: $N={d['n_corrected']}$, $K={d['K']}$, "
             rf"$R_{{\mathrm{{cov}}}}={d['r_corrected']:.0f}$\,m}};")

    # ---- the reference set ------------------------------------------
    o.append(hatched(x0, 1.00, x_ours, 1.16, BLUE))
    o.append(rf"  \node[anchor=south west, font=\tiny] at ({x0:.2f},1.19) "
             rf"{{CTDE MAPPO}};")
    o.append(rf"  \node[anchor=west, font=\tiny] at ({x_ours + 0.06:.2f},1.08) "
             rf"{{{d['ck_ours']:.3f}}};")
    o.append(rf"  \filldraw[fill=gray!55, draw=gray!70, line width=0.4pt] "
             rf"({x0:.2f},0.36) rectangle ({x_rule:.2f},0.52);")
    o.append(rf"  \node[anchor=south west, font=\tiny] at ({x0:.2f},0.55) "
             rf"{{unprivileged reactive rule}};")
    o.append(rf"  \node[anchor=west, font=\tiny] at ({x_rule + 0.06:.2f},0.44) "
             rf"{{{d['ck_rule']:.3f}}};")
    # the gap between the two bars
    o.append(rf"  \draw[{RED}, line width=0.9pt, <->] ({x_ours:.2f},0.85) -- "
             rf"({x_rule:.2f},0.85);")
    o.append(rf"  \node[anchor=north, font=\tiny, text={RED}] at "
             rf"({(x_ours + x_rule) / 2:.2f},0.83) {{gap {d['gap']:.3f}}};")
    # the achievability ceiling
    o.append(rf"  \draw[black, dashed, line width=1.0pt] ({x_ora:.2f},0.25) "
             rf"-- ({x_ora:.2f},1.45);")
    o.append(rf"  \node[anchor=south east, font=\tiny] at ({x_ora - 0.05:.2f},"
             rf"1.30) {{teleporting oracle {d['ck_oracle']:.3f}}};")
    o.append("\\end{scope}")
    return "\n".join(o)


# ----------------------------------------------------------------------
# panel (c): the controlled arms against the gap
# ----------------------------------------------------------------------
def panel_c(d):
    """The arms' 95% intervals, against the gap they would have to explain."""
    gap = d["gap"]
    half = d["gap_half"]
    arms = d["arms"]
    n = len(arms)
    lo_all = min(a["lo"] for a in arms)
    hi_all = max(a["hi"] for a in arms)
    xmin = math.floor((lo_all - 0.03) * 10) / 10.0
    xmax = max(math.ceil((hi_all + 0.04) * 10) / 10.0, round(gap + 0.11, 3))
    ymin, ymax = 0.35, n + 0.65

    o = []
    o.append(f"\\begin{{axis}}[at={{({X_C:.2f}cm,0cm)}}, anchor=south west,")
    o.append(f"  scale only axis, width={W_C:.2f}cm, height={PLOT_H:.2f}cm,")
    o.append(f"  xmin={xmin:.3f}, xmax={xmax:.3f}, ymin={ymin:.2f}, "
             f"ymax={ymax:.2f},")
    ticks = []
    k = math.ceil(xmin / 0.1 - 1e-9)
    while k * 0.1 <= xmax + 1e-9:
        ticks.append(round(k * 0.1, 10))
        k += 1
    o.append("  xtick={" + ",".join(f"{t:g}" for t in ticks) + "},")
    o.append("  ytick={" + ",".join(str(n - i) for i in range(n)) + "},")
    o.append("  yticklabels={"
             + ",".join("{" + a["short"] + "}" for a in arms) + "},")
    o.append(r"  xlabel={difference in persistent coverage},")
    o.append(r"  axis x line*=bottom, axis y line*=left, grid=both, "
             r"grid style={gray!20},")
    o.append(r"  tick label style={font=\tiny}, label style={font=\small},")
    o.append(r"  clip=false, enlargelimits=false,]")
    if half is not None:
        o.append(f"  \\addplot[draw=none, fill=gray!20, forget plot] "
                 f"coordinates {{({gap - half:.3f},{ymin:.2f}) "
                 f"({gap + half:.3f},{ymin:.2f}) "
                 f"({gap + half:.3f},{ymax:.2f}) "
                 f"({gap - half:.3f},{ymax:.2f})}} \\closedcycle;")
    o.append(f"  \\addplot[black, dashed, line width=1.1pt, forget plot] "
             f"coordinates {{({gap:.3f},{ymin:.2f}) ({gap:.3f},{ymax:.2f})}};")
    for i, a in enumerate(arms):
        y = n - i
        col = GREEN if a["excluded"] else RED
        o.append(f"  \\addplot[color={col}, mark=*, mark size=1.7pt, "
                 f"mark options={{fill=white,draw=black,line width=0.5pt}},"
                 f" forget plot,"
                 f" error bars/.cd, x dir=both, x explicit,"
                 f" error bar style={{line width=2.4pt, color={col}}},"
                 f" error mark=|,"
                 f" error mark options={{mark size=3.2pt, "
                 f"line width=0.8pt, color={col}}}] coordinates "
                 f"{{({a['mean']:.3f},{y}) +- ({a['half']:.3f},0)}};")
        o.append(f"  \\node[anchor=south, font=\\tiny] at "
                 f"(axis cs:{a['mean']:.3f},{y + 0.17:.2f}) "
                 f"{{${sgn(a['mean'])}$}};")
    # the group separators: the observation arms, then the energy arms
    for boundary in (2, 5):
        if boundary < n:
            ysep = n - boundary + 0.5
            o.append(f"  \\draw[gray!50, line width=0.4pt, "
                     f"dash pattern=on 2pt off 2pt] "
                     f"(axis cs:{xmin:.3f},{ysep:.2f}) -- "
                     f"(axis cs:{xmax:.3f},{ysep:.2f});")
    o.append(f"  \\node[anchor=north, font=\\tiny] at "
             f"(axis cs:{gap:.3f},{ymax - 0.06:.2f}) "
             f"{{the gap {gap:.3f}}};")
    o.append("\\end{axis}")
    return "\n".join(o)


# ----------------------------------------------------------------------
# the legend strip and the panel titles
# ----------------------------------------------------------------------
def legend_strip(d):
    """The horizontal boxed legend across the top of the figure."""
    items = [
        (r"\tikz[baseline=-0.6ex]{"
         + hatched(0, 0, 0.52, 0.15, BLUE, indent="  ") + "}",
         r"\textbf{the learned CTDE MAPPO}"),
        (rf"\tikz[baseline=-0.6ex]{{\filldraw[fill=gray!55, draw=gray!70, "
         rf"line width=0.4pt] (0,0) rectangle (0.52,0.15);}}",
         r"\textbf{the hand-designed rule}"),
        (rf"\tikz[baseline=-0.6ex]{{\draw[black, dashed, line width=1.1pt] "
         rf"(0,0) -- (0.52,0);}}", "the gap"),
        (rf"\tikz[baseline=-0.6ex]{{\filldraw[fill=gray!20, draw=gray!50, "
         rf"line width=0.4pt] (0,0) rectangle (0.52,0.15);}}",
         "the gap's 95\\% CI"),
        (rf"\tikz[baseline=-0.6ex]{{\draw[{GREEN}, line width=2.4pt, "
         rf"line cap=round] (0,0) -- (0.52,0); "
         rf"\filldraw[fill=white, draw=black, line width=0.5pt] "
         rf"(0.26,0) circle (0.055);}}", "95\\% CI, paired mean"),
        (rf"\tikz[baseline=-0.6ex]{{\filldraw[fill={RED}!8, draw={RED}!40, "
         rf"line width=0.4pt] (0,0) rectangle (0.52,0.15);}}",
         "the two criteria disagree"),
    ]
    body = r"\hspace*{6pt}" + " \\hfill ".join(f"{sw}\\ {{{lab}}}" for sw, lab in items) + r"\hspace*{6pt}"
    o = []
    # The strip is INSET from the picture's bounding box: the frame is
    # drawn 2.5pt outside the node's box on each side, so the node is
    # placed STRIP_INSET from the left edge and its makebox is shortened
    # by twice that, which leaves the whole legend -- frame, swatches and
    # the last label -- inside the canvas with a margin on both sides.
    # The items themselves are padded by 6pt, so the last label does not
    # end against the frame.
    o.append(r"  \node[anchor=north west, inner sep=0pt, outer sep=0pt, "
             r"font=\tiny] (strip) at (" + f"{STRIP_INSET:.1f}pt,"
             + f"{STRIP_Y:.2f}) {{")
    o.append(r"    \makebox[\dimexpr\textwidth-"
             + f"{2 * STRIP_INSET:.0f}pt" + r"\relax][s]{")
    o.append("      " + body)
    o.append(r"    }};")
    o.append(r"  \begin{scope}[on background layer]")
    o.append(r"    \draw[fill=white, draw=gray!55, line width=0.5pt, "
             r"rounded corners=1.5pt]")
    o.append(r"      ([xshift=-2.5pt,yshift=-2pt]strip.south west) rectangle "
             r"([xshift=2.5pt,yshift=2pt]strip.north east);")
    o.append(r"  \end{scope}")
    return "\n".join(o)


def titles():
    """The panel titles, centred on the plot rectangles themselves."""
    o = []
    for cx, txt in ((X_A + AXIS_SHIFT_A + W_A / 2,
                     "Feasibility certificate"),
                    (X_B + W_B / 2, "Controller and its references"),
                    (X_C + AXIS_SHIFT_C + W_C / 2,
                     "Arms against the gap")):
        o.append(f"  \\node[anchor=south, font=\\small\\bfseries] at "
                 f"({cx:.2f},{TITLE_Y:.2f}) {{({txt})}};")
    return "\n".join(o)


# ----------------------------------------------------------------------
# the fragment
# ----------------------------------------------------------------------
def fragment(tok, d):
    o = []
    o.append(r"\begin{tikzpicture}["
             r"font=\tiny,"
             r"box/.style={draw,rounded corners=2pt,align=center,"
             r"inner sep=2pt,font=\tiny},"
             r"arr/.style={-{Latex[length=1.6mm]},semithick,uavblue},"
             r"darr/.style={-{Latex[length=1.6mm]},semithick,dashed,"
             r"uavpurple}]")
    o.append(legend_strip(d))
    o.append(titles())
    o.append(panel_a(d))
    o.append(panel_b(d))
    o.append(panel_c(d))
    # The picture's own bounding box is set to the text width, so the
    # figure occupies exactly one text width and never an overfull hbox:
    # the strip's frame is \\textwidth wide and the panels are measured to
    # fit inside it.
    o.append(r"  \pgfresetboundingbox")
    o.append(r"  \path[use as bounding box] (0,-1.15) rectangle "
             r"(\textwidth,4.90);")
    # the trailing % keeps the newline after the picture from adding a
    # space to the box, which would make the figure wider than the text
    o.append(r"\end{tikzpicture}%")
    return "\n".join(o)


# ----------------------------------------------------------------------
# the renderer
# ----------------------------------------------------------------------
PREAMBLE = r"""\documentclass[10pt]{article}
\usepackage[paperwidth=7.5in,paperheight=6.4in,margin=0.17in]{geometry}
\usepackage{amsmath}
\usepackage{tikz}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\usetikzlibrary{arrows.meta,positioning,backgrounds,patterns}
\definecolor{uavblue}{RGB}{37,99,235}
\definecolor{uavcyan}{RGB}{8,145,178}
\definecolor{uavgreen}{RGB}{22,163,74}
\definecolor{uavorange}{RGB}{234,88,12}
\definecolor{uavred}{RGB}{220,38,38}
\definecolor{uavpurple}{RGB}{124,58,237}
\definecolor{uavgray}{RGB}{71,85,105}
\definecolor{uavlight}{RGB}{241,245,249}
\pagestyle{empty}
\setlength{\parindent}{0pt}
\begin{document}
\newsavebox{\figbox}
\sbox{\figbox}{\input{%s}}
\typeout{FIGWIDTH=\the\wd\figbox}
\noindent\usebox{\figbox}
\end{document}
"""


def compile_tex(doc, timeout=240):
    base = os.path.basename(doc).replace(".tex", "")
    for stale in (base + ".pdf", base + ".log", base + ".aux"):
        p = os.path.join(SCRATCH, stale)
        if os.path.exists(p):
            os.remove(p)
    try:
        subprocess.run(["pdflatex", "-interaction=nonstopmode",
                        "-file-line-error", base + ".tex"], cwd=SCRATCH,
                       capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return False, "pdflatex timed out"
    logp = os.path.join(SCRATCH, base + ".log")
    log = open(logp, encoding="utf-8", errors="replace").read() \
        if os.path.exists(logp) else ""
    return ("Output written on" in log), log


def measure_panels(pdf):
    """Where the rendered panels actually landed, measured from the PDF.

    pgfplots places an axis at the OUTER bounding box of its description,
    so where the plot rectangle ends up has to be measured rather than
    assumed.  The origin of the picture is the left edge of the legend
    strip's frame, and the plot rectangles are the bottom spines of the
    two plotted panels.  Returns (origin_x, [(x0, x1), ...]) in PDF points.
    """
    try:
        import pymupdf
    except Exception:                                        # pragma: no cover
        return None, []
    doc = pymupdf.open(pdf)
    page = doc[0]
    lines, frames = [], []
    xmin, xmax = 1e9, -1e9
    for d in page.get_drawings():
        r = d["rect"]
        xmin, xmax = min(xmin, r.x0), max(xmax, r.x1)
        if r.width > 60 and r.height < 2:
            lines.append((round(r.y0, 1), round(r.x0, 1), round(r.x1, 1)))
        if r.width > 400 and r.height < 40:     # the legend strip's frame
            frames.append(r)
    for b in page.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            for s in l["spans"]:
                xmin = min(xmin, s["bbox"][0])
                xmax = max(xmax, s["bbox"][2])
    if not lines or not frames:
        return None, [], None
    origin = min(f.x0 for f in frames) + 2.5
    bottom = max(y for y, _, _ in lines)
    spines = sorted({(x0, x1) for y, x0, x1 in lines if abs(y - bottom) < 0.6})
    return origin, spines, (xmin, xmax)


def crop_png(png, pdf, dpi=150, margin=6):
    """Crop the rendered page to the figure."""
    import numpy as np
    import pymupdf
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


def render(name, body, do_render=True):
    """Write the fragment, render it, and report the natural width."""
    frag = os.path.join(HERE, name + ".tex")
    with open(frag, "w", encoding="utf-8") as f:
        f.write(body)
    if not do_render:
        return None, None
    os.makedirs(SCRATCH, exist_ok=True)
    doc = os.path.join(SCRATCH, "render_" + name + ".tex")
    with open(doc, "w", encoding="utf-8") as f:
        f.write(PREAMBLE % (name + ".tex"))
    # the fragment has to be found by the compiler: copy it into the
    # scratch directory as well, so the render does not depend on the
    # project's own path
    shutil_copy = os.path.join(SCRATCH, name + ".tex")
    with open(shutil_copy, "w", encoding="utf-8") as f:
        f.write(body)
    ok, log = compile_tex(doc)
    if not ok:
        print("  [render] did not compile:")
        print("\n".join(log.splitlines()[-25:]))
        return None
    m = re.search(r"FIGWIDTH=([0-9.]+)pt", log)
    w = float(m.group(1)) if m else None
    if w is not None:
        print(f"  [render] natural width {w:.1f}pt ({w / 72.27:.2f}in) "
              f"against a {TEXT_W_CM / 2.54:.2f}in text width"
              + ("   <-- TOO WIDE" if w > TEXT_W_CM * 28.4527 + 1.0
                 else "   <-- fits"))
    over = re.findall(r"Overfull \\hbox \(([0-9.]+)pt", log)
    if over:
        print(f"  [render] overfull hboxes: {over}")
    pdf = doc.replace(".tex", ".pdf")
    origin, spines, extent = measure_panels(pdf)
    if origin:
        for x0, x1 in spines:
            print(f"  [render] a plot rectangle spans "
                  f"{(x0 - origin) / 28.45:.2f}..{(x1 - origin) / 28.45:.2f} cm "
                  f"from the picture's origin")
        if extent:
            print(f"  [render] the content spans "
                  f"{(extent[1] - extent[0]) / 28.45:.2f} cm in total")
    png = os.path.join(HERE, name + ".png")
    if os.path.exists(png):
        os.remove(png)
    subprocess.run(["pdftoppm", "-png", "-r", "150", "-singlefile",
                    os.path.basename(pdf), os.path.join(SCRATCH, name)],
                   cwd=SCRATCH, capture_output=True, text=True)
    raw = os.path.join(SCRATCH, name + ".png")
    if os.path.exists(raw):
        crop_png(png, pdf)
        print(f"Wrote {png}")
    else:
        print("  [render] the PNG was not produced")
    return w, pdf


def main():
    global AXIS_SHIFT_A, AXIS_SHIFT_C, X_A, X_C
    do_render = "--no-render" not in sys.argv
    tok, d = gather()

    # ---- the fitting loop --------------------------------------------
    # The figure is rendered, the place where the two plot rectangles
    # actually landed is measured from the PDF, and the two anchor offsets
    # are corrected until the three panels sit exactly where the layout
    # says they should.  Nothing here is a guess: the geometry is fitted
    # to the rendered page.
    for attempt in range(5):
        X_A = LEFT + LAB_A - AXIS_SHIFT_A
        X_C = X_B + W_B + GAP + LAB_C - AXIS_SHIFT_C
        body = fragment(tok, d)
        w, pdf = render("fig_teaser", body, do_render)
        if not do_render or pdf is None:
            break
        origin, spines, extent = measure_panels(pdf)
        if origin is None or len(spines) < 2:
            break
        want_a = LEFT + LAB_A
        want_c = X_B + W_B + GAP + LAB_C
        got_a = (spines[0][0] - origin) / 28.45
        got_c = (spines[1][0] - origin) / 28.45
        err_a, err_c = got_a - want_a, got_c - want_c
        print(f"  [fit] pass {attempt + 1}: panel (a) at {got_a:.2f} cm "
              f"(want {want_a:.2f}), panel (c) at {got_c:.2f} cm "
              f"(want {want_c:.2f})")
        if abs(err_a) < 0.01 and abs(err_c) < 0.01:
            break
        AXIS_SHIFT_A += err_a
        AXIS_SHIFT_C += err_c

    print("  [a] published N=%d: sigma=%.3f, bound N>=%d (=4K), "
          "area criterion accepts from N>=%.2f"
          % (d["N_pub"], d["sigma_pub"], d["N_bound"], d["N_area"]))
    print("      sensor set: N>=%.2f on average, %d worst of %d draws; "
          "N=%d excluded in %d%% of them"
          % (d["pack_n_mean"], d["pack_n_max"], d["pack_seeds"],
             d["N_pub"], d["pack_excl_pct"]))
    print("  [b] ours %.3f, rule %.3f (%s), oracle %.3f, gap %.3f %s "
          "over %s seeds"
          % (d["ck_ours"], d["ck_rule"], d["rule_name"], d["ck_oracle"],
             d["gap"], d["gap_ci"], d["gap_n"]))
    print("      mask H=%d, %d pads, %s steps (%s s), %s episodes, %s seeds"
          % (d["mask_h"], d["pads"], d["episode_steps"],
             d["episode_seconds"], d["episodes"], d["seeds"]))
    for a in d["arms"]:
        print("      %-7s %+0.3f  95%% CI [%+0.3f, %+0.3f]  %s"
              % (a["key"], a["mean"], a["lo"], a["hi"],
                 "below the gap" if a["excluded"] else "PAST the gap"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
