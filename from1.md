Yes — there are three inconsistencies I can verify by arithmetic on the numbers you pasted, plus a handful of code patterns in the excerpts that would explain them. Caveat first: this is a truncated bundle, not the full tree, so I can't do a line-level audit. Everything below is either recomputed from your own artefact values (high confidence) or a suspicion that needs the actual file to confirm.

## 1. Two different "Full" policies claim the same protocol

Both rows say `train_seeds=8, episodes=25, eval_seeds=5, device=cpu`:

- `results_ablation.csv` → CK **0.6740706**, per-seed `0.761365;0.699660;0.633015;…`
- the part-B CSV → CK **0.6622725**, per-seed `0.743950;0.679425;0.671520;…`

No seed value overlaps. That's not RNG jitter — it's two generations of the experiment. The behavioural columns differ too: `MinBattery` 3.43 vs 0.0, `ReturnEvents` 515.8 vs 620.7. Charging behaviour changed, which points at the charger fix rather than nondeterminism.

The damage: your Table XV caption asserts the full row *is* the base comparison's first 8 runs. True for one file, false for the other. And `by = {r["model"]: r for r in abl}` makes duplicates **last-wins silently** — so which Full your yardstick and ΔCK use depends on row order. `no-undercoverage` also appears twice (0.56801 and 0.57697), so duplicates exist within files as well.

## 2. `no-degraded` is bit-identical to Full on two seeds

At the *same seed indices*: seed 2 = `0.633015`, seed 4 = `0.696500`, in both the Full and no-degraded vectors. Two of eight matching to six decimals isn't coincidence. Two candidate mechanisms:

- **The variant didn't take effect** on those runs — a cache keyed by seed without the variant name, or a `--resume` path returning the base policy.
- **`D_t` was identically zero** on those seeds, so `lam_D=0` changes no gradient and training is bitwise identical.

Both mean the same thing for the claim: that component was inactive, so its ΔCK is partly measuring nothing. Which one it is decides whether you have a code bug or an ablation-design bug.

## 3. Mixed sd conventions — verified on four rows

Your ablation CSVs store **population** sd (ddof=0), while the tables and `results_main.csv` use **sample** sd (ddof=1):

| row | CSV `CK_std` | ddof=0 | ddof=1 |
|---|---|---|---|
| Full (0.674) | 0.056517 | **0.056517** | 0.060419 |
| no-arbitration | 0.050852 | **0.050852** | 0.054363 |
| no-undercoverage | 0.119592 | **0.119592** | 0.127849 |

The printed table says `0.577 ± 0.128` — that's ddof=1, recomputed from `per_seed_CK`. So `make_tables.py` is right and the CSV column is wrong. Anything reading `CK_std` directly is ~6.5% low, including `summary.py` and the "worst resolution 0.042" claim.

It's visible in the code too: `yardstick = float(np.std(cks))` (ddof=0) sits next to `_s = float(np.std(_ps, ddof=1))` — same vector, two conventions. You already have a `sample_std` helper; route everything through it.

**Worse, one table mixes axes.** The rule-baseline block does `np.std([x[k] for x in evs])` — that's spread over *5 eval scenes*, ddof=0. The learner's ± is spread over *8 training seeds*, ddof=1. Your prose explicitly says the scene component cancels and the seed component is what's reported. The ± column currently means two different things depending on the row.

## 4. Silent fallbacks that change reported numbers

- **`except Exception: crit = 1.96`** in `fill_tokens.py`. Without scipy, every n=8 interval shrinks from t=2.365 to z=1.96 — about 17% narrower, silently. That's a reported-CI change contingent on the environment. Hard-fail or ship a t-table.
- **`except Exception: print("BC load failed"); training from scratch`**. Training now depends on cwd and whether a checkpoint file exists, not just the seed. This is my first suspect for the 0.744-vs-0.733 reproducibility failure you logged.
- **`device = a.device or ("cuda" if torch.cuda.is_available() else "cpu")`** in eval, while training is pinned to CPU. On any CUDA box, eval moves device and your one-device rule and bitwise-identity claim both break.
- **BLAS pinning lives in the runners.** Direct `python analysis/ab_credit.py` bypasses it. Put it in `uav_wireless/__init__.py` before numpy imports.

## 5. Components ablated where they cannot fire

`Denied = 0.0` in **every row you pasted**. If arbitration never denies a request, `no-arbitration` removes a dead path — the +0.013 is noise, not evidence. Same for reserve: the 3-seed `no-reserve` row is identical to `Full` in *every field*, down to `Distance 9708.266666666666`. Base config has `fail=False`, so the reserve never deploys.

The cheap fix is a diagnostic, not a rerun: **log the mean absolute contribution of each reward term per episode**. Any term sitting at zero makes its ablation a no-op, and you can then say so in the table instead of reporting a null you can't interpret.

## 6. Metric columns that are aliases or censored

- `CK + Ubar = 1.0` exactly, and `CovIntegral == Ubar` exactly, in every row. So CK, Ubar, CovDef and CovIntegral are **one** metric. ΔCK and ΔCovDef are the same number sign-flipped — don't let them read as independent evidence.
- `SC == Kcov_ok` exactly, every row.
- `ProjectionRevisions == UnexecutedActions` exactly, every row.
- `MaxRefresh = 2000.0` in every stress row — pinned at the horizon, so it's right-censored and can't discriminate.
- **`MinBattery` units look inconsistent**: 0.0, 0.78, 3.43, 11.75 in one column across tables. Fraction and kJ are being mixed somewhere.
- `AG` sits at 0.98–1.00 throughout. Saturated.

Net effect: your evaluation is effectively single-metric with a lot of correlated columns.

## 7. Two fairness issues a reviewer will find

- **Budgets don't match.** Learned baselines are at `episodes=20`; the proposed method is at 25. The paper's matched-budget claim doesn't hold as measured.
- **IDQN at ε≈0.91** after 20 episodes is a random policy, not a value-based baseline. The decay is per-episode and tuned for a much longer run. Decay per env step, or set the schedule to land near 0.05 at the reported budget, and report final ε.

Also: observation ablations that change obs dim change network shape and parameter count. "Differs in exactly one component" isn't true there. Mask the field to keep dim constant, or report param counts per arm.

## 8. A training signal worth chasing

`no-undercoverage` per-seed: `0.771, 0.450, 0.590, 0.753, 0.595, 0.469, 0.539, 0.449`. That's bimodal — two basins, not Gaussian noise. A paired t-CI on 8 bimodal seeds is fragile. Worth checking whether the split is "learned to use the pad" vs "didn't", because that's a fixable instability, not a variance floor.

---

A 15-line check that settles findings 1–3 against the real files:

```python
import csv, numpy as np
from pathlib import Path
from collections import defaultdict

for p in sorted(Path("ml_impl").glob("results_*.csv")):
    seen = defaultdict(list)
    for r in csv.DictReader(open(p, encoding="utf-8")):
        v = r.get("per_seed_CK") or r.get("per_seed_ck")
        if not v: continue
        x = np.array([float(t) for t in v.split(";")])
        s = float(r["CK_std"])
        tag = ("ddof=0" if abs(s - x.std()) < 1e-9 else
               "ddof=1" if abs(s - x.std(ddof=1)) < 1e-9 else "MISMATCH")
        print(f"{p.name:38s} {r['model']:20s} {tag}")
        seen[tuple(np.round(x, 6))].append(r["model"])
    for vec, models in seen.items():
        if len(models) > 1:
            print(f"  IDENTICAL VECTORS: {models}")
```

Extend it to compare vectors *across* files at matching seed indices and it'll flag the `no-degraded` collision too.

The structural fix underneath all of this: stamp a hash of (config + protocol + code version) into every row, and make the merge **refuse** to combine rows with different hashes. Right now nothing stops a pre-fix artefact from sitting next to a post-fix one under identical metadata, which is exactly what finding 1 is.

Where do you want to go first — the `no-degraded` collision (I'd want `ablation_part.py` and its cache logic), or the determinism failure (`train_mappo` and the BC-load path)? Those two are the ones that can invalidate claims rather than just shift a decimal.