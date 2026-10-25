p = "/home/gbust/omnetpp_ws/inet-4.6.0/examples/uav_omnet/UavNetwork.ned"
s = open(p).read()
s = s.replace("        int numSensors;\n        string traceFile;", "        int numSensors;")
s = s.replace('                mobility.traceFile = traceFile;', '                mobility.traceFile = "traces/episode_000.movements";')
open(p, "w").write(s)
print("done")
print("traceFile" in s)
