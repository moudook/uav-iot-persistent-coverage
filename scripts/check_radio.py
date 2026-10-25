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
            try:
                scalars.setdefault(mod, {})[name] = float(val)
            except ValueError:
                pass
for mod, vals in scalars.items():
    if "uav[0].wlan[0].radio" in mod:
        for k, v in vals.items():
            if "transmit" in k.lower() or "received" in k.lower() or "sent" in k.lower():
                print("  " + k + " = " + str(v))
print("---done---")
