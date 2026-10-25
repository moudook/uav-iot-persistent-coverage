import re
mods = set()
with open("Simulation/omnet_uav/results/General-#0.sca") as f:
    for line in f:
        line = line.strip()
        if not line.startswith("scalar "):
            continue
        m = re.match(r'scalar\s+(\S+)\s+"([^"]+)"\s+(\S+)', line)
        if m:
            mods.add(m.group(1))
for m in sorted(mods):
    if "radio" in m.lower():
        print(m)
print("total radio modules:", sum(1 for m in mods if "radio" in m.lower()))
