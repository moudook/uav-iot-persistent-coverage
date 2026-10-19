#!/bin/bash
set -e
TARGET=/home/gbust/omnetpp-workspace/run_clean
mkdir -p $TARGET
cp /home/gbust/omnetpp-workspace/simu5g-1.4.3/simulations/uav_iot_demo/* $TARGET/
cd $TARGET
opp_run -u Cmdenv -c UAVIoT -f omnetpp.ini 2>&1
echo "EXIT_CODE=$?"
