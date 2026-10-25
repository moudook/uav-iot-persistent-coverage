# Parent audit — verified findings (not delegated)

Everything here was reproduced by the orchestrator with the command shown.
Reviewer claims that could not be reproduced are quarantined at the bottom.

---

## P1 — BLOCKER — The paper's central promise is broken at ~2/3 scale

The paper states that every number is emitted by `fill_tokens.py` and that
comparative claims are derived in code. Measured, not estimated:

- macros defined in the generated block: **357** (lines 88–444)
- macros actually used in the body: **87**
- of those 87, how many are bare numbers: **70**
- claim-bearing decimal literals typed directly into prose: **~130**
  (224 decimal literals outside `$...$` in prose lines, minus ~90 that are
  TikZ style parameters, software versions, and bibliography identifiers)

So roughly two thirds of the numbers a reader sees are **not** derived from an
artefact, and the gate cannot see them because the gate only checks macros that
exist. This is the structural reason a stale number can survive a passing gate.

Reproduce: `python` scan of body lines 445+ for `\d+\.\d+` outside `$...$`,
excluding lines containing `coordinates {`, `axis cs`, `xmin=`, `ytick`.

Note the inversion this exposes: **270 macros are defined and unused while ~130
literals are hand-typed.** The prose was largely written against literals and the
derivations were generated but never wired in. That makes the repair mechanical
(replace literal with the already-computed macro) rather than a rewrite.

---

## P2 — BLOCKER — Five stale-number sets confirmed by exact match (not suspected)

Each prose literal below was matched against a pre-charger-fix artefact to 3 d.p.
These numbers are wrong now and will still be wrong after the arms are re-run,
because nothing regenerates a literal.

| # | prose site | literal(s) | artefact it matches | status |
|---|---|---|---|---|
| a | line 2145 | `G=0: 0.640, G=4: 0.643, G=8: 0.651` | `ab_map_resolution.json` CK 0.639813 / 0.642891 / 0.651165 | stale, exact |
| b | lines 2492, 2507 | `-0.022`, interval `[-0.080, +0.036]` | `ab_credit.stale-precharger.json` A 0.662272 − B 0.640536 = **−0.021737** | stale, exact |
| c | line 2286 | `+0.023`, `-0.001`, `-0.078` | `ab_energy_management.stale-precharger.json` deltas vs arm A: **+0.0230 / −0.0006 / −0.0779** | stale, exact |
| d | lines 1902, 2365, 2366 | `8 episodes: 0.595, 16: 0.621, 25: 0.662` | `0.662` equals the stale arm-A CK **0.662272**; current budget run gives 16 → **0.624**, and 25 → 0.761/0.700 on the two seeds finished so far | stale, exact for 0.662 |
| e | line 2143 | `distinct actions 1.84 → 2.43` | arm A measures **1.84** (confirmed in `q6_obs.log`); arm B currently 1.97/2.48/2.96/1.85 over seeds 0–3, so 2.43 is not yet reproducible | pending arm C |

Reproduce: the table above was produced by loading each stale JSON and applying
the paper's own stated statistic (mean over 8 training seeds, rounded to 3 d.p.).

Consequence for the writing: (a)–(d) must be re-derived after the re-runs, and
the only way they stay correct is if they become macros. Fixing P2 without
fixing P1 just resets the same trap.

---

## P3 — MAJOR — One dropped clause, uniquely localised

`Mlawn-midsem-tex.tex:2147`:

    The observation terms are priced individually in the table above  The reason is easy to see in
    retrospect.  Without a direction to the charger a UAV cannot come home, ...

A sentence was deleted mid-paragraph and the join was never repaired: no full
stop, and a double space. The body contains **exactly one** instance of a
double space not preceded by sentence-ending punctuation, so this is the only
defect of its class.

Reproduce: regex `[a-zA-Z,]  +[A-Z]` over body lines, excluding `&`/command lines
— one hit, line 2147.

---

## P4 — CORRECTION TO MY OWN RECORD

My earlier note said "87 of 373 macros used". The denominator was wrong: the
generated block defines **357** macros, not 373. Reviewer A caught this and I
reproduced it. The 87 numerator was right. Recording it so the number does not
propagate further.

---

## P5 — Quarantined reviewer claims (could not be reproduced)

- Reviewer A, finding #2 and #8 ("hand-typed decimals in abstract/intro",
  marked `SUSPECTED`): directionally correct but never enumerated; the claim as
  written had no line numbers, so it was not used. The enumeration was done by
  the orchestrator instead and is P1/P2 above.
- A false positive from my own first scan: lines 2682–2754 appeared to contain
  empty `~dB` holes. They do not — the scanner had stripped `$+43.2$` inline
  math. The SNR figures are present and intact.

---

## Proposed repair order (depends on the arm re-runs, not on each other)

1. Wait for `ab_observation` (arm C), `ab_credit`, `ab_energy_management`,
   `ab_map_resolution` to finish; then `fill_tokens.py` re-derives everything.
2. Add a ninth gate check: any claim-bearing decimal literal in prose that is not
   in an explicit whitelist of protocol constants **fails** the build. Without
   this, P2 recurs by construction.
3. Wire the ~130 literals to macros — most already exist among the 270 unused.
4. Repair the P3 join.
