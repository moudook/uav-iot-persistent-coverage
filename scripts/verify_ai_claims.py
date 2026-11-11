import csv, sys
import numpy as np
from pathlib import Path
from collections import defaultdict

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("ml_impl")
for p in sorted(root.glob("results_*.csv")):
    seen = defaultdict(list)
    for r in csv.DictReader(open(p, encoding="utf-8")):
        v = r.get("per_seed_CK") or r.get("per_seed_ck")
        if not v:
            continue
        x = np.array([float(t) for t in v.split(";")])
        try:
            s = float(r["CK_std"])
        except Exception:
            s = None
        if s is None:
            tag = "NOSTD"
        else:
            tag = ("ddof=0" if abs(s - x.std()) < 1e-9
                   else ("ddof=1" if abs(s - x.std(ddof=1)) < 1e-9 else "MISMATCH"))
        if "model" not in r:
            continue
        print(f"{p.name:38s} {r['model']:22s} {tag}")
        seen[tuple(np.round(x, 6))].append(r["model"])
    for vec, models in seen.items():
        if len(models) > 1:
            print(f"  IDENTICAL VECTORS in {p.name}: {models}")
