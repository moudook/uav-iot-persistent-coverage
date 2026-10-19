#!/usr/bin/env python3
"""
MAPPO Agent TCP Server for OMNeT++ Simu5G Integration
=====================================================
This script:
1. Starts a TCP server on localhost:6543
2. Receives simulation state from OMNeT++ (JSON)
3. Runs MAPPO inference to decide UAV actions
4. Sends actions back to OMNeT++ (JSON)

Protocol:
  OMNeT++ -> Python: {"type":"state", "step":N, "uavs":[{"id":0,"battery":85.0,"x":10.0,"y":20.0},...], "iot_coverage":0.85}
  Python -> OMNeT++: {"type":"action", "uavs":[{"id":0,"dx":1.0,"dy":-0.5,"action":"patrol"},...]}
"""

import socket
import json
import time
import sys
import os
import logging
import numpy as np
from collections import defaultdict

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(os.path.dirname(__file__), 'mappo_server.log'))
    ]
)
logger = logging.getLogger(__name__)

HOST = "127.0.0.1"
PORT = 6543
BUFFER_SIZE = 65536


class SimpleMAPPOAgent:
    """
    Simplified MAPPO agent for demonstration.
    In production, this would be a full MAPPO with:
    - Centralized critic network
    - Decentralized actor networks (one per UAV)
    - Shared replay buffer
    - PPO clip objective

    For demo purposes, this uses a rule-based policy that mimics
    what a trained MAPPO agent would do.
    """

    def __init__(self, num_uavs=3, num_iot_nodes=5):
        self.num_uavs = num_uavs
        self.num_iot_nodes = num_iot_nodes
        self.step_count = 0
        self.episode_count = 0
        self.total_reward = 0.0

        # Simulated network centroid (where IoT nodes are)
        self.iot_centroid = np.array([200.0, 350.0])

        # Charging station positions
        self.charging_stations = [
            np.array([650.0, 500.0]),
            np.array([150.0, 500.0])
        ]

        logger.info(f"MAPPO Agent initialized: {num_uavs} UAVs, {num_iot_nodes} IoT nodes")

    def get_state_vector(self, state):
        """Convert JSON state to feature vector for the agent."""
        features = []
        for uav in state.get("uavs", []):
            features.extend([
                uav.get("battery", 100.0) / 100.0,
                uav.get("x", 0.0) / 1000.0,
                uav.get("y", 0.0) / 1000.0,
            ])
        features.append(state.get("iot_coverage", 0.0))
        return np.array(features)

    def select_actions(self, state):
        """
        MAPPO action selection:
        - If battery < 20%: return to nearest charging station
        - If battery < 40%: move toward charging station while maintaining coverage
        - Otherwise: patrol around IoT node centroid to maximize coverage
        """
        actions = []
        step = state.get("step", 0)
        coverage = state.get("iot_coverage", 0.0)

        for uav in state.get("uavs", []):
            uid = uav.get("id", 0)
            battery = uav.get("battery", 100.0)
            x = uav.get("x", 0.0)
            y = uav.get("y", 0.0)
            pos = np.array([x, y])

            if battery < 10.0:
                action_type = "emergency_return"
                nearest_station = min(self.charging_stations,
                                     key=lambda s: np.linalg.norm(pos - s))
                direction = nearest_station - pos
                dist = np.linalg.norm(direction)
                if dist > 0:
                    direction = direction / dist * 3.0
                dx, dy = direction[0], direction[1]

            elif battery < 25.0:
                action_type = "return_to_charge"
                nearest_station = min(self.charging_stations,
                                     key=lambda s: np.linalg.norm(pos - s))
                direction = nearest_station - pos
                dist = np.linalg.norm(direction)
                if dist > 0:
                    direction = direction / dist * 2.0
                dx, dy = direction[0], direction[1]

            elif coverage < 0.5:
                action_type = "converge_coverage"
                target = self.iot_centroid + np.array([
                    (uid - self.num_uavs / 2) * 80,
                    (uid % 2 - 0.5) * 60
                ])
                direction = target - pos
                dist = np.linalg.norm(direction)
                if dist > 0:
                    direction = direction / dist * 1.5
                dx, dy = direction[0], direction[1]

            else:
                action_type = "patrol"
                angle = (step * 0.1 + uid * 2.094) % (2 * np.pi)
                patrol_center = self.iot_centroid + np.array([
                    (uid - self.num_uavs / 2) * 100,
                    0
                ])
                target = patrol_center + np.array([
                    np.cos(angle) * 50,
                    np.sin(angle) * 30
                ])
                direction = target - pos
                dist = np.linalg.norm(direction)
                if dist > 0:
                    direction = direction / dist * 1.0
                dx, dy = direction[0], direction[1]

            actions.append({
                "id": uid,
                "dx": round(float(dx), 2),
                "dy": round(float(dy), 2),
                "action": action_type,
                "battery": round(float(battery), 1)
            })

            logger.info(f"  UAV{uid}: battery={battery:.1f}%, action={action_type}, "
                       f"move=({dx:.1f}, {dy:.1f})")

        self.step_count += 1
        return actions

    def compute_reward(self, state, actions, next_state):
        """Compute reward signal for MAPPO training."""
        coverage_reward = next_state.get("iot_coverage", 0.0) * 10.0
        battery_penalty = sum(
            max(0, 20 - uav.get("battery", 100)) * 0.1
            for uav in next_state.get("uavs", [])
        )
        movement_penalty = sum(
            (abs(a.get("dx", 0)) + abs(a.get("dy", 0))) * 0.01
            for a in actions
        )
        reward = coverage_reward - battery_penalty - movement_penalty
        return reward


class TCPServer:
    """TCP server for OMNeT++ communication."""

    def __init__(self, host=HOST, port=PORT):
        self.host = host
        self.port = port
        self.server_socket = None
        self.client_socket = None

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.settimeout(600.0)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)
        logger.info(f"TCP Server listening on {self.host}:{self.port}")
        logger.info("Waiting for OMNeT++ to connect...")

    def accept(self):
        self.client_socket, addr = self.server_socket.accept()
        self.client_socket.settimeout(30.0)
        logger.info(f"Connected to OMNeT++ at {addr}")
        return True

    def receive_state(self):
        try:
            data = b""
            while True:
                chunk = self.client_socket.recv(BUFFER_SIZE)
                if not chunk:
                    return None
                data += chunk
                if b"\n" in data:
                    break
            return json.loads(data.decode("utf-8").strip())
        except socket.timeout:
            return None
        except json.JSONDecodeError:
            return None
        except ConnectionResetError:
            return None

    def send_action(self, action):
        try:
            msg = json.dumps(action) + "\n"
            self.client_socket.sendall(msg.encode("utf-8"))
            return True
        except (ConnectionResetError, BrokenPipeError):
            return False

    def close(self):
        if self.client_socket:
            self.client_socket.close()
        if self.server_socket:
            self.server_socket.close()


def main():
    num_uavs = 3
    num_iot_nodes = 5

    agent = SimpleMAPPOAgent(num_uavs=num_uavs, num_iot_nodes=num_iot_nodes)
    server = TCPServer()

    try:
        server.start()
        server.accept()

        step = 0
        while True:
            state = server.receive_state()
            if state is None:
                logger.info("OMNeT++ disconnected or timed out")
                break

            logger.info(f"\n{'='*60}")
            logger.info(f"Step {step} | Coverage: {state.get('iot_coverage', 'N/A')}")
            logger.info(f"{'='*60}")

            actions = agent.select_actions(state)

            response = {"type": "action", "uavs": actions}
            if not server.send_action(response):
                logger.error("Failed to send actions")
                break

            step += 1

    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        server.close()
        logger.info(f"Session complete: {step} steps")


if __name__ == "__main__":
    main()
