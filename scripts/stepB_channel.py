"""Step B: INET information-channel calibration.

Design (no pcap needed):
  - Traffic is a RING: uav[i] -> uav[(i+1) mod N] only.
    Therefore received-count at uav[j] is exactly the delivery count of link (j-1 -> j).
  - Geometry is CONTROLLED: stationary nodes at known positions, so each link
    has a well-defined distance.
  - Sweep N (load) and beacon interval (traffic intensity).

Output: Simulation/omnet_uav/stepB_channel.json
  list of {N, interval, layout, links:[{src,dst,dist,sent,recv,pdr}]}
"""
import os, sys, subprocess, json, re, shutil, argparse, math

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WSL = "/home/gbust/omnetpp_ws"
INET = WSL + "/inet-4.6.0"
SCN = INET + "/examples/uav_omnet"
UNC = r"\\wsl.localhost\Ubuntu" + WSL.replace("/", "\\")
SCN_UNC = UNC + r"\inet-4.6.0\examples\uav_omnet"
INI = os.path.join(SCN_UNC, "omnetpp.ini")
RESULTS_UNC = os.path.join(SCN_UNC, "results")

AREA = 80.0

INI_TMPL = """[General]
network = UavNetwork
sim-time-limit = {simtime}s

*.numUavs = {N}
*.numSensors = 0

**.constraintAreaMinX = 0m
**.constraintAreaMinY = 0m
**.constraintAreaMinZ = 0m
**.constraintAreaMaxX = 80m
**.constraintAreaMaxY = 80m
**.constraintAreaMaxZ = 0m

**.uav[*].mobility.typename = "BonnMotionMobility"
**.uav[*].mobility.traceFile = "traces/{trace}"
**.uav[*].mobility.nodeId = -1

**.wlan[*].bitrate = 6Mbps
**.wlan[*].mac.dcf.channelAccess.cwMin = 7
**.wlan[*].radio.transmitter.power = 0.5W
**.wlan[*].radio.receiver.sensitivity = -85dBm
**.wlan[*].radio.receiver.snirThreshold = 4dB

*.configurator.config = xml("<config><interface hosts='**' address='10.0.0.x' netmask='255.255.255.0'/></config>")

*.uav[*].numApps = 1
*.uav[*].app[0].typename = "UdpBasicApp"
{ring_lines}
*.uav[*].app[0].destPort = 1000
*.uav[*].app[0].messageLength = 64B
*.uav[*].app[0].sendInterval = {interval}s
*.uav[*].app[0].startTime = uniform(0s, 1s)
*.uav[*].app[0].localPort = 1000

**.scalar-recording = true
**.vector-recording = false
"""

RUN_SH = """#!/bin/bash
cd /home/gbust/omnetpp_ws
opp_env run inet-4.6.0 -c 'cd /home/gbust/omnetpp_ws/inet-4.6.0/examples/uav_omnet && rm -f results/General-*.sca results/General-*.vec results/General-*.vci && opp_run -u Cmdenv -l /home/gbust/omnetpp_ws/inet-4.6.0/out/clang-release/src/libINET.so -n /home/gbust/omnetpp_ws/inet-4.6.0/src:/home/gbust/omnetpp_ws/inet-4.6.0/examples' 2>&1 | tail -20
"""


def make_layout(seed, N):
    """Random stationary positions, min separation enforced a bit."""
    rng = __import__("random").Random(seed)
    pts = []
    tries = 0
    while len(pts) < N and tries < 5000:
        tries += 1
        x = rng.uniform(0, AREA)
        y = rng.uniform(0, AREA)
        if all((x - px) ** 2 + (y - py) ** 2 > 36 for px, py in pts):
            pts.append((x, y))
    while len(pts) < N:
        pts.append((rng.uniform(0, AREA), rng.uniform(0, AREA)))
    return pts


def write_trace(name, pts, duration):
    """BonnMotion: one line per node:  t0 x0 y0 t1 x1 y1 (stationary)."""
    path = os.path.join(SCN_UNC, "traces", name)
    with open(path, "w", newline="\n") as f:
        for (x, y) in pts:
            f.write(f"0.00 {x:.3f} {y:.3f} {duration:.2f} {x:.3f} {y:.3f}\n")
    return path


def write_ini(N, trace, interval, simtime):
    ring = "\n".join(
        f'*.uav[{i}].app[0].destAddresses = "uav[{(i + 1) % N}]"' for i in range(N)
    )
    with open(INI, "w", newline="\n") as f:
        f.write(INI_TMPL.format(N=N, trace=trace, interval=interval, simtime=simtime, ring_lines=ring))


def run_inet():
    sh = os.path.join(SCN_UNC, "run_opp.sh")
    with open(sh, "w", newline="\n") as f:
        f.write(RUN_SH)
    subprocess.run(["wsl", "-d", "Ubuntu", "--", "bash", "-c",
                    "sed -i 's/\\r$//' /home/gbust/omnetpp_ws/inet-4.6.0/examples/uav_omnet/run_opp.sh"],
                   capture_output=True)
    r = subprocess.run(["wsl", "-d", "Ubuntu", "--", "bash",
                        "/home/gbust/omnetpp_ws/inet-4.6.0/examples/uav_omnet/run_opp.sh"],
                       capture_output=True, text=True, timeout=600)
    return r.stdout + r.stderr


def parse_sca(N):
    path = os.path.join(RESULTS_UNC, "General-#0.sca")
    if not os.path.exists(path):
        return None
    sent = [None] * N
    recv = [None] * N
    pat = re.compile(r'^scalar\s+UavNetwork\.uav\[(\d+)\]\.app\[0\]\s+"([^"]+)"\s+(\S+)')
    with open(path, errors="replace") as f:
        for line in f:
            m = pat.match(line.strip())
            if not m:
                continue
            i, name, val = int(m.group(1)), m.group(2), m.group(3)
            try:
                v = float(val)
            except ValueError:
                continue
            if name == "packets sent":
                sent[i] = v
            elif name == "packets received":
                recv[i] = v
    return sent, recv


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--layouts", type=int, default=8)
    ap.add_argument("--n-list", nargs="+", type=int, default=[4, 8])
    ap.add_argument("--interval-list", nargs="+", type=float, default=[0.5, 1.0])
    ap.add_argument("--simtime", type=float, default=40.0)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    out_path = args.out or os.path.join(PROJ, "Simulation", "omnet_uav", "stepB_channel.json")
    results = []
    for N in args.n_list:
        for interval in args.interval_list:
            for layout in range(args.layouts):
                seed = 1000 * N + 17 * layout + int(interval * 10)
                pts = make_layout(seed, N)
                tname = f"stepB_n{N}_l{layout}.movements"
                write_trace(tname, pts, args.simtime)
                write_ini(N, tname, interval, args.simtime)
                out = run_inet()
                ok = "Simulation time limit reached" in out
                tag = f"N={N} int={interval} layout={layout}"
                if not ok:
                    last = next((l for l in out.strip().splitlines()[::-1] if l.strip()), "?")
                    print(f"  {tag}: FAIL ({last[:120]})", flush=True)
                    results.append({"N": N, "interval": interval, "layout": layout, "ok": False})
                    continue
                sc = parse_sca(N)
                if not sc:
                    print(f"  {tag}: no sca", flush=True)
                    results.append({"N": N, "interval": interval, "layout": layout, "ok": False})
                    continue
                sent, recv = sc
                links = []
                for i in range(N):
                    j = (i + 1) % N
                    d = math.dist(pts[i], pts[j])
                    s = sent[i] or 0
                    r_ = recv[j] or 0
                    links.append({"src": i, "dst": j, "dist": d,
                                  "sent": s, "recv": r_,
                                  "pdr": (r_ / s) if s else None})
                pdr = [l["pdr"] for l in links if l["pdr"] is not None]
                mean_pdr = sum(pdr) / len(pdr) if pdr else None
                print(f"  {tag}: mean PDR={mean_pdr:.3f}" if mean_pdr is not None else f"  {tag}: no pdr", flush=True)
                results.append({"N": N, "interval": interval, "layout": layout,
                                "ok": True, "positions": pts, "links": links,
                                "mean_pdr": mean_pdr})
    with open(out_path, "w") as f:
        json.dump(results, f, indent=1)
    print("saved", out_path)


if __name__ == "__main__":
    main()
