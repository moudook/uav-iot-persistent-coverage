"""Step B1: pure link calibration PDR(d), N=2, at the simulator's 50 m altitude.

Nodes are placed with StationaryMobility at explicit coordinates, so the
geometry is exact and there is no trace-file parsing in the loop.
Only PHY + MAC are exercised (one bidirectional link, no contention).

Output: Simulation/omnet_uav/stepB_pair.json
"""
import os, sys, json, subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stepB_channel import SCN_UNC, INI, run_inet, parse_sca, PROJ

INI_TMPL = """[General]
network = UavNetwork
sim-time-limit = {simtime}s

*.numUavs = 2
*.numSensors = 0

**.constraintAreaMinX = -100m
**.constraintAreaMinY = -100m
**.constraintAreaMinZ = 0m
**.constraintAreaMaxX = {amax}m
**.constraintAreaMaxY = 200m
**.constraintAreaMaxZ = 100m

**.uav[*].mobility.typename = "StationaryMobility"
**.uav[*].mobility.initFromDisplayString = false
**.uav[0].mobility.initialX = 0m
**.uav[0].mobility.initialY = 100m
**.uav[0].mobility.initialZ = 50m
**.uav[1].mobility.initialX = {d}m
**.uav[1].mobility.initialY = 100m
**.uav[1].mobility.initialZ = 50m

**.wlan[*].bitrate = {bitrate}
**.wlan[*].mac.dcf.channelAccess.cwMin = 7
**.wlan[*].radio.transmitter.power = {power}W
**.wlan[*].radio.receiver.sensitivity = {sens}dBm
**.wlan[*].radio.receiver.snirThreshold = {snir}dB

*.configurator.config = xml("<config><interface hosts='**' address='10.0.0.x' netmask='255.255.255.0'/></config>")

*.uav[0].numApps = 1
*.uav[0].app[0].typename = "UdpBasicApp"
*.uav[0].app[0].destAddresses = "uav[1]"
*.uav[0].app[0].destPort = 1000
*.uav[0].app[0].messageLength = 64B
*.uav[0].app[0].sendInterval = {interval}s
*.uav[0].app[0].startTime = 0s
*.uav[0].app[0].localPort = 1000

*.uav[1].numApps = 1
*.uav[1].app[0].typename = "UdpBasicApp"
*.uav[1].app[0].destAddresses = "uav[0]"
*.uav[1].app[0].destPort = 1000
*.uav[1].app[0].messageLength = 64B
*.uav[1].app[0].sendInterval = {interval}s
*.uav[1].app[0].startTime = {start1}s
*.uav[1].app[0].localPort = 1000

**.scalar-recording = true
**.vector-recording = false
"""


def run_point(d, power, sens, snir, bitrate, interval, simtime):
    amax = max(200.0, d + 100.0)
    with open(INI, "w", newline="\n") as f:
        f.write(INI_TMPL.format(d=d, amax=amax, power=power, sens=sens, snir=snir,
                                bitrate=bitrate, interval=interval, simtime=simtime,
                                start1=interval / 2.0))
    out = run_inet()
    ok = "Simulation time limit reached" in out
    if not ok:
        last = next((l for l in out.strip().splitlines()[::-1] if l.strip()), "?")
        return None, last[:160]
    sc = parse_sca(2)
    if not sc:
        return None, "no sca"
    sent, recv = sc
    s0, r0, s1, r1 = sent[0], recv[0], sent[1], recv[1]
    p01 = (r1 / s0) if s0 else None
    p10 = (r0 / s1) if s1 else None
    vals = [p for p in (p01, p10) if p is not None]
    mean = sum(vals) / len(vals) if vals else None
    return {"pdr": mean, "p01": p01, "p10": p10, "sent": s0, "recv": r1}, None


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--distances", nargs="+", type=float,
                    default=[5, 10, 20, 30, 40, 60, 80, 100, 150, 200, 300, 450, 650, 900])
    ap.add_argument("--power", default="0.1")
    ap.add_argument("--sens", default="-85")
    ap.add_argument("--snir", default="4")
    ap.add_argument("--bitrate", default="6Mbps")
    ap.add_argument("--interval", type=float, default=0.1)
    ap.add_argument("--simtime", type=float, default=30.0)
    ap.add_argument("--tag", default="")
    args = ap.parse_args()

    tag = args.tag or f"p{args.power}_s{args.sens}"
    out_path = os.path.join(PROJ, "Simulation", "omnet_uav", f"stepB_pair{tag}.json")
    rows = []
    for d in args.distances:
        res, err = run_point(d, args.power, args.sens, args.snir, args.bitrate,
                             args.interval, args.simtime)
        if res is None:
            print(f"  d={d:6.0f} m: FAIL ({err})", flush=True)
            rows.append({"dist": d, "ok": False, "err": err})
            continue
        p = res["pdr"]
        print(f"  d={d:6.0f} m: PDR={p:.4f}  (0->1 {res['p01']:.3f}, 1->0 {res['p10']:.3f}, "
              f"sent={res['sent']:.0f})", flush=True)
        rows.append({"dist": d, "ok": True, **res})
    with open(out_path, "w") as f:
        json.dump(rows, f, indent=1)
    print("saved", out_path)


if __name__ == "__main__":
    main()
