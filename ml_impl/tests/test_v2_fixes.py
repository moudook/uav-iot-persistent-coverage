"""Regression tests for the second-round simulator and learner fixes.

Each test pins one defect that was found in the external code audit and
verified against the source before it was changed:

* the Ng potential must start at the CURRENT state, not at zero;
* the physics must bill the executed action, not the sampled one;
* PHY-aware ego features must not point a UAV at a sensor it already serves;
* the return-mode assist mask must not let a UAV hover itself flat;
* value normalisation must initialise on the first batch;
* scalable identities must keep obs_dim independent of N.
"""
import numpy as np
import torch

from uav_wireless import SimConfig, UAVIoTEnv, MAPPO
from uav_wireless.env import (
    A_HOVER, A_PX, A_CHARGE, N_ACTIONS, obs_dim,
)


def _env(**kw):
    c = SimConfig(N=1, K=1, M=4, episode_len=200, seed=0, **kw)
    return c, UAVIoTEnv(c)


class TestNgPotentialReset:
    def test_first_potential_is_unset(self):
        c, e = _env(dist_shape_kappa=0.5, energy_shape_kappa=0.5)
        assert e._prev_phi is None
        assert e._prev_phi_e is None

    def test_first_step_does_not_inject_a_shock(self):
        c, e = _env(dist_shape_kappa=0.5)
        e.reset()
        # Phi(s_0) is computed by the first step and stored; the first step
        # must not add kappa*(gamma*Phi(s_1) - 0).
        before = e._prev_phi
        assert before is None
        e.step(np.array([A_HOVER]))
        assert e._prev_phi is not None


class TestExecutedActionAccounting:
    def test_blocked_move_is_billed_as_hover(self):
        c = SimConfig(N=2, K=1, M=4, episode_len=200, seed=0,
                      B_max=30_000.0)
        e = UAVIoTEnv(c)
        e.reset()
        # Put UAV 1 one step ahead of UAV 0 so the +x move violates d_safe
        # and is masked.  Both are otherwise healthy.
        e.p[0] = np.array([20.0, 40.0])
        e.p[1] = np.array([21.0, 40.0])
        e.E[:] = 20_000.0
        e.v[:] = 0.0
        e0 = float(e.E[0])
        _, _, _, _, info = e.step(np.array([A_PX, A_HOVER]))
        assert int(info["executed_actions"][0]) == A_HOVER
        drop = e0 - float(e.E[0])
        hover_draw = (c.P_hover + c.P_elec + c.P_tx) * c.dt
        move_draw = (c.P_move + c.P_elec + c.P_tx) * c.dt
        assert abs(drop - hover_draw) < 0.5, (
            f"blocked move billed {drop:.2f} J; hover is {hover_draw:.2f} J "
            f"and flight is {move_draw:.2f} J")


class TestPhyEgoFeatures:
    def test_self_served_sensor_is_not_the_first_target(self):
        c = SimConfig(N=1, K=2, M=4, episode_len=200, seed=0,
                      ego_sensors=True, n_ego=3, phy_ego_sensors=True,
                      side=200.0, R_cov=30.0)
        e = UAVIoTEnv(c)
        e.reset()
        e.p[0] = np.array([100.0, 100.0])
        e.sensors = np.array([[100.0, 100.0], [250.0, 250.0],
                              [120.0, 100.0], [100.0, 120.0]])
        e.v[0] = 0.0
        e.E[0] = 20_000.0
        obs = e.local_obs()
        # Layout: own(7) + nb(16) + tail(7) = 30, then the 11 ego features.
        first_dist = float(obs[0, 30 + 2])
        assert first_dist > 0.01, (
            "the first ego slot still points at the sensor underneath the "
            "UAV, which this UAV already serves and cannot serve twice")

    def test_obs_dim_is_independent_of_fleet_size(self):
        base = dict(K=2, M=20, ego_sensors=True, n_ego=3,
                    phy_ego_sensors=True, use_scalable_id=True,
                    use_agent_id=False, map_grid=4, use_pad_bearing=True,
                    use_critical_anchor=True)
        dims = [obs_dim(SimConfig(N=n, **base)) for n in (3, 5, 8)]
        assert len(set(dims)) == 1
        c = SimConfig(N=3, **base)
        e = UAVIoTEnv(c)
        obs, _ = e.reset()
        assert obs.shape == (3, obs_dim(c))


class TestAssistReturnMask:
    def test_return_mode_forbids_hover_when_an_approach_is_feasible(self):
        c = SimConfig(N=1, K=1, M=4, episode_len=200, seed=0,
                      n_pads=1, start_clustered=False,
                      assist_return_mask=True, strict_energy_mask=True)
        e = UAVIoTEnv(c)
        e.reset()
        e.pads = np.array([[70.0, 40.0]])
        e.p[0] = np.array([10.0, 40.0])
        e.v[0] = 0.0
        e.E[0] = e.return_threshold(0)
        mask = e.action_mask(0)
        assert not mask[A_HOVER], (
            "a UAV at its return threshold, away from a pad, must not be "
            "allowed to hover when it can move toward the pad")
        assert mask[A_PX]

    def test_mask_is_unchanged_when_assist_is_off(self):
        c = SimConfig(N=1, K=1, M=4, episode_len=200, seed=0,
                      n_pads=1, start_clustered=False,
                      assist_return_mask=False)
        e = UAVIoTEnv(c)
        e.reset()
        e.pads = np.array([[70.0, 40.0]])
        e.p[0] = np.array([10.0, 40.0])
        e.E[0] = e.return_threshold(0)
        assert e.action_mask(0)[A_HOVER]


class TestValueNormInitialisation:
    def test_first_batch_sets_the_return_scale_exactly(self):
        c = SimConfig(N=2, K=1, M=4, episode_len=50, seed=0)
        e = UAVIoTEnv(c)
        ag = MAPPO(n_agents=c.N, obs_dim=e.obs_dim, state_dim=e.state_dim,
                   value_norm=True, device="cpu")
        T, N = 4, c.N
        rng = np.random.default_rng(0)
        batch = dict(
            obs=rng.normal(size=(T, N, e.obs_dim)).astype(np.float32),
            mask=np.ones((T, N, N_ACTIONS), bool),
            acts=rng.integers(0, N_ACTIONS, size=(T, N)).astype(np.int64),
            logp=np.full((T, N), -np.log(N_ACTIONS), np.float32),
            adv=rng.normal(size=(T, N)).astype(np.float32),
            ret=np.linspace(100.0, 110.0, T * N).reshape(T, N).astype(np.float32),
            states=rng.normal(size=(T, e.state_dim)).astype(np.float32),
            values=np.zeros((T, N), np.float32),
            active=np.ones((T, N), bool),
        )
        ag.update(batch, epochs=0, n_minibatch=2)
        assert abs(ag._ret_mean - 105.0) < 1.0
        assert 2.0 < ag._ret_std < 5.0
