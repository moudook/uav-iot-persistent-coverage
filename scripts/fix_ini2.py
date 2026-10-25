p = "/home/gbust/omnetpp_ws/inet-4.6.0/examples/uav_omnet/omnetpp.ini"
s = open(p).read()
s = s.replace(
    '**.sensor[*].mobility.typename = "StationaryMobility"\n**.sensor[*].mobility.initialX = uniform(0m, 80m)',
    '**.sensor[*].mobility.typename = "StationaryMobility"\n**.sensor[*].mobility.initFromDisplayString = false\n**.sensor[*].mobility.initialX = uniform(0m, 80m)')
s = s.replace(
    '**.sink.mobility.typename = "StationaryMobility"\n**.sink.mobility.initialX = 40m',
    '**.sink.mobility.typename = "StationaryMobility"\n**.sink.mobility.initFromDisplayString = false\n**.sink.mobility.initialX = 40m')
open(p, "w").write(s)
print("done")
