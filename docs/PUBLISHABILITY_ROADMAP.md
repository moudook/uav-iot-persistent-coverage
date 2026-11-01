# PUBLISHABILITY ROADMAP - research-level framing
Status: 2026-11-02 03:15. The report (25 pages) is coherent; this is the
plan for making it a submit-able research paper.

## 1. The core contribution, sharpened

The paper's claim is not "MAPPO is better than a rule" (it is, +0.029 on
nominal, resolved) and not "rules beat learning" (false on the corrected
measurement).  It is:

  A certification methodology that separates (i) whether an instance is
  feasible, (ii) whether a controller is broken, and (iii) where learning
  helps.  Demonstrator: 200 episodes of PPO with a sign-flipped entropy
  bonus produce a learner that LOOKS like a failed method (0.674 vs rule
  0.972); corrected, the same method beats the rule on 4 of 6 regimes and
  loses on 2 (small battery, spread start), and the LOSS itself is a
  finding (energy management is the regime where the rule's explicit
  policy beats the learned one).

Reviewers want (a) a crisp formal object, (b) falsifiable protocol
checklist, (c) clean statistical reporting.

## 2. To-do list for paper readiness

A. Formalize:
   - Theorem (packing bound) with proof: N >= K * P(Omega, R_cov), tight
     for the square case; state P = 4 lemma.
   - Definition: certification gap = C* - floor(any feasible controller),
     where C* = oracle. Feasibility certificate excludes C* = 0 cases.
   - Definition of the "zero-shot certificate": a controller is
     *certified on regime r* only if dim(state_r)=dim(state_train);
     otherwise NA (this is exactly what our stress table shows).
B. Protocol checklist (as a short box in Methods):
   [ ] random baseline on the SAME config (found the 0.860 bug)
   [ ] frozen-policy eval (found the train-CK bug)
   [ ] rules reproduce on old seeds (control)
   [ ] held-out scenes disjoint from training (1000+)
   [ ] report kill of sampled vs argmax
C. Stats: we have per-seed CK data. Add bootstrap 95% CIs (10k) for
   each headline difference (learner-vs-rule; ablation +0.093; stress
   diffs). Already do t-CIs; add bootstrap appendix artifact.
D. Add one strong figure: "coverage trajectories" maybe unnecessary; the
   teaser v2 (a/b/c) is the key figure. Keep.
E. Related-work: frame against (i) MORL multi-objective UAS papers, (ii)
   curriculum MARL, (iii) sim-to-real gap papers. 3-5 new refs.
F. Ablation of "value of information": full_obs arm (running) closes the
   question "does the learner need the global state" - if full_obs is
   NOT above ego, the ego observation is sufficient -> stronger claim.
G. Compute-matched fairness: add wall-clock and env-call counts to Table
   tab:remeasured (grid rows deterministic; learner reports seconds).
H. Ablation of training time vs inference: optional.

## 3. Which experiments remain

| experiment | purpose | status |
|---|---|---|
| no_w sweep | movement penalty effect | RUNNING (2/3 seeds) |
| diff2 sweep | credit assignment | RUNNING |
| full_obs sweep | value of information | RUNNING |
| budget 25/50/100/200 | budget curve | 25 done, 50/100/200 RUNNING |
| PPO-local baseline | old table row replacement | scheduled after sweeps |
| action-mask speedup bench | compute claim | scheduled |

## 4. Messaging decision (recorded)

The user's early instruction "emphasise that ML is not performing better"
predated the corrected measurement. The report states the data: learner
ahead on nominal by +0.029 (resolved), behind on 2/6 stress regimes; the
CERTIFICATE is the contribution. The "learning does not help" thesis
survives in the specific regimes (small battery, spread start) and as the
methodological warning (a broken learner looks like a failed method).
