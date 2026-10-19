"""
Dec-POMDP environment for persistent, fault-tolerant UAV-IoT coverage.

Implements Section III of Mlawn_midsem_report_FINAL:
  A. system architecture      B. Dec-POMDP formulation
  C. global state (3)         D. local observation (4)
  E. discrete actions (5,6)   F. persistent K-coverage (7-10)
  G. connectivity + articulation points (11-13)
  H. battery model (14-16)    I. charging arbitration (17-18)
  J. safety constraints (19)  K. failure and recovery (20)
  L. team reward (23) + weights from Table IV
  M. parameters from Table VI / VII

Every coverage and connectivity quantity is PHY-derived via wireless.py.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
import numpy as np

from .wireless import WirelessModel, los_probability

# --------------------------------------------------------------------------
# Actions (Table III)
# --------------------------------------------------------------------------
A_HOVER, A_PX, A_NX, A_PY, A_NY, A_CHARGE = range(6)
N_ACTIONS = 6
ACTION_VECTORS = np.array(
    [[0.0, 0.0], [1.0, 0.0], [-1.0, 0.0], [0.0, 1.0], [0.0, -1.0], [0.0, 0.0]]
)


@dataclass
class SimConfig:
    # Table VI
    N: int = 5                    # active UAVs
    N_reserve: int = 1
    M: int = 20                   # IoT sensors
    side: float = 80.0            # Omega = 80 x 80 m^2
    R_cov: float = 35.0           # coverage radius
    R_comm: float = 40.0          # communication radius (geometric cap)
    z0: float = 50.0              # nominal altitude
    K: int = 2                    # coverage redundancy target
    dt: float = 0.2               # control interval
    v_max: float = 5.0
    d_safe: float = 5.0
    B_max: float = 30_000.0       # J
    P_hover: float = 50.0         # W
    P_move: float = 75.0          # W
    P_elec: float = 5.0           # W  avionics + comms
    P_tx: float = 0.5             # W  RF transmit
    charge_rate: float = 0.0002   # battery fraction per step
    episode_len: int = 1_000      # steps (report uses 10000 = 2000 s)
    n_pads: int = 2               # S, charging pads
    pad_service_radius: float = 15.0
    E_reserve: float = 2_000.0    # J kept in reserve
    failure_enabled: bool = False
    failure_time: int = -1        # -1 = disabled
    # Table IV weights
    lam_O: float = 1.00           # under-coverage
    lam_E: float = 0.10           # energy consumption
    # Degraded service is the JOINT condition (K-coverage AND connectivity).
    # The draft's 0.50 was below lam_O, so the learner happily traded
    # connectivity for coverage gain. Raised so that violating either
    # invariant dominates, matching the "service first" intent of Table IV.
    lam_D: float = 2.00           # degraded service
    lam_W: float = 0.05           # unnecessary movement
    lam_R: float = 0.30           # recovery delay
    lam_C: float = 0.50           # articulation-point criticality
    # ablations (Table VIII / vanilla MAPPO)
    use_connectivity_term: bool = True
    use_reserve: bool = True
    use_charging_arbitration: bool = True
    use_action_mask: bool = True
    mask_horizon: int = 3         # H-step connectivity lookahead in the mask
    # Initial deployment.  False: a centred ring that already covers most of
    # the field (little headroom).  True: a connected cluster in one corner
    # that covers little, so the policy must deploy while keeping the graph
    # connected -- the regime in which the constraint actually binds.
    start_clustered: bool = False
    seed: int = 0

    def dict(self):
        return asdict(self)


def obs_dim(cfg: SimConfig) -> int:
    """Length of the per-agent observation for this configuration (Eq. 4)."""
    return 7 + 4 * 4 + 7          # own(7) + 4 neighbour slots x 4 + tail(7)


def state_dim(cfg: SimConfig) -> int:
    """Length of the centralised critic input for this configuration (Eq. 3)."""
    return 2 * cfg.N + 3 * cfg.N + 2 * cfg.M + cfg.n_pads + 3


class UAVIoTEnv:
    """Cooperative persistent-coverage Dec-POMDP."""

    #: Number of neighbour slots in the local observation (Eq. 4).
    NB_SLOTS = 4

    # Local observation layout (Eq. 4), built by concatenation:
    #   7  own state  [x, y, vx, vy, battery, mode, pad_assigned]
    #   16 4 neighbour slots x [dx, dy, battery_j, distance]
    #   7  [n_neighbours, local_coverage, bridge_risk,
    #       return_urgency, pad_energy, charging_wait, active]
    OBS_DIM = 7 + 4 * NB_SLOTS + 7          # = 30

    # Global state layout (Eq. 3), built by concatenation:
    #   2N positions, N battery, N mode, N failed, 2M sensors, n_pads, 3 scalars
    # For the reference configuration (N=5, M=20, n_pads=2) this is
    # 10 + 15 + 40 + 2 + 3 = 70. Kept as a constant so code that only knows the
    # default config keeps working; always prefer `env.state_dim` or
    # `state_dim(cfg)`, which are correct for every configuration. The previous
    # value, 80, was correct only for N=5 and raised for N >= 8.
    STATE_DIM = 2 * 5 + 3 * 5 + 2 * 20 + 2 + 3      # = 70 for N=5, M=20

    def __init__(self, cfg: SimConfig):
        self.cfg = cfg
        self.rng = np.random.default_rng(cfg.seed)
        self.radio = WirelessModel(z0=cfg.z0, p_tx=cfg.P_tx)
        self.obs_dim = obs_dim(cfg)
        self.state_dim = state_dim(cfg)
        self.reset()

    # ------------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------------
    def reset(self):
        c = self.cfg
        self.t = 0
        # Initial deployment must be FEASIBLE. Uniformly random positions left
        # the swarm disconnected on 11/20 seeds, which makes SC>0 unreachable
        # regardless of policy quality -- the learner cannot recover from an
        # infeasible start. UAVs are therefore seeded as a connected cluster
        # (ring + centre) and the connectivity invariant is checkable from t=0.
        self.p = self._connected_initial_positions()
        self.v = np.zeros((c.N, 2))
        self.E = self.rng.uniform(0.7, 1.0, size=c.N) * c.B_max
        self.failed = np.zeros(c.N, dtype=bool)
        self.mode = np.zeros(c.N, dtype=int)          # 0 serve, 1 return, 2 charge
        self.pad_assigned = np.full(c.N, -1, dtype=int)
        self.pad_queue = np.zeros(c.n_pads, dtype=int)
        self.pad_occupied_by = np.full(c.n_pads, -1, dtype=int)

        self.sensors = self.rng.uniform(0, c.side, size=(c.M, 2))
        self.pads = self.rng.uniform(0.15 * c.side, 0.85 * c.side, size=(c.n_pads, 2))

        # Draw the episode's propagation environment once. Seeded from the
        # episode seed but fed through a separate stream, so shadowing draws
        # never perturb the env's own RNG (and vice versa) -- otherwise the
        # physics would leak into action sampling and runs would not replay.
        self.radio.reset_links(c.N, c.M, seed=(int(c.seed) * 1_000_003 + 17))

        self.reserve_used = 0
        self.failure_t = c.failure_time if c.failure_time >= 0 else -1
        if c.failure_enabled and c.failure_time < 0:
            self.failure_t = int(self.rng.integers(c.episode_len // 3, c.episode_len))

        self._history_len = 6
        self.prev_cov_score = 0.0
        self.prev_w_dist = 0.0
        self.last_cost = dict(U_t=1.0, E_t=0.0, D_t=1.0, W_t=0.0, R_t=0.0, Crit_t=1.0)
        self.recovery_start = -1
        self.recovered = True
        self.charging_wait = np.zeros(c.N)
        self.denied_charge = 0

        self.ep = self.metrics()
        self._under_streak = 0
        self.truncated = False
        self.terminated = False
        self.prev_metrics = dict(self.ep)
        return self.local_obs(), self.global_state()

    # ------------------------------------------------------------------
    # PHY-derived coverage and connectivity
    # ------------------------------------------------------------------
    def _connected_initial_positions(self):
        """Place N UAVs so the communication graph is connected from t=0.

        Two deployments are supported.

        ``start_clustered=False`` (default): a ring of radius R_local centred
        in the region, plus any extra UAVs inside the ring.  R_local is
        chosen as a fraction of R_comm so that every ring neighbour is well
        within communication range even after the PHY rate check.  This is
        the deployment a dispatcher would actually use, but it has a
        property worth stating: on an 80x80 m field with R_cov = 35 m the
        ring already covers most of the sensor set, so the achievable range
        for any controller is roughly [0.9, 1.0] and the task has little
        headroom.

        ``start_clustered=True``: every UAV starts in one connected blob
        near a corner.  The swarm is connected from t=0 (so the invariant
        is still checkable) but the initial coverage is low, and the policy
        has to deploy across the field while keeping the graph connected.
        This is the standard benchmark arrangement for persistent coverage
        and it is the regime in which the connectivity constraint and the
        feasibility mask actually bind.
        """
        c = self.cfg
        if c.start_clustered:
            # A tight connected chain: consecutive UAVs are one hop apart,
            # so the graph is connected, but the blob covers only a small
            # part of the field.
            r_local = min(0.25 * c.R_comm, 0.12 * c.side)
            corner = np.array([0.15 * c.side, 0.15 * c.side])
            n_ring = max(c.N - 1, 1)
            ang = np.linspace(0, 2 * np.pi, n_ring, endpoint=False)
            pos = [corner + r_local * np.array([np.cos(a), np.sin(a)])
                   for a in ang]
            while len(pos) < c.N:
                pos.append(corner + self.rng.normal(0, 0.08 * r_local, size=2))
            pos = np.array(pos[: c.N])
            return np.clip(pos, 0.0, c.side)

        centre = np.array([c.side / 2.0, c.side / 2.0])
        r_local = min(0.45 * c.R_comm, 0.30 * c.side)
        n_ring = max(c.N - 1, 1)
        ang = np.linspace(0, 2 * np.pi, n_ring, endpoint=False)
        pos = [centre + r_local * np.array([np.cos(a), np.sin(a)]) for a in ang]
        while len(pos) < c.N:                      # extra UAVs fill the centre
            pos.append(centre + self.rng.normal(0, 0.1 * r_local, size=2))
        pos = np.array(pos[: c.N])
        return np.clip(pos, 0.0, c.side)

    def _active_idx(self):
        return np.where(~self.failed)[0]

    def coverage_counts(self):
        """n_d(t) for each sensor: how many ACTIVE UAVs can actually SERVE it."""
        act = self._active_idx()
        if len(act) == 0:
            return np.zeros(self.cfg.M)
        # geometric ceiling first
        d = np.linalg.norm(self.sensors[:, None, :] - self.p[act][None, :, :], axis=-1)
        within = d <= self.cfg.R_cov
        # PHY gate: a UAV only "counts" if ITS OWN serving link clears the rate
        # threshold. Each sensor has a serving UAV (the strongest receiver), so
        # evaluate the SINR per (sensor, uav) pair rather than once per sensor.
        sinr = self._access_sinr_matrix(self.p[act], self.sensors, act)   # (M, K)
        rate = self.radio.rate_mbps(self.radio.snr_db(sinr))              # (M, K)
        phy_ok = rate >= self.radio.rate_min_mbps                         # (M, K)
        usable = within & phy_ok
        return usable.sum(axis=1)

    def _access_sinr_matrix(self, uav_xy, sensor_xy, uav_idx):
        """(M, K) SINR of every sensor->UAV pair, with inter-UAV interference.

        The report's K-coverage counts how many UAVs can *simultaneously serve*
        a sensor, so we need a per-pair value rather than a single best-SINR
        number. Each UAV is treated as an interfering transmitter for the
        others, so serving with more UAVs costs SINR -- which is exactly the
        interference effect the experiment is meant to expose.

        `uav_idx` are the GLOBAL ids of the UAVs in `uav_xy`, used to look up
        each link's shadowing by identity rather than by position.
        """
        return self.radio.access_sinr(sensor_xy, uav_xy, uav_idx)

    def comm_graph(self):
        """Adjacency + SNR matrix over active UAVs."""
        act = self._active_idx()
        n = len(act)
        if n == 0:
            return act, np.zeros((0, 0), dtype=bool), np.zeros((0, 0))
        snr_lin = self.radio.backhaul_snr(self.p[act], act)
        snr = self.radio.snr_db(snr_lin)
        rate = self.radio.link_rate_mbps(snr, backhaul=True)
        d = np.linalg.norm(self.p[act][:, None, :] - self.p[act][None, :, :], axis=-1)
        adj = (d <= self.cfg.R_comm) & (rate >= self.radio.rate_min_mbps)
        np.fill_diagonal(adj, False)
        return act, adj, snr

    @staticmethod
    def articulation_points(adj: np.ndarray) -> np.ndarray:
        """Tarjan articulation points of an undirected graph. Eq. (12)."""
        n = len(adj)
        if n < 3:
            return np.zeros(n, dtype=bool)
        disc = [-1] * n
        low = [0] * n
        parent = [-1] * n
        ap = np.zeros(n, dtype=bool)
        timer = [0]

        def dfs(u):
            disc[u] = low[u] = timer[0]
            timer[0] += 1
            children = 0
            for v in range(n):
                if not adj[u, v]:
                    continue
                if disc[v] == -1:
                    parent[v] = u
                    children += 1
                    dfs(v)
                    low[u] = min(low[u], low[v])
                    if parent[u] == -1 and children > 1:
                        ap[u] = True
                    if parent[u] != -1 and low[v] >= disc[u]:
                        ap[u] = True
                elif v != parent[u]:
                    low[u] = min(low[u], disc[v])

        for u in range(n):
            if disc[u] == -1:
                dfs(u)
        return ap

    def is_connected(self, adj: np.ndarray) -> bool:
        n = len(adj)
        if n == 0:
            return False
        if n == 1:
            return True
        visited = np.zeros(n, dtype=bool)
        stack = [0]
        visited[0] = True
        while stack:
            u = stack.pop()
            for v in range(n):
                if adj[u, v] and not visited[v]:
                    visited[v] = True
                    stack.append(v)
        return visited.all()

    # ------------------------------------------------------------------
    # Battery
    # ------------------------------------------------------------------
    def power_draw(self, actions):
        c = self.cfg
        p = np.where(
            np.isin(actions, [A_PX, A_NX, A_PY, A_NY]),
            c.P_move,
            c.P_hover,
        )
        return p + c.P_elec + c.P_tx     # P_comm / P_elec, constant baseline

    def pad_energy(self, i):
        """E^pad_i: energy to reach the nearest feasible pad. Eq. (16)."""
        if len(self.pads) == 0:
            return 0.0
        d = np.linalg.norm(self.pads - self.p[i], axis=1)
        d_min = float(np.min(d))
        t = d_min / self.cfg.v_max
        return t * (self.cfg.P_move + self.cfg.P_elec) * 1.15

    def return_threshold(self, i):
        return self.pad_energy(i) + self.cfg.E_reserve

    # ------------------------------------------------------------------
    # Charging arbitration (Hungarian-style). Eq. (17)-(18)
    # ------------------------------------------------------------------
    def arbitrate(self, requests):
        if not requests:
            return {}
        if not self.cfg.use_charging_arbitration:
            return {requests[0]: 0} if len(self.pads) else {}

        n_pads = len(self.pads)
        max_q = max(self.pad_queue.max(), 1)
        cost = np.zeros((len(requests), n_pads))
        for a, i in enumerate(requests):
            d = np.linalg.norm(self.pads - self.p[i], axis=1)
            urgency = 1.0 - self.E[i] / self.cfg.B_max
            for s in range(n_pads):
                cost[a, s] = (
                    1.0 * (d[s] / self.cfg.side)
                    + 0.5 * (self.pad_queue[s] / max_q)
                    + 1.0 * urgency
                )
        from scipy.optimize import linear_sum_assignment

        rows, cols = linear_sum_assignment(cost)
        assign = {}
        for r, s in zip(rows, cols):
            i = requests[r]
            if self.pad_occupied_by[s] == -1:
                assign[i] = s
                self.pad_occupied_by[s] = i
            else:
                self.denied_charge += 1
        return assign

    # ------------------------------------------------------------------
    # Action feasibility mask. Section IV-B / Table V
    # ------------------------------------------------------------------
    def action_mask(self, i):
        c = self.cfg
        m = np.zeros(N_ACTIONS, dtype=bool)
        m[A_HOVER] = True

        act = self._active_idx()
        others = act[act != i]
        step = c.v_max * c.dt
        for a_dir, a in enumerate([A_PX, A_NX, A_PY, A_NY], start=1):
            p_new = np.clip(self.p[i] + ACTION_VECTORS[a] * step, 0, c.side)
            ok = True
            # workspace: reject moves that would leave the region
            if np.any(p_new < 0) or np.any(p_new > c.side):
                ok = False
            # separation
            if ok and len(others):
                if np.min(np.linalg.norm(p_new - self.p[others], axis=1)) < c.d_safe:
                    ok = False
            # energy reachability
            if ok and self.E[i] - c.P_move * c.dt <= 0:
                ok = False
            # connectivity preservation: block moves that would break the
            # graph NOW *or* leave it fragile. A one-step check alone lets
            # the swarm walk itself into a partition, which is exactly what
            # the first experiment run showed (AG collapsed 1.0 -> 0.2).
            if ok and c.use_action_mask:
                if not self._h_step_safe(i, p_new, c.mask_horizon):
                    ok = False
                elif self._is_articulation_move(i, p_new):
                    ok = False
            m[a] = ok

        # charge: must be inside a pad service region and energy must be low
        near = np.any(np.linalg.norm(self.pads - self.p[i], axis=1) <= c.pad_service_radius)
        needs = self.E[i] <= self.return_threshold(i)
        m[A_CHARGE] = bool(near and needs)
        return m

    def _is_articulation_move(self, i, p_new):
        """True if moving to p_new makes UAV i a cut vertex of the graph.

        Staying connected at t+1 is not enough: if the swarm only survives
        while one particular UAV sits in the middle, the next move may split
        it. Blocking articulation-forming moves gives the policy room to
        re-spread instead of tunnelling.
        """
        act = self._active_idx()
        if len(act) <= 3:
            return False
        saved = self.p[i].copy()
        self.p[i] = p_new
        _, adj, _ = self.comm_graph()
        self.p[i] = saved
        pos_i = list(act).index(i)
        ap = self.articulation_points(adj)
        return bool(pos_i < len(ap) and ap[pos_i])

    def _h_step_safe(self, i, p_new, horizon=3):
        """Reject a move that leaves the swarm unable to stay connected.

        One-step lookahead cannot see a partition that forms two steps later,
        which is exactly how the swarm walked itself apart in the first
        experiment run (AG 1.0 -> 0.2). This checks the pessimistic case: after
        moving, can every other active UAV still reach UAV i within `horizon`
        communication hops? If the answer is no, the move is infeasible.
        """
        act = self._active_idx()
        if len(act) <= 2:
            return True
        saved = self.p[i].copy()
        self.p[i] = p_new
        _, adj, _ = self.comm_graph()
        self.p[i] = saved
        if not self.is_connected(adj):
            return False
        # BFS hop-distance from UAV i; every node must be within `horizon` hops
        n = len(adj)
        pos_i = list(act).index(i)
        dist = np.full(n, -1, dtype=int)
        dist[pos_i] = 0
        queue = [pos_i]
        while queue:
            u = queue.pop(0)
            if dist[u] >= horizon:
                continue
            for v in range(n):
                if adj[u, v] and dist[v] < 0:
                    dist[v] = dist[u] + 1
                    queue.append(v)
        return bool((dist >= 0).all())

    def _would_disconnect(self, i, p_new):
        """True if moving UAV i to p_new partitions the swarm graph."""
        act = self._active_idx()
        if len(act) <= 2:
            return False
        saved = self.p[i].copy()
        self.p[i] = p_new
        _, adj, _ = self.comm_graph()
        self.p[i] = saved
        return not self.is_connected(adj)

    # ------------------------------------------------------------------
    # Observations
    # ------------------------------------------------------------------
    def local_obs(self):
        """o_i(t) = [p_i, v_i, b_i, N_i, C_i^local, rho_i, tau_i^return, E_i^pad]. Eq. (4).

        The vector is built by concatenation and then checked against
        `self.obs_dim`. The previous revision wrote into a preallocated array
        with a stride of 2 while storing 4 values per neighbour, so neighbour
        slots overlapped each other and neighbour 3 overwrote the neighbour
        count and the local coverage count. The actor was trained on a
        corrupted observation. Building by concatenation makes that class of
        bug impossible, and the assertion makes any future mismatch loud
        instead of silent.
        """
        c = self.cfg
        act, adj, _ = self.comm_graph()
        ncov = self.coverage_counts()
        ap = self.articulation_points(adj) if len(adj) else np.zeros(0, bool)

        rows = []
        for i in range(c.N):
            if self.failed[i]:
                rows.append(np.zeros(self.obs_dim, dtype=np.float32))
                continue

            own = np.array([
                self.p[i][0] / c.side,
                self.p[i][1] / c.side,
                self.v[i][0] / c.v_max,
                self.v[i][1] / c.v_max,
                self.E[i] / c.B_max,
                self.mode[i] / 2.0,
                1.0 if self.pad_assigned[i] >= 0 else 0.0,
            ], dtype=np.float32)

            # four nearest neighbours within R_comm, each 4 fields
            near = []
            for j in act:
                if j == i:
                    continue
                d = float(np.linalg.norm(self.p[j] - self.p[i]))
                if d <= c.R_comm:
                    near.append((j, d))
            near.sort(key=lambda z: z[1])
            nb = np.zeros(4 * self.NB_SLOTS, dtype=np.float32)
            for k, (j, d) in enumerate(near[: self.NB_SLOTS]):
                rel = (self.p[j] - self.p[i]) / c.R_comm
                nb[4 * k + 0] = rel[0]
                nb[4 * k + 1] = rel[1]
                nb[4 * k + 2] = self.E[j] / c.B_max
                nb[4 * k + 3] = d / c.R_comm

            # local bridge risk rho_i: is any neighbour a cut vertex locally?
            # adj rows/cols are indexed by POSITION within `act`, not by the
            # global UAV id, so translate before indexing.
            pos_i = list(act).index(i)
            deg = int(adj[pos_i].sum()) if len(adj) else 0
            bridge = 1.0 if (0 < deg <= 2) else 0.0
            for k, j in enumerate([x for x in act if x != i][:4]):
                idx = list(act).index(j)
                if idx < len(ap) and ap[idx]:
                    bridge = max(bridge, 1.0 - 0.25 * k)

            d_s = np.linalg.norm(self.sensors - self.p[i], axis=1)
            thresh = self.return_threshold(i)
            tail = np.array([
                min(len(near), self.NB_SLOTS) / self.NB_SLOTS,
                float(np.sum(d_s <= c.R_cov)) / max(c.M, 1),
                bridge,
                np.clip((thresh - self.E[i]) / max(thresh, 1.0), -1, 1),
                self.pad_energy(i) / c.B_max,
                np.clip(self.charging_wait[i] / 200.0, 0, 1),
                1.0,
            ], dtype=np.float32)

            rows.append(np.concatenate([own, nb, tail]))

        obs = np.stack(rows).astype(np.float32)
        if obs.shape[1] != self.obs_dim:
            raise AssertionError(
                f"local_obs produced {obs.shape[1]} features but obs_dim is "
                f"{self.obs_dim}; the observation layout and the declared "
                f"dimension have diverged"
            )
        return obs

    def global_state(self):
        """s_t for the centralized critic. Eq. (3).

        Built by concatenation and checked, for the same reason as
        `local_obs`: the previous revision wrote into a fixed-size buffer of
        `STATE_DIM = 80`, which is only large enough for N = 5. At N = 8 the
        pad-occupancy slice ran past the end of the array and raised, and
        between those sizes it would have been silently misaligned.
        """
        c = self.cfg
        parts = [
            (self.p / c.side).flatten(),          # 2N
            self.E / c.B_max,                     # N
            self.mode / 2.0,                      # N
            self.failed.astype(float),            # N
            (self.sensors / c.side).flatten(),    # 2M
            (self.pad_occupied_by >= 0).astype(float),   # n_pads
            np.array([
                self.reserve_used / max(c.N_reserve, 1),
                self.t / c.episode_len,
                1.0 if self.is_connected(self.comm_graph()[1]) else 0.0,
            ]),
        ]
        s = np.concatenate([np.asarray(p, dtype=np.float32).ravel() for p in parts])
        if s.shape[0] != self.state_dim:
            raise AssertionError(
                f"global_state produced {s.shape[0]} features but state_dim is "
                f"{self.state_dim}; the state layout and the declared dimension "
                f"have diverged"
            )
        return s

    # ------------------------------------------------------------------
    # Step
    # ------------------------------------------------------------------
    def step(self, actions):
        c = self.cfg
        act_before = self._active_idx().copy()

        # --- 1. motion with safety projection --------------------------
        step = c.v_max * c.dt
        for i in self._active_idx():
            a = int(actions[i])
            if a in (A_PX, A_NX, A_PY, A_NY):
                self.v[i] = ACTION_VECTORS[a] * c.v_max
            elif a == A_CHARGE:
                self.v[i] = np.zeros(2)
            else:
                self.v[i] = np.zeros(2)
            p_new = np.clip(self.p[i] + self.v[i] * c.dt, 0, c.side)
            if np.all(self.action_mask(i)):
                self.p[i] = p_new
            elif a in (A_PX, A_NX, A_PY, A_NY):
                pass    # masked movement -> hold position (mask made this infeasible)

        # --- 2. failure injection --------------------------------------
        if self.failure_t >= 0 and self.t == self.failure_t:
            victim = act_before[self.rng.integers(len(act_before))]
            self.failed[victim] = True
            self.mode[victim] = -1
            self.recovered = False
            self.recovery_start = self.t
            self.failure_t = -1
            self.recovered = False
        elif c.use_reserve and self.reserve_used < c.N_reserve and not self.recovered:
            # activate reserve
            self.reserve_used += 1
            self.failed = self.failed.copy()
            # re-seat one failed slot with a fresh UAV at a pad
            dead = np.where(self.failed)[0]
            if len(dead):
                j = int(dead[0])
                self.p[j] = self.pads[self.rng.integers(len(self.pads))]
                self.E[j] = c.B_max
                self.failed[j] = False
                self.mode[j] = 0
                self.recovered = False

        # --- 3. charging arbitration -----------------------------------
        self.pad_occupied_by = np.full(len(self.pads), -1)
        requests = []
        for i in self._active_idx():
            if int(actions[i]) == A_CHARGE:
                requests.append(int(i))
        assign = self.arbitrate(requests)
        for i, s in assign.items():
            self.pad_assigned[i] = s
            self.mode[i] = 2
            self.E[i] = min(c.B_max, self.E[i] + c.charge_rate * c.B_max)
        for i in self._active_idx():
            if i not in assign:
                self.pad_assigned[i] = -1
                if self.mode[i] == 2:
                    self.mode[i] = 0
                self.charging_wait[i] = min(self.charging_wait[i] + 1, 999)
                if self.charging_wait[i] > 150:
                    self.charging_wait[i] = 0

        # --- 4. battery update (14)-(15) -------------------------------
        draw = self.power_draw(actions)
        self.E = np.clip(self.E - draw * c.dt, 0, c.B_max)
        for i in range(c.N):
            if self.failed[i]:
                self.E[i] = 0.0

        self.t += 1

        # --- 5. recovery detection -------------------------------------
        ncov = self.coverage_counts()
        _, adj, _ = self.comm_graph()
        connected_now = self.is_connected(adj)
        # D_t must not duplicate U_t. U_t already carries coverage continuously,
        # so the binary "service requirement violated" indicator is used for the
        # CONNECTIVITY invariant -- the one that collapsed to 0.2 and left
        # SC = 0 in the first run. This gives the learner a discrete, learnable
        # signal for the thing it was previously not being told about.
        degraded_now = not connected_now
        ok_now = (float(np.mean(ncov >= c.K)) >= 1.0) and connected_now
        if not self.recovered and ok_now:
            self.recovered = True
        rec_delay = 0.0
        if self.recovery_start >= 0 and self.recovered:
            rec_delay = min((self.t - self.recovery_start) / c.episode_len, 1.0)

        # --- 6. reward (23) --------------------------------------------
        #
        # Eq. (22) is a MINIMISATION of a weighted cost. Eq. (23) states the
        # team reward is the NEGATED weighted cost, and the learner MAXIMISES
        # return. Therefore EVERY term must carry a negative sign. The first
        # implementation negated only U_t, which turned energy, degraded
        # service, movement, recovery delay and criticality into positive
        # rewards -- the agent was paid to disconnect. Fixed here.
        U_t = float(np.mean(ncov < c.K))
        E_cons = float(np.sum(draw) * c.dt / (c.N * c.B_max))
        D_t = 1.0 if degraded_now else 0.0
        w_dist = float(np.linalg.norm(self.v, axis=1).sum() * c.dt) if act_before.size else 0.0
        # W_t = "distance flown / distance that changed coverage". A move that
        # buys no new coverage is pure waste, so penalise the fraction of flown
        # distance that did not improve the covered-sensor count.
        cov_now = float(np.mean(ncov >= c.K))
        newly_covered = max(cov_now - self.prev_cov_score, 0.0)
        if w_dist > 1e-9:
            W_t = float(np.clip(1.0 - newly_covered / (w_dist + 1e-9), 0.0, 1.0))
        else:
            W_t = 0.0
        crit = float(self.articulation_points(adj).mean()) if len(adj) else 1.0
        R_rec = rec_delay

        # Terms are exposed so eq. (23) can be checked as an equation rather
        # than by inspecting its side effects. See tests/test_physics_and_env.py
        # ::TestRewardEquation and tests/mutation_check.py.
        self.last_cost = dict(
            U_t=U_t, E_t=E_cons, D_t=D_t, W_t=W_t, R_t=R_rec, Crit_t=crit,
        )
        r = self.reward_from_terms(self.last_cost)

        self.prev_cov_score = cov_now
        self.prev_w_dist = w_dist

        # --- 7. metrics -------------------------------------------------
        self._update_metrics(ncov, adj, draw, w_dist)
        # An episode ends either because the mission time limit is reached or
        # because the swarm can no longer serve the sensors.  These are NOT
        # the same event: a time limit is a TRUNCATION, and the value of the
        # final state is still meaningful, so the GAE recursion must bootstrap
        # from V(s_T) rather than treat it as absorbing.  Conflating the two
        # biases every value target downward (Pardo et al., ICML 2018).
        self.truncated = self.t >= c.episode_len
        # A genuine terminal state: every UAV has failed, so nothing can
        # serve the sensors and no future return is possible.  In every other
        # case the episode simply hit the time limit, which is a truncation.
        self.terminated = (len(self._active_idx()) == 0) and not self.truncated
        done = self.truncated or self.terminated
        return self.local_obs(), self.global_state(), r, done, {}

    # ------------------------------------------------------------------
    # Reward, eq. (23)
    # ------------------------------------------------------------------
    def reward_from_terms(self, terms: dict) -> float:
        """Eq. (23):  r_t = -( sum_k lambda_k * cost_k(t) ).

        Implemented as a pure function of the cost terms so that the equation in
        the report can be asserted against directly. Every term is subtracted.
        A previous revision negated only U_t, which rewarded energy burn,
        partitions, motion, recovery delay and criticality; that defect is now
        impossible to reintroduce without failing the test suite.
        """
        c = self.cfg
        cost = (
            c.lam_O * terms["U_t"]
            + c.lam_E * terms["E_t"]
            + c.lam_D * terms["D_t"]
            + c.lam_W * terms["W_t"]
            + c.lam_R * terms["R_t"]
        )
        if c.use_connectivity_term:
            cost += c.lam_C * terms["Crit_t"]
        return -float(cost)

    # ------------------------------------------------------------------
    # Metrics (Table IX)
    # ------------------------------------------------------------------
    def _update_metrics(self, ncov, adj, draw, w_dist):
        c = self.cfg
        m = self.ep
        kcov_frac_this = float(np.mean(ncov >= c.K))
        m["Kcov_ok"] += float(np.all(ncov >= c.K))
        m["Kcov_frac"] += kcov_frac_this
        m["under_cov"] += float(np.mean(ncov < c.K))
        m["connected"] += float(self.is_connected(adj))
        m["service_cont"] += float(np.all(ncov >= c.K) and self.is_connected(adj))
        m["crit"] += float(self.articulation_points(adj).mean()) if len(adj) else 1.0
        m["energy"] += float(np.sum(draw) * c.dt)
        m["distance"] += w_dist
        m["min_batt"] = min(m["min_batt"], float(np.min(self.E[self._active_idx()])) if len(self._active_idx()) else 0.0)
        m["steps"] += 1
        m["denied"] += self.denied_charge
        m["reserve_activations"] = self.reserve_used
        # Non-degenerate metrics: time-averaged coverage deficit + worst refresh.
        m["cov_integral"] += (1.0 - kcov_frac_this)
        if kcov_frac_this < 1.0:
            self._under_streak += 1
            m["max_under_streak"] = max(m["max_under_streak"], self._under_streak)
        else:
            self._under_streak = 0

    def metrics(self):
        return dict(
            Kcov_ok=0.0, Kcov_frac=0.0, under_cov=0.0, connected=0.0,
            service_cont=0.0, crit=0.0, energy=0.0, distance=0.0,
            min_batt=float("inf"), steps=0, denied=0, reserve_activations=0,
            # Non-degenerate metrics (Deep Research recommendation):
            # time-averaged coverage deficit and worst-case refresh streak.
            cov_integral=0.0, max_under_streak=0,
        )

    def summary(self):
        s = self.ep["steps"]
        if s == 0:
            return {}
        return dict(
            CK=self.ep["Kcov_frac"] / s,
            Kcov_ok=self.ep["Kcov_ok"] / s,
            Ubar=self.ep["under_cov"] / s,
            AG=self.ep["connected"] / s,
            SC=self.ep["service_cont"] / s,
            Crit=self.ep["crit"] / s,
            Energy=self.ep["energy"],
            MinBattery=self.ep["min_batt"],
            Distance=self.ep["distance"],
            Denied=self.ep["denied"],
            Reserve=self.ep["reserve_activations"],
            # Non-degenerate metrics (Deep Research recommendation):
            # CovIntegral = time-averaged coverage deficit (0 = perfect coverage)
            # MaxRefresh  = longest run of steps with any under-covered sensor
            CovIntegral=self.ep["cov_integral"] / s,
            MaxRefresh=self.ep["max_under_streak"],
        )