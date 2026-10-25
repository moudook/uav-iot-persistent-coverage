p = "/home/gbust/omnetpp_ws/inet-4.6.0/examples/uav_omnet/UavNetwork.ned"
s = open(p).read()
# remove visualizer block
import re
s = re.sub(r"        visualizer:.*?\n        \}\n", "", s, count=1, flags=re.DOTALL)
s = s.replace("import inet.visualizer.contract.IIntegratedVisualizer;\n", "")
open(p, "w").write(s)
print("done")
# verify
for line in s.splitlines():
    if "visualizer" in line.lower():
        print("  ", line.strip())
print("no visualizer" if "visualizer" not in s.lower() else "still has visualizer")
