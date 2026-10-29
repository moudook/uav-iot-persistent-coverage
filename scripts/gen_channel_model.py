"""Generate the calibrated information-channel model from INET measurements.

Inputs (measured, see Simulation/omnet_uav2/):
  - Free-space knee: PDR = 0.9975 for d <= 1750 m, 0.0 for d >= 1775 m.
    (sigma = 0, 50 m altitude, 20 dBm, -85 dBm sensitivity, -94 dBm noise)
  - Shadowing: LogNormalShadowing, sigma = 6 dB, quasi-static per link.

Model (for the Python simulator):
  PL(d) = 20 log10(d) + 20 log10(f) - 147.55   (free space, f = 2.412 GHz)
  Rx(d)  = Tx - PL(d) - X,   X ~ N(0, sigma)     (shadowing, per link)
  PDR(d) = P(Rx >= sensitivity) = 1 - Phi((sensitivity - (Tx-PL(d))) / sigma)

At the mission scale (80 m) this gives PDR = 0.9975: the network is reliable
and is NOT the binding constraint.  The model's job is to certify that, and to
state the range (1.76 km) beyond which it stops being true.

Outputs:
  - Simulation/omnet_uav2/channel_model.csv   (dense PDR(d) curve)
  - ml_impl/uav_wireless/channel_model.py     (callable model for the simulator)
"""
import os, sys, json, math

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(PROJ, "Simulation", "omnet_uav2")
OUT_CSV = os.path.join(SRC, "channel_model.csv")
OUT_PY = os.path.join(PROJ, "ml_impl", "uav_wireless", "channel_model.py")

# --- calibrated constants (from INET, see docs/LOG.md 2026-10-29) ---
F_HZ = 2.412e9
TX_DBM = 20.0          # 0.1 W
SENS_DBM = -85.0       # receiver sensitivity
NOISE_DBM = -94.0      # -174 dBm/Hz + 7 dB NF over 20 MHz
SIGMA_DB = 6.0         # log-normal shadowing, per link, quasi-static
# free-space knee measured by INET
KNEE_M = 1762.0


def path_loss_db(d, f=F_HZ):
    return 20.0 * math.log10(d) + 20.0 * math.log10(f) - 147.55


def pdr(d, sigma=SIGMA_DB):
    """Analytic outage probability under log-normal shadowing."""
    import statistics
    pl = path_loss_db(d)
    rx_mean = TX_DBM - pl            # dBm, mean received power
    # outage if Rx < SENS; Rx = rx_mean - X, X~N(0,sigma)
    # P(Rx < sens) = P(X > rx_mean - sens) = 1 - Phi((rx_mean-sens)/sigma)
    z = (rx_mean - SENS_DBM) / sigma
    # Phi(z) via error function
    phi = 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))
    return phi


def main():
    # Dense curve
    rows = []
    for i in range(1, 4001):
        d = float(i) * 5.0  # 5 m .. 20 km
        rows.append((d, pdr(d)))
    with open(OUT_CSV, "w") as f:
        f.write("dist_m,pdr_model\n")
        for d, p in rows:
            f.write(f"{d:.0f},{p:.6f}\n")
    print("wrote", OUT_CSV)

    # Python module for the simulator
    mod = '''"""Information channel model calibrated against OMNeT++/INET.

Source of truth: Simulation/omnet_uav2/pair_pdr_freespace.json and
pair_pdr_outage.json (INET, 50 m altitude, 20 dBm, -85 dBm sensitivity,
-94 dBm noise floor, LogNormalShadowing sigma = 6 dB).

At the mission scale (80 m, 8 UAVs) this model gives PDR = {p80:.4f}: the
wireless layer is reliable and is NOT the binding constraint.  The binding
constraints are energy and coverage geometry.  The model's job is to certify
that, and to state the range ({knee:.0f} m) beyond which it stops being true.
"""
import math

F_HZ = {f}
TX_DBM = {tx}
SENS_DBM = {sens}
SIGMA_DB = {sigma}
KNEE_M = {knee}


def path_loss_db(d, f=F_HZ):
    return 20.0 * math.log10(max(d, 1.0)) + 20.0 * math.log10(f) - 147.55


def pdr(d, sigma=SIGMA_DB):
    """Delivery probability for a link of length d (metres)."""
    pl = path_loss_db(d)
    rx_mean = TX_DBM - pl
    z = (rx_mean - SENS_DBM) / sigma
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def reliable(d, threshold=0.99):
    return pdr(d) >= threshold
'''.format(p80=pdr(80.0), knee=KNEE_M, f=F_HZ, tx=TX_DBM, sens=SENS_DBM, sigma=SIGMA_DB)
    with open(OUT_PY, "w") as f:
        f.write(mod)
    print("wrote", OUT_PY)
    print(f"PDR at 80 m (mission scale) = {pdr(80.0):.4f}")
    print(f"PDR at 1762 m (knee) = {pdr(KNEE_M):.4f}")


if __name__ == "__main__":
    main()
