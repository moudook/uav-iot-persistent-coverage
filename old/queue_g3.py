"""Unattended G3 queue: run every remaining regime/variant in one process tree.

run_g3.py already skips seeds whose result file exists, so this queue is
idempotent: re-running it after an interruption picks up where it stopped.

Order is by paper value, not by convenience:
  1. low_comm / team        -- completes the four-regime headroom table
  2. failure / team         -- single-UAV failure
  3. multi_failure / team   -- multi-UAV failure
  4. single_pad / c3        -- the C3 credit ablation, on the best regime
  5. small_battery / c3     -- the second C3 ablation

Only one training process runs at a time: ten concurrent runs exhausted memory
on this machine, so the queue is deliberately serial.
"""
import os, sys, subprocess, time, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
RUN = os.path.join(HERE, "run_g3.py")
LOG = os.path.join(PROJ, "ml_impl", "runs", "g3", "_queue.log")

QUEUE = [
    ("low_comm", "team"),
    ("failure", "team"),
    ("multi_failure", "team"),
    ("single_pad", "c3"),
    ("small_battery", "c3"),
]

SEEDS = ["0", "1", "2", "3", "4"]
EPISODES = "200"
N_STEPS = "2000"


def log(msg):
    line = f"[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}] {msg}"
    print(line, flush=True)
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def done(regime, mode):
    d = os.path.join(PROJ, "ml_impl", "runs", "g3", regime, mode)
    if not os.path.isdir(d):
        return False
    return all(os.path.exists(os.path.join(d, f"seed_{s}.json")) for s in SEEDS)


def main():
    log(f"queue start: {len(QUEUE)} jobs")
    for regime, mode in QUEUE:
        if done(regime, mode):
            log(f"skip (complete): {regime}/{mode}")
            continue
        cmd = [sys.executable, RUN, "--regime", regime, "--credit-mode", mode,
               "--seeds", *SEEDS, "--episodes", EPISODES, "--n-steps", N_STEPS]
        log(f"start: {regime}/{mode}")
        t0 = time.time()
        r = subprocess.run(cmd, cwd=PROJ)
        dt = time.time() - t0
        status = "ok" if r.returncode == 0 else f"exit {r.returncode}"
        log(f"end:   {regime}/{mode}  {status}  {dt / 3600:.2f} h")
    log("queue finished")


if __name__ == "__main__":
    main()
