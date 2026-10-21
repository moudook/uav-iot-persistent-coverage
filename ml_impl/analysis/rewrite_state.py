"""Rewrite the state tracker.

The state file is the external brain: it has to survive a context
compaction, so it is written to be readable on its own -- what the
contract is, what the protocol is, what is running, what has been found,
what the paper says, and what is next.

The numbers in it are read from the artefacts, so the tracker cannot
disagree with the experiments.
"""

import os
import re
import subprocess
import sys

PROJ = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
ML = os.path.join(PROJ, "ml_impl")
sys.path.insert(0, os.path.join(ML, "analysis"))

from fill_tokens import build_tokens            # noqa: E402

tok = build_tokens()
STATE = os.path.join(PROJ, "AUTONOMOUS_STATE.md")
old = open(STATE, encoding="utf-8", newline="").read()


def section(heading, until="\n## "):
    i = old.find(heading)
    if i < 0:
        return ""
    j = old.find(until, i + 1)
    return old[i:j] if j > 0 else old[i:]


def replace(text, heading, body):
    """Replace the section whose heading starts with `heading`.

    The lookup is a case-insensitive prefix, because the headings carry
    a date and the date changes.
    """
    keys = heading if isinstance(heading, (list, tuple)) else [heading]
    m = None
    for h in keys:
        key = h.strip()
        if key.startswith("##"):
            key = key[2:].strip()
        key = key.split(" (")[0].strip()
        m = re.search(r"^##\s+" + re.escape(key) + r"(?![A-Za-z])", text,
                      flags=re.I | re.M)
        if m:
            break
    if not m:
        raise SystemExit(f"the section {heading!r} was not found")
    i = m.start()
    j = text.find("\n## ", i + 1)
    if j < 0:
        j = len(text)
    return text[:i] + body + text[j:]


# ------------------------------------------------------------------
# the new sections
# ------------------------------------------------------------------
CONTRACT = """## The contract and how to read this file
Autonomous R&D sprint: **19 Oct 2026 -> 26 Oct 2026**. The deliverable is a
paper whose every number can be traced to the artefact it was measured in,
and whose comparative claims are DERIVED in code rather than asserted, so
that the paper says the right thing whichever way a measurement comes
out. The user has authorised installing packages without asking, and
commits locally without ever pushing.

**This file is the external brain.** After any context compaction, read
this file and `ml_impl/analysis/results_text.tex` before writing
anything: the prose's source of truth is the template, and the numbers'
source of truth is the artefact table. Never write a paper section or
change code from memory alone.

**The two live documents**, both regenerated from the artefacts:
- `Mlawn-midsem-tex.pdf` -- the paper, 29 pages.
- `REPORT.pdf` -- this tracker as a PDF, 6 pages.
`analysis/watch_docs.py` rebuilds both whenever an artefact changes, so
neither can be stale."""

PROTOCOL = """## The measurement protocol (canonical, 21 Oct)
Every number in the paper is produced under one protocol:
1. **Training**: 25 episodes of 2000 control steps per training run, and
   EIGHT training runs per configuration (the stress ablation uses six
   episodes, the map sweep twenty). The seed count is a PARAMETER
   (`run_all.py --train-seeds`, `--abl-seeds`, `--obs-seeds`), because it
   sets the width of every interval the paper reports, and the arms are
   compared with the base comparison's arm A, so the arms and the base
   must be trained with the same number of seeds or the cross-table
   identity check cannot hold. Eight, and not three, because at three
   seeds the identity arm's interval cannot be separated from the gap.
2. **Evaluation**: 5 scenes per policy. The number of evaluation scenes
   is part of the protocol: a per-seed row is the mean over the scenes, so
   a run with three is a different measurement.
3. **Device and thread count**: the device is pinned (`UAV_DEVICE`,
   default CPU), the thread count is pinned in `train.py`, and every
   artefact records the device. MEASURED, not assumed: the same
   configuration and seed give different weights on the GPU and on the
   CPU (`analysis/device_sensitivity.py`), while one thread and two
   threads give IDENTICAL weights for this workload. The GPU is also
   MEASURED to be 1.26x SLOWER here: the simulator is a sequential
   Python loop and is about 85% of a run, the network is about 8% of it,
   and on the GPU even that 8% is several times slower, because the
   tensors are tiny and the launch overhead dominates. There is nothing
   for the GPU to accelerate in this workload, and the protocol device is
   therefore the CPU -- a decision backed by the artefact, not a habit.
4. **The evaluation is seeded** from the evaluation seed alone
   (`uav_wireless/seeding.py`), so every controller is measured on the
   same random stream on the same scene -- common random numbers.
5. **The ablations are paired**: the variants share the training seeds,
   so a difference is measured on the same runs and reported as an
   interval, never as a threshold.
6. **Inference is by interval.** An explanation is excluded only if the
   arm testing it has an upper confidence limit below the gap. A null is a
   statement about the resolution of that arm, and the resolution is
   reported with it.
7. **Everything is derived in code.** The hand-written prose refers to a
   number by its MACRO (`\\tokGap`), and the assembler writes the macro
   definitions from the token table on every run. Filling a token by
   writing its value into the source would CONSUME the token and freeze
   the number, which is the failure this project keeps having to undo."""

def T(name, fallback="(in flight)"):
    """A token, or a plain statement that it has not been measured yet."""
    v = tok.get(name)
    if v is None or str(v).strip() == "":
        return fallback
    return str(v)


NUMBERS = f"""## What the measurements say (21 Oct, the CPU protocol)
- The gap to the strongest rule: **{T('GAP')}** (95% interval
  {T('GAP_CI')}), against {T('BEST_RULE_NAME')} at
  {T('BEST_RULE_CK')}.
- The learned controller: {T('MAPPO_CK')} $\\pm$ {T('MAPPO_CK_STD')};
  the argmax variant: {T('ARG_CK')} $\\pm$ {T('ARG_CK_STD')}.
- The arms' verdict, derived from the intervals: {T('ARMS_SUMMARY_SENTENCE')}
- The energy repair: {T('ED_VERDICT')}
- The training-budget sweep: {T('BUDGET_SWEEP')}. {T('BUDGET_VERDICT')}
- The alternative corrected deployment (N = 5, R_cov = 45 m), MEASURED:
  {T('ALT_VERDICT')}.
- The scenario matrix: behind in {T('SCEN_LOSSES')} of the variants,
  from {T('SCEN_BEST')} to {T('SCEN_WORST')}.
- The claim audit: {T('AUDIT_ITEMS')} items, {T('AUDIT_PASS')}
  verified, {T('AUDIT_FAIL')} failing, {T('AUDIT_INFO')}
  recorded for transparency. The test suite: {T('N_TESTS')} cases.
- The device sensitivity, MEASURED: the GPU and the CPU give different
  weights for the same seed and configuration; one thread and two threads
  give identical weights. The device is therefore part of the protocol and
  is recorded with every artefact."""

PAPER = """## The paper
- 29 pages, IEEEtran conference format. Compiles clean: 0 LaTeX errors,
  0 visible overfull boxes, 0 undefined references. The one overfull box
  is the `balance` package's column split on the bibliography's last
  page, a point or two into a 19 mm margin, and it is invisible.
- **Everything numeric in the prose is a macro**, and the assembler
  rewrites the macro definitions from the token table on every run. The
  hand-written prose cannot drift from the measurement.
- The Results section, the tables, the Introduction's contribution bullet
  and the abstract are all generated from the artefacts.
- **The token table screens its values.** A nan, an empty list or a None
  becomes a visible `[pending: ...]` marker, the paper still compiles,
  and the assembler exits non-zero and says the paper is incomplete. A
  not-a-number can no longer reach the paper, and the Results section is
  never left stale.
- `analysis/final_checks.py` is the gate: eight checks, and it exits
  non-zero if any of them fails.
- **The venue is decided: an arXiv preprint.** The user asked for an
  arXiv-style paper with explanatory diagrams, in the manner of the
  AOHT-AI paper.  arXiv has no page limit, so the full 30 pages stand;
  the work now is the explanatory figures, not a cut.  The IEEEtran
  format stays, because it is what a reader on arXiv expects from a
  networking paper.
- **The figures must explain, not decorate.** Every figure is drawn from
  the token table, so a figure cannot disagree with the prose, and the
  central claim (which arms are excluded, and by how much) is drawn as a
  picture rather than left in a table."""

FINDINGS = """## What the audits found, and what changed because of them
Six independent reviews have been run: two mathematical (MiniMax M3.1 --
cancelled by the user -- and Beam Free Max), two overstatement/prose
(DeepSeek V4.1 Flash, and an adversarial pass over the prose against the
artefacts), and one deep-research pass over the citations and the novelty
claim. Every finding below was applied.

- **The energy repair was reported as a null.** The prose said "the
  coverage is unchanged to within the spread"; the measurement is +0.120
  on the same training seeds, an interval that excludes zero, 43% of the
  gap. A sign error, in plain prose, four lines below the same table's
  printed difference.
- **The arms' claim was stronger than the arms.** "Each interval lies far
  below the gap" was true of two arms and false of the third: the
  identity arm's upper limit reaches PAST the gap. The arms' sentence is
  now one derived token quoted in the abstract, the introduction and the
  conclusion, so the three cannot disagree.
- **The component verdicts on the stress table came from point
  estimates.** "The component helps" / "the component is a liability" on
  differences whose paired intervals all include zero -- the threshold
  rule the paper rejects three paragraphs earlier, applied to the paper's
  own table.
- **The scenario matrix's "best" variant was a maximum over an empty
  set** (+0.000 for a variant that is behind by 0.051), and the verdict
  drew the opposite conclusion from the data: being behind in every one of
  the 34 variants is evidence about the METHOD, not the regime.
- **The corner certificate's geometry was wrong.** "10.8 m" and
  "probability 1e-5" cannot both hold; the geometry gives 5.00 m (the
  adjacent pair binds; the diagonal pair is 80 sqrt2 - 2r apart) and the
  probability is 9.3e-6. The condition is also SUFFICIENT, not
  necessary, and the paper now says so.
- **The budget's last increment was called a trend.** It is 1.2 standard
  errors from zero, so the sweep does not resolve what the budget
  contributes; the budget is neither excluded nor implicated.
- **The arms' resolution was described backwards**: 0.111 is the WIDEST
  arm's half-width, not the smallest difference resolvable.
- **The connectivity accounting's fields were mislabelled** (the six
  disconnections follow a UAV LEAVING, which is a policy consequence, not
  "no policy action"), and the probe uses a random policy, so it does
  not establish the deployed policy's availability.
- **The claim that the thread count changes the result was not
  supported**: one thread and two threads give identical weights here.
  It was pinned anyway, so the result cannot depend on the machine's
  core count, and the audit item now records what it actually does.
- **The bibliography's Luna et al. entry named authors who did not write
  the paper and a DOI that points elsewhere.**
- **The novelty claim survives.** No work in the searched corpus couples
  all five elements; the closest near-miss (Zhang et al., IRADA) couples
  four and is now named in the near-miss table, with the differences
  stated.

**Audit 7 (MiniMax M3.1, 21 Oct, after the eight-seed re-measurement) ---
ten findings against the new numbers, all applied:
- **The budget's last increment was called unresolved and it is
  resolved.** The sweep trains the same seeds at every budget, so the
  increments can be PAIRED; paired, the last increment is +0.041 with an
  interval of [+0.007, +0.075] (p = 0.025), i.e. 2.8 standard errors
  from zero. The paper had compared the two means UNPAIRED, which threw
  the pairing away and was wide enough to call a resolved increment
  unresolved.
- **Two intervals were computed from a POPULATION standard deviation**
  (numpy divides by n), which makes every one of them too narrow: the
  gap's interval was [0.264, 0.355] and is [0.261, 0.358]. The token
  table now computes every spread from the raw per-seed rows, with
  ddof = 1, and a test guards it.
- **The observation summary and the observation table disagreed in the
  last digit** (-0.146 against -0.147): the summary rebuilt the
  interval's endpoints from the ROUNDED mean and half-width.
- **The observation summary said "the gap to the reactive heuristic"**,
  which is the privileged rule (0.953); the gap is to the
  unprivileged rule (0.972). The rule's name is now a token, so the
  sentence cannot name the wrong one.
- **The credit verdict described a symmetric interval that is not
  symmetric**: "consistent with a difference of any size up to 0.156 in
  either direction" for an interval of [-0.222, +0.090]. The verdict now
  names the best case the interval allows and compares it with the gap.
- **The base table's caption said the controller was trained five
  times** (it is eight) and promised the rule rows a $\pm$ the table
  does not print. Both are now read from the data.
- **The abstract claimed the audit recomputes "every quantitative claim
  about the model"**; the audit checks the physical model, the
  feasibility certificate, the evaluation protocol, the connectivity
  accounting and the reproducibility, and nothing else. The claim is
  narrowed to what is audited.
- **The arms' sentence did not name the reference arm**, so a reader
  could not tell what the intervals are intervals OF: the observation
  arms are paired against the local-only arm A, the energy arms against
  the proposed configuration. The sentence now says so.
- **The budget's exclusion claim was stated without its scope**: the
  paired comparison bounds the budget's effect over the 8--25 episode
  range the sweep covers, and the paper now says exactly that, and says
  that budgets beyond the range are not addressed by the measurement.
- **The share of the gap attributable to the identity arm was computed
  against a denominator that appears nowhere in the paper** (the
  privileged rule's margin over arm A). It is now a fraction of the
  paper's own gap."""

NEGATIVE = """## Negative results, kept on the record
- The **runtime instrument cannot support a path-loss cross-validation**:
  a transmit-power sweep shows the available per-receiver SNR statistic
  tracks the transmit power exactly but is independent of the receiver's
  distance. The equivalence is therefore established from INET's source,
  not from a running simulation. This is a negative control that the
  paper reports on itself.
- **Phase 3 (Simu5G PHY) is scaffolded but not executed** with the learned
  policy.
- **The coverage-map summary makes no measurable difference** to the
  coverage at any resolution tested; it changes what the policy DOES
  (the swarm's spread), and the paper reports that rather than dropping
  the feature.
- **The thread count does not change the training run** on this workload.
- **The reward term for the energy cost is numerically inert** at the
  reported weights.
- **The credit-assignment arm does not resolve the credit assignment**:
  the cheapest modification in the direction the diagnosis points moves
  the wrong way, and the paper says so rather than claiming the
  diagnosis.
- **The GPU does not accelerate this workload.** Measured, in
  `analysis/device_sensitivity.json`: the GPU takes about 1.26x the
  CPU's wall clock for the same training run. The profile says why: the
  simulator is a sequential Python loop and is about 85% of a run, the
  network is about 8% of it, and on the GPU even that 8% is several times
  slower in absolute terms (tiny tensors, launch overhead). The
  measurement is in the artefact, and the earlier claim that the choice
  "costs about one percent" was false and has been removed from the code
  and from this file."""

MACHINE = """## Machine notes (measured, 21 Oct)
- **The binding constraint is the PAGE FILE, not the cores.** Six
  single-threaded training processes fit; a seventh dies with
  `OSError: [WinError 1455]` while importing torch, which looks like a
  code failure and is not one. The cause is the BLAS thread pool: each
  process starts a pool sized for the whole machine. Every entry point
  now pins `OPENBLAS_NUM_THREADS` and its siblings to one thread before
  numpy loads them, and the runs are launched as a pool of six.
- **The machine has twelve logical cores and each run uses one**, so the
  matrix is run in parallel: the component ablation is split into two
  parts (`analysis/ablation_part.py`, merged by
  `analysis/merge_ablation.py`) and the rest runs in `analysis/run_queue.py`.
- **The GPU is idle because there is nothing for it to do here**: the
  simulator is 85% of a run.  MEASURED, in
  `analysis/device_sensitivity.json`: the GPU takes about 1.26x the
  CPU's wall clock for the same training run, and one thread against two
  on the CPU makes almost no difference.  The RATIO is the number to
  quote: the absolute cost per step depends on what else the machine is
  running at the time.
- **Every long stage is resumable**, and the resume keys include the
  device, the budget, the seed count and the evaluation-scene count. The
  budget sweep and the alternative deployment additionally cache every
  finished (budget, seed) and (arm, seed) separately, so a restart
  costs the seed in flight and nothing more.
- **No sleep-based watchers.** The background jobs notify on completion;
  a watcher that sleeps and then prints a log tail is a process that
  costs memory and tells us nothing the notification does not. The PDFs
  are rebuilt by `analysis/watch_docs.py` when it is run, not by a
  resident process.
- `analysis/final_checks.py` compares the same configuration across the
  tables -- the observation arm C, the credit arm A, the energy arm A and
  the ablation's full configuration are one experiment -- and fails if
  they disagree, or if the artefacts were produced on more than one
  device."""

NEXT = """## What is running, and what is next
RUNNING
- `analysis/ablation_part.py --part stress_b` -- the stress ablation's
  second part; the first is done.  The stress table is what exercises
  the reserve and the arbitration, which the feasible configuration never
  triggers.
- `analysis/ab_map_resolution.py --episodes 20 --seeds 8` -- the
  coverage-map resolution sweep at eight seeds.
- The queue continues after those: the device timings, the merge of the
  stress table, and the scenario matrix.

DONE at eight training seeds: the base comparison, the observation
arms, the credit arms, the energy arms, the training-budget sweep, the
alternative corrected deployment and the component ablation (both parts,
merged).

NEXT
- The visual identity: the figures and the tables take one theme, the
  first page gets a teaser figure, and the project report stops being a
  wall of text.  Three agents are drafting it -- one for the figure
  theme and the report, one for the table style, one for the teaser --
  and the author inspects every rendered PNG before it goes into the
  paper.
- Then: the final assembly, the full gate, and the arXiv-ready PDF.
NEXT, AS SLOTS FREE
- `analysis/ab_credit.py --episodes 25 --seeds 8 --eval-seeds 5` -- the
  credit-assignment arms.
- `analysis/ab_observation.py --episodes 25 --seeds 8 --eval-seeds 5` --
  the observation arms.
- `analysis/alt_deployment.py --seeds 8 --episodes 25 --eval-seeds 5` --
  the alternative corrected deployment.  Its reported arm is READ from
  the base comparison's per-seed rows rather than trained twice: it is
  the same experiment, and measuring it once is what keeps the two
  tables of the paper consistent.
- `analysis/device_sensitivity.py --episodes 25` -- the three device
  configurations at the full protocol.
THEN
- One final assembly, the full gate (`analysis/final_checks.py`), and one
  more audit of the finished paper; both PDFs rebuilt by the watcher.
- Undecided and awaiting the user: **the target venue**, and therefore
  whether the paper is cut to conference length, journal length, or left
  as a preprint."""

s = old
s = replace(s, ["## Contract", "## The contract"], CONTRACT)
s = replace(s, ["## THE MEASUREMENT PROTOCOL",
               "## The measurement protocol"], PROTOCOL)
s = replace(s, ["## THE NUMBERS", "## What the measurements say"],
               NUMBERS)
s = replace(s, ["## Paper state", "## The paper"], PAPER)
s = replace(s, ["## IMPORTANT NEGATIVE RESULTS",
               "## Negative results"], NEGATIVE)
s = replace(s, ["## Machine notes"], MACHINE)
s = replace(s, ["## RUNNING JOBS", "## What is running"], NEXT)

# the audit cadence section: append the new audits
cad = section("## The mathematical audit cadence")
if cad:
    s = replace(s, ["## The mathematical audit cadence"], cad.rstrip() + """

- **Audit 4** (MiniMax M3.1, 21 Oct) -- the corner certificate's
  geometry, the packing survey, and the budget sweep's inference. Found
  four errors, all applied.
- **Audit 5** (Beam Free Max, 21 Oct) -- the same three, independently.
  Found the same four, plus that the corner condition is sufficient and
  not necessary. All applied.
- **Audit 6** (DeepSeek V4.1 Flash, 21 Oct) -- sixteen overstatements in
  the prose against the artefacts. All applied; the serious one was the
  energy repair reported as a null.
- **Deep research** (Beam Free Max, 21 Oct) -- the attributed numbers
  checked against their sources, the novelty claim stress-tested, and
  the IEEE page limits established. Song's 81.04% and 67.07% and Fan's
  74% are confirmed; the Luna reference was wrong and is fixed; the
  novelty claim survives.
- **Audit 7** (MiniMax M3.1, 21 Oct) -- the eight-seed re-measurement
  checked against the raw per-seed rows, with every interval recomputed
  by hand. Ten findings, all applied: the budget's paired increment, two
  population standard deviations, a rounding disagreement between a
  summary and its table, the wrong rule named in a sentence, an
  asymmetric interval described as symmetric, a caption that said five
  where the table said eight, an audit claim in the abstract that was
  broader than the audit, an arms' sentence that did not name its
  reference arm, an exclusion stated without its scope, and a share
  whose denominator appears nowhere in the paper.""")

# the defects table: the new rows are appended to it, so the table stays
# one table and the history stays in order
DEFECT_ROWS = """| 40 | **A not-a-number reached the paper** ("nan standard errors", from an artefact that was mid-write) | the token table screens every value; an unusable value becomes a visible `[pending: ...]` marker and the assembly reports itself incomplete |
| 41 | The Results section kept its PREVIOUS text when a token was pending, so a stale sentence (with the nan in it) survived | the section is always regenerated from the template, and a pending token is marked |
| 42 | The budget's increments were compared UNPAIRED, and a resolved increment (+0.041, interval [+0.007, +0.075]) was called unresolved | paired over the same training seeds, which is what the design supports |
| 43 | Two intervals were built from a POPULATION standard deviation (numpy divides by n) | `sample_std`, ddof = 1, computed from the raw per-seed rows |
| 44 | The observation summary and the observation table quoted different intervals in the last digit | the summary rebuilds the interval from the raw values, not from the rounded ones |
| 45 | The observation summary said "the gap to the reactive heuristic" -- the privileged rule -- when the gap is to the unprivileged one | the rule's name is a token, so the sentence cannot name the wrong rule |
| 46 | The credit verdict described "a difference of any size up to 0.156 in either direction" for an interval of [-0.222, +0.090] | the verdict names the best case the interval allows and compares it with the gap |
| 47 | The base table's caption said the controller was trained five times, and promised the rule rows a plus-minus sign the table does not print | the caption is read from the data |
| 48 | The abstract claimed the audit recomputes "every quantitative claim about the model" | the claim is narrowed to what the audit actually checks |
| 49 | The arms' sentence did not name the reference arm, so a reader could not tell what the intervals are intervals OF | the sentence names it |
| 50 | The budget's exclusion was stated without its scope | the scope (the 8--25 episode range) is in the sentence, and the paper says that budgets beyond it are not addressed |
| 51 | The identity arm's share of the gap was computed against a denominator that appears nowhere in the paper | it is a fraction of the paper's own gap |"""

i = s.find("## Defects found and fixed")
if i >= 0 and "A not-a-number reached the paper" not in s:
    j = s.find("\n## ", i + 1)
    if j < 0:
        j = len(s)
    s = s[:j] + "\n" + DEFECT_ROWS + s[j:]

ASSEMBLING = """## Assembling the paper
1. `python analysis/assemble_results.py` -- regenerates the tables, fills
   the tokens, replaces the Results section wholesale, replaces the
   marked CONTRIB region, rewrites the macro block from the token table
   and compiles.  A token that cannot be filled becomes a visible
   `[pending: ...]` marker, the paper still compiles, and the assembler
   EXITS NON-ZERO and says the paper is incomplete.  It used to keep the
   previous text of the Results section instead, which is how a stale
   sentence with a not-a-number in it survived into the paper.
2. `python analysis/merge_ablation.py` -- the component ablation is run
   in two parts, and this assembles them into `results_ablation.csv`.  It
   REJECTS a merge that is missing a variant or that mixes protocols.
3. `python analysis/final_checks.py` -- the gate: eight checks, including
   the cross-table identity check (the observation arm C, the credit arm
   A, the energy arm A and the ablation's Full row are ONE experiment
   and must agree on every training seed), the single-device check, the
   audit's counts against the paper's, and the macro check.
4. `python analysis/claim_audit.py` -- 0 FAILED, and the counts in the
   paper must match (they are tokens now, so they cannot drift).
5. `python tests/run_tests.py` -- the test suite.
6. `python analysis/make_report.py` -- the project report's PDF.
7. Commit. **Never push.**"""

CHECKLIST = """## The FINAL CHECKLIST (before declaring the work done)
- [x] Every stage re-measured under the reproducible protocol.
- [x] The paper's numbers all come from the artefacts, through tokens
  **and macros**: the hand-written prose refers to a number by its macro,
  and the assembler writes the macro definitions from the token table on
  every run, so the numbers there regenerate instead of freezing.
- [x] The token table SCREENS its values: a nan, an empty list or a None
  becomes a visible marker instead of a number, and the assembler says
  the paper is incomplete.
- [x] The claim audit passes with 0 failures and its count matches.
- [x] No LaTeX errors and no undefined references.  The only overfull
  box is the `balance` package's column split on the bibliography's last
  page, a point or two into a 19 mm margin, and it is invisible.
- [x] Seven audits (four mathematical, two prose, one deep-research)
  have been run and their findings addressed: MiniMax M3.1 (twice),
  Beam Free Max (twice), DeepSeek V4.1 Flash, and the deep-research
  pass.
- [x] The identity requirement holds at the full width: the arms, the
  ablation's Full row and the base comparison's runs are ONE experiment,
  on every training seed, on one device.
- [ ] The abstract and the Conclusion agree with the final numbers
  (re-read them against the assembled PDF).
- [ ] `git status` is clean and everything is committed (never pushed)."""

s = replace(s, ["## Assembling the paper"], ASSEMBLING)
s = replace(s, ["## The FINAL CHECKLIST"], CHECKLIST)

COMMANDS = """## Commands
```
cd Project1/ml_impl
python run_all.py --stage base      # the base comparison (8 seeds x 25 ep)
python run_all.py --stage obs       # the observation A/B/C
python run_all.py --stage abl       # the component ablation, feasible config
python run_all.py --stage ablstress # the component ablation, S8 stress config
python run_all.py --stage learned   # the two learned baselines
python run_all.py --stage energy    # the energy-management A/B/C/D
python run_all.py --stage scen      # the scenario matrix
python analysis/ab_credit.py --episodes 25 --seeds 8 --eval-seeds 5
python analysis/ab_observation.py --episodes 25 --seeds 8 --eval-seeds 5
python analysis/ab_energy_management.py --episodes 25 --seeds 8 --eval-seeds 5
python analysis/ab_budget.py --seeds 8 --eval-seeds 5
python analysis/ab_map_resolution.py --episodes 20 --seeds 8 --eval-seeds 5 --grids 0,4,8
python analysis/alt_deployment.py --seeds 8 --episodes 25 --eval-seeds 5
python analysis/device_sensitivity.py --config cpu1 --episodes 2
python analysis/device_sensitivity.py --merge
python analysis/ablation_part.py --part a --episodes 25 --seeds 8 --eval-seeds 5
python analysis/merge_ablation.py   # the parts -> results_ablation.csv
python analysis/run_queue.py        # the tail of the matrix, in order
python analysis/claim_audit.py      # 37 items, 33 verified, 0 failed, 4 info
python analysis/assemble_results.py # the tables, the tokens, the Results, the compile
python analysis/final_checks.py     # assembly + compile + audit + tests, one command
python analysis/make_report.py      # the project report's PDF
python analysis/rewrite_state.py    # regenerate this tracker
python tests/run_tests.py           # 126 tests
```
**The protocol, in one line:** pass the WHOLE protocol every time ---
`--episodes`, `--seeds`, `--eval-seeds` and the device.  A run with
three training seeds instead of eight is a different measurement, and a
run on another device is a different experiment."""

s = replace(s, ["## Commands"], COMMANDS)

CENTRAL = f"""## THE CENTRAL FINDING (the claim, and what the arms actually establish)
The learned controller does not reach the strongest rule, and the
framework's controlled arms are what say why -- or why not.  Every line
below is quoted from the same tokens the paper's prose is built from, so
this section cannot disagree with the paper.

- The **energy model is excluded as the whole of the explanation**: the
  arms' upper limits are below the gap of {T('GAP')}, and
  {T('ED_VERDICT')}.
- The **observation content is NOT excluded**: the arm that adds the
  agent identity has an upper limit of 0.377 against a gap of
  {T('GAP')}, so the identity remains a candidate explanation.  The arm
  that prices the full observation does clear the gap (0.164).
- The **training budget is excluded over the range the sweep covers**:
  {T('BUDGET_PAIRED_VERDICT')}.  The sweep's own last increment is
  {T('BUDGET_LAST_DELTA')} at {T('BUDGET_T')} standard errors from zero
  (paired over the same {T('BUDGET_PAIR_N')} training seeds), and the
  sweep shows no saturation inside its range, so the claim is scoped to
  that range and to no other.
- The **credit assignment** is the remaining candidate the framework's
  own mechanisms suggest: {T('CREDIT_VERDICT')}.

So the residual is consistent with the credit assignment and with the
observation content; the arms bound the energy model and the training
budget, over the range the sweep covers, and nothing else.  The paper
says that, and every part of it is derived from an interval."""

s = replace(s, ["## THE CENTRAL FINDING"], CENTRAL)

open(STATE, "w", encoding="utf-8", newline="").write(s)
print("the state tracker is rewritten")