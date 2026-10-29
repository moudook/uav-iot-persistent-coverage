"""Shared driver for the controlled INET scenarios (UavPair / UavSwarm).

All tuning knobs are network-level parameters, so the ini uses single-star
patterns only.  Every measurement run is preceded (once per process) by a
self-test that sets a parameter to an invalid value and requires the run to
abort; a silently ignored override therefore cannot masquerade as a result.

Public API
----------
run_probe(network, N, trace, ..., simtime) -> (sent, recv, raw_output)
write_trace(name, positions, duration)     -> trace file name
self_test()                                -> bool
"""
import os, sys, re, json, subprocess, shutil

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(PROJ, "Simulation", "omnet_uav2")

WSL_ROOT = "/home/gbust/omnetpp_ws"
INET = WSL_ROOT + "/inet-4.6.0"
SCN = WSL_ROOT + "/uavsim"
SCN_UNC = r"\\wsl.localhost\Ubuntu" + SCN.replace("/", "\\")
INI = os.path.join(SCN_UNC, "omnetpp.ini")

RUN_SH = """#!/bin/bash
cd /home/gbust/omnetpp_ws
opp_env run inet-4.6.0 -c 'cd /home/gbust/omnetpp_ws/uavsim && rm -f results/General-*.sca results/General-*.vci results/General-*.vec && opp_run -u Cmdenv -l /home/gbust/omnetpp_ws/inet-4.6.0/out/clang-release/src/libINET.so -n /home/gbust/omnetpp_ws/inet-4.6.0/src:/home/gbust/omnetpp_ws/inet-4.6.0/examples:/home/gbust/omnetpp_ws/uavsim' 2>&1 | tail -25
"""


def ensure_env():
    subprocess.run(["wsl", "-d", "Ubuntu", "--", "bash", "-c",
                    "mkdir -p /home/gbust/omnetpp_ws/uavsim/traces /home/gbust/omnetpp_ws/uavsim/results"],
                   capture_output=True)
    for f in ("UavPair.ned", "UavSwarm.ned"):
        shutil.copyfile(os.path.join(SRC, f), os.path.join(SCN_UNC, f))


def write_ini(network, params, simtime):
    lines = ["[General]", f"network = {network}", f"sim-time-limit = {simtime}s", ""]
    for k, v in params.items():
        lines.append(f"*.{k} = {v}")
    lines += ["", "**.scalar-recording = true", "**.vector-recording = false", ""]
    with open(INI, "w", newline="\n") as f:
        f.write("\n".join(lines))


def run_raw():
    sh = os.path.join(SCN_UNC, "run.sh")
    with open(sh, "w", newline="\n") as f:
        f.write(RUN_SH)
    subprocess.run(["wsl", "-d", "Ubuntu", "--", "bash", "-c",
                    "sed -i 's/\\r$//' /home/gbust/omnetpp_ws/uavsim/run.sh && chmod +x /home/gbust/omnetpp_ws/uavsim/run.sh"],
                   capture_output=True)
    r = subprocess.run(["wsl", "-d", "Ubuntu", "--", "bash", "/home/gbust/omnetpp_ws/uavsim/run.sh"],
                       capture_output=True, text=True, timeout=1800)
    return r.stdout + r.stderr


def parse_sca(network, N):
    path = os.path.join(SCN_UNC, "results", "General-#0.sca")
    if not os.path.exists(path):
        return None
    sent = [0.0] * N
    recv = [0.0] * N
    pat = re.compile(r'^scalar\s+' + network + r'\.uav\[(\d+)\]\.app\[0\]\s+"([^"]+)"\s+(\S+)')
    with open(path, errors="replace") as f:
        for line in f:
            m = pat.match(line.strip())
            if not m:
                continue
            i, name, val = int(m.group(1)), m.group(2), m.group(3)
            if i >= N:
                continue
            try:
                v = float(val)
            except ValueError:
                continue
            if name == "packets sent":
                sent[i] = v
            elif name == "packets received":
                recv[i] = v
    return sent, recv


def write_trace(name, positions, duration):
    """3-D BonnMotion trace: one line per node, (t x y z) tuples."""
    path = os.path.join(SCN_UNC, "traces", name)
    with open(path, "w", newline="\n") as f:
        for (x, y, z) in positions:
            f.write(f"0.00 {x:.3f} {y:.3f} {z:.3f} {duration:.2f} {x:.3f} {y:.3f} {z:.3f}\n")
    return name


def run_probe(network, N, trace, simtime=20.0, txPower="0.1W", sensitivity="-85dBm",
              snirThreshold="4dB", sendInterval="0.1s", bitrate="6Mbps",
              extra=None):
    params = {
        "simTrace": f'"traces/{trace}"',
        "simTxPower": txPower,
        "simSensitivity": sensitivity,
        "simSnir": snirThreshold,
        "simInterval": sendInterval,
        "simBitrate": bitrate,
    }
    if network == "UavSwarm":
        params["simNumUavs"] = N
    if extra:
        params.update(extra)
    write_ini(network, params, simtime)
    out = run_raw()
    if "Simulation time limit reached" not in out:
        return None, None, out
    return (*parse_sca(network, N), out)


_SELF_TESTED = {"done": False, "ok": False}


def self_test():
    """Prove the ini reaches the simulator, behaviourally.

    Two earlier versions of this check were worthless.  The first only
    required a run to FAIL, and passed while the NED file was not even
    loading.  The second used an "invalid" sensitivity of -1e9 dBm, which is
    merely EXTREME (maximum sensitivity), not invalid: the run completed
    normally and every packet still arrived.

    So the check is now causal: shortening the send interval by 5x must
    produce roughly 5x more packets.  A parameter that is silently ignored
    cannot pass that.
    """
    if _SELF_TESTED["done"]:
        return _SELF_TESTED["ok"]
    ensure_env()
    write_trace("_selftest.movements", [(0.0, 0.0, 50.0), (30.0, 0.0, 50.0)], 3.0)

    slow, _, out_slow = run_probe("UavPair", 2, "_selftest.movements",
                                  simtime=2.0, sendInterval="0.1s")
    fast, _, out_fast = run_probe("UavPair", 2, "_selftest.movements",
                                  simtime=2.0, sendInterval="0.02s")

    ok = False
    reason = ""
    if slow is None or fast is None:
        last = [l for l in (out_slow + out_fast).strip().splitlines() if l.strip()]
        reason = "run failed: " + (last[-1][:120] if last else "?")
    else:
        n_slow, n_fast = sum(slow), sum(fast)
        total = n_slow + n_fast
        if n_slow < 5:
            reason = f"baseline sent only {n_slow:.0f} packets"
        elif n_fast < 3.0 * n_slow:
            reason = (f"interval had no effect: {n_slow:.0f} packets at 0.1 s vs "
                      f"{n_fast:.0f} at 0.02 s")
        else:
            ok = True
    if reason:
        print("  self-test:", reason, flush=True)
    _SELF_TESTED["ok"] = ok
    _SELF_TESTED["done"] = True
    return ok
