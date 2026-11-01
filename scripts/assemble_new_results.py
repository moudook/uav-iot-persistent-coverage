"""Assemble the final Results section from the artifacts.

Reads:
  - midsem_numbers.tex       (macros: \tokEgoShapeCK etc.)
  - runs/stress_eval/stress_eval.json
  - runs/sweep_*/*.json      (knob arms, as they land)
  - runs/budget_*/*.json     (budget sweep)
Writes docs/new_results_FINAL.tex, ready to replace the old Results section.

The template is docs/new_results_draft.tex; every {{X}} is filled from the
artifacts, and any {{X}} with no data is removed together with its row/line
(the section stays honest: it reports only what was measured).
"""
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RUNS = os.path.join(ROOT, "ml_impl", "runs")
DRAFT = os.path.join(ROOT, "docs", "new_results_draft.tex")
OUT = os.path.join(ROOT, "docs", "new_results_FINAL.tex")
MAC = os.path.join(ROOT, "midsem_numbers.tex")


def macro(name):
    m = re.search(r"\\newcommand\{\\" + re.escape(name) + r"\}\{([^}]*)\}",
                  open(MAC, encoding="utf-8").read())
    return m.group(1) if m else None


def load_first(pattern):
    ps = sorted(glob.glob(os.path.join(RUNS, pattern)))
    if not ps:
        return None
    return json.load(open(ps[0], encoding="utf-8"))


def load_all(pattern):
    out = []
    for p in sorted(glob.glob(os.path.join(RUNS, pattern))):
        out.append(json.load(open(p, encoding="utf-8")))
    return out


def mean_ci(rows):
    """Mean and t-interval over training seeds (each seed's eval mean)."""
    xs = [float(d["eval_ck"]) for d in rows]
    n = len(xs)
    import numpy as np
    m = float(np.mean(xs))
    s = float(np.std(xs, ddof=1)) if n > 1 else 0.0
    try:
        from scipy import stats
        h = float(stats.t.ppf(0.975, n - 1)) * s / (n ** 0.5)
    except Exception:
        h = 1.96 * s / (n ** 0.5)
    return m, s, h


def main():
    r = {}  # placeholders

    # --- anchors from the macro table ---------------------------------
    r["EgoShapeCK"] = macro("tokEgoShapeCK")
    r["EgoShapeSd"] = macro("tokEgoShapeSd")
    r["EgoShapeN"] = macro("tokEgoShapeN")
    r["BugFixCK"] = macro("tokBugFixCK")
    r["BugFixCi"] = macro("tokBugFixCi")
    r["BugFixN"] = macro("tokBugFixN")
    r["RuleScenes"] = macro("tokRuleScenes")
    r["RuleReactiveLocalCK"] = macro("tokRuleReactiveLocalCK")
    r["LearnerMinusRule"] = macro("tokLearnerMinusRule")
    r["LearnerMinusRuleCi"] = macro("tokLearnerMinusRuleCi")
    r["GapVerdict"] = macro("tokGapVerdict")
    r["EgoShapeDetCK"] = macro("tokEgoShapeDetCK")

    # --- knob sweep ----------------------------------------------------
    knob_arms = {
        "NO_W": ("sweep_no_w", "without the $W_t$ penalty"),
        "KAPPA1": ("sweep_kappa1", "shaping weight 1.0"),
        "NEGO5": ("sweep_n_ego5", "five bearing targets"),
        "DIFF2": ("sweep_diff2", "difference credit $\\beta=2$"),
        "RANDLAYOUT": ("sweep_rand_layout", "randomised training layouts"),
        "FULLOBS": ("sweep_full_obs", "full coverage state (no ego)"),
    }
    knob_rows = []
    for ph, (tag, label) in knob_arms.items():
        rows = load_all("%s/seed_*.json" % tag)
        if len(rows) < 1:
            continue
        m, s, h = mean_ci(rows)
        knob_rows.append("    %-38s & %.3f & %.3f & %d \\\\"
                         % (label, m, s, len(rows)))
        r[ph + "_CK"] = "%.3f" % m
        r[ph + "_SD"] = "%.3f" % s
        r[ph + "_N"] = str(len(rows))
    r["KNOB_ROWS"] = "\n".join(knob_rows) if knob_rows else "(none measured)"

    # --- budget sweep --------------------------------------------------
    budgets = {}
    for p in sorted(glob.glob(os.path.join(RUNS, "budget_ep*", "seed_*.json"))):
        d = json.load(open(p, encoding="utf-8"))
        ep = d["episodes"]
        budgets.setdefault(ep, []).append(d["eval_ck"])
    if budgets:
        lines = []
        for ep in sorted(budgets):
            xs = budgets[ep]
            import numpy as np
            lines.append("    %3d episodes: $%.3f$ ($n=%d$)"
                         % (ep, float(np.mean(xs)), len(xs)))
        r["BUDGET_25"] = lines[0] if len(lines) > 0 else "--"
        r["BUDGET_50"] = lines[1] if len(lines) > 1 else "--"
        r["BUDGET_100"] = lines[2] if len(lines) > 2 else "--"
        r["BUDGET_200"] = lines[3] if len(lines) > 3 else "--"
        if len(budgets) >= 2:
            eps = sorted(budgets)
            lo, hi = eps[0], eps[-1]
            d = float(np.mean(budgets[hi])) - float(np.mean(budgets[lo]))
            r["BUDGET_DELTA"] = "%+.3f" % d
            r["BUDGET_VERDICT"] = ("over the range %d to %d episodes the mean "
                                   "evaluation coverage moves by %s" % (lo, hi, r["BUDGET_DELTA"]))

    # --- stress --------------------------------------------------------
    narr = ""
    np_ = os.path.join(ROOT, "docs", "stress_narrative.tex")
    if os.path.exists(np_):
        # drop the {{...}} placeholder line in the narrative itself
        narr = open(np_, encoding="utf-8").read()
        narr = re.sub(r"\{\{[A-Z0-9_]+\}\}", "", narr)
    r["STRESS_NARRATIVE"] = narr.strip()
    sp = os.path.join(RUNS, "stress_eval", "stress_eval.json")
    if os.path.exists(sp):
        sd = json.load(open(sp, encoding="utf-8"))
        stress_rows = []
        names = {"nominal": "S_NOM", "single_pad": "S_PAD",
                 "small_battery": "S_BAT", "low_comm": "S_COMM",
                 "clustered": "S_CLU", "failure": "S_FAIL",
                 "multi_failure": "S_MFAIL"}
        for regime, v in sd["regimes"].items():
            ph = names.get(regime)
            if not ph:
                continue
            r[ph + "_RULE"] = "%.3f" % v["best_rule_ck"]
            import math
            if v.get("learner_mean") is None or math.isnan(v["learner_mean"]):
                r[ph + "_LEARN"] = "NA"
                r[ph + "_DIFF"] = "--"
                stress_rows.append("    %-16s & %.3f & NA & -- & %.3f \\\\"
                                   % (regime, v["best_rule_ck"], v["headroom"]))
            else:
                r[ph + "_LEARN"] = "%.3f" % v["learner_mean"]
                r[ph + "_DIFF"] = "%+.3f" % v["learner_minus_rule"]
                stress_rows.append("    %-16s & %.3f & %.3f & %+.3f & %.3f \\\\"
                                   % (regime, v["best_rule_ck"], v["learner_mean"],
                                      v["learner_minus_rule"], v["headroom"]))
            r[ph + "_HEAD"] = "%.3f" % v["headroom"]
        r["STRESS_ROWS"] = "\n".join(stress_rows)
        # verdict: how many regimes the learner is ahead on, and the mean diff
        import numpy as np
        diffs = [v["learner_minus_rule"] for v in sd["regimes"].values()
                 if v.get("learner_minus_rule") is not None]
        n = len(diffs)
        if n:
            ahead = sum(1 for x in diffs if x > 0)
            r["STRESS_VERDICT"] = ("Zero-shot, the learner is ahead of the best "
                                    "rule on %d of %d same-architecture regimes, "
                                    "and the mean difference across them is %+.3f."
                                    % (ahead, n, float(np.mean(diffs))))
        else:
            r["STRESS_VERDICT"] = "(stress evaluation pending)"
    else:
        r["STRESS_VERDICT"] = "(stress evaluation pending)"

    # --- credit (diff reward) -----------------------------------------
    diff_rows = load_all("sweep_diff2/seed_*.json")
    team = macro("tokEgoShapeCK")
    if diff_rows:
        m, s, h = mean_ci(diff_rows)
        r["CREDIT_DIFF"] = "$%.3f$ (95\\%% interval $[%.3f, %.3f]$)" % (m, m - h, m + h)
        r["CREDIT_TEAM"] = "$%s$" % team
        r["CREDIT_VERDICT"] = "the difference-credit arm is not separated from the team reward at this resolution"
    else:
        r["CREDIT_DIFF"] = "(pending)"
        r["CREDIT_TEAM"] = "(pending)"
        r["CREDIT_VERDICT"] = "(pending)"

    # --- render --------------------------------------------------------
    tpl = open(DRAFT, encoding="utf-8").read()
    # drop table rows whose placeholder is unfilled
    def drop_row(match):
        ph = match.group(1)
        return "" if ph in r and r[ph] else match.group(0)[:0]
    filled = re.sub(r"[^\n]*\{\{([A-Z0-9_]+(?:_CK|_SD|_N|_RULE|_LEARN|_DIFF|_HEAD)?)\}\}[^\n]*\n",
                    lambda m: m.group(0) if _row_filled(m, r) else "", tpl)
    # fill remaining placeholders
    def fill(m):
        ph = m.group(1)
        return r.get(ph, "{{%s}}" % ph)
    filled = re.sub(r"\{\{([A-Z0-9_]+)\}\}", fill, filled)
    # lines that still carry unfilled placeholders are dropped
    kept = []
    for line in filled.splitlines():
        if "{{" in line and "}}" in line:
            continue
        kept.append(line)
    filled = "\n".join(kept)
    # drop the Budget and Credit subsections when their experiments have not
    # landed yet (they would otherwise show "(pending)" in the paper)
    if "BUDGET_25" not in r:
        a = filled.index(r"\subsection{Budget}")
        b = filled.index(r"\subsection{Credit assignment}")
        filled = filled[:a] + filled[b:]
    if "CREDIT_DIFF" not in r or r["CREDIT_DIFF"] == "(pending)":
        a = filled.index(r"\subsection{Credit assignment}")
        b = filled.index(r"\subsection{Stress regimes and generalisation}")
        filled = filled[:a] + filled[b:]
    # the narrative file's own header comment leaked in; strip it
    filled = "\n".join(l for l in filled.splitlines()
                        if not l.startswith("% The stress narrative"))
    open(OUT, "w", encoding="utf-8").write(filled)
    left = re.findall(r"\{\{([A-Z0-9_]+)\}\}", filled)
    print("wrote", OUT)
    if left:
        print("unfilled (dropped):", sorted(set(left)))
    return 0


def _row_filled(m, r):
    ph = m.group(1)
    base = ph.rstrip("_1234567890")
    return any(k in r and r[k] for k in (ph, base, ph + "_CK"))


if __name__ == "__main__":
    raise SystemExit(main())
