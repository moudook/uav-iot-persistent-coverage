"""Which ini pattern actually reaches the mobility submodule?

Writes the same config three times with an invalid mobility type under
different patterns. A pattern that matches makes OMNeT++ fail loudly.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stepB_pair as sp
from stepB_channel import INI, run_inet

BASE = sp.INI_TMPL.format(d=200.0, amax=300.0, power="0.1", sens="-85", snir="4",
                          bitrate="6Mbps", interval=0.1, simtime=1.0, start1=0.05)

PATTERNS = [
    '**.uav[0].mobility.typename',
    '*.uav[*].mobility.typename',
    '**.**.mobility.typename',
    '**.mobility.typename',
]

for pat in PATTERNS:
    ini = BASE.replace('**.uav[*].mobility.typename = "StationaryMobility"',
                       f'{pat} = "NoSuchMobility"')
    assert "NoSuchMobility" in ini, pat
    open(INI, "w", newline="\n").write(ini)
    out = run_inet()
    hit = "NoSuchMobility" in out or "not found" in out.lower()
    print(f"{pat:42s} -> {'MATCHES' if hit else 'ignored'}", flush=True)
