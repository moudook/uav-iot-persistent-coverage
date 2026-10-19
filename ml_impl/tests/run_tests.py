"""
Zero-dependency test runner.

Why not pytest: installing packages on the user's machine requires explicit
permission, and a result that cannot be reproduced without an extra dependency
is a weaker artifact. This runner discovers `Test*` classes and `test_*`
methods exactly like pytest does, reports per-test pass/fail, and exits non-zero
on failure so it can gate a CI step or an experiment run.

Usage:
    python tests/run_tests.py            # all tests
    python tests/run_tests.py TestPHY    # one class
    python tests/run_tests.py -q         # summary only
"""

from __future__ import annotations

import importlib.util
import inspect
import os
import sys
import time
import traceback


HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)


def load_module(path: str):
    name = os.path.splitext(os.path.basename(path))[0]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def discover():
    """Yield (class_name, method_name, callable) for every test."""
    for fname in sorted(os.listdir(HERE)):
        if not fname.startswith("test_") or not fname.endswith(".py"):
            continue
        mod = load_module(os.path.join(HERE, fname))
        for cname, cls in inspect.getmembers(mod, inspect.isclass):
            if not cname.startswith("Test"):
                continue
            if cls.__module__ != mod.__name__:
                continue
            for mname, meth in inspect.getmembers(cls, inspect.isfunction):
                if mname.startswith("test_"):
                    yield cname, mname, meth, cls


def main(argv):
    quiet = "-q" in argv
    filt = [a for a in argv if not a.startswith("-")]

    passed, failed, skipped = [], [], []

    for cname, mname, meth, cls in discover():
        label = f"{cname}::{mname}"
        if filt and not any(f in label for f in filt):
            continue
        t0 = time.time()
        try:
            inst = cls()
            meth(inst)
        except Exception as exc:                       # noqa: BLE001
            failed.append((label, exc, traceback.format_exc(), time.time() - t0))
            print(f"FAIL  {label}")
        else:
            passed.append(label)
            if not quiet:
                print(f"ok    {label}  ({time.time()-t0:.2f}s)")

    print("-" * 66)
    print(f"{len(passed)} passed, {len(failed)} failed, {len(skipped)} skipped")

    for label, exc, tb, _dt in failed:
        print("=" * 66)
        print(f"FAILED: {label}")
        print(tb)

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
