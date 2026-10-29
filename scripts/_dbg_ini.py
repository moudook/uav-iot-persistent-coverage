import sys
sys.path.insert(0, r"C:\Users\gbust\Downloads\Academic\Courses\Machine_learning_in_wireless_network\Project1\scripts")
import inet_probe as ip
ip.ensure_env()
ip.write_trace("_dbg.movements", [(0, 0, 50), (30, 0, 50)], 2.0)
params = {
    "simTrace": '"traces/_dbg.movements"',
    "simTxPower": "0.1W",
    "simSensitivity": "-85dBm",
    "simSnir": "4dB",
    "simInterval": "0.1s",
    "simBitrate": "6Mbps",
    "simSigma": "6",
    "simNoise": "-94dBm",
}
ip.write_ini("UavPair", params, 2.0, seed_set=0)
print("written")
