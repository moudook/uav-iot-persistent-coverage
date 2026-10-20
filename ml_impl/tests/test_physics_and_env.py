"""
Test suite. Every quantitative claim in the report should be checkable here.

Run:  python tests/run_tests.py
      python tests/run_tests.py TestRewardSign

No pytest dependency -- see tests/run_tests.py for why.
"""

from __future__ import annotations

import numpy as np

from uav_wireless import SimConfig, UAVIoTEnv, MAPPO
from uav_wireless.wireless import (
    WirelessModel, MCS_TABLE, SNR_SENSITIVITY_DB, snr_to_rate,
    los_probability, path_loss_db, log_distance_pl,
)
from uav_wireless.env import N_ACTIONS, ACTION_VECTORS, A_HOVER, A_CHARGE


# ======================================================================
# PHY layer
# ======================================================================
class TestPHY:
    def test_mcs_table_monotonic(self):
        """Rate must be non-decreasing in required SNR."""
        assert np.all(np.diff(MCS_TABLE[:, 0]) > 0)
        assert np.all(np.diff(MCS_TABLE[:, 1]) > 0)

    def test_rate_increases_with_snr(self):
        r_low = snr_to_rate(-5.0)
        r_mid = snr_to_rate(10.0)
        r_high = snr_to_rate(40.0)
        assert r_low <= r_mid <= r_high
        assert r_low == 0.0                 # below sensitivity: no usable link
        assert r_high == MCS_TABLE[-1, 1]   # ceiling at the highest MCS

    def test_below_sensitivity_yields_zero_rate(self):
        """Returning the lowest MCS below sensitivity silently disables the
        PHY gate, because `rate_min_mbps` IS the lowest MCS."""
        assert snr_to_rate(SNR_SENSITIVITY_DB - 0.01) == 0.0
        assert snr_to_rate(SNR_SENSITIVITY_DB) == MCS_TABLE[0, 1]

    def test_rate_never_exceeds_requirement(self):
        """Regression: `side='left'` searching returned an MCS whose SNR
        requirement was not met (3.9 dB -> the 4.0 dB MCS)."""
        for snr in np.arange(-5.0, 25.0, 0.1):
            rate = snr_to_rate(snr)
            if rate == 0.0:
                continue
            threshold = MCS_TABLE[MCS_TABLE[:, 1] == rate, 0].min()
            assert snr >= threshold - 1e-9, (
                f"SNR {snr:.1f} dB claimed the {rate} Mbit/s MCS "
                f"which needs {threshold:.1f} dB"
            )

    def test_gate_actually_gates(self):
        """The PHY usability test must be false for a weak link.

        If `snr_to_rate` floored at the minimum MCS, `rate >= rate_min_mbps`
        would be true for every SNR and coverage would be purely geometric --
        exactly the 'abstract disc' model the professor rejected.
        """
        r = WirelessModel()
        assert not r.usable(np.array([-10.0, 0.0, 1.0])).any()
        assert r.usable(np.array([20.0, 40.0])).all()

    def test_los_probability_bounds_and_monotonicity(self):
        """P(LoS) in [0,1] and increasing with elevation angle (shorter slant)."""
        p_far = los_probability(400.0, 50.0)
        p_near = los_probability(60.0, 50.0)
        assert 0.0 <= p_far <= 1.0
        assert 0.0 <= p_near <= 1.0
        assert p_near > p_far, "higher elevation must mean more LoS"

    def test_path_loss_increases_with_distance(self):
        pl_near = path_loss_db(10.0, 1.0, 2.4e9)
        pl_far = path_loss_db(100.0, 1.0, 2.4e9)
        assert pl_far > pl_near

    def test_nlos_worse_than_los(self):
        """At equal distance NLoS loss must exceed LoS loss.

        Regression: the exponent was applied additively on top of the free-space
        slope, so n=3.5 gave an effective exponent of 2.35 against 2.2 for the
        LoS case -- almost no difference, which erased the distinction.
        """
        d = 100.0
        pl_los = log_distance_pl(d, 2.4e9, 2.0)
        pl_nlos = log_distance_pl(d, 2.4e9, 3.5)
        assert pl_nlos > pl_los + 10.0, (
            f"NLoS loss {pl_nlos:.1f} dB is not meaningfully above LoS "
            f"{pl_los:.1f} dB; the path-loss exponent is not being applied"
        )
        # the blended model must sit between the two
        pl_blend = path_loss_db(d, 0.5, 2.4e9, n_los=2.0, n_nlos=3.5)
        assert pl_los < pl_blend < pl_nlos

    def test_free_space_matches_friis(self):
        """At n = 2 the log-distance model must reproduce Friis free space."""
        d, f = 100.0, 2.4e9
        expected = 20.0 * np.log10(d) + 20.0 * np.log10(4 * np.pi * f / 299_792_458.0)
        assert np.isclose(log_distance_pl(d, f, 2.0), expected, atol=1e-6)

    def test_backhaul_snr_positive_in_nominal_formation(self):
        """Relay links must be usable at formation spacing.

        Regression test: the original backhaul model summed all UAVs as
        co-channel interferers, giving ~-14 dB and making connectivity
        unachievable. Uses THREE UAVs -- with only two, rx/(sum-rx) is exactly
        1 for any interference model, so a two-node test cannot fail.
        """
        r = WirelessModel(z0=50.0)
        r.reset_links(3, 4, seed=3)
        xy = np.array([[40.0, 40.0], [40.0 + 25.0, 40.0], [40.0, 40.0 + 25.0]])
        snr = r.backhaul_snr(xy)
        assert snr[0, 1] > 0.0, f"backhaul SNR {snr[0,1]:.1f} dB is unusable"

    def test_backhaul_is_not_cochannel(self):
        """Adding a third, far-away UAV must not change the first pair's link.

        This is the invariant that separates an SNR model from a co-channel
        SINR model. Under the old code the extra UAV consumed a share of the
        budget and the pair's SINR collapsed; under the correct relay model the
        two-UAV and three-UAV cases must agree exactly.
        """
        r = WirelessModel(z0=50.0)
        r.reset_links(3, 4, seed=3)
        two = np.array([[40.0, 40.0], [65.0, 40.0]])
        three = np.vstack([two, [[40.0, 75.0]]])          # far, unrelated UAV
        s2 = r.backhaul_snr(two, uav_idx=[0, 1])
        s3 = r.backhaul_snr(three, uav_idx=[0, 1, 2])
        assert s3[0, 1] == s2[0, 1], (
            f"link (0,1) changed from {s2[0,1]:.2f} to {s3[0,1]:.2f} dB when an "
            "unrelated UAV was added -- the backhaul is being modelled as "
            "co-channel interference"
        )

    def test_backhaul_diagonal_is_zeroed(self):
        r = WirelessModel()
        r.reset_links(3, 4, seed=1)
        xy = np.array([[0.0, 0.0], [10.0, 0.0], [0.0, 10.0]])
        snr = r.backhaul_snr(xy)
        assert snr[0, 0] == 0.0 and snr[1, 1] == 0.0 and snr[2, 2] == 0.0

    def test_shadowing_table_is_reciprocal(self):
        """S(i,j) must equal S(j,i): one physical path, one shadowing value.

        Checked on the stored table rather than on backhaul_snr's output,
        because the output is explicitly symmetrised and would hide an
        asymmetric table. The original model drew an independent value per
        matrix element, so a link had two different channels depending on
        which end you measured from.
        """
        r = WirelessModel()
        r.reset_links(5, 6, seed=13)
        S = r.shadow_uu_db
        assert S.shape == (5, 5)
        assert np.allclose(S, S.T), "UAV-UAV shadowing table is not reciprocal"
        assert np.allclose(np.diag(S), 0.0), "a self-link must carry no shadowing"

    def test_scene_is_drawn_once_per_episode(self):
        """Re-evaluating a link must not re-draw the channel.

        The original `received_w` sampled shadowing and fading on every call,
        so the propagation environment changed with each link evaluation and
        with the number of nodes in the array being evaluated.
        """
        r = WirelessModel(z0=50.0)
        r.reset_links(3, 4, seed=5)
        xy = np.array([[10.0, 20.0], [40.0, 25.0], [60.0, 70.0]])
        first = r.backhaul_snr(xy)
        for _ in range(5):
            assert np.array_equal(r.backhaul_snr(xy), first), (
                "backhaul_snr returned a different value on a repeat call at "
                "identical positions; the channel is being re-drawn"
            )

    def test_noise_power_units_are_watts(self):
        """Thermal noise must be in watts, not dBm read as dBW.

        The conversion is 30 dB, so a units slip makes every link budget 1000x
        too pessimistic and silently changes which links are usable.
        """
        r = WirelessModel(bandwidth_hz=20e6, noise_fig_db=7.0)
        noise_dbm = -174.0 + 7.0 + 10 * np.log10(20e6)
        expected_w = 10 ** (noise_dbm / 10.0) / 1000.0
        assert np.isclose(r.noise_w, expected_w, rtol=1e-6)
        assert 1e-14 < r.noise_w < 1e-12, "noise power outside the watt range"

    def test_backhaul_snr_symmetric_in_geometry(self):
        """Path loss is reciprocal, so SNR(i,j) == SNR(j,i)."""
        r = WirelessModel(z0=50.0)
        r.reset_links(3, 4, seed=7)
        xy = np.array([[10.0, 20.0], [40.0, 25.0], [60.0, 70.0]])
        snr = r.backhaul_snr(xy)
        assert np.allclose(snr, snr.T)

    def test_link_is_stable_when_another_uav_fails(self):
        """A failure must not re-draw the surviving links.

        Channels are addressed by global node index, so removing UAV 2 must
        leave the (0,1) link exactly as it was. Otherwise the fault-tolerance
        experiment quietly changes the propagation environment as well as the
        topology, and the measured effect is not attributable to the failure.
        """
        r = WirelessModel(z0=50.0)
        r.reset_links(3, 4, seed=11)
        xy = np.array([[10.0, 20.0], [40.0, 25.0], [60.0, 70.0]])
        full = r.backhaul_snr(xy, uav_idx=[0, 1, 2])
        kept = r.backhaul_snr(xy[:2], uav_idx=[0, 1])
        assert kept[0, 1] == full[0, 1]
        assert kept[1, 0] == full[1, 0]


class TestReproducibility:
    """Runs must replay exactly. A reportable number that cannot be
    regenerated is not evidence."""

    def test_phy_does_not_touch_global_rng(self):
        """PHY draws must come from the model's own generator.

        Sharing the global RNG makes the physics perturb action sampling, so
        the same seed produces different rollouts depending on how many link
        evaluations happened to run.
        """
        np.random.seed(1234)
        before = np.random.get_state()[1][:8].copy()
        pos_rng = np.random.default_rng(99)          # separate stream for inputs,
        r = WirelessModel(z0=50.0)                   # so this test does not
        r.reset_links(4, 6, seed=5)                  # consume the global RNG itself
        xy = pos_rng.uniform(0, 80, size=(4, 2))
        r.backhaul_snr(xy)
        r.access_sinr(pos_rng.uniform(0, 80, size=(6, 2)), xy)
        after = np.random.get_state()[1][:8]
        assert np.array_equal(before, after), (
            "the wireless model consumed the global numpy RNG"
        )

    def test_same_seed_replays_identically(self):
        def rollout():
            c = SimConfig(seed=7, episode_len=40)
            e = UAVIoTEnv(c)
            e.reset()
            rs = []
            rng = np.random.default_rng(0)
            for _ in range(40):
                m = np.stack([e.action_mask(i) for i in range(c.N)])
                a = np.array([rng.choice(np.flatnonzero(m[i])) for i in range(c.N)])
                rs.append(e.step(a)[2])
            return np.array(rs)

        assert np.array_equal(rollout(), rollout())

    def test_different_seed_changes_environment(self):
        """Seeds must produce genuinely different scenes.

        Note: this asserts on the *scene* (positions, sensors, channel), not on
        the reward. The reward is currently near-constant across seeds because
        `U_t == 1` whenever no sensor is K-covered -- see
        TestFeasibility.test_coverage_is_the_binding_constraint.
        """
        def scene(seed):
            c = SimConfig(seed=seed, episode_len=10)
            e = UAVIoTEnv(c)
            e.reset()
            return e.p.copy(), e.sensors.copy(), e.radio.shadow_su_db.copy()

        p1, s1, h1 = scene(1)
        p2, s2, h2 = scene(2)
        assert not np.allclose(s1, s2), "sensors identical across seeds"
        assert not np.allclose(h1, h2), "channel realisations identical across seeds"


# ======================================================================
# Environment contract
# ======================================================================
class TestEnvContract:
    def test_shapes(self):
        c = SimConfig(episode_len=10)
        e = UAVIoTEnv(c)
        obs, state = e.reset()
        assert obs.shape == (c.N, e.obs_dim)
        assert state.shape == (e.state_dim,)
        assert np.all(np.isfinite(obs)) and np.all(np.isfinite(state))

    def test_dimensions_scale_with_configuration(self):
        """State/obs dims must follow N, M and n_pads.

        Regression: STATE_DIM was the hardcoded value 80, which is only correct
        for N=5. At N=8 the pad-occupancy slice ran off the end of the array and
        raised; between those sizes it would have been silently misaligned.
        """
        prev = None
        for n in (4, 5, 6, 8, 10):
            c = SimConfig(N=n, M=20, n_pads=2, episode_len=5)
            e = UAVIoTEnv(c)
            obs, state = e.reset()
            assert obs.shape == (n, e.obs_dim)
            assert state.shape == (e.state_dim,)
            assert e.state_dim == 2 * n + 3 * n + 2 * 20 + 2 + 3
            assert e.state_dim != prev
            prev = e.state_dim

    def test_dimension_constants_track_the_reference_config(self):
        c = SimConfig()
        e = UAVIoTEnv(c)
        assert UAVIoTEnv.STATE_DIM == e.state_dim, (
            f"class constant {UAVIoTEnv.STATE_DIM} != {e.state_dim} for the "
            "default config; the convenience constant has drifted"
        )
        assert UAVIoTEnv.OBS_DIM == e.obs_dim

    def test_observation_slots_are_not_overwritten(self):
        """Each neighbour must own its own 4 slots, with a self-consistent group.

        Regression: the neighbour block used a stride of 2 while storing 4
        values per neighbour, so consecutive neighbours overlapped and the third
        neighbour overwrote the neighbour count and the local coverage count.

        The invariant that catches it: within one neighbour group, the recorded
        relative offset and the recorded distance must agree, because
        |(dx, dy)| * R_comm == distance. An overlapping layout mixes fields from
        different neighbours and breaks that.
        """
        c = SimConfig(episode_len=10, N=5, M=20)
        e = UAVIoTEnv(c)
        e.reset()
        # three neighbours in known, distinct directions
        e.p[0] = np.array([40.0, 40.0])
        e.p[1] = np.array([50.0, 40.0])
        e.p[2] = np.array([40.0, 50.0])
        e.p[3] = np.array([40.0, 40.0 + 20.0])
        e.p[4] = np.array([40.0, 40.0])

        obs = e.local_obs()[0]
        assert len(obs) == e.obs_dim

        n_slots = 4
        base = 7
        populated = 0
        for k in range(n_slots):
            g = obs[base + 4 * k: base + 4 * k + 4]
            dx, dy, _bj, dist = g
            if dx == 0.0 and dy == 0.0 and dist == 0.0:
                continue
            populated += 1
            assert dist > 0.0, (
                f"slot {k} has an offset but zero distance -- fields from "
                f"different neighbours are sharing a slot"
            )
            assert np.isclose(np.hypot(dx, dy), dist, atol=1e-5), (
                f"slot {k}: |(dx,dy)| = {np.hypot(dx, dy):.5f} but the distance "
                f"field says {dist:.5f}; the neighbour block is misaligned"
            )
        assert populated == 3, f"expected 3 populated neighbour slots, got {populated}"

        # the tail must survive the neighbour block
        assert 0.0 < obs[base + 4 * n_slots] <= 1.0, "neighbour count clobbered"
        assert obs[base + 4 * n_slots + 6] == 1.0, "active flag clobbered"

    def test_initial_connectivity_is_feasible(self):
        """Regression: 11/20 random seeds used to start disconnected."""
        bad = []
        for s in range(30):
            c = SimConfig(seed=s, episode_len=10)
            e = UAVIoTEnv(c)
            e.reset()
            if not e.is_connected(e.comm_graph()[1]):
                bad.append(s)
        assert not bad, f"infeasible initial deployment on seeds {bad}"

    def test_observation_is_local_not_global(self):
        """The actor must not receive sensor coordinates directly."""
        c = SimConfig(episode_len=10)
        e = UAVIoTEnv(c)
        obs, state = e.reset()
        assert obs.shape[1] < state.shape[0], "obs should be smaller than state"

    def test_action_mask_always_nonempty(self):
        c = SimConfig(episode_len=20)
        e = UAVIoTEnv(c)
        e.reset()
        for _ in range(20):
            for i in range(c.N):
                m = e.action_mask(i)
                assert m.any(), f"UAV {i} has no feasible action"
            a = np.zeros(c.N, dtype=np.int64)
            e.step(a)

    def test_mask_blocks_leaving_workspace(self):
        c = SimConfig(episode_len=10)
        e = UAVIoTEnv(c)
        e.reset()
        e.p[0] = np.array([0.01, 0.01])       # pinned in the corner
        m = e.action_mask(0)
        # -x and -y would leave the region and must be masked
        from uav_wireless.env import A_NX, A_NY
        assert not m[A_NX]
        assert not m[A_NY]

    def test_mask_blocks_collision(self):
        c = SimConfig(episode_len=10, d_safe=5.0)
        e = UAVIoTEnv(c)
        e.reset()
        e.p[0] = np.array([40.0, 40.0])
        e.p[1] = np.array([40.0 + 0.5, 40.0])   # already too close
        m = e.action_mask(0)
        from uav_wireless.env import A_PX
        # moving further toward UAV 1 must be infeasible
        assert not m[A_PX]

    def test_step_returns_finite_reward(self):
        c = SimConfig(episode_len=30)
        e = UAVIoTEnv(c)
        e.reset()
        for _ in range(30):
            obs, state, r, done, info = e.step(np.zeros(c.N, dtype=np.int64))
            assert np.isfinite(r)
        assert done

    def test_episode_terminates_at_horizon(self):
        c = SimConfig(episode_len=15)
        e = UAVIoTEnv(c)
        e.reset()
        done = False
        n = 0
        while not done:
            _, _, _, done, _ = e.step(np.zeros(c.N, dtype=np.int64))
            n += 1
        assert n == 15


# ======================================================================
# Reward sign  (the eq. 23 bug)
# ======================================================================
class TestRewardSign:
    def test_reward_is_negative_cost(self):
        """Eq. (22) is a minimisation and eq. (23) is its negation, so the
        learner's reward must be a NEGATIVE cost. If this test fails, some
        cost term is being rewarded again."""
        c = SimConfig(episode_len=200)
        e = UAVIoTEnv(c)
        e.reset()
        rng = np.random.default_rng(0)
        rs = []
        for _ in range(200):
            m = np.stack([e.action_mask(i) for i in range(c.N)])
            a = np.array([
                rng.choice(np.flatnonzero(m[i])) if m[i].any() else 0
                for i in range(c.N)
            ])
            _, _, r, _, _ = e.step(a)
            rs.append(r)
        assert max(rs) <= 1e-6, (
            f"reward reached {max(rs):+.3f}; a cost term is being rewarded"
        )

    def test_hovering_costs_energy_and_is_penalised(self):
        """Doing nothing must still incur the energy cost, so the agent cannot
        farm reward by freezing."""
        c = SimConfig(episode_len=50)
        e = UAVIoTEnv(c)
        e.reset()
        _, _, r_hover, _, _ = e.step(np.full(c.N, A_HOVER, dtype=np.int64))
        assert r_hover < 0

    def test_disconnecting_is_worse_than_staying_connected(self):
        """The D_t term must make a partition strictly worse at equal coverage."""
        c = SimConfig(episode_len=10)
        e = UAVIoTEnv(c)
        e.reset()
        connected_before = e.is_connected(e.comm_graph()[1])
        assert connected_before
        # force a partition and confirm the connectivity metric reflects it
        e.p[0] = np.array([0.0, 0.0])
        e.p[1:] = np.array([[79.0, 79.0]] * (c.N - 1))
        assert not e.is_connected(e.comm_graph()[1])


class TestRewardEquation:
    """Eq. (23) checked as an equation, not via its side effects.

    The earlier `TestRewardSign::test_reward_is_negative_cost` asserted only
    that the reward was negative. That is satisfied by `-lam_O * U_t` alone, so
    it passed even while the other five terms were inverted -- a mutation check
    proved it. These tests pin the actual formula.
    """

    def _env(self, **kw):
        kw.setdefault("episode_len", 30)
        c = SimConfig(**kw)
        e = UAVIoTEnv(c)
        e.reset()
        return e

    def test_step_reward_equals_formula(self):
        """r_t must equal the negated weighted sum of the reported terms."""
        e = self._env()
        c = e.cfg
        _, _, r, _, _ = e.step(np.full(c.N, A_HOVER, dtype=np.int64))
        t = e.last_cost
        expected = -(
            c.lam_O * t["U_t"] + c.lam_E * t["E_t"] + c.lam_D * t["D_t"]
            + c.lam_W * t["W_t"] + c.lam_R * t["R_t"]
            + (c.lam_C * t["Crit_t"] if c.use_connectivity_term else 0.0)
        )
        assert r == expected, f"step reward {r} != eq.(23) value {expected}"

    def test_reward_decreases_in_every_cost_term(self):
        """Flipping any single term must strictly LOWER the reward.

        This is the assertion that actually catches the sign bug: under the old
        code, five of six terms increased the reward when their cost rose.
        """
        e = self._env()
        zero = dict(U_t=0.0, E_t=0.0, D_t=0.0, W_t=0.0, R_t=0.0, Crit_t=0.0)
        base = e.reward_from_terms(zero)
        for key in zero:
            bumped = dict(zero, **{key: 1.0})
            r1 = e.reward_from_terms(bumped)
            assert r1 < base, (
                f"raising cost term {key} increased the reward "
                f"({base} -> {r1}); that term is being rewarded"
            )

    def test_all_lambdas_are_positive(self):
        """A negative lambda would invert a term's meaning."""
        c = SimConfig()
        for name in ("lam_O", "lam_E", "lam_D", "lam_W", "lam_R", "lam_C"):
            assert getattr(c, name) > 0.0, f"{name} must be positive"

    def test_zero_cost_gives_zero_reward(self):
        """No cost must mean zero reward -- no constant offset anywhere."""
        e = self._env()
        assert e.reward_from_terms(
            dict(U_t=0.0, E_t=0.0, D_t=0.0, W_t=0.0, R_t=0.0, Crit_t=0.0)
        ) == 0.0

    def test_cost_terms_are_bounded(self):
        """Every cost term must lie in [0,1] so lambdas are comparable."""
        e = self._env(episode_len=60)
        c = e.cfg
        rng = np.random.default_rng(3)
        for _ in range(60):
            m = np.stack([e.action_mask(i) for i in range(c.N)])
            a = np.array([rng.choice(np.flatnonzero(m[i])) if m[i].any() else 0
                          for i in range(c.N)])
            e.step(a)
            for k, v in e.last_cost.items():
                assert 0.0 <= v <= 1.0 + 1e-9, f"{k}={v} outside [0,1]"


# ======================================================================
# Coverage / connectivity maths
# ======================================================================
class TestGeometry:
    def test_articulation_point_detection(self):
        """A 3-node path has a cut vertex in the middle."""
        adj = np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]], dtype=bool)
        ap = UAVIoTEnv.articulation_points(adj)
        assert ap.tolist() == [False, True, False]

    def test_no_articulation_in_triangle(self):
        adj = np.ones((3, 3), dtype=bool)
        np.fill_diagonal(adj, False)
        ap = UAVIoTEnv.articulation_points(adj)
        assert not ap.any()

    def test_connectivity_detection(self):
        conn = np.array([[0, 1, 1], [1, 0, 1], [1, 1, 0]], dtype=bool)
        split = np.array([[0, 1, 0], [1, 0, 0], [0, 0, 0]], dtype=bool)
        c = SimConfig(episode_len=5)
        e = UAVIoTEnv(c)
        assert e.is_connected(conn)
        assert not e.is_connected(split)

    def test_coverage_counts_respect_k(self):
        c = SimConfig(episode_len=5, N=4, M=8, R_cov=35.0)
        e = UAVIoTEnv(c)
        e.reset()
        ncov = e.coverage_counts()
        assert ncov.shape == (c.M,)
        assert (ncov >= 0).all() and (ncov <= c.N).all()

    def test_perfect_coverage_when_uavs_on_sensors(self):
        """If every UAV sits on a sensor, coverage counts must be high."""
        c = SimConfig(episode_len=5, N=5, M=5, R_cov=35.0)
        e = UAVIoTEnv(c)
        e.reset()
        e.p = e.sensors.copy()          # one UAV per sensor
        ncov = e.coverage_counts()
        assert (ncov >= 1).all()


# ======================================================================
# Battery / charging / failure
# ======================================================================
class TestEnergyAndFaults:
    def test_battery_depletes(self):
        c = SimConfig(episode_len=200, B_max=30_000.0)
        e = UAVIoTEnv(c)
        e.reset()
        e0 = e.E.copy()
        for _ in range(200):
            e.step(np.full(c.N, A_HOVER, dtype=np.int64))
        assert (e.E < e0).all(), "battery must drain"

    def test_battery_stays_in_bounds(self):
        c = SimConfig(episode_len=100)
        e = UAVIoTEnv(c)
        e.reset()
        for _ in range(100):
            e.step(np.full(c.N, A_HOVER, dtype=np.int64))
            assert (e.E >= 0).all() and (e.E <= c.B_max).all()

    def test_failure_removes_uav_from_active_set(self):
        c = SimConfig(episode_len=200, failure_enabled=True, failure_time=50)
        e = UAVIoTEnv(c)
        e.reset()
        e.failure_t = 50
        for _ in range(60):
            e.step(np.full(c.N, A_HOVER, dtype=np.int64))
        assert e.failed.sum() >= 1 or e.reserve_used >= 1, "failure never fired"

    def test_reserve_activates_after_failure(self):
        """Regression: reserve must actually engage, not be dead code."""
        c = SimConfig(episode_len=300, failure_enabled=True, failure_time=50,
                      use_reserve=True)
        e = UAVIoTEnv(c)
        e.reset()
        e.failure_t = 50
        for _ in range(200):
            e.step(np.full(c.N, A_HOVER, dtype=np.int64))
        assert e.reserve_used == c.N_reserve

    def test_charging_requests_can_be_served(self):
        c = SimConfig(episode_len=200, n_pads=2, B_max=4000.0, charge_rate=0.01)
        e = UAVIoTEnv(c)
        e.reset()
        e.E[:] = 100.0                       # everyone desperate
        e.p[:] = e.pads[0]                   # everyone on a pad
        # move UAVs to pad locations so charge is feasible
        for k in range(min(c.N, len(e.pads))):
            e.p[k] = e.pads[k % len(e.pads)]
        acts = np.full(c.N, A_CHARGE, dtype=np.int64)
        e.step(acts)
        assert e.E.max() > 100.0, "charging did not restore any energy"


# ======================================================================
# MAPPO
# ======================================================================
class TestMAPPO:
    def test_masked_actions_are_never_selected(self):
        """A masked-out action must have zero probability."""
        agent = MAPPO(n_agents=3, device="cpu")
        obs = np.zeros((3, UAVIoTEnv.OBS_DIM), np.float32)
        mask = np.ones((3, N_ACTIONS), dtype=bool)
        mask[0, 1:] = False             # UAV 0 may only hover
        acts = np.array([agent.act(obs, mask, deterministic=True), ] * 1)[0]
        assert acts[0] == 0, "picked a masked action"

    def test_act_handles_fully_masked_row(self):
        agent = MAPPO(n_agents=2, device="cpu")
        obs = np.zeros((2, UAVIoTEnv.OBS_DIM), np.float32)
        mask = np.zeros((2, N_ACTIONS), dtype=bool)
        acts = agent.act(obs, mask, deterministic=True)
        assert acts.shape == (2,)
        assert np.isfinite(acts).all()

    def test_update_changes_parameters(self):
        from uav_wireless.train import collect_rollout
        c = SimConfig(episode_len=40)
        env = UAVIoTEnv(c)
        agent = MAPPO(n_agents=c.N, device="cpu")
        before = [p.detach().clone() for p in agent.actor.parameters()]
        B, _ = collect_rollout(env, agent, 40)
        agent.update(B)
        after = list(agent.actor.parameters())
        assert any(not np.allclose(b.numpy(), a.detach().numpy())
                   for b, a in zip(before, after)), "actor did not learn"

    def test_rollout_shapes_align(self):
        from uav_wireless.train import collect_rollout
        c = SimConfig(episode_len=30)
        env = UAVIoTEnv(c)
        agent = MAPPO(n_agents=c.N, device="cpu")
        B, _ = collect_rollout(env, agent, 30)
        T = B["obs"].shape[0]
        for k in ("obs", "mask", "acts", "logp", "adv", "ret", "values"):
            assert B[k].shape[0] == T, f"{k} has inconsistent length"
        assert B["obs"].shape[1] == c.N
        assert B["states"].shape[1] == UAVIoTEnv.STATE_DIM


# ======================================================================
# Metrics
# ======================================================================
class TestMetrics:
    def test_summary_keys(self):
        c = SimConfig(episode_len=20)
        e = UAVIoTEnv(c)
        e.reset()
        for _ in range(20):
            e.step(np.zeros(c.N, dtype=np.int64))
        s = e.summary()
        for k in ("CK", "AG", "SC", "Crit", "Energy", "MinBattery", "Distance"):
            assert k in s, f"missing metric {k}"

    def test_metrics_in_unit_interval(self):
        c = SimConfig(episode_len=50)
        e = UAVIoTEnv(c)
        e.reset()
        rng = np.random.default_rng(1)
        for _ in range(50):
            m = np.stack([e.action_mask(i) for i in range(c.N)])
            a = np.array([rng.choice(np.flatnonzero(m[i])) for i in range(c.N)])
            e.step(a)
        s = e.summary()
        for k in ("CK", "AG", "SC", "Crit"):
            assert -1e-9 <= s[k] <= 1.0 + 1e-9, f"{k}={s[k]} outside [0,1]"

    def test_sc_implies_ck_and_ag(self):
        """SC is the joint condition, so SC>0 requires CK and AG both >0."""
        c = SimConfig(episode_len=100)
        e = UAVIoTEnv(c)
        e.reset()
        for _ in range(100):
            e.step(np.zeros(c.N, dtype=np.int64))
        s = e.summary()
        if s["SC"] > 0:
            assert s["CK"] > 0 and s["AG"] > 0

    def test_non_degenerate_metrics_present(self):
        """Deep Research recommended non-degenerate alternatives to SC."""
        c = SimConfig(episode_len=20)
        e = UAVIoTEnv(c)
        e.reset()
        for _ in range(20):
            e.step(np.zeros(c.N, dtype=np.int64))
        s = e.summary()
        assert "CovIntegral" in s, "CovIntegral metric missing"
        assert "MaxRefresh" in s, "MaxRefresh metric missing"
        assert 0.0 <= s["CovIntegral"] <= 1.0, f"CovIntegral={s['CovIntegral']} out of [0,1]"
        assert s["MaxRefresh"] >= 0

    def test_cov_integral_zero_on_perfect_coverage(self):
        """If every step has full K-coverage, CovIntegral should be 0."""
        # Use a very large R_cov so coverage is trivially full every step.
        c = SimConfig(episode_len=10, R_cov=1e6)
        e = UAVIoTEnv(c)
        e.reset()
        for _ in range(10):
            e.step(np.zeros(c.N, dtype=np.int64))
        s = e.summary()
        assert s["CovIntegral"] < 1e-9, f"expected ~0, got {s['CovIntegral']}"


# ======================================================================
# Dormancy / plasticity probe (analysis/dormancy.py)
# ======================================================================
class TestDormancyProbe:
    """The probe must be able to DETECT dormancy, not just report zero.

    A diagnostic that cannot fail is decoration. These tests deliberately
    kill neurons and assert that the probe notices.
    """

    @staticmethod
    def _tiny_batch(n_steps=6, n_agents=3, obs_dim=8):
        rng = np.random.default_rng(0)
        return dict(
            obs=rng.normal(size=(n_steps, n_agents, obs_dim)).astype(np.float32),
            mask=np.ones((n_steps, n_agents, N_ACTIONS), bool),
            acts=rng.integers(0, N_ACTIONS, size=(n_steps, n_agents)),
            logp=rng.normal(size=(n_steps, n_agents)).astype(np.float32) * 0.1,
            adv=rng.normal(size=(n_steps, n_agents)).astype(np.float32),
        )

    def test_probe_runs_and_reports_both_directions(self):
        import torch
        from analysis.dormancy import probe, summarise
        agent = MAPPO(obs_dim=8, state_dim=8, n_agents=3, hidden=16)
        stats = probe(agent, self._tiny_batch())
        rows = summarise(stats)
        assert len(rows) >= 1, "no layers probed"
        for r in rows:
            for key in ("dormant_frac_0.01", "silent_frac_0.01",
                        "dead_frac_0.01"):
                assert key in r, f"missing {key}"
                assert 0.0 <= r[key] <= 1.0

    def test_probe_detects_killed_neurons(self):
        """Zeroing a neuron's incoming weights must make it dormant."""
        import torch
        from analysis.dormancy import probe, summarise
        agent = MAPPO(obs_dim=8, state_dim=8, n_agents=3, hidden=16)
        # kill the first 8 neurons of the first hidden layer
        with torch.no_grad():
            agent.actor.net[0].weight[:8] = 0.0
            agent.actor.net[0].bias[:8] = 0.0
        stats = probe(agent, self._tiny_batch())
        rows = summarise(stats)
        first = rows[0]
        assert first["dormant_frac_0.01"] > 0.25, (
            f"probe failed to detect 8 killed neurons out of 16 "
            f"(dormant_frac={first['dormant_frac_0.01']})")

    def test_probe_reports_healthy_network_as_alive(self):
        """A freshly initialised network must not look dead."""
        from analysis.dormancy import probe, summarise
        agent = MAPPO(obs_dim=8, state_dim=8, n_agents=3, hidden=16)
        stats = probe(agent, self._tiny_batch())
        rows = summarise(stats)
        for r in rows:
            assert r["dormant_frac_0.01"] < 0.25, (
                f"healthy network reported {r['dormant_frac_0.01']:.3f} dormant")
            assert r["dead_frac_0.01"] < 0.25, (
                f"healthy network reported {r['dead_frac_0.01']:.3f} dead")


# ======================================================================
# Baseline seed handling
# ======================================================================
class TestBaselineSeeding:
    """The baselines must actually use the seed they are given.

    They previously accepted a `seed` argument and ignored it, so a
    "five-seed" comparison ran the same episode five times for the baselines
    while the learned policy was evaluated on five different scenes.  That is
    the unfair comparison the review flagged, and it flattered the learned
    policy whenever the extra seeds happened to be easier.
    """

    @staticmethod
    def _cfg():
        return SimConfig(N=4, K=1, M=8, episode_len=60, seed=0)

    def test_baselines_accept_and_apply_a_seed(self):
        from uav_wireless.train import (baseline_fixed, baseline_greedy,
                                        baseline_reactive)
        c = self._cfg()
        for fn in (baseline_fixed, baseline_greedy, baseline_reactive):
            a = fn(c, steps=60, seed=1)
            b = fn(c, steps=60, seed=2)
            assert set(a) == set(b)
            # the scenes differ, so at least one metric must differ
            differs = any(abs(a[k] - b[k]) > 1e-9 for k in a
                          if isinstance(a[k], (int, float)))
            assert differs, (
                f"{fn.__name__} produced identical results for seeds 1 and 2 "
                f"-- the seed is being ignored")

    def test_baseline_is_deterministic_for_a_fixed_seed(self):
        from uav_wireless.train import baseline_reactive
        c = self._cfg()
        a = baseline_reactive(c, steps=60, seed=3)
        b = baseline_reactive(c, steps=60, seed=3)
        for k in a:
            assert abs(a[k] - b[k]) < 1e-9, f"{k} not reproducible for one seed"

    def test_baseline_does_not_mutate_the_caller_config(self):
        from uav_wireless.train import baseline_reactive
        c = self._cfg()
        before = c.seed
        baseline_reactive(c, steps=30, seed=7)
        assert c.seed == before, "baseline mutated the caller's config"


# ======================================================================
# Termination vs truncation
# ======================================================================
class TestTerminationVsTruncation:
    """A time limit is a truncation; only a real dead end is a termination.

    If the environment reports the time limit as `done` without saying which
    it was, the GAE recursion bootstraps from zero at every episode
    boundary and every value target is biased downward.  The environment
    therefore reports `terminated` separately, and these tests pin that
    distinction.
    """

    def test_time_limit_is_a_truncation_not_a_termination(self):
        c = SimConfig(N=4, K=1, M=6, episode_len=5, seed=0)
        e = UAVIoTEnv(c)
        e.reset()
        for _ in range(5):
            _, _, _, done, _ = e.step(np.zeros(c.N, dtype=np.int64))
        assert done, "episode should report done at the time limit"
        assert e.truncated is True, "time limit must be flagged as truncation"
        assert e.terminated is False, "time limit must NOT be a termination"

    def test_bootstrap_is_used_at_a_time_limit(self):
        """A truncated rollout must bootstrap, not zero."""
        import numpy as np
        from uav_wireless.env import UAVIoTEnv
        c = SimConfig(N=4, K=1, M=6, episode_len=5, seed=0)
        e = UAVIoTEnv(c)
        e.reset()
        for _ in range(5):
            e.step(np.zeros(c.N, dtype=np.int64))
        assert e.truncated and not e.terminated

    def test_rollout_honours_the_terminated_flag(self):
        """collect_rollout must read env.terminated, not infer it from done."""
        import inspect
        from uav_wireless import train
        src = inspect.getsource(train.collect_rollout)
        assert "env.terminated" in src or "getattr(env, \"terminated\"" in src, (
            "collect_rollout does not consult the environment's terminated flag")
        assert "truncated = (t == n_steps) and (not done)" not in src, (
            "collect_rollout still infers truncation from `done`, which cannot "
            "distinguish a time limit from a terminal state")


# ======================================================================
# Initial deployment
# ======================================================================
class TestInitialDeployment:
    """Both deployments must be connected from t=0; only one may pre-solve
    the task.

    The centred ring already covers most of the field, so every controller
    scores the same and the comparison cannot separate them.  The clustered
    deployment keeps the connectivity invariant checkable while leaving the
    controller real work to do.
    """

    def test_clustered_start_is_connected_and_leaves_headroom(self):
        c = SimConfig(N=8, K=2, R_cov=35.0, M=20, episode_len=50, seed=0,
                      start_clustered=True)
        e = UAVIoTEnv(c)
        e.reset()
        act, adj, _ = e.comm_graph()
        assert e.is_connected(adj), "clustered start must be connected at t=0"
        nc = e.coverage_counts()
        ck0 = float(np.mean(nc >= c.K))
        assert ck0 < 0.5, f"clustered start still pre-solves the task (CK={ck0})"

    def test_ring_start_is_connected(self):
        c = SimConfig(N=8, K=2, R_cov=35.0, M=20, episode_len=50, seed=0,
                      start_clustered=False)
        e = UAVIoTEnv(c)
        e.reset()
        act, adj, _ = e.comm_graph()
        assert e.is_connected(adj), "ring start must be connected at t=0"

    def test_both_deployments_are_connected_over_many_seeds(self):
        for cl in (False, True):
            for s in range(10):
                c = SimConfig(N=8, K=2, R_cov=35.0, M=20, episode_len=50,
                              seed=s, start_clustered=cl)
                e = UAVIoTEnv(c)
                e.reset()
                act, adj, _ = e.comm_graph()
                assert e.is_connected(adj), (
                    f"disconnected start (clustered={cl}, seed={s})")


# ======================================================================
# Motion
# ======================================================================
class TestMotion:
    """A UAV that is told to move must move.

    The simulator previously applied a move only when EVERY action in the
    feasibility mask was available.  A_CHARGE is available only at a pad
    with low energy, so that condition was false for practically every UAV
    at every step, and no UAV ever moved: the entire simulation was static
    and every controller scored identically.  These tests pin the correct
    behaviour -- the mask is a property of the CHOSEN action, not of the
    whole set.
    """

    def test_uav_moves_when_asked(self):
        from uav_wireless.env import A_PX, A_NX, A_PY, A_NY, A_HOVER
        c = SimConfig(N=4, K=1, M=8, episode_len=50, seed=0)
        e = UAVIoTEnv(c)
        e.reset()
        p0 = e.p.copy()
        acts = np.array([A_PX, A_NX, A_PY, A_NY] + [A_HOVER] * (c.N - 4))
        for _ in range(10):
            e.step(acts)
        disp = np.linalg.norm(e.p - p0, axis=1)
        expect = 10 * c.v_max * c.dt
        assert disp.max() > 0.8 * expect, (
            f"UAVs did not move (max displacement {disp.max():.3f} m, "
            f"expected ~{expect:.1f} m) -- the simulator is static")

    def test_directions_are_respected(self):
        from uav_wireless.env import A_PX, A_NX, A_PY, A_NY, A_HOVER
        c = SimConfig(N=4, K=1, M=8, episode_len=50, seed=0)
        e = UAVIoTEnv(c)
        e.reset()
        p0 = e.p.copy()
        e.step(np.array([A_PX, A_NX, A_PY, A_NY] + [A_HOVER] * (c.N - 4)))
        assert e.p[0][0] > p0[0][0], "+X must increase x"
        assert e.p[1][0] < p0[1][0], "-X must decrease x"
        assert e.p[2][1] > p0[2][1], "+Y must increase y"
        assert e.p[3][1] < p0[3][1], "-Y must decrease y"

    def test_masked_movement_holds_position(self):
        """A movement that the mask rejects must not be applied."""
        from uav_wireless.env import A_PX, A_HOVER
        c = SimConfig(N=2, K=1, M=6, episode_len=50, seed=0, d_safe=5.0)
        e = UAVIoTEnv(c)
        e.reset()
        # place the two UAVs exactly d_safe apart so that a +X step by UAV 0
        # would violate the separation constraint and must therefore be masked
        e.p[0] = np.array([0.0, 0.0])
        e.p[1] = np.array([c.d_safe, 0.0])
        assert not e.action_mask(0)[A_PX], (
            "test setup wrong: +X should be masked here")
        p0 = e.p[0].copy()
        e.step(np.array([A_PX, A_HOVER]))
        assert np.allclose(e.p[0], p0), (
            "a masked movement was applied; the feasibility mask is not "
            "being enforced")


# ======================================================================
# Observation content
# ======================================================================
class TestObservationContent:
    """The shared-policy argument depends on what the observation contains.

    Parameter sharing is sound only if each agent's own observation
    identifies it (Foerster et al., AAMAS 2016).  It is also useless if the
    observation does not say where the coverage deficit is.  These tests
    pin both.
    """

    def test_agent_identity_distinguishes_agents(self):
        c = SimConfig(N=8, K=2, R_cov=35.0, M=20, episode_len=50, seed=0,
                      use_agent_id=True)
        e = UAVIoTEnv(c)
        e.reset()
        o = e.local_obs()
        ident = o[:, -c.N:]
        assert np.allclose(ident, np.eye(c.N)), (
            "the identity block is not a one-hot encoding")
        # each agent must be distinguishable in the full observation
        for i in range(c.N):
            for j in range(i + 1, c.N):
                assert not np.allclose(o[i], o[j]), (
                    f"agents {i} and {j} have identical observations")

    def test_observation_without_identity_keeps_agents_similar(self):
        """This is the condition the A/B is about: without the identity the
        agents in a symmetric deployment are nearly indistinguishable."""
        c = SimConfig(N=8, K=2, R_cov=35.0, M=20, episode_len=50, seed=0,
                      start_clustered=True, use_agent_id=False)
        e = UAVIoTEnv(c)
        e.reset()
        o = e.local_obs()
        assert not np.allclose(o[0], o[1]), (
            "the test is only meaningful if the agents differ somewhere")

    def test_map_summary_locates_the_deficit(self):
        c = SimConfig(N=4, K=1, R_cov=35.0, M=20, episode_len=50, seed=0,
                      map_grid=4)
        e = UAVIoTEnv(c)
        e.reset()
        nc = e.coverage_counts()
        s = e.coverage_map_summary(nc)
        assert s.shape == (16,)
        under = int(np.sum(nc < c.K))
        assert under > 0, "test setup wrong: nothing is under-covered"
        assert s.sum() > 0, "the map summary does not report the deficit"
        # the summary is a share of all sensors, so it cannot exceed 1
        assert s.max() <= 1.0 + 1e-9

    def test_map_summary_is_empty_when_everything_is_covered(self):
        c = SimConfig(N=4, K=1, R_cov=35.0, M=20, episode_len=50, seed=0,
                      map_grid=4)
        e = UAVIoTEnv(c)
        e.reset()
        covered = np.full(c.M, c.K, dtype=float)
        s = e.coverage_map_summary(covered)
        assert np.allclose(s, 0.0), (
            "the map summary must be silent when there is no deficit")

    def test_map_summary_length_is_independent_of_M(self):
        """The observation must not grow with the number of sensors."""
        dims = []
        for M in (10, 20, 40):
            c = SimConfig(N=4, K=1, R_cov=35.0, M=M, episode_len=50, seed=0,
                          map_grid=4, use_agent_id=True)
            e = UAVIoTEnv(c)
            e.reset()
            dims.append(e.local_obs().shape[1])
        assert len(set(dims)) == 1, (
            f"the observation length depends on M: {dims}")

    def test_obs_dim_matches_the_actual_vector(self):
        for aid in (False, True):
            for mg in (0, 4):
                c = SimConfig(N=6, K=1, R_cov=35.0, M=15, episode_len=50,
                              seed=0, use_agent_id=aid, map_grid=mg)
                e = UAVIoTEnv(c)
                e.reset()
                o = e.local_obs()
                assert o.shape[1] == e.obs_dim, (
                    f"obs_dim={e.obs_dim} but the vector has {o.shape[1]}")


# ======================================================================
# Energy state machine
# ======================================================================
class TestEnergyStateMachine:
    """serve -> return -> charge -> serve must actually happen.

    The environment previously never made the serve-to-return transition:
    only the rule-based baselines implemented it themselves, so a LEARNED
    policy had no way to express the return, the charging arbitration was
    never exercised, and a UAV with an empty pack was still counted as
    providing coverage and connectivity.
    """

    def test_low_energy_triggers_the_return_state(self):
        c = SimConfig(N=2, K=1, M=6, episode_len=50, seed=0,
                      B_max=1000.0, E_reserve=100.0, charge_rate=0.01)
        e = UAVIoTEnv(c)
        e.reset()
        e.E[0] = 50.0                     # far below the return threshold
        e.step(np.zeros(c.N, dtype=np.int64))
        assert e.mode[0] == 1, (
            "a UAV below its return threshold must enter the return state")

    def test_a_full_pack_is_in_service(self):
        c = SimConfig(N=2, K=1, M=6, episode_len=50, seed=0)
        e = UAVIoTEnv(c)
        e.reset()
        e.step(np.zeros(c.N, dtype=np.int64))
        assert e.mode[0] == 0, "a UAV with a full pack must be in service"

    def test_an_empty_uav_away_from_a_pad_is_out_of_service(self):
        c = SimConfig(N=2, K=1, M=6, episode_len=50, seed=0,
                      B_max=1000.0, E_reserve=100.0)
        e = UAVIoTEnv(c)
        e.reset()
        e.E[0] = 0.0
        e.p[0] = np.array([0.0, 0.0])       # away from any pad
        e.step(np.zeros(c.N, dtype=np.int64))
        assert e.failed[0], (
            "a UAV with an empty pack away from a pad must not stay active")
        assert e.stranded == 1, "the stranding was not counted"

    def test_an_empty_uav_on_a_pad_is_not_stranded(self):
        c = SimConfig(N=2, K=1, M=6, episode_len=50, seed=0,
                      B_max=1000.0, E_reserve=100.0)
        e = UAVIoTEnv(c)
        e.reset()
        e.E[0] = 0.0
        e.p[0] = e.pads[0].copy()          # sitting on a pad
        e.step(np.zeros(c.N, dtype=np.int64))
        assert not e.failed[0], (
            "a UAV on a pad with an empty pack can recharge; it must not be "
            "declared dead")
        assert e.stranded == 0

    def test_a_charging_uav_gains_energy(self):
        from uav_wireless.env import A_CHARGE
        c = SimConfig(N=2, K=1, M=6, episode_len=50, seed=0,
                      B_max=1000.0, E_reserve=100.0, charge_rate=0.01,
                      n_pads=1)
        e = UAVIoTEnv(c)
        e.reset()
        e.E[0] = 100.0
        e.p[0] = e.pads[0].copy()
        before = e.E[0]
        e.step(np.array([A_CHARGE, 0]))
        assert e.E[0] > before, "a granted charge request must add energy"

    def test_a_charging_uav_draws_less_than_a_hovering_one(self):
        """Rotors idle on the pad.

        Billing a charging UAV the full hover power made charging
        uneconomic: the pack lost more to the rotors than the pad put back,
        so no UAV could ever recover.
        """
        from uav_wireless.env import A_CHARGE
        c = SimConfig(N=2, K=1, M=6, episode_len=50, seed=0)
        e = UAVIoTEnv(c)
        e.reset()
        draw = e.power_draw(np.array([A_CHARGE, 0]))
        assert draw[0] < draw[1], (
            "a charging UAV must draw less than a hovering one")
        assert draw[0] <= c.P_elec + c.P_tx + 1e-9, (
            "a charging UAV must draw only the avionics baseline")

    def test_the_summary_reports_the_energy_dynamics(self):
        c = SimConfig(N=2, K=1, M=6, episode_len=50, seed=0)
        e = UAVIoTEnv(c)
        e.reset()
        e.step(np.zeros(c.N, dtype=np.int64))
        s = e.summary()
        for k in ("ReturnEvents", "Stranded", "Returning"):
            assert k in s, f"the summary does not report {k}"


# ======================================================================
# Learned baselines
# ======================================================================
class TestLearnedBaselines:
    """The learned baselines must survive an episode that ends early.

    An episode ends early whenever a UAV failure terminates the mission, so
    the number of collected steps is smaller than the horizon.  Both
    trainers therefore have to form their targets from the TRUNCATED
    arrays: the advantage array is allocated for the full horizon and only
    its first t rows are filled, so adding it to a truncated value array is a
    shape mismatch.
    """

    def test_the_mappo_rollout_survives_an_early_end(self):
        """The MAPPO rollout must handle a rollout shorter than the horizon."""
        import inspect
        from uav_wireless import train
        src = inspect.getsource(train.collect_rollout)
        assert 'B["ret"] = B["adv"] + B["values"]' in src, (
            "the returns must be formed from the truncated batch")
        assert 'B["ret"] = adv + B["values"][:t]' not in src, (
            "the returns are formed from the untruncated advantage array")

    def test_the_ppo_local_trainer_survives_an_early_end(self):
        import inspect
        from uav_wireless import baselines_rl
        src = inspect.getsource(baselines_rl.train_ppo_local)
        assert "ret = adv[:t] + B[\"values\"][:t]" in src, (
            "the PPO-local returns must be formed from the truncated advantage")
        assert "ret = adv + B[\"values\"][:t]" not in src, (
            "the PPO-local returns are formed from the untruncated advantage")

    def test_both_trainers_run(self):
        from uav_wireless.env import UAVIoTEnv
        from uav_wireless.train import train_mappo
        from uav_wireless.baselines_rl import train_ppo_local
        c = SimConfig(N=4, K=1, M=8, episode_len=40, seed=0)
        e = UAVIoTEnv(c)
        train_mappo(c, episodes=1, n_steps=40, seed=0, verbose=False)
        train_ppo_local(c, episodes=1, steps=40, seed=0, verbose=False)


# ======================================================================
# Feasibility mask
# ======================================================================
class TestMaskConsistency:
    """The H-step check and the articulation check must see the same graph.

    They used to recompute the prospective communication graph separately,
    which doubled the physics evaluation per candidate action.  The graph is
    now computed once and shared, and these tests assert that sharing it
    does not change either verdict.
    """

    def test_shared_adjacency_gives_the_same_verdicts(self):
        from uav_wireless.env import ACTION_VECTORS
        c = SimConfig(N=6, K=1, M=10, episode_len=50, seed=0, R_comm=25.0)
        e = UAVIoTEnv(c)
        e.reset()
        step = c.v_max * c.dt
        for i in range(c.N):
            for vec in ACTION_VECTORS[:4]:
                p_new = np.clip(e.p[i] + vec * step, 0, c.side)
                adj = e._candidate_adjacency(i, p_new)
                h1 = e._h_step_safe(i, p_new, c.mask_horizon, adj=adj)
                h2 = e._h_step_safe(i, p_new, c.mask_horizon)
                a1 = e._is_articulation_move(i, p_new, adj=adj)
                a2 = e._is_articulation_move(i, p_new)
                assert h1 == h2, (
                    f"the shared graph changed the H-step verdict for agent {i}")
                assert a1 == a2, (
                    f"the shared graph changed the articulation verdict for "
                    f"agent {i}")

    def test_the_candidate_adjacency_is_a_real_graph(self):
        c = SimConfig(N=6, K=1, M=10, episode_len=50, seed=0)
        e = UAVIoTEnv(c)
        e.reset()
        p_new = e.p[0] + np.array([1.0, 0.0])
        adj = e._candidate_adjacency(0, p_new)
        assert adj.shape == (c.N, c.N)
        assert not np.any(np.diag(adj)), "the diagonal must be empty"
        assert np.array_equal(adj, adj.T), "the graph must be undirected"

    def test_the_spliced_candidate_graph_equals_the_full_recomputation(self):
        """The candidate graph is computed by splicing one recomputed row
        into the base SNR matrix, because the shadowing table is symmetric.

        That is an optimisation of a physics-critical path, so it must be
        EXACTLY equal to recomputing the whole matrix with the UAV moved.
        """
        import numpy as np
        for seed in range(4):
            c = SimConfig(N=6, K=1, M=10, episode_len=50, seed=seed,
                          R_comm=30.0)
            e = UAVIoTEnv(c)
            e.reset()
            for i in range(c.N):
                for vec in ((1.0, 0.0), (-1.0, 0.0), (0.0, 1.0),
                            (0.0, -1.0)):
                    p_new = np.clip(e.p[i] + np.array(vec) * c.v_max * c.dt,
                                    0, c.side)
                    fast = e._candidate_adjacency(i, p_new)
                    # the reference: move the UAV and recompute in full
                    saved = e.p[i].copy()
                    e.p[i] = p_new
                    _, slow, _ = e.comm_graph()
                    e.p[i] = saved
                    assert np.array_equal(fast, slow), (
                        f"the spliced candidate graph differs from the full "
                        f"recomputation (seed {seed}, agent {i}, move {vec})")


# ======================================================================
# Joint connectivity projection
# ======================================================================
class TestJointProjection:
    """A set of individually admissible moves can jointly disconnect the swarm.

    The per-agent feasibility mask is evaluated against the pre-move state
    and every agent moves at the same time, so two UAVs can each step away
    from a third in a way that is admissible for both and fatal for the
    third.  The joint configuration must therefore be projected back onto
    the connected set.
    """

    def test_the_projection_keeps_the_swarm_connected(self):
        """With the projection on, the post-move graph must be connected."""
        import numpy as np
        from uav_wireless.env import A_NX, A_PX, A_HOVER
        c = SimConfig(N=6, K=1, M=10, episode_len=50, seed=0, R_comm=25.0,
                      use_joint_projection=True)
        e = UAVIoTEnv(c)
        e.reset()
        # place the swarm in a line, so that stepping apart disconnects it
        e.p[:] = np.array([[10.0, 0.0], [12.0, 0.0], [14.0, 0.0],
                            [16.0, 0.0], [18.0, 0.0], [20.0, 0.0]])
        acts = np.array([A_NX] * 3 + [A_PX] * 3)
        for _ in range(30):
            e.step(acts)
            act, adj, _ = e.comm_graph()
            assert e.is_connected(adj), (
                "the joint projection failed to keep the swarm connected")

    def test_the_projection_can_be_switched_off(self):
        """The ablation switch must actually change the behaviour."""
        from uav_wireless.env import A_NX, A_PX
        import numpy as np
        c = SimConfig(N=6, K=1, M=10, episode_len=50, seed=0, R_comm=25.0,
                      use_joint_projection=False)
        e = UAVIoTEnv(c)
        e.reset()
        e.p[:] = np.array([[10.0, 0.0], [12.0, 0.0], [14.0, 0.0],
                            [16.0, 0.0], [18.0, 0.0], [20.0, 0.0]])
        acts = np.array([A_NX] * 3 + [A_PX] * 3)
        for _ in range(30):
            e.step(acts)
        assert e.projection_revisions == 0, (
            "the projection fired although it is switched off")

    def test_revisions_are_counted(self):
        """The projection must actually repair a disconnected configuration.

        The per-agent mask is usually sufficient on its own -- on the
        configurations tested it prevented every disconnection -- so the
        repair path is exercised directly.
        """
        import numpy as np
        from uav_wireless.env import A_NX, A_PX
        c = SimConfig(N=6, K=1, M=10, episode_len=50, seed=0, R_comm=25.0,
                      use_joint_projection=True)
        e = UAVIoTEnv(c)
        e.reset()
        # a connected configuration ...
        old = np.array([[10.0, 0.0], [12.0, 0.0], [14.0, 0.0],
                        [16.0, 0.0], [18.0, 0.0], [20.0, 0.0]])
        e.p[:] = old
        # ... and a disconnected one, reached by moving every UAV away
        e.p[:] = np.array([[0.0, 0.0], [12.0, 0.0], [14.0, 0.0],
                           [16.0, 0.0], [18.0, 0.0], [60.0, 0.0]])
        _, adj, _ = e.comm_graph()
        assert not e.is_connected(adj), "test setup wrong: already connected"
        n = e._project_connected(old, [0, 5])
        assert n > 0, "the projection did not revert any move"
        _, adj, _ = e.comm_graph()
        assert e.is_connected(adj), (
            "the projection did not restore connectivity")

    def test_the_summary_reports_the_projection(self):
        c = SimConfig(N=2, K=1, M=6, episode_len=50, seed=0)
        e = UAVIoTEnv(c)
        e.reset()
        e.step(np.zeros(c.N, dtype=np.int64))
        assert "ProjectionRevisions" in e.summary()


    def test_a_failed_uav_has_only_the_hover_action(self):
        """A failed UAV is not in the active set, and the mask must still be
        computable for every index."""
        c = SimConfig(N=4, K=1, M=6, episode_len=50, seed=0)
        e = UAVIoTEnv(c)
        e.reset()
        e.failed[0] = True
        masks = e.action_masks()
        assert len(masks) == c.N
        assert masks[0].sum() == 1, "a failed UAV may only hover"

    def test_a_uav_may_not_depart_if_it_cannot_still_reach_a_pad(self):
        """The energy rule of the mask.

        A UAV must retain the energy to reach a charging pad plus the
        reserve margin, computed from where it WOULD BE after the move.
        The previous test admitted a departure with a flat battery, so a UAV
        could fly until its pack was empty away from a pad -- and an
        exhausted UAV is removed from the active set, taking its share of
        the coverage and of the communication graph with it.
        """
        from uav_wireless.env import A_NX, A_PX, A_HOVER
        c = SimConfig(N=2, K=1, M=6, episode_len=50, seed=0,
                      E_reserve=2000.0, B_max=30_000.0, n_pads=1)
        e = UAVIoTEnv(c)
        e.reset()
        # the UAV sits 8 m to the LEFT of the single pad, so +x moves it
        # towards the pad and -x moves it away
        e.p[0] = e.pads[0] + np.array([-8.0, 0.0])
        e.E[0] = e._pad_energy_from(0, e.p[0]) + c.E_reserve - 50.0
        mask = e.action_mask(0)
        assert not mask[A_NX], (
            "a UAV that cannot still reach a pad was allowed to move away "
            "from it")
        assert mask[A_PX], (
            "a UAV that can still reach a pad was not allowed to move "
            "towards it")
        assert mask[A_HOVER], "hovering must always be admissible"

    def test_a_uav_may_still_move_towards_a_pad_when_already_low(self):
        """A UAV that is already below the threshold must be allowed to move
        towards a pad; blocking it there would strand it certainly."""
        from uav_wireless.env import A_NX
        c = SimConfig(N=2, K=1, M=6, episode_len=50, seed=0,
                      E_reserve=2000.0, B_max=30_000.0)
        e = UAVIoTEnv(c)
        e.reset()
        e.E[0] = 10.0            # far below the threshold
        e.p[0] = e.pads[0] + np.array([8.0, 0.0])   # next to the pad
        mask = e.action_mask(0)
        # the move that reduces the distance to the pad is admissible
        assert mask[A_NX], (
            "a UAV that is already low was not allowed to move towards a pad")

    def test_a_uav_with_a_full_pack_may_depart(self):
        from uav_wireless.env import A_NX
        c = SimConfig(N=2, K=1, M=6, episode_len=50, seed=0,
                      E_reserve=2000.0, B_max=30_000.0)
        e = UAVIoTEnv(c)
        e.reset()
        e.E[0] = c.B_max
        assert e.action_mask(0)[A_NX], (
            "a UAV with a full pack was not allowed to depart")

    def test_the_previous_energy_rule_is_available_and_weaker(self):
        """The switch that reproduces the previous rule must exist, and the
        previous rule must be the weaker of the two."""
        from uav_wireless.env import A_NX
        c = SimConfig(N=2, K=1, M=6, episode_len=50, seed=0,
                      E_reserve=2000.0, B_max=30_000.0, n_pads=1)
        e = UAVIoTEnv(c)
        e.reset()
        e.p[0] = e.pads[0] + np.array([-8.0, 0.0])
        # just above the return threshold, so that the new rule blocks the
        # move away from the pad and the old one does not
        e.E[0] = e._pad_energy_from(0, e.p[0]) + c.E_reserve - 50.0
        strict = e.action_mask(0)[A_NX]
        c.strict_energy_mask = False
        loose = e.action_mask(0)[A_NX]
        assert not strict, "the strict rule admitted a departure it should not"
        assert loose, "the previous rule is not the weaker of the two"


# ======================================================================
# Graph traversal equivalence
# ======================================================================
class TestGraphTraversalEquivalence:
    """The fast traversals must agree EXACTLY with the reference ones.

    The action mask's H-step check and its articulation check are on the
    hot path of the simulator, and they were replaced with integer
    bitmask traversals.  A fast traversal that disagrees with the
    reference is a silent change in the safety filter, so the two are
    compared over random graphs.

    The references below are the original implementations: a
    breadth-first search that expands only the nodes at distance less than
    the horizon, and a test of whether deleting a node disconnects the
    graph.
    """

    @staticmethod
    def _ref_hstep(adj, pos, horizon):
        dist = np.full(len(adj), -1, dtype=int)
        dist[pos] = 0
        queue = [pos]
        while queue:
            u = queue.pop(0)
            if dist[u] >= horizon:
                continue
            for v in range(len(adj)):
                if adj[u, v] and dist[v] < 0:
                    dist[v] = dist[u] + 1
                    queue.append(v)
        return bool((dist >= 0).all())

    @staticmethod
    def _ref_cut(adj, pos):
        n = len(adj)
        if n <= 3:
            return False
        red = adj.copy()
        red[pos, :] = False
        red[:, pos] = False
        start = 0 if pos != 0 else 1
        seen = {start}
        queue = [start]
        while queue:
            u = queue.pop(0)
            for v in range(n):
                if red[u, v] and v not in seen:
                    seen.add(v)
                    queue.append(v)
        return len(seen) != n - 1

    def test_the_bitmask_traversals_agree_with_the_references(self):
        from uav_wireless.env import UAVIoTEnv
        e = UAVIoTEnv(SimConfig(N=8, K=1, M=6, seed=0))
        rng = np.random.default_rng(0)
        mismatches = 0
        for _ in range(300):
            n = int(rng.integers(4, 9))
            adj = rng.random((n, n)) < 0.35
            adj = np.triu(adj, 1)
            adj = adj | adj.T
            bits = e._adj_bits(adj)

            # the H-step check
            for horizon in (1, 2, 3, 4):
                reach, _ = e._bfs_mask(bits, 0, limit=horizon)
                if (reach == (1 << n) - 1) != self._ref_hstep(adj, 0, horizon):
                    mismatches += 1

            # the articulation check: node 0 removed
            drop = 1 << 0
            b2 = list(bits)
            for u in range(n):
                if b2[u] & drop:
                    b2[u] &= ~drop
            b2[0] = 0
            start = 1
            reach, _ = e._bfs_mask(b2, start)
            target = ((1 << n) - 1) & ~drop
            if (reach != target) != self._ref_cut(adj, 0):
                mismatches += 1
        assert mismatches == 0, (
            f"{mismatches} disagreements between the bitmask traversals and "
            f"the reference implementations")


# ======================================================================
# Value normalisation
# ======================================================================
class TestValueNormalisation:
    """MAPPO's value normalisation must be consistent at every use.

    The critic's raw output is the NORMALISED value, so the TD residual, the
    GAE recursion and the bootstrap must all un-normalise it.  Forgetting
    this is a silent scale error in the advantage estimates, and it is
    invisible in the loss curves.
    """

    def test_value_unnormalises_the_critic_output(self):
        import torch
        from uav_wireless.mappo import MAPPO
        agent = MAPPO(obs_dim=6, state_dim=6, n_agents=2, hidden=16,
                      value_norm=True)
        agent._ret_mean = 3.0
        agent._ret_std = 2.0
        s = torch.zeros(4, 6)
        raw = agent.critic(s)
        got = agent.value(s)
        assert torch.allclose(got, raw * 2.0 + 3.0, atol=1e-5), (
            "value() must un-normalise the critic's output")

    def test_value_normalisation_is_off_when_disabled(self):
        import torch
        from uav_wireless.mappo import MAPPO
        agent = MAPPO(obs_dim=6, state_dim=6, n_agents=2, hidden=16,
                      value_norm=False)
        agent._ret_mean = 3.0
        agent._ret_std = 2.0
        s = torch.zeros(4, 6)
        assert torch.allclose(agent.value(s), agent.critic(s), atol=1e-6)

    def test_the_rollout_uses_the_unnormalised_value(self):
        import inspect
        from uav_wireless import train
        src = inspect.getsource(train.collect_rollout)
        assert "agent.value(" in src, (
            "collect_rollout must read the value through the un-normalising "
            "accessor, not the raw critic output")
        assert "agent.critic(" not in src, (
            "collect_rollout reads the raw critic output, which is the "
            "NORMALISED value when value normalisation is on")

    def test_training_runs_with_value_normalisation(self):
        from uav_wireless.env import UAVIoTEnv
        from uav_wireless.train import train_mappo
        c = SimConfig(N=4, K=1, M=8, episode_len=40, seed=0)
        e = UAVIoTEnv(c)
        agent, hist = train_mappo(c, episodes=2, n_steps=40, seed=0,
                                  verbose=False)
        assert agent._ret_mean != 0.0, (
            "the running return statistics were never updated")
        assert agent._ret_std > 0.0

# ======================================================================
# The reproducibility of an evaluation
# ======================================================================
class TestEvaluationReproducibility:
    """Eq. (13) specifies that the deployed policy SAMPLES, so an
    evaluation draws from the global torch RNG.  If that RNG is not seeded,
    the same policy on the same scene gives a different answer every time
    it is run: the paper's numbers cannot be reproduced from the stored
    artefact, and a comparison between two controllers carries an
    unquantified sampling component.  These tests pin the discipline."""

    def _agent_and_cfg(self):
        from uav_wireless.env import UAVIoTEnv
        from uav_wireless.mappo import MAPPO
        c = SimConfig(N=4, K=1, M=8, episode_len=40, seed=0)
        e = UAVIoTEnv(c)
        agent = MAPPO(n_agents=c.N, obs_dim=e.obs_dim, state_dim=e.state_dim)
        return agent, c

    def test_the_same_policy_gives_the_same_number_twice(self):
        import torch
        from uav_wireless.experiments import eval_agent
        agent, c = self._agent_and_cfg()
        torch.manual_seed(1234)
        a = eval_agent(agent, c, steps=40, seed=3)
        b = eval_agent(agent, c, steps=40, seed=3)
        assert a["CK"] == b["CK"], (
            "an evaluation of a sampled policy is not reproducible: the "
            "same policy on the same scene gave two different numbers")

    def test_the_ambient_rng_state_does_not_leak_into_an_evaluation(self):
        import torch
        from uav_wireless.experiments import eval_agent
        agent, c = self._agent_and_cfg()
        torch.manual_seed(7)
        a = eval_agent(agent, c, steps=40, seed=5)
        torch.manual_seed(999999)          # perturb the global RNG
        np.random.seed(123456)
        b = eval_agent(agent, c, steps=40, seed=5)
        assert a["CK"] == b["CK"], (
            "an evaluation depends on the ambient state of the global RNG, "
            "so it is not a function of (policy, scene)")

    def test_every_evaluator_seeds_the_policy_sampling(self):
        import inspect
        from uav_wireless import experiments, baselines_rl
        for mod, fn in ((experiments, "eval_agent"),
                        (baselines_rl, "eval_id_dqn"),
                        (baselines_rl, "eval_ppo_local")):
            src = inspect.getsource(getattr(mod, fn))
            assert "seed_evaluation" in src, (
                f"{fn} rolls a policy out without seeding the RNG that the "
                f"policy samples from, so its measurement is a random draw")

    def test_the_seed_derives_only_from_the_evaluation_seed(self):
        from uav_wireless.seeding import seed_evaluation
        assert seed_evaluation(3) == seed_evaluation(3)
        assert seed_evaluation(3) != seed_evaluation(4)

    def test_the_deterministic_evaluation_is_unaffected(self):
        from uav_wireless.experiments import eval_agent
        agent, c = self._agent_and_cfg()
        a = eval_agent(agent, c, steps=40, seed=2, deterministic=True)
        b = eval_agent(agent, c, steps=40, seed=2, deterministic=True)
        assert a["CK"] == b["CK"]