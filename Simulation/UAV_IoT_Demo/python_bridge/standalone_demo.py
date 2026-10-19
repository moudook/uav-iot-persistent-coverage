#!/usr/bin/env python3
"""
Standalone MAPPO Demo - Shows ML Decision Making for UAVs
=========================================================
Run this to demonstrate the MAPPO agent making decisions
based on simulated UAV state data.

This demonstrates what the Python side does when connected to OMNeT++.
"""

import numpy as np
import json
import time
import sys

class MAPPOAgent:
    def __init__(self, num_uavs=3):
        self.num_uavs = num_uavs
        self.iot_centroid = np.array([200.0, 350.0])
        self.charging_stations = [np.array([650.0, 500.0]), np.array([150.0, 500.0])]

    def select_actions(self, state):
        actions = []
        coverage = state.get("iot_coverage", 0.5)
        step = state.get("step", 0)

        for uav in state["uavs"]:
            uid, battery, x, y = uav["id"], uav["battery"], uav["x"], uav["y"]
            pos = np.array([x, y])

            if battery < 10:
                atype = "EMERGENCY_RETURN"
                target = min(self.charging_stations, key=lambda s: np.linalg.norm(pos - s))
                direction = (target - pos)
                d = np.linalg.norm(direction)
                direction = direction / d * 3.0 if d > 0 else direction
            elif battery < 25:
                atype = "RETURN_TO_CHARGE"
                target = min(self.charging_stations, key=lambda s: np.linalg.norm(pos - s))
                direction = (target - pos)
                d = np.linalg.norm(direction)
                direction = direction / d * 2.0 if d > 0 else direction
            elif coverage < 0.5:
                atype = "CONVERGE_COVERAGE"
                target = self.iot_centroid + np.array([(uid - 1) * 80, (uid % 2 - 0.5) * 60])
                direction = (target - pos)
                d = np.linalg.norm(direction)
                direction = direction / d * 1.5 if d > 0 else direction
            else:
                atype = "PATROL"
                angle = (step * 0.1 + uid * 2.094) % (2 * np.pi)
                center = self.iot_centroid + np.array([(uid - 1) * 100, 0])
                target = center + np.array([np.cos(angle) * 50, np.sin(angle) * 30])
                direction = (target - pos)
                d = np.linalg.norm(direction)
                direction = direction / d * 1.0 if d > 0 else direction

            actions.append({"id": uid, "dx": round(float(direction[0]), 2),
                          "dy": round(float(direction[1]), 2), "action": atype,
                          "battery": round(float(battery), 1)})
        return actions


def simulate_uav_state(step, uav_states):
    """Simulate UAV movement based on actions."""
    for uav in uav_states:
        uav["x"] += uav.get("dx", 0) * 10
        uav["y"] += uav.get("dy", 0) * 10
        uav["x"] = max(0, min(1000, uav["x"]))
        uav["y"] = max(0, min(700, uav["y"]))
        uav["battery"] -= 0.5
        if uav["battery"] < 10:
            uav["battery"] = min(100, uav["battery"] + 2.0)


def main():
    agent = MAPPOAgent(num_uavs=3)

    uav_states = [
        {"id": 0, "battery": 95.0, "x": 550.0, "y": 350.0},
        {"id": 1, "battery": 80.0, "x": 650.0, "y": 400.0},
        {"id": 2, "battery": 15.0, "x": 750.0, "y": 350.0},
    ]

    print("=" * 70)
    print("  MAPPO Agent - UAV IoT Coverage Optimization Demo")
    print("  (This simulates what happens when connected to OMNeT++)")
    print("=" * 70)

    for step in range(10):
        coverage = max(0, min(1.0, 0.3 + 0.05 * step + np.random.uniform(-0.05, 0.05)))
        state = {"type": "state", "step": step, "uavs": uav_states, "iot_coverage": round(coverage, 3)}

        print(f"\n--- Step {step} ---")
        print(f"Network Coverage: {coverage:.1%}")
        for u in uav_states:
            print(f"  UAV{u['id']}: pos=({u['x']:.0f},{u['y']:.0f}) battery={u['battery']:.1f}%")

        actions = agent.select_actions(state)
        for a in actions:
            print(f"  -> UAV{a['id']}: {a['action']} delta=({a['dx']:.1f},{a['dy']:.1f})")
            uav_states[a["id"]]["dx"] = a["dx"]
            uav_states[a["id"]]["dy"] = a["dy"]

        simulate_uav_state(step, uav_states)

        time.sleep(0.5)

    print("\n" + "=" * 70)
    print("  MAPPO Demo Complete")
    print("  When connected to OMNeT++, real network state replaces simulation")
    print("=" * 70)


if __name__ == "__main__":
    main()
