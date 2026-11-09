"""Launch G1 (5 seeds) in parallel as separate processes."""
import subprocess, sys, os, time
HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
SEEDS = [0,1,2,3,4]
procs = []
for i, s in enumerate(SEEDS):
    cmd = [PY, os.path.join(HERE, "run_g1.py"), "--seeds", str(s), "--episodes", "200", "--n-steps", "2000", "--seed-idx", "0"]
    # run_g1.py with --seeds s --seed-idx 0 runs just that seed
    cmd = [PY, os.path.join(HERE, "run_g1.py"), "--seeds", str(s), "--episodes", "200", "--n-steps", "2000"]
    p = subprocess.Popen(cmd, stdout=open(os.path.join(HERE, f"..", "ml_impl", "runs", "g1", f"seed_{s}.log"), "w"), stderr=subprocess.STDOUT)
    procs.append((s, p))
    print(f"launched seed {s} pid={p.pid}")
    time.sleep(2)
print("all launched; monitor ml_impl/runs/g1/seed_*.log")
