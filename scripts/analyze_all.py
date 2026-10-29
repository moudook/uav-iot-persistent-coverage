"""Comprehensive G3 + residual analysis for the paper.

Computes per-regime stats, C3 vs team comparisons, residual MAPPO vs MAPPO,
headroom gates, and rliable-style aggregates (IQM, mean, median, optimality gap,
probability of improvement) with bootstrap CIs via scipy.stats.bootstrap.

Usage: python scripts/analyze_all.py
"""
import os, sys, json, glob, statistics, numpy as np
from scipy.stats import bootstrap, mannwhitneyu

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
G3 = os.path.join(PROJ, "ml_impl", "runs", "g3")
RES = os.path.join(PROJ, "ml_impl", "runs", "residual")


def load_g3(regime, mode):
    base = os.path.join(G3, regime, mode)
    out = []
    for f in sorted(glob.glob(os.path.join(base, "seed_*.json"))):
        d = json.load(open(f))
        hist = d["hist"]
        cks = [h.get("CK", 0.0) for h in hist]
        ents = [h.get("entropy", 0.0) for h in hist]
        out.append({
            "seed": d["seed"],
            "final_ck": d["final_ck"],
            "mean_ck": statistics.fmean(cks) if cks else None,
            "last10_ck": statistics.fmean(cks[-10:]) if len(cks) >= 10 else None,
            "min_ent": min(ents) if ents else None,
            "final_ent": ents[-1] if ents else None,
            "n_ep": len(hist),
            "seconds": d["seconds"],
        })
    return out


def load_residual(regime):
    base = os.path.join(RES, regime)
    out = []
    for f in sorted(glob.glob(os.path.join(base, "seed_*.json"))):
        d = json.load(open(f))
        hist = d["hist"]
        cks = [h.get("CK", 0.0) for h in hist]
        out.append({
            "seed": d["seed"],
            "final_ck": d["final_ck"],
            "mean_ck": statistics.fmean(cks) if cks else None,
            "last10_ck": statistics.fmean(cks[-10:]) if len(cks) >= 10 else None,
            "final_ent": (hist[-1].get("entropy") if hist else None),
            "n_ep": len(hist),
        })
    return out


def summarise(rows, key="final_ck"):
    if not rows:
        return None
    vals = [r[key] for r in rows if r[key] is not None]
    if not vals:
        return None
    arr = np.array(vals)
    mean = float(np.mean(arr))
    sd = float(np.std(arr, ddof=1)) if len(arr) > 1 else 0.0
    # bootstrap CI
    try:
        res = bootstrap((arr,), np.mean, n_resamples=10000, confidence_level=0.95,
                        method="BCa", rng=np.random.default_rng(42))
        ci_lo = float(res.confidence_interval.low)
        ci_hi = float(res.confidence_interval.high)
    except Exception as e:
        ci_lo = ci_hi = float("nan")
    return {
        "n": len(vals),
        "mean": mean,
        "sd": sd,
        "min": float(np.min(arr)),
        "max": float(np.max(arr)),
        "ci95": (ci_lo, ci_hi),
    }


def iqm(arr):
    return float(scipy_trim_mean(arr, 0.25)) if False else None


from scipy.stats import trim_mean as _trim_mean


def agg_iqm(arr):
    return float(_trim_mean(arr, 0.25))


def rliable_block(label, scores, gamma=1.0):
    """Compute rliable-style aggregates with bootstrap CIs."""
    arr = np.array(scores, dtype=float)
    n = len(arr)
    mean = float(np.mean(arr))
    median = float(np.median(arr))
    iqm_val = float(_trim_mean(arr, 0.25))
    og = float(gamma - np.mean(np.minimum(arr, gamma)))  # optimality gap
    # bootstrap CIs
    def ci(stat_func):
        try:
            res = bootstrap((arr,), stat_func, n_resamples=10000, confidence_level=0.95,
                            method="BCa", rng=np.random.default_rng(42))
            return (float(res.confidence_interval.low), float(res.confidence_interval.high))
        except Exception:
            return (float("nan"), float("nan"))
    print(f"  {label} (n={n}):")
    print(f"    mean={mean:.4f}  95%CI=[{ci(np.mean)[0]:.4f}, {ci(np.mean)[1]:.4f}]")
    print(f"    median={median:.4f}  95%CI=[{ci(np.median)[0]:.4f}, {ci(np.median)[1]:.4f}]")
    print(f"    IQM={iqm_val:.4f}  95%CI=[{ci(agg_iqm)[0]:.4f}, {ci(agg_iqm)[1]:.4f}]")
    print(f"    optimality_gap={og:.4f}  95%CI=[{ci(lambda x: gamma - np.mean(np.minimum(x, gamma)))[0]:.4f}, "
          f"{ci(lambda x: gamma - np.mean(np.minimum(x, gamma)))[1]:.4f}]")
    return {"mean": mean, "median": median, "iqm": iqm_val, "og": og, "n": n}


def prob_improvement(x, y):
    """P(X > Y) averaged, with Mann-Whitney U."""
    x, y = np.array(x, float), np.array(y, float)
    if np.array_equal(x, y):
        p = 0.5
    else:
        u, _ = mannwhitneyu(x, y, alternative="greater")
        p = u / (len(x) * len(y))
    return float(p)


def main():
    print("=" * 70)
    print("G3 COMPREHENSIVE ANALYSIS")
    print("=" * 70)

    regimes = ["single_pad", "small_battery", "low_comm", "failure", "multi_failure"]
    reactive = {"nominal": 0.7162, "single_pad": 0.7402, "small_battery": 0.7162,
                "low_comm": 0.6757, "failure": 0.7162, "multi_failure": 0.7162}

    # --- Per-regime team results ---
    print("\n" + "=" * 70)
    print("1. PER-REGIME TEAM RESULTS (MAPPO)")
    print("=" * 70)
    team_results = {}
    for r in regimes:
        rows = load_g3(r, "team")
        if not rows:
            print(f"  {r}: NO DATA")
            continue
        s = summarise(rows)
        hr = 1.0 - s["mean"]
        team_results[r] = (rows, s)
        print(f"\n  {r} (n={s['n']}):")
        print(f"    final CK:  mean={s['mean']:.4f}  sd={s['sd']:.4f}  "
              f"range=[{s['min']:.4f}, {s['max']:.4f}]")
        print(f"    95% CI:    [{s['ci95'][0]:.4f}, {s['ci95'][1]:.4f}]")
        print(f"    entropy:   mean={statistics.fmean([r2['final_ent'] for r2 in rows if r2['final_ent'] is not None]):.3f}")
        print(f"    headroom:  {hr:.4f}  {'OK' if hr >= 0.10 else 'FAIL'}")
        print(f"    reactive CK={reactive.get(r, '?'):.4f}  "
              f"learned-reactive gap={s['mean'] - reactive.get(r, 0):.4f}")

    # --- C3 vs team ---
    print("\n" + "=" * 70)
    print("2. C3 CREDIT vs TEAM REWARD")
    print("=" * 70)
    for r in ["single_pad", "small_battery"]:
        team_rows = load_g3(r, "team")
        c3_rows = load_g3(r, "c3")
        if not team_rows or not c3_rows:
            print(f"  {r}: missing data (team={len(team_rows)}, c3={len(c3_rows)})")
            continue
        print(f"\n  {r}:")
        ts = summarise(team_rows)
        cs = summarise(c3_rows)
        print(f"    team:  CK={ts['mean']:.4f} sd={ts['sd']:.4f}  ent={statistics.fmean([r2['final_ent'] for r2 in team_rows]):.3f}")
        print(f"    c3:    CK={cs['mean']:.4f} sd={cs['sd']:.4f}  ent={statistics.fmean([r2['final_ent'] for r2 in c3_rows]):.3f}")
        # paired delta
        t_by = {r2["seed"]: r2 for r2 in team_rows}
        c_by = {r2["seed"]: r2 for r2 in c3_rows}
        common = sorted(set(t_by) & set(c_by))
        if common:
            deltas = [c_by[s]["final_ck"] - t_by[s]["final_ck"] for s in common]
            d_mean = statistics.fmean(deltas)
            d_sd = statistics.stdev(deltas) if len(deltas) > 1 else 0.0
            # paired t-test
            from scipy.stats import ttest_rel
            t_stat, p_val = ttest_rel([c_by[s]["final_ck"] for s in common],
                                       [t_by[s]["final_ck"] for s in common])
            print(f"    paired delta (c3-team): mean={d_mean:+.4f} sd={d_sd:.4f}  "
                  f"range=[{min(deltas):+.4f}, {max(deltas):+.4f}]")
            print(f"    paired t-test: t={t_stat:.3f}  p={p_val:.4f}")
            pi = prob_improvement([c_by[s]["final_ck"] for s in common],
                                  [t_by[s]["final_ck"] for s in common])
            print(f"    P(c3 > team) = {pi:.3f}")
        # headroom
        print(f"    headroom team={1-ts['mean']:.4f}  c3={1-cs['mean']:.4f}")

    # --- Residual MAPPO ---
    print("\n" + "=" * 70)
    print("3. RESIDUAL MAPPO (BC init + PPO)")
    print("=" * 70)
    res_rows = load_residual("single_pad")
    if res_rows:
        rs = summarise(res_rows)
        print(f"  residual on single_pad (n={rs['n']}):")
        print(f"    final CK:  mean={rs['mean']:.4f}  sd={rs['sd']:.4f}  "
              f"range=[{rs['min']:.4f}, {rs['max']:.4f}]")
        print(f"    95% CI:    [{rs['ci95'][0]:.4f}, {rs['ci95'][1]:.4f}]")
        # compare to MAPPO team on single_pad
        sp_team = load_g3("single_pad", "team")
        if sp_team:
            sps = summarise(sp_team)
            print(f"  MAPPO team on single_pad: CK={sps['mean']:.4f} sd={sps['sd']:.4f}")
            print(f"  residual - MAPPO: {rs['mean'] - sps['mean']:+.4f}")
            pi = prob_improvement([r["final_ck"] for r in res_rows],
                                  [r["final_ck"] for r in sp_team])
            print(f"  P(residual > MAPPO) = {pi:.3f}")
    else:
        print("  NO DATA")

    # --- Headroom gate ---
    print("\n" + "=" * 70)
    print("4. HEADROOM GATE (ceiling - best tuned rule >= 0.10)")
    print("=" * 70)
    tuned_rules = {
        "single_pad": 0.7402,
        "small_battery": 0.7162,
        "low_comm": 0.6757,
        "failure": 0.7162,
        "multi_failure": 0.7162,
    }
    for r in regimes:
        rows = load_g3(r, "team")
        if not rows:
            continue
        s = summarise(rows)
        best_learned = s["mean"]
        tuned = tuned_rules.get(r, 0.0)
        best = max(best_learned, tuned)
        headroom = 1.0 - best
        gate = "PASS" if headroom >= 0.10 else "FAIL"
        print(f"  {r}: best={best:.4f} (learned={best_learned:.4f}, tuned={tuned:.4f})  "
              f"headroom={headroom:.4f}  {gate}")

    # --- rliable-style aggregates ---
    print("\n" + "=" * 70)
    print("5. RLIABLE-STYLE AGGREGATES (across regimes as tasks)")
    print("=" * 70)
    # Build score matrix: rows=seeds, cols=regimes (only regimes with data)
    # For team mode
    score_matrix = []
    regime_list = []
    for r in regimes:
        rows = load_g3(r, "team")
        if rows:
            regime_list.append(r)
    # Need same number of seeds per regime for matrix; use min
    min_n = min(len(load_g3(r, "team")) for r in regime_list)
    print(f"  regimes: {regime_list}, min seeds={min_n}")
    scores = np.array([[load_g3(r, "team")[i]["final_ck"] for r in regime_list]
                       for i in range(min_n)])
    print(f"  score matrix shape: {scores.shape}")
    rliable_block("MAPPO (team) across regimes", scores.flatten())

    # C3 aggregate where available
    c3_regimes = [r for r in ["single_pad", "small_battery"] if load_g3(r, "c3")]
    if c3_regimes:
        c3_min_n = min(len(load_g3(r, "c3")) for r in c3_regimes)
        c3_scores = np.array([[load_g3(r, "c3")[i]["final_ck"] for r in c3_regimes]
                              for i in range(c3_min_n)])
        rliable_block("C3 credit across regimes", c3_scores.flatten())

    # --- Stress regime comparison ---
    print("\n" + "=" * 70)
    print("6. STRESS REGIME COMPARISON (MAPPO team)")
    print("=" * 70)
    print(f"  {'regime':<16s} {'CK':>8s} {'sd':>7s} {'ent':>7s} {'headroom':>10s} {'vs reactive':>12s}")
    for r in regimes:
        rows = load_g3(r, "team")
        if not rows:
            continue
        s = summarise(rows)
        ent = statistics.fmean([r2["final_ent"] for r2 in rows if r2["final_ent"] is not None])
        hr = 1.0 - s["mean"]
        vs = s["mean"] - reactive.get(r, 0)
        print(f"  {r:<16s} {s['mean']:8.4f} {s['sd']:7.4f} {ent:7.3f} {hr:10.4f} {vs:+12.4f}")

    # --- Entropy collapse check ---
    print("\n" + "=" * 70)
    print("7. ENTROPY STABILITY")
    print("=" * 70)
    for r in regimes:
        rows = load_g3(r, "team")
        if not rows:
            continue
        ents = [r2["final_ent"] for r2 in rows if r2["final_ent"] is not None]
        min_ents = [r2["min_ent"] for r2 in rows if r2["min_ent"] is not None]
        print(f"  {r:<16s} final_ent={statistics.fmean(ents):.3f}  "
              f"min_ent={statistics.fmean(min_ents):.3f}  "
              f"collapsed={'YES' if statistics.fmean(min_ents) < 0.1 else 'no'}")

    # --- BC accuracy (from saved model) ---
    print("\n" + "=" * 70)
    print("8. BC ACTOR")
    print("=" * 70)
    bc_path = os.path.join(PROJ, "ml_impl", "bc_actor.pt")
    if os.path.exists(bc_path):
        import torch
        ckpt = torch.load(bc_path, map_location="cpu", weights_only=False)
        print(f"  bc_actor.pt exists ({os.path.getsize(bc_path)/1e6:.1f} MB)")
        if isinstance(ckpt, dict):
            print(f"  keys: {list(ckpt.keys())[:10]}")
    else:
        print("  bc_actor.pt NOT FOUND")

    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
