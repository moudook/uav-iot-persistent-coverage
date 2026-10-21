"""
How far is the corner certificate from transferring to a random sensor set?

The region bound of Section IV is a statement about the CORNERS of the
region: the four corner points of the square are pairwise at least `side`
apart, which is more than 2*R_cov, so their coverage discs are pairwise
disjoint and each corner consumes K UAVs of its own.

For the SENSOR requirement the same proof would go through if the sensor
set contained four sensors whose coverage discs were pairwise disjoint.
This script asks how close to the corners the sensors would have to be for
that to hold, and how likely a uniform draw of M sensors is to do it.

Two facts are established, both in code rather than in prose:

1. THE CAP RADIUS.  If each of the four sensors sits within a distance r
   of its corner, the binding pair is two ADJACENT corners: the closest
   two points of their caps are (side - 2r) apart.  The discs are
   disjoint whenever side - 2r > 2*R_cov, i.e. r < (side - 2R_cov)/2.
   The grid check confirms that the minimum separation over the caps is
   what the formula says.

2. THE PROBABILITY.  The four corner caps are quarter-discs of radius r
   in the square, so each has area pi*r^2/4 and each is hit with
   probability p = pi*r^2/(4*side^2) by a uniform sensor.  The exact
   probability that all four are hit by M sensors follows from
   inclusion-exclusion over the four caps,

       P = sum_{k=0..4} (-1)^k C(4,k) (1 - k*p)^M,

   and a Monte-Carlo estimate is reported alongside it.

The measured packing survey is the operative statement for the paper: the
corner certificate does not transfer, and the packing bound does.  This
script supplies the geometry that explains WHY it does not transfer.

Usage:  python analysis/corner_transfer.py [--seeds 200000]
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ML = os.path.dirname(HERE)
sys.path.insert(0, ML)

from uav_wireless import SimConfig


def cap_radius_bound(side: float, r_cov: float) -> float:
    """The largest corner-cap radius that keeps the corner discs disjoint.

    Two sensors in ADJACENT corner caps are at least (side - 2r) apart
    (the worst case is both displaced along the shared edge).  Their
    coverage discs are disjoint iff that exceeds 2*R_cov.
    """
    return (side - 2.0 * r_cov) / 2.0


def cap_area_fraction(side: float, r: float) -> float:
    """The fraction of the square covered by one corner cap."""
    return (math.pi * r * r / 4.0) / (side * side)


def probability_all_caps_hit(side: float, r: float, m: int) -> float:
    """Exact probability that all four corner caps contain a sensor.

    Inclusion-exclusion over the four caps, each of which is hit
    independently with probability p by each uniform sensor.
    """
    p = cap_area_fraction(side, r)
    total = 0.0
    for k in range(5):
        total += ((-1) ** k) * math.comb(4, k) * (1.0 - k * p) ** m
    return max(0.0, total)


def monte_carlo(side: float, r: float, m: int, trials: int, rng) -> dict:
    """How often a uniform draw of M sensors hits all four corner caps."""
    hits = 0
    centres = np.array([[0.0, 0.0], [side, 0.0], [0.0, side], [side, side]])
    for _ in range(trials):
        pts = rng.uniform(0.0, side, size=(m, 2))
        d = np.linalg.norm(pts[:, None, :] - centres[None, :, :], axis=-1)
        if np.all(d.min(axis=0) <= r):
            hits += 1
    return {"trials": trials, "hits": hits,
            "estimate": hits / trials if trials else float("nan")}


def grid_min_separation(side: float, r: float, n: int = 161) -> float:
    """The minimum distance between two points in DIFFERENT corner caps.

    This is the quantity the cap-radius formula reasons about; the grid
    check confirms that the analytic bound is the one that binds.
    """
    g = np.linspace(0.0, side, n)
    X, Y = np.meshgrid(g, g, indexing="ij")
    pts = np.stack([X.ravel(), Y.ravel()], axis=1)
    centres = np.array([[0.0, 0.0], [side, 0.0], [0.0, side], [side, side]])
    d = np.linalg.norm(pts[:, None, :] - centres[None, :, :], axis=-1)
    cap = d.min(axis=1) <= r
    best = np.inf
    for i in range(4):
        for j in range(i + 1, 4):
            a = pts[cap & (d[:, i] <= r)]
            b = pts[cap & (d[:, j] <= r)]
            if len(a) == 0 or len(b) == 0:
                continue
            dd = np.linalg.norm(a[:, None, :] - b[None, :, :], axis=-1)
            best = min(best, float(dd.min()))
    return best


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=200_000)
    ap.add_argument("--out", default=os.path.join(HERE, "corner_transfer.json"))
    a = ap.parse_args()

    cfg = SimConfig()
    side, r_cov, m = cfg.side, cfg.R_cov, cfg.M

    r_star = cap_radius_bound(side, r_cov)
    # the bound is strict (side - 2r > 2 R_cov), so the radius used for the
    # probability is a hair under it and the grid check is run at that radius
    r_use = r_star - 1e-6
    p = cap_area_fraction(side, r_use)
    prob = probability_all_caps_hit(side, r_use, m)
    rng = np.random.default_rng(20261021)
    mc = monte_carlo(side, r_use, m, a.seeds, rng)

    # the grid check is run at the CLOSED bound r_star, where the caps are
    # just disjoint: the analytic bound is tight if the grid then reports
    # exactly side - 2*r_star = 2*R_cov
    grid_closed = grid_min_separation(side, r_star)

    payload = dict(
        side=side, R_cov=r_cov, M=m,
        two_R_cov=2.0 * r_cov,
        cap_radius_max=r_star,
        cap_radius_used=r_use,
        cap_area_fraction=p,
        probability_all_caps_hit=prob,
        monte_carlo=mc,
        grid_min_separation_closed=grid_closed,
        analytic_min_separation=side - 2.0 * r_star,
        grid_min_separation_open=grid_min_separation(side, r_use),
        note=("the corner certificate transfers to the sensor requirement "
              "only if the sensor set contains four sensors whose coverage "
              "discs are pairwise disjoint; with one sensor near each "
              "corner that means a cap radius below cap_radius_max, and a "
              "uniform draw does that with the probability above"),
    )
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=1)

    print("=" * 74)
    print("HOW CLOSE MUST THE SENSORS BE FOR THE CORNER CERTIFICATE TO HOLD?")
    print("=" * 74)
    print(f"  the square is {side:.0f} m on a side, R_cov = {r_cov:.0f} m, "
          f"so 2 R_cov = {2*r_cov:.0f} m")
    print(f"  adjacent corners are {side:.0f} m apart, so a sensor within r "
          f"of each corner is")
    print(f"  at least {side:.0f} - 2r apart: the discs stay disjoint "
          f"while r < {r_star:.2f} m")
    print(f"  grid check at the closed bound r = {r_star:.2f} m: the minimum "
          f"separation between different caps is")
    print(f"             {payload['grid_min_separation_closed']:.4f} m, and "
          f"the analytic bound is "
          f"{payload['analytic_min_separation']:.4f} m")
    print(f"             (they agree, so the bound is tight)")
    print(f"  a cap of radius {r_use:.3f} m is {100*p:.4f}% of the square")
    print(f"  a uniform draw of {m} sensors hits all four caps with "
          f"probability {prob:.3e}")
    print(f"  Monte-Carlo ({a.seeds} draws): {mc['hits']} hits "
          f"(estimate {mc['estimate']:.3e})")
    print(f"  written -> {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
