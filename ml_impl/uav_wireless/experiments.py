"""
Experiment design matrix (Table X / Section VII).

Runs the full comparison: Fixed, Greedy, Reactive, MAPPO (proposed),
Vanilla MAPPO (ablation) across 8 scenarios x 5 seeds, and prints a
metrics table. Results are saved to CSV.
"""

from __future__ import annotations

import os
import numpy as np

from .env import SimConfig, UAVIoTEnv
from .train import (
    train_mappo, collect_rollout,
    baseline_fixed, baseline_greedy, baseline_reactive,
)


def scenario_cfgs(base: SimConfig):
    """S1..S8 -> list of (id, research question, [configs])."""
    import copy

    def cp(**kw):
        c = copy.deepcopy(base)
        for k, v in kw.items():
            setattr(c, k, v)
        return c

    scen = []
    scen.append(("S1", "sensor density",
                 [cp(M=10, seed=s) for s in range(5)] +
                 [cp(M=40, seed=s) for s in range(5)]))
    scen.append(("S2", "fleet size N",
                 [cp(N=3, seed=s) for s in range(5)] +
                 [cp(N=8, seed=s) for s in range(5)]))
    scen.append(("S3", "battery capacity",
                 [cp(B_max=15_000.0, charge_rate=0.0004, seed=s) for s in range(5)] +
                 [cp(B_max=60_000.0, seed=s) for s in range(5)]))
    scen.append(("S4", "charging pads S",
                 [cp(n_pads=1, seed=s) for s in range(5)] +
                 [cp(n_pads=4, seed=s) for s in range(5)]))
    scen.append(("S5", "R_comm",
                 [cp(R_comm=25.0, seed=s) for s in range(5)] +
                 [cp(R_comm=55.0, seed=s) for s in range(5)]))
    scen.append(("S6", "R_cov",
                 [cp(R_cov=28.0, seed=s) for s in range(5)] +
                 [cp(R_cov=45.0, seed=s) for s in range(5)]))
    scen.append(("S7", "failure time",
                 [cp(failure_enabled=True, failure_time=200, seed=s) for s in range(5)] +
                 [cp(failure_enabled=True, failure_time=700, seed=s) for s in range(5)]))
    scen.append(("S8", "combined stress",
                 [cp(failure_enabled=True, failure_time=500, n_pads=1,
                     B_max=15_000.0, charge_rate=0.0004, R_comm=30.0, R_cov=30.0, seed=s)
                  for s in range(5)]))
    return scen


def eval_agent(agent, cfg, steps=1000, seed=0):
    import copy
    c = copy.deepcopy(cfg)
    c.seed = seed
    env = UAVIoTEnv(c)
    obs, st = env.reset()
    for _ in range(steps):
        import numpy as np
        mask = np.stack([env.action_mask(i) for i in range(c.N)])
        for i in range(c.N):
            if mask[i].sum() == 0:
                mask[i, 0] = True
                mask[i] = mask[i] | (mask[i] == 0)
        acts = agent.act(obs, mask, deterministic=True)
        obs, st, r, done, _ = env.step(acts)
        if done:
            break
    return env.summary()


def run_base_comparison(base: SimConfig, out_csv="results_main.csv"):
    """Train MAPPO once on the base config, compare against rule baselines."""
    import csv
    rows = []

    print("\n=== Training proposed MAPPO on base config ===")
    agent, hist = train_mappo(base, episodes=120, n_steps=400, seed=0, log_every=20)
    agent.save("mappo_base.pt")

    print("\n=== Rule-based baselines (5 seeds) ===")
    for name, fn in [("Fixed", baseline_fixed),
                     ("Greedy", baseline_greedy),
                     ("Reactive", baseline_reactive)]:
        sums = [fn(base, steps=base.episode_len, seed=s) for s in range(5)]
        agg = {k: float(np.mean([s[k] for s in sums])) for k in sums[0]}
        print(f"{name:10s} CK={agg['CK']:.3f} AG={agg['AG']:.3f} SC={agg['SC']:.3f} "
              f"Crit={agg['Crit']:.3f} E={agg['Energy']:.0f}")
        rows.append(dict(model=name, **agg))

    print("\n=== MAPPO (proposed) evaluation (5 seeds) ===")
    evs = [eval_agent(agent, base, steps=base.episode_len, seed=s) for s in range(5)]
    agg = {k: float(np.mean([s[k] for s in evs])) for k in evs[0]}
    std = {k: float(np.std([s[k] for s in evs])) for k in evs[0]}
    print(f"{'MAPPO':10s} CK={agg['CK']:.3f}±{std['CK']:.3f} AG={agg['AG']:.3f} "
          f"SC={agg['SC']:.3f} Crit={agg['Crit']:.3f} E={agg['Energy']:.0f}")
    rows.append(dict(model="MAPPO", **agg))

    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"\nSaved -> {out_csv}")
    return agent, rows


def run_ablation(base: SimConfig, out_csv="results_ablation.csv", stress=True):
    """Turn off one proposed component at a time (Table VIII).

    stress=True  -- ablate on the S8 combined-stress scenario.  The stress
                    config is what actually exercises the reserve and
                    arbitration mechanisms, but K=2 coverage is not
                    achievable there, so the coverage numbers are bounded by
                    the geometry rather than by the policy.
    stress=False -- ablate directly on the base (feasible) configuration, so
                    the component contributions are measured on a task that a
                    controller can actually solve.  This is the table that
                    supports the paper's claims.
    """
    import copy, csv
    print(f"\n=== Ablations ({'S8 combined stress' if stress else 'feasible base config'}) ===")
    variants = {
        "Full": dict(),
        "no-connectivity": dict(use_connectivity_term=False),
        "no-reserve": dict(use_reserve=False),
        "no-arbitration": dict(use_charging_arbitration=False),
        "no-mask": dict(use_action_mask=False),
        "VanillaMAPPO": dict(use_connectivity_term=False, use_reserve=False,
                             use_charging_arbitration=False, use_action_mask=False),
    }
    rows = []
    for name, kw in variants.items():
        c = copy.deepcopy(base)
        if stress:
            # Ablate on the COMBINED-STRESS scenario (S8), not the base config.
            # On the base config no UAV fails and nobody contends for a pad, so
            # the reserve / arbitration mechanisms never fire and every ablation
            # trivially matches. The stress config is what actually exercises them.
            c.failure_enabled = True
            c.failure_time = 120
            c.n_pads = 1
            c.B_max = 15_000.0
            c.charge_rate = 0.0004
            c.R_comm = 32.0
        for k, v in kw.items():
            setattr(c, k, v)
        c.episode_len = min(c.episode_len, 400)
        agent, _ = train_mappo(c, episodes=60, n_steps=250, seed=0, verbose=False)
        evs = [eval_agent(agent, c, steps=c.episode_len, seed=s) for s in range(3)]
        agg = {k: float(np.mean([s[k] for s in evs])) for k in evs[0]}
        agg["Reserve"] = float(np.mean([s["Reserve"] for s in evs]))
        agg["Denied"] = float(np.mean([s["Denied"] for s in evs]))
        print(f"{name:18s} CK={agg['CK']:.3f} AG={agg['AG']:.3f} SC={agg['SC']:.3f} "
              f"CI={agg['CovIntegral']:.3f} Reserve={agg['Reserve']:.1f} "
              f"Denied={agg['Denied']:.0f}", flush=True)
        rows.append(dict(model=name, **agg))

    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"Saved -> {out_csv}")
    return rows


def run_scenarios(base: SimConfig, out_csv="results_scenarios.csv"):
    """Table X: MAPPO vs the Reactive heuristic on every scenario variant.

    Each scenario defines two variants (e.g. sparse vs dense sensors). Both
    are evaluated; the agent is trained once on the base configuration and
    then transferred, which is the point of the exercise -- the policy is not
    retrained per scenario.
    """
    import csv
    import copy
    agent, _ = train_mappo(base, episodes=60, n_steps=300, seed=0, verbose=False)
    rows = []
    print("\n=== Scenarios (MAPPO vs Reactive) ===")
    for sid, question, cfgs in scenario_cfgs(base):
        for vi, c0 in enumerate(cfgs):
            c = copy.deepcopy(c0)
            c.episode_len = min(c.episode_len, 400)
            m = eval_agent(agent, c, steps=c.episode_len, seed=0)
            r = baseline_reactive(c, steps=c.episode_len, seed=0)
            # a short description of the variant for the CSV
            variant = (f"N={c.N} M={c.M} Rcov={c.R_cov:.0f} "
                       f"Rcomm={c.R_comm:.0f} pads={c.n_pads} "
                       f"Bmax={c.B_max:.0f} fail={c.failure_enabled}")
            print(f"{sid}.{vi} ({question:16s}) {variant}  "
                  f"MAPPO CK={m['CK']:.3f} SC={m['SC']:.3f} "
                  f"CI={m['CovIntegral']:.3f} | "
                  f"Reactive CK={r['CK']:.3f} SC={r['SC']:.3f}")
            rows.append(dict(scenario=sid, variant=vi, question=question,
                             config=variant,
                             mappo_CK=m["CK"], mappo_SC=m["SC"],
                             mappo_CovIntegral=m["CovIntegral"],
                             react_CK=r["CK"], react_SC=r["SC"],
                             react_CovIntegral=r["CovIntegral"]))
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"Saved -> {out_csv}")
    return rows