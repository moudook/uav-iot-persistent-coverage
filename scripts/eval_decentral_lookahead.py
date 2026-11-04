"""
Decentralised 1-hop lookahead (SI-3 Creative Experiment 1).

For each UAV i, instead of executing the actor's single sample, draw K
candidate actions from the actor, score each by a 100% local criterion
using only o_i(t) (ego-centric deficit bearings + neighbour relative
positions + critical-coverage tether), and execute the best per UAV.
No global simulator clone, no joint action search: CTDE-compliant.

The score for a candidate action a_i:
  + sum over the k nearest under-covered sensors of  cos(angle between
    the action's velocity and the bearing to that sensor) / (d_j + eps)
    (rewards moving toward nearby deficits)
  - connectivity penalty if the new position would leave R_comm of a
    1-hop neighbour (using neighbour relative positions from the obs)
  - critical-tether penalty if UAV i currently covers a sensor with
    n_d == K and the action moves away from that sensor's direction

Run:
    python scripts/eval_decentral_lookahead.py --tag exp_ego_eval \\
        --eval-offset 1000 --eval-seeds 2 --steps 200 --K 4
"""
import argparse
import copy
import glob
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ml_impl"))
for _v in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np
import torch

from uav_wireless.env import UAVIoTEnv, SimConfig
from uav_wireless.experiments import base_config
from uav_wireless.mappo import MAPPO

# action -> velocity mapping (cardinal directions, v_max scaled)
# actions: 0=HOVER, 1=+x, 2=-x, 3=+y, 4=-y, 5=CHARGE
VEL = np.array([[0.0, 0.0], [1.0, 0.0], [-1.0, 0.0],
                [0.0, 1.0], [0.0, -1.0], [0.0, 0.0]], dtype=float)


def action_masks_safe(env):
    mask = np.stack(env.action_masks())
    for i in range(env.cfg.N):
        if mask[i].sum() == 0:
            mask[i, 0] = True
    return mask


def local_score(obs_i, mask_i, cand_action, cfg):
    """Score a single candidate action for UAV i using only its local obs.

    obs_i layout (ego_sensors=True, k=3):
      [0:2]   position (normalised)
      [2]     battery
      [3]     mode
      [4:4+3*3]  k nearest deficits: for each j: bearing_x, bearing_y, dist_norm
      ...     neighbour block: for each neighbour: rel_x, rel_y, batt, mode
      ...     pad bearings etc.

    We parse the obs defensively by recomputing from cfg rather than
    hard-coding offsets, because the obs layout has several variants.
    """
    # Verified layout (env.local_obs, ego_sensors=True):
    #   [0:7]    own: p_x, p_y, v_x, v_y, E, mode, pad_assigned
    #   [7:23]   neighbours: NB_SLOTS=4 slots x 4 fields (rel_x, rel_y, E, d_norm)
    #   [23:30]  tail: nb_count, local_cov_frac, bridge, reserve_gap, pad_energy, wait, const
    #   [30:30+3k+2]  ego: k deficit bearings (unit x, unit y, dist_norm) + repulsion (x, y)
    #   [+1]     critical anchor (if use_critical_anchor)
    OWN_SZ = 7
    NB_SLOTS = 4
    TAIL_SZ = 7
    k = cfg.n_ego if hasattr(cfg, "n_ego") else 3
    ego_start = OWN_SZ + NB_SLOTS * 4 + TAIL_SZ   # 30
    nb_start = OWN_SZ                              # 7
    ego_block = obs_i[ego_start:ego_start + 3 * k]
    bearings = []
    dists = []
    for j in range(k):
        bx = ego_block[3 * j + 0]
        by = ego_block[3 * j + 1]
        d = ego_block[3 * j + 2]
        bearings.append((bx, by))
        dists.append(d)

    n_nb = NB_SLOTS
    nb_block = obs_i[nb_start:nb_start + 4 * n_nb]

    v = VEL[cand_action]
    vnorm = np.linalg.norm(v)
    if vnorm > 0:
        v = v / vnorm

    # score: move toward nearby deficits
    score = 0.0
    for (bx, by), d in zip(bearings, dists):
        bnorm = np.sqrt(bx * bx + by * by)
        if bnorm < 1e-6:
            continue
        bn = (bx / bnorm, by / bnorm)
        # reward for moving toward deficit, weighted by proximity (1/(d+eps))
        cos_sim = v[0] * bn[0] + v[1] * bn[1]
        w = 1.0 / (d + 0.1)
        score += w * cos_sim

    # critical-tether: if obs indicates the UAV covers a critical sensor,
    # the obs has an anchor dim at the end (if use_critical_anchor). Penalise
    # moving away from the tether direction.  We approximate the tether as
    # the mean bearing of deficits that are very close (d < 0.3).
    close_bearings = [(bx, by) for (bx, by), d in zip(bearings, dists) if d < 0.3]
    if close_bearings:
        tx = np.mean([b[0] for b in close_bearings])
        ty = np.mean([b[1] for b in close_bearings])
        tnorm = np.sqrt(tx * tx + ty * ty)
        if tnorm > 1e-6:
            tn = (tx / tnorm, ty / tnorm)
            # if moving away from tether, penalise
            cos_tether = v[0] * tn[0] + v[1] * tn[1]
            score -= 0.5 * max(0.0, -cos_tether)  # penalty for moving away

    # connectivity penalty: if any neighbour is close to R_comm boundary,
    # penalise moving away from them
    for j in range(n_nb):
        rx = nb_block[4 * j + 0]
        ry = nb_block[4 * j + 1]
        rnorm = np.sqrt(rx * rx + ry * ry)
        if rnorm < 1e-6:
            continue
        # neighbour is at relative (rx, ry); if we move away, distance increases
        # penalty if current relative distance is large (near comm boundary)
        # and action increases it
        if rnorm > 0.6:  # near boundary (normalised)
            # direction away from neighbour
            away = (rx / rnorm, ry / rnorm)
            cos_away = v[0] * away[0] + v[1] * away[1]
            if cos_away > 0:  # moving away
                score -= 0.3 * cos_away

    # hover bonus: small preference for not moving if no clear deficit
    if cand_action == 0:
        score += 0.05

    return score


def decentral_eval(agent, cfg, steps, seed):
    c = copy.deepcopy(cfg)
    c.seed = seed
    env = UAVIoTEnv(c)
    obs, _ = env.reset()
    n = 0
    while n < steps:
        mask = action_masks_safe(env)
        obs_arr = np.asarray(obs, dtype=np.float32)
        # per-UAV action selection
        acts = np.zeros(env.cfg.N, dtype=np.int64)
        for i in range(env.cfg.N):
            obs_i = obs_arr[i]
            mask_i = mask[i]
            # sample K candidates from this UAV's actor
            obs_t = torch.as_tensor(obs_i, dtype=torch.float32).unsqueeze(0)
            mask_t = torch.as_tensor(mask_i, dtype=torch.bool).unsqueeze(0)
            with torch.no_grad():
                logits = agent.masked_logits(obs_t, mask_t)
                logp = torch.log_softmax(logits, dim=-1)
                dist = torch.distributions.Categorical(logits=logp)
            cands = dist.sample((4,)).squeeze(-1).cpu().numpy()  # K=4
            # score each candidate locally
            best_a = int(cands[0])
            best_sc = -1e18
            for cand in cands:
                sc = local_score(obs_i, mask_i, int(cand), cfg)
                if sc > best_sc:
                    best_sc = sc
                    best_a = int(cand)
            acts[i] = best_a
        obs, _, r, done, _ = env.step(acts)
        n += 1
        if done:
            break
    return float(env.summary().get("CK", 0.0))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="exp_ego_eval")
    ap.add_argument("--eval-offset", type=int, default=1000)
    ap.add_argument("--eval-seeds", type=int, default=5)
    ap.add_argument("--steps", type=int, default=500)
    ap.add_argument("--K", type=int, default=4)
    ap.add_argument("--out", default="")
    a = ap.parse_args()

    rundir = os.path.join(os.path.dirname(__file__), "..", "ml_impl", "runs", a.tag)
    ckpts = sorted(glob.glob(os.path.join(rundir, "seed_*.pt")))
    if not ckpts:
        print("no checkpoints")
        return 1
    scenes = list(range(a.eval_offset, a.eval_offset + a.eval_seeds))
    print("decentral lookahead on %d scenes x %d ckpts" % (len(scenes), len(ckpts)), flush=True)

    results = {}
    t0 = time.time()
    for ck in ckpts:
        meta = json.load(open(ck.replace(".pt", ".json"), encoding="utf-8"))
        cfg = base_config()
        cfg.ego_sensors = meta.get("ego", False)
        cfg.n_ego = meta.get("n_ego", 3)
        cfg.dist_shape_kappa = meta.get("shape", 0.0)
        cfg.use_w_penalty = meta.get("use_w", True)
        cfg.use_critical_anchor = meta.get("anchor", False)
        cfg.episode_len = a.steps
        env = UAVIoTEnv(cfg)
        agent = MAPPO(n_agents=cfg.N, obs_dim=env.obs_dim,
                      state_dim=env.state_dim, device="cpu")
        agent.load(ck)
        cks = []
        for s in scenes:
            cks.append(decentral_eval(agent, cfg, a.steps, s))
        name = os.path.basename(ck)
        results[name] = {"mean": float(np.mean(cks)),
                         "std": float(np.std(cks, ddof=1)) if len(cks) > 1 else 0.0,
                         "per_scene": cks}
        print("%-14s decentral CK=%.4f (sd %.4f)  [%.0fs]"
              % (name, results[name]["mean"], results[name]["std"], time.time() - t0), flush=True)

    means = [r["mean"] for r in results.values()]
    summary = {"tag": a.tag, "steps": a.steps, "scenes": scenes,
               "per_checkpoint": results,
               "mean_over_seeds": float(np.mean(means)),
               "sd_over_seeds": float(np.std(means, ddof=1)) if len(means) > 1 else 0.0,
               "n_seeds": len(means)}
    out = a.out or os.path.join(rundir, "eval_decentral_lookahead.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=1)
    print("\nmean over %d seeds = %.4f (sd %.4f)" % (len(means), summary["mean_over_seeds"], summary["sd_over_seeds"]))
    print("wrote", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
