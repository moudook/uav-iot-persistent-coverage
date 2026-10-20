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


def base_config(**overrides) -> SimConfig:
    """The one canonical experimental configuration.

    Every script must build its configuration from here, so that the
    numbers in the paper, the numbers in the CSVs and the numbers in the
    audit all describe the same experiment.

    Choices, and why:

    N = 8, K = 2, R_cov = 35 m
        The corner-packing bound requires N >= 4K, so N = 8 is the smallest
        feasible fleet for K = 2 on this field.

    start_clustered = True
        A centred ring deployment already covers 17 of 20 sensors at t = 0,
        so every controller -- including one that never moves -- scores
        CK = 0.850 and the comparison cannot separate them.  The clustered
        deployment is connected at t = 0 and covers 3 of 20, so the
        controller has real work to do.

    episode_len = 2000 steps (400 s of flight)
        At 400 steps the pack never depletes, so the return-to-charge
        transition never fires, the charging arbitration is never
        exercised and the reserve UAV has nothing to recover.  At 2000
        steps the constraint binds (283 return transitions and 0.7 stranded
        UAVs per episode under the Reactive heuristic) while the mission
        remains achievable.

    B_max = 30 000 J, charge_rate = 0.0002/step
        The pack size and charge rate of the report's parameter table; the
        episode length is what changed.

    use_agent_id, map_grid = 4, use_pad_bearing
        The observation must identify the agent for a shared policy to
        specialise, must say where the coverage deficit is, and must give
        the direction of the charging pad.
    """
    cfg = SimConfig(
        N=8, K=2, R_cov=35.0, M=20, episode_len=2000, seed=0,
        B_max=30_000.0, charge_rate=0.0002,
        lam_B=2.0,
        start_clustered=True,
        use_agent_id=True, map_grid=4, use_pad_bearing=True,
    )
    for k, v in overrides.items():
        setattr(cfg, k, v)
    return cfg


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
    scen.append(("S9", "initial deployment",
                 [cp(start_clustered=True, seed=s) for s in range(5)] +
                 [cp(start_clustered=False, seed=s) for s in range(5)]))
    return scen


def eval_agent(agent, cfg, steps=1000, seed=0, deterministic=False):
    """Roll out the learned policy and return the episode summary.

    The default is the SAMPLED policy, because Eq. (13) of the report
    specifies a_i(t) ~ pi_theta(a_i | o_i(t)): the deployed policy draws
    from the categorical distribution, it does not take the argmax.  The
    difference between the two is not cosmetic and is reported: with a
    shared actor the deterministic policy tends to select the SAME action
    for every UAV, so the swarm translates as a rigid body and never
    disperses, while the sampled policy breaks that tie by chance and
    deploys.  `deterministic=True` selects the argmax policy for
    comparison.
    """
    import copy
    c = copy.deepcopy(cfg)
    c.seed = seed
    env = UAVIoTEnv(c)
    obs, st = env.reset()
    for _ in range(steps):
        import numpy as np
        mask = np.stack(env.action_masks())
        for i in range(c.N):
            if mask[i].sum() == 0:
                mask[i, 0] = True
                mask[i] = mask[i] | (mask[i] == 0)
        acts = agent.act(obs, mask, deterministic=deterministic)
        obs, st, r, done, _ = env.step(acts)
        if done:
            break
    return env.summary()


def run_base_comparison(base: SimConfig, out_csv="results_main.csv",
                        eval_seeds=5, train=True, agent=None):
    """Train MAPPO on the base config, compare against the rule baselines.

    The baselines are evaluated on the SAME seeds as the learned policy.
    (They previously accepted a seed and ignored it, so a "five-seed"
    comparison ran one scene five times for the baselines while the learned
    policy was evaluated on five different scenes -- which flatters the
    learned policy whenever the extra seeds happen to be easier.)
    """
    import csv
    rows = []

    if agent is None and train:
        print("\n=== Training proposed MAPPO on base config ===")
        agent, hist = train_mappo(base, episodes=120, n_steps=400, seed=0,
                                  log_every=20)
        agent.save("mappo_base.pt")

    print(f"\n=== Rule-based baselines ({eval_seeds} seeds) ===")
    for name, fn in [("Fixed", baseline_fixed),
                     ("Greedy", baseline_greedy),
                     ("Reactive", baseline_reactive)]:
        sums = [fn(base, steps=base.episode_len, seed=s)
                for s in range(eval_seeds)]
        agg = {k: float(np.mean([s[k] for s in sums])) for k in sums[0]}
        std = {k: float(np.std([s[k] for s in sums])) for k in sums[0]}
        print(f"{name:10s} CK={agg['CK']:.3f}±{std['CK']:.3f} "
              f"AG={agg['AG']:.3f} SC={agg['SC']:.3f} "
              f"CI={agg['CovIntegral']:.3f} E={agg['Energy']:.0f}")
        rows.append(dict(model=name, **agg))

    print(f"\n=== MAPPO (proposed) evaluation ({eval_seeds} seeds) ===")
    evs = [eval_agent(agent, base, steps=base.episode_len, seed=s)
           for s in range(eval_seeds)]
    agg = {k: float(np.mean([s[k] for s in evs])) for k in evs[0]}
    std = {k: float(np.std([s[k] for s in evs])) for k in evs[0]}
    print(f"{'MAPPO':10s} CK={agg['CK']:.3f}±{std['CK']:.3f} AG={agg['AG']:.3f} "
          f"SC={agg['SC']:.3f} CI={agg['CovIntegral']:.3f} "
          f"E={agg['Energy']:.0f}")
    rows.append(dict(model="MAPPO", **agg))

    # the deterministic (argmax) policy of the SAME learned actor, for
    # comparison.  This is not the policy Eq. (13) specifies, and the gap
    # between the two is a reported result, not an implementation detail.
    det = [eval_agent(agent, base, steps=base.episode_len, seed=s,
                       deterministic=True) for s in range(eval_seeds)]
    dagg = {k: float(np.mean([s[k] for s in det])) for k in det[0]}
    dstd = {k: float(np.std([s[k] for s in det])) for k in det[0]}
    print(f"{'MAPPO(argmax)':10s} CK={dagg['CK']:.3f}±{dstd['CK']:.3f} "
          f"AG={dagg['AG']:.3f} SC={dagg['SC']:.3f} "
          f"CI={dagg['CovIntegral']:.3f}")
    rows.append(dict(model="MAPPO-argmax", **dagg))

    # ---- the achievability ceiling ---------------------------------
    # The teleporting placement oracle is the reference against which every
    # coverage number in this table is meant to be read.  It is a property
    # of the configuration, not of any controller, so it is reported once.
    try:
        import sys as _sys
        _sys.path.insert(0, os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))))
        from analysis.feasibility import analyse_scene
        ck = []
        for s in range(min(eval_seeds, 3)):
            r = analyse_scene(s, base, iters=60, restarts=8)
            ck.append(float(r["oracle_CK_connected"]))
        orc = float(np.mean(ck))
        print(f"{'Oracle':10s} CK={orc:.3f}  (teleporting placement, "
              f"ignores energy and motion)")
        rows.append(dict(model="Oracle (ceiling)", CK=orc, AG=1.0, SC=orc,
                         CovIntegral=0.0, Energy=0.0, Denied=0.0,
                         Reserve=0.0, Stranded=0.0, Returning=0.0))
    except Exception as exc:                      # pragma: no cover
        print(f"{'Oracle':10s} (not computed: {exc})")

    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"\nSaved -> {out_csv}")
    return agent, rows


def run_ablation(base: SimConfig, out_csv="results_ablation.csv", stress=True,
                 episodes=12, eval_seeds=3):
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

    Every variant is trained from the same seed on the same configuration
    except for the one component that is removed, so the differences are
    attributable to that component.
    """
    import copy, csv
    print(f"\n=== Ablations ({'S8 combined stress' if stress else 'feasible base config'}) ===")
    variants = {
        "Full": dict(),
        "no-criticality": dict(lam_C=0.0),
        "no-degraded": dict(lam_D=0.0),
        "no-energy-cost": dict(lam_E=0.0),
        "no-undercoverage": dict(lam_O=0.0),
        "no-reserve": dict(use_reserve=False),
        "no-arbitration": dict(use_charging_arbitration=False),
        "no-mask": dict(use_action_mask=False),
        "no-agent-id": dict(use_agent_id=False),
        "no-map": dict(map_grid=0),
        "no-pad-bearing": dict(use_pad_bearing=False),
        "VanillaMAPPO": dict(lam_C=0.0, lam_D=0.0, use_reserve=False,
                             use_charging_arbitration=False,
                             use_action_mask=False, use_agent_id=False,
                             map_grid=0, use_pad_bearing=False),
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
            c.failure_time = 500
            c.n_pads = 1
            c.B_max = 15_000.0
            c.charge_rate = 0.0004
            c.R_comm = 30.0
            c.R_cov = 30.0
        for k, v in kw.items():
            setattr(c, k, v)
        agent, _ = train_mappo(c, episodes=episodes, n_steps=c.episode_len,
                               seed=0, verbose=False)
        evs = [eval_agent(agent, c, steps=c.episode_len, seed=s)
               for s in range(eval_seeds)]
        agg = {k: float(np.mean([s[k] for s in evs])) for k in evs[0]}
        agg["Reserve"] = float(np.mean([s["Reserve"] for s in evs]))
        agg["Denied"] = float(np.mean([s["Denied"] for s in evs]))
        agg["Stranded"] = float(np.mean([s["Stranded"] for s in evs]))
        print(f"{name:18s} CK={agg['CK']:.3f} AG={agg['AG']:.3f} SC={agg['SC']:.3f} "
              f"CI={agg['CovIntegral']:.3f} Reserve={agg['Reserve']:.1f} "
              f"Denied={agg['Denied']:.0f} Stranded={agg['Stranded']:.1f}",
              flush=True)
        rows.append(dict(model=name, **agg))

    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"Saved -> {out_csv}")
    return rows


def run_learned_baselines(base: SimConfig, out_csv="results_learned_baselines.csv",
                          episodes=12, eval_seeds=3, seeds=2):
    """The learned baselines of Table VI, evaluated on the same scenes.

    These are implementations of the METHOD FAMILIES the comparison table
    names -- a value-based multi-agent method and a PPO-family method that
    uses action masking -- not reproductions of the cited papers.  They use
    the same simulator, observation, action mask and team reward as the
    proposed method, so the only differences are the learning machinery.
    """
    import csv
    import copy
    from .baselines_rl import (train_id_dqn, train_ppo_local,
                                eval_id_dqn, eval_ppo_local)
    rows = []
    print("\n=== Learned baselines (Table VI) ===")

    for name, trainer, evaluator in [
            ("Independent DQN (value-based)", train_id_dqn, eval_id_dqn),
            ("Masked PPO, local critic", train_ppo_local, eval_ppo_local)]:
        cks, ags, scs, cis = [], [], [], []
        for s in range(seeds):
            c = copy.deepcopy(base)
            c.seed = s
            agent, _ = trainer(c, episodes=episodes, steps=c.episode_len,
                               seed=s, verbose=False)
            evs = [evaluator(agent, c, steps=c.episode_len, seed=e)
                   for e in range(eval_seeds)]
            agg = {k: float(np.mean([x[k] for x in evs])) for k in evs[0]}
            std = {k: float(np.std([x[k] for x in evs])) for k in evs[0]}
            cks.append(agg["CK"]); ags.append(agg["AG"]); scs.append(agg["SC"])
            cis.append(agg["CovIntegral"])
            print(f"  {name:32s} seed {s}: CK={agg['CK']:.3f}±{std['CK']:.3f} "
                  f"AG={agg['AG']:.3f} SC={agg['SC']:.3f} "
                  f"CI={agg['CovIntegral']:.3f}", flush=True)
        print(f"  {name:32s} MEAN     CK={np.mean(cks):.3f} "
              f"AG={np.mean(ags):.3f} SC={np.mean(scs):.3f} "
              f"CI={np.mean(cis):.3f}", flush=True)
        rows.append(dict(model=name, CK=float(np.mean(cks)),
                         CK_std=float(np.std(cks)), AG=float(np.mean(ags)),
                         SC=float(np.mean(scs)),
                         CovIntegral=float(np.mean(cis))))

    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"Saved -> {out_csv}")
    return rows


def run_scenarios(base: SimConfig, out_csv="results_scenarios.csv",
                  episodes=12):
    """Table X: MAPPO vs the Reactive heuristic on every scenario variant.

    Each scenario defines two variants (e.g. sparse vs dense sensors). Both
    are evaluated; the agent is trained once on the base configuration and
    then transferred, which is the point of the exercise -- the policy is not
    retrained per scenario.
    """
    import csv
    import copy
    agent, _ = train_mappo(base, episodes=episodes, n_steps=base.episode_len,
                           seed=0, verbose=False)
    rows = []
    print("\n=== Scenarios (MAPPO vs Reactive) ===")
    for sid, question, cfgs in scenario_cfgs(base):
        for vi, c0 in enumerate(cfgs):
            c = copy.deepcopy(c0)
            m = eval_agent(agent, c, steps=c.episode_len, seed=c.seed)
            r = baseline_reactive(c, steps=c.episode_len, seed=c.seed)
            # a short description of the variant for the CSV
            variant = (f"N={c.N} M={c.M} Rcov={c.R_cov:.0f} "
                       f"Rcomm={c.R_comm:.0f} pads={c.n_pads} "
                       f"Bmax={c.B_max:.0f} fail={c.failure_enabled} "
                       f"clustered={c.start_clustered}")
            print(f"{sid}.{vi} ({question:16s}) {variant}  "
                  f"MAPPO CK={m['CK']:.3f} SC={m['SC']:.3f} "
                  f"CI={m['CovIntegral']:.3f} | "
                  f"Reactive CK={r['CK']:.3f} SC={r['SC']:.3f}", flush=True)
            rows.append(dict(scenario=sid, variant=vi, question=question,
                             config=variant,
                             mappo_CK=m["CK"], mappo_SC=m["SC"],
                             mappo_AG=m["AG"],
                             mappo_CovIntegral=m["CovIntegral"],
                             react_CK=r["CK"], react_SC=r["SC"],
                             react_AG=r["AG"],
                             react_CovIntegral=r["CovIntegral"]))
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"Saved -> {out_csv}")
    return rows