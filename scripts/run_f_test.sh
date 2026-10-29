#!/bin/bash
cd /home/gbust/omnetpp_ws/uavsim
opp_env run inet-4.6.0 -c 'opp_run -u Cmdenv -f /home/gbust/omnetpp_ws/uavsim/test_run.ini -r 0 -l /home/gbust/omnetpp_ws/inet-4.6.0/out/clang-release/src/libINET.so -n /home/gbust/omnetpp_ws/inet-4.6.0/src:/home/gbust/omnetpp_ws/inet-4.6.0/examples:/home/gbust/omnetpp_ws/uavsim' 2>&1 | tail -8
