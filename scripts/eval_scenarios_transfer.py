"""Zero-shot scenario transfer for a scalable-identity actor.

One policy trained on the nominal configuration is evaluated, without any
retraining, on every scenario variant.  This is only valid when the actor's
observation dimension is independent of N, M and the pad count, i.e. when the
checkpoint was trained with use_scalable_id=True.  The script checks that and
refuses to run otherwise.

Writes ml_impl/results_scenarios_transfer.csv and prints the win tally.
"""
import argparse
import copy
import csv
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "ml_impl"))

from uav_wireless.env import UAVIoTEnv, obs_dim  # noqa: E402
from uav_wireless.experiments import (  # noqa: E402
    base_config, eval_agent, scenario_cfgs,
)
from uav_wireless.mappo import MAPPO  # noqa: E402
from uav_wireless.train import (  # noqa: E402
    baseline_reactive, baseline_reactive_local,
)


def actor_cfg(meta):
    c = base_config()
    c.ego_sensors = meta.get("ego", True)
    c.n_ego = meta.get("n_ego", 3)
    c.phy_ego_sensors = meta.get("phy_ego", False)
    c.use_critical_anchor = meta.get("anchor", False)
    c.use_scalable_id = meta.get("scalable_id", False)
    if "use_agent_id" in meta:
        c.use_agent_id = bool(meta["use_agent_id"])
    c.assist_return_mask = meta.get("assist_return", False)
    c.dist_shape_kappa = meta.get("shape", 0.0)
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="exp_v2")
    ap.add_argument("--out", default="ml_impl/results_scenarios_transfer.csv")
    ap.add_argument("--limit", type=int, default=0,
                    help="evaluate only the first N variants (0 = all)")
    a = ap.parse_args()

    rundir = os.path.join(ROOT, "ml_impl", "runs", a.tag)
    ckpts = sorted(glob.glob(os.path.join(rundir, "seed_*.pt")))
    if not ckpts:
        print("no checkpoints in", rundir)
        return 1
    meta = json.load(open(ckpts[0].replace(".pt", ".json"), encoding="utf-8"))
    if not meta.get("scalable_id", False):
        print("checkpoints were not trained with use_scalable_id; "
              "zero-shot transfer across N/M/pads is not defined")
        return 1

    cfg_actor = actor_cfg(meta)
    env0 = UAVIoTEnv(cfg_actor)
    dim = env0.obs_dim
    agents = []
    for ck in ckpts:
        ag = MAPPO(n_agents=cfg_actor.N, obs_dim=dim,
                   state_dim=env0.state_dim, device="cpu")
        ag.load_actor(ck)
        agents.append(ag)

    rows = []
    wins = losses = 0
    variants = []
    for sid, question, cfgs in scenario_cfgs(base_config()):
        for vi, c0 in enumerate(cfgs):
            variants.append((sid, vi, question, c0))
    if a.limit:
        variants = variants[:a.limit]

    for sid, vi, question, c0 in variants:
        c = copy.deepcopy(c0)
        if obs_dim(c) != dim:
            print(f"skip {sid}.{vi}: obs_dim {obs_dim(c)} != {dim}")
            continue
        evs = [eval_agent(ag, c, steps=c.episode_len, seed=c.seed)
               for ag in agents]
        m = float(np.mean([e["CK"] for e in evs]))
        r = baseline_reactive(c, steps=c.episode_len, seed=c.seed)
        rl = baseline_reactive_local(c, steps=c.episode_len, seed=c.seed)
        won = m > rl["CK"]
        wins += int(won)
        losses += int(not won)
        variant = (f"N={c.N} M={c.M} Rcov={c.R_cov:.0f} "
                   f"Rcomm={c.R_comm:.0f} pads={c.n_pads} "
                   f"Bmax={c.B_max:.0f} fail={c.failure_enabled} "
                   f"clustered={c.start_clustered}")
        rows.append(dict(
            scenario=sid, variant=vi, question=question, config=variant,
            mappo_CK=m, mappo_sd=float(np.std([e["CK"] for e in evs], ddof=1)),
            react_CK=r["CK"], reactlocal_CK=rl["CK"],
            delta_vs_local=m - rl["CK"],
            winner="MODEL" if won else "RULE",
            protocol="zero-shot transfer, 5 seeds, 2000 steps",
            train_seeds=len(agents),
        ))
        print(f"{sid}.{vi} {variant}  model {m:.3f}  local {rl['CK']:.3f}  "
              f"{'MODEL' if won else 'RULE'}", flush=True)

    out = os.path.join(ROOT, a.out)
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"\nvariant tally: MODEL {wins} - {losses} RULE")
    print("saved ->", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
