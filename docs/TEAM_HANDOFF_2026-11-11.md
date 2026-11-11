# Team handoff - external review of the project (2026-11-11)

Context: two external AIs reviewed the bundled project. Both uploads were truncated; one saw NO Python source and inferred everything from our docs. Every load-bearing claim below was verified against the actual repo at the file:line given. Read this before touching anything. Each item is verified, refuted, or explicitly unverifiable - do not treat the AI text as gospel, treat this file as the current truth.

## The short version

- Headline results unchanged (claim audit 34/0, run today): learner 0.9512 vs rule 0.923 (+0.028 [0.016, 0.041]), stress deltas, classical OR 0.929, planning oracle 0.9723, distilled 0.9618, energy ceilings (0.113 steady state).
- Fixes 1-6 are code + re-measurement, NO retraining. Decide today what to do with #7 (2-3 days of wall-clock).
- Do not edit the report, the PDF, or the clean repo yet. Fixes land, claim_audit.py re-runs, THEN one report revision.
- I will not be able to do hands-on work on this today. Whoever picks something up, moves ahead without waiting for me.

## Verified REAL - fix these

1. Mixed sd conventions. `results_ablation*.csv` store ddof=0 (all ab_*.py runners); `results_main.csv` stores ddof=1. `make_tables.py:138` recomputes ddof=1 from per-seed values when present but silently falls back to the ddof=0 CSV at 140-143. `fill_tokens.py:827` uses ddof=0 (yardstick) next to `:877` ddof=1 (pstd). `summary.py` prints raw CK_std. `ab_observation.json` has no per_seed_CK, so the observation table prints population sd. Rule baselines carry scene-axis +/- while the learner carries seed-axis +/- (main-table caption discloses the rule axis; the ab_observation/ab_credit tables do not).
2. sd fallback everywhere. `fill_tokens.py:199, 357, 373` - without scipy, CIs silently shrink from t(7)=2.365 to z=1.96 (~17% narrower). Hard-fail, or ship a t-table.
3. Dead ablation arms. **Fix done:** corrected `Denied` to count charge requests left unassigned by pad capacity (with or without arbitration), stopped summing the cumulative denial counter once per step, and added a per-episode degraded-step fraction plus per-training-seed `Denied`, `Degraded`, and `Reserve` vectors to new ablation rows. Bumped the measurement-schema hash so resume logs without these diagnostics are not reused as complete rows. No scenario, reward, or policy behavior changed, and the ablation has not been rerun. **What was previously wrong:** zero `Denied` did not show that no requests competed—the counter only recorded a narrower occupied-slot case, and the metric also repeatedly summed that cumulative counter. The nominal Full/no-arbitration CK difference (+0.0133) is unresolved at eight seeds (paired 95% CI about [-0.0100, +0.0365], p about 0.220), not proof that arbitration has no effect. Full and no-reserve match in the nominal artifacts but diverge under stress, so no-reserve is inactive only in the nominal regime. No-degraded's CK matches Full on nominal seeds 2 and 4 and stress seed 2, but the old artifacts lack per-seed connectivity/D_t measurements; those matches do not establish D_t == 0. Rerun the ablation with the new diagnostics before concluding which arms are information-free.
4. Duplicate generations + last-wins merge. **Fix done:** archived the stale `results_ablation_parta/partb.csv` files as `.stale-precharger.csv`; added a configuration/protocol hash to ablation rows; made the merger reject missing or mismatched hashes, duplicate models, and mixed protocols; made `make_tables.py` reject duplicate models or mixed hashes. The live artifacts are one consistent generation (results_main MAPPO == results_ablation.csv Full == ab_credit arm A == ab_energy arm A; identical per-seed vectors, CK 0.6740706). The archived part files had all-zero MinBattery signatures and must not be used as merge inputs. **Suggestion:** regenerate part files under the corrected configuration before merging; retain the hash and duplicate checks to prevent mixing generations or silently accepting last-wins duplicates.
5. table XIV "single_pad: NA" is an eval-script bug, not an architecture limit. obs_dim is 68 regardless of pad count (pad features are a fixed 3 dims, nearest pad only); state_dim shifts by 1 per pad. `mappo.load` loads actor AND critic (`mappo.py:329-330`); `eval_stress.py:81-83` builds MAPPO with the shifted state_dim, so the critic load_state_dict shape-mismatches. Fix: load actor-only for frozen zero-shot eval (correct under CTDE), or build the critic with the checkpoint's saved state_dim. A real single_pad number is free.
6. Action-repeat conclusion overstated. Trained hold=4 (`old/launch_ar_fixed.ps1`: --n-steps 500 --action-repeat 4) but evaluated hold=1 (`eval_ckpt.py` has no --action-repeat). 0.9086 vs 0.9512 measures cross-MDP transfer, not "repetition hurts the deployed policy". Also: the exp_ar_eval seed metas never log action_repeat. Reword Section VIII-F, and run the hold=4 eval (add the flag) or retrain with gamma^4.
7. Shaping sign inverted - the big one. Report Section III-O and `env.py:1333` (and `:1342`, energy potential) compute kappa*(prev_phi - gamma*phi_after), which is exactly -F for Ng's reward-max form F = gamma*Phi' - Phi. With Phi = -dist <= 0 this rewards RETREATING from sensors and penalizes approach, and the sum does not exactly telescope. The headline (exp_ego_eval, 0.9512) was trained with shape=0.5. Two acceptable resolutions: (a) fix the sign in both terms + III-O and rerun ego+shape (2-3 days wall-clock); (b) keep the number, reword: "dense reward shaping", drop "potential-based / policy-invariant". The frozen-policy measurements remain valid as artifacts; the mechanistic claim does not.

Also, small but fix in the same pass: MaxRefresh == 2000 in every stress row (right-censored, discriminates nothing) - drop or recompute it in the stress table.

## Refuted - do not "fix" these

8. Active-agent mask off-by-one: `train.py:83` stores B["active"] BEFORE the env.step() at :88 - active at action time, exactly what is required.
9. EMA value-norm drift breaking PPO clip: stats update once per rollout, and target and old values are re-normalized with the same post-update stats (`mappo.py:194-205`). No mixed frames.
10. MinBattery "unit mixing": raw Joules everywhere (`env.py:1470, 1523`).
11. "Matched-budget claim": the report makes no such claim; the main-table caption discloses 20 vs 25 and points to the credit arm at base budget.
12. "AG saturated everywhere": only in the nominal regime; in stress, AG discriminates arms (~0.80 typical vs 0.981 no-reserve / 0.996 VanillaMAPPO).
13. IDQN epsilon ~0.91 after 20 episodes: plausible (SC=0.000, AG=0.996) but the IDQN training script is absent from the repo - do not report or rely on the claim; mark the row as artifact-only.

## Unverifiable from this repo

14. no-undercoverage per-seed vector is bimodal in both generations: [0.771, 0.450, 0.590, 0.753, 0.595, 0.469, 0.539, 0.449]. The "uses the pad vs doesn't" hypothesis cannot be checked - artifacts carry no per-seed auxiliary metrics. If you want this answered, log per-seed ReturnEvents/pad occupancy for that arm and rerun.

## Ground rules

- Verify every claim at file:line in THIS repo before acting on it. If you cannot verify it, it goes to the unverified bucket, not into the fix.
- No retraining in fixes 1-6. Item 7 = decision, not default: rerun (2-3 days) or reword.
- Observation arms change parameter counts too (no-map -16 dims, no-agent-id -8, no-pad-bearing -3, VanillaMAPPO -11); "differs in exactly one component" is only true of the reward/mask arms. Quote it that way.
- Freeze nothing silently: every fix lands with its file:line and the re-measured number in the PR/group message.
- Pick ONE unverified item, verify it, report back in the group.

Suggested owners (not binding): someone takes 1+2+5 (one morning), someone takes 4+6 (one morning), one decision owner for 7.
