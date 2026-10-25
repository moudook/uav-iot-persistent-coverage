p = "/home/gbust/omnetpp_ws/inet-4.6.0/examples/uav_omnet/omnetpp.ini"
s = open(p).read()
s = s.replace('*.uav[*].app[0].destAddresses = "255.255.255.255"', '*.uav[*].app[0].destAddresses = "uav[1]"')
open(p, "w").write(s)
print("done")
# verify
for line in s.splitlines():
    if "destAddresses" in line:
        print("  " + line)
