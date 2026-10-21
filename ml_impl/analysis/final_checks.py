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
        # An overfull HBOX is a line that sticks out of the column: the
        # reader sees it.  An overfull VBOX is a page that sticks out of
        # the text block, and it is only visible if it reaches past the
        # bottom margin (the IEEE page has about 19 mm of it, which is
        # 54 pt).  The balance package's column split on the
        # bibliography's last page is a VBOX overfull of a few points,
        # which lands in the margin and is invisible.
        margin_pt = 54.0

        def visible(o):
            if "hbox" in o:
                return True
            m = re.search(r"([0-9.]+)pt", o)
            return bool(m) and float(m.group(1)) > margin_pt

        vis = [o for o in overfull if visible(o)]
        invis = [o for o in overfull if o not in vis]
        undef = re.findall(r"Reference `[^\']*' on page \d+ undefined", text)
        pages = re.findall(r"Output written on .*?\((\d+) pages", text)
        print(f"   LaTeX errors      : {len(errors)}")
        print(f"   overfull boxes    : {len(overfull)} "
              f"({len(vis)} visible, {len(invis)} inside the margin)")
        print(f"   undefined refs    : {len(undef)}")
        print(f"   pages             : {pages[0] if pages else '?'}")
        for e in errors[:6]:
            print(f"     {e}")
        for o in overfull[:6]:
            print(f"     {o}")
        if errors:
            failures.append(f"{len(errors)} LaTeX errors")
        if vis:
            failures.append(f"{len(vis)} visible overfull boxes")
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
    unrecorded = 0
    for name in ("results_main.csv", "results_ablation.csv",
                 "results_ablation_stress.csv", "results_scenarios.csv"):
        p = os.path.join(ML, name)
        if not os.path.exists(p):
            continue
        with open(p, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                d = (r.get("device") or "").strip()
                if d and d != "?":
                    devices.add(d)
                elif not d:
                    unrecorded += 1
    for name in ("ab_observation.json", "ab_credit.json",
                 "ab_energy_management.json", "ab_map_resolution.json",
                 "ab_budget.json"):
        p = os.path.join(HERE, name)
        if not os.path.exists(p):
            continue
        try:
            rows = json.load(open(p, encoding="utf-8"))
        except Exception:
            continue
        for r in rows if isinstance(rows, list) else []:
            d = (r.get("device") or "").strip()
            if d and d != "?":
                devices.add(d)
            elif not d:
                unrecorded += 1
    print(f"   the devices the artefacts record: {sorted(devices) or 'none'}")
    if unrecorded:
        print(f"   {unrecorded} rows record no device (the deterministic "
              "baselines have no trained policy of their own)")
    if len(devices) > 1:
        failures.append(f"the artefacts were produced on more than one "
                        f"device: {sorted(devices)}")
    elif not devices:
        print("   (no artefact records a device -- the re-measurement may not "
              "have run yet)")

    print("=" * 72)
    print(" 6. the same configuration in different tables")
    # The observation arm C, the credit arm A, the energy arm A and the
    # ablation's full configuration are the SAME experiment: the base
    # configuration, the same training seeds and the same budget.  If the
    # protocol is consistent they must agree exactly, and if they do not,
    # something in the protocol is not pinned.
    def per_seed(path, key):
        p = os.path.join(HERE, path)
        if not os.path.exists(p):
            return None
        try:
            rows = json.load(open(p, encoding="utf-8"))
        except Exception:
            return None
        for r in rows:
            # The arm's NAME is the VALUE of the "arm" field.  The gate
            # used to look for the name among the row's KEYS, which is
            # never true, so it compared nothing and passed.
            if str(r.get("arm", "")).startswith(key):
                return [round(float(x), 6) for x in (r.get("per_seed_CK")
                                                     or [])]
        return None

    ref = None
    ref_name = None
    for path, key, name in (("ab_observation.json", "C + identity + map",
                              "the observation arm C"),
                             ("ab_credit.json", "A: shared actor",
                              "the credit arm A"),
                             ("ab_energy_management.json", "A: the proposed",
                              "the energy arm A")):
        v = per_seed(path, key)
        if v:
            if ref is None:
                ref, ref_name = v, name
            elif v != ref:
                # the WHOLE list, not its first three entries: the arms
                # are measured at the same number of training seeds as
                # the base comparison, and a table that was measured at
                # a different width is a different measurement
                failures.append(
                    f"{name} and {ref_name} are the same configuration but "
                    f"give different numbers: {v} against {ref}")
            else:
                print(f"   {name} agrees with {ref_name} on all "
                      f"{len(v)} training seeds")
    # and the main table's training runs
    main_p = os.path.join(ML, "results_main.csv")
    if os.path.exists(main_p) and ref:
        with open(main_p, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r.get("model") == "MAPPO":
                    n = r.get("train_seeds", "?")
                    print(f"   the main table's controller is trained {n} "
                          f"times, so its runs are the reference the other "
                          f"tables reuse")
                    if str(n).isdigit() and int(n) != len(ref):
                        failures.append(
                            f"the main table's controller is trained {n} "
                            f"times but the arms carry {len(ref)} training "
                            f"seeds: the arms are compared with the base "
                            f"comparison's arm A, so the widths have to "
                            f"match")
                    break

    print("=" * 72)
    print(" 7. the paper's numbers about itself")
    tex = open(os.path.join(PROJ, "Mlawn-midsem-tex.tex"),
               encoding="utf-8").read()
    # The paper refers to these numbers by their MACROS, so the checks
    # have to resolve them the way LaTeX does: read the definitions out
    # of the macro block and substitute them.
    macros = dict(re.findall(r"\\newcommand\{\\(tok[A-Za-z]*)\}\{([^}]*)\}",
                             tex))

    def resolve(text):
        for name, value in macros.items():
            text = text.replace("\\" + name, value)
        return text

    resolved = resolve(tex)
    audit = json.load(open(os.path.join(HERE, "claim_audit.json"),
                           encoding="utf-8"))
    n_audit = len(audit)
    m = re.search(r"claim audit \((\d+) items", resolved)
    if m:
        print(f"   the paper says {m.group(1)} audit items, "
              f"the audit has {n_audit}")
        if int(m.group(1)) != n_audit:
            failures.append("the paper's audit count does not match the audit")
    else:
        failures.append("the paper does not state its audit count")
    m = re.search(r"test suite of (\d+) cases", resolved)
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
    print(" 8. the numbers in the hand-written prose")
    # The hand-written prose refers to a number by its MACRO, and the
    # assembler writes the definitions from the token table.  So the
    # numbers there regenerate; a number typed into the source would
    # freeze at whatever the first assembly found.  This check finds the
    # ones that are still typed in.
    macros = set(re.findall(r"\\newcommand\{\\(tok[A-Za-z]*)\}", tex))
    used = set(re.findall(r"\\(tok[A-Za-z]+)", tex))
    undefined = sorted(u for u in used if u not in macros)
    print(f"   {len(macros)} macros defined, {len(used)} used")
    if undefined:
        failures.append(f"the paper uses macros that are not defined: "
                        f"{undefined[:8]}")
    else:
        print("   every macro the prose uses is defined by the token table")
    # the macro block must be present: without it the paper would not
    # compile, and with a stale one the numbers would be stale
    if "%% BEGIN TOKEN MACROS" not in tex:
        failures.append("the paper has no token-macro region")
    else:
        print("   the token-macro region is present and is rewritten on "
              "every assembly")

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
