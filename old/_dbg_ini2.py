path = r"\\wsl.localhost\Ubuntu\home\gbust\omnetpp_ws\uavsim\test_run.ini"
content = """[General]
network = UavPair
sim-time-limit = 2.0s
repeat = 100
seed-set = ${runnumber}

*.simTrace = "traces/_dbg.movements"
*.simTxPower = 0.1W
*.simSensitivity = -85dBm
*.simSnir = 4dB
*.simInterval = 0.02s
*.simBitrate = 6Mbps
*.simSigma = 6
*.simNoise = -94dBm

**.scalar-recording = true
**.vector-recording = false
"""
open(path, "w", newline="\n").write(content)
print("written")
print([l for l in content.splitlines() if "sim-time" in l or "simInterval" in l])
