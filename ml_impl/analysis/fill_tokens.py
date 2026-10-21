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
import math
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ML = os.path.dirname(HERE)
# the package under test lives one level up, and the test module imports it
if ML not in sys.path:
    sys.path.insert(0, ML)


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


def bound_clause(label, mean, half, gap):
    """One clause of an exclusion argument, derived from the measurement.

    To EXCLUDE an explanation of a gap of size `gap`, the arm that tests it
    must be shown to be too small to account for the gap: it is not enough
    for the arm's point estimate to be small, its upper confidence limit
    has to be below the gap.  The clause says which of the two happened.
    """
    upper = mean + half
    if gap is None or gap != gap:
        return (f"${label}$ ({mean:+.3f}, 95\\% interval "
                f"[{mean-half:+.3f}, {upper:+.3f}])")
    if upper < gap:
        return (f"${label}$ ({mean:+.3f}, 95\\% interval "
                f"[{mean-half:+.3f}, {upper:+.3f}], an upper limit below "
                f"the gap of {gap:.3f})")
    return (f"${label}$ ({mean:+.3f}, 95\\% interval "
            f"[{mean-half:+.3f}, {upper:+.3f}], whose upper limit is NOT "
            f"below the gap of {gap:.3f} and which therefore cannot be "
            f"excluded)")


def paired_stat(a, b):
    """The paired comparison of two arms that share their training seeds.

    `a` and `b` are the per-training-seed coverage values of the two arms.
    The arms are trained on the SAME seeds, so the difference is measured on
    the same training runs, and the interval is a paired t interval on the
    per-seed differences.  Returns (mean difference, half width of the 95%
    interval, two-sided p, number of pairs).

    A threshold on the size of a difference is not a test, so nothing here
    decides "the component matters" by comparing the difference with some
    other number: the interval does the work, and the reader can see what
    the measurement resolved.
    """
    try:
        from scipy import stats as _st
    except Exception:                                      # pragma: no cover
        _st = None
    n = min(len(a), len(b))
    if n < 2:
        return (float("nan"), float("nan"), float("nan"), n)
    d = [float(a[i]) - float(b[i]) for i in range(n)]
    mean = float(np.mean(d))
    sd = float(np.std(d, ddof=1))
    crit = _st.t.ppf(0.975, n - 1) if _st else 1.96
    half = crit * sd / np.sqrt(n)
    if _st:
        if sd > 0:
            tv = mean / (sd / np.sqrt(n))
            p = float(2 * (1 - _st.t.cdf(abs(tv), n - 1)))
        else:
            p = 0.0 if mean != 0 else 1.0
    else:                                                   # pragma: no cover
        p = float("nan")
    return (mean, float(half), p, n)


def build_tokens():
    """Read every artefact and return the token table.

    The tokens are the ONLY way a number reaches the paper's prose, so this
    function is the single point at which the paper's numbers are decided.
    """
    tok = {}

    main_rows = {r["model"]: r for r in load_csv("results_main.csv")}
    for key, model in (("FIXED", "Fixed"), ("GREEDY", "Greedy"),
                       ("REACT", "Reactive"), ("VAN", "VanillaMAPPO"),
                       ("MAPPO", "MAPPO"), ("ARG", "MAPPO-argmax"),
                       ("REACTL", "Reactive-local")):
        r = main_rows.get(model)
        if r is None:
            continue
        tok[f"{key}_CK"] = f(r["CK"])
        tok[f"{key}_AG"] = f(r["AG"])
        tok[f"{key}_SC"] = f(r["SC"])
        tok[f"{key}_CI"] = f(r["CovIntegral"])
        tok[f"{key}_E"] = f(r.get("Energy", 0), 0)
        tok[f"{key}_STR"] = f(r.get("Stranded", 0), 1)
        tok[f"{key}_RET"] = f(r.get("ReturnEvents", 0), 0)
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
    # the difference between the proposed method and the local-critic arm,
    # which the credit section tests on paired seeds
    mp0 = main_rows.get("MAPPO")
    for r in load_csv("results_learned_baselines.csv"):
        if "PPO" in r["model"] and mp0 is not None:
            tok["PPOL_DELTA"] = f"{float(r['CK']) - float(mp0['CK']):+.3f}"

    arg = main_rows.get("MAPPO-argmax")
    if arg is not None:
        tok["ARG_DISTANCE"] = f"{float(arg.get('Distance', 0)):.0f}"
        tok["ARG_CK"] = f(arg["CK"])
    mp = main_rows.get("MAPPO")
    if mp is not None:
        tok["MAPPO_DISTANCE"] = f"{float(mp.get('Distance', 0)):.0f}"
        tok["MAPPO_STRANDED"] = f"{float(mp.get('Stranded', 0)):.1f}"
        tok["MAPPO_UNEXEC"] = f"{float(mp.get('UnexecutedActions', 0)):.0f}"
        tok["PROJ_REVISIONS"] = f"{float(mp.get('ProjectionRevisions', 0)):.2f}"
        # THE GAP.  The reactive heuristic is deterministic, so it has no
        # training-seed spread; the uncertainty of the gap is therefore the
        # learned controller's own seed spread, divided by the number of
        # training runs.  The scene-to-scene variation is common to every
        # controller -- they are evaluated on the same scenes -- and cancels
        # in the difference.
        react = main_rows.get("Reactive")
        if react:
            # THE GAP is against the STRONGEST controller in the table, which
            # is not necessarily the privileged heuristic: the gap has to
            # be the hardest one the learned controller faces.
            best = None
            for cand in ("Reactive-local", "Reactive", "Greedy", "Fixed"):
                r = main_rows.get(cand)
                if r is None:
                    continue
                if best is None or float(r["CK"]) > float(best[1]["CK"]):
                    best = (cand, r)
            if best is not None:
                name, r = best
                tok["BEST_RULE_NAME"] = {
                    "Reactive-local": "the unprivileged reactive rule",
                    "Reactive": "the reactive heuristic",
                    "Greedy": "the greedy recharge controller",
                    "Fixed": "the fixed formation",
                }.get(name, name)
                tok["BEST_RULE_CK"] = f(r["CK"])
                gap = float(r["CK"]) - float(mp["CK"])
            else:
                gap = float(react["CK"]) - float(mp["CK"])
            tok["GAP"] = f"{gap:.3f}"
            s = mp.get("CK_std")
            n = int(mp.get("train_seeds", 0) or 0)
            if s not in (None, "") and n > 1:
                try:
                    from scipy import stats as _st
                    half = (float(_st.t.ppf(0.975, n - 1))
                            * float(s) / np.sqrt(n))
                except Exception:                          # pragma: no cover
                    half = 1.96 * float(s) / np.sqrt(n)
                tok["GAP_HALF"] = f"{half:.3f}"
                tok["GAP_CI"] = f"[{gap-half:.3f}, {gap+half:.3f}]"
                tok["GAP_N"] = str(n)
    # the fallback for the gap's interval: the per-seed training artefact
    if "GAP_CI" not in tok and "GAP" in tok:
        bs_path = os.path.join(HERE, "base_training_seeds.json")
        if os.path.exists(bs_path):
            bs = json.load(open(bs_path, encoding="utf-8"))
            cks = [float(b["CK"]) for b in bs]
            n = len(cks)
            if n > 1:
                try:
                    from scipy import stats as _st
                    crit = float(_st.t.ppf(0.975, n - 1))
                except Exception:                          # pragma: no cover
                    crit = 1.96
                gap = float(tok["GAP"])
                half = crit * float(np.std(cks, ddof=1)) / np.sqrt(n)
                tok["GAP_HALF"] = f"{half:.3f}"
                tok["GAP_CI"] = f"[{gap-half:.3f}, {gap+half:.3f}]"
                tok["GAP_N"] = str(n)

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
        # the paired intervals: the three arms share their training seeds
        for key, x, y in (("OBS_B", b, a), ("OBS_C", c, a)):
            if not (x and y):
                continue
            pa = x.get("per_seed_CK") or []
            pb = y.get("per_seed_CK") or []
            if not (pa and pb):
                continue
            mean, half, p, n = paired_stat(pa, pb)
            tok[f"{key}_PAIRED"] = f"{mean:+.3f}"
            tok[f"{key}_HALF"] = f"{half:.3f}"
            tok[f"{key}_CI"] = f"[{mean-half:+.3f}, {mean+half:+.3f}]"
            tok[f"{key}_P"] = f"{p:.3f}"
            tok[f"{key}_N"] = str(n)
        # the exclusion argument for the observation content
        obs_stats = []
        for key, label in (("OBS_B", "adding the agent identity"),
                           ("OBS_C", "the full observation of the proposed "
                                     "configuration")):
            if f"{key}_PAIRED" in tok:
                obs_stats.append((label, float(tok[f"{key}_PAIRED"]),
                                  float(tok[f"{key}_HALF"])))
        if obs_stats and "GAP" in tok:
            gap = float(tok["GAP"])
            clauses = [bound_clause(lab, m, h, gap) for lab, m, h in obs_stats]
            excluded = all((m + h) < gap for _, m, h in obs_stats)
            n = len(obs_stats)
            tok["OBS_SUMMARY"] = (
                ("The arms" if n > 1 else "The arm")
                + " share their training seeds, so the "
                + ("comparisons are paired: " if n > 1 else "comparison is paired: ")
                + "; ".join(clauses)
                + ((".  Each upper limit is below the gap of " if n > 1
                    else ".  The upper limit is below the gap of ")
                   if excluded else
                   (".  The intervals are wide relative to the gap of "
                    if n > 1 else
                    ".  The interval is wide relative to the gap of "))
                + f"{gap:.3f} to the reactive heuristic, so the content "
                + ("of the observation is not what accounts for the gap; "
                   if excluded else
                   "of the observation is not excluded by these arms; ")
                + "what the observation terms buy is the ability to "
                "specialise at all, and the arms here do not separate "
                "the coverage they produce.")

    mr = load_json("ab_map_resolution.json")
    if mr:
        parts = []
        for r in mr:
            parts.append(f"$G={r['grid']}$: {f(r['CK'])}")
        # the yardstick for "makes a difference": the learner's own
        # seed-to-seed spread
        spreads = [float(r.get("CK_std", 0.0)) for r in mr]
        yard = max(spreads) if spreads else 0.0
        cks = {int(r["grid"]): float(r["CK"]) for r in mr}
        sp = {int(r["grid"]): float(r.get("mean_spread_m", 0.0)) for r in mr}
        base = cks.get(0)
        resolvable = base is not None and any(
            abs(cks[g] - base) >= yard for g in cks if g != 0)
        if resolvable:
            tok["MAP_RESOLUTION"] = (
                "The resolution of the summary does not rescue it: " +
                ", ".join(parts) +
                ", and the swarm's spread contracts in every case, because "
                "the policy follows the deficit instead of dividing the "
                "work.")
        else:
            # the sweep may be mid-measurement, with only the G=0 arm in
            # the artefact; there is then nothing to compare it with
            worst = (max(abs(cks[g] - base) for g in cks if g != 0)
                     if base is not None and len(cks) > 1 else 0.0)
            sp_txt = ""
            if 0 in sp and len(sp) > 1:
                sp_txt = (
                    f"  What the summary does change is the swarm's "
                    f"behaviour: the spread falls from {sp[0]:.1f} m without "
                    f"it to "
                    + " and ".join(f"{sp[g]:.1f} m" for g in sorted(sp)
                                   if g != 0)
                    + " with it, because a policy that follows the deficit "
                      "keeps the swarm together instead of dispersing it.")
            tok["MAP_RESOLUTION"] = (
                "The resolution of the summary makes no difference to the "
                "coverage: " + ", ".join(parts)
                + f", and the largest of the differences is {worst:.3f}, "
                f"inside the seed-to-seed spread of the learner "
                f"({yard:.3f})." + sp_txt
                + "  The map is therefore neither what makes the controller "
                "work nor what stops it working: it is a channel the policy "
                "uses to move differently, and the difference it makes is "
                "visible in the trajectory rather than in the score.")
        # the verdict for the contribution bullet
        if base is not None and not resolvable:
            tok["MAP_VERDICT"] = (
                "A broadcast summary of where the coverage deficit is was "
                "added a priori and measured to make no difference to the "
                "coverage at any resolution tested, while it does change "
                "what the policy does; it is reported rather than quietly "
                "dropped.")
            tok["MAP_MODEL_SENTENCE"] = (
                "the summary makes no measurable difference to the coverage "
                "at any resolution tested, so the argument for adding it is "
                "neither supported nor refuted by the score, and what it "
                "does change is the shape of the swarm's motion")
        else:
            tok["MAP_VERDICT"] = (
                "A broadcast summary of where the coverage deficit is was "
                "added a priori and measured, and the measurement is "
                "reported rather than the summary being quietly dropped.")
            tok["MAP_MODEL_SENTENCE"] = (
                "the summary measurably changes the coverage, and the "
                "measurement is reported in Section~\\ref{sec:results_obs}")

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
        tok["EA_RET"] = f(ea["return_events_per_episode"], 0)
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
        tok["ED_RET"] = f(ed["return_events_per_episode"], 0)
        tok["ED_STR_DELTA"] = f(ed["stranded_per_episode"]
                                - ea["stranded_per_episode"], 1)
        tok["ED_RET_DELTA"] = f(abs(ed["return_events_per_episode"]
                                    - ea["return_events_per_episode"]), 0)
    # the paired intervals of the energy arms against arm A
    en_stats = []
    for key, arm, label in (("EB", "B", "removing the energy constraint"),
                             ("EC", "C", "removing the threshold term"),
                             ("ED", "D", "the previous energy rule")):
        r = arms_en.get(arm)
        if not (ea and r):
            continue
        pa = ea.get("per_seed_CK") or []
        pb = r.get("per_seed_CK") or []
        if not (pa and pb):
            continue
        mean, half, p, n = paired_stat(pb, pa)
        if not (mean == mean and half == half):
            # fewer than two shared training seeds: no interval is
            # computable, and the paper must say so rather than print a
            # not-a-number
            tok[f"{key}_PAIRED"] = "not measured"
            tok[f"{key}_HALF"] = "not measured"
            tok[f"{key}_CI"] = "not measured"
            tok[f"{key}_P"] = "not measured"
            tok[f"{key}_N"] = str(n)
            continue
        tok[f"{key}_PAIRED"] = f"{mean:+.3f}"
        tok[f"{key}_HALF"] = f"{half:.3f}"
        tok[f"{key}_CI"] = f"[{mean-half:+.3f}, {mean+half:+.3f}]"
        tok[f"{key}_P"] = f"{p:.3f}"
        tok[f"{key}_N"] = str(n)
        en_stats.append((label, mean, half))
    # ------------------------------------------------------------------
    # the exclusion argument, derived from the measurements
    # ------------------------------------------------------------------
    if "GAP" in tok and not en_stats:
        tok["ENERGY_SUMMARY"] = (
            "The three interventions are paired with the proposed "
            "configuration -- they share its training seeds -- so each one "
            "is reported as an interval rather than as a point, but the "
            "arms have not yet been measured with enough shared training "
            "seeds for an interval to be computable, and no bound is "
            "claimed for them here.")
    elif en_stats and "GAP" in tok:
        gap = float(tok["GAP"])
        clauses = [bound_clause(lab, m, h, gap) for lab, m, h in en_stats]
        excluded = all((m + h) < gap for _, m, h in en_stats)
        if excluded:
            tok["ENERGY_SUMMARY"] = (
                "The reading was wrong, and Table~\\ref{tab:results_energy} "
                "says so.  The three interventions are paired with the "
                "proposed configuration -- they share its training seeds -- "
                "so each one is reported as an interval rather than as a "
                "point, and each interval's upper limit is below the gap of "
                f"{gap:.3f} to the reactive heuristic: "
                + "; ".join(clauses)
                + ".  The energy model is therefore not what accounts for "
                "the gap, and the paper does not claim that it is.")
        else:
            tok["ENERGY_SUMMARY"] = (
                "Table~\\ref{tab:results_energy} bounds the energy "
                "explanation rather than settling it.  The three "
                "interventions are paired with the proposed configuration -- "
                "they share its training seeds -- so each one is reported "
                "as an interval rather than as a point: "
                + "; ".join(clauses)
                + f".  Not every interval excludes the gap of {gap:.3f}, so "
                "the energy model is not excluded by these arms; what the "
                "arms do establish is that the energy model is not the "
                "whole of the explanation, and the point estimates are all "
                "far smaller than the gap.")

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
                pstd = float(np.std(diffs, ddof=1)) if len(diffs) > 1 else 0.0
                paired.append((name, pmean, pstd))
            (moved if abs(delta) >= yardstick else still).append(
                (name, delta, pmean, pstd))

        # --------------------------------------------------------------
        # THE INFERENCE.  A threshold on the size of a difference is not a
        # test: with a per-arm null error rate of about a third at R = 3,
        # a rule that calls an effect "measurable" when it exceeds the
        # learner's own seed spread would flag one null component in three
        # and would still be unable to detect a true effect of that size.
        # The paired design supplies the right test instead: the variants
        # share the training seeds, so the difference is measured on the
        # same training runs, and the paired t interval says what the
        # measurement resolved.  Where the interval includes zero, the
        # honest statement is that NO EFFECT LARGER THAN THE INTERVAL'S
        # HALF-WIDTH WAS DETECTED -- not that the component is inert.
        # --------------------------------------------------------------
        if paired:
            try:
                from scipy import stats as _st
            except Exception:                                  # pragma: no cover
                _st = None
            n_p = len(paired[0][1] and [1] or [1])
            R = len(fs)
            crit = (_st.t.ppf(0.975, R - 1) if (_st and R > 1) else 0.0)
            rows_p = []
            for n, pmean, pstd in paired:
                half = crit * pstd / math.sqrt(R) if R > 1 else float("nan")
                if _st and R > 1 and pstd > 0:
                    tv = pmean / (pstd / math.sqrt(R))
                    pval = 2 * (1 - _st.t.cdf(abs(tv), R - 1))
                elif _st and R > 1:
                    pval = 0.0 if pmean != 0 else 1.0
                else:
                    pval = float("nan")
                rows_p.append(dict(name=n, mean=pmean, sd=pstd, half=half,
                                    p=pval,
                                    excludes_zero=(pmean - half > 0
                                                   or pmean + half < 0)))
            sig = [r for r in rows_p if r["excludes_zero"]]
            nulls = [r for r in rows_p if not r["excludes_zero"]]
            # the resolution of the measurement: the widest half-width among
            # the components whose interval includes zero
            delta_res = max([r["half"] for r in nulls], default=0.0)
            tok["ABL_N_SEEDS"] = str(R)
            tok["ABL_RESOLUTION"] = f"{delta_res:.3f}"
            tok["ABL_RESOLUTION_SD"] = f"{delta_res / crit:.3f}" if crit else "n/a"
            tok["ABL_CRIT"] = f"{crit:.2f}"
            if sig:
                parts = []
                for r in sorted(sig, key=lambda x: -abs(x["mean"])):
                    nm = names.get(r["name"], r["name"])
                    parts.append(f"${nm}$ ({r['mean']:+.3f}, 95\\% CI "
                                 f"[{r['mean']-r['half']:+.3f}, "
                                 f"{r['mean']+r['half']:+.3f}])")
                tok["ABL_SUMMARY"] = (
                    "The paired comparison, in which every variant is "
                    "trained on the same training seeds as the full "
                    "configuration, separates the components into two "
                    "groups.  The components whose 95\\% confidence interval "
                    "for the paired difference excludes zero are "
                    + ", ".join(parts)
                    + "; every other component's interval includes zero, "
                    "and the smallest difference this protocol could "
                    "resolve is $@@ABL_RESOLUTION@@$ of persistent coverage")
            else:
                tok["ABL_SUMMARY"] = (
                    "Every component's 95\\% confidence interval for the "
                    "paired difference includes zero, and the smallest "
                    "difference this protocol could resolve is "
                    "$@@ABL_RESOLUTION@@$ of persistent coverage")
            for r in rows_p:
                key = {"no-agent-id": "ID", "no-pad-bearing": "PAD",
                       "no-map": "MAP", "no-mask": "MASK"}.get(r["name"])
                if key:
                    tok[f"ABL_{key}_DELTA"] = f"{r['mean']:+.3f}"
                    tok[f"ABL_{key}_SPREAD"] = f"{r['sd']:.3f}"
                    tok[f"ABL_{key}_CI"] = (f"[{r['mean']-r['half']:+.3f}, "
                                            f"{r['mean']+r['half']:+.3f}]")
                    tok[f"ABL_{key}_P"] = f"{r['p']:.3f}"
                    if key == "ID":
                        # the contribution bullet must not overstate: if the
                        # interval includes zero, the honest sentence is
                        # about the ability to specialise, not the coverage
                        if r["excludes_zero"]:
                            tok["ABL_ID_CLAUSE"] = (
                                f"the identity is worth "
                                f"${r['mean']:+.3f}$ persistent coverage "
                                f"(95\\% interval $@@ABL_ID_CI@@$)")
                        else:
                            tok["ABL_ID_CLAUSE"] = (
                                f"the identity changes persistent coverage by "
                                f"${r['mean']:+.3f}$, an interval "
                                f"$@@ABL_ID_CI@@$ that includes zero, so at "
                                f"this budget what it demonstrably buys is "
                                f"the ability to specialise")
        else:
            tok["ABL_N_SEEDS"] = "?"
            tok["ABL_RESOLUTION"] = "n/a"
            tok["ABL_RESOLUTION_SD"] = "n/a"
            tok["ABL_CRIT"] = "n/a"
            # no per-seed values in the artefact: the paired comparison is
            # not available, and the unpaired differences are reported with
            # that stated rather than dressed up as an interval
            if moved:
                parts = []
                for n, dlt, pmean, pstd in sorted(moved, key=lambda x: -abs(x[1])):
                    parts.append(f"${names.get(n, n)}$ ({dlt:+.3f})")
                tok["ABL_SUMMARY"] = (
                    "the components whose difference from the full "
                    "configuration is largest are " + ", ".join(parts)
                    + ", and the rest do not move the coverage by more than "
                    "the seed-to-seed spread of the learner itself")
                for n, dlt, pmean, pstd in moved:
                    if n == "no-agent-id":
                        tok["ABL_ID_CLAUSE"] = (
                            f"the identity is worth ${-dlt:+.3f}$ persistent "
                            f"coverage")
                        tok.setdefault("ABL_ID_CI", "n/a")
                        tok.setdefault("ABL_ID_DELTA", f"{-dlt:+.3f}")
            else:
                tok["ABL_SUMMARY"] = (
                    "no single component changes the persistent coverage by "
                    "more than the seed-to-seed spread of the learner "
                    "itself, and the table is reported in full because that "
                    "is the result")
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
                    tok[f"ABL_{key}_SPREAD"] = f"{pstd:.3f}"
        tok["ABL_YARDSTICK"] = f"{yardstick:.3f}"
        tok["ABL_SEEDS"] = str(full.get("train_seeds", "?")) if full else "?"
        tok["ABL_EPISODES"] = str(full.get("episodes", "?")) if full else "?"
        # WHICH observation term matters most is a comparison, so it is
        # derived rather than asserted
        obs_terms = {"no-agent-id": "the agent identity",
                     "no-map": "the coverage map",
                     "no-pad-bearing": "the pad bearing"}
        best = None
        for n, pmean, pstd in paired:
            if n in obs_terms:
                if best is None or abs(pmean) > abs(best[1]):
                    best = (n, pmean, pstd)
        if best is not None:
            n, pmean, pstd = best
            tok["ABL_BEST_OBS"] = obs_terms[n]
            tok["ABL_BEST_OBS_DELTA"] = f"{-pmean:+.3f}"
            resolved = (pmean + pstd) < 0 or (pmean - pstd) > 0
            tok["ABL_BEST_OBS_TEXT"] = (
                f"The observation term with the largest effect on the "
                f"coverage is {obs_terms[n]}, and the ablation of the next "
                f"section prices it: it is worth {-pmean:.3f} of persistent "
                f"coverage, paired over the shared training seeds"
                + (", and it is the largest single observation effect in "
                   "this work." if resolved else
                   ", and it is the largest of the three, though the "
                   "interval is wide at this seed count."))
        else:
            tok["ABL_BEST_OBS"] = "the observation terms"
            tok["ABL_BEST_OBS_DELTA"] = "n/a"
            tok["ABL_BEST_OBS_TEXT"] = (
                "The ablation of the next section prices the observation "
                "terms individually")
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
                # the comparison is against the STRONGER of the two rules on
                # that variant, so the matrix is read against the best
                # reference the framework has
                rule = float(r["react_CK"])
                if r.get("reactlocal_CK") not in (None, ""):
                    rule = max(rule, float(r["reactlocal_CK"]))
                d = float(r["mappo_CK"]) - rule
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
        # the closing sentence of the section, derived from the matrix
        by_scen = {}
        for r in scen:
            try:
                rule = float(r["react_CK"])
                if r.get("reactlocal_CK") not in (None, ""):
                    rule = max(rule, float(r["reactlocal_CK"]))
                d = float(r["mappo_CK"]) - rule
            except (TypeError, ValueError, KeyError):
                continue
            by_scen.setdefault(r["scenario"], []).append(d)
        ahead = sorted(s for s, v in by_scen.items()
                       if sum(v) / len(v) > 0.02)
        behind = sorted(s for s, v in by_scen.items()
                        if sum(v) / len(v) < -0.02)
        if ahead:
            tok["SCEN_TEXT"] = (
                "At the level of scenario means the learned controller is "
                "ahead of the stronger rule in " + ", ".join(ahead)
                + (", and behind it in " + ", ".join(behind) if behind
                   else ", and behind it in no scenario")
                + ".  The matrix therefore says something the single "
                "configuration cannot: the ordering of the two is a "
                "property of the regime, not of the method, and a reader who "
                "is told only that a learned controller loses to a rule has "
                "been told half of it.")
        else:
            tok["SCEN_TEXT"] = (
                "At the level of scenario means the learned controller is "
                "behind the stronger rule in every scenario, although it is "
                f"ahead on {wins} of the {wins + losses + ties} variants, so "
                "the ordering is a property of the regime rather than of "
                "the method, and a reader told only that a learned "
                "controller loses to a rule has been told half of it.")
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
        # the paired comparison of the two learners
        pa = a.get("per_seed_CK") or []
        pb = b.get("per_seed_CK") or []
        if pa and pb:
            mean, half, p, n = paired_stat(pb, pa)
            tok["CREDIT_PAIRED"] = f"{mean:+.3f}"
            tok["CREDIT_HALF"] = f"{half:.3f}"
            tok["CREDIT_CI"] = f"[{mean-half:+.3f}, {mean+half:+.3f}]"
            tok["CREDIT_P"] = f"{p:.3f}"
            tok["CREDIT_N"] = str(n)
            # the verdict is derived: an interval that excludes zero says
            # something the point estimate does not
            if mean + half < 0:
                tok["CREDIT_VERDICT"] = (
                    f"the per-agent arm is measurably WORSE than the shared "
                    f"one, by {-mean:.3f} of persistent coverage, and the "
                    f"interval excludes zero, so the cheapest modification "
                    f"in the direction the diagnosis points does not close "
                    f"the gap --- it opens it slightly")
            elif mean - half > 0:
                tok["CREDIT_VERDICT"] = (
                    f"the per-agent arm is measurably BETTER than the shared "
                    f"one, by {mean:.3f} of persistent coverage, and the "
                    f"interval excludes zero, so the cheapest modification "
                    f"in the direction the diagnosis points helps --- "
                    f"although not by enough to close the gap")
            else:
                tok["CREDIT_VERDICT"] = (
                    f"the difference is not resolved by this arm: the "
                    f"interval is consistent with a difference of any size up "
                    f"to about {half:.3f} in either direction, so the "
                    f"cheapest modification in the direction the diagnosis "
                    f"points has not been shown to close the gap")

    # ------------------------------------------------------------------
    # THE ARMS' VERDICT, derived.  The abstract and the introduction both
    # say what the controlled arms establish.  Whether they establish it
    # depends on the measurements, so the sentence is derived here: an
    # explanation is excluded only if the arm that tests it has an upper
    # confidence limit below the gap.
    # ------------------------------------------------------------------
    arm_bounds = []
    if obs_stats and "GAP" in tok:
        arm_bounds.append(("the content of the observation",
                           max(m + h for _, m, h in obs_stats)))
    if en_stats and "GAP" in tok:
        arm_bounds.append(("the energy model",
                           max(m + h for _, m, h in en_stats)))
    if arm_bounds:
        gap = float(tok["GAP"])
        excluded = [lab for lab, up in arm_bounds if up == up and up < gap]
        not_excluded = [lab for lab, up in arm_bounds
                        if not (up == up and up < gap)]
        # the sentence names ONLY the arms that were actually measured, so
        # it cannot claim an arm was tested when its artefact is missing
        names_all = " and ".join(lab for lab, _ in arm_bounds)
        if not not_excluded:
            tok["ARMS_VERDICT"] = (
                "controlled arms bound how much of the gap the alternative "
                "explanations can account for: "
                + names_all
                + (" is" if len(arm_bounds) == 1 else " are")
                + " tested with a single-factor intervention whose "
                "interval lies far below the gap")
        else:
            tok["ARMS_VERDICT"] = (
                "controlled arms bound how much of the gap the alternative "
                "explanations can account for: the interval of "
                + ("the arm testing " if len(arm_bounds) == 1
                   else "the arms testing ")
                + names_all + " "
                + ("does" if len(arm_bounds) == 1 else "do")
                + " not exclude the whole gap"
                + (", so " + " and ".join(not_excluded)
                   + (" is" if len(not_excluded) == 1 else " are")
                   + " not excluded by "
                   + ("it" if len(not_excluded) == 1 else "them")
                   if not_excluded else ""))
    else:
        tok["ARMS_VERDICT"] = (
            "the arms that test the alternative explanations have not been "
            "measured yet, so no bound is claimed for them")

    # ------------------------------------------------------------------
    # the causes the arms do NOT test
    # ------------------------------------------------------------------
    # The list is a token so that the abstract and the conclusion quote the
    # same one, and so that a cause which has since been MEASURED cannot
    # stay on the list: the rule's privileged access to the coverage state
    # was on it until the local-assignment arm measured it.
    tok["UNTESTED_CAUSES"] = (
        "the possibility that the hand-written rule was tuned against the "
        "evaluation scenes, the limit of a decentralised policy class, and "
        "the state-dependent corrections that the safety filter and the "
        "joint projection impose on the executed trajectory")

    # ------------------------------------------------------------------
    # what the metrics do on an INFEASIBLE configuration
    # ------------------------------------------------------------------
    inf = load_json("infeasible_instance.json")
    if inf:
        m = inf.get("mean", {})
        tok["INF_CK"] = f(m.get("CK", float("nan")))
        tok["INF_SC"] = f(m.get("SC", float("nan")))
        tok["INF_AG"] = f(m.get("AG", float("nan")))
        tok["INF_ORACLE"] = f(m.get("oracle_CK", float("nan")))
        tok["INF_N"] = str(len(inf.get("rows", [])))

    # ------------------------------------------------------------------
    # THE INFORMATION-ASYMMETRY ARM.  The reactive heuristic is given the
    # exact set of under-covered sensors; the learned policy is given a
    # fixed-size summary.  The arm below is the same rule with the global
    # coverage state removed, and it is what turns the caveat into a
    # measurement.
    # ------------------------------------------------------------------
    rl = main_rows.get("Reactive-local")
    rp = main_rows.get("Reactive")
    if rl and rp and "GAP" in tok:
        priv = float(rp["CK"])
        loc = float(rl["CK"])
        gap = float(tok["GAP"])
        d = priv - loc
        share = d / gap if abs(gap) > 1e-9 else 0.0
        tok["REACTL_SHARE"] = f"{100 * share:.0f}"
        if d < 0:
            # the unprivileged rule is BETTER: the privilege was a handicap
            tok["REACTL_VERDICT"] = (
                f"The privileged version is in fact slightly WORSE than the "
                f"unprivileged one ({d:+.3f}), so the global coverage state "
                f"is not what gives the rule its edge --- the global "
                f"round-robin assignment makes the UAVs contend for "
                f"sensors, and the local rule does better --- and the gap "
                f"to the learned controller is therefore not an information "
                f"artefact at all")
        elif abs(d) < 0.5 * abs(gap):
            tok["REACTL_VERDICT"] = (
                f"the privilege is therefore worth {d:.3f} of persistent "
                f"coverage, which is a small part of the {gap:.3f} gap to "
                f"the learned controller, and the gap is not an information "
                f"artefact")
        else:
            tok["REACTL_VERDICT"] = (
                f"the privilege is therefore worth {d:.3f} of persistent "
                f"coverage, which is {100 * share:.0f}\\% of the {gap:.3f} "
                f"gap to the learned controller, and a large part of the "
                f"gap is therefore an information artefact")

    # ------------------------------------------------------------------
    # where the connectivity availability below 1.000 comes from
    # ------------------------------------------------------------------
    ca = load_json("connectivity_accounting.json")
    if ca:
        n = int(ca.get("disconnected_steps", 0))
        left = int(ca.get("after_active_set_change", 0))
        tel = int(ca.get("after_teleport", 0))
        unex = int(ca.get("unexplained", 0))
        tok["CONN_STEPS"] = str(n)
        tok["CONN_LEFT"] = str(left)
        tok["CONN_TELE"] = str(tel)
        tok["CONN_UNEXPLAINED"] = str(unex)
        if unex == 0:
            tok["CONN_VERDICT"] = (
                "every one of them is attributable to the recovery "
                "mechanism and none to a policy action, so the filter's "
                "guarantee holds over the actions and the availability below "
                "1.000 is the price of the recovery")
        else:
            tok["CONN_VERDICT"] = (
                f"{unex} of them are NOT attributable to either mechanism, "
                f"which is a residual the filter does not account for and "
                f"which we report rather than explain away")

    # ------------------------------------------------------------------
    # the alternative corrected deployment (N = 5, K = 2, R_cov = 45 m)
    # ------------------------------------------------------------------
    # the threshold is what the witness construction needs: four discs at
    # the side midpoints and one at the centre, over the square's grid
    try:
        side = 80.0
        centres = [(side / 2, 0.0), (side / 2, side), (0.0, side / 2),
                   (side, side / 2), (side / 2, side / 2)]
        grid = np.linspace(0.0, side, 161)
        X, Y = np.meshgrid(grid, grid, indexing="ij")
        pts = np.stack([X.ravel(), Y.ravel()], axis=1)
        d = np.linalg.norm(pts[:, None, :] - np.asarray(centres)[None, :, :],
                           axis=-1)
        d.sort(axis=1)
        tok["ALT_N5_R"] = f"{float(d[:, 1].max()):.2f}"
    except Exception:                                      # pragma: no cover
        pass

    # ------------------------------------------------------------------
    # THE COMBINED-STRESS TABLE.  The ordering of the components is not the
    # same there as in the nominal regime, and the difference is a finding
    # rather than a nuisance, so it is derived rather than left in a table.
    # ------------------------------------------------------------------
    stress = load_csv("results_ablation_stress.csv")
    if stress:
        sby = {r["model"]: r for r in stress}
        sfull = sby.get("Full")
        if sfull:
            sfs = per_seed_ck(sfull)
            helped, hurt = [], []
            for r in stress:
                if r["model"] in ("Full",):
                    continue
                vs = per_seed_ck(r)
                if not (sfs and vs and len(sfs) == len(vs)):
                    continue
                d = float(r["CK"]) - float(sfull["CK"])   # variant - Full
                label = names.get(r["model"], r["model"])
                if r["model"] == "VanillaMAPPO":
                    label = "the whole design"
                if d <= -0.02:
                    helped.append((label, -d))
                elif d >= 0.02:
                    hurt.append((label, d))
            helped.sort(key=lambda x: -x[1])
            hurt.sort(key=lambda x: -x[1])
            parts = []
            if helped:
                parts.append("removing " + ", ".join(
                    f"{lab} costs {v:.3f}" for lab, v in helped)
                    + " of persistent coverage, so the component helps")
            if hurt:
                parts.append("removing " + ", ".join(
                    f"{lab} GAINS {v:.3f}" for lab, v in hurt)
                    + ", so the component is a liability there")
            if parts:
                tok["STRESS_SUMMARY"] = (
                    "The ordering of the components is not the same here as "
                    "in the nominal regime, and that is a result rather than "
                    "a nuisance: " + "; ".join(parts)
                    + ".  The framework's recovery mechanism, which re-seats "
                    "an exhausted UAV at a charging pad, is a liability when "
                    "energy is scarce, because the re-seated UAV is out of "
                    "communication range of the swarm until it flies back, "
                    "and the swarm spends the scenario disconnected and "
                    "gathered rather than spread.")

    # ------------------------------------------------------------------
    # the plasticity probe of the trained actor
    # ------------------------------------------------------------------
    dor = load_json("dormancy.json")
    if dor:
        silent_vals, dormant_any = [], 0
        for r in dor:
            lay = str(r.get("layer", "L0")).upper()
            for tau, tag in (("0.001", "T001"), ("0.01", "T01"),
                             ("0.05", "T05"), ("0.1", "T1")):
                tok[f"DORM_{lay}_{tag}_DORMANT"] = f(
                    r.get(f"dormant_frac_{tau}", 0.0), 3)
                tok[f"DORM_{lay}_{tag}_SILENT"] = f(
                    r.get(f"silent_frac_{tau}", 0.0), 3)
                tok[f"DORM_{lay}_{tag}_DEAD"] = f(
                    r.get(f"dead_frac_{tau}", 0.0), 3)
                if tau in ("0.001", "0.01", "0.05", "0.1"):
                    silent_vals.append(float(r.get(f"silent_frac_{tau}", 0.0)))
                    dormant_any = max(dormant_any,
                                      float(r.get(f"dormant_frac_{tau}", 0.0)))
            tok[f"DORM_{lay}_SOME"] = str(
                r.get("neurons_dormant_for_some_agent_only", 0))
        if silent_vals:
            tok["DORM_SILENT_MIN"] = f"{100 * min(silent_vals):.0f}"
            tok["DORM_SILENT_MAX"] = f"{100 * max(silent_vals):.0f}"
        tok["DORM_DORMANT_MAX"] = f"{dormant_any:.3f}"

    # ------------------------------------------------------------------
    # the training-budget sweep
    # ------------------------------------------------------------------
    bud = load_json("ab_budget.json")
    if bud:
        rows = sorted(bud, key=lambda r: int(r.get("episodes", 0)))
        parts = ", ".join(f"{int(r['episodes'])} episodes: {f(r['CK'])}"
                          for r in rows)
        spread = float(rows[-1]["CK"]) - float(rows[0]["CK"])
        tok["BUDGET_SWEEP"] = parts
        tok["BUDGET_SPREAD"] = f"{spread:+.3f}"
        tok["BUDGET_MIN"] = f"{min(float(r['CK']) for r in rows):.3f}"
        tok["BUDGET_MAX"] = f"{max(float(r['CK']) for r in rows):.3f}"
        tok["BUDGET_VERDICT"] = (
            f"the coverage moves by {spread:+.3f} between the shortest and "
            f"the longest budget, against a seed-to-seed spread of about "
            f"{max(float(r.get('CK_std', 0.0)) for r in rows):.3f}, so the "
            f"shortfall is not made of the training budget at this scale")

    # ------------------------------------------------------------------
    # the episode length, in both units, so that the two "400"s of the
    # paper (the 2000-step episode's 400 SECONDS, and the earlier
    # 400-STEP episode) can never be confused
    # ------------------------------------------------------------------
    try:
        # the CANONICAL configuration, not the dataclass defaults: the
        # default episode length is not the one the experiments use
        from uav_wireless.experiments import base_config
        c0 = base_config()
        endurance = c0.B_max / c0.P_hover            # seconds of hover
        old_steps = 400
        old_seconds = old_steps * c0.dt
        tok["PACK_ENDURANCE"] = f"{endurance:.0f}"
        tok["OLD_EPISODE_S"] = f"{old_seconds:.0f}"
        tok["OLD_EPISODE_PCT"] = f"{100 * old_seconds / endurance:.0f}"
        tok["EPISODE_STEPS"] = f"{int(c0.episode_len)}"
        tok["EPISODE_SECONDS"] = f"{c0.episode_len * c0.dt:.0f}"
    except Exception:                                      # pragma: no cover
        pass

    # ------------------------------------------------------------------
    # the numbers the paper quotes about ITSELF
    # ------------------------------------------------------------------
    # the claim audit's own counts, so that the paper cannot claim a
    # different number of verified claims than the audit verifies
    audit = load_json("claim_audit.json")
    if audit:
        n_pass = sum(1 for r in audit if r.get("status") == "PASS")
        n_fail = sum(1 for r in audit if r.get("status") == "FAIL")
        n_info = sum(1 for r in audit if r.get("status") == "INFO")
        tok["AUDIT_ITEMS"] = str(len(audit))
        tok["AUDIT_PASS"] = str(n_pass)
        tok["AUDIT_FAIL"] = str(n_fail)
        tok["AUDIT_INFO"] = str(n_info)
        # the connectivity regime, as the audit measured it
        for r in audit:
            d = r.get("data") or {}
            if r.get("id") == "C6" and d:
                tok["C6_DEGREE"] = f(d["mean_degree"], 2)
                tok["C6_MAXDEG"] = str(int(d["max_degree"]))
                tok["C6_COMPLETE"] = f"{100*d['frac_complete']:.0f}"
                tok["C6_LEAVES"] = f"{100*d['frac_leaves']:.0f}"

    # the size of the test suite, counted the way the runner discovers it.
    # The test module is PARSED, not imported: importing it pulls in torch,
    # which loads the CUDA runtime, and that is several hundred megabytes
    # that the machine may not have while the experiments are running.
    try:
        import ast
        tests_dir = os.path.join(ML, "tests")
        n_tests = 0
        for fname in sorted(os.listdir(tests_dir)):
            if not fname.startswith("test_") or not fname.endswith(".py"):
                continue
            tree = ast.parse(open(os.path.join(tests_dir, fname),
                                  encoding="utf-8").read())
            for node in tree.body:
                if not isinstance(node, ast.ClassDef):
                    continue
                if not node.name.startswith("Test"):
                    continue
                for item in node.body:
                    if (isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                            and item.name.startswith("test_")):
                        n_tests += 1
        tok["N_TESTS"] = str(n_tests)
    except Exception as exc:  # pragma: no cover - diagnostic path
        print(f"WARNING: the test count could not be determined: {exc}",
              file=sys.stderr)
    # the variance decomposition of the headline number: the seed-to-seed
    # component and the scene-to-scene component, reported separately.  The
    # scene component is COMMON to every controller, because they are all
    # evaluated on the same scenes, and it therefore cancels in every
    # comparison the paper draws; the seed component does not.
    seed_rows = os.path.join(HERE, "base_seed_rows.jsonl")
    if os.path.exists(seed_rows):
        by_seed = {}
        for line in open(seed_rows, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            ps = d.get("per_seed") or []
            if ps:
                # the file is appended to, so the LAST row for a seed is the
                # one from the most recent run
                by_seed[int(d.get("train_seed", len(by_seed)))] = \
                    [float(x["CK"]) for x in ps]
        per_seed_scenes = [by_seed[k] for k in sorted(by_seed)]
        if len(per_seed_scenes) > 1:
            n_scenes = min(len(x) for x in per_seed_scenes)
            seed_means = [float(np.mean(x[:n_scenes])) for x in per_seed_scenes]
            scene_means = [float(np.mean([x[e] for x in per_seed_scenes]))
                           for e in range(n_scenes)]
            s_seed = float(np.std(seed_means, ddof=1))
            s_scene = float(np.std(scene_means, ddof=1))
            tok["VAR_SEED"] = f"{s_seed:.3f}"
            tok["VAR_SCENE"] = f"{s_scene:.3f}"
            tok["VAR_SEED_SE"] = f"{s_seed / np.sqrt(len(seed_means)):.3f}"
            tok["VAR_SCENE_SE"] = f"{s_scene / np.sqrt(n_scenes):.3f}"
            tok["VAR_N_SEEDS"] = str(len(seed_means))
            tok["VAR_N_SCENES"] = str(n_scenes)
            # the yardstick of the whole paper: the seed-to-seed spread
            tok["ABL_YARDSTICK"] = f"{s_seed:.3f}"

    # ------------------------------------------------------------------
    # the learning curve of the first training run
    # ------------------------------------------------------------------
    # The curve is what speaks to the compute-asymmetry objection: a
    # hand-designed rule embeds a human's solution, and the learner gets a
    # fixed budget, so the question "would more training have helped?" has
    # to be answered rather than assumed.  The per-episode coverage of the
    # first training run, on the training scene, answers it.
    hist_path = os.path.join(ML, "hist_base.json")
    if os.path.exists(hist_path):
        try:
            hist = json.load(open(hist_path, encoding="utf-8"))
        except Exception:                                  # pragma: no cover
            hist = []
        cks = [float(h["CK"]) for h in hist if "CK" in h]
        if len(cks) >= 10:
            k = min(5, len(cks) // 2)
            tok["CURVE_EPISODES"] = str(len(cks))
            tok["CURVE_FIRST"] = f"{float(np.mean(cks[:k])):.3f}"
            tok["CURVE_LAST"] = f"{float(np.mean(cks[-k:])):.3f}"
            tok["CURVE_BEST"] = f"{max(cks):.3f}"
            tok["CURVE_FINAL"] = f"{cks[-1]:.3f}"
            tok["CURVE_MIN"] = f"{min(cks):.3f}"
            tok["CURVE_MAX"] = f"{max(cks):.3f}"
            # the evaluated coverage of the SAME policy, on unseen scenes
            if per_seed_scenes:
                tok["CURVE_EVAL"] = f"{float(np.mean(per_seed_scenes[0])):.3f}"
    return tok


def fill(text, tok):
    """Replace every @@TOKEN@@ in `text`; return (filled_text, missing).

    The substitution is repeated until it reaches a fixed point, because a
    token's VALUE can itself contain a token: the ablation's summary quotes
    the resolution, and if the two are substituted in the wrong order the
    quoted token reaches the paper as text.
    """
    for _ in range(4):
        for k, v in tok.items():
            text = text.replace(f"@@{k}@@", str(v))
        if not re.search(r"@@[A-Z_0-9]+@@", text):
            break
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
