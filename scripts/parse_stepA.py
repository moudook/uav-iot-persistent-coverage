"""Parse INET .sca for Step A: per-link beacon delivery, PDR, delay."""
import os, sys, re, json, argparse

def parse_sca(path):
    scalars = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line.startswith("scalar "):
                continue
            # handle quoted names: scalar <mod> "name" value
            m = re.match(r'scalar\s+(\S+)\s+"([^"]+)"\s+(\S+)', line)
            if m:
                mod, name, valstr = m.group(1), m.group(2), m.group(3)
            else:
                parts = line.split()
                if len(parts) < 4:
                    continue
                mod, name, valstr = parts[1], parts[2], parts[3]
            try:
                val = float(valstr)
            except ValueError:
                continue
            scalars.setdefault(mod, {})[name] = val
    return scalars

def extract(sca_path):
    sc = parse_sca(sca_path)
    uav_stats = {}
    for mod, vals in sc.items():
        if ".app[0]" in mod and "uav" in mod:
            uid = mod.split("uav[")[1].split("]")[0]
            uav_stats[uid] = {
                "sent": vals.get("packets sent", 0),
                "received": vals.get("packets received", 0),
            }
    total_sent = sum(v["sent"] for v in uav_stats.values())
    total_rx = sum(v["received"] for v in uav_stats.values())
    pdr = total_rx / total_sent if total_sent > 0 else 0
    return {
        "uav_app": uav_stats,
        "total_sent": total_sent,
        "total_received": total_rx,
        "pdr": pdr,
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sca")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    res = extract(args.sca)
    print("Total sent: %d, received: %d" % (res["total_sent"], res["total_received"]))
    print("PDR (app-level): %.4f" % res["pdr"])
    for uid, v in sorted(res["uav_app"].items()):
        print("  uav[%s]: sent=%d received=%d" % (uid, v["sent"], v["received"]))
    if args.out:
        with open(args.out, "w") as f:
            import json
            json.dump(res, f, indent=2)
        print("saved to " + args.out)

if __name__ == "__main__":
    main()
