p = "scripts/eval_decentral_lookahead.py"
s = open(p, encoding="utf-8").read()

old = """    k = cfg.n_ego if hasattr(cfg, "n_ego") else 3
    # ego sensor block starts at index 4 (after pos(2)+batt(1)+mode(1))
    ego_start = 4
    ego_block = obs_i[ego_start:ego_start + 3 * k]
    bearings = []
    dists = []
    for j in range(k):
        bx = ego_block[3 * j + 0]
        by = ego_block[3 * j + 1]
        d = ego_block[3 * j + 2]
        bearings.append((bx, by))
        dists.append(d)

    # neighbour block: after ego block
    nb_start = ego_start + 3 * k
    # each neighbour: rel_x, rel_y, batt, mode (4 features) -- n_ego neighbours
    n_nb = cfg.n_ego if hasattr(cfg, "n_ego") else 3
    nb_block = obs_i[nb_start:nb_start + 4 * n_nb]"""

new = """    # Verified layout (env.local_obs, ego_sensors=True):
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
    nb_block = obs_i[nb_start:nb_start + 4 * n_nb]"""

assert old in s, "old parser block not found"
s = s.replace(old, new, 1)
open(p, "w", encoding="utf-8").write(s)
print("fixed parser offsets")