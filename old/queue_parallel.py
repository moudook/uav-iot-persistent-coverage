"""Parallel G3 + residual queue.

Runs up to MAX_PARALLEL training processes at once.  Each seed is one job,
so three seeds of a regime run simultaneously and a 5-seed regime finishes
in ~2 batches instead of 5.  run_g3.py and run_residual.py both skip seeds
whose result file already exists, so the queue is idempotent and safe to
restart after an interruption.

Memory check: one training process ~560 MB.  Three concurrent ~1.7 GB,
well inside the 15.7 GB available.  BLAS is pinned to 1 thread per process
via the env vars set in both runners, so 3 processes use 3 cores.
"""
import os, sys, subprocess, time, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
MAX_PARALLEL = 6
LOG = os.path.join(PROJ, "ml_impl", "runs", "g3", "_parallel.log")

# (kind, regime, mode, seed, episodes, n_steps)
JOBS = []
for (regime, mode) in [("failure", "team"), ("multi_failure", "team"),
                       ("single_pad", "c3"), ("small_battery", "c3")]:
    for s in range(5):
        JOBS.append(("g3", regime, mode, s, 200, 2000))
# failure seed 4 already missing -> include it
# residual on single_pad
for s in range(5):
    JOBS.append(("residual", "single_pad", None, s, 200, 2000))


def result_exists(kind, regime, mode, seed):
    if kind == "g3":
        d = os.path.join(PROJ, "ml_impl", "runs", "g3", regime, mode)
        return os.path.exists(os.path.join(d, f"seed_{seed}.json"))
    else:
        d = os.path.join(PROJ, "ml_impl", "runs", "residual", regime)
        return os.path.exists(os.path.join(d, f"seed_{seed}.json"))


def cmd_for(job):
    kind, regime, mode, seed, ep, ns = job
    if kind == "g3":
        return [sys.executable, os.path.join(HERE, "run_g3.py"),
                "--regime", regime, "--credit-mode", mode,
                "--seeds", str(seed), "--episodes", str(ep), "--n-steps", str(ns)]
    else:
        return [sys.executable, os.path.join(HERE, "run_residual.py"),
                "--regime", regime, "--seeds", str(seed),
                "--episodes", str(ep), "--n-steps", str(ns)]


def log(msg):
    line = f"[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}] {msg}"
    print(line, flush=True)
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def main():
    # Filter out already-done jobs
    pending = [j for j in JOBS if not result_exists(*j[:4])]
    log(f"parallel queue: {len(pending)} jobs pending, max {MAX_PARALLEL} concurrent")
    running = {}  # proc -> job
    t0 = time.time()
    while pending or running:
        # Launch as many as slots allow
        while pending and len(running) < MAX_PARALLEL:
            job = pending.pop(0)
            kind, regime, mode, seed, ep, ns = job
            label = f"{kind}/{regime}" + (f"/{mode}" if mode else "") + f"/seed{seed}"
            log(f"start: {label}")
            p = subprocess.Popen(cmd_for(job), cwd=PROJ,
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            running[p] = (job, label, time.time())
        # Poll
        finished = []
        for p, (job, label, started) in list(running.items()):
            rc = p.poll()
            if rc is not None:
                dt = time.time() - started
                kind, regime, mode, seed, ep, ns = job
                ok = result_exists(*job[:4])
                status = "ok" if ok else f"MISSING RESULT (exit {rc})"
                log(f"end:   {label}  {status}  {dt/60:.1f} min")
                finished.append(p)
        for p in finished:
            del running[p]
        if running:
            time.sleep(10)
    total = time.time() - t0
    log(f"ALL DONE in {total/3600:.2f} h")


if __name__ == "__main__":
    main()
