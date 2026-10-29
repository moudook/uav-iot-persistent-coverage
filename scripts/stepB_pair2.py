"""Step B1: PDR vs separation, two nodes, 50 m altitude, no contention.

Measures the PHY directly: one link in each direction, nothing else on the
channel.  Distances are the positions written into the trace, so the analysis
and the simulator cannot disagree about geometry.

Shadowing is quasi-static per link, not per packet (INET caches the path loss
for the duration of a transmission, and the draw is per link per run).  A single
run therefore samples ONE shadowing realisation, and reading it as an outage
probability is wrong -- the first version of this script did exactly that and
reported PDR = 1.0 at 1500 m and 0.0 at 1800 m from runs that differed only in
seed.  Every point here is the mean over `--reps` independent run numbers, each
with its own seed-set.

Output: Simulation/omnet_uav2/pair_pdr_<tag>.json
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
    ap.add_argument("--sigma", default="6")
    ap.add_argument("--noise", default="-94dBm")
    ap.add_argument("--simtime", type=float, default=20.0)
    ap.add_argument("--reps", type=int, default=1)
    ap.add_argument("--tag", default="")
    args = ap.parse_args()

    ip.ensure_env()
    if not ip.self_test():
        print("ABORT: self-test failed, measurements would be meaningless.", flush=True)
        return 2
    print("self-test: PASS (send interval scales packet count as expected)", flush=True)

    tag = args.tag or f"tx{args.txPower}_sens{args.sensitivity}"
    out_path = OUT.replace(".json", f"_{tag}.json")
    rows = []
    for d in args.distances:
        trace = ip.write_trace(f"pair_{int(d):05d}.movements",
                               [(0.0, 100.0, args.altitude), (d, 100.0, args.altitude)],
                               args.simtime)
        pdrs, sents, fails = [], [], 0
        for r in range(args.reps):
            sent, recv, out = ip.run_probe(
                "UavPair", 2, trace, simtime=args.simtime,
                txPower=args.txPower, sensitivity=args.sensitivity,
                snirThreshold=args.snirThreshold, sendInterval=args.sendInterval,
                bitrate=args.bitrate, sigma=args.sigma, noise=args.noise,
                runnumber=r)
            if sent is None:
                fails += 1
                continue
            s0, r0, s1, r1 = sent[0], recv[0], sent[1], recv[1]
            p01 = (r1 / s0) if s0 else None
            p10 = (r0 / s1) if s1 else None
            vals = [p for p in (p01, p10) if p is not None]
            if vals:
                pdrs.append(sum(vals) / len(vals))
                sents.append(s0)
        if not pdrs:
            print(f"  d={d:7.0f} m: FAIL ({fails} failed runs)", flush=True)
            rows.append({"dist": d, "ok": False, "fails": fails})
            continue
        mean = sum(pdrs) / len(pdrs)
        lo, hi = min(pdrs), max(pdrs)
        print(f"  d={d:7.0f} m: PDR={mean:.4f}  [{lo:.3f}, {hi:.3f}]  "
              f"reps={len(pdrs)} sent={sum(sents)/len(sents):.0f}", flush=True)
        rows.append({"dist": d, "ok": True, "altitude": args.altitude,
                     "sigma": args.sigma, "reps": len(pdrs),
                     "pdr": mean, "pdr_min": lo, "pdr_max": hi,
                     "pdr_all": pdrs, "sent": sents[0] if sents else None})
    with open(out_path, "w") as f:
        json.dump(rows, f, indent=1)
    print("saved", out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
