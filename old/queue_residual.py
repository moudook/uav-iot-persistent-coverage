"""Unattended residual-MAPPO queue.

Runs only after queue_g3.py has finished all of its jobs, so that the two
queues never compete for the single training slot.  Polls for completion with
a 60 s sleep -- cheap, and avoids racing on the result files.
"""
import os, sys, subprocess, time, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
G3_REGIMES = [("low_comm", "team"), ("failure", "team"), ("multi_failure", "team"),
              ("single_pad", "c3"), ("small_battery", "c3")]
SEEDS = ["0", "1", "2", "3", "4"]
RUN_RESIDUAL = os.path.join(HERE, "run_residual.py")
LOG = os.path.join(PROJ, "ml_impl", "runs", "residual", "_queue.log")


def g3_done():
    for regime, mode in G3_REGIMES:
        d = os.path.join(PROJ, "ml_impl", "runs", "g3", regime, mode)
        if not (os.path.isdir(d) and all(
                os.path.exists(os.path.join(d, f"seed_{s}.json")) for s in SEEDS)):
            return False
    return True


def log(msg):
    line = f"[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}] {msg}"
    print(line, flush=True)
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def main():
    log("waiting for queue_g3.py to finish")
    while not g3_done():
        time.sleep(60)
    log("queue_g3 complete; starting residual MAPPO on single_pad")
    cmd = [sys.executable, RUN_RESIDUAL, "--regime", "single_pad",
           "--seeds", *SEEDS, "--episodes", "200", "--n-steps", "2000"]
    t0 = time.time()
    r = subprocess.run(cmd, cwd=PROJ)
    dt = time.time() - t0
    log(f"residual single_pad done: exit {r.returncode} in {dt/3600:.2f} h")
    log("queue finished")


if __name__ == "__main__":
    main()
