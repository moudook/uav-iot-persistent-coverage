#!/bin/bash
cd /home/gbust/omnetpp_ws
rm -rf omnetpp-6.4.0
opp_env run omnetpp-6.4.0 --install --chdir -c './configure && make -j4' > /tmp/opp_build.log 2>&1
echo DONE_INSTALL >> /tmp/opp_build.log
