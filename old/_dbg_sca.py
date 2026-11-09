import glob
files = glob.glob(r"\\wsl.localhost\Ubuntu\home\gbust\omnetpp_ws\uavsim\results\*.sca")
path = files[0] if files else None
print("using", path)
for line in open(path, errors="replace"):
    s = line.strip()
    if "sendInterval" in s or "startTime" in s or "packets sent" in s:
        print(s)
