import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stepB_pair as sp
from stepB_channel import INI, run_inet

# Rebuild the ini exactly as stepB_pair does, then corrupt the typename.
sp.run_point  # noqa
amax = 200.0
tmpl = sp.INI_TMPL
ini = tmpl.format(d=400.0, amax=amax, power="0.1", sens="-85", snir="4",
                  bitrate="6Mbps", interval=0.1, simtime=2.0, start1=0.05)
base_ok = '**.uav[*].mobility.typename = "StationaryMobility"' in ini
print("template has typename line:", base_ok)
open(INI, "w", newline="\n").write(ini.replace("StationaryMobility", "NoSuchMobility"))
out = run_inet()
print("--- tail ---")
for l in [x for x in out.splitlines() if x.strip()][-10:]:
    print("   ", l.strip()[:200])
