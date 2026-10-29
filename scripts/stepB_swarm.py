"""Step B2: delivery ratio vs swarm DENSITY (MAC contention), not distance.

Step B1 measures one isolated link.  This probe puts many nodes on one channel
and measures how delivery degrades as the number of contenders rises: every
node transmits to uav[0], and uav[0] transmits to uav[1], so the measurement
node is itself a contender rather than a silent observer.

Aggregate delivery ratio
    PDR = recv[0] / sum(sent[i] for i != 0)
because uav[0]'s own packets go to uav[1], not to itself.

Geometry: a square grid of side `spacing` at `altitude`, supplied as a 3-D
BonnMotion trace, so node density and link distance are controlled separately
(spacing held fixed, N varied; then N held fixed, spacing varied).

Output: Simulation/omnet_uav2/swarm_contention.json
"""
import os, sys, json, math, argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inet_probe as ip

OUT = os.path.join(ip.SRC, "swarm_contention.json")


def grid_positions(n, spacing, altitude, cols=None):
    cols = cols or max(1, int(math.ceil(math.sqrt(n))))
    return [((i % cols) * spacing, (i // cols) * spacing, altitude) for i in range(n)]


def run_point(n, spacing, altitude, interval, simtime, **kw):
    pts = grid_positions(n, spacing, altitude)
    trace = ip.write_trace(f"swarm_n{n}_s{int(spacing)}.movements", pts, simtime)
    sent, recv, out = ip.run_probe("UavSwarm", n, trace, simtime=simtime,
                                   sendInterval=interval, **kw)
    if sent is None:
        last = [l for l in out.strip().splitlines() if l.strip()]
        return None, (last[-1][:120] if last else "?")
    contenders = sum(sent) - sent[0]
    delivered = recv[0]
    pdr = (delivered / contenders) if contenders > 0 else None
    return {"n": n, "spacing": spacing, "interval": interval,
            "contenders_sent": contenders, "delivered": delivered,
            "pdr": pdr, "own_sent": sent[0], "own_recv": recv[1] if len(recv) > 1 else None}, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-list", nargs="+", type=int, default=[4, 8, 16, 32, 64])
    ap.add_argument("--spacing", type=float, default=20.0)
    ap.add_argument("--altitude", type=float, default=50.0)
    ap.add_argument("--intervals", nargs="+", default=["0.1s"])
    ap.add_argument("--simtime", type=float, default=20.0)
    ap.add_argument("--txPower", default="0.1W")
    ap.add_argument("--sensitivity", default="-85dBm")
    ap.add_argument("--snirThreshold", default="4dB")
    ap.add_argument("--bitrate", default="6Mbps")
    ap.add_argument("--tag", default="")
    args = ap.parse_args()

    ip.ensure_env()
    if not ip.self_test():
        print("ABORT: self-test failed, measurements would be meaningless.", flush=True)
        return 2
    print("self-test: PASS", flush=True)

    out_path = OUT.replace(".json", f"_{args.tag}.json") if args.tag else OUT
    rows = []
    for interval in args.intervals:
        for n in args.n_list:
            res, err = run_point(n, args.spacing, args.altitude, interval, args.simtime,
                                 txPower=args.txPower, sensitivity=args.sensitivity,
                                 snirThreshold=args.snirThreshold, bitrate=args.bitrate)
            if res is None:
                print(f"  N={n:3d} interval={interval}: FAIL ({err})", flush=True)
                rows.append({"n": n, "interval": interval, "ok": False, "err": err})
                continue
            print(f"  N={n:3d} interval={interval}: PDR={res['pdr']:.4f}  "
                  f"sent={res['contenders_sent']:.0f} delivered={res['delivered']:.0f}", flush=True)
            res["ok"] = True
            rows.append(res)
    with open(out_path, "w") as f:
        json.dump(rows, f, indent=1)
    print("saved", out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
