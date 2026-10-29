"""Step B1: PDR vs separation, two nodes, 50 m altitude, no contention.

Measures the PHY directly: one link in each direction, nothing else on the
channel.  Distances are the positions written into the trace, so the analysis
and the simulator cannot disagree about geometry.

Output: Simulation/omnet_uav2/pair_pdr.json
"""
import os, sys, json, argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inet_probe as ip

OUT = os.path.join(ip.SRC, "pair_pdr.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--distances", nargs="+", type=float,
                    default=[5, 10, 20, 30, 40, 60, 80, 100, 140, 180, 240, 320,
                             450, 650, 900, 1300, 1800])
    ap.add_argument("--altitude", type=float, default=50.0)
    ap.add_argument("--txPower", default="0.1W")
    ap.add_argument("--sensitivity", default="-85dBm")
    ap.add_argument("--snirThreshold", default="4dB")
    ap.add_argument("--sendInterval", default="0.1s")
    ap.add_argument("--bitrate", default="6Mbps")
    ap.add_argument("--simtime", type=float, default=20.0)
    ap.add_argument("--tag", default="")
    args = ap.parse_args()

    ip.ensure_env()
    if not ip.self_test():
        print("ABORT: ini overrides do not reach the simulator.", flush=True)
        return 2
    print("self-test: PASS (send interval scales packet count as expected)", flush=True)

    tag = args.tag or f"tx{args.txPower}_sens{args.sensitivity}"
    out_path = OUT.replace(".json", f"_{tag}.json")
    rows = []
    for d in args.distances:
        trace = ip.write_trace(f"pair_{int(d):05d}.movements",
                               [(0.0, 100.0, args.altitude), (d, 100.0, args.altitude)],
                               args.simtime)
        sent, recv, out = ip.run_probe(
            "UavPair", 2, trace, simtime=args.simtime,
            txPower=args.txPower, sensitivity=args.sensitivity,
            snirThreshold=args.snirThreshold, sendInterval=args.sendInterval,
            bitrate=args.bitrate)
        if sent is None:
            last = [l for l in out.strip().splitlines() if l.strip()]
            print(f"  d={d:7.0f} m: FAIL ({last[-1][:90] if last else '?'})", flush=True)
            rows.append({"dist": d, "ok": False})
            continue
        s0, r0, s1, r1 = sent[0], recv[0], sent[1], recv[1]
        p01 = (r1 / s0) if s0 else None
        p10 = (r0 / s1) if s1 else None
        vals = [p for p in (p01, p10) if p is not None]
        mean = sum(vals) / len(vals) if vals else None
        inner = max(0.0, (d ** 2 + (2 * args.altitude) ** 2) ** 0.5) if False else d
        print(f"  d={d:7.0f} m: PDR={mean:.4f}  (0->1 {p01:.3f}, 1->0 {p10:.3f}, "
              f"sent={s0:.0f})", flush=True)
        rows.append({"dist": d, "ok": True, "altitude": args.altitude,
                     "pdr": mean, "p01": p01, "p10": p10, "sent": s0, "recv": r1})
    with open(out_path, "w") as f:
        json.dump(rows, f, indent=1)
    print("saved", out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
