"""
Generate the LaTeX for the results tables from the artefacts.

The point of doing this mechanically is that the tables and the prose come
from the same numbers: there is no path by which a digit in the text can
differ from the digit in the CSV.

Every table is set in the project's shared table style, which lives once
in analysis/theme_tables.tex: the highlighted row (\\tblHl), the two-level
group header (\\tblGroup) and the note line under a table (\\tblNote).
Each generated table bootstraps that file in the same way the figure
fragments bootstrap analysis/theme.tex, so the style cannot differ
between the paper and the report, and a paper whose preamble has not
been wired yet still compiles.

Run:  python analysis/make_tables.py
"""

from __future__ import annotations

import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ML = os.path.dirname(HERE)
OUT = os.path.join(HERE, "tables.tex")

# The display names.  None of them carries a weight of its own: the row
# the reader is meant to look at is bolded precisely because it is the
# highlighted one (theme_tables.tex pairs the fill with the weight), and
# which row that is comes out of the numbers, not out of this map.
NAMES = {
    "Full": "Full (proposed)",
    "no-criticality": "no-criticality term",
    "no-degraded": "no-degraded-service term",
    "no-energy-cost": "no-energy-cost term",
    "no-undercoverage": "no-under-coverage term",
    "no-reserve": "no-reserve UAV",
    "no-arbitration": "no-charging arbitration",
    "no-mask": "no-action mask",
    "no-agent-id": "no agent identity",
    "with-map": "with coverage map",
    "no-map": "no coverage map",
    "no-pad-bearing": "no pad bearing",
    "VanillaMAPPO": "Vanilla MAPPO",
}
ORDER = list(NAMES.keys())

# The shared table style, bootstrapped by every table: the marker says
# whether analysis/theme_tables.tex is already loaded (the report loads
# it in its preamble), and the file is looked up relative to the paper's
# directory first, then relative to the tables' own directory, so an
# extracted fragment still typesets.  The same idiom the figure
# fragments use for analysis/theme.tex.
THEME_BLOCK = (
    "% the shared table style: analysis/theme_tables.tex, the file the\n"
    "% report's preamble loads; see that file's header comment\n"
    "\\ifdefined\\tbltheme\\else\n"
    "  \\IfFileExists{ml_impl/analysis/theme_tables.tex}"
    r"{\input{ml_impl/analysis/theme_tables.tex}}{%" "\n"
    "  \\IfFileExists{theme_tables.tex}"
    r"{\input{theme_tables.tex}}{%" "\n"
    "  \\errmessage{the tables need ml_impl/analysis/theme_tables.tex}}}\n"
    "\\fi\n"
)


def fmt(v, nd=3):
    try:
        return f"{float(v):.{nd}f}"
    except (TypeError, ValueError):
        return "--"


def load_csv(name):
    p = os.path.join(ML, name)
    if not os.path.exists(p):
        return None
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_json(name):
    p = os.path.join(HERE, name)
    if not os.path.exists(p):
        return []
    return json.load(open(p, encoding="utf-8"))


def ck_cell(r, nd=3):
    """The coverage with its spread, when the row has one.

    A learned controller is trained several times, so its row carries the
    seed-to-seed spread of CK.  The rule baselines are deterministic, so
    their rows carry the spread over the evaluation scenes instead; the
    cell says which spread it is in the caption.
    """
    v = fmt(r.get("CK"), nd)
    s = r.get("CK_std")
    if s in (None, ""):
        return v
    return f"{v}\\,$\\pm$\\,{fmt(s, nd)}"


def _b(cell):
    """One bolded cell of the highlighted row.

    theme_tables.tex pairs the row's fill with the row's weight: the
    fill is \\tblHl's, the weight is this.  The $\\pm$ inside a spread
    cell keeps its own weight, which is right: the numbers are what the
    weight is for.
    """
    return r"\textbf{" + cell + "}"


def _best(pool, key="CK"):
    """The member of the pool with the largest value of the key, by row
    identity, or None.

    Every highlighted row in every table comes out of this one function
    rather than out of a hard-coded name, so the highlight follows the
    numbers when they change.  Rows whose key is not a number are
    skipped, and a pool where nothing is measurable highlights nothing.
    """
    best, bestv = None, float("-inf")
    for r in pool:
        try:
            v = float(r.get(key))
        except (TypeError, ValueError):
            continue
        if v > bestv:
            best, bestv = r, v
    return best


def _row(cells, hl=False):
    """One data row; the highlighted one starts with \\tblHl and is bold."""
    first = r"\tblHl " if hl else ""
    body = " & ".join(_b(c) if hl else c for c in cells)
    return first + body + " \\\\"


def grouped_head(stubs, groups, tails):
    """The two-level header: a group row above a sub-head row.

    `stubs' are the left-hand label columns, whose headers sit on the
    sub-head row under the empty cells of the group row, the way the
    reference table puts `Mask' under the `Targets' overhang.  `groups'
    are (title, sub-heads) pairs: each is a \\tblGroup over its own
    span, with a \\cmidrule over the same span, written from the same
    span so the two cannot drift apart.  `tails' are the single columns
    that belong to no group: their headers sit on the group row (the
    reference table's `Top-1' column) and the sub-head row is empty
    under them.
    """
    n_stub = len(stubs)
    pos = n_stub
    top = [""] * n_stub
    rules = []
    for title, subs in groups:
        start = pos + 1
        pos += len(subs)
        top.append("\\tblGroup{%d}{%s}" % (len(subs), title))
        rules.append("\\cmidrule(lr){%d-%d}" % (start, pos))
    top += tails
    sub = list(stubs) + [s for _t, subs in groups for s in subs]
    sub += [""] * len(tails)
    out = [" & ".join(top) + " \\\\"]
    if rules:
        out.append(" ".join(rules))
    out.append(" & ".join(sub) + " \\\\")
    return out


# The tables live in one column of a two-column IEEE paper, which is
# narrow, so the column separation is tightened.  A table that does not fit
# is an overfull box, and an overfull box in a submitted paper is a defect.
# The two-level head and the bolded highlight row are a little wider than
# the flat head was, so the separation is tightened by half a point to
# keep the widest table inside the column.
NARROW = r"\setlength{\tabcolsep}{2.5pt}"


def table_main(rows, learned=None):
    lines = []
    # The caption states the seed count and the meaning of the $\pm$, and
    # both are read from the data: a caption that says "five times" when
    # the table was measured eight times is a caption that lies, and a
    # caption that promises the rules a $\pm$ the table does not print is
    # the same kind of lie.
    n_seeds = 0
    if learned:
        try:
            n_seeds = int(learned.get("MAPPO", {}).get("train_seeds", 0) or 0)
        except Exception:
            n_seeds = 0
    if not n_seeds:
        for r in rows:
            if r.get("model") == "MAPPO" and r.get("train_seeds"):
                n_seeds = int(r["train_seeds"])
    rule_models = ("Fixed", "Greedy", "Reactive", "Reactive-local", "Oracle")
    rules_have_std = any(r.get("model") in rule_models
                          and r.get("CK_std") not in (None, "")
                          for r in rows)
    if n_seeds:
        seed_clause = (f"The learned controller is trained {n_seeds} times "
                       f"and its row is the mean over those {n_seeds} runs, "
                       f"with the $\\pm$ the seed-to-seed spread")
    else:
        seed_clause = ("The learned controller's row is the mean over its "
                       "training runs, with the $\\pm$ the seed-to-seed spread")
    if rules_have_std:
        rule_clause = ("the rule baselines are deterministic, and their "
                       "$\\pm$ is the spread over the evaluation scenes")
    else:
        rule_clause = ("the rule baselines are deterministic and carry no "
                       "spread of their own")
    lines.append(r"\begin{table}[t]")
    lines.append(THEME_BLOCK)
    lines.append(r"\caption{Base comparison on the corrected configuration.  "
                 + seed_clause + "; " + rule_clause + ".  "
                 r"``Unexec.'' is the number of sampled actions that the "
                 r"safety filter or the joint projection did not execute, "
                 r"which is the size of the gap between the policy gradient "
                 r"and the trajectory.  The two learned baselines are "
                 r"implementations of the method families of "
                 r"Table~\ref{tab:comparison}, not reproductions of the "
                 r"cited papers.}")
    lines.append(r"\label{tab:results_main}")
    lines.append(r"\centering")
    lines.append(r"\scriptsize")
    lines.append(NARROW)

    # The highlighted row: the best of the LEARNED controllers by the
    # table's own key, CK.  The rule baselines are the thing the learned
    # controllers are compared against, and the oracle is the ceiling
    # reference, so neither belongs to the candidate pool; the choice
    # itself is made on the printed numbers, so the highlight follows
    # them when they change.
    LEARNED = ("MAPPO", "MAPPO-argmax", "Independent DQN (value-based)",
               "Masked PPO, local critic")
    pool = [r for r in rows if r.get("model") in LEARNED]
    if learned:
        pool = pool + list(learned)
    best = _best(pool)
    hl = lambda r: best is not None and r == best

    head = grouped_head(["Model"],
                        [("Task metrics",
                          ["CK", "AG", "SC", r"CovDef\textsuperscript{*}"])],
                        ["Unexec.", "Energy"])
    lines.append(r"\begin{tabular}{@{}lcccccc@{}}")
    lines.append(r"\toprule")
    lines += head
    lines.append(r"\midrule")
    order = ["Fixed", "Greedy", "Reactive", "Reactive-local"]
    by_model = {r["model"]: r for r in rows}
    for name in order:
        r = by_model.get(name)
        if r is None:
            continue
        disp = {"Reactive-local": r"Reactive (local assignment)"}.get(name, name)
        lines.append(_row(
            [disp, ck_cell(r), fmt(r.get('AG')), fmt(r.get('SC')),
             fmt(r.get('CovIntegral')), fmt(r.get('UnexecutedActions'), 2),
             fmt(r.get('Energy'), 0)]))
    if learned:
        # the display names are shortened to fit the column; the full names
        # are in the prose and in the artefact
        SHORT = {"Independent DQN (value-based)": "Independent DQN",
                 "Masked PPO, local critic": "Masked PPO (local critic)"}
        for r in learned:
            name = SHORT.get(r["model"], r["model"])
            lines.append(_row(
                [name, ck_cell(r), fmt(r.get('AG')), fmt(r.get('SC')),
                 fmt(r.get('CovIntegral')), "--", "--"]))
    for name, disp in (("VanillaMAPPO", "Vanilla MAPPO"),
                       ("MAPPO", "MAPPO (proposed)"),
                       ("MAPPO-argmax", "MAPPO (argmax)")):
        r = by_model.get(name)
        if r is None:
            continue
        lines.append(_row(
            [disp, ck_cell(r), fmt(r.get('AG')), fmt(r.get('SC')),
             fmt(r.get('CovIntegral')), fmt(r.get('UnexecutedActions'), 2),
             fmt(r.get('Energy'), 0)], hl=hl(r)))
    r = by_model.get("Oracle (ceiling)")
    if r is not None:
        lines.append(r"\midrule")
        lines.append(
            f"Oracle (ceiling) & {fmt(r.get('CK'))} & {fmt(r.get('AG'))} & "
            f"{fmt(r.get('SC'))} & {fmt(r.get('CovIntegral'))} & -- & 0 \\\\")
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    # The note the starred column points at (theme_tables.tex \tblNote):
    # CovDef is the one acronym this caption does not spell out.
    lines.append(r"\tblNote{* CovDef is the time-averaged coverage deficit.}")
    lines.append(r"\end{table}")
    return "\n".join(lines)


def _per_seed_ck(row):
    v = row.get("per_seed_CK", "") if row else ""
    if not v:
        return []
    out = []
    for part in str(v).split(";"):
        try:
            out.append(float(part))
        except ValueError:
            return []
    return out


def table_abl(rows, label, caption):
    by = {r["model"]: r for r in rows}
    full = by.get("Full")
    fs = _per_seed_ck(full) if full else []
    # The highlighted row is the full configuration: the row against which
    # the table's own key, the paired $\Delta$CK column, is measured.  It
    # is found through the same lookup the $\Delta$CK arithmetic uses
    # (the row whose per-seed CK vector every difference subtracts), so
    # the highlight and the differencing cannot disagree: if the
    # artefact's reference configuration is relabelled, both follow it.
    lines = []
    lines.append(r"\begin{table}[t]")
    lines.append(THEME_BLOCK)
    lines.append(rf"\caption{{{caption}}}")
    lines.append(rf"\label{{{label}}}")
    lines.append(r"\centering")
    lines.append(r"\scriptsize")
    lines.append(NARROW)
    head = grouped_head(["Variant"],
                        [("Task metrics", ["CK", "AG", "SC", "CovDef"])],
                        ["Stranded", r"$\Delta$CK"])
    lines.append(r"\begin{tabular}{@{}lcccccc@{}}")
    lines.append(r"\toprule")
    lines += head
    lines.append(r"\midrule")
    for name in ORDER:
        r = next((x for x in rows if x["model"] == name), None)
        if r is None:
            continue
        # the paired difference: the variants share the training seeds, so
        # the difference is measured on the same training runs
        d = "--"
        vs = _per_seed_ck(r)
        if fs and len(vs) == len(fs):
            diffs = [fs[i] - vs[i] for i in range(len(fs))]
            d = f"{sum(diffs)/len(diffs):+.3f}"
        lines.append(_row(
            [NAMES[name], ck_cell(r), fmt(r.get('AG')), fmt(r.get('SC')),
             fmt(r.get('CovIntegral')), fmt(r.get('Stranded'), 1), d],
            hl=(full is not None and r == full)))
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(r"\end{table}")
    return "\n".join(lines)


def table_scen(rows):
    """One row per scenario: the mean over that scenario's variants."""
    # the research questions are plain strings in the artefact; the ones that
    # are symbols have to be set in math mode, or the underscore is read as
    # a subscript and the table does not compile
    QMAP = {"R_comm": r"$R_{\mathrm{comm}}$",
            "R_cov": r"$R_{\mathrm{cov}}$",
            "B_max": r"$B_{\max}$",
            "N": r"$N$",
            "M": r"$M$",
            "S": r"$S$"}
    by = {}
    for r in rows:
        by.setdefault(r["scenario"], []).append(r)
    lines = []
    lines.append(r"\begin{table}[t]")
    lines.append(THEME_BLOCK)
    lines.append(r"\caption{Scenario matrix.  Each row is the mean over the "
                 r"variants of that scenario; \emph{M} is the proposed "
                 r"controller, \emph{R} the reactive heuristic and "
                 r"\emph{RL} the same rule without its global access to the "
                 r"coverage state, which is the stronger of the two rules on "
                 r"the base configuration.}")
    lines.append(r"\label{tab:results_scen}")
    lines.append(r"\centering")
    lines.append(r"\scriptsize")
    lines.append(NARROW)
    lines.append(r"\begin{tabular}{@{}llcccccc@{}}")
    lines.append(r"\toprule")
    lines += grouped_head(["ID", "Variable"],
                          [("CK", ["M", "R", "RL"]),
                           ("SC", ["M", "R", "RL"])], [])
    lines.append(r"\midrule")
    # The highlighted row: the scenario in which the learned controller
    # comes closest to the stronger of the two rules, computed from the
    # same columns the table prints.  In a matrix read across the rows,
    # the row the reader looks for first is this one.
    best_sid, best_marg = None, float("-inf")
    for sid, rs in by.items():
        def mean(key, rs=rs):
            vals = [float(x[key]) for x in rs
                    if x.get(key) not in (None, "")]
            return sum(vals) / len(vals) if vals else float("nan")

        marg = mean("mappo_CK") - max(mean("react_CK"), mean("reactlocal_CK"))
        if marg > best_marg:
            best_sid, best_marg = sid, marg
    for sid in sorted(by):
        rs = by[sid]
        q = QMAP.get(rs[0]["question"], rs[0]["question"])

        def mean(key):
            vals = [float(x[key]) for x in rs
                    if x.get(key) not in (None, "")]
            return fmt(sum(vals) / len(vals)) if vals else "--"

        lines.append(_row(
            [sid, q, mean('mappo_CK'), mean('react_CK'),
             mean('reactlocal_CK'), mean('mappo_SC'), mean('react_SC'),
             mean('reactlocal_SC')],
            hl=(sid == best_sid)))
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(r"\end{table}")
    return "\n".join(lines)


def main():
    parts = []
    main_rows = load_csv("results_main.csv")
    if main_rows:
        parts.append(table_main(main_rows,
                                load_csv("results_learned_baselines.csv")))
    abl = load_csv("results_ablation.csv")
    if abl:
        parts.append(table_abl(
            abl, "tab:results_abl",
            "Component ablation on the feasible base configuration.  Every "
            "variant is trained on the same configuration with the same "
            "budget and from the same training seeds, and differs from the "
            "full configuration in exactly one component.  The $\\pm$ is the "
            "seed-to-seed spread of the training runs, and $\\Delta$CK is the "
            "paired difference from the full configuration, measured on the "
            "same training runs."))
    stress = load_csv("results_ablation_stress.csv")
    if stress:
        parts.append(table_abl(
            stress, "tab:results_ablstress",
            "Component ablation on the S8 combined-stress scenario (a failure "
            "at step 500, one charging pad, $B=15$\\,kJ, "
            "$R_{\\mathrm{comm}}=30$\\,m, $R_{\\mathrm{cov}}=30$\\,m)."))
    scen = load_csv("results_scenarios.csv")
    if scen:
        parts.append(table_scen(scen))
    obs = os.path.join(HERE, "ab_observation.json")
    if os.path.exists(obs):
        rows = json.load(open(obs, encoding="utf-8"))
        arms = [r for r in rows if r.get("kind") != "baseline"]
        # the highlighted arm: the best of the measured arms by the
        # table's key, computed here so the highlight follows the
        # measurements
        best = _best(arms)
        lines = [r"\begin{table}[t]",
                 THEME_BLOCK,
                 r"\caption{What the local observation must contain.  "
                 r"``Distinct'' is the number of distinct actions the "
                 r"deterministic (argmax) policy selects across the eight "
                 r"UAVs, and ``Spread'' is the mean distance of a UAV from "
                 r"the swarm centroid.}",
                 r"\label{tab:results_obs}", r"\centering", r"\scriptsize",
                 NARROW,
                 r"\begin{tabular}{@{}lccccc@{}}", r"\toprule"]
        lines += grouped_head(
            ["Observation"],
            [("Task metrics", ["CK", "AG", "SC"])],
            ["Distinct", "Spread (m)"])
        lines.append(r"\midrule")
        for r in rows:
            if r.get("kind") == "baseline":
                continue
            name = r["arm"].split(":")[0]
            lines.append(_row(
                [name, ck_cell(r), fmt(r.get('AG')), fmt(r.get('SC')),
                 fmt(r.get('distinct_actions'), 2) + " / 8",
                 fmt(r.get('mean_spread_m'), 1)],
                hl=(best is not None and r == best)))
        lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
        parts.append("\n".join(lines))
    en = os.path.join(HERE, "ab_energy_management.json")
    if os.path.exists(en):
        rows = json.load(open(en, encoding="utf-8"))
        best = _best(rows)
        # the note: the table prints the arms as letters, and the
        # artefact carries the letters' full names, so the note is
        # written from the artefact rather than pasted by hand
        letters = "; ".join(
            "{}: {}".format(r["arm"].partition(":")[0].strip(),
                            r["arm"].partition(":")[2].strip())
            for r in rows)
        lines = [r"\begin{table}[t]",
                 THEME_BLOCK,
                 r"\caption{The energy-management diagnosis.  ``Stranded'' is "
                 r"the mean number of UAVs that run out of energy away from a "
                 r"pad per episode, and ``Returns'' the mean number of "
                 r"return-to-charge transitions.}",
                 r"\label{tab:results_energy}", r"\centering", r"\scriptsize",
                 NARROW,
                 r"\begin{tabular}{@{}lccccc@{}}", r"\toprule"]
        lines += grouped_head(
            ["Variant"], [("Task metrics", ["CK", "AG", "SC"])],
            ["Stranded", "Returns"])
        lines.append(r"\midrule")
        for r in rows:
            lines.append(_row(
                [r['arm'].split(':')[0], fmt(r.get('CK')), fmt(r.get('AG')),
                 fmt(r.get('SC')), fmt(r.get('stranded_per_episode'), 1),
                 fmt(r.get('return_events_per_episode'), 1)],
                hl=(best is not None and r == best)))
        lines += [r"\bottomrule", r"\end{tabular}",
                  r"\tblNote{* " + letters + ".}",
                  r"\end{table}"]
        parts.append("\n".join(lines))
    mres = os.path.join(HERE, "ab_map_resolution.json")
    if os.path.exists(mres):
        rows = json.load(open(mres, encoding="utf-8"))
        lines = [r"\begin{table}[t]",
                 THEME_BLOCK,
                 r"\caption{The resolution of the broadcast coverage-map "
                 r"summary.  A finer summary does not help: the swarm's "
                 r"spread contracts, because the policy follows the "
                 r"deficit instead of dividing the work.}",
                 r"\label{tab:results_mapres}", r"\centering", r"\scriptsize",
                 NARROW,
                 r"\begin{tabular}{@{}lcccc@{}}", r"\toprule",
                 r"Grid & CK & AG & SC & Spread (m) \\", r"\midrule"]
        for r in rows:
            lines.append(
                f"$G={r['grid']}$ & {fmt(r.get('CK'))} & {fmt(r.get('AG'))} & "
                f"{fmt(r.get('SC'))} & {fmt(r.get('mean_spread_m'), 1)} \\\\")
        lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
        parts.append("\n".join(lines))
    cr = load_json("ab_credit.json")
    if cr:
        best = _best(cr)
        no_energy = all(not r.get("Energy") for r in cr)
        lines = [r"\begin{table}[t]",
                 THEME_BLOCK,
                 r"\caption{The cheapest test of the credit-assignment "
                 r"hypothesis.  The two arms differ in the learner that "
                 r"produces the advantage: a parameter-shared actor with a "
                 r"centralised critic, or a per-agent actor with a per-agent "
                 r"local critic.  A per-agent \emph{baseline} changes the "
                 r"variance of the advantage, not its signal, which remains "
                 r"the shared team reward.}",
                 r"\label{tab:results_credit}", r"\centering", r"\scriptsize",
                 NARROW,
                 r"\begin{tabular}{@{}lccccc@{}}", r"\toprule"]
        lines += grouped_head(
            ["Learner"],
            [("Task metrics", ["CK", "AG", "SC", "CovIntegral"])],
            ["Energy (J)"])
        lines.append(r"\midrule")
        for r in cr:
            name = r["arm"].split(":")[0]
            lines.append(_row(
                [name, ck_cell(r), fmt(r.get('AG')), fmt(r.get('SC')),
                 fmt(r.get('CovIntegral')), fmt(r.get('Energy'))],
                hl=(best is not None and r == best)))
        lines += [r"\bottomrule", r"\end{tabular}"]
        if no_energy:
            # the artefact records no energy measurement for these arms;
            # the note is derived from the artefact, so an artefact that
            # one day records it prints it and drops the note
            lines.append(r"\tblNote{* Energy is not recorded in this artefact.}")
        lines += [r"\end{table}"]
        parts.append("\n".join(lines))
    text = "\n\n".join(parts)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(text + "\n")
    print(f"Wrote {OUT} ({len(text)} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
