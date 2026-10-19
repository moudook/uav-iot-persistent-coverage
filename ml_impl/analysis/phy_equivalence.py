"""
Model-equivalence check: Python PHY  vs  INET 4.6 / OMNeT++ 6.4.

WHAT THIS PROVES
----------------
The Python reference PHY (ml_impl/uav_wireless/wireless.py) and INET's
BreakpointPathLoss are the same function.  INET's source
(inet/physicallayer/wireless/common/pathloss/BreakpointPathLoss.cc) reads

    l01 = math::dB2fraction(par("l01"));      // linear path loss at 1 m
    l02 = math::dB2fraction(par("l02"));
    alpha1, alpha2, breakpointDistance
    if (distance < breakpointDistance)
        return 1 / (l01 * pow(distance.get(), alpha1));
    else
        return 1 / (l02 * pow((distance / breakpointDistance).get<unit>(), alpha2));

so the returned quantity is a GAIN, and the path loss in dB is

    PL(d) = 10*log10(l02_linear) + 10*alpha2*log10(d / breakpointDistance)
          = l02_dB + 10*alpha2*log10(d / bp)

which is exactly the log-distance form the Python model implements:

    PL(d) = 20*log10(4*pi*d0*f/c) + 10*n*log10(d/d0)

With the parameters actually recorded by the OMNeT++ run
(Simulation/UAV_IoT_Demo/results/phy_validation_0.sca):

    pathLoss.l01 = 40.04 dB, l02 = 40.04 dB, alpha1 = alpha2 = 2,
    breakpointDistance = 1 m, backgroundNoise.power = -93.99 dBm

the two agree to within the 0.008 dB difference between INET's rounded
reference loss and the analytic free-space reference loss at 1 m.

WHAT THIS DOES NOT PROVE
------------------------
It does not prove that INET's *runtime* produces a per-link physical-layer
measurement in the scenario that was built.  A control configuration
(transmit power crushed by 60 dB) showed that the MAC-level frame count was
identical at every range, i.e. that observable was invalid; and INET's
`minSnir` statistic turned out to be a cached value that did not vary with
node position.  Those negative results are reported rather than hidden.

Run:  python analysis/phy_equivalence.py
"""

from __future__ import annotations

import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np

from uav_wireless import wireless as phy

HERE = os.path.dirname(os.path.abspath(__file__))
RESDIR = os.path.join(
    os.path.dirname(HERE), "..", "Simulation", "UAV_IoT_Demo", "results",
)

# Parameters as recorded by the OMNeT++ run (see the .sca parameter dump).
INET_L01_DB = 40.04
INET_ALPHA = 2.0
INET_BREAKPOINT_M = 1.0
F_HZ = 2.4e9
C = 299792458.0
NOISE_DBM = -93.99
P_TX_W = 0.5


def inet_path_loss_db(d_m, l01_db=INET_L01_DB, alpha=INET_ALPHA,
                      bp=INET_BREAKPOINT_M):
    """INET BreakpointPathLoss, transcribed from BreakpointPathLoss.cc."""
    l_lin = 10 ** (l01_db / 10.0)          # math::dB2fraction(par("l01"))
    if d_m < bp:
        gain = 1.0 / (l_lin * d_m ** alpha)
    else:
        gain = 1.0 / (l_lin * (d_m / bp) ** alpha)
    return -10.0 * math.log10(gain)


def python_path_loss_db(d_m, n=INET_ALPHA, d0=1.0, f_hz=F_HZ):
    """The Python model's path loss (wireless.log_distance_pl)."""
    return float(phy.log_distance_pl(d_m, f_hz, n, d0))


def main():
    print("=" * 78)
    print(" MODEL EQUIVALENCE:  Python log_distance_pl  vs  INET BreakpointPathLoss")
    print("=" * 78)
    print(f" INET recorded params : l01=l02={INET_L01_DB} dB, alpha={INET_ALPHA}, "
          f"breakpoint={INET_BREAKPOINT_M} m")
    print(f" Python reference    : PL(d0) = 20log10(4*pi*d0*f/c) = "
          f"{python_path_loss_db(1.0):.4f} dB, n = {INET_ALPHA}")
    print()

    print(f"{'d (m)':>8} {'n':>5} {'PY PL (dB)':>12} {'INET PL (dB)':>14} "
          f"{'delta (dB)':>11}")
    print("-" * 78)
    worst = 0.0
    rows = []
    for n in (2.0, 3.5):
        for d in (1.0, 5.0, 10.0, 20.0, 35.0, 40.0, 50.0, 61.0, 80.0,
                  100.0, 200.0, 1000.0):
            p = python_path_loss_db(d, n)
            o = inet_path_loss_db(d, INET_L01_DB, n, INET_BREAKPOINT_M)
            delta = o - p
            worst = max(worst, abs(delta))
            rows.append(dict(distance_m=d, n=n, python_pl_db=p, inet_pl_db=o,
                              delta_db=delta))
            print(f"{d:8.0f} {n:5.1f} {p:12.4f} {o:14.4f} {delta:+11.4f}")
    print("-" * 78)
    print(f" worst |delta| over the grid: {worst:.4f} dB")
    print(" => the two implementations are the same function to within the")
    print("    rounding of INET's reference loss (40.04 dB vs 40.048 dB).")

    # SNR agreement at the report's operating radii.
    print()
    print("SNR at the report's operating radii (both models, noise -93.99 dBm):")
    for name, slant in (("R_cov = 35 m (3-D slant 61.0 m)", 61.0),
                        ("R_comm = 40 m (UAV-UAV, 40.0 m)", 40.0)):
        pl = python_path_loss_db(slant)
        rx_dbm = 10 * math.log10(P_TX_W * 1000.0) - pl
        snr = rx_dbm - NOISE_DBM
        rate = float(phy.snr_to_rate(np.array([snr]))[0])
        print(f"  {name:36s} PL={pl:6.2f} dB  Rx={rx_dbm:7.2f} dBm  "
              f"SNR={snr:6.2f} dB  rate={rate:5.1f} Mbps")

    out = os.path.join(HERE, "phy_equivalence.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(dict(rows=rows, worst_delta_db=worst), f, indent=2)
    print(f"\nSaved -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
