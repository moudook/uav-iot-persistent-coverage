"""
Mutation check: does the test suite actually have teeth?

A green test suite proves nothing on its own -- tests that pass on broken code
are worse than no tests, because they manufacture false confidence. This script
deliberately re-introduces each historical defect, runs the suite, and asserts
that at least one test FAILS. If a mutation survives, the corresponding test is
decoration and must be fixed.

Every mutation below is a real bug that was actually found in this codebase.

Usage:  python tests/mutation_check.py
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# name -> (relative file, exact text to find, replacement text, why it was a bug)
MUTATIONS = {
    "reward_sign_only_U_t": (
        "uav_wireless/env.py",
        '        cost = (\n            c.lam_O * terms["U_t"]\n            + c.lam_E * terms["E_t"]\n            + c.lam_D * terms["D_t"]\n            + c.lam_W * terms["W_t"]\n            + c.lam_R * terms["R_t"]\n        )\n        if c.use_connectivity_term:\n            cost += c.lam_C * terms["Crit_t"]\n        return -float(cost)',
        '        return -float(c.lam_O * terms["U_t"]) + float(\n            c.lam_E * terms["E_t"]\n            + c.lam_D * terms["D_t"]\n            + c.lam_W * terms["W_t"]\n            + c.lam_R * terms["R_t"]\n            + (c.lam_C * terms["Crit_t"] if c.use_connectivity_term else 0.0)\n        )',
        "only U_t negated: energy/service/movement/recovery/criticality get rewarded",
    ),
    "backhaul_cochannel_interference": (
        "uav_wireless/wireless.py",
        "        snr = rx / self.noise_w\n        snr = 0.5 * (snr + snr.T)          # enforce reciprocity exactly",
        "        total = rx.sum(axis=1, keepdims=True)\n        snr = rx / np.maximum(total - rx, 1e-12)\n        snr = 0.5 * (snr + snr.T)",
        "every other UAV counted as a co-channel interferer on the relay link",
    ),
    "random_initial_deployment": (
        "uav_wireless/env.py",
        "        self.p = self._connected_initial_positions()",
        "        self.p = self.rng.uniform(0, c.side, size=(c.N, 2))",
        "uniformly random start leaves the swarm disconnected on ~half of seeds",
    ),
    "rate_floor_disables_phy_gate": (
        "uav_wireless/wireless.py",
        '    idx = np.searchsorted(MCS_TABLE[:, 0], v, side="right") - 1\n    rate = np.where(idx >= 0, MCS_TABLE[np.clip(idx, 0, None), 1], 0.0)',
        '    idx = np.searchsorted(MCS_TABLE[:, 0], v, side="left")\n    rate = MCS_TABLE[np.clip(idx, 0, len(MCS_TABLE) - 1), 1]',
        "side='left' + floor at the lowest MCS: claims a rate the link cannot "
        "carry and makes rate >= rate_min_mbps always true",
    ),
    "path_loss_exponent_additive": (
        "uav_wireless/wireless.py",
        "    return pl_d0 + 10.0 * n * np.log10(d / d0)",
        "    return 20.0 * np.log10(d / d0) + pl_d0 + n * np.log10(d / d0)",
        "exponent added on top of the free-space slope: n=3.5 acts like 2.35, "
        "erasing the LoS/NLoS distinction",
    ),
    "observation_neighbour_stride": (
        "uav_wireless/env.py",
        "                nb[4 * k + 0] = rel[0]\n                nb[4 * k + 1] = rel[1]\n                nb[4 * k + 2] = self.E[j] / c.B_max\n                nb[4 * k + 3] = d / c.R_comm",
        "                nb[2 * k + 0] = rel[0]\n                nb[2 * k + 1] = rel[1]",
        "stride 2 for 4 fields per neighbour: slots overlap and later "
        "neighbours overwrite the tail features",
    ),
    "state_dim_hardcoded": (
        "uav_wireless/env.py",
        "    return 2 * cfg.N + 3 * cfg.N + 2 * cfg.M + cfg.n_pads + 3",
        "    return 80",
        "state dimension fixed at the N=5 value: overflows for N>=8 and "
        "misaligns in between",
    ),
    "access_every_uav_cochannel": (
        "uav_wireless/wireless.py",
        "        access_cochannel: int = 0,     # other UAVs sharing a sensor's channel",
        "        access_cochannel: int = 4,     # other UAVs sharing a sensor's channel",
        "all UAVs modelled as co-channel interferers on the access link",
    ),
    "non_reciprocal_shadowing": (
        "uav_wireless/wireless.py",
        "        z = np.triu(z, 1)                    # strict upper triangle only\n        self.shadow_uu_db = z + z.T          # mirror => S(i,j) == S(j,i)",
        "        self.shadow_uu_db = z",
        "per-element shadowing: S(i,j) != S(j,i), so a link has two different "
        "channels depending on which end you measure from",
    ),
    "channel_redrawn_per_evaluation": (
        "uav_wireless/wireless.py",
        "        if shadow_db is not None:\n            pl = pl + shadow_db",
        "        pl = pl + np.random.normal(\n            0.0, self.shadowing_sigma_db, size=np.shape(pl)\n        )",
        "shadowing drawn per call from the global RNG: the propagation "
        "environment changes on every link evaluation and with the number of "
        "nodes in the array",
    ),
}


def run_suite(workdir: str) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, os.path.join("tests", "run_tests.py"), "-q"],
        cwd=workdir, capture_output=True, text=True,
    )
    return proc.returncode, proc.stdout + proc.stderr


def main() -> int:
    print("baseline (unmutated) ...", end=" ", flush=True)
    code, out = run_suite(ROOT)
    if code != 0:
        print("FAILED")
        print(out)
        print("!! the unmutated suite is already red; fix that first")
        return 2
    print("green")

    survivors = []
    for name, (relpath, old, new, why) in MUTATIONS.items():
        src = os.path.join(ROOT, relpath)
        with open(src, encoding="utf-8") as f:
            original = f.read()
        if old not in original:
            print(f"{name:34s} SKIP (anchor not found in {relpath})")
            survivors.append((name, "anchor not found -- mutation check is stale"))
            continue

        backup = original.replace(old, new, 1)
        try:
            with open(src, "w", encoding="utf-8") as f:
                f.write(backup)
            code, out = run_suite(ROOT)
        finally:
            with open(src, "w", encoding="utf-8") as f:
                f.write(original)

        m = re.search(r"(\d+) passed, (\d+) failed", out)
        detail = m.group(0) if m else "no summary"
        if code != 0:
            print(f"{name:34s} CAUGHT   ({detail})")
        else:
            print(f"{name:34s} SURVIVED ({detail})  <- {why}")
            survivors.append((name, why))

    print("-" * 66)
    if survivors:
        print(f"{len(survivors)} mutation(s) survived -- tests are too weak:")
        for name, why in survivors:
            print(f"  - {name}: {why}")
        return 1
    print(f"all {len(MUTATIONS)} historical bugs are caught by the suite")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
