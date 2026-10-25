import json, glob
for f in sorted(glob.glob("ml_impl/runs/g1/seed_*.json")):
    d = json.load(open(f))
    hist = d["hist"]
    cks = [h.get("CK", 0.0) for h in hist]
    last10 = cks[-10:]
    print(f"seed {d['seed']}: final CK={d['final_ck']:.4f}, last10 mean={sum(last10)/len(last10):.4f}, last10 min={min(last10):.4f}, max={max(last10):.4f}")
# overall
all_finals = []
all_last10 = []
for f in sorted(glob.glob("ml_impl/runs/g1/seed_*.json")):
    d = json.load(open(f))
    hist = d["hist"]
    cks = [h.get("CK", 0.0) for h in hist]
    all_finals.append(d["final_ck"])
    all_last10.extend(cks[-10:])
import statistics
print(f"\nMean final CK: {statistics.mean(all_finals):.4f} (sd {statistics.stdev(all_finals):.4f})")
print(f"Mean last-10 CK: {statistics.mean(all_last10):.4f} (sd {statistics.stdev(all_last10):.4f})")
