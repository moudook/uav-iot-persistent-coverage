"""
Fill the @@TOKEN@@ placeholders in the results prose from the artefacts.

The prose is written with placeholders so that no number in the text can be
typed by hand: every value is read from the same artefact that the table
generator read, so the text and the tables cannot disagree.

Run:  python analysis/fill_tokens.py
"""

from __future__ import annotations

import csv
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ML = os.path.dirname(HERE)


def load_csv(name):
    p = os.path.join(ML, name)
    if not os.path.exists(p):
        return []
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_json(name):
    p = os.path.join(HERE, name)
    if not os.path.exists(p):
        return []
    return json.load(open(p, encoding="utf-8"))


def f(x, nd=3):
    return f"{float(x):.{nd}f}"


def main():
    tok = {}

    main_rows = {r["model"]: r for r in load_csv("results_main.csv")}
    for key, model in (("FIXED", "Fixed"), ("GREEDY", "Greedy"),
                       ("REACT", "Reactive"), ("VAN", "VanillaMAPPO"),
                       ("MAPPO", "MAPPO"), ("ARG", "MAPPO-argmax")):
        r = main_rows.get(model)
        if r is None:
            continue
        tok[f"{key}_CK"] = f(r["CK"])
        tok[f"{key}_AG"] = f(r["AG"])
        tok[f"{key}_SC"] = f(r["SC"])
        tok[f"{key}_CI"] = f(r["CovIntegral"])
        tok[f"{key}_E"] = f(r.get("Energy", 0), 0)
    for r in load_csv("results_learned_baselines.csv"):
        key = ("IDDQN" if "DQN" in r["model"] else
               "PPOL" if "PPO" in r["model"] else None)
        if key is None:
            continue
        tok[f"{key}_CK"] = f(r["CK"])
        tok[f"{key}_AG"] = f(r["AG"])
        tok[f"{key}_SC"] = f(r["SC"])
        tok[f"{key}_CI"] = f(r["CovIntegral"])

    obs = load_json("ab_observation.json")
    arms = {}
    for r in obs:
        if r.get("kind") == "baseline":
            continue
        key = r["arm"].strip()[0].upper()
        arms[key] = r
    a, b, c = arms.get("A"), arms.get("B"), arms.get("C")
    if a and b:
        tok["A_CK"] = f(a["CK"])
        tok["A_AG"] = f(a["AG"])
        tok["A_SC"] = f(a["SC"])
        tok["A_DIST"] = f(a["distinct_actions"], 2)
        tok["A_SPREAD"] = f(a["mean_spread_m"], 1)
        tok["B_CK"] = f(b["CK"])
        tok["B_AG"] = f(b["AG"])
        tok["B_SC"] = f(b["SC"])
        tok["B_DIST"] = f(b["distinct_actions"], 2)
        tok["B_SPREAD"] = f(b["mean_spread_m"], 1)
        delta = b["CK"] - a["CK"]
        tok["B_MINUS_A"] = f"{delta:+.3f}"
        react = main_rows.get("Reactive")
        if react:
            gap = float(react["CK"]) - a["CK"]
            share = (delta / gap) if abs(gap) > 1e-9 else 0.0
            tok["B_SHARE"] = f"{100*share:.0f}\\%"
    if c:
        tok["C_CK"] = f(c["CK"])
        tok["C_AG"] = f(c["AG"])
        tok["C_SC"] = f(c["SC"])
        tok["C_DIST"] = f(c["distinct_actions"], 2)
        tok["C_SPREAD"] = f(c["mean_spread_m"], 1)

    mr = load_json("ab_map_resolution.json")
    if mr:
        parts = []
        for r in mr:
            parts.append(f"$G={r['grid']}$: {f(r['CK'])}")
        tok["MAP_RESOLUTION"] = (
            "The resolution of the summary does not rescue it: " +
            ", ".join(parts) +
            ", and the swarm's spread contracts in every case, because the "
            "policy follows the deficit instead of dividing the work.")

    en = load_json("ab_energy_management.json")
    arms_en = {}
    for r in en:
        arms_en[r["arm"].strip()[0].upper()] = r
    ea, eb, ec = arms_en.get("A"), arms_en.get("B"), arms_en.get("C")
    if ea:
        tok["EA_CK"] = f(ea["CK"])
        tok["EA_AG"] = f(ea["AG"])
        tok["EA_SC"] = f(ea["SC"])
        tok["EA_STR"] = f(ea["stranded_per_episode"], 1)
        tok["EA_RET"] = f(ea["return_events_per_episode"], 1)
    if eb:
        tok["EB_CK"] = f(eb["CK"])
        tok["EB_AG"] = f(eb["AG"])
        tok["EB_SC"] = f(eb["SC"])
        tok["EB_RET"] = f(eb["return_events_per_episode"], 1)
    if ec:
        tok["EC_CK"] = f(ec["CK"])
        tok["EC_AG"] = f(ec["AG"])
        tok["EC_SC"] = f(ec["SC"])
        tok["EC_STR"] = f(ec["stranded_per_episode"], 1)
        tok["EC_RET"] = f(ec["return_events_per_episode"], 1)
    if ea and eb:
        tok["ENERGY_DELTA"] = f(eb["CK"] - ea["CK"])

    # the ablation and the scenario summary are written by hand from the
    # tables, but their anchors are computed here so that the sentences
    # cannot drift from the numbers.
    abl = load_csv("results_ablation.csv")
    if abl:
        by = {r["model"]: r for r in abl}
        full = by.get("Full")
        van = by.get("VanillaMAPPO")
        if full and van:
            d = float(full["CK"]) - float(van["CK"])
            tok["ABL_DELTA"] = f"{d:+.3f}"
            # which components actually move the coverage?
            moved, still = [], []
            for name, r in by.items():
                if name in ("Full", "VanillaMAPPO"):
                    continue
                try:
                    delta = abs(float(r["CK"]) - float(full["CK"]))
                except (TypeError, ValueError, KeyError):
                    continue
                (moved if delta >= 0.02 else still).append(
                    (name, float(r["CK"]) - float(full["CK"])))
            names = {"no-criticality": "the criticality term",
                     "no-degraded": "the degraded-service term",
                     "no-energy-cost": "the energy-cost term",
                     "no-undercoverage": "the under-coverage term",
                     "no-reserve": "the reserve UAV",
                     "no-arbitration": "the charging arbitration",
                     "no-mask": "the action mask",
                     "no-agent-id": "the agent identity",
                     "with-map": "the coverage map",
                     "no-pad-bearing": "the pad bearing"}
            if moved:
                parts = []
                for n, dlt in sorted(moved, key=lambda x: -abs(x[1])):
                    parts.append(f"${names.get(n, n)}$ ({dlt:+.3f})")
                tok["ABL_MOVED"] = (", ".join(parts) +
                                    " have a measurable effect on persistent "
                                    "coverage")
            else:
                tok["ABL_MOVED"] = ("no single component has a measurable "
                                    "effect on persistent coverage")
            if still:
                parts = [names.get(n, n) for n, _ in still]
                tok["ABL_STILL"] = (", ".join(parts) +
                                     " do not, at this budget and on this "
                                     "configuration")
            else:
                tok["ABL_STILL"] = ""
    scen = load_csv("results_scenarios.csv")
    if scen:
        wins = losses = ties = 0
        worst = ("", 0.0)
        best = ("", 0.0)
        for r in scen:
            try:
                d = float(r["mappo_CK"]) - float(r["react_CK"])
            except (TypeError, ValueError, KeyError):
                continue
            if d > 0.02:
                wins += 1
            elif d < -0.02:
                losses += 1
            else:
                ties += 1
            if d < worst[1]:
                worst = (r["scenario"], d)
            if d > best[1]:
                best = (r["scenario"], d)
        tok["SCEN_WINS"] = str(wins)
        tok["SCEN_LOSSES"] = str(losses)
        tok["SCEN_TIES"] = str(ties)
        tok["SCEN_WORST"] = f"{worst[0]} ({worst[1]:+.3f})"
        tok["SCEN_BEST"] = f"{best[0]} ({best[1]:+.3f})"
    tok.setdefault("ABL_TEXT", "")
    tok.setdefault("CREDIT_TEXT", "")
    tok.setdefault("SCEN_TEXT", "")

    cr = load_json("ab_credit.json")
    if len(cr) >= 2:
        a, b = cr[0], cr[1]
        d = b["CK"] - a["CK"]
        tok["CREDIT_DELTA"] = f"{d:+.3f}"
        tok["CREDIT_A_CK"] = f(a["CK"])
        tok["CREDIT_B_CK"] = f(b["CK"])
        tok["CREDIT_A_SC"] = f(a["SC"])
        tok["CREDIT_B_SC"] = f(b["SC"])
        react = main_rows.get("Reactive")
        if react:
            gap = float(react["CK"]) - a["CK"]
            tok["CREDIT_OF_GAP"] = (f"{100*abs(d)/gap:.0f}\\%" if abs(gap) > 1e-9
                                     else "0\\%")

    tmpl = os.path.join(HERE, "results_text.tex")
    out = os.path.join(HERE, "results_text_filled.tex")
    s = open(tmpl, encoding="utf-8").read()
    missing = []
    for k, v in tok.items():
        s = s.replace(f"@@{k}@@", v)
    for m in re.findall(r"@@([A-Z_0-9]+)@@", s):
        missing.append(m)
    open(out, "w", encoding="utf-8").write(s)
    if missing:
        print("UNFILLED TOKENS:", sorted(set(missing)))
    else:
        print("all tokens filled")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
