"""Step B: run multiple INET scenarios and collect delivery stats for info channel model."""
import os, sys, subprocess, time, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ml_impl"))

WSL = "/home/gbust/omnetpp_ws"
INET = WSL + "/inet-4.6.0"
SCN = INET + "/examples/uav_omnet"
PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run_scenario(trace_name):
    """Run one scenario. Returns (success, stdout_tail)."""
    # Update ini traceFile
    cmd = "sed -i 's|traces/[^ ]*\\.movements|traces/%s|' %s/omnetpp.ini" % (trace_name, SCN)
    subprocess.run(["wsl", "-d", "Ubuntu", "--", "bash", "-c", cmd], capture_output=True, timeout=30)
    # Copy trace to WSL
    subprocess.run(["wsl", "-d", "Ubuntu", "--", "bash", "-c",
                   "cp /mnt/c/Users/gbust/Downloads/Academic/Courses/Machine_learning_in_wireless_network/Project1/Simulation/omnet_uav/traces/%s %s/traces/%s" % (trace_name, SCN, trace_name)],
                  capture_output=True, timeout=30)
    # Run
    run_cmd = ("cd %s && opp_env run inet-4.6.0 -c 'cd %s/examples/uav_omnet && opp_run -u Cmdenv "
               "-l %s/out/clang-release/src/libINET.so -n %s/src:%s/examples 2>&1 | tail -3' 2>&1 | tail -5") % (WSL, INET, INET, INET, INET)
    r = subprocess.run(["wsl", "-d", "Ubuntu", "--", "bash", "-c", run_cmd], capture_output=True, text=True, timeout=120)
    ok = "Simulation time limit reached" in r.stdout
    return ok, r.stdout[-100:]

def main():
    traces = ["episode_000.movements", "episode_001.movements"]
    results = []
    for t in traces:
        print(f"Running {t}...", flush=True)
        ok, out = run_scenario(t)
        print(f"  {'OK' if ok else 'FAIL'}")
        results.append({"trace": t, "success": ok})
    # Save
    out_path = os.path.join(PROJ, "Simulation", "omnet_uav", "stepB_results.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved {len(results)} results")

if __name__ == "__main__":
    main()
