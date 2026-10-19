#!/usr/bin/env python3
"""
MAPPO-OMNeT++ TCP Bridge
=========================
Handles bidirectional communication between the Python MAPPO agent
and the OMNeT++ Simu5G simulation.

Protocol (JSON over TCP):
  - OMNeT++ sends state as JSON: {"type":"state","uavs":[{"id":0,"battery":85.0,"pos_x":10.0,"pos_y":20.0},...], "iot_coverage": 0.85}
  - Python responds with actions as JSON: {"type":"actions","uavs":[{"id":0,"move_x":1.0,"move_y":-0.5,"action":"patrol"},...]}

Port: 6543 (configurable)
"""

import socket
import json
import time
import threading
import logging
from typing import Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# ==================== Configuration ====================
HOST = "127.0.0.1"
PORT = 6543
BUFFER_SIZE = 8192
RECV_TIMEOUT = 30.0  # seconds to wait for OMNeT++ data
SEND_TIMEOUT = 10.0


class OMNeTBridge:
    """TCP bridge for OMNeT++ <-> Python MAPPO communication."""

    def __init__(self, host: str = HOST, port: int = PORT):
        self.host = host
        self.port = port
        self.server_socket: Optional[socket.socket] = None
        self.client_socket: Optional[socket.socket] = None
        self.connected = False
        self.episode_count = 0
        self.step_count = 0
        self.total_reward = 0.0
        self.state_history: List[dict] = []
        self.action_history: List[dict] = []

    def start_server(self):
        """Start TCP server and wait for OMNeT++ to connect."""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.settimeout(60.0)

        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)
        logger.info(f"Bridge server listening on {self.host}:{self.port}")
        logger.info("Waiting for OMNeT++ simulation to connect...")

        try:
            self.client_socket, addr = self.server_socket.accept()
            self.client_socket.settimeout(RECV_TIMEOUT)
            self.connected = True
            logger.info(f"Connected to OMNeT++ at {addr}")
        except socket.timeout:
            logger.error("Timeout waiting for OMNeT++ connection")
            raise

    def receive_state(self) -> Optional[dict]:
        """Receive state from OMNeT++ simulation."""
        if not self.connected:
            logger.error("Not connected to OMNeT++")
            return None

        try:
            data = self.client_socket.recv(BUFFER_SIZE).decode('utf-8')
            if not data:
                logger.warning("Empty data received - connection may be closed")
                self.connected = False
                return None

            state = json.loads(data)
            logger.debug(f"Received state: step={state.get('step', '?')}, uavs={len(state.get('uavs', []))}")
            self.state_history.append(state)
            return state

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return None
        except socket.timeout:
            logger.warning("Receive timeout - no data from OMNeT++")
            return None
        except ConnectionResetError:
            logger.warning("Connection reset by OMNeT++")
            self.connected = False
            return None

    def send_actions(self, actions: dict) -> bool:
        """Send actions to OMNeT++ simulation."""
        if not self.connected:
            logger.error("Not connected to OMNeT++")
            return False

        try:
            data = json.dumps(actions).encode('utf-8')
            self.client_socket.sendall(data)
            self.action_history.append(actions)
            self.step_count += 1
            logger.debug(f"Sent actions: {len(actions.get('uavs', []))} UAV commands")
            return True

        except (ConnectionResetError, BrokenPipeError):
            logger.warning("Connection lost while sending actions")
            self.connected = False
            return False

    def close(self):
        """Close all sockets."""
        if self.client_socket:
            self.client_socket.close()
        if self.server_socket:
            self.server_socket.close()
        self.connected = False
        logger.info("Bridge connection closed")


class MAPPOAgent:
    """
    Placeholder MAPPO agent.
    Replace with your actual MAPPO implementation.
    """

    def __init__(self, num_uavs: int = 3):
        self.num_uavs = num_uavs

    def select_actions(self, state: dict) -> dict:
        """
        Select actions for each UAV based on current state.

        Args:
            state: Dictionary with keys:
                - "uavs": list of UAV states (battery, position, etc.)
                - "iot_coverage": float (0-1) current IoT coverage
                - "step": int current simulation step

        Returns:
            actions: Dictionary with keys:
                - "uavs": list of action dicts per UAV
        """
        uav_states = state.get("uavs", [])
        actions = {"type": "actions", "uavs": []}

        for uav in uav_states:
            battery = uav.get("battery", 100.0)
            pos_x = uav.get("pos_x", 0.0)
            pos_y = uav.get("pos_y", 0.0)

            if battery < 10.0:
                action = "return_to_charging"
                move_x = -pos_x * 0.1
                move_y = -pos_y * 0.1
            elif battery < 25.0:
                action = "return_to_charging"
                move_x = -pos_x * 0.05
                move_y = -pos_y * 0.05
            else:
                action = "patrol"
                move_x = 1.0
                move_y = 0.5

            actions["uavs"].append({
                "id": uav.get("id", 0),
                "move_x": move_x,
                "move_y": move_y,
                "action": action
            })

        return actions


def run_bridge():
    """Main entry point for the bridge."""
    bridge = OMNeTBridge()
    agent = MAPPOAgent(num_uavs=3)

    try:
        bridge.start_server()
        logger.info("Bridge ready - entering main loop")

        step = 0
        while bridge.connected:
            state = bridge.receive_state()
            if state is None:
                logger.info("Simulation ended or disconnected")
                break

            actions = agent.select_actions(state)
            bridge.send_actions(actions)

            step += 1
            if step % 50 == 0:
                logger.info(f"Step {step}: episode={bridge.episode_count}, "
                          f"total_steps={bridge.step_count}")

    except KeyboardInterrupt:
        logger.info("Bridge interrupted by user")
    except Exception as e:
        logger.error(f"Bridge error: {e}")
    finally:
        bridge.close()
        logger.info(f"Session complete: {bridge.step_count} steps")


if __name__ == "__main__":
    run_bridge()
