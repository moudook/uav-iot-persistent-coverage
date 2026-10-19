"""
Choosing an episode in which the energy constraint actually binds.

WHY
  In the reported configuration the battery never depletes inside an
  episode, so the return-to-charge transition never fires, the charging
  arbitration is never exercised, and the reserve-UAV mechanism has nothing
  to recover.  The paper proposes all three, so a regime in which they never
  activate is a regime in which they are not tested.

  The probe uses the Reactive heuristic, which already implements the
  return-to-pad behaviour, so it shows what the energy model does to a
  competent controller.  The question is not "which configuration gives the
  best number" but "which configuration makes the constraint ACTIVE while
  leaving the mission achievable".

CRITERIA
  binds     : the return-to-charge state is entered (ReturnEvents > 0)
  reachable : charging pads are actually reached (Charging steps > 0)
  survivable: most of the swarm is still operational at the end
  covered   : the coverage target is still attainable

Run:  python analysis/energy_regime.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np

from uav_wireless.env import SimConfig
from uav_wireless.train import baseline_reactive

HERE = os.path.dirname(os.path.abspath(__file__))


def probe(ep_len, b_max, charge_rate, e_reserve=2000.0, label=""):
    cfg = SimConfig(N=8, K=2, R_cov=35.0, M=20, episode_len=ep_len,
                    B_max=b_max, charge_rate=charge_rate,
                    E_reserve=e_reserve, n_pads=2, seed=0,
                    start_clustered=True, use_agent_id=True, map_grid=4,
                    use_pad_bearing=True)
    evs = [baseline_reactive(cfg, steps=ep_len, seed=s) for s in range(3)]
    agg = {k: float(np.mean([x[k] for x in evs])) for k in evs[0]}
    return dict(
        label=label, ep_len=ep_len, B_max=b_max, charge_rate=charge_rate,
        E_reserve=e_reserve,
        CK=agg["CK"], AG=agg["AG"], SC=agg["SC"],
        ReturnEvents=agg["ReturnEvents"], Stranded=agg["Stranded"],
        Returning=agg["Returning"], Denied=agg["Denied"],
        Reserve=agg["Reserve"], MinBattery=agg["MinBattery"],
        Energy=agg["Energy"])


def main():
    print("=" * 100)
    print(" ENERGY REGIME SWEEP (Reactive heuristic, 3 seeds, clustered start)")
    print("=" * 100)
    hdr = (f"{'label':<30}{'ep':>6}{'B_max':>8}{'chg':>8}{'Eres':>7}"
           f"{'CK':>7}{'AG':>7}{'SC':>7}{'retEv':>7}{'strnd':>7}"
           f"{'charg':>7}{'deny':>6}{'minE':>7}")
    print(hdr)

    candidates = [
        (400, 30000, 0.0002, 2000.0, "current"),
        (1000, 15000, 0.0020, 2000.0, "1000 steps, 15 kJ, fast charge"),
        (1000, 20000, 0.0020, 2000.0, "1000 steps, 20 kJ, fast charge"),
        (1000, 15000, 0.0010, 2000.0, "1000 steps, 15 kJ, slow charge"),
        (1500, 20000, 0.0020, 2000.0, "1500 steps, 20 kJ, fast charge"),
        (1500, 30000, 0.0020, 2000.0, "1500 steps, 30 kJ, fast charge"),
        (2000, 30000, 0.0020, 2000.0, "2000 steps, 30 kJ, fast charge"),
        (2000, 30000, 0.0010, 2000.0, "2000 steps, 30 kJ, slow charge"),
    ]
    rows = []
    for ep_len, b_max, cr, er, label in candidates:
        r = probe(ep_len, b_max, cr, er, label)
        rows.append(r)
        print(f"{r['label']:<30}{r['ep_len']:>6}{r['B_max']:>8.0f}"
              f"{r['charge_rate']:>8.4f}{r['E_reserve']:>7.0f}"
              f"{r['CK']:>7.3f}{r['AG']:>7.3f}{r['SC']:>7.3f}"
              f"{r['ReturnEvents']:>7.0f}{r['Stranded']:>7.1f}"
              f"{r['Returning']:>7.3f}{r['Denied']:>6.0f}{r['MinBattery']:>7.0f}",
              flush=True)

    import json
    out = os.path.join(HERE, "energy_regime.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)
    print(f"\nSaved -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
