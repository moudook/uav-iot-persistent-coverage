"""Run INET Step A for multiple trace files and collect per-scenario delivery stats."""
import os, sys, subprocess, time, json, glob, shutil
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ml_impl"))

WSL_DIR = "/home/gbust/omnetpp_ws"
INET_DIR = WSL_DIR + "/inet-4.6.0"
SCN_DIR = INET_DIR + "/examples/uav_omnet"
TRACES_SRC = "/mnt/c/Users/gbust/Downloads/Academic/Courses/Machine_learning_in_wireless_network/Project1/Simulation/omnet_uav/traces"

def run_scenario(trace_name):
    """Run one INET scenario with the given trace file. Returns (trace_name, success)."""
    # Update omnetpp.ini traceFile
    ini_path = SCN_DIR + "/omnetpp.ini"
    # Use sed to replace traceFile
    cmd = f"sed -i 's|traces/episode_[0-9]*.movements|traces/{trace_name}|' {ini_path}"
    subprocess.run(["wsl", "-d", "Ubuntu", "--", "bash", "-c", cmd], capture_output=True)
    # Run simulation
    run_cmd = f"cd {WSL_DIR} && opp_env run inet-4.6.0 -c 'cd {INET_DIR}/examples/uav_omnet && opp_run -u Cmdenv -l {INET_DIR}/out/clang-release/src/libINET.so -n {INET_DIR}/src:{INET_DIR}/examples 2>&1 | tail -3' 2>&1 | tail -5"
    r = subprocess.run(["wsl", "-d", "Ubuntu", "--", "bash", "-c", run_cmd], capture_output=True, text=True, timeout=120)
    success = "Simulation time limit reached" in r.stdout
    return trace_name, success, r.stdout[-200:]

def main():
    traces = sorted(glob.glob("Simulation/omnet_uav/traces/episode_*.movements"))
    print(f"Found {len(traces)} trace files")
    results = []
    for tf in traces:
        name = os.path.basename(tf)
        print(f"Running {name}...", flush=True)
        tn, ok, out = run_scenario(name)
        print(f"  {name}: {'OK' if ok else 'FAIL'}")
        results.append({"trace": name, "success": ok})
    # Save
    out_path = "Simulation/omnet_uav/stepA_results.json"
    with open(out_path, "w") as f:
        import json
        json.dump(results, f, indent=2)
    print(f"Saved {len(results)} results to {out_path}")

if __name__ == "__main__":
    main()
