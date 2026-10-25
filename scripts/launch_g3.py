"""Launch G3 for a regime: 5 seeds in parallel."""
import subprocess, sys, os, time
HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
regime = sys.argv[1] if len(sys.argv) > 1 else "single_pad"
credit = sys.argv[2] if len(sys.argv) > 2 else "team"
seeds = [0,1,2,3,4]
procs = []
for s in seeds:
    cmd = [PY, os.path.join(HERE, "run_g3.py"), "--regime", regime, "--seeds", str(s), "--episodes", "200", "--n-steps", "2000", "--credit-mode", credit]
    logdir = os.path.join(HERE, "..", "ml_impl", "runs", "g3", regime, credit)
    os.makedirs(logdir, exist_ok=True)
    logfile = os.path.join(logdir, f"seed_{s}.log")
    p = subprocess.Popen(cmd, stdout=open(logfile, "w"), stderr=subprocess.STDOUT)
    procs.append((s, p))
    print(f"launched seed {s} pid={p.pid}")
    time.sleep(2)
print("all launched for regime=%s credit=%s" % (regime, credit))
