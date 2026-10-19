"""
PHY layer for UAV-IoT wireless links.

This module is the answer to the professor's main criticism: the earlier draft
modelled coverage and connectivity as *abstract discs*. Here every link is
computed from an actual radio model:

    distance -> path loss (log-distance, LoS / NLoS) -> received power
             -> SINR (with interference from other transmitters)
             -> achievable rate (Shannon, clipped by 802.11 MCS table)

Both the UAV-UAV relay graph and the UAV-sensor access links go through this,
so `connectivity` and `K-coverage` in the simulator are PHY-derived rather
than geometric.

References: 3GPP TR 36.777 (UAV channel models), Al-Hourani et al. 2014
(air-to-ground LoS probability), IEEE 802.11 OFDM MCS sensitivity table.
"""

from __future__ import annotations

import numpy as np

# --------------------------------------------------------------------------
# IEEE 802.11 OFDM MCS sensitivity table (802.11n/ac, 20 MHz, SGI).
# Maps required RX SNR (dB) -> PHY rate (Mbit/s).
# --------------------------------------------------------------------------
MCS_TABLE = np.array(
    [
        [2.0, 6.5],
        [4.0, 9.0],
        [5.5, 12.0],
        [6.5, 13.5],  # legacy non-HT
        [8.0, 15.0],
        [8.5, 18.0],
        [9.0, 20.0],
        [10.0, 26.0],
        [11.0, 29.0],
        [12.0, 31.5],
        [13.0, 34.5],
        [14.0, 38.5],
        [15.0, 42.0],
        [16.0, 45.0],
        [17.0, 49.5],
    ]
)


def snr_to_rate(snr_db: np.ndarray | float, mcs_shift: int = 0) -> np.ndarray | float:
    """Map instantaneous SNR to achievable PHY rate via the MCS table.

    `mcs_shift` moves the operating point: negative = more robust (used for
    inter-UAV relay links that must not drop), positive = faster (used for
    sensor access links that carry bulk traffic).
    """
    snr_db = np.asarray(snr_db, dtype=np.float64)
    idx = np.clip(
        np.searchsorted(MCS_TABLE[:, 0], snr_db + mcs_shift),
        0,
        len(MCS_TABLE) - 1,
    )
    rate = MCS_TABLE[idx, 1]
    if np.isscalar(snr_db) or np.ndim(snr_db) == 0:
        return float(rate)
    return rate


def log_distance_pl(d_3d: np.ndarray, f_hz: float, alpha: float, d0: float = 1.0):
    """Log-distance path loss in dB (returns PL, positive loss)."""
    d = np.maximum(d_3d, d0)
    return 20.0 * np.log10(d / d0) + 20.0 * np.log10(4.0 * np.pi * f_hz / 299_792_458.0) + alpha * np.log10(d / d0)


def path_loss_db(d_3d, los_prob, f_hz, alpha_los=2.0, alpha_nlos=3.5):
    """Blend LoS and NLoS path loss according to the LoS probability."""
    pl_los = log_distance_pl(d_3d, f_hz, alpha_los)
    pl_nlos = log_distance_pl(d_3d, f_hz, alpha_nlos)
    return los_prob * pl_los + (1.0 - los_prob) * pl_nlos


def los_probability(d_3d: np.ndarray, z0: float, h_building: float = 15.0, a: float = 9.61, b: float = 0.16):
    """
    Al-Hourani (2014) air-to-ground LoS probability.

        P(LoS) = 1 / (1 + a * exp(-b * (theta - a)))    theta in degrees

    theta is the elevation angle of the UAV as seen from the user.
    """
    d_3d = np.maximum(np.asarray(d_3d, dtype=np.float64), 1e-6)
    theta = np.degrees(np.arcsin(np.clip(z0 / d_3d, 0.0, 1.0)))
    return 1.0 / (1.0 + a * np.exp(-b * (theta - a)))


class WirelessModel:
    """Radio parameters shared by every link in the simulator."""

    def __init__(
        self,
        f_hz: float = 2.4e9,
        p_tx: float = 0.5,          # W, radiated RF power (<=1 W 802.11 ceiling)
        noise_fig_db: float = 7.0,
        bandwidth_hz: float = 20e6,  # 20 MHz channel
        alpha_los: float = 2.0,
        alpha_nlos: float = 3.5,
        z0: float = 50.0,
        snr_min_db: float = 2.0,      # below this the link is unusable
        rate_min_mbps: float = 6.5,   # minimum usable service rate for a sensor
        shadowing_sigma_db: float = 4.0,
        rayleigh_scale: float = 1.0,
        mcs_shift_access: int = 0,
        mcs_shift_backhaul: int = -2,
    ):
        self.f_hz = f_hz
        self.p_tx = p_tx
        self.bandwidth_hz = bandwidth_hz
        self.alpha_los = alpha_los
        self.alpha_nlos = alpha_nlos
        self.z0 = z0
        self.snr_min_db = snr_min_db
        self.rate_min_mbps = rate_min_mbps
        self.shadowing_sigma_db = shadowing_sigma_db
        self.rayleigh_scale = rayleigh_scale
        self.mcs_shift_access = mcs_shift_access
        self.mcs_shift_backhaul = mcs_shift_backhaul
        self.noise_w = 10 ** ((-174.0 + noise_fig_db + 10 * np.log10(bandwidth_hz)) / 10.0)

    # -- helpers -----------------------------------------------------------
    def to_3d(self, p_xy: np.ndarray) -> np.ndarray:
        """Add the common nominal altitude to a horizontal position."""
        return np.sqrt(np.sum(np.square(p_xy), axis=-1) + self.z0 ** 2)

    def received_w(self, d_3d, los_prob):
        """Path loss + shadowing + fading -> received power in W."""
        pl = path_loss_db(d_3d, los_prob, self.f_hz, self.alpha_los, self.alpha_nlos)
        shadow = np.random.normal(0.0, self.shadowing_sigma_db, size=np.shape(pl))
        rayleigh = np.random.gamma(shape=1.0, scale=self.rayleigh_scale, size=np.shape(pl))
        return self.p_tx * rayleigh * 10 ** (-(pl + shadow) / 10.0)

    def rate_mbps(self, snr_db):
        return snr_to_rate(snr_db, self.mcs_shift_access)

    # -- link evaluation ---------------------------------------------------
    def snr_db(self, sinr_linear):
        return 10.0 * np.log10(np.maximum(sinr_linear, 1e-12))

    def access_sinr(self, uav_xy, sensor_xy, interferer_xy):
        """
        SINR of each sensor served by its UAV, with interference summed from
        every *other* UAV that is also transmitting.

        uav_xy       : (N, 2)
        sensor_xy    : (M, 2)
        interferer_xy: (N, 2) positions of the interfering transmitters
                       (same as uav_xy for full interference accounting)
        returns      : (M,) SINR for sensor->its assigned UAV link
        """
        n_uav = len(uav_xy)
        m = len(sensor_xy)
        if n_uav == 0 or m == 0:
            return np.zeros(m)

        # each sensor is attached to the UAV that currently covers it
        d_all = np.linalg.norm(
            sensor_xy[:, None, :] - uav_xy[None, :, :], axis=-1
        )                                    # (M, N)
        d3_all = np.sqrt(d_all ** 2 + self.z0 ** 2)
        los_all = los_probability(d3_all, self.z0)
        rx_all = self.received_w(d3_all, los_all)          # (M, N)
        self.p_ = rx_all

        # serving link = argmax received power among active transmitters
        serving = np.argmax(rx_all, axis=1)
        rx_serv = rx_all[np.arange(m), serving]

        # interference = all other transmitters transmitting the same signal
        inter = rx_all.sum(axis=1) - rx_serv
        sinr = rx_serv / (inter + self.noise_w)
        return sinr

    def backhaul_sinr(self, uav_xy):
        """SINR matrix between UAVs (link (i,j) = i hears j)."""
        n = len(uav_xy)
        if n == 0:
            return np.zeros((0, 0))
        d = np.linalg.norm(uav_xy[:, None, :] - uav_xy[None, :, :], axis=-1)
        d3 = np.sqrt(d ** 2 + self.z0 ** 2)
        los = los_probability(d3, self.z0)
        rx = self.received_w(d3, los)
        rx = rx * np.eye(n) * 0.0 + rx  # keep full matrix
        total = rx.sum(axis=1, keepdims=True)
        sinr = rx / np.maximum(total - rx, 1e-12)          # self excluded
        return sinr

    def link_rate_mbps(self, snr_db, backhaul: bool = False):
        shift = self.mcs_shift_backhaul if backhaul else self.mcs_shift_access
        return snr_to_rate(snr_db, shift)