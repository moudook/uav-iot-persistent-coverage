#!/bin/bash
export OMNETPP_NED_PACKAGE_EXCLUSIONS="inet-4.6.0;simu5g-1.4.3;omnetpp-6.4.0"
cd /home/gbust/omnetpp-workspace
opp_run -u Cmdenv -c UAVIoT -f omnetpp.ini > /home/gbust/omnetpp-workspace/sim_result.log 2>&1
echo "EXIT=$?" >> /home/gbust/omnetpp-workspace/sim_result.log
