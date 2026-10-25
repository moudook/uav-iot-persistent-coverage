"""The second re-measurement: the artefacts the charger fix invalidated.

The first re-measurement resumed from the saved policies, and those
policies had been trained against the old charger, so the base table,
the observation arms, the learned baselines and the scenario matrix were
still the old measurements.  Their policies and caches have been moved
aside and these four stages are run again from scratch.

The probes come after the base table, because they read its policies.
"""
from __future__ import annotations

import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ML = os.path.dirname(HERE)
PY = sys.executable

STAGES = [
    ("scen", [PY, "-u", os.path.join(ML, "run_all.py"), "--stage", "scen"]),
    ("base", [PY, "-u", os.path.join(ML, "run_all.py"), "--stage", "base",
              "--train-seeds", "8"]),
    ("obs", [PY, "-u", os.path.join(HERE, "ab_observation.py"),
             "--episodes", "25", "--seeds", "8", "--eval-seeds", "5"]),
    ("learned", [PY, "-u", os.path.join(ML, "run_all.py"), "--stage", "learned"]),
]

# the probes, which need the base table's policies
PROBES = [
    ("dormancy", [PY, "-u", os.path.join(ML, "run_all.py"),
                  "--stage", "probe"]),
    ("conn", [PY, "-u", os.path.join(HERE, "connectivity_accounting.py"),
              "--full", "--episodes", "3", "--steps", "2000"]),
]


def free_memory():
    import ctypes

    class MEMORYSTATUSEX(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong),
                    ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]

    m = MEMORYSTATUSEX()
    m.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return m.ullAvailPhys / 1024 ** 3, m.ullAvailPageFile / 1024 ** 3


def room(need_phys=4.5, need_page=4.0):
    # The page file, not the RAM, is the binding constraint: four
    # training jobs exhausted it on this machine, and the commit that
    # was running alongside them failed with a CLR out-of-memory
    # error.  The rule is therefore conservative: two jobs, and a lot
    # of headroom on both.
    phys, page = free_memory()
    return phys >= need_phys and page >= need_page


def run(cmd, log, env):
    with open(log, "w", encoding="utf-8") as f:
        return subprocess.run(cmd, cwd=ML, stdout=f, stderr=subprocess.STDOUT,
                              env=env).returncode


def main() -> int:
    env = dict(os.environ)
    env["UAV_DEVICE"] = "cpu"
    env["OPENBLAS_NUM_THREADS"] = "1"
    env["OMP_NUM_THREADS"] = "1"
    env["MKL_NUM_THREADS"] = "1"

    running = {}
    pending = list(STAGES)
    limit = 2
    t0 = time.time()

    while pending or running:
        for name, cmd in list(pending):
            if len(running) >= limit or not room():
                break
            pending.remove((name, cmd))
            log = os.path.join(HERE, f"q3_{name}.log")
            print(f"[{time.strftime('%H:%M:%S')}] start {name}", flush=True)
            running[name] = (subprocess.Popen(cmd, cwd=ML,
                                              stdout=open(log, "w", encoding="utf-8"),
                                              stderr=subprocess.STDOUT, env=env),
                              log, time.time())
        for name in list(running):
            p, log, ts = running[name]
            if p.poll() is not None:
                print(f"[{time.strftime('%H:%M:%S')}] {name} finished with "
                      f"{p.returncode} in {time.time()-ts:.0f}s", flush=True)
                del running[name]
        time.sleep(5)

    # the probes, once the base table's policies exist
    for name, cmd in PROBES:
        log = os.path.join(HERE, f"q3_{name}.log")
        print(f"[{time.strftime('%H:%M:%S')}] start {name}", flush=True)
        rc = run(cmd, log, env)
        print(f"[{time.strftime('%H:%M:%S')}] {name} finished with {rc}",
              flush=True)

    print(f"[{time.strftime('%H:%M:%S')}] the queue is done in "
          f"{time.time()-t0:.0f}s", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
