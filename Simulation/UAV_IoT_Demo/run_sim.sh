#!/bin/bash
cd /home/gbust/omnetpp-workspace/simu5g-1.4.3/simulations/uav_iot_demo
echo "CWD=$(pwd)" > /home/gbust/omnetpp-workspace/sim_output.log
echo "=== Running ===" >> /home/gbust/omnetpp-workspace/sim_output.log
opp_run -u Cmdenv -c Demo -f omnetpp.ini >> /home/gbust/omnetpp-workspace/sim_output.log 2>&1
echo "=== EXIT: $? ===" >> /home/gbust/omnetpp-workspace/sim_output.log
