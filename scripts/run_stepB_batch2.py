"""Step B: run INET scenarios with different traces, collect delivery stats."""
import os, sys, subprocess, time, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ml_impl"))

WSL = "/home/gbust/omnetpp_ws"
INET = WSL + "/inet-4.6.0"
SCN = INET + "/examples/uav_omnet"
PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRACES_WIN = os.path.join(PROJ, "Simulation", "omnet_uav", "traces")
TRACES_WSL = SCN + "/traces"

def gen_trace(seed, idx):
    """Generate one trace file with given seed."""
    import subprocess
    out_dir = os.path.join(PROJ, "Simulation", "omnet_uav", "traces_tmp")
    os.makedirs(out_dir, exist_ok=True)
    cmd = [sys.executable, os.path.join(PROJ, "scripts", "export_trajectories.py"),
           "--episodes", "1", "--seed", str(seed),
           "--out", out_dir]
    subprocess.run(cmd, capture_output=True)
    src = os.path.join(out_dir, "episode_000.movements")
    dst = os.path.join(TRACES_WIN, f"stepB_{idx:03d}.movements")
    if os.path.exists(src):
        os.replace(src, dst)
    # cleanup
    import shutil
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)
    return dst

def run_one(trace_name):
    # Update ini traceFile
    cmd = "sed -i 's|traces/[^ ]*\\.movements|traces/%s|' %s/omnetpp.ini" % (trace_name, SCN)
    subprocess.run(["wsl", "-d", "Ubuntu", "--", "bash", "-c", cmd], capture_output=True, timeout=30)
    # Copy trace to WSL
    subprocess.run(["wsl", "-d", "Ubuntu", "--", "bash", "-c",
                   "cp /mnt/c/Users/gbust/Downloads/Academic/Courses/Machine_learning_in_wireless_network/Project1/Simulation/omnet_uav/traces/%s %s/traces/%s" % (trace_name, SCN, trace_name)],
                  capture_output=True, timeout=30)
    # Run
    run_cmd = ("cd %s && opp_env run inet-4.6.0 -c 'cd %s/examples/uav_omnet && opp_run -u Cmdenv "
               "-l %s/out/clang-release/src/libINET.so -n %s/src:%s/examples 2>&1 | tail -2' 2>&1 | tail -3") % (WSL, INET, INET, INET, INET)
    r = subprocess.run(["wsl", "-d", "Ubuntu", "--", "bash", "-c", run_cmd], capture_output=True, text=True, timeout=120)
    ok = "Simulation time limit reached" in r.stdout
    return ok

def parse_results():
    """Parse the .sca file for delivery stats."""
    sca_path = os.path.join(PROJ, "Simulation", "omnet_uav", "results", "General-#0.sca")
    # Copy from WSL
    subprocess.run(["wsl", "-d", "Ubuntu", "--", "bash", "-c",
                   "cp %s/examples/uav_omnet/results/General-#0.sca /mnt/c/Users/gbust/Downloads/Academic/Courses/Machine_learning_in_wireless_network/Project1/Simulation/omnet_uav/results/General-#0.sca" % SCN],
                  capture_output=True, timeout=30)
    import re
    scalars = {}
    with open(sca_path) as f:
        for line in f:
            line = line.strip()
            if not line.startswith("scalar "):
                continue
            m = re.match(r'scalar\s+(\S+)\s+"([^"]+)"\s+(\S+)', line)
            if m:
                mod, name, val = m.group(1), m.group(2), m.group(3)
                try:
                    scalars.setdefault(mod, {})[name] = float(val)
                except ValueError:
                    pass
    # Extract per-UAV sent/received
    results = []
    for mod, vals in scalars.items():
        if "uav[" in mod and ".app[0]" in mod:
            uid = mod.split("uav[")[1].split("]")[0]
            results.append({
                "uav": int(uid),
                "sent": vals.get("packets sent", 0),
                "received": vals.get("packets received", 0),
            })
    total_sent = sum(r["sent"] for r in results)
    total_rx = sum(r["received"] for r in results)
    pdr = total_rx / total_sent if total_sent > 0 else 0
    return total_sent, total_rx, pdr

def main():
    n_scenarios = 5
    seeds = list(range(n_scenarios))
    print(f"Generating {n_scenarios} trace files...")
    gen_trace(0, 0)
    
    all_results = []
    for i in range(n_scenarios):
        name = f"stepB_{i:03d}.movements"
        # rename the generated file
        src = os.path.join(TRACES_WIN, f"scenario_{i:03d}.movements")
        dst = os.path.join(TRACES_WIN, name)
        if os.path.exists(src):
            os.replace(src, dst)
        print(f"Running scenario {i} ({name})...", flush=True)
        ok = run_one(name)
        if ok:
            sent, rx, pdr = parse_results()
            print(f"  OK: sent={sent} rx={rx} PDR={pdr:.4f}")
            all_results.append({"scenario": i, "trace": name, "sent": sent, "received": rx, "pdr": pdr})
        else:
            print(f"  FAIL")
            all_results.append({"scenario": i, "trace": name, "success": False})
    
    out_path = os.path.join(PROJ, "Simulation", "omnet_uav", "stepB_results.json")
    with open(out_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"Saved {len(all_results)} results to {out_path}")

if __name__ == "__main__":
    main()
