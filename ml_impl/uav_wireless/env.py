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
    seed: int = 0

    def dict(self):
        return asdict(self)


class UAVIoTEnv:
    """Cooperative persistent-coverage Dec-POMDP."""

    OBS_DIM = 32
    # N*2 (pos) + N (batt) + N (mode) + N (failed) + M*2 (sensors)
    # + n_pads (pad occupancy) + 3 (reserve, time, connectivity)
    STATE_DIM = 80

    def __init__(self, cfg: SimConfig):
        self.cfg = cfg
        self.rng = np.random.default_rng(cfg.seed)
        self.radio = WirelessModel(z0=cfg.z0, p_tx=cfg.P_tx)
        self.reset()

    # ------------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------------
    def reset(self):
        c = self.cfg
        self.t = 0
        self.p = self.rng.uniform(0, c.side, size=(c.N, 2))
        self.v = np.zeros((c.N, 2))
        self.E = self.rng.uniform(0.7, 1.0, size=c.N) * c.B_max
        self.failed = np.zeros(c.N, dtype=bool)
        self.mode = np.zeros(c.N, dtype=int)          # 0 serve, 1 return, 2 charge
        self.pad_assigned = np.full(c.N, -1, dtype=int)
        self.pad_queue = np.zeros(c.n_pads, dtype=int)
        self.pad_occupied_by = np.full(c.n_pads, -1, dtype=int)

        self.sensors = self.rng.uniform(0, c.side, size=(c.M, 2))
        self.pads = self.rng.uniform(0.15 * c.side, 0.85 * c.side, size=(c.n_pads, 2))

        self.reserve_used = 0
        self.failure_t = c.failure_time if c.failure_time >= 0 else -1
        if c.failure_enabled and c.failure_time < 0:
            self.failure_t = int(self.rng.integers(c.episode_len // 3, c.episode_len))

        self._history_len = 6
        self.prev_cov_score = 0.0
        self.prev_w_dist = 0.0
        self.recovery_start = -1
        self.recovered = True
        self.charging_wait = np.zeros(c.N)
        self.denied_charge = 0

        self.ep = self.metrics()
        self.prev_metrics = dict(self.ep)
        return self.local_obs(), self.global_state()

    # ------------------------------------------------------------------
    # PHY-derived coverage and connectivity
    # ------------------------------------------------------------------
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
        sinr = self._access_sinr_matrix(self.p[act], self.sensors)   # (M, N)
        rate = self.radio.rate_mbps(self.radio.snr_db(sinr))         # (M, N)
        phy_ok = rate >= self.radio.rate_min_mbps                    # (M, N)
        usable = within & phy_ok
        return usable.sum(axis=1)

    def _access_sinr_matrix(self, uav_xy, sensor_xy):
        """(M, N) SINR of every sensor->UAV pair, with inter-UAV interference.

        The report's K-coverage counts how many UAVs can *simultaneously serve*
        a sensor, so we need a per-pair value rather than a single best-SINR
        number. Each UAV is treated as an interfering transmitter for the
        others, so serving with more UAVs costs SINR -- which is exactly the
        interference effect the experiment is meant to expose.
        """
        m = len(sensor_xy)
        n = len(uav_xy)
        if n == 0 or m == 0:
            return np.zeros((m, n))
        d = np.linalg.norm(sensor_xy[:, None, :] - uav_xy[None, :, :], axis=-1)
        d3 = np.sqrt(d ** 2 + self.cfg.z0 ** 2)
        los = los_probability(d3, self.cfg.z0)
        rx = self.radio.received_w(d3, los)          # (M, N) watts
        inter = rx.sum(axis=1, keepdims=True) - rx    # all but the serving UAV
        return rx / (inter + self.radio.noise_w)

    def comm_graph(self):
        """Adjacency + SINR matrix over active UAVs."""
        act = self._active_idx()
        n = len(act)
        if n == 0:
            return act, np.zeros((0, 0), dtype=bool), np.zeros((0, 0))
        sinr = self.radio.backhaul_sinr(self.p[act])
        snr = self.radio.snr_db(sinr)
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
                if self._would_disconnect(i, p_new):
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
        """o_i(t) = [p_i, v_i, b_i, N_i, C_i^local, rho_i, tau_i^return, E_i^pad]. Eq. (4)."""
        c = self.cfg
        obs = np.zeros((c.N, self.OBS_DIM), dtype=np.float32)
        act, adj, _ = self.comm_graph()
        ncov = self.coverage_counts()

        for i in range(c.N):
            if self.failed[i]:
                continue
            o = obs[i]
            o[0:2] = self.p[i] / c.side
            o[2:4] = self.v[i] / c.v_max
            o[4] = self.E[i] / c.B_max
            o[5:8] = self.mode[i] / 2.0
            o[8] = 1.0 if self.pad_assigned[i] >= 0 else 0.0

            # neighbours within R_comm (relative, first 4 slots)
            others = [j for j in act if j != i]
            near = []
            for j in others:
                d = np.linalg.norm(self.p[j] - self.p[i])
                if d <= c.R_comm:
                    near.append(((self.p[j] - self.p[i]) / c.R_comm, self.E[j] / c.B_max, d))
            near.sort(key=lambda z: z[2])
            for k, (rel, ej, d) in enumerate(near[:4]):
                o[9 + 2 * k] = rel[0]
                o[10 + 2 * k] = rel[1]
                o[11 + 2 * k] = ej
                o[12 + 2 * k] = d / c.R_comm
            o[17] = min(len(near), 4) / 4.0

            # local coverage count
            d_s = np.linalg.norm(self.sensors - self.p[i], axis=1)
            o[18] = np.sum(d_s <= c.R_cov) / max(c.M, 1)

            # local bridge risk rho_i: is any neighbour a cut-vertex locally?
            # adj rows/cols are indexed by POSITION within `act`, not by the
            # global UAV id, so translate before indexing.
            ap = self.articulation_points(adj) if len(adj) else np.zeros(0, bool)
            pos_i = list(act).index(i)
            deg = int(adj[pos_i].sum()) if len(adj) else 0
            bridge = 1.0 if (0 < deg <= 2) else 0.0
            for k, j in enumerate([x for x in act if x != i][:4]):
                idx = list(act).index(j)
                if idx < len(ap) and ap[idx]:
                    bridge = max(bridge, 1.0 - 0.25 * k)
            o[19] = bridge

            # return urgency and pad energy
            thresh = self.return_threshold(i)
            o[20] = np.clip((thresh - self.E[i]) / max(thresh, 1.0), -1, 1)
            o[21] = self.pad_energy(i) / c.B_max
            o[22] = np.clip(self.charging_wait[i] / 200.0, 0, 1)
            o[23] = 1.0 if i in list(act) else 0.0
        return obs

    def global_state(self):
        """s_t for the centralized critic. Eq. (3)."""
        c = self.cfg
        s = np.zeros(self.STATE_DIM, dtype=np.float32)
        i = 0
        s[i:i + c.N * 2] = (self.p / c.side).flatten(); i += c.N * 2
        s[i:i + c.N] = self.E / c.B_max; i += c.N
        s[i:i + c.N] = self.mode / 2.0; i += c.N
        s[i:i + c.N] = self.failed.astype(float); i += c.N
        s[i:i + self.cfg.M * 2] = (self.sensors / c.side).flatten(); i += self.cfg.M * 2
        s[i:i + c.n_pads] = self.pad_occupied_by >= 0; i += c.n_pads
        s[i] = self.reserve_used / max(c.N_reserve, 1)
        s[i + 1] = self.t / c.episode_len
        s[i + 2] = 1.0 if self.is_connected(self.comm_graph()[1]) else 0.0
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
        ok_now = (ncov >= c.K).all() and self.is_connected(adj)
        if not self.recovered and ok_now:
            self.recovered = True
        rec_delay = 0.0
        if self.recovery_start >= 0 and self.recovered:
            rec_delay = min((self.t - self.recovery_start) / c.episode_len, 1.0)

        # --- 6. reward (23) --------------------------------------------
        U_t = float(np.mean(ncov < c.K))
        E_cons = float(np.sum(draw) * c.dt / (c.N * c.B_max))
        D_t = 1.0 if (not ok_now) else 0.0
        w_dist = float(np.linalg.norm(self.v, axis=1).sum() * c.dt) if act_before.size else 0.0
        if act_before.size:
            W_t = w_dist / max(self.prev_w_dist + 1e-6, 1.0)
            W_t = min(W_t, 1.0)
        else:
            W_t = 0.0
        crit = float(self.articulation_points(adj).mean()) if len(adj) else 1.0
        R_rec = rec_delay

        r = (
            -c.lam_O * U_t
            + c.lam_E * E_cons
            + c.lam_D * D_t
            + c.lam_W * W_t
            + c.lam_R * R_rec
            + (c.lam_C * crit if c.use_connectivity_term else 0.0)
        )
        self.prev_w_dist = w_dist

        # --- 7. metrics -------------------------------------------------
        self._update_metrics(ncov, adj, draw, w_dist)
        if self.t >= c.episode_len:
            done = True
        else:
            done = False
        return self.local_obs(), self.global_state(), r, done, {}

    # ------------------------------------------------------------------
    # Metrics (Table IX)
    # ------------------------------------------------------------------
    def _update_metrics(self, ncov, adj, draw, w_dist):
        c = self.cfg
        m = self.ep
        m["Kcov_ok"] += float(np.all(ncov >= c.K))
        m["Kcov_frac"] += float(np.mean(ncov >= c.K))
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

    def metrics(self):
        return dict(
            Kcov_ok=0.0, Kcov_frac=0.0, under_cov=0.0, connected=0.0,
            service_cont=0.0, crit=0.0, energy=0.0, distance=0.0,
            min_batt=float("inf"), steps=0, denied=0, reserve_activations=0,
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
        )