"""
Keep the two PDFs live.

The paper and the project report are both generated from the artefacts,
and the artefacts change while the experiments run.  This watches the
artefacts and the sources, and regenerates the two documents whenever
something changes, so that both PDFs are always current without anyone
having to remember to rebuild them.

It is deliberately a watcher and not a daemon with a schedule: the work
it does is a rebuild, and the rebuild is cheap and idempotent.

    python analysis/watch_docs.py [--once]

Run it in the background; it prints a line each time it rebuilds.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ML = os.path.dirname(HERE)
PROJ = os.path.dirname(ML)

# the files whose change means a rebuild
WATCH = [
    os.path.join(ML, "results_main.csv"),
    os.path.join(ML, "results_ablation.csv"),
    os.path.join(ML, "results_ablation_stress.csv"),
    os.path.join(ML, "results_scenarios.csv"),
    os.path.join(ML, "results_learned_baselines.csv"),
    os.path.join(HERE, "ab_observation.json"),
    os.path.join(HERE, "ab_energy_management.json"),
    os.path.join(HERE, "ab_credit.json"),
    os.path.join(HERE, "ab_budget.json"),
    os.path.join(HERE, "ab_map_resolution.json"),
    os.path.join(HERE, "alt_deployment.json"),
    os.path.join(HERE, "claim_audit.json"),
    os.path.join(HERE, "connectivity_accounting.json"),
    os.path.join(HERE, "corner_transfer.json"),
    os.path.join(HERE, "fill_tokens.py"),
    os.path.join(HERE, "results_text.tex"),
    os.path.join(HERE, "make_tables.py"),
    os.path.join(HERE, "assemble_results.py"),
    os.path.join(HERE, "make_report.py"),
    os.path.join(PROJ, "Mlawn-midsem-tex.tex"),
    os.path.join(PROJ, "AUTONOMOUS_STATE.md"),
]


def stamp():
    out = {}
    for p in WATCH:
        try:
            out[p] = os.path.getmtime(p)
        except OSError:
            out[p] = 0.0
    return out


def run(script):
    r = subprocess.run([sys.executable, os.path.join(HERE, script)],
                       cwd=ML, capture_output=True, text=True)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def rebuild(label=""):
    rc, out = run("assemble_results.py")
    paper = "ok"
    for line in out.split("\n"):
        if "pages:" in line:
            paper = line.strip()
        if "WARNING" in line and "tokens" in line:
            paper = "the paper has an unfilled token"
    rc2, out2 = run("make_report.py")
    report = "ok"
    for line in out2.split("\n"):
        if "REPORT.pdf" in line:
            report = line.strip()
    print(f"[{time.strftime('%H:%M:%S')}] {label} the paper: {paper} | "
          f"the report: {report}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true",
                    help="rebuild once and exit")
    ap.add_argument("--interval", type=float, default=60.0)
    a = ap.parse_args()

    if a.once:
        rebuild("rebuild")
        return 0

    print(f"watching {len(WATCH)} files; rebuilding the paper and the report "
          f"whenever one of them changes", flush=True)
    last = stamp()
    rebuild("the first build")
    while True:
        time.sleep(a.interval)
        now = stamp()
        changed = [os.path.basename(p) for p in WATCH
                   if now.get(p, 0) > last.get(p, 0)]
        if changed:
            last = now
            rebuild("changed: " + ", ".join(changed[:4]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
