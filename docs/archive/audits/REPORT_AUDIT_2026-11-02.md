# REPORT AUDIT - gaps, stale numbers, and the experiment plan
Date: 2026-11-02 00:40. Companion to docs/MEASURED_NUMBERS.md.
Source of truth: the 34-page PDF (docs/PDF_TEXT.txt) and Mlawn-midsem-tex.tex.

## 1. CURRENT HEADLINE (what the report now claims, and what supports it)

| claim | number | artefact | status |
|---|---|---|---|
| learner (ego+shape) vs best rule | 0.9522 vs 0.9233, diff +0.0289, 95% CI [+0.0159, +0.0420] | runs/exp_ego_eval/eval_heldout.json | resolved, supported |
| bug-fix-only learner | 0.8594 (95% CI [0.8363, 0.8825]) | runs/bugfix_eval/ | supported |
| observation/shaping ablation | +0.0928 | same two runs | resolved |
| rules reproduce pre-correction table | Fixed 0.371/0.784/0.953/0.972 over scenes 0-4 | runs/rules/eval_rules.json | control passed |
| random baseline | 0.5612 (20 held-out scenes) | runs/diag/random_baseline.json | supported |
| network not binding | PDR ~0.998, range margin 22x | Simulation/omnet_uav2/* | supported, old |
| feasibility certificate | N>=4K tight at these params | math, checked | supported |

## 2. STALE / OLD NUMBERS STILL IN THE PDF (from stale_lines.txt scan)

All are in the two top sections and in the boxed superseded Results section.

A. The pre-correction narrative in the INTRO (lines ~94-180):
   - "sigma = 1.503 ... 0.674" (teaser panel a)
   - "gap 0.298" (teaser panel c, lines 97, 110, 180)
   - "outperforms ... by 0.298" (line 180)
   These are inside the teaser figure caption and the contributions list. The
   teaser is the FIRST thing a reader sees; it still shows the OLD gap.
   DECISION: regenerate the teaser from the new macros (make_teaser.py reads
   tokens, but the figure's panels carry hardcoded 0.298/0.674 in coordinates;
   update the figure generator).

B. alt-deployment macro \tokAltReportedCk = 0.674 (line 679): "0.757 against
   0.674" — that claim is from the buggy learner, on a different deployment.
   DECISION: either retract explicitly or delete the alt-deployment paragraph
   until re-run under the fixed protocol.

C. The boxed superseded Results section (lines 1501-2346) still contains the
   whole old ablation apparatus keyed to 0.674 and 0.298. This is intentional
   (kept as record) but occupies ~9 pages of the 34. Two options:
   (i) keep as an appendix-like record with a clear banner (current);
   (ii) compress to a 1-paragraph summary + pointer to the re-measurement,
        and REPLACE the ablation tables with re-run numbers under the fixed
        learner. Option (ii) is what a reviewer wants: the paper's actual
        evidence base should be the corrected one.
   DECISION: run the corrected ablations (Section 4 below), then replace the
   superseded section by a compact "pre-correction record" subsection.

D. Budget sweep (lines 1607-1643): 8/16/25-episode numbers (0.588/0.624/
   0.674) are from the buggy learner. The "budget is excluded" conclusion was
   about the buggy learner. DECISION: re-run the sweep with the fixed learner
   at 25/50/100/200 episodes (5 seeds each) to re-establish or drop the
   claim. This is cheap-ish and directly testable.

E. Credit section (lines 2057-2069): local-critic arm 0.639 vs 0.674; the
   verdict "not resolved... worst case 0.079 worse" was against the buggy
   learner. Re-run with diff-reward flag already implemented; this is one of
   the SI-1/SI-2 knobs.
   DECISION: re-run credit arm (team vs diff, 3-5 seeds) under fixed learner.

F. Stress regimes claims (in the now-replaced sprint paragraph of the old
   version): "stress prevents collapse, CK 0.44 -> 0.615 (single_pad)",
   "C3 not significant p=0.66", "residual MAPPO collapses to 0.4500",
   "headroom gate passes all five regimes". These were measured under the
   OLD learner and are NOT in the new section (they were in the old sprint
   paragraph which I replaced). Check whether they still appear anywhere:
   search PDF for "0.615", "0.4500", "0.44" -> if they appear outside the
   superseded record, they must go or be re-run.
   DECISION: they are superseded; the stress_eval run (in flight) will
   produce FRESH stress numbers under the corrected learner, which replace
   these.

G. "The 0.860 random baseline" is fully gone (1 occurrence found, which is
   in the retraction sentence - good).

H. Historical comparison numbers (IDDQN 0.381, Masked PPO 0.625) in
   tab:results_main are from the buggy learner too; they stay in the record
   table but are meaningless as baseline claims. They are inside the
   superseded section, so acceptable with the banner; if we re-run the
   comparison table (section 4), replace them.

## 3. STRUCTURAL ISSUES (confusion risks flagged by the user's "one sentence can confuse")

1. The abstract now says the learner is AHEAD (+0.029). The old Results
   section says the learner LOSES by 0.298. The box explains it, but the
   conflict is a reviewer red flag unless the superseded section is
   compressed and clearly dated. Prefer: a single "History of this
   measurement" short subsection (1 paragraph + pointer table) instead of 9
   pages of old results.
2. The teaser figures still depict the old gap. Must regenerate.
3. Section numbering / cross-refs: sec:second_sprint label is used from the
   abstract and supersession box; fine. Table tab:remeasured is referenced
   from the new section and the box; fine.
4. The thesis statement appears twice ("certifying where learning does not
   help" x2 in older paragraphs; now deduped - verify).
5. Headroom gate: on held-out scenes, best rule = 0.923, so ceiling - best
   rule = 0.077 < 0.10 on nominal. The old sprint text claimed all stress
   regimes pass the gate. With held-out scenes this needs recomputation per
   regime (stress eval in flight). The gate definition must be stated per
   regime and the nominal case reported honestly (0.077, fails) or the gate
   re-derived. Do not fudge: report actual numbers.
6. "5 seeds" claims in old sections vs the new 5-seed runs: consistent now.

## 4. EXPERIMENT PLAN (ordered by cost/value; each run saves .pt + eval)

RQ  "what makes the learner win now" already partial: +0.093 from obs/
    shaping. Remaining knobs to sweep (3-5 seeds each, 200 ep):
    1. W_t penalty OFF (config exists: --no-w)  [already one seed; extend to 5]
    2. dist_shape_kappa: 0.1 / 0.3 / 1.0 (currently 0.5)
    3. n_ego: 5 (currently 3)
    4. credit diff rewards beta: 0.5 / 2.0 (code exists)
    5. randomize_layout on (currently off) — generalization knob
    6. action repeat: not implemented; skip unless time allows (implementation
       cost high, speedup 4x, but changes dynamics; keep as future work)
    7. Entropy coef / lr grid: optional, only if plateau persists.

RQ  "does the learner generalize to other regimes" - stress_eval in flight.
    If zero-shot fails on some regime, that becomes a headline negative
    result: learning helps on nominal, NOT on stress; the certificate says
    which regime is even feasible. That is the publishable "where learning
    does not help" story. If the learner wins everywhere, story flips to
    "learning beats tuned rules once correctly trained" - also publishable.

RQ  budget sweep re-run (25/50/100/200 ep, 5 seeds, fixed learner).

RQ  credit arm re-run (team vs diff, 3-5 seeds).

RQ  comparison-table re-run: full tab:results_main under fixed learner (5
    seeds) - IDDQN/MaskedPPO/argmax rows + rules, we can produce with 5
    more trainings of the local-critic config and argmax eval from existing
    checkpoints. IDDQN would need new code; likely drop IDDQN row and say
    "state-of-the-art MAPPO variants" instead of reproducing published DQN.
    Decision: drop IDDQN (it was a reproduction claim we cannot defend),
    keep Masked PPO local-critic (re-run), keep argmax (eval only).

RQ  A proper confidence/effect-size analysis: bootstrap or t-based CIs for
    all pairwise differences (rliable-style). Add to the tables.

RQ  The "action mask speedup" (SI-1) - if we claim any compute, we should
    measure it: bench action_mask fast path vs current. It is a 20-line
    change; measure on 5 episodes; report wall-time per step.

## 5. PUBLISHABILITY / NOVELTY POSITIONING (research-level target)

Current centrepiece: feasibility-certified evaluation framework (C4) +
  corrected protocol narrative. The story reads honest but the novelty is
  methodological, not algorithmic. To reach "research-level publishable":

A. Add a crisp formal statement: "certification gap" = (ceiling - best any
   policy that satisfies the invariants). Show how the certificate bounds
   what any learner can achieve and separates feasibility from controller
   quality. Formalize the packing bound and the oracle in theorem/lemma
   form with proofs (we already have the math; it needs a theorem
   environment instead of prose).
B. Add the negative-control methodology as a *contribution*: a checklist for
   "is the learner broken or is the task hard" with falsifiable tests
   (random baseline on the SAME config, frozen-policy eval, rule
   reproduction check). That is a transferable evaluation protocol — a
   methodological contribution reviewers can cite.
C. The INET network certificate is a nice second pillar: present it as a
   composable certificate (network does not bind at 80 m; geometry/energy
   do). Keep the PDR + margin + contention evidence.
D. One algorithmic knob that would raise the ceiling: allow the learner to
   act at a coarser timescale (action repeat 4-10) to cut the number of
   decisions and make the task easier, then re-evaluate. If it pushes the
   learner toward the oracle, that is a genuine algorithmic result.
E. Consider adding an upper-bound experiment: run the learner with oracle
   teleporting replaced by the learned policy but with ideal observation
   (full state) to measure the value of information; that directly measures
   "how much of the residual gap is observation content". This is exactly
   the old obs arm but under the fixed learner (one re-run).
F. Add a "compute-matched" comparison to answer the fairness concern: rule
   gets no compute; learner gets 200 episodes. Report both the budget and
   the wall time; maybe add a "same wall-clock" ablation (rule evaluated
   under the same random seeds with the same number of environment calls).
G. Statistical hygiene: for each pairwise headline difference, report the
   t 95% CI AND a bootstrap CI (10k resamples) with the seed-level data
   available in the artifacts; rliable-style reporting of per-seed scores.

DECISION on messaging (interim): the user's instruction "emphasise that ML
is not performing better" predates the corrected measurements. The data now
say the opposite on nominal (learner +0.029). The report must NOT claim the
learner loses; it must claim the corrected comparison is the point. On
stress, the story may return to "learning does not help" - the stress eval
will decide. This is a facts-over-instructions case and the report will say
what the data say.

## 6. FILE / SANITY CHECKS TO RUN AFTER EVERY EXPERIMENT

- scripts/make_midsem_numbers.py must run with zero NaN in CIs for any tag
  that is cited (n>=2).
- grep PDF for every dead number after regeneration: 0.674, 0.298, 0.860,
  0.749, 0.926 should appear ONLY in retraction/supersession sentences.
- pdflatex must compile 0 errors.
- All headline numbers must trace to an artefact path listed in
  MEASURED_NUMBERS.md.
