# Shameless Claims Review (adversarial)

## Summary
Paper makes several strong novelty/feasibility/audit claims. Most are well-hedged in text but several overstate. Biggest blockers: "first" claims bounded only by a self-defined corpus; feasibility certificate only certifies region coverability not policy coverage; credit-assignment diagnosis is speculation; determinism check ignores unshipped scen_old.csv; fault-tolerance asserted not demonstrated.

## Findings

### 1. "First"/novelty claims — SUSPECTED (major)
- File:line `Mlawn-midsem-tex.tex:492` "The central invention of this work is a feasibility-certified evaluation framework"
- Attack: Novelty bounded by "corpus of Table survey/nearmiss" self-defined by authors. No PRISMA. "no paper in corpus" is not "no paper".
- Evidence needed: independent reproducible literature search.

### 2. Feasibility-certified evaluation — SUSPECTED (blocker)
- File:line `Mlawn-midsem-tex.tex:458` "supplies a teleporting placement oracle that certifies the instance is coverable"
- Attack: Oracle certifies region coverability, not that the policy covers. Certificate is a lower bound on N; policy coverage is separate. "certified" overstates.
- Evidence needed: show oracle bound actually attained by some policy on this instance.

### 3. Negative result fairness — SUSPECTED (major)
- File:line `Mlawn-midsem-tex.tex:1753` "trained for 20 episodes, a smaller budget than the proposed method's"
- Attack: Learned arm given 20 episodes vs proposed 80? Hyperparameter search not described. Not compute-matched.
- Evidence needed: compute-matched budget + HPO.

### 4. Attribution gaps — CONFIRMED (major)
- k-fold covering, area-surplus criterion, GxG deficit grid, reward shaping appear adapted from prior work without clear attribution.
- File:line multiple. Evidence: cite originals.

### 5. Claim audit independence — SUSPECTED (blocker)
- File:line claim_audit.py is authors' own script. 38 items self-checked.
- Attack: Not independent. Evidence: third-party audit.

### 6. Determinism 170/170 — SUSPECTED (minor)
- File:line determinism_check.json. scen_old.csv unshipped.
- Attack: Reproducibility claim ignores missing artefact. Evidence: ship scen_old.csv + re-run.

### 7. Fault-tolerant claim — SUSPECTED (blocker)
- Title "Fault-Tolerant" but single failure only; multiple simultaneous failures out of scope (line 1299).
- Attack: Title overclaims. Evidence: multi-failure experiments.

### 8. Credit assignment diagnosis — SUSPECTED (major)
- File:line 221 tokCreditResidual. "consistent with credit assignment" is speculation; per-agent critic difference includes zero.
- Attack: Not supported. Evidence: controlled per-agent advantage study.

### 9. 5.3 dB path-loss spread — SUSPECTED (major)
- Computed from assumption (tx power, etc). Not measured.
- Evidence: field measurement.

### 10. Decorative citations — SUSPECTED (minor)
- Some citations (e.g. basu2004) cited for motivation not support. Need check each.

## Verdict
Multiple blockers. Not acceptable as-is.