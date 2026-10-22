"""Re-measure the whole matrix, in parallel, with the page-file rule.

The charger fix changed the simulator, so every number in the paper has
to be measured again.  The previous queue ran the jobs one after
another, which is why the matrix took days; this one runs them
concurrently, up to a limit that keeps the page file from filling.

The jobs that the paper's central inference depends on come first, and
the long one (the scenario matrix, six hours) starts immediately so
that it is not the last thing still running.
"""
from __future__ import annotations

import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ML = os.path.dirname(HERE)
PY = sys.executable

JOBS = [
    # the long one first
    ("scen", [PY, "-u", os.path.join(ML, "run_all.py"), "--stage", "scen"]),
    ("base", [PY, "-u", os.path.join(ML, "run_all.py"), "--stage", "base",
              "--train-seeds", "8", "--resume"]),
    ("obs", [PY, "-u", os.path.join(HERE, "ab_observation.py"),
             "--episodes", "25", "--seeds", "8", "--eval-seeds", "5"]),
    ("credit", [PY, "-u", os.path.join(HERE, "ab_credit.py"),
                "--episodes", "25", "--seeds", "8", "--eval-seeds", "5"]),
    ("energy", [PY, "-u", os.path.join(HERE, "ab_energy_management.py"),
                "--episodes", "25", "--seeds", "8", "--eval-seeds", "5"]),
    ("budget", [PY, "-u", os.path.join(HERE, "ab_budget.py"),
                "--seeds", "8", "--eval-seeds", "5"]),
    ("alt", [PY, "-u", os.path.join(HERE, "alt_deployment.py"),
             "--seeds", "8", "--episodes", "25", "--eval-seeds", "5"]),
    ("abl", [PY, "-u", os.path.join(ML, "run_all.py"), "--stage", "abl"]),
    ("stress_a", [PY, "-u", os.path.join(HERE, "ablation_part.py"),
                  "--part", "stress_a", "--episodes", "6", "--seeds", "8",
                  "--eval-seeds", "5"]),
    ("stress_b", [PY, "-u", os.path.join(HERE, "ablation_part.py"),
                  "--part", "stress_b", "--episodes", "6", "--seeds", "8",
                  "--eval-seeds", "5"]),
    ("learned", [PY, "-u", os.path.join(ML, "run_all.py"), "--stage", "learned"]),
    ("map", [PY, "-u", os.path.join(HERE, "ab_map_resolution.py"),
             "--episodes", "20", "--seeds", "8", "--eval-seeds", "5",
             "--grids", "0,4,8"]),
    ("dev_cpu1", [PY, "-u", os.path.join(HERE, "device_sensitivity.py"),
                  "--config", "cpu1", "--episodes", "2"]),
    ("dev_cpu2", [PY, "-u", os.path.join(HERE, "device_sensitivity.py"),
                  "--config", "cpu2", "--episodes", "2"]),
    ("dev_merge", [PY, "-u", os.path.join(HERE, "device_sensitivity.py"),
                   "--merge"]),
]

# the merge of the stress parts has to wait for both of them
AFTER = {"merge_stress": ("stress_a", "stress_b")}


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


def room(need_phys=3.0, need_page=1.5):
    phys, page = free_memory()
    return phys >= need_phys and page >= need_page


def main() -> int:
    env = dict(os.environ)
    env["UAV_DEVICE"] = "cpu"
    env["OPENBLAS_NUM_THREADS"] = "1"
    env["OMP_NUM_THREADS"] = "1"
    env["MKL_NUM_THREADS"] = "1"

    # the merge job is appended with its dependency
    jobs = list(JOBS) + [(
        "merge_stress",
        [PY, "-u", os.path.join(HERE, "merge_ablation.py"), "--stress"])]

    running = {}          # name -> (process, log file, t0)
    done = set()
    pending = list(jobs)
    limit = 5
    t_start = time.time()

    while pending or running:
        # start what can be started
        for name, cmd in list(pending):
            need = AFTER.get(name)
            if need and not all(d in done for d in need):
                continue
            if len(running) >= limit or not room():
                break
            pending.remove((name, cmd))
            log = os.path.join(HERE, f"q2_{name}.log")
            print(f"[{time.strftime('%H:%M:%S')}] start {name} -> {log}",
                  flush=True)
            fh = open(log, "w", encoding="utf-8")
            p = subprocess.Popen(cmd, cwd=ML, stdout=fh,
                                 stderr=subprocess.STDOUT, env=env)
            running[name] = (p, fh, time.time())
        # reap what finished
        for name in list(running):
            p, fh, t0 = running[name]
            if p.poll() is not None:
                fh.close()
                print(f"[{time.strftime('%H:%M:%S')}] {name} finished with "
                      f"{p.returncode} in {time.time()-t0:.0f}s", flush=True)
                done.add(name)
                del running[name]
        time.sleep(5)

    print(f"[{time.strftime('%H:%M:%S')}] the queue is done in "
          f"{time.time()-t_start:.0f}s", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
