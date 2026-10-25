p = "/home/gbust/omnetpp_ws/inet-4.6.0/examples/uav_omnet/omnetpp.ini"
s = open(p).read()
old = """# sensor mobility: stationary
**.sensor[*].mobility.typename = "StationaryMobility"
**.sink.mobility.typename = "StationaryMobility"
"""
new = """# sensor mobility: stationary, random positions within area
**.sensor[*].mobility.typename = "StationaryMobility"
**.sensor[*].mobility.initialX = uniform(0m, 80m)
**.sensor[*].mobility.initialY = uniform(0m, 80m)
**.sink.mobility.typename = "StationaryMobility"
**.sink.mobility.initialX = 40m
**.sink.mobility.initialY = 40m
"""
assert old in s, "old not found"
s = s.replace(old, new)
open(p, "w").write(s)
print("done")
