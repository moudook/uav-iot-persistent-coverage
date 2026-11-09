"""
Create a compact context bundle for an external AI reviewer.

Includes:
  - the current report source (Mlawn-midsem-tex.tex)
  - the implementation and evaluation code directly relevant to its claims
  - the measured artifacts and claim ledger for those evaluations
  - the two feedback documents being discussed

Excludes training artifacts, old drafts, logs, PDFs, and generated dumps.
If any required file is missing, abort rather than silently omitting context.

Run:
    python scripts/make_report_context_bundle.py
"""
import os
import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "PROJECT_REPORT_CONTEXT.txt")

FILES = [
    "Mlawn-midsem-tex.tex",

    # implementation

    "ml_impl/uav_wireless/env.py",
    "ml_impl/uav_wireless/experiments.py",
    "ml_impl/uav_wireless/mappo.py",
    "ml_impl/uav_wireless/train.py",
    "ml_impl/uav_wireless/seeding.py",
    "ml_impl/analysis/feasibility.py",

    # evaluation / analysis code

    "scripts/energy_certificate.py",
    "scripts/eval_ckpt.py",
    "scripts/eval_ckpt_stress_base.py",
    "scripts/eval_stress.py",
    "scripts/eval_classical_baseline.py",
    "scripts/eval_classical_stress.py",
    "scripts/eval_planning_v2.py",
    "scripts/eval_planning_stress.py",
    "scripts/gen_planning_dataset.py",
    "scripts/distill_actor.py",
    "scripts/compare_distilled.py",
    "scripts/compare_planning_2000.py",
    "scripts/compare_planning_stress.py",
    "scripts/compare_planning.py",
    "scripts/stress_regimes.py",
    "scripts/check_dead_numbers.py",

    # measured artifacts

    "ml_impl/runs/energy_certificate.json",
    "ml_impl/runs/classical_baseline_2000.json",
    "ml_impl/runs/classical_stress_2000.json",
    "ml_impl/runs/exp_ego_eval/eval_heldout.json",
    "ml_impl/runs/exp_ego_eval/eval_planning_2000.json",
    "ml_impl/runs/exp_ego_eval/eval_planning_stress.json",
    "ml_impl/runs/exp_ego_eval/eval_ckpt_500.json",
    "ml_impl/runs/exp_ego_eval/eval_ckpt_stress_base.json",
    "ml_impl/runs/exp_distilled/eval_heldout_2000.json",
    "ml_impl/runs/exp_distilled20/eval_heldout_2000.json",
    "ml_impl/runs/exp_anchor_eval/eval_heldout.json",
    "ml_impl/runs/exp_ar_eval/eval_heldout.json",
    "ml_impl/runs/stress_eval/stress_eval.json",
    "ml_impl/runs/stress_eval/stress_eval_anchor.json",

    # claim ledger and measured records

    "docs/CLAIMS.md",
    "docs/INNOVATION_RESULTS_2026-11-04.md",
    "docs/INNOVATION_RESULTS_2026-11-03.md",
    "docs/INDEPENDENT_AUDIT_2026-11-04.md",
    "docs/NOVELTY.md",
    "docs/NEGATIVE.md",
    "docs/MEASURED_NUMBERS.md",

    # feedback being discussed

    "Feedback_from_si/Feedback_from_SI_3.md",
    "Feedback_from_si/Feedback_from_SI_4.md",
]

def relpath(p: str) -> str:
    return p.replace("\\", "/")

def main() -> int:
    missing = []
    for rel in FILES:
        p = os.path.join(ROOT, rel)
        if not os.path.isfile(p):
            missing.append(rel)
    if missing:
        print("missing required files:")
        for x in missing:
            print("  " + x)
        return 1

    included = [os.path.join(ROOT, rel) for rel in FILES]
    treesize = sum(os.path.getsize(p) for p in included)
    with open(OUT, "w", encoding="utf-8", errors="replace") as out:
        out.write("FOCUSED REPORT CONTEXT BUNDLE\n")
        out.write("Generated: %s\n" % datetime.datetime.now().isoformat(timespec="seconds"))
        out.write("Root: %s\n" % ROOT)
        out.write("Files: %d\n" % len(included))
        out.write("Total content: %.2f MB (%d bytes)\n" % (treesize / 1e6, treesize))
        out.write("\nWhat is included:\n")
        out.write("  the current report source; the implementation and evaluation code\n")
        out.write("  backing its claims; the measured artifacts; the claim ledger; the\n")
        out.write("  feedback documents under discussion.\n\n")
        out.write("What is excluded:\n")
        out.write("  training artifacts, PDFs, logs, generated dumps, and old drafts.\n")
        out.write("\nFILE TREE (included)\n")
        for rel, p in zip(FILES, included):
            out.write(relpath(rel) + "  [%d bytes]\n" % os.path.getsize(p))
        out.write("\nFILE CONTENTS\n")
        for rel, p in zip(FILES, included):
            out.write("\n\n" + "=" * 80 + "\nPATH: " + relpath(rel) +
                      "\n" + "=" * 80 + "\n")
            with open(p, "r", encoding="utf-8", errors="replace") as f:
                out.write(f.read())
    print("wrote", OUT)
    print("bundle MB:", round(os.path.getsize(OUT) / 1e6, 2))
    print("bundle bytes:", os.path.getsize(OUT))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())