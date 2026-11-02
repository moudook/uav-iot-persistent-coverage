"""Teaser v2: feasibility (a), corrected comparison (b), stress split (c).

Reads:
  - Mlawn-midsem-tex.tex token macros (mid) via midsem_numbers.tex
  - runs/stress_eval/stress_eval.json
  - results_feasibility.json (panel a, unchanged from v1)
Writes ml_impl/analysis/fig_teaser.tex (drop-in pgfplots fragment).

Run:  python scripts/make_teaser_v2.py
"""
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ML = os.path.join(ROOT, "ml_impl")
ANALYSIS = os.path.join(ML, "analysis")
OUT = os.path.join(ANALYSIS, "fig_teaser.tex")

TEXT_W_CM = 7.16 * 2.54
PLOT_H = 3.60
W_A = 4.55
W_B = 4.75
W_C = 4.95
LAB_A = 0.95
LAB_C = 1.60
GAP = 0.40
LEFT = 0.15
AXIS_SHIFT_A = 0.95
AXIS_SHIFT_C = 0.47
X_A = LEFT + LAB_A - AXIS_SHIFT_A
X_B = LEFT + LAB_A + W_A + GAP
X_C = X_B + W_B + GAP + LAB_C - AXIS_SHIFT_C

BLUE, GREEN, RED = "uavblue", "uavgreen", "uavred"


def macro(name):
    p = os.path.join(ROOT, "midsem_numbers.tex")
    if not os.path.exists(p):
        return None
    t = open(p, encoding="utf-8").read()
    m = re.search(r"\\newcommand{\\" + name + r"}\{([^}]*)\}", t)
    return m.group(1) if m else None


def num(name, default=None):
    v = macro(name)
    try:
        return float(v) if v is not None else default
    except (TypeError, ValueError):
        return default


def sgn(x):
    return f"{x:+.3f}"


def hatched(x0, y0, x1, y1, color=BLUE, indent="  "):
    h = y1 - y0
    step = max(h * 0.9, 0.10)
    n = int((x1 - x0) / step) + 2
    o = [f"{indent}\\begin{{scope}}"]
    o.append(f"{indent}  \\clip ({x0:.3f},{y0:.3f}) rectangle ({x1:.3f},{y1:.3f});")
    o.append(f"{indent}  \\fill[{color}] ({x0:.3f},{y0:.3f}) rectangle "
             f"({x1:.3f},{y1:.3f});")
    o.append(f"{indent}  \\foreach \\t in {{"
             + ",".join(f"{i * step:.3f}" for i in range(n)) + "}{")
    o.append(f"{indent}    \\draw[white, line width=0.35pt] "
             f"(\\t,{y0:.3f}) -- (\\t+{h:.3f},{y1:.3f});")
    o.append(f"{indent}  }}")
    o.append(f"{indent}\\end{{scope}}")
    o.append(f"{indent}\\draw[{color}, line width=0.4pt] ({x0:.3f},{y0:.3f}) "
             f"rectangle ({x1:.3f},{y1:.3f});")
    return "\n".join(o)


def panel_a():
    """Feasibility: area surplus vs covering bound (unchanged from v1)."""
    fp = os.path.join(ML, "results_feasibility.json")
    if not os.path.exists(fp):
        return "% panel (a): results_feasibility.json missing"
    feas = json.load(open(fp, encoding="utf-8"))
    cfg = feas["config"]
    rb = feas["region_bound"]
    sur = feas["surplus"]
    K = int(cfg["K"])
    R = float(cfg["R_cov"])
    area = float(sur["field_area_m2"])
    N_pub = int(rb["N_available"])
    N_bound = int(rb["N_required_for_corners"])
    sigma_pub = float(sur["surplus_sigma"])
    sigma = lambda n: n * math.pi * R ** 2 / (K * area)
    N_area = K * area / (math.pi * R ** 2)
    xmin, xmax = 2.8, 9.3
    ymin, ymax = 0.0, 3.05
    xs = [3, 4, 5, 6, 7, 8, 9]
    ys = [sigma(n) for n in xs]
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
    o.append(f"  \\addplot[draw=none, fill={RED}!8, forget plot] "
             f"coordinates {{({N_area:.3f},{ymin:.2f}) "
             f"({N_bound - 0.001:.3f},{ymin:.2f}) "
             f"({N_bound - 0.001:.3f},{ymax:.2f}) "
             f"({N_area:.3f},{ymax:.2f})}} \\closedcycle;")
    o.append(f"  \\addplot[gray!65, dashed, line width=0.9pt, forget plot] "
             f"coordinates {{({xmin:.2f},1) ({xmax:.2f},1)}};")
    o.append(f"  \\addplot[{RED}, dashed, line width=1.1pt, forget plot] "
             f"coordinates {{({N_bound},{ymin:.2f}) "
             f"({N_bound},{ymax:.2f})}};")
    coords = " ".join(f"({n},{y:.4f})" for n, y in zip(xs, ys))
    o.append(f"  \\addplot[color={BLUE}, thick, mark=*, mark size=1.7pt, "
             f"mark options={{fill={BLUE}}}, forget plot] coordinates "
             f"{{{coords}}};")
    o.append(f"  \\addplot[only marks, mark=o, mark size=2.6pt, "
             f"color={RED}, mark options={{fill=white, line width=1.1pt}}, "
             f"forget plot] coordinates "
             f"{{({N_pub},{sigma_pub:.4f})}};")
    o.append(f"  \\addplot[only marks, mark=*, mark size=2.4pt, "
             f"color={BLUE}, mark options={{fill={BLUE}}}, forget plot] "
             f"coordinates {{({N_bound},{sigma(N_bound):.4f})}};")
    o.append(f"  \\node[anchor=north west, font=\\tiny, align=left] at "
             f"(axis cs:{N_pub + 0.08:.2f},{sigma_pub - 0.06:.3f}) "
             f"{{published\\\\$\\sigma={sigma_pub:.3f}$}};")
    o.append(f"  \\node[anchor=south east, font=\\tiny] at "
             f"(axis cs:{N_bound - 0.08:.2f},{sigma(N_bound) + 0.06:.3f}) "
             f"{{corrected $N={N_bound}$}};")
    o.append(f"  \\node[rotate=90, anchor=south, font=\\tiny, text={RED}] at "
             f"(axis cs:{N_bound},1.05) {{$N\\geq 4K={N_bound}$}};")
    o.append(f"  \\node[anchor=south west, font=\\tiny] at "
             f"(axis cs:{xmin + 0.18:.2f},1.25) {{$\\sigma=1$}};")
    o.append(f"  \\node[anchor=south west, font=\\tiny] at "
             f"(axis cs:{N_area + 0.10:.2f},{ymax - 0.06:.2f}) "
             f"{{the two criteria disagree}};")
    o.append("\\end{axis}")
    return "\n".join(o)


def panel_b():
    """Corrected comparison: learner (0.951) vs rule (0.923) vs oracle (1)."""
    ck_ours = num("tokEgoShapeCK")
    ck_rule = num("tokRuleReactiveLocalCK")
    ck_oracle = 1.0
    if ck_ours is None or ck_rule is None:
        return "% panel (b): midsem_numbers.tex missing"
    diff = ck_ours - ck_rule
    scale = 4.20
    x0 = 0.05
    w_ours = scale * ck_ours
    w_rule = scale * ck_rule
    x_ours = x0 + w_ours
    x_rule = x0 + w_rule
    x_ora = x0 + scale * ck_oracle
    o = []
    o.append(f"\\begin{{scope}}[shift={{({X_B:.2f}cm,0cm)}}]")
    o.append(r"  \node[box, fill=" + BLUE + r"!9, draw=" + BLUE + r","
             r" minimum width=1.55cm, minimum height=0.40cm, inner sep=1pt]"
             r" (actor) at (2.00,3.30) {shared actor $\pi_\theta$};")
    o.append(r"  \draw[arr] (actor.east) -- (3.45,3.30);")
    o.append(r"  \node[align=center, font=\tiny, text=" + RED + r"] "
             r"(hardlbl) at (3.50,2.34) {connectivity mask\\reserve UAV\\"
             r"charging\\\emph{not learned}};")
    o.append(r"  \draw[arr] (hardlbl.north) -- (3.45,3.10);")
    o.append(hatched(x0, 1.20, x_ours, 1.34, BLUE))
    o.append(rf"  \node[anchor=south west, font=\tiny] at ({x0:.2f},1.36) "
             rf"{{CTDE MAPPO}};")
    o.append(rf"  \node[anchor=west, font=\tiny] at ({x_ours + 0.08:.2f},1.27) "
             rf"{{{ck_ours:.3f}}};")
    o.append(rf"  \filldraw[fill=gray!55, draw=gray!70, line width=0.4pt] "
             rf"({x0:.2f},0.40) rectangle ({x_rule:.2f},0.54);")
    o.append(rf"  \node[anchor=north west, font=\tiny] at ({x0:.2f},0.36) "
             rf"{{unprivileged reactive rule}};")
    o.append(rf"  \node[anchor=north, font=\tiny] at ({x_rule:.2f},0.38) "
             rf"{{{ck_rule:.3f}}};")
    col = GREEN if diff >= 0 else RED
    x_lo, x_hi = min(x_ours, x_rule), max(x_ours, x_rule)
    o.append(rf"  \draw[{col}, line width=0.9pt, <->] ({x_lo:.2f},0.90) -- "
             rf"({x_hi:.2f},0.90);")
    o.append(rf"  \node[anchor=north, font=\tiny, text={col}, yshift=-1pt] at "
             rf"({(x_ours + x_rule) / 2:.2f},0.88) "
             rf"{{learner minus rule {diff:+.3f}}};")
    o.append(rf"  \draw[black, dashed, line width=1.0pt] ({x_ora:.2f},0.22) "
             rf"-- ({x_ora:.2f},1.16);")
    o.append(rf"  \node[anchor=west, font=\tiny] at ({x_ora + 0.04:.2f},1.16) "
             rf"{{{ck_oracle:.3f}}};")
    o.append("\\end{scope}")
    return "\n".join(o)


def panel_c():
    """Stress split: zero-shot learner minus rule per regime."""
    sp = os.path.join(ML, "runs", "stress_eval", "stress_eval.json")
    if not os.path.exists(sp):
        return "% panel (c): stress_eval.json missing"
    data = json.load(open(sp, encoding="utf-8"))
    regs = data.get("regimes", {})
    order = ["nominal", "small_battery", "low_comm", "clustered",
             "failure", "multi_failure"]
    labels = {"nominal": "nominal", "small_battery": "small battery",
              "low_comm": "low comm", "clustered": "spread start",
              "failure": "failure", "multi_failure": "multi-failure"}
    regimes = []
    for k in order:
        v = regs.get(k)
        if not v:
            continue
        diff = v.get("learner_minus_rule")
        if diff is None:
            continue
        regimes.append((labels.get(k, k), float(diff)))
    n = len(regimes)
    if n == 0:
        return "% panel (c): no stress data"
    diffs = [d for _, d in regimes]
    xmin = math.floor(min(min(diffs), 0.0) * 10) / 10.0 - 0.02
    xmax = math.ceil(max(max(diffs), 0.0) * 10) / 10.0 + 0.02
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
             + ",".join("{" + a + "}" for a, _ in regimes) + "},")
    o.append(r"  xlabel={learner minus best rule (persistent coverage)},")
    o.append(r"  axis x line*=bottom, axis y line*=left, grid=both, "
             r"grid style={gray!20},")
    o.append(r"  tick label style={font=\tiny}, label style={font=\small},")
    o.append(r"  clip=false, enlargelimits=false,]")
    o.append(f"  \\addplot[black, dashed, line width=1.0pt, forget plot] "
             f"coordinates {{(0,{ymin:.2f}) (0,{ymax:.2f})}};")
    for i, (_, diff) in enumerate(regimes):
        y = n - i
        col = GREEN if diff >= 0 else RED
        o.append(f"  \\draw[{col}, line width=1.6pt] "
                 f"(0,{y}) -- ({diff:.3f},{y});")
        o.append(f"  \\addplot[color={col}, line width=2.2pt, forget plot, "
                 f"only marks, mark=*, mark size=1.7pt, "
                 f"mark options={{fill=white, draw=black, line width=0.5pt}}] "
                 f"coordinates {{({diff:.3f},{y})}};")
        o.append(f"  \\node[anchor=south, font=\\tiny] at "
                 f"(axis cs:{diff:.3f},{y + 0.16:.2f}) "
                 f"{{${sgn(diff)}$}};")
    o.append("\\end{axis}")
    return "\n".join(o)


def main():
    a = panel_a()
    b = panel_b()
    c = panel_c()
    frag = "\n".join([
        "% generated by scripts/make_teaser_v2.py -- do not edit",
        "% (a) feasibility certificate | (b) corrected comparison | (c) stress split",
        "\\ifdefined\\uavtheme\\else",
        "  \\IfFileExists{ml_impl/analysis/theme.tex}{\\input{ml_impl/analysis/theme.tex}}{%",
        "  \\IfFileExists{theme.tex}{\\input{theme.tex}}{%",
        "  \\errmessage{the figures need ml_impl/analysis/theme.tex}}}%",
        "\\fi",
        "\\begin{tikzpicture}[font=\\tiny,box/.style={draw,rounded corners=2pt,align=center,inner sep=2pt,font=\\tiny},arr/.style={-{Latex[length=1.6mm]},semithick,uavblue},darr/.style={-{Latex[length=1.6mm]},semithick,dashed,uavpurple}]",
        a, b, c,
        "\\end{tikzpicture}",
    ])
    os.makedirs(ANALYSIS, exist_ok=True)
    open(OUT, "w", encoding="utf-8").write(frag + "\n")
    print("wrote", OUT)
    print("panel c regimes:", len([1 for l in c.splitlines() if "coordinates {{" in l or "\\draw[" in l]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
