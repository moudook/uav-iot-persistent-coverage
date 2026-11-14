# Persistent K-coverage by a UAV fleet

This repository contains the simulator, the MAPPO learner, the evaluation and
verification pipeline, the OMNeT++ co-simulation assets, and the end-semester
report.

## Active deliverable

- `endsem-report.pdf` - the 8-page report.
- `endsem-report.tex` - its source. Do not edit reported numbers by hand;
  they are checked against stored artifacts.

## Layout

- `ml_impl/uav_wireless/` - environment, MAPPO learner, training loop, seeds.
- `ml_impl/analysis/` - claim audit, table/token generation, ablation producers.
- `ml_impl/tests/` - 158 regression tests.
- `ml_impl/runs/` - stored evidence. The headline is `exp_ego_fixed`; the
  second-generation retrain is `exp_v2` (experimental, not promoted; see
  `docs/archive/audits/V2_REVIEW_ATTEMPT_2026-11-15.md`). `rules_heldout`,
  `stress_eval`, `exp_ego_eval`, `exp_distilled20`, and `budget_ep*` support
  the report.
- `scripts/` - training, evaluation, planning, distillation, energy certificate,
  report verifier, review bundler, and OMNeT trace export.
- `Simulation/` - OMNeT++/INET configuration, traces, and results.
- `docs/` - active environment notes; `docs/archive/` holds prior papers,
  audits, reviews, and research notes.
- `DEMO_GUIDE.md` - commands for the energy certificate, audit, and INET demo.

## Verification

```powershell
$env:PYTHONPATH = "ml_impl"
python -m pytest ml_impl/tests -q
python scripts/verify_report_numbers.py
python ml_impl/analysis/claim_audit.py
```

`scripts/verify_report_numbers.py` recomputes every number printed in the
report from its owning artifact. A change that breaks it is a regression.

## Training and evaluation

```powershell
python scripts/run_exp.py --seeds 0 --episodes 200 --n-steps 2000 `
  --ego --phy-ego --anchor --assist-return --scalable-id --no-agent-id `
  --shape 0.5 --credit-mode diff --per-agent-adv --randomize-layout `
  --eval-seeds 20 --eval-offset 1000 --tag exp_v2 --device cpu

python scripts/eval_ckpt.py --tag exp_v2 --eval-offset 1000 --eval-seeds 20
python scripts/eval_stress.py --tag exp_v2 --out ml_impl/runs/stress_eval/stress_eval_v2.json
python scripts/finalize_headline.py --tag exp_v2
```

## History

The pre-cleanup state is preserved by the git tag
`pre-cleanup-2026-11-15`. The verified first-generation headline is preserved
by `v1-final-verified-2026-11-14`.
