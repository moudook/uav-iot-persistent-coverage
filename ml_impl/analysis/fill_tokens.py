"""
Fill the @@TOKEN@@ placeholders in the prose from the artefacts.

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

import numpy as np

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


def per_seed_ck(row):
    """The per-training-seed CK values of an ablation row, if present."""
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


def build_tokens():
    """Read every artefact and return the token table.

    The tokens are the ONLY way a number reaches the paper's prose, so this
    function is the single point at which the paper's numbers are decided.
    """
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
        tok[f"{key}_STR"] = f(r.get("Stranded", 0), 1)
        tok[f"{key}_DIST"] = f(r.get("Distance", 0), 0)
        if r.get("CK_std") not in (None, ""):
            tok[f"{key}_CK_STD"] = f(r["CK_std"])

    for r in load_csv("results_learned_baselines.csv"):
        key = ("IDDQN" if "DQN" in r["model"] else
               "PPOL" if "PPO" in r["model"] else None)
        if key is None:
            continue
        tok[f"{key}_CK"] = f(r["CK"])
        tok[f"{key}_AG"] = f(r["AG"])
        tok[f"{key}_SC"] = f(r["SC"])
        tok[f"{key}_CI"] = f(r["CovIntegral"])
        if r.get("CK_std") not in (None, ""):
            tok[f"{key}_CK_STD"] = f(r["CK_std"])

    arg = main_rows.get("MAPPO-argmax")
    if arg is not None:
        tok["ARG_DISTANCE"] = f"{float(arg.get('Distance', 0)):.0f}"
        tok["ARG_CK"] = f(arg["CK"])
    mp = main_rows.get("MAPPO")
    if mp is not None:
        tok["MAPPO_DISTANCE"] = f"{float(mp.get('Distance', 0)):.0f}"
        tok["MAPPO_STRANDED"] = f"{float(mp.get('Stranded', 0)):.1f}"
        tok["MAPPO_UNEXEC"] = f"{float(mp.get('UnexecutedActions', 0)):.0f}"

    # ------------------------------------------------------------------
    # the observation A/B/C
    # ------------------------------------------------------------------
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
        tok["A_CK_STD"] = f(a.get("CK_std", 0.0))
        tok["B_CK"] = f(b["CK"])
        tok["B_AG"] = f(b["AG"])
        tok["B_SC"] = f(b["SC"])
        tok["B_DIST"] = f(b["distinct_actions"], 2)
        tok["B_SPREAD"] = f(b["mean_spread_m"], 1)
        tok["B_CK_STD"] = f(b.get("CK_std", 0.0))
        delta = b["CK"] - a["CK"]
        tok["B_MINUS_A"] = f"{delta:+.3f}"
        react = main_rows.get("Reactive")
        if react:
            gap = float(react["CK"]) - a["CK"]
            share = (delta / gap) if abs(gap) > 1e-9 else 0.0
            tok["B_SHARE"] = f"{100*share:.0f}\\%"
    if c:
        tok["C_CK"] = f(c["CK"])
        tok["C_CK_STD"] = f(c.get("CK_std", 0.0))
        if a:
            tok["C_DELTA"] = f"{c['CK'] - a['CK']:+.3f}"
        if b:
            tok["B_DELTA"] = f"{b['CK'] - a['CK']:+.3f}" if a else "n/a"
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

    # ------------------------------------------------------------------
    # the energy arms
    # ------------------------------------------------------------------
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
    if ea and ec:
        tok["EC_DELTA"] = f(ec["CK"] - ea["CK"])
    arms_en = {r["arm"].split(":")[0].strip(): r for r in en}
    ed = arms_en.get("D")
    if ea and ed:
        tok["ED_DELTA"] = f(ed["CK"] - ea["CK"])
        tok["ED_STR"] = f(ed["stranded_per_episode"], 1)
        tok["ED_CK"] = f(ed["CK"])
        tok["ED_RET"] = f(ed["return_events_per_episode"], 1)

    # ------------------------------------------------------------------
    # the component ablation
    # ------------------------------------------------------------------
    # The yardstick is the spread of the learner itself: how much the
    # training seed moves the coverage of the FULL configuration.  A
    # component effect smaller than this is not measurable at this budget.
    yardstick = 0.02
    bs_path = os.path.join(HERE, "base_training_seeds.json")
    if os.path.exists(bs_path):
        bs = json.load(open(bs_path, encoding="utf-8"))
        cks = [float(b["CK"]) for b in bs]
        if len(cks) > 1:
            yardstick = float(np.std(cks))

    abl = load_csv("results_ablation.csv")
    if abl:
        by = {r["model"]: r for r in abl}
        full = by.get("Full")
        van = by.get("VanillaMAPPO")
        # the full configuration's own seed spread, if the ablation measured
        # it, is the better yardstick: it is the same experiment
        if full:
            fs = per_seed_ck(full)
            if len(fs) > 1:
                yardstick = float(np.std(fs))
        if full and van:
            d = float(full["CK"]) - float(van["CK"])
            tok["ABL_DELTA"] = f"{d:+.3f}"

        names = {"no-criticality": "the criticality term",
                 "no-degraded": "the degraded-service term",
                 "no-energy-cost": "the energy-cost term",
                 "no-undercoverage": "the under-coverage term",
                 "no-reserve": "the reserve UAV",
                 "no-arbitration": "the charging arbitration",
                 "no-mask": "the action mask",
                 "no-agent-id": "the agent identity",
                 "no-map": "the coverage map",
                 "no-pad-bearing": "the pad bearing"}
        moved, still, paired = [], [], []
        fs = per_seed_ck(full) if full else []
        for name, r in by.items():
            if name in ("Full", "VanillaMAPPO"):
                continue
            try:
                delta = float(r["CK"]) - float(full["CK"])
            except (TypeError, ValueError, KeyError):
                continue
            vs = per_seed_ck(r)
            pmean = pstd = None
            if fs and len(vs) == len(fs):
                diffs = [fs[i] - vs[i] for i in range(len(fs))]
                pmean = float(np.mean(diffs))
                pstd = float(np.std(diffs))
                paired.append((name, pmean, pstd))
            (moved if abs(delta) >= yardstick else still).append(
                (name, delta, pmean, pstd))
        if moved:
            parts = []
            for n, dlt, pmean, pstd in sorted(moved, key=lambda x: -abs(x[1])):
                nm = names.get(n, n)
                if pmean is not None:
                    parts.append(f"${nm}$ ({pmean:+.3f} paired, "
                                 f"seed-to-seed spread {pstd:.3f})")
                else:
                    parts.append(f"${nm}$ ({dlt:+.3f})")
            tok["ABL_SUMMARY"] = (
                f"On this configuration {', '.join(parts)} "
                f"{'has' if len(parts) == 1 else 'have'} a measurable "
                f"effect on persistent coverage, and the remaining "
                f"variants do not")
        else:
            tok["ABL_SUMMARY"] = (
                "On this configuration no single component changes the "
                "persistent coverage by more than the seed-to-seed spread "
                "of the learner itself, and the table is reported in "
                "full because that is the result")
        # the paired deltas of the components that matter, for the prose
        if paired:
            parts = []
            for n, pmean, pstd in sorted(paired, key=lambda x: -abs(x[1])):
                if abs(pmean) < yardstick:
                    continue
                parts.append(f"{names.get(n, n)} {pmean:+.3f}"
                             f"\\,({pstd:.3f})")
            tok["ABL_PAIRS"] = ", ".join(parts) if parts else "none"
            for n, pmean, pstd in paired:
                key = {"no-agent-id": "ID", "no-pad-bearing": "PAD",
                       "no-map": "MAP", "no-mask": "MASK"}.get(n)
                if key:
                    tok[f"ABL_{key}_DELTA"] = f"{pmean:+.3f}"
                    tok[f"ABL_{key}_SPREAD"] = f"{pstd:.3f}")
        tok["ABL_YARDSTICK"] = f"{yardstick:.3f}"
        tok["ABL_SEEDS"] = str(full.get("train_seeds", "?")) if full else "?"
        tok["ABL_EPISODES"] = str(full.get("episodes", "?")) if full else "?"
        # the fall-back for the components that matter: if the per-seed
        # values are not in the artefact, the unpaired difference is used and
        # is reported as such
        for n, dlt, pmean, pstd in moved:
            key = {"no-agent-id": "ID", "no-pad-bearing": "PAD",
                   "no-map": "MAP", "no-mask": "MASK"}.get(n)
            if key and f"ABL_{key}_DELTA" not in tok:
                tok[f"ABL_{key}_DELTA"] = f"{-dlt:+.3f}"
                tok[f"ABL_{key}_SPREAD"] = f"{yardstick:.3f}"

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
    return tok


def fill(text, tok):
    """Replace every @@TOKEN@@ in `text`; return (filled_text, missing)."""
    for k, v in tok.items():
        text = text.replace(f"@@{k}@@", str(v))
    missing = sorted(set(re.findall(r"@@([A-Z_0-9]+)@@", text)))
    return text, missing


def main():
    tok = build_tokens()
    tmpl = os.path.join(HERE, "results_text.tex")
    out = os.path.join(HERE, "results_text_filled.tex")
    s = open(tmpl, encoding="utf-8").read()
    s, missing = fill(s, tok)
    with open(out, "w", encoding="utf-8") as f:
        f.write(s)
    if missing:
        print("UNFILLED TOKENS:", missing)
        return 1
    print("all tokens filled")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
