"""Fit a PDR(d) model to the INET outage measurements.

Reads Simulation/omnet_uav2/pair_pdr_<tag>.json and fits:

  PDR(d) = 1 / (1 + exp(-(a + b*log(d))))

i.e. a logistic in log-distance, which is the standard form for an outage
probability under log-normal shadowing.  Reports the knee (distance where
PDR = 0.5 and where PDR = 0.9) and writes a dense fitted curve to CSV.

Run after stepB_pair2.py finishes:
    python scripts/fit_pdr.py --tag outage
"""
import os, sys, json, math, argparse

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(PROJ, "Simulation", "omnet_uav2")


def load(tag):
    path = os.path.join(SRC, f"pair_pdr_{tag}.json")
    data = json.load(open(path))
    pts = [(r["dist"], r["pdr"], r.get("pdr_min"), r.get("pdr_max"))
           for r in data if r.get("ok")]
    return pts, path


def fit_logistic(pts):
    """Least squares on (log d, logit PDR).  Returns (a, b) or None."""
    import numpy as np
    xs, ys = [], []
    for d, p, lo, hi in pts:
        if p is None or p <= 0 or p >= 1:
            continue
        xs.append(math.log(d))
        ys.append(math.log(p / (1 - p)))
    if len(xs) < 3:
        return None
    x = np.asarray(xs); y = np.asarray(ys)
    A = np.vstack([np.ones_like(x), x]).T
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    return float(coef[0]), float(coef[1])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="outage")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    pts, path = load(args.tag)
    print(f"loaded {len(pts)} points from {path}")
    for d, p, lo, hi in pts:
        print(f"  d={d:7.0f} m  PDR={p:.4f}  [{lo:.3f}, {hi:.3f}]")

    coef = fit_logistic(pts)
    if coef is None:
        print("not enough non-degenerate points to fit")
        return 1
    a, b = coef
    print(f"\nfit: logit PDR = {a:.3f} + {b:.3f} * ln(d)")

    def pdr(d):
        return 1.0 / (1.0 + math.exp(-(a + b * math.log(d))))

    # knee distances
    for target in (0.99, 0.9, 0.5):
        # solve a + b ln d = logit(target)
        logit = math.log(target / (1 - target))
        d = math.exp((logit - a) / b)
        print(f"  PDR = {target:.2f} at d = {d:7.0f} m")

    out_path = args.out or os.path.join(SRC, f"pdr_fit_{args.tag}.csv")
    with open(out_path, "w") as f:
        f.write("dist_m,pdr_fit\n")
        for i in range(1, 2001):
            d = 10.0 * i
            f.write(f"{d:.0f},{pdr(d):.6f}\n")
    print("wrote fitted curve:", out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
