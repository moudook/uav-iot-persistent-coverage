#!/bin/bash
# OMNeT++/INET radio-chain probe.
#
# A transmit-power sweep of the PhyValidation scenario with sensors at
# 10, 30, 50 and 80 m.  The ONLY difference between the configurations is
# the UAV's transmit power, over a 117 dB range.  For each configuration the
# per-receiver `minSnir` statistic and the reception count are read from the
# .sca scalar file.
#
# The transmit power is written into the NED file rather than the ini: the
# ini path for that parameter was found not to reach the radio, and the
# NED assignment is applied before the ini.
#
# The results are copied to results/NedTx<TAG>.sca for
# analysis/phy_runtime_probe.py to parse.
#
# Run on WSL:  bash run_phy_probe.sh
set -u
W=~/omnetpp-workspace
export PATH="/usr/local/bin:/usr/bin:/bin:$HOME/.local/bin:$PATH"
D=/mnt/c/Users/gbust/Downloads/Academic/Courses/Machine_learning_in_wireless_network/Project1/Simulation/UAV_IoT_Demo

cd "$W" || exit 1

python3 - "$W" "$D" <<'PY'
import os, subprocess, shutil, sys

W, D = sys.argv[1], sys.argv[2]
base_ned = open(os.path.join(W, "sim", "PhyValidation.ned")).read()
base_ini = open(os.path.join(D, "simulations", "snr_sweep.ini")).read()

# The ini must not set the transmitter power (that path is unreliable) and
# must point at the low-power network.
ini = "\n".join(line for line in base_ini.splitlines()
                if not line.startswith("*.uav.wlan[0].radio.transmitter.power"))
ini = ini.replace("network = sim.PhyValidation",
                  "network = sim.PhyValidationLowPower")
open(os.path.join(W, "ned_sweep.ini"), "w").write(ini)

for tag, power in [("0.5W", "0.5W"), ("1mW", "0.001W"),
                   ("1uW", "0.000001W"), ("1pW", "0.000000000001W")]:
    ned = base_ned.replace("network PhyValidation\n",
                            "network PhyValidationLowPower\n")
    ned = ned.replace("wlan[0].radio.transmitter.power = 0.5W;",
                       f"wlan[0].radio.transmitter.power = {power};")
    open(os.path.join(W, "sim", "PhyValidationLowPower.ned"), "w").write(ned)
    r = subprocess.run(
        ["opp_env", "run", "simu5g-1.4.3", "-c",
         "opp_run -u Cmdenv -c Tx1pW -f ned_sweep.ini"],
        cwd=W, capture_output=True, text=True)
    ok = r.returncode == 0
    print(f"{tag:>6s}  {'ok' if ok else 'FAILED'}")
    if not ok:
        print((r.stdout or r.stderr or "")[-600:])
    src = os.path.join(W, "results", "Tx1pW", "0.sca")
    if ok and os.path.exists(src):
        shutil.copy(src, os.path.join(W, "results", f"NedTx{tag}.sca"))
PY

echo
echo "=== done; now parse the results ==="
python3 /mnt/c/Users/gbust/Downloads/Academic/Courses/Machine_learning_in_wireless_network/Project1/ml_impl/analysis/phy_runtime_probe.py
