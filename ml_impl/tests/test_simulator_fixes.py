"""The four simulator fixes, pinned by tests.

The charger was a limit cycle and none of the 126 tests caught it:
the suite tested that a UAV ENTERS the charge state, not that it can
stay in it long enough to leave.  These four tests pin the properties
the reviewers found broken.
"""
import numpy as np

from uav_wireless import SimConfig, UAVIoTEnv
from uav_wireless.wireless import MCS_TABLE


class TestChargerIsNotALimitCycle:
    """A UAV at a pad must be able to charge ABOVE the return threshold.

    The Charge action was admissible only while E <= return_threshold,
    and the departure rule demanded E_after >= pad_energy(destination)
    + E_reserve.  At a pad the threshold IS E_reserve, so the two
    conditions trapped the UAV: it could not charge above the threshold
    and could not leave without charging above it.
    """

    def _env_at_a_pad(self, energy=2000.0):
        c = SimConfig(N=2, K=1, M=6, episode_len=200, seed=0,
                      B_max=30_000.0, E_reserve=2_000.0, charge_rate=0.0002)
        e = UAVIoTEnv(c)
        e.reset()
        e.p[0] = e.pads[0].copy()
        e.E[0] = energy
        return c, e

    def test_the_charge_action_is_admissible_at_a_pad(self):
        c, e = self._env_at_a_pad()
        mask = e.action_mask(0, base=e._base_graph(e._active_idx()))
        assert mask[5], (
            "a UAV sitting on a pad must be allowed to charge: the old "
            "condition (E <= return_threshold) made the charger's "
            "admission test depend on the same threshold the departure "
            "rule uses")

    def test_a_uav_at_a_pad_can_charge_above_the_return_threshold(self):
        c, e = self._env_at_a_pad()
        thr = e.return_threshold(0)
        for _ in range(40):
            e.step(np.array([5, 0]))
        assert e.E[0] > thr + 100.0, (
            f"a UAV at a pad must be able to charge above the return "
            f"threshold ({thr:.0f} J); it reached {e.E[0]:.0f} J.  With the "
            f"old condition it could not pass the threshold at all, and "
            f"could therefore never satisfy the departure rule.")

    def test_a_charged_uav_can_depart(self):
        c, e = self._env_at_a_pad()
        for _ in range(40):
            e.step(np.array([5, 0]))
        mask = e.action_mask(0, base=e._base_graph(e._active_idx()))
        assert mask[1] or mask[2] or mask[3] or mask[4], (
            "a UAV that has charged above the threshold must be able to "
            "leave the pad: the departure rule needs the energy to reach "
            "a pad from the destination plus the reserve, and the charger "
            "must be able to deliver it")


class TestTheAccessLinkIsAnUplink:
    """The access link is a sensor uplink, budgeted with the sensor's
    own transmit power."""

    def test_the_access_path_uses_the_sensors_power(self):
        c = SimConfig(N=2, K=1, M=6, episode_len=50, seed=0)
        e = UAVIoTEnv(c)
        e.reset()
        assert e.radio.p_tx_sensor < e.radio.p_tx, (
            "the sensor must transmit at less power than the UAV: the "
            "access path used to be budgeted with the UAV's power, which "
            "handed the sensor an advantage it does not have")
        sinr = e._access_sinr_matrix(e.p[:1], e.sensors, np.array([0]))
        # The shadowing is drawn per episode and applies to both budgets,
        # so it cancels in the RATIO: the access path's signal-to-noise
        # ratio must be the UAV's budget scaled by the sensor's power.
        from uav_wireless.wireless import path_loss_db, los_probability
        d3 = np.sqrt(np.sum((e.sensors - e.p[0]) ** 2, axis=-1) + e.radio.z0 ** 2)
        los = los_probability(d3, e.radio.z0)
        pl = path_loss_db(d3, los, e.radio.f_hz, e.radio.n_los, e.radio.n_nlos)
        rx_sensor = e.radio.p_tx_sensor * 10.0 ** (-pl / 10.0)
        rx_uav = e.radio.p_tx * 10.0 ** (-pl / 10.0)
        ratio = (rx_sensor / e.radio.noise_w) / (rx_uav / e.radio.noise_w)
        assert np.allclose(ratio, e.radio.p_tx_sensor / e.radio.p_tx,
                           rtol=1e-9), (
            "the access path must be the sensor's budget, not the UAV's")
        assert np.all(sinr[0] > 0), "the access SINR must be positive"


class TestTheAirToAirPath:
    """Two UAVs at the same altitude: their separation IS the slant
    range, and the air-to-ground LoS probability does not apply."""

    def test_the_separation_is_the_slant_range(self):
        c = SimConfig(N=2, K=1, M=6, episode_len=50, seed=0)
        e = UAVIoTEnv(c)
        e.reset()
        d, d3, los = e.radio.uu_geometry(e.p)
        assert np.allclose(d, d3), (
            "the inter-UAV slant range must be the horizontal separation: "
            "the old code added the altitude twice and charged the link "
            "4.4 dB for an altitude the two ends do not differ in")
        assert np.allclose(los, 1.0), (
            "an air-to-air path is not an air-to-ground path: the "
            "ground-reference LoS probability must not be applied to it")


class TestTheMCSTable:
    """The table is the 802.11n 20 MHz set, and the selection is a
    search over a sorted threshold column."""

    def test_the_table_is_the_standard_set(self):
        rates = [row[1] for row in MCS_TABLE]
        assert rates == [6.5, 13.0, 19.5, 26.0, 39.0, 52.0, 58.5, 65.0], (
            "the MCS table must be the 802.11n 20 MHz rate set")

    def test_the_threshold_column_is_sorted(self):
        snrs = [row[0] for row in MCS_TABLE]
        assert all(b > a for a, b in zip(snrs, snrs[1:])), (
            "the selection is a search over the threshold column, so it "
            "must be sorted")

    def test_the_service_gate_is_the_lowest_mcs(self):
        from uav_wireless.wireless import snr_to_rate
        assert snr_to_rate(MCS_TABLE[0, 0] - 0.1) == 0.0, (
            "below the lowest MCS's threshold no rate is usable")
        assert snr_to_rate(MCS_TABLE[0, 0]) == MCS_TABLE[0, 1], (
            "at the threshold the lowest MCS is usable")
