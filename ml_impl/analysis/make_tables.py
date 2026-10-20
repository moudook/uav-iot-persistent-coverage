"""
Generate the LaTeX for the results tables from the artefacts.

The point of doing this mechanically is that the tables and the prose come
from the same numbers: there is no path by which a digit in the text can
differ from the digit in the CSV.

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

NAMES = {
    "Full": r"\textbf{Full (proposed)}",
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
    "VanillaMAPPO": r"\textbf{Vanilla MAPPO}",
}
ORDER = list(NAMES.keys())


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


# The tables live in one column of a two-column IEEE paper, which is
# narrow, so the column separation is tightened.  A table that does not fit
# is an overfull box, and an overfull box in a submitted paper is a defect.
NARROW = r"\setlength{\tabcolsep}{3pt}"


def table_main(rows, learned=None):
    lines = []
    lines.append(r"\begin{table}[t]")
    lines.append(r"\caption{Base comparison on the corrected configuration.  "
                 r"The learned controller is trained five times and its row "
                 r"is the mean over those five runs, with the $\pm$ the "
                 r"seed-to-seed spread; the rule baselines are "
                 r"deterministic, and their $\pm$ is the spread over the "
                 r"five evaluation scenes.  "
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
    lines.append(r"\begin{tabular}{@{}lcccccc@{}}")
    lines.append(r"\toprule")
    lines.append(r"Model & CK & AG & SC & CovDef & Unexec. & Energy \\")
    lines.append(r"\midrule")
    order = ["Fixed", "Greedy", "Reactive", "Reactive-local"]
    by_model = {r["model"]: r for r in rows}
    for name in order:
        r = by_model.get(name)
        if r is None:
            continue
        disp = {"Reactive-local": r"Reactive (local assignment)"}.get(name, name)
        lines.append(
            f"{disp} & {ck_cell(r)} & {fmt(r.get('AG'))} & "
            f"{fmt(r.get('SC'))} & {fmt(r.get('CovIntegral'))} & "
            f"{fmt(r.get('UnexecutedActions'), 0)} & "
            f"{fmt(r.get('Energy'), 0)} \\\\")
    if learned:
        # the display names are shortened to fit the column; the full names
        # are in the prose and in the artefact
        SHORT = {"Independent DQN (value-based)": "Independent DQN",
                 "Masked PPO, local critic": "Masked PPO (local critic)"}
        for r in learned:
            name = SHORT.get(r["model"], r["model"])
            lines.append(
                f"{name} & {ck_cell(r)} & {fmt(r.get('AG'))} & "
                f"{fmt(r.get('SC'))} & {fmt(r.get('CovIntegral'))} & -- & -- \\\\")
    for name, disp in (("VanillaMAPPO", r"\textbf{Vanilla MAPPO}"),
                       ("MAPPO", r"\textbf{MAPPO (proposed)}"),
                       ("MAPPO-argmax", "MAPPO (argmax)")):
        r = by_model.get(name)
        if r is None:
            continue
        lines.append(
            f"{disp} & {ck_cell(r)} & {fmt(r.get('AG'))} & "
            f"{fmt(r.get('SC'))} & {fmt(r.get('CovIntegral'))} & "
            f"{fmt(r.get('UnexecutedActions'), 0)} & "
            f"{fmt(r.get('Energy'), 0)} \\\\")
    r = by_model.get("Oracle (ceiling)")
    if r is not None:
        lines.append(r"\midrule")
        lines.append(
            f"Oracle (ceiling) & {fmt(r.get('CK'))} & {fmt(r.get('AG'))} & "
            f"{fmt(r.get('SC'))} & {fmt(r.get('CovIntegral'))} & -- & 0 \\\\")
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
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
    lines = []
    lines.append(r"\begin{table}[t]")
    lines.append(rf"\caption{{{caption}}}")
    lines.append(rf"\label{{{label}}}")
    lines.append(r"\centering")
    lines.append(r"\scriptsize")
    lines.append(NARROW)
    lines.append(r"\begin{tabular}{@{}lcccccc@{}}")
    lines.append(r"\toprule")
    lines.append(r"Variant & CK & AG & SC & CovIntegral & Stranded & "
                 r"$\Delta$CK \\")
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
        lines.append(
            f"{NAMES[name]} & {ck_cell(r)} & {fmt(r.get('AG'))} & "
            f"{fmt(r.get('SC'))} & "
            f"{fmt(r.get('CovIntegral'))} & {fmt(r.get('Stranded'), 1)} & "
            f"{d} \\\\")
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
    lines.append(r"& & \multicolumn{3}{c}{CK} & \multicolumn{3}{c}{SC} \\")
    lines.append(r"\cmidrule(lr){3-5}\cmidrule(lr){6-8}")
    lines.append(r"ID & Variable & M & R & RL & M & R & RL \\")
    lines.append(r"\midrule")
    for sid in sorted(by):
        rs = by[sid]
        q = QMAP.get(rs[0]["question"], rs[0]["question"])

        def mean(key):
            vals = [float(x[key]) for x in rs
                    if x.get(key) not in (None, "")]
            return fmt(sum(vals) / len(vals)) if vals else "--"

        lines.append(f"{sid} & {q} & {mean('mappo_CK')} & "
                     f"{mean('react_CK')} & {mean('reactlocal_CK')} & "
                     f"{mean('mappo_SC')} & {mean('react_SC')} & "
                     f"{mean('reactlocal_SC')} \\\\")
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
        lines = [r"\begin{table}[t]",
                 r"\caption{What the local observation must contain.  "
                 r"``Distinct'' is the number of distinct actions the "
                 r"deterministic (argmax) policy selects across the eight "
                 r"UAVs, and ``Spread'' is the mean distance of a UAV from "
                 r"the swarm centroid.}",
                 r"\label{tab:results_obs}", r"\centering", r"\scriptsize",
                 r"\begin{tabular}{@{}lccccc@{}}", r"\toprule",
                 r"Observation & CK & AG & SC & Distinct & Spread (m) \\",
                 r"\midrule"]
        for r in rows:
            if r.get("kind") == "baseline":
                continue
            name = r["arm"].split(":")[0]
            lines.append(
                f"{name} & {ck_cell(r)} & {fmt(r.get('AG'))} & "
                f"{fmt(r.get('SC'))} & "
                f"{fmt(r.get('distinct_actions'), 2)} / 8 & "
                f"{fmt(r.get('mean_spread_m'), 1)} \\\\")
        lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
        parts.append("\n".join(lines))
    en = os.path.join(HERE, "ab_energy_management.json")
    if os.path.exists(en):
        rows = json.load(open(en, encoding="utf-8"))
        lines = [r"\begin{table}[t]",
                 r"\caption{The energy-management diagnosis.  ``Stranded'' is "
                 r"the mean number of UAVs that run out of energy away from a "
                 r"pad per episode, and ``Returns'' the mean number of "
                 r"return-to-charge transitions.}",
                 r"\label{tab:results_energy}", r"\centering", r"\scriptsize",
                 r"\begin{tabular}{@{}lccccc@{}}", r"\toprule",
                 r"Variant & CK & AG & SC & Stranded & Returns \\",
                 r"\midrule"]
        for r in rows:
            lines.append(
                f"{r['arm'].split(':')[0]} & {fmt(r.get('CK'))} & "
                f"{fmt(r.get('AG'))} & "
                f"{fmt(r.get('SC'))} & "
                f"{fmt(r.get('stranded_per_episode'), 1)} & "
                f"{fmt(r.get('return_events_per_episode'), 1)} \\\\")
        lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
        parts.append("\n".join(lines))
    mres = os.path.join(HERE, "ab_map_resolution.json")
    if os.path.exists(mres):
        rows = json.load(open(mres, encoding="utf-8"))
        lines = [r"\begin{table}[t]",
                 r"\caption{The resolution of the broadcast coverage-map "
                 r"summary.  A finer summary does not help: the swarm's "
                 r"spread contracts, because the policy follows the "
                 r"deficit instead of dividing the work.}",
                 r"\label{tab:results_mapres}", r"\centering", r"\scriptsize",
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
        lines = [r"\begin{table}[t]",
                 r"\caption{The cheapest test of the credit-assignment "
                 r"hypothesis.  The two arms differ in the learner that "
                 r"produces the advantage: a parameter-shared actor with a "
                 r"centralised critic, or a per-agent actor with a per-agent "
                 r"local critic.  A per-agent \\emph{baseline} changes the "
                 r"variance of the advantage, not its signal, which remains "
                 r"the shared team reward.}",
                 r"\label{tab:results_credit}", r"\centering", r"\scriptsize",
                 r"\begin{tabular}{@{}lccccc@{}}", r"\toprule",
                 r"Learner & CK & AG & SC & CovIntegral & Energy (J) \\",
                 r"\midrule"]
        for r in cr:
            name = r["arm"].split(":")[0]
            lines.append(
                f"{name} & {ck_cell(r)} & {fmt(r.get('AG'))} & "
                f"{fmt(r.get('SC'))} & {fmt(r.get('CovIntegral'))} & -- \\\\")
        lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
        parts.append("\n".join(lines))
    text = "\n\n".join(parts)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(text + "\n")
    print(f"Wrote {OUT} ({len(text)} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
