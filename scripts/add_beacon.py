p = "/home/gbust/omnetpp_ws/inet-4.6.0/examples/uav_omnet/omnetpp.ini"
s = open(p).read()
traffic = """# traffic: periodic beacons (UAV->broadcast) every 1s
*.uav[*].numApps = 1
*.uav[*].app[0].typename = "UdpBasicApp"
*.uav[*].app[0].destAddresses = "255.255.255.255"
*.uav[*].app[0].destPort = 1000
*.uav[*].app[0].messageLength = 64B
*.uav[*].app[0].sendInterval = 1s
*.uav[*].app[0].startTime = uniform(0s, 1s)
*.uav[*].app[0].localPort = 1000

"""
s = s.replace("**.scalar-recording", traffic + "**.scalar-recording", 1)
open(p, "w").write(s)
print("done")
