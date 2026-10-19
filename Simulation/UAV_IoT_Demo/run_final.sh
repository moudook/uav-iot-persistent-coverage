#!/bin/bash
echo "SCRIPT_EXECUTING" > /home/gbust/omnetpp-workspace/run_result.txt
export NEDPATH="/home/gbust/omnetpp-workspace/inet-4.6.0/src:/home/gbust/omnetpp-workspace/simu5g-1.4.3/src:/home/gbust/omnetpp-workspace/sim"
cd /home/gbust/omnetpp-workspace/sim
opp_run -u Cmdenv -c UAVIoT -f omnetpp.ini 2>&1 | grep -v "Loading NED" | tail -50 >> /home/gbust/omnetpp-workspace/run_result.txt
echo "SCRIPT_DONE" >> /home/gbust/omnetpp-workspace/run_result.txt
