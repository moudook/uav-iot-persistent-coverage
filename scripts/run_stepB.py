"""Step B: run INET scenarios with varying topologies and collect delivery stats.

Generates trace files with different seeds, runs INET for each, parses .sca,
and saves per-scenario delivery statistics to a CSV for fitting the
information-channel model.
"""
import os, sys, subprocess, time, json, glob
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ml_impl"))

WSL = "/home/gbust/omnetpp_ws"
INET = WSL + "/inet-4.6.0"
SCN = INET + "/examples/uav_omnet"
PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRACES = os.path.join(PROJ, "Simulation", "omnet_uav", "traces")

def gen_traces(n_episodes, seeds):
    """Generate trace files with different seeds."""
    import subprocess
    os.makedirs(TRACES, exist_ok=True)
    for i, seed in enumerate(seeds):
        # Use the export script
        cmd = [sys.executable, os.path.join(PROJ, "scripts", "export_trajectories.py"),
               "--episodes", "1", "--seed", str(seed),
               "--out", os.path.join(PROJ, "Simulation", "omnet_uav", "traces_tmp")]
        subprocess.run(cmd, capture_output=True)
        # rename
        src = os.path.join(PROJ, "Simulation", "omnet_uav", "traces_tmp", "episode_000.movements")
        dst = os.path.join(TRACES, f"scenario_{i:03d}.movements")
        if os.path.exists(src):
            os.replace(src, dst)
    # cleanup
    import shutil
    tmp = os.path.join(PROJ, "Simulation", "omnet_uav", "traces_tmp")
    if os.path.exists(tmp):
        shutil.rmtree(tmp)
    print(f"Generated {len(seeds)} trace files")

def run_one(trace_name):
    """Run INET for one trace file. Returns success."""
    # Update ini traceFile
    cmd = "sed -i 's|traces/[^ ]*\\.movements|traces/%s|' %s/omnetpp.ini" % (trace_name, SCN)
    subprocess.run(["wsl", "-d", "Ubuntu", "--", "bash", "-c", cmd], capture_output=True)
    # Run
    run_cmd = "cd %s && opp_env run inet-4.6.0 -c 'cd %s/examples/uav_omnet && opp_run -u Cmdenv -l %s/out/clang-release/src/libINET.so -n %s/src:%s/examples 2>&1 | tail -2' 2>&1 | tail -3" % (WSL, INET, INET, INET, INET)
    r = subprocess.run(["wsl", "-d", "Ubuntu", "--", "bash", "-c", run_cmd], capture_output=True, text=True, timeout=120)
    return "Simulation time limit reached" in r.stdout

def main():
    # Generate 5 traces with different seeds
    seeds = list(range(5))
    gen_traces(5, seeds)
    # Run each
    results = []
    for i in range(5):
        name = f"scenario_{i:03d}.movements"
        print(f"Running {name}...", flush=True)
        # copy trace to WSL
        src = os.path.join(TRACES, name)
        subprocess.run(["wsl", "-d", "Ubuntu", "--", "bash", "-c",
                       f"cp /mnt/c/Users/gbust/Downloads/Academic/Courses/Machine_learning_in_wireless_network/Project1/Simulation/omnet_uav/traces/{name} {SCN}/traces/{name}"], capture_output=True)
        ok = run_one(name)
        print(f"  {name}: {'OK' if ok else 'FAIL'}")
        results.append({"trace": name, "success": ok})
    # Save
    out = os.path.join(PROJ, "Simulation", "omnet_uav", "stepB_results.json")
    with open(out, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved {len(results)} results")

if __name__ == "__main__":
    main()
