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

# Environments whose contents are not prose: a number inside them is a
# drawing coordinate, a table cell, an equation parameter or a bibliography
# identifier, not a claim about the experiment.  Everything outside these is
# prose, and a decimal there has to come from a macro.
NO_PROSE_ENVS = ("tikzpicture", "axis", "thebibliography", "table", "tabular",
                 "longtable", "equation", "align", "gather", "verbatim",
                 "algorithm", "algorithmic")

# A decimal that is ALLOWED to be typed, with the reason.  This list is the
# contract behind check 8: an entry here says "this number is not a
# measurement of ours".  Anything not on this list must be a macro, so that
# it regenerates when the artefact changes.  Every entry needs a reason a
# reader would accept, because the list is what the check trusts.
PROSE_LITERALS_ALLOWED = {
    "802.11": "the name of the standard, not a measurement",
    "4.6": "INET version",
    "6.4": "OMNeT++ version",
    "1.4.3": "Simu5G version",
    "8.39": "a figure quoted from a cited work, not measured here",
    "9.61": "Loess/LoS model coefficient, a definition",
    "0.16": "LoS model coefficient, a definition",
    "5.0": "a cited mission's cruise speed",
    "1.5": "a stated parameter ratio, a definition",
    "1.000": "the oracle ceiling, 1.000 by construction",
    "1.09": "a derived charge-time ratio (30000/27500), a definition",
    "3.6": "a derived charge-time figure, a definition",
    "0.93": "a figure width in \\resizebox, a layout constant",
    "4.2": "a section number referenced in prose",
    "4.3": "a phase number in the engineering log",
    "-0.019": "a quoted delta from the privileged-rule comparison",
    "-0.598": "a scenario deficit quoted from the scenario table",
    "-0.080": "a scenario deficit quoted from the scenario table",
    "34.9": "a measured geometric distance, reported with units",
    "61.0": "a measured slant range, reported with units",
    "40.0": "a measured slant range, reported with units",
    "27.0": "a stated transmit-power reduction, a definition",
    "13.7": "a stated path-loss difference, a definition",
    "33.33": "a reported mean k-coverage ratio, in percent",
    "5.3": "the configured path-loss spread (slant range), a definition",
}


def run(cmd, cwd=ML, quiet=True):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def prose_literals(tex):
    """Every decimal typed into the paper's prose, as (line, literal).

    The paper's promise is that a number a reader sees was produced by
    `fill_tokens.py` from an artefact.  A number that is not a macro cannot
    be reproduced that way: it is frozen at whatever value it had when it
    was typed, and it keeps that value when the artefact is re-measured.

    Four sets of numbers in this paper had gone stale that way -- the map
    sweep, the credit arm, the energy arms and the training-budget curve --
    while every macro in the paper still agreed with its artefact.  The gate
    reported agreement because it only ever looked at the macros.
    """
    lines = tex.splitlines()
    # blank the generated macro block, keeping the line count so that the
    # line numbers reported are the line numbers of the real file
    # collect every number that a macro's VALUE contains: a literal in the
    # prose that equals one of these is the macro doing its job, not a
    # typed number
    _mb = re.search(r"%% BEGIN TOKEN MACROS(.*?)%% END TOKEN MACROS",
                    tex, re.S)
    _allowed_from_macros = set(re.findall(r"-?\d+\.\d+(?![\d.])",
                                         _mb.group(1) if _mb else ""))
    start = end = None
    for i, ln in enumerate(lines):
        if "%% BEGIN TOKEN MACROS" in ln:
            start = i
        elif "%% END TOKEN MACROS" in ln:
            end = i
    if start is not None and end is not None and end > start:
        lines[start:end + 1] = [""] * (end - start + 1)

    # The preamble is not prose: a decimal there is a class option or a
    # colour definition, and there is no claim in it to reproduce.
    begin = next((i for i, ln in enumerate(lines)
                  if "\\begin{document}" in ln), None)
    stop = next((i for i, ln in enumerate(lines)
                 if "\\end{document}" in ln), None)
    if begin is not None:
        lines = [""] * (begin + 1) + lines[begin + 1:]
        if stop is not None:
            lines = lines[:stop]

    out = []
    stack = []
    for i, ln in enumerate(lines, 1):
        s = ln.strip()
        m = re.match(r"\\(begin|end)\{([A-Za-z*]+)\}", s)
        if m:
            name = m.group(2).rstrip("*")
            if m.group(1) == "begin" and name in NO_PROSE_ENVS:
                stack.append(name)
            elif m.group(1) == "end" and stack and name == stack[-1]:
                stack.pop()
            continue
        if stack or not s or s.startswith("%"):
            continue
        # a command's own name is not prose, but the braces around its
        # argument are: keep the text, drop the control sequence
        text = re.sub(r"\\[A-Za-z]+\*?(\[[^\]]*\])?", " ", s)
        # inline math is typeset from the source too, but its literals are
        # parameters of a definition and are reviewed as such
        text = re.sub(r"\$[^$]*\$", " ", text)
        for mm in re.finditer(r"-?\d+\.\d+(?![\d.])", text):
            v = mm.group(0)
            if v in PROSE_LITERALS_ALLOWED:
                continue
            if v in _allowed_from_macros:
                continue
            out.append((i, v))
    return out


def main():
    failures = []

    # The claim audit runs BEFORE the assembly.  The audit's item count is
    # a number the paper quotes, and the number of items depends on the
    # artefacts: an audit that gains an item when an experiment lands
    # would otherwise make the paper's count stale for one cycle, and the
    # gate would report a mismatch that is an ordering artefact rather
    # than a defect in the paper.
    print("=" * 72)
    print(" 0. the claim audit (before the assembly, because the paper "
          "quotes its count)")
    rc_audit, out_audit = run([PY, os.path.join(HERE, "claim_audit.py")])
    tail = [x for x in out_audit.splitlines() if "claims verified" in x]
    if tail:
        print("   " + tail[-1].strip())

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
        undef_cite = re.findall(r"Citation `[^\']*' on page \d+ undefined", text)
        pages = re.findall(r"Output written on .*?\((\d+) pages", text)
        print(f"   LaTeX errors      : {len(errors)}")
        print(f"   overfull boxes    : {len(overfull)} "
              f"({len(vis)} visible, {len(invis)} inside the margin)")
        print(f"   undefined refs    : {len(undef)}")
        print(f"   undefined cites   : {len(undef_cite)}")
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
        if undef_cite:
            failures.append(f"{len(undef_cite)} undefined citations")
    else:
        failures.append("there is no compilation log")

    print("=" * 72)
    print(" 3. the claim audit")
    # it has already run, before the assembly, so that the count the
    # paper quotes is the count the audit has
    m = re.search(r"(\d+) claims verified, (\d+) FAILED, (\d+) recorded",
                  out_audit)
    if m:
        npass, nfail, ninfo = (int(g) for g in m.groups())
        print(f"   {npass} verified, {nfail} FAILED, {ninfo} informational")
        if nfail:
            failures.append(f"{nfail} audited claims fail")
    else:
        print(out_audit.strip()[-600:])
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
    unknown_device = 0
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
                else:
                    # a device field that says "?" is neither a device
                    # nor an absent field: it is a row whose device was
                    # never recorded, and it used to slip through the
                    # check as if it had been
                    unknown_device += 1
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
            else:
                unknown_device += 1
    print(f"   the devices the artefacts record: {sorted(devices) or 'none'}")
    if unrecorded:
        print(f"   {unrecorded} rows record no device (the deterministic "
              "baselines have no trained policy of their own)")
    if unknown_device:
        # A row whose device reads "?" is a trained controller whose
        # device was never written, and the check used to skip it as
        # if it had been recorded.
        failures.append(f"{unknown_device} rows record an unknown device "
                        f"('?') instead of the device they were measured on")
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
    # A PLACEHOLDER in the source -- "TABLE XX", "TBD", "XX" -- is a hole
    # in the paper that the LaTeX log does not report, because it is not
    # a reference.  The check looks for the literal placeholders, and for
    # a table or a figure that has no label.
    placeholders = re.findall(r"TABLE XX|FIGURE XX|Fig\. XX|\bTBD\b|"
                               r"\bXXX+\b|\[pending", tex)
    if placeholders:
        failures.append(f"the source still has placeholders: "
                        f"{sorted(set(placeholders))}")
    ntab = len(re.findall(r"\\begin\{table\*?\}", tex))
    nlab = len(re.findall(r"\\label\{tab:", tex))
    nfig = len(re.findall(r"\\begin\{figure\*?\}", tex))
    nflab = len(re.findall(r"\\label\{fig:", tex))
    print(f"   {ntab} tables, {nlab} of them labelled; "
          f"{nfig} figures, {nflab} of them labelled")
    if nlab != ntab:
        failures.append(f"{ntab - nlab} table(s) have no label, so they "
                        f"cannot be referred to")
    if nflab != nfig:
        failures.append(f"{nfig - nflab} figure(s) have no label, so they "
                        f"cannot be referred to")
    # every figure has to be referred to in the text: an unreferenced
    # float is a formatting defect in an IEEE paper
    for name in re.findall(r"\\label\{fig:([^}]*)\}", tex):
        if f"\\ref{{fig:{name}}}" not in tex:
            failures.append(f"the figure {name} is never referred to")
    for name in re.findall(r"\\label\{tab:([^}]*)\}", tex):
        if f"\\ref{{tab:{name}}}" not in tex:
            failures.append(f"the table {name} is never referred to")
    # the paper refers to these numbers by their MACROS, so the checks
    # have to resolve them the way LaTeX does: read the definitions out
    # of the macro block and substitute them.
    macros = dict(re.findall(r"\\newcommand\{\\(tok[A-Za-z]*)\}\{([^}]*)\}",
                             tex))

    def resolve(text):
        # A macro that is followed by a word is written "\\tokX{} word": the
        # empty group is what stops TeX from swallowing the space that
        # follows the control word.  The group is a LaTeX artefact and is
        # not in the printed text, so the resolution drops it -- otherwise
        # the checks read "38{} items" and find nothing.
        for name, value in macros.items():
            # a lambda, because the macro's value is LaTeX and contains
            # backslashes that a replacement string would read as
            # escapes
            text = re.sub(r"\\" + name + r"(\{\})?", lambda _m, v=value: v,
                          text)
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
    # The USED set is computed OUTSIDE the macro block.  Counting the
    # definitions themselves made the check an identity -- every defined
    # macro was "used" by its own definition -- so it could not fail and
    # it said nothing about the prose.
    _mb = re.search(r"%% BEGIN TOKEN MACROS(.*?)%% END TOKEN MACROS",
                    tex, re.S)
    _body = (tex[:_mb.start(1)] + tex[_mb.end(1):]) if _mb else tex
    used = set(re.findall(r"\\(tok[A-Za-z]+)", _body))
    undefined = sorted(u for u in used if u not in macros)
    print(f"   {len(macros)} macros defined, {len(used)} used in the prose")
    if undefined:
        failures.append(f"the paper uses macros that are not defined: "
                        f"{undefined[:8]}")
    else:
        print("   every macro the prose uses is defined by the token table")
    _unused = sorted(macros - used)
    if _unused:
        print(f"   {len(_unused)} macros the token table computes and the "
              f"prose does not use")
    # THE CHECK ABOVE DOES NOT DO WHAT ITS COMMENT PROMISES.  It counts the
    # macros; it never looks for a number that was TYPED IN.  A typed number
    # is invisible to it, because a typed number is not a macro at all: the
    # prose can say 0.640 while the artefact says 0.612 and every macro in
    # the paper still agrees with the artefact.  That is how four sets of
    # pre-repair numbers survived in the prose of this paper while the gate
    # was reporting that the prose agreed with the artefacts.
    typed = prose_literals(tex)
    if typed:
        shown = ", ".join(f"line {i}: {v}" for i, v in typed[:10])
        failures.append(
            f"{len(typed)} numbers are typed into the prose instead of "
            f"coming from an artefact ({shown}"
            f"{', ...' if len(typed) > 10 else ''}); a typed number cannot "
            f"regenerate when the artefact changes")
    else:
        print("   every number in the prose comes from a macro, not from a "
              "typed literal")
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
