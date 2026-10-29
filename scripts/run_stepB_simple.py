import subprocess, os, sys
WSL = "/home/gbust/omnetpp_ws"
INET = WSL + "/inet-4.6.0"
SCN = INET + "/examples/uav_omnet"
PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRACES_WIN = os.path.join(PROJ, "Simulation", "omnet_uav", "traces")

for t in ["episode_000.movements", "episode_001.movements"]:
    # update ini
    subprocess.run(["wsl","-d","Ubuntu","--","bash","-c",
        "sed -i 's|traces/[^ ]*\\.movements|traces/%s|' %s/omnetpp.ini" % (t, SCN)])
    # copy trace
    subprocess.run(["wsl","-d","Ubuntu","--","bash","-c",
        "cp /mnt/c/Users/gbust/Downloads/Academic/Courses/Machine_learning_in_wireless_network/Project1/Simulation/omnet_uav/traces/%s %s/traces/%s" % (t, SCN, t)])
    # run
    run_cmd = "cd %s && opp_env run inet-4.6.0 -c 'cd %s/examples/uav_omnet && opp_run -u Cmdenv -l %s/out/clang-release/src/libINET.so -n %s/src:%s/examples 2>&1 | tail -2' 2>&1 | tail -3" % (WSL, INET, INET, INET, INET)
    r = subprocess.run(["wsl","-d","Ubuntu","--","bash","-c", run_cmd], capture_output=True, text=True, timeout=120)
    ok = "Simulation time limit reached" in r.stdout
    print(f"{t}: {'OK' if ok else 'FAIL'}")
