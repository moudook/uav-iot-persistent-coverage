p = "/home/gbust/omnetpp_ws/inet-4.6.0/examples/uav_omnet/omnetpp.ini"
s = open(p).read()
s = s.replace("hosts='*'", "hosts='**'")
open(p, "w").write(s)
print("done")
print("configurator" in s)
