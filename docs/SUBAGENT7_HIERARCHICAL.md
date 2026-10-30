# Subagent 7 - Hierarchical RL / Options (first-principles, 2026-10-30)

From ses_e76ee63e6ffeb4p3quDjz5x8Wm (Mercury 3, read-only).

## Reframed problem
Learned MARL must beat handwritten reactive rule on CK (0.74/0.716) without collapsing. Central paradox: decisions that matter (when to leave coverage, target which deficit, when to return) are long-horizon and coupled to per-step motor choice, so flat PPO drowns sparse return signal in 2000 noisy primitive actions.

## Ground truths
- Env already runs a hard mode machine (0 serve / 1 return / 2 charge, env.py L198, L1138-1142) and rule's modes are exactly these: cover, return, charge (train.py L391-416). Threshold = pad_energy + E_reserve (L483) [FACT: code].
- Observations already expose mode, pad bearing, 4x4 deficit map, charging wait, agent id (L873-963). Actions are 6 primitives; no macros [FACT: code].
- C3 credit null; residual PPO (BC init) smokes at 0.792 then collapse risk; BC alone reaches 0.8-0.98 [FACT: docs/FINDINGS.md].

## Constraint ledger (decisive rows)
- Rule's mode structure is a fence: it separates deploy/refuel/idle sensibly. Keep it; attack only transitions.
- Rule is greedy-Markovian: returns at fixed energy threshold regardless of pad contention (2 pads, 8 UAVs), failures, future deficits. This is exploitable headroom [ASSUMPTION: untested, low cost to test].

## Representation shift
Compress time. Replace "policy over 6 primitives at every step" with policy over 3 options chosen at SMDP decision points, each option executed by frozen intra-option skill. Splits Dec-POMDP into learnable high level (mode timing/targeting) and low level (motor skills) that is NOT fine-tuned - sidestepping PPO-collapse entirely.

## Portfolio (mechanisms)
1. HIGH-LEVEL ONLY (best bet): freeze rule's own cover/return/charge movement code as options; train only MAPPO option-selector (3 actions, CTDE, existing centralized critic, existing masks/seeding, warm-started from rule's transition policy). Isolates "can learned transitions beat hand-coded ones?" - sharpest falsifiable question. Prior art: option-critic (Sutton 1999), DOC (AAMAS 2020), MADDPOC (arXiv:2112.10630, UAV charging, continuous low-level; differs: we freeze discrete low-level and benchmark vs handwritten rule).
2. BC-SKILLS (high-variance): swap low-level skills for existing BC actor (0.8-0.98 evidence) - only after (1) proves transitions matter.
3. Threshold-sweep probe (cheap): sweep E_reserve/deferral on rule; bounds greedy-timing headroom before any training.

## Why it should work
(a) Options compress 2000-step credit to ~20-50 option decisions - return event's advantage attaches to one logit instead of 300 smeared primitives; (b) peer non-stationarity absorbed at option boundaries (high level sees modes directly); (c) frozen BC skills preserve proven >0.8 low level, so PPO never touches what works; (d) env already ships every high-level signal selector needs.

## TEST
H: learned option transitions beat rule's threshold transitions. Minimal: option-wrapper around baseline_reactive internals + 3-action high-level MAPPO; same 200ep x 2000 steps x 5 seeds, both regimes, seeded eval. Success: paired mean CK gain > +0.02 (95% CI excluding 0) both regimes, no collapse.

## RECOMMENDATION
Run (1) first: frozen rule-skills + learned MAPPO option-selector. Reuses existing baseline/runtime code, one extra small policy, identical budget. If wins, upgrade skills via (2); if threshold sweep (3) already caps rule, proceed with (1) anyway - learned transitions can anticipate, not just re-threshold.

## TEST
Implement option_selector (3 logits) over frozen rule-skill options; warm-start from rule's own mode-flip policy; MAPPO at SMDP level with existing critic/masks; paired 5-seed eval vs rule on single_pad and small_battery.

## KILL RULE
If mean CK(selector) - CK(rule) <= +0.02 with paired CI spanning 0 on both regimes after 200 episodes, or entropy -> 0 / CK < 0.5 in last-10 on >=2/5 seeds, hierarchy in this form does not rescue: kill this angle (keep BC-residual separate).

## CONFIDENCE
Options compress credit and improve sample efficiency: [reasoned, sourced - Sutton 1999; DOC; MADDPOC]. Learned transitions beating greedy threshold: [speculative - precisely what TEST measures]. BC-as-skill quality: [FACT: docs, eval-mode confound unresolved]. PPO collapse is low-level, avoidable by freezing: [hypothesis; residual smoke 0.792 consistent]. Env supports test: [FACT: code]. Overall beats rule: 0.35-0.45; mechanism addresses diagnosed failures: 0.8. Reversible: no new physics, one policy, one week.
