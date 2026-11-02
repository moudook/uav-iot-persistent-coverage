P = r"C:\Users\gbust\Downloads\Academic\Courses\Machine_learning_in_wireless_network\Project1\docs\MEASURED_NUMBERS.md"
s = open(P, encoding="utf-8").read()

rep = [
    ("| anchor (ego+shape) | 0.9522 | 0.0105 | 5 | -- |",
     "| anchor (ego+shape) | 0.9512 | 0.0105 | 5 | -- |"),
    ("    learner (ego+shape)   = 0.9522  (95% CI [0.9392, 0.9653], 5 seeds)",
     "    learner (ego+shape)   = 0.9512  (95% CI [0.9381, 0.9643], 5 seeds, 20 held-out scenes)"),
    ("    learner - rule = +0.0289  (95% CI [+0.0159, +0.0420])  -> excludes zero",
     "    learner - rule = +0.0279  (95% CI [+0.0149, +0.0410])  -> excludes zero"),
    ("    ablation: +ego/shaping = +0.0928, resolved",
     "    ablation: +ego/shaping = +0.0918, resolved"),
    ("| anchor (ego+shape) | base | nominal | 0.9522 | -- | +0.029 (resolved) |",
     "| anchor (ego+shape) | base | nominal | 0.9512 | -- | +0.028 (resolved) |"),
]
for old, new in rep:
    assert s.count(old) == 1, old
    s = s.replace(old, new, 1)

# append protocol note
note = ("\n## PROTOCOL NOTE (2026-11-03)\n\n"
        "The per-seed `exp_ego_eval/seed_*.json` records carry an in-run eval on\n"
        "scenes 0-9 that predates the corrected protocol; the headline numbers are\n"
        "now read from `exp_ego_eval/eval_heldout.json` (5 frozen checkpoints x 20\n"
        "held-out scenes, seeds 1000-1019), which is the evaluation the report\n"
        "describes.  Nominal: 0.9512 [0.9381, 0.9643]; diff vs Reactive-local\n"
        "0.9233 = +0.0279 [+0.0149, +0.0410], excludes zero.\n")
s = s.rstrip() + "\n" + note
open(P, "w", encoding="utf-8").write(s)
print("docs updated")
