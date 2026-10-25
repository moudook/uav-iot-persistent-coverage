"""Analyze G3 results: per-regime CK, headroom check, C3 vs team comparison."""
import json, glob, os, statistics

def load(regime, credit):
    out = []
    base = os.path.join("ml_impl", "runs", "g3", regime, credit)
    for f in sorted(glob.glob(os.path.join(base, "seed_*.json"))):
        d = json.load(open(f))
        hist = d["hist"]
        cks = [h.get("CK", 0) for h in hist]
        ents = [h.get("entropy", 0) for h in hist]
        out.append({
            "seed": d["seed"],
            "final_ck": d["final_ck"],
            "last10_ck": sum(cks[-10:]) / 10 if len(cks) >= 10 else sum(cks)/len(cks),
            "min_ck": min(cks), "max_ck": max(cks),
            "final_ent": ents[-1] if ents else 0,
            "n_ep": len(hist),
        })
    return out

def summarize(regime, credit):
    data = load(regime, credit)
    if not data:
        return None
    finals = [d["final_ck"] for d in data]
    last10s = [d["last10_ck"] for d in data]
    ents = [d["final_ent"] for d in data]
    print(f"\n=== {regime} / {credit} (n={len(data)}) ===")
    print(f"  final CK:  mean={statistics.mean(finals):.4f} sd={statistics.stdev(finals):.4f} range=[{min(finals):.4f}, {max(finals):.4f}]")
    print(f"  last10 CK: mean={statistics.mean(last10s):.4f} sd={statistics.stdev(last10s):.4f}")
    print(f"  entropy:   mean={statistics.mean(ents):.4f} (min={min(ents):.4f})")
    # headroom
    headroom = 1.0 - statistics.mean(finals)
    print(f"  headroom (1 - mean CK): {headroom:.4f} {'OK' if headroom >= 0.10 else 'FAIL'}")
    return data

if __name__ == "__main__":
    import sys
    regimes = sys.argv[1:] if len(sys.argv) > 1 else ["single_pad"]
    for r in regimes:
        for credit in ["team", "c3"]:
            summarize(r, credit)
