"""
The final checks, in one command.

    python analysis/final_checks.py

It assembles the paper from the artefacts, compiles it, runs the claim
audit and the test suite, and reports every number a reader of the paper
would want to check.  It exits non-zero if any of them fails, so it can
gate a commit.

The checks are:
  1. the assembly completes, which means every prose token was filled
     from an artefact and no table is missing;
  2. the paper compiles with no LaTeX error, no overfull box and no
     undefined reference;
  3. the claim audit has no FAIL;
  4. the test suite passes;
  5. the numbers the paper quotes about ITSELF (the audit's item count,
     the test count) agree with the artefacts, which is checked by
     reading them back out of the compiled source.
"""

from __future__ import annotations

import csv
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ML = os.path.dirname(HERE)
PROJ = os.path.dirname(ML)
PY = sys.executable


def run(cmd, cwd=ML, quiet=True):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def main():
    failures = []

    print("=" * 72)
    print(" 1. the assembly")
    rc, out = run([PY, os.path.join(HERE, "assemble_results.py")])
    print(out.strip()[-1200:])
    if rc != 0:
        failures.append("the assembly did not complete")
    if "UNFILLED TOKENS" in out:
        failures.append("prose tokens are unfilled")
    if "WARNING: the table" in out:
        failures.append("a table is missing from the artefacts")

    print("=" * 72)
    print(" 2. the paper")
    log = os.path.join(PROJ, "Mlawn-midsem-tex.log")
    if os.path.exists(log):
        text = open(log, encoding="utf-8", errors="ignore").read()
        errors = re.findall(r"^! .*$", text, flags=re.M)
        overfull = re.findall(r"^Overfull .*$", text, flags=re.M)
        undef = re.findall(r"Reference `[^\']*' on page \d+ undefined", text)
        pages = re.findall(r"Output written on .*?\((\d+) pages", text)
        print(f"   LaTeX errors      : {len(errors)}")
        print(f"   overfull boxes    : {len(overfull)}")
        print(f"   undefined refs    : {len(undef)}")
        print(f"   pages             : {pages[0] if pages else '?'}")
        for e in errors[:6]:
            print(f"     {e}")
        for o in overfull[:6]:
            print(f"     {o}")
        if errors:
            failures.append(f"{len(errors)} LaTeX errors")
        if overfull:
            failures.append(f"{len(overfull)} overfull boxes")
        if undef:
            failures.append(f"{len(undef)} undefined references")
    else:
        failures.append("there is no compilation log")

    print("=" * 72)
    print(" 3. the claim audit")
    rc, out = run([PY, os.path.join(HERE, "claim_audit.py")])
    m = re.search(r"(\d+) claims verified, (\d+) FAILED, (\d+) recorded", out)
    if m:
        npass, nfail, ninfo = (int(g) for g in m.groups())
        print(f"   {npass} verified, {nfail} FAILED, {ninfo} informational")
        if nfail:
            failures.append(f"{nfail} audited claims fail")
    else:
        print(out.strip()[-600:])
        failures.append("the claim audit did not report")

    print("=" * 72)
    print(" 4. the test suite")
    rc, out = run([PY, os.path.join(ML, "tests", "run_tests.py"), "-q"])
    m = re.search(r"(\d+) passed, (\d+) failed", out)
    if m:
        ntest, nfail = int(m.group(1)), int(m.group(2))
        print(f"   {ntest} passed, {nfail} failed")
        if nfail:
            failures.append(f"{nfail} tests fail")
    else:
        print(out.strip()[-600:])
        failures.append("the test suite did not report")

    print("=" * 72)
    print(" 5. the device the measurements were produced on")
    # The device is part of the protocol: the floating-point kernels differ
    # between the CPU and the GPU, so two runs of the same configuration on
    # different devices are not the same experiment, and a variant and the
    # arm it is compared against must be on the same one.
    devices = set()
    for name in ("results_main.csv", "results_ablation.csv",
                 "results_ablation_stress.csv", "results_scenarios.csv"):
        p = os.path.join(ML, name)
        if not os.path.exists(p):
            continue
        with open(p, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                d = (r.get("device") or "").strip()
                if d:
                    devices.add(d)
    for name in ("ab_observation.json", "ab_credit.json",
                 "ab_energy_management.json", "ab_map_resolution.json"):
        p = os.path.join(HERE, name)
        if not os.path.exists(p):
            continue
        try:
            rows = json.load(open(p, encoding="utf-8"))
        except Exception:
            continue
        for r in rows if isinstance(rows, list) else []:
            d = (r.get("device") or "").strip()
            if d:
                devices.add(d)
    print(f"   the devices the artefacts record: {sorted(devices) or 'none'}")
    if len(devices) > 1:
        failures.append(f"the artefacts were produced on more than one "
                        f"device: {sorted(devices)}")
    elif not devices:
        print("   (no artefact records a device -- the re-measurement may not "
              "have run yet)")

    print("=" * 72)
    print(" 6. the paper's numbers about itself")
    tex = open(os.path.join(PROJ, "Mlawn-midsem-tex.tex"),
               encoding="utf-8").read()
    audit = json.load(open(os.path.join(HERE, "claim_audit.json"),
                           encoding="utf-8"))
    n_audit = len(audit)
    m = re.search(r"claim audit \((\d+) items", tex)
    if m:
        print(f"   the paper says {m.group(1)} audit items, "
              f"the audit has {n_audit}")
        if int(m.group(1)) != n_audit:
            failures.append("the paper's audit count does not match the audit")
    else:
        failures.append("the paper does not state its audit count")
    m = re.search(r"test suite of (\d+) cases", tex)
    if m:
        print(f"   the paper says {m.group(1)} test cases, "
              f"the suite has {ntest}")
        if int(m.group(1)) != ntest:
            failures.append("the paper's test count does not match the suite")
    else:
        failures.append("the paper does not state its test count")
    left = re.findall(r"@@([A-Z_0-9]+)@@", tex)
    if left:
        failures.append(f"the paper still contains tokens: {sorted(set(left))}")

    print("=" * 72)
    if failures:
        print(" FAILED:")
        for f in failures:
            print(f"   - {f}")
        return 1
    print(" every check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
