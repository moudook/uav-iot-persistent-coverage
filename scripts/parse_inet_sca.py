"""Parse an INET .sca file and extract per-module scalar statistics."""
import os, sys, re, argparse

def parse(path):
    scalars = {}
    current_module = None
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line.startswith("scalar "):
                parts = line.split()
                # scalar <module> <name> <value>
                if len(parts) >= 4:
                    mod = parts[1]
                    name = parts[2]
                    try:
                        val = float(parts[3])
                    except ValueError:
                        continue
                    scalars.setdefault(mod, {})[name] = val
            elif line.startswith("module "):
                current_module = line.split()[1] if len(line.split()) > 1 else None
    return scalars

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sca", help="path to .sca file")
    args = ap.parse_args()
    sc = parse(args.sca)
    print(f"Modules: {len(sc)}")
    # Print beacon-related scalars
    for mod, vals in sorted(sc.items()):
        if "mac" in mod or "app" in mod or "udp" in mod:
            for k, v in vals.items():
                if "packetReceived\|packetSent\|dropped" in k or "received" in k.lower() or "sent" in k.lower():
                    print(f"  {mod}: {k} = {v}")
    # Summary
    total_tx = sum(v.get("packetSent", 0) for m, v in sc.items() if "mac" in m)
    total_rx = sum(v.get("packetReceivedFromPeer:count", 0) for m, v in sc.items() if "mac" in m)
    print(f"\nSummary: MAC tx={total_tx}, rx(peer)={total_rx}")

if __name__ == "__main__":
    main()
