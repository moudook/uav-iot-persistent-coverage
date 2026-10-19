#!/bin/bash
# ============================================================
# MAPPO + Simu5G Demo Launcher
# Starts both OMNeT++ simulation and Python MAPPO agent
# ============================================================
set -e

WORKSPACE="/home/gbust/omnetpp-workspace"
BRIDGE_DIR="$WORKSPACE/../../Downloads/Academic/Courses/Machine_learning_in_wireless_network/Project1/Simulation/UAV_IoT_Demo/python_bridge"

echo "============================================"
echo "  MAPPO + Simu5G Integrated Demo"
echo "============================================"
echo ""
echo "Architecture:"
echo "  Python MAPPO Agent  <--TCP:6543-->  OMNeT++ Simu5G"
echo "  (Decentralized)                     (5G UAV-IoT Network)"
echo ""

# Start Python MAPPO agent in background
echo "[1/2] Starting Python MAPPO agent on port 6543..."
python3 "$BRIDGE_DIR/mappo_agent.py" &
MAPPO_PID=$!
echo "  MAPPO PID: $MAPPO_PID"

sleep 2

# Start OMNeT++ simulation
echo "[2/2] Starting OMNeT++ Simu5G simulation..."
echo "  Click OK on the config dialog, then press Play to start"
echo ""
cd "$WORKSPACE"
export PATH="$HOME/.local/bin:$PATH"
opp_env run simu5g-1.4.3 -c "opp_run -u Qtenv -c UAVIoT -f omnetpp.ini"

# Cleanup
echo ""
echo "Stopping MAPPO agent..."
kill $MAPPO_PID 2>/dev/null || true
echo "Demo complete."
