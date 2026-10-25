import re
scalars = {}
with open("Simulation/omnet_uav/results/General-#0.sca") as f:
    for line in f:
        line = line.strip()
        if not line.startswith("scalar "):
            continue
        m = re.match(r'scalar\s+(\S+)\s+"([^"]+)"\s+(\S+)', line)
        if m:
            mod, name, val = m.group(1), m.group(2), m.group(3)
            scalars.setdefault(mod, {})[name] = val
radio_mods = [m for m in scalars if "radio" in m]
print("radio modules:", len(radio_mods))
if radio_mods:
    m = radio_mods[0]
    print("module:", m)
    for k in sorted(scalars[m])[:10]:
        print("  " + k + " = " + scalars[m][k])
