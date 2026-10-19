#!/bin/bash
mkdir -p /home/gbust/omnetpp-workspace/run_dir
cp /home/gbust/omnetpp-workspace/omnetpp.ini /home/gbust/omnetpp-workspace/run_dir/
cp /home/gbust/omnetpp-workspace/UAVIoTNetwork.ned /home/gbust/omnetpp-workspace/run_dir/
cd /home/gbust/omnetpp-workspace/run_dir
opp_run -u Cmdenv -c Demo -f omnetpp.ini -n /home/gbust/omnetpp-workspace/run_dir,/home/gbust/omnetpp-workspace/inet-4.6.0/src,/home/gbust/omnetpp-workspace/simu5g-1.4.3/src
