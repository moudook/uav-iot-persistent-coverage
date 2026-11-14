"""Compare the v2 retrain against the verified v1 headline.

Reads only stored artifacts; prints a paired per-seed comparison on the
held-out scenes, the AG/SC means, and the stress-regime table if a v2 stress
artifact exists.  No training and no evaluation.
"""
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RUNS = os.path.join(ROOT, "ml_impl", "runs")


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def headline(tag):
    p = os.path.join(RUNS, tag, "eval_heldout.json")
    if not os.path.exists(p):
        return None
    h = load(p)
    per = [float(v["mean"]) for v in h["per_checkpoint"].values()]
    return h, per


def main():
    v1 = headline("exp_ego_fixed")
    v2 = headline("exp_v2")
    if v1 is None:
        print("v1 eval_heldout missing")
        return 1
    h1, p1 = v1
    print("v1  CK=%.4f sd=%.4f n=%d" % (
        h1["mean_over_seeds"], h1["sd_over_seeds"], len(p1)))
    if v2 is None:
        print("v2 eval_heldout not ready")
        return 0
    h2, p2 = v2
    print("v2  CK=%.4f sd=%.4f n=%d" % (
        h2["mean_over_seeds"], h2["sd_over_seeds"], len(p2)))
    if len(p1) == len(p2):
        d = np.array(p2) - np.array(p1)
        from scipy import stats
        half = float(stats.t.ppf(0.975, len(d) - 1)
                     * np.std(d, ddof=1) / np.sqrt(len(d)))
        print("paired v2-v1: %+.4f  95%% CI [%+.4f, %+.4f]  per-seed %s"
              % (d.mean(), d.mean() - half, d.mean() + half,
                 ", ".join("%+.4f" % x for x in d)))
    for tag in ("exp_ego_fixed", "exp_v2"):
        p = os.path.join(RUNS, tag, "agsc.json")
        if os.path.exists(p):
            m = load(p)["mean"]
            print("%s AG=%.4f SC=%.4f" % (tag, m["AG"], m["SC"]))
    s2 = os.path.join(RUNS, "stress_eval", "stress_eval_v2.json")
    if os.path.exists(s2):
        reg = load(s2)["regimes"]
        print("\nstress regime          v2 model   best rule   delta    w/l")
        for name, r in reg.items():
            m = r.get("learner_mean")
            if m is None:
                continue
            b = r.get("best_rule_ck")
            print("%-22s %8.4f  %9.4f  %+7.4f   %s"
                  % (name, m, b, m - b, "MODEL" if m > b else "RULE"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
