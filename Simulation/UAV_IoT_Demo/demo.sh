#!/bin/bash
# ============================================================
# Quick Demo Script for Professor Presentation
# UAV-IoT MAPPO Simulation
# ============================================================
set -e

echo "============================================"
echo "  UAV-IoT MAPPO Simulation - Quick Demo"
echo "============================================"
echo ""

# Check we are in WSL
if grep -qi microsoft /proc/version 2>/dev/null; then
    echo "[OK] Running in WSL"
else
    echo "[WARN] Not running in WSL - some steps may differ"
fi

# Check opp_env is available
if ! command -v opp_env &> /dev/null; then
    echo "[ERROR] opp_env not found. Please install OMNeT++ first."
    echo "  Run: opp_env setup --download --force -o /opt/omnetpp -r 'omnetpp-6.0.3'"
    exit 1
fi

echo ""
echo "Step 1: Building simulation..."
echo "-------------------------------"

# Enter the workspace
WORKSPACE=$(find /opt -maxdepth 3 -name "uav_iot_demo" -type d 2>/dev/null | head -1)
if [ -z "$WORKSPACE" ]; then
    WORKSPACE=$(find ~/omnetpp* -maxdepth 3 -name "uav_iot_demo" -type d 2>/dev/null | head -1)
fi

if [ -z "$WORKSPACE" ]; then
    echo "[INFO] Workspace not found in standard locations."
    echo "  Please navigate to your workspace directory and run:"
    echo "  opp_run -u Cmdenv -c Demo -f simulations/omnetpp.ini"
    exit 1
fi

cd "$WORKSPACE"

# Build the project
if command -v make &> /dev/null; then
    make
elif command -v opp_makemake &> /dev/null; then
    opp_makemake -f src/uav_iot_demo --deep -o uav_iot_demo
    make
fi

echo ""
echo "Step 2: Starting Python bridge (background)..."
echo "----------------------------------------------"

cd python_bridge
python3 omnetpp_bridge.py &
BRIDGE_PID=$!
cd ..

sleep 2
echo "[OK] Bridge started (PID: $BRIDGE_PID)"

echo ""
echo "Step 3: Launching OMNeT++ simulation..."
echo "----------------------------------------"
echo "  - Config: Demo (5 min sim-time)"
echo "  - Network: UAVIoTNetwork"
echo "  - UAVs: 3 | IoT Nodes: 10 | Charging Stations: 2"
echo ""

# Run the simulation
opp_run -u Qtenv -c Demo -f simulations/omnetpp.ini \
    --record-eventlog=true \
    --vector-recording=true

echo ""
echo "Step 4: Cleaning up..."
kill $BRIDGE_PID 2>/dev/null || true
echo "[OK] Bridge stopped"

echo ""
echo "============================================"
echo "  Demo Complete!"
echo "============================================"
echo ""
echo "Results saved in: results/"
echo "Open scalar/vector files in OMNeT++ to view statistics."
echo ""
