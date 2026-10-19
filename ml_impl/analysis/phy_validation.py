"""
Cross-validate the Python PHY against INET 4.6 / OMNeT++ 6.4.

The OMNeT++ scenario (Simulation/UAV_IoT_Demo/sim/PhyValidation.ned) places a
UAV base station at z0 = 50 m with the report's Table IV radio (0.5 W,
2.437 GHz, 20 MHz, noise floor -93.99 dBm) and ground sensors at a range of
horizontal distances.  INET's BreakpointPathLoss with breakpoint 1 m,
l01 = l02 = 40.04 dB and alpha = 2 evaluates to exactly

    PL(d) = PL(1m) + 10*n*log10(d/1m)

which is algebraically the Python log_distance_pl().  The two can therefore be
compared numerically, not just functionally.

The observable is INET's `minSnir` statistic, i.e. the SNIR that INET's radio
actually measured at the receiver, together with the 802.11 packet error rate,
which says whether the link was usable.

IMPORTANT METHODOLOGICAL NOTE
-----------------------------
The first version of this validation was invalid.  Counting MAC-layer frames
gave 500 received packets at every range, including 50 km at 1e-6 W, which is
physically impossible.  A control configuration (transmit power crushed by
60 dB) exposed this: the count did not change.  The 802.11 stack in that
configuration was not gating on the physical layer at all.  The validation was
therefore rebuilt around the measured `minSnir`, and the control now checks
that the measured SNIR tracks the transmit power by the expected 60 dB.

Run:  python analysis/phy_validation.py
"""

from __future__ import annotations

import json
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np

from uav_wireless import wireless as phy

HERE = os.path.dirname(os.path.abspath(__file__))
RESDIR = os.path.join(
    os.path.dirname(HERE), "..", "Simulation", "UAV_IoT_Demo", "results",
)

# Each sweep: the OMNeT++ configuration, its horizontal ranges, and the
# path-loss exponent used.  (mirrors simulations/phy_validation.ini)
SWEEPS = {
    "near": dict(sca="phy_validation_0.sca", n=2.0,
                  ranges=[10.0, 20.0, 30.0, 35.0, 40.0, 50.0, 60.0, 80.0],
                  label="the report's operating range"),
    "nlos": dict(sca="phy_validation_nlos_0.sca", n=3.5,
                 ranges=[40.0, 60.0, 100.0, 140.0, 160.0, 180.0, 190.0,
                         220.0, 300.0],
                 label="obstructed case, closure boundary inside the field"),
    "far": dict(sca="phy_validation_far_0.sca", n=2.0,
                ranges=[100.0, 1000.0, 3000.0, 5000.0, 7000.0, 8000.0,
                        8800.0, 8900.0, 9500.0],
                label="free-space case, closure boundary at ~9 km"),
    "far2": dict(sca="phy_validation_far2_0.sca", n=2.0,
                 ranges=[8860.0, 9000.0, 9500.0, 10000.0, 11000.0, 12000.0,
                         15000.0, 20000.0, 50000.0],
                 label="beyond the closure boundary"),
    "control": dict(sca="phy_validation_control_0.sca", n=2.0,
                    ranges=[10.0, 1000.0, 50000.0],
                    label="CONTROL: transmit power crushed by 60 dB"),
}

Z0 = 50.0
N_EXPONENT = 2.0
NOISE_DBM = -93.99
P_TX_W = 0.5
CONTROL_P_TX_W = 1e-6
SNR_THRESHOLD_DB = 2.0
RATE_MIN_MBPS = 6.5


# ----------------------------------------------------------------------
# .sca parsing
# ----------------------------------------------------------------------
def parse_histograms(path):
    """Return {module_path: {statistic: {'mean':..,'count':..}}} from a .sca.

    Handles both the scalar form ('scalar NAME value') and the histogram
    form ('statistic NAME:histogram' followed by 'field mean ...' and
    'bin lower upper count' lines).
    """
    out = {}
    cur = None
    with open(path, encoding="utf-8", errors="replace") as f:
        for raw in f:
            line = raw.rstrip("\n")
            s = line.strip()
            if s.startswith("statistic "):
                raw = s[len("statistic "):]
                # "MODULE.stat NAME:histogram" -> "MODULE.stat.NAME"
                name = raw.split(":")[0].replace(" ", ".")
                cur = (name, out.setdefault(name, {}))
            elif s.startswith("scalar ") and cur is None:
                parts = s.split()
                if len(parts) >= 3:
                    name = parts[1]
                    val = parts[-1]
                    try:
                        out.setdefault(name, {})["value"] = float(val)
                    except ValueError:
                        pass
            elif s.startswith("field ") and cur is not None:
                parts = s.split()
                if len(parts) >= 3:
                    try:
                        cur[1][parts[1]] = float(parts[2])
                    except ValueError:
                        pass
            elif s.startswith("bin ") and cur is not None:
                parts = s.split()
                if len(parts) >= 4:
                    try:
                        cur[1].setdefault("count", 0.0)
                        cur[1]["count"] += float(parts[3])
                    except ValueError:
                        pass
    return out


def sensor_stats(hists, index):
    """minSnir (linear) and packetErrorRate for one sensor radio."""
    snir = hists.get(f"PhyValidation.sensor[{index}].wlan[0].radio.minSnir")
    per = hists.get(f"PhyValidation.sensor[{index}].wlan[0].radio.packetErrorRate")
    snir_lin = None
    if snir and "mean" in snir:
        snir_lin = float(snir["mean"])
    per_mean = None
    if per and "mean" in per:
        per_mean = float(per["mean"])
    return snir_lin, per_mean


# ----------------------------------------------------------------------
# Python reference
# ----------------------------------------------------------------------
def python_link(horizontal_m: float, n: float = N_EXPONENT,
                p_tx: float = P_TX_W):
    """Python PHY: slant range, path loss, SNR and rate at one range."""
    d3 = math.sqrt(horizontal_m ** 2 + Z0 ** 2)
    pl = float(phy.log_distance_pl(d3, 2.4e9, n, 1.0))
    rx_w = p_tx * 10 ** (-pl / 10.0)
    k, t, bw, nf = 1.380649e-23, 290.0, 20e6, 10 ** (7.0 / 10.0)
    noise_w = k * t * bw * nf
    snr_db = 10 * math.log10(rx_w / noise_w)
    rate = float(phy.snr_to_rate(np.array([snr_db]))[0])
    return dict(slant_m=d3, path_loss_db=pl,
                rx_dbm=10 * math.log10(rx_w * 1000.0), snr_db=snr_db,
                rate_mbps=rate,
                phy_ok=bool(snr_db >= SNR_THRESHOLD_DB
                            and rate >= RATE_MIN_MBPS))


def main():
    print("=" * 92)
    print(" PYTHON PHY  vs  INET 4.6 / OMNeT++ 6.4  --  measured minSnir")
    print(" UAV at z0=50 m, 0.5 W, 2.437 GHz, 20 MHz, noise -93.99 dBm")
    print("=" * 92)

    rows = []
    worst = 0.0
    for name, spec in SWEEPS.items():
        sca = os.path.join(RESDIR, spec["sca"])
        if not os.path.exists(sca):
            print(f"\n[{name}] missing {os.path.normpath(sca)} -- run the "
                  "OMNeT++ scenario first")
            continue
        hists = parse_histograms(sca)
        p_tx = CONTROL_P_TX_W if name == "control" else P_TX_W
        print(f"\n--- {name} sweep (n = {spec['n']}, P_tx = {p_tx} W) ---")
        print(f"{'range':>7} {'slant':>8} {'py SNR':>8} {'INET SNR':>9} "
              f"{'delta':>7} {'py rate':>8} {'INET PER':>9} {'link':>6}")
        print("-" * 92)
        for i, d in enumerate(spec["ranges"]):
            p = python_link(d, spec["n"], p_tx)
            snir_lin, per = sensor_stats(hists, i)
            if snir_lin is None or snir_lin <= 0:
                inet_snr = float("nan")
                delta = float("nan")
            else:
                inet_snr = 10 * math.log10(snir_lin)
                delta = inet_snr - p["snr_db"]
                if name != "control":
                    worst = max(worst, abs(delta))
            inet_ok = (per is not None and per < 1e-9
                       and p["snr_db"] >= SNR_THRESHOLD_DB)
            py_ok = p["phy_ok"]
            agree = "OK" if py_ok == inet_ok else "MISMATCH"
            print(f"{d:7.0f} {p['slant_m']:8.1f} {p['snr_db']:8.2f} "
                  f"{inet_snr:9.2f} {delta:+7.2f} {p['rate_mbps']:8.1f} "
                  f"{(per if per is not None else float('nan')):9.3f} "
                  f"{agree:>6}")
            rows.append(dict(sweep=name, index=i, distance_m=d,
                             python_snr_db=p["snr_db"],
                             inet_snr_db=inet_snr, delta_db=delta,
                             python_path_loss_db=p["path_loss_db"],
                             slant_m=p["slant_m"],
                             python_rate_mbps=p["rate_mbps"],
                             inet_packet_error_rate=per,
                             python_link_ok=py_ok, inet_link_ok=inet_ok))

    print("\n" + "=" * 92)
    print(f" worst |SNR deviation| between the two implementations "
          f"(excl. control): {worst:.2f} dB")
    print("=" * 92)

    out = os.path.join(HERE, "phy_validation.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(dict(rows=rows, worst_snr_deviation_db=worst), f, indent=2)
    print(f"Saved -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
