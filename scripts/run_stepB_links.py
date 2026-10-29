"""Step B v1: per-link PDR from INET pcap.

For each trace:
  - copy trace to WSL scenario dir
  - set ini traceFile
  - enable pcap recording (fcsMode=computed)
  - run INET 40s
  - parse pcap -> (t, src, dst) per UDP packet
  - compute per-pair PDR and distance from trace
Output: Simulation/omnet_uav/stepB_links.json
"""
import os, sys, subprocess, json, struct, re, shutil, time

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WSL = "/home/gbust/omnetpp_ws"
INET = WSL + "/inet-4.6.0"
SCN = INET + "/examples/uav_omnet"
UNC = r"\\wsl.localhost\Ubuntu" + WSL.replace("/", "\\")
SCN_UNC = UNC + r"\inet-4.6.0\examples\uav_omnet"
LOCAL_TRACES = os.path.join(PROJ, "Simulation", "omnet_uav", "traces")

INI = os.path.join(SCN_UNC, "omnetpp.ini")

BASE_INI = """[General]
network = UavNetwork
sim-time-limit = 40s

*.numUavs = 8
*.numSensors = 20

**.constraintAreaMinX = 0m
**.constraintAreaMinY = 0m
**.constraintAreaMinZ = 0m
**.constraintAreaMaxX = 80m
**.constraintAreaMaxY = 80m
**.constraintAreaMaxZ = 0m

**.uav[*].mobility.typename = "BonnMotionMobility"
**.uav[*].mobility.traceFile = "traces/{trace}"
**.uav[*].mobility.nodeId = -1

**.sensor[*].mobility.typename = "StationaryMobility"
**.sensor[*].mobility.initFromDisplayString = false
**.sensor[*].mobility.initialX = uniform(0m, 80m)
**.sensor[*].mobility.initialY = uniform(0m, 80m)
**.sink.mobility.typename = "StationaryMobility"
**.sink.mobility.initFromDisplayString = false
**.sink.mobility.initialX = 40m
**.sink.mobility.initialY = 40m

**.wlan[*].bitrate = 6Mbps
**.wlan[*].mac.dcf.channelAccess.cwMin = 7
**.wlan[*].radio.transmitter.power = {power}W
**.wlan[*].radio.receiver.sensitivity = -85dBm
**.wlan[*].radio.receiver.snirThreshold = 4dB
**.wlan[*].mac.fcsMode = "computed"
**.crcMode = "computed"
**.checksumMode = "computed"

*.configurator.config = xml("<config><interface hosts='**' address='10.0.0.x' netmask='255.255.255.0'/></config>")

*.uav[*].numApps = 1
*.uav[*].app[0].typename = "UdpBasicApp"
*.uav[*].app[0].destAddresses = "uav[0] uav[1] uav[2] uav[3] uav[4] uav[5] uav[6] uav[7]"
*.uav[*].app[0].destPort = 1000
*.uav[*].app[0].messageLength = 64B
*.uav[*].app[0].sendInterval = {interval}s
*.uav[*].app[0].startTime = uniform(0s, 1s)
*.uav[*].app[0].localPort = 1000

**.scalar-recording = true
**.vector-recording = false
**.recordPcap = true
"""


def write_ini(trace, power=0.5, interval=1.0):
    with open(INI, "w") as f:
        f.write(BASE_INI.format(trace=trace, power=power, interval=interval))


def copy_trace(name):
    src = os.path.join(LOCAL_TRACES, name)
    dst = os.path.join(SCN_UNC, "traces", name)
    shutil.copyfile(src, dst)


RUN_SH = r"""#!/bin/bash
set -e
cd /home/gbust/omnetpp_ws
opp_env run inet-4.6.0 -c 'cd /home/gbust/omnetpp_ws/inet-4.6.0/examples/uav_omnet && rm -rf results/*.pcap && opp_run -u Cmdenv -l /home/gbust/omnetpp_ws/inet-4.6.0/out/clang-release/src/libINET.so -n /home/gbust/omnetpp_ws/inet-4.6.0/src:/home/gbust/omnetpp_ws/inet-4.6.0/examples' 2>&1 | tail -4
"""


def run_inet():
    sh = os.path.join(SCN_UNC, "run_opp.sh")
    with open(sh, "w", newline="\n") as f:
        f.write(RUN_SH)
    subprocess.run(["wsl", "-d", "Ubuntu", "--", "bash", "-c", "sed -i 's/\\r$//' /home/gbust/omnetpp_ws/inet-4.6.0/examples/uav_omnet/run_opp.sh && chmod +x /home/gbust/omnetpp_ws/inet-4.6.0/examples/uav_omnet/run_opp.sh"], check=False)
    r = subprocess.run(["wsl", "-d", "Ubuntu", "--", "bash", "/home/gbust/omnetpp_ws/inet-4.6.0/examples/uav_omnet/run_opp.sh"],
                       capture_output=True, text=True, timeout=300)
    return r.stdout + r.stderr


def parse_pcap(path):
    """Return list of (t, src_ip, dst_ip, udp_len) for IPv4 UDP packets."""
    out = []
    with open(path, "rb") as f:
        data = f.read()
    magic = data[:4]
    if magic == b"\xd4\xc3\xb2\xa1":
        endian = "<"; nano = False
    elif magic == b"\xa1\xb2\xc3\xd4":
        endian = ">"; nano = False
    elif magic == b"\x4d\x3c\xb2\xa1":
        endian = "<"; nano = True
    elif magic == b"\xa1\xb2\x3c\x4d":
        endian = ">"; nano = True
    else:
        raise ValueError("unknown pcap magic %r" % magic)
    linktype = struct.unpack(endian + "I", data[20:24])[0]
    off = 24
    n = len(data)
    while off + 16 <= n:
        ts_sec, ts_frac, incl, orig = struct.unpack(endian + "IIII", data[off:off+16])
        off += 16
        pkt = data[off:off+incl]
        off += incl
        t = ts_sec + ts_frac / (1e9 if nano else 1e6)
        # link layer
        if linktype == 1:  # ethernet
            if len(pkt) < 14:
                continue
            eth_type = struct.unpack(">H", pkt[12:14])[0]
            if eth_type == 0x0800:
                ip = pkt[14:]
            elif eth_type == 0x8100 and len(pkt) >= 18:
                eth_type = struct.unpack(">H", pkt[16:18])[0]
                ip = pkt[18:]
            else:
                continue
        elif linktype == 105 or linktype == 127:  # 802.11
            continue
        else:
            continue
        if len(ip) < 20:
            continue
        vihl = ip[0]
        if (vihl >> 4) != 4:
            continue
        ihl = (vihl & 0x0F) * 4
        if len(ip) < ihl + 8:
            continue
        proto = ip[9]
        if proto != 17:  # UDP
            continue
        src = ".".join(str(b) for b in ip[12:16])
        dst = ".".join(str(b) for b in ip[16:20])
        out.append((t, src, dst))
    return out, linktype


def read_trace_positions(path):
    """BonnMotion .movements: each line = node's trajectory: t x y t x y ..."""
    nodes = []
    with open(path) as f:
        for line in f:
            vals = [float(x) for x in line.split()]
            pts = [(vals[i], vals[i+1], vals[i+2]) for i in range(0, len(vals), 3)]
            nodes.append(pts)
    return nodes


def pos_at(pts, t):
    if not pts:
        return None
    if t <= pts[0][0]:
        return pts[0][1], pts[0][2]
    for i in range(1, len(pts)):
        if pts[i][0] >= t:
            t0, x0, y0 = pts[i-1]
            t1, x1, y1 = pts[i]
            if t1 == t0:
                return x1, y1
            a = (t - t0) / (t1 - t0)
            return x0 + a * (x1 - x0), y0 + a * (y1 - y0)
    return pts[-1][1], pts[-1][2]


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--traces", nargs="+", default=None)
    ap.add_argument("--power", type=float, default=0.5)
    ap.add_argument("--interval", type=float, default=1.0)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    traces = args.traces
    if not traces:
        traces = sorted(n for n in os.listdir(LOCAL_TRACES) if n.endswith(".movements"))
    if args.limit:
        traces = traces[:args.limit]

    results = []
    for name in traces:
        print(f"[{name}]", flush=True)
        copy_trace(name)
        write_ini(name, power=args.power, interval=args.interval)
        out = run_inet()
        ok = "Simulation time limit reached" in out
        if not ok:
            print("  RUN FAIL:", out.strip().splitlines()[-1] if out.strip() else "?")
            results.append({"trace": name, "ok": False, "raw": out[-500:]})
            continue
        pcaps = [p for p in os.listdir(os.path.join(SCN_UNC, "results")) if p.endswith(".pcap")]
        if not pcaps:
            print("  NO PCAP")
            results.append({"trace": name, "ok": False, "reason": "no pcap"})
            continue
        # choose the pcap corresponding to uav interfaces; parse all and merge
        allsamp = []
        linktypes = set()
        for p in pcaps:
            m = re.search(r"uav\[(\d+)\]", p)
            if not m:
                continue
            uid = int(m.group(1))
            try:
                samp, lt = parse_pcap(os.path.join(SCN_UNC, "results", p))
            except Exception as e:
                print("  pcap parse err", p, e)
                continue
            linktypes.add(lt)
            for (t, src, dst) in samp:
                allsamp.append({"t": t, "src": src, "dst": dst, "iface": uid})
        print(f"  packets={len(allsamp)} linktypes={linktypes} pcaps={len(pcaps)}")
        results.append({"trace": name, "ok": True, "samples": allsamp, "linktypes": list(linktypes)})

    out_path = os.path.join(PROJ, "Simulation", "omnet_uav", "stepB_links.json")
    with open(out_path, "w") as f:
        json.dump(results, f)
    print("saved", out_path)


if __name__ == "__main__":
    main()
