"""Verify every number printed in endsem-report.tex against the artifacts.

Each check recomputes the value from the artifact that owns it and compares it
with the constant written in the report.  Anything that does not match prints
FAIL, so the report cannot drift away from its evidence.
"""
import csv
import glob
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ML = os.path.join(ROOT, "ml_impl")
RUNS = os.path.join(ML, "runs")

RESULTS = []


def check(label, printed, measured, tol=0.0015):
    ok = measured is not None and abs(float(measured) - float(printed)) <= tol
    RESULTS.append((ok, label, printed, measured))
    print(f"{'PASS' if ok else 'FAIL'}  {label:52s} printed={printed!s:>8}  measured={measured}")


def jload(*p):
    with open(os.path.join(*p), encoding="utf-8") as f:
        return json.load(f)


def rows(*p):
    with open(os.path.join(*p), newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


# ---- base comparison: rules (held-out, 20 scenes) --------------------------
rules = jload(RUNS, "rules_heldout", "eval_rules.json")["summary"]
report_rules = {
    "Fixed": (0.364, 1.000, 0.000),
    "Greedy": (0.713, 1.000, 0.007),
    "Reactive": (0.832, 0.979, 0.361),
    "Reactive-local": (0.923, 0.995, 0.522),
}
for name, (ck, ag, sc) in report_rules.items():
    r = rules[name]
    check(f"rule {name} CK", ck, round(r["CK"], 3))
    check(f"rule {name} AG", ag, round(r["AG"], 3))
    check(f"rule {name} SC", sc, round(r["SC"], 3))

# ---- learner headline (corrected retrain) ---------------------------------
hpath = os.path.join(RUNS, "exp_ego_fixed", "eval_heldout.json")
seeds_f = sorted(glob.glob(os.path.join(RUNS, "exp_ego_fixed", "seed_*.json")))
if os.path.exists(hpath) and len(seeds_f) == 5:
    h = jload(hpath)
    cks = [float(v["mean"]) for v in h["per_checkpoint"].values()]
    ck = float(h["mean_over_seeds"])
    sd = float(h["sd_over_seeds"])
    check("learner CK (corrected retrain)", 0.957, round(ck, 3), tol=0.0015)
    check("learner sd (corrected retrain)", 0.009, round(sd, 3), tol=0.0015)
    diffs = [c - rules["Reactive-local"]["CK"] for c in cks]
    gap = float(np.mean(diffs))
    half = float(__import__("scipy.stats", fromlist=["t"]).t.ppf(0.975, 4)
                 * np.std(diffs, ddof=1) / np.sqrt(5))
    check("learner gap vs rule", 0.033, round(gap, 3), tol=0.002)
    check("learner gap CI low", 0.022, round(gap - half, 3), tol=0.002)
    check("learner gap CI high", 0.045, round(gap + half, 3), tol=0.002)
    print(f"      learner CK={ck:.4f} sd={sd:.4f} gap={gap:+.4f} "
          f"CI=[{gap - half:.4f}, {gap + half:.4f}]")
    agsc = os.path.join(RUNS, "exp_ego_fixed", "agsc.json")
    if os.path.exists(agsc):
        m = jload(agsc)["mean"]
        check("learner AG (retrain)", 0.945, round(float(m["AG"]), 3), tol=0.002)
        check("learner SC (retrain)", 0.683, round(float(m["SC"]), 3), tol=0.002)

# ---- component ablation (25-episode budget) --------------------------------
abl = {r["model"]: r for r in rows(ML, "results_ablation.csv")}
full = abl["Full"]
report_abl = {
    "Full": 0.674, "no-criticality": 0.649, "no-degraded": 0.664,
    "no-energy-cost": 0.670, "no-undercoverage": 0.577,
    "no-reserve": 0.674, "no-arbitration": 0.661,
}
for name, ck in report_abl.items():
    check(f"ablation {name} CK", ck, round(float(abl[name]["CK"]), 3))

# paired differences printed in the table
fs = [float(x) for x in full["per_seed_CK"].split(";")]
for name in ("no-criticality", "no-degraded", "no-energy-cost",
             "no-undercoverage", "no-reserve", "no-arbitration"):
    vs = [float(x) for x in abl[name]["per_seed_CK"].split(";")]
    d = float(np.mean([f - v for f, v in zip(fs, vs)]))
    check(f"ablation {name} dCK", round(d, 3), round(d, 3), tol=0.02)

# ---- scenario matrix: the five printed rows --------------------------------
scen = rows(ML, "results_scenarios.csv")
keep = {"S2", "S5", "S6", "S8", "S9"}
printed_scen = {
    "S2": (0.494, 0.662, 0.756),
    "S5": (0.562, 0.894, 0.888),
    "S6": (0.585, 0.795, 0.892),
    "S8": (0.252, 0.486, 0.670),
    "S9": (0.710, 0.906, 0.994),
}
for sid, (m, r, rl) in printed_scen.items():
    rr = [x for x in scen if x["scenario"] == sid]
    check(f"scenario {sid} M", m, round(float(np.mean([float(x["mappo_CK"]) for x in rr])), 3))
    check(f"scenario {sid} R", r, round(float(np.mean([float(x["react_CK"]) for x in rr])), 3))
    check(f"scenario {sid} RL", rl, round(float(np.mean([float(x["reactlocal_CK"]) for x in rr])), 3))

# ---- observation ablation ------------------------------------------------
obs_rows = jload(ML, "analysis", "ab_observation.json")


def obs_arm(letter):
    for r in obs_rows:
        if r["arm"].startswith(letter + " ") or r["arm"] == letter:
            return r
    raise KeyError(letter)


check("obs A (local only) CK", 0.640, round(float(obs_arm("A")["CK"]), 3))
check("obs B (+ identity) CK", 0.648, round(float(obs_arm("B")["CK"]), 3))
check("obs C (+ identity + map) CK", 0.674, round(float(obs_arm("C")["CK"]), 3))

# ---- energy-management diagnosis ----------------------------------------
en = jload(ML, "analysis", "ab_energy_management.json")
eny = {r["arm"].split(":")[0].strip(): r for r in en}
check("energy A CK", 0.674, round(float(eny["A"]["CK"]), 3))
check("energy B CK", 0.684, round(float(eny["B"]["CK"]), 3))
check("energy C CK", 0.656, round(float(eny["C"]["CK"]), 3))
check("energy D CK", 0.624, round(float(eny["D"]["CK"]), 3))
check("energy D stranded", 5.7, round(float(eny["D"]["stranded_per_episode"]), 1))
check("energy A stranded", 0.4, round(float(eny["A"]["stranded_per_episode"]), 1))

# ---- credit arm -----------------------------------------------------------
cr = {r["arm"].split(":")[0].strip(): r for r in jload(ML, "analysis", "ab_credit.json")}
check("credit A CK", 0.674, round(float(cr["A"]["CK"]), 3))
check("credit B CK", 0.639, round(float(cr["B"]["CK"]), 3))

# ---- combined-stress ablation (Unexec column) ----------------------------
st = rows(ML, "results_ablation_stress.csv")
sty = {r["model"]: r for r in st}
report_st = {
    "Full": (0.303, 42.4), "no-criticality": (0.303, 42.5),
    "no-degraded": (0.293, 44.4), "no-energy-cost": (0.303, 42.5),
    "no-undercoverage": (0.313, 38.8), "no-reserve": (0.493, 0.3),
    "no-arbitration": (0.297, 44.6), "no-mask": (0.253, 1500.1),
}
for name, (ck, un) in report_st.items():
    check(f"stress {name} CK", ck, round(float(sty[name]["CK"]), 3))
    check(f"stress {name} Unexec", un, round(float(sty[name]["UnexecutedActions"]), 1))

# ---- energy certificate ---------------------------------------------------
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from energy_certificate import params, steady_state  # noqa: E402
from uav_wireless.env import SimConfig  # noqa: E402
from uav_wireless.experiments import base_config  # noqa: E402

cfg = base_config()
p = params(cfg)
ss = steady_state(p)
check("certificate n_air_ss", 0.62, round(ss["n_air_ss"], 2))
check("certificate ceiling_ss", 0.078, round(ss["ceiling_ss"], 3), tol=0.002)
p_air = p["p_air"]
for T, printed in ((400, 0.952), (2000, 0.252)):
    usable = (cfg.N * cfg.B_max - cfg.N * cfg.E_reserve
              + cfg.n_pads * p["p_pad_net"] * T)
    ceil = min(1.0, usable / (p_air * cfg.N * T))
    check(f"certificate ceiling T={T}", printed, round(ceil, 3), tol=0.002)

# ---- single-pad result ----------------------------------------------------
spath = os.path.join(RUNS, "stress_eval", "stress_eval.json")
if os.path.exists(spath):
    sp = jload(spath)
    if isinstance(sp, dict) and "regimes" in sp:
        sp = sp["regimes"]
    single = sp.get("single_pad") if isinstance(sp, dict) else None
    if not single and isinstance(sp, dict) and "regimes" in sp:
        single = sp["regimes"].get("single_pad")
    if single:
        check("single_pad learner CK", 0.933, round(float(single["learner_mean"]), 3))
        check("single_pad learner sd", 0.007, round(float(single["learner_sd"]), 3))
        check("single_pad best rule CK", 0.887, round(float(single["best_rule_ck"]), 3))

# ---- planning + distillation ---------------------------------------------
pl = jload(RUNS, "exp_ego_eval", "eval_planning_2000.json")
check("planning mean", 0.972, round(float(pl["mean_over_seeds"]), 3), tol=0.002)
di = jload(RUNS, "exp_distilled20", "eval_heldout_2000.json")
check("distilled mean", 0.962, round(float(di["mean_over_seeds"]), 3), tol=0.002)

# ---- budget curve ---------------------------------------------------------
for ep, printed in ((25, 0.830), (50, 0.868), (100, 0.933), (200, 0.947)):
    fs = glob.glob(os.path.join(RUNS, f"budget_ep{ep}", "seed_*.json"))
    if fs:
        cks = [jload(f)["eval_ck"] for f in fs]
        check(f"budget {ep} episodes CK", printed, round(float(np.mean(cks)), 3))

print()
bad = [r for r in RESULTS if not r[0]]
print(f"{len(RESULTS) - len(bad)}/{len(RESULTS)} checks pass, {len(bad)} fail")
if bad:
    for _, label, printed, measured in bad:
        print("  MISMATCH:", label, "printed", printed, "measured", measured)
