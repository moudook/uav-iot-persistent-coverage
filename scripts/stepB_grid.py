"""Step B: channel calibration against our own controlled INET network.

Why this script exists
----------------------
The earlier attempts wrote ini overrides such as
``**.uav[*].mobility.typename`` which do not match through a module vector.
OMNeT++ ignored them silently, so every "distance" run replayed the same
default trace and returned the same PDR.  This harness therefore:

  * uses a NED network whose geometry is a NETWORK-LEVEL parameter
    (``*.spacing``, ``*.cols``, ``*.altitude``), which single-star patterns do
    apply to, and computes the same distances in Python from the same numbers;
  * SETS one parameter to an out-of-range value in a self-test and requires the
    run to fail, so a silently-ignored override can never pass unnoticed again.

Output: Simulation/omnet_uav2/stepB_links.json
"""
import os, sys, json, math, re, subprocess, shutil, argparse

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(PROJ, "Simulation", "omnet_uav2")

WSL_ROOT = "/home/gbust/omnetpp_ws"
INET = WSL_ROOT + "/inet-4.6.0"
SCN = WSL_ROOT + "/uavsim"
UNC = r"\\wsl.localhost\Ubuntu" + SCN.replace("/", "\\")
SCN_UNC = UNC
INI = os.path.join(SCN_UNC, "omnetpp.ini")

RUN_SH = """#!/bin/bash
cd /home/gbust/omnetpp_ws
opp_env run inet-4.6.0 -c 'cd /home/gbust/omnetpp_ws/uavsim && rm -f results/General-*.sca results/General-*.vci results/General-*.vec && opp_run -u Cmdenv -l /home/gbust/omnetpp_ws/inet-4.6.0/out/clang-release/src/libINET.so -n /home/gbust/omnetpp_ws/inet-4.6.0/src:/home/gbust/omnetpp_ws/inet-4.6.0/examples:/home/gbust/omnetpp_ws/uavsim' 2>&1 | tail -25
"""

INI_TMPL = """[General]
network = uavsim.UavGrid
sim-time-limit = {simtime}s

*.numUavs = {N}
*.cols = {cols}
*.spacing = {spacing}m
*.altitude = {altitude}m
*.txPower = {power}W
*.sensitivity = {sens}dBm
*.snirThreshold = {snir}dB
*.sendInterval = {interval}s
*.bitrate = "{bitrate}"
*.ring = {ring}

**.scalar-recording = true
**.vector-recording = false
"""


def ensure_wsl_dir():
    subprocess.run(["wsl", "-d", "Ubuntu", "--", "bash", "-c",
                    "mkdir -p /home/gbust/omnetpp_ws/uavsim/results"], capture_output=True)
    for f in ("UavGrid.ned",):
        shutil.copyfile(os.path.join(SRC, f), os.path.join(SCN_UNC, f))


def write_ini(N, cols, spacing, altitude, power, sens, snir, interval, bitrate, ring, simtime):
    txt = INI_TMPL.format(N=N, cols=cols, spacing=spacing, altitude=altitude,
                          power=power, sens=sens, snir=snir, interval=interval,
                          bitrate=bitrate, ring="true" if ring else "false",
                          simtime=simtime)
    with open(INI, "w", newline="\n") as f:
        f.write(txt)


def run_inet():
    sh = os.path.join(SCN_UNC, "run.sh")
    with open(sh, "w", newline="\n") as f:
        f.write(RUN_SH)
    subprocess.run(["wsl", "-d", "Ubuntu", "--", "bash", "-c",
                    "sed -i 's/\\r$//' /home/gbust/omnetpp_ws/uavsim/run.sh && chmod +x /home/gbust/omnetpp_ws/uavsim/run.sh"],
                   capture_output=True)
    r = subprocess.run(["wsl", "-d", "Ubuntu", "--", "bash", "/home/gbust/omnetpp_ws/uavsim/run.sh"],
                       capture_output=True, text=True, timeout=900)
    return r.stdout + r.stderr


def parse_sca(N):
    path = os.path.join(SCN_UNC, "results", "General-#0.sca")
    if not os.path.exists(path):
        return None
    sent = [0.0] * N
    recv = [0.0] * N
    seen_s = [False] * N
    seen_r = [False] * N
    pat = re.compile(r'^scalar\s+UavGrid\.uav\[(\d+)\]\.app\[0\]\s+"([^"]+)"\s+(\S+)')
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
                sent[i], seen_s[i] = v, True
            elif name == "packets received":
                recv[i], seen_r[i] = v, True
    return sent, recv


def positions(N, cols, spacing, altitude):
    return [((i % cols) * spacing, (i // cols) * spacing, altitude) for i in range(N)]


def one_run(N, cols, spacing, altitude, power, sens, snir, interval, bitrate, simtime):
    """Return (sent, recv) or (None, error_string)."""
    write_ini(N, cols, spacing, altitude, power, sens, snir, interval, bitrate, True, simtime)
    out = run_inet()
    if "Simulation time limit reached" not in out:
        last = [l for l in out.strip().splitlines() if l.strip()]
        return None, last[-1] if last else "?"
    sc = parse_sca(N)
    if sc is None:
        return None, "no .sca written"
    return sc, None


def self_test(N=2, cols=2):
    """Require an invalid parameter to abort the run.

    If this returns True, single-star network parameters reach the simulator,
    so a measurement cannot be an artefact of an ignored override.
    """
    write_ini(N, cols, 10.0, 50.0, 0.1, -85, 4, 1.0, "6Mbps", True, 1.0)
    txt = open(INI).read().replace("*.sensitivity = -85dBm", "*.sensitivity = -1e9dBm")
    open(INI, "w", newline="\n").write(txt)
    out = run_inet()
    return "Simulation time limit reached" not in out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spacings", nargs="+", type=float, default=[10, 20, 30, 40, 60, 80, 120, 160, 240, 320])
    ap.add_argument("--N", type=int, default=8)
    ap.add_argument("--cols", type=int, default=3)
    ap.add_argument("--altitude", type=float, default=50.0)
    ap.add_argument("--power", type=float, default=0.1)
    ap.add_argument("--sens", type=float, default=-85)
    ap.add_argument("--snir", type=float, default=4)
    ap.add_argument("--interval", type=float, default=0.1)
    ap.add_argument("--bitrate", default="6Mbps")
    ap.add_argument("--simtime", type=float, default=20.0)
    ap.add_argument("--tag", default="")
    ap.add_argument("--skip-self-test", action="store_true")
    args = ap.parse_args()

    ensure_wsl_dir()

    if not args.skip_self_test:
        ok = self_test()
        print(f"self-test (invalid sensitivity must abort): {'PASS' if ok else 'FAIL'}", flush=True)
        if not ok:
            print("  ABORT: ini overrides are not reaching the simulator; "
                  "measurements would be meaningless.", flush=True)
            return 2

    tag = args.tag or f"N{args.N}_int{args.interval}"
    out_path = os.path.join(SRC, f"stepB_links_{tag}.json")
    rows = []
    pos = positions(args.N, args.cols, 1.0, args.altitude)

    for s in args.spacings:
        sc, err = one_run(args.N, args.cols, s, args.altitude, args.power, args.sens,
                          args.snir, args.interval, args.bitrate, args.simtime)
        if sc is None:
            print(f"  spacing={s:6.0f} m: FAIL ({err[:90]})", flush=True)
            rows.append({"spacing": s, "ok": False, "err": err})
            continue
        sent, recv = sc
        pts = positions(args.N, args.cols, s, args.altitude)
        links = []
        for i in range(args.N):
            j = (i + 1) % args.N
            d = math.dist(pts[i], pts[j])
            snt = sent[i]
            rcv = recv[j]
            links.append({"src": i, "dst": j, "dist": d, "sent": snt, "recv": rcv,
                          "pdr": (rcv / snt) if snt else None})
        good = [l["pdr"] for l in links if l["pdr"] is not None]
        mean = sum(good) / len(good) if good else None
        dmean = sum(l["dist"] for l in links) / len(links)
        print(f"  spacing={s:6.0f} m  mean link d={dmean:6.1f} m  "
              f"PDR={mean:.4f}  sent={links[0]['sent']:.0f}", flush=True)
        rows.append({"spacing": s, "ok": True, "altitude": args.altitude,
                     "interval": args.interval, "positions": pts,
                     "links": links, "mean_pdr": mean, "mean_dist": dmean})
    with open(out_path, "w") as f:
        json.dump(rows, f, indent=1)
    print("saved", out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
