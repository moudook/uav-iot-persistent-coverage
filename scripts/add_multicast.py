p = "/home/gbust/omnetpp_ws/inet-4.6.0/examples/uav_omnet/omnetpp.ini"
s = open(p).read()

# Remove existing traffic section
if "# traffic:" in s:
    idx = s.find("# traffic:")
    rec_idx = s.find("# recording")
    s = s[:idx] + s[rec_idx:]

traffic = """# traffic: periodic beacons (UAV->all others) every 1s
*.uav[*].numApps = 1
*.uav[*].app[0].typename = "UdpBasicApp"
*.uav[*].app[0].destAddresses = "uav[0] uav[1] uav[2] uav[3] uav[4] uav[5] uav[6] uav[7]"
*.uav[*].app[0].destPort = 1000
*.uav[*].app[0].messageLength = 64B
*.uav[*].app[0].sendInterval = 1s
*.uav[*].app[0].startTime = uniform(0s, 1s)
*.uav[*].app[0].localPort = 1000

"""
s = s.replace("# recording", traffic + "# recording", 1)
open(p, "w").write(s)
print("done")
