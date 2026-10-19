#!/bin/bash
export NEDPATH="/home/gbust/omnetpp-workspace/sim:/home/gbust/omnetpp-workspace/inet-4.6.0/src:/home/gbust/omnetpp-workspace/simu5g-1.4.3/src"
cd /home/gbust/omnetpp-workspace/sim
opp_run -u Cmdenv -c UAVIoT -f omnetpp.ini > /home/gbust/omnetpp-workspace/sim_result.log 2>&1
echo "EXIT_CODE=$?" >> /home/gbust/omnetpp-workspace/sim_result.log
