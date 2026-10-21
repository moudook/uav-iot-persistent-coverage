"""Run the remaining re-measurements, one after another, in the background.

The machine's binding constraint is the page file, not the cores: six
training processes fit, a seventh dies with WinError 1455 while importing
torch.  The matrix is therefore run as a pool of six, and this queue is
the tail of it: the jobs that are left run one after another, each in its
own process, each logging to its own file.

The queue does not poll and it does not watch: it runs the jobs in order
and stops.  Every job is itself resumable, so a job that is killed by a
restart loses only the seed it was training.

    python analysis/run_queue.py                 # the default queue
    python analysis/run_queue.py --only credit   # one job
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ML = os.path.dirname(HERE)
PY = sys.executable

# The jobs, in order.  The first ones are the ones the paper's central
# inference depends on.
QUEUE = [
    ("base", [PY, "-u", os.path.join(ML, "run_all.py"),
              "--stage", "base", "--train-seeds", "8", "--resume"]),
    ("credit", [PY, "-u", os.path.join(HERE, "ab_credit.py"),
                "--episodes", "25", "--seeds", "8", "--eval-seeds", "5"]),
    ("alt", [PY, "-u", os.path.join(HERE, "alt_deployment.py"),
             "--seeds", "8", "--episodes", "25", "--eval-seeds", "5"]),
    ("stress_a", [PY, "-u", os.path.join(HERE, "ablation_part.py"),
                  "--part", "stress_a", "--episodes", "6", "--seeds", "8",
                  "--eval-seeds", "5"]),
    ("stress_b", [PY, "-u", os.path.join(HERE, "ablation_part.py"),
                  "--part", "stress_b", "--episodes", "6", "--seeds", "8",
                  "--eval-seeds", "5"]),
    ("merge_stress", [PY, "-u", os.path.join(HERE, "merge_ablation.py"),
                      "--stress"]),
    ("dev_cpu1", [PY, "-u", os.path.join(HERE, "device_sensitivity.py"),
                  "--config", "cpu1", "--episodes", "2"]),
    ("dev_cpu2", [PY, "-u", os.path.join(HERE, "device_sensitivity.py"),
                  "--config", "cpu2", "--episodes", "2"]),
    ("dev_cuda", [PY, "-u", os.path.join(HERE, "device_sensitivity.py"),
                  "--config", "cuda", "--episodes", "2"]),
    ("dev_merge", [PY, "-u", os.path.join(HERE, "device_sensitivity.py"),
                   "--merge"]),
    ("map", [PY, "-u", os.path.join(HERE, "ab_map_resolution.py"),
             "--episodes", "20", "--seeds", "8", "--eval-seeds", "5",
             "--grids", "0,4,8"]),
]


def free_memory():
    """The free physical and virtual memory, in GB."""
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


def wait_for_room(need_phys=3.2, need_page=1.5, timeout=3600):
    """Wait until a job can start without exhausting the page file.

    The project's own rule: do not start a training process until there
    is room for it.  A process that starts without room dies with
    WinError 1455 while importing torch, and it takes the other five
    processes' throughput down with it while the machine thrashes.
    """
    t0 = time.time()
    while True:
        phys, page = free_memory()
        if phys >= need_phys and page >= need_page:
            return True
        if time.time() - t0 > timeout:
            print(f"    giving up waiting for room: {phys:.1f} GB physical, "
                  f"{page:.1f} GB page file free", flush=True)
            return False
        time.sleep(20)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    a = ap.parse_args()

    env = dict(os.environ)
    env["UAV_DEVICE"] = "cpu"
    # the BLAS pools are pinned: a process that starts a pool sized for
    # the whole machine is what exhausts the page file
    for v in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS",
              "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        env.setdefault(v, "1")

    jobs = QUEUE
    if a.only:
        want = set(a.only.split(","))
        jobs = [j for j in QUEUE if j[0] in want]

    for name, cmd in jobs:
        log = os.path.join(HERE, f"queue_{name}.log")
        print(f"[{time.strftime('%H:%M:%S')}] {name} -> {log}", flush=True)
        if not wait_for_room():
            print(f"[{time.strftime('%H:%M:%S')}] {name} skipped: no room",
                  flush=True)
            continue
        t0 = time.time()
        with open(log, "w", encoding="utf-8") as f:
            r = subprocess.run(cmd, cwd=ML, stdout=f, stderr=subprocess.STDOUT,
                               env=env)
        print(f"[{time.strftime('%H:%M:%S')}] {name} finished with "
              f"{r.returncode} in {time.time()-t0:.0f}s", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
