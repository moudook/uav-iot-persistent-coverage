# UAV-IoT MAPPO Simulation — Complete Setup Guide

## Project Overview

This project simulates a UAV-IoT network where multiple UAVs (drones) provide coverage
to ground IoT sensor nodes. A MAPPO (Multi-Agent Proximal Policy Optimization) agent
in Python controls the UAVs via a TCP bridge to OMNeT++/Simu5G.

```
┌─────────────────────────────────────────────────────────────────┐
│                        ARCHITECTURE                             │
│                                                                 │
│   ┌──────────────┐    TCP/JSON    ┌──────────────────────────┐  │
│   │  Python MAPPO │◄─────────────►│  OMNeT++ 6.4.0           │  │
│   │  (CTDE)      │   Port 6543   │    ├── INET 4.6.0         │  │
│   │              │               │    ├── Simu5G 1.4.3        │  │
│   │  - Actor net │               │    └── UAV_IoT_Demo        │  │
│   │  - Critic net│               │        ├── UAVs (battery)  │  │
│   │  - Replay buf│               │        ├── IoT nodes       │  │
│   └──────────────┘               │        ├── ChargingStations│  │
│                                  │        └── gNodeB/BaseStn  │  │
│                                  └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Version Requirements

| Component | Version   |
|-----------|-----------|
| OMNeT++   | 6.4.0     |
| INET      | 4.6.0     |
| Simu5G    | 1.4.3     |
| Python    | 3.10+     |
| PyTorch   | 2.0+      |
| WSL       | 2 (Ubuntu)|

---

## STEP-BY-STEP SETUP (Windows + WSL2)

### Phase 1: Install WSL2

Open **PowerShell as Administrator** and run:

```powershell
wsl --install
wsl --update
```

Restart Windows if prompted. Then install Ubuntu:

```powershell
wsl --install -d Ubuntu
```

Launch Ubuntu from the Start Menu. Create your Linux username and password.

Verify:
```bash
wsl --version
```

---

### Phase 2: Install opp_env (inside WSL/Ubuntu)

Open Ubuntu terminal and run:

```bash
python3 --version
python3 -m pip install --user opp-env
export PATH="$HOME/.local/bin:$PATH"
opp_env --version
```

Add to your shell profile so PATH persists:
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

---

### Phase 3: Create Workspace and Install Simu5G

```bash
mkdir -p ~/omnetpp-workspace
cd ~/omnetpp-workspace
opp_env init
opp_env install simu5g-1.4.3
```

This downloads and builds OMNeT++ 6.4.0, INET 4.6.0, and Simu5G 1.4.3 together.

Expected output:
```
simu5g-1.4.3
inet-4.6.0
omnetpp-6.4.0
```

---

### Phase 4: Enter Development Shell and Launch IDE

```bash
opp_env shell simu5g-1.4.3
```

Inside the shell, verify:
```bash
which omnetpp
which opp_run
omnetpp --version    # Should show 6.4.0
```

Launch the IDE:
```bash
omnetpp
```

---

### Phase 5: Import Projects into IDE

In the OMNeT++ IDE:

1. **Import INET:**
   - File → Import → General → Existing Projects into Workspace
   - Select the installed INET directory (check `~/opp_env/inet-4.6.0`)
   - Do NOT check "Copy projects into workspace"
   - Click Finish
   - Right-click `inet` → Build Project → Wait for 0 errors

2. **Import Simu5G:**
   - File → Import → General → Existing Projects into Workspace
   - Select the Simu5G directory (check `~/opp_env/simu5g-1.4.3`)
   - Do NOT check "Copy projects into workspace"
   - Click Finish
   - Right-click `simu5G` → Properties → Project References → Ensure `inet` is checked
   - Right-click `simu5G` → Build Project → Wait for 0 errors

3. **Verify Simu5G works:**
   - Navigate to `simu5G/simulations/nr/tutorial/`
   - Open `omnetpp.ini`
   - Right-click → Run As → OMNeT++ Simulation
   - A Qtenv window should appear with a 5G simulation

---

### Phase 6: Copy Project Files into WSL

Copy the `UAV_IoT_Demo` project from Windows into the WSL workspace:

```bash
# From WSL terminal:
cp -r /mnt/c/Users/gbust/Downloads/Academic/Courses/Machine_learning_in_wireless_network/Project1/Simulation/UAV_IoT_Demo ~/omnetpp-workspace/

# OR if that path doesn't work, copy manually:
# 1. In Windows Explorer, go to: \\wsl.localhost\Ubuntu\home\<your-username>\omnetpp-workspace\
# 2. Drag the UAV_IoT_Demo folder into this directory
```

**IMPORTANT:** Keep all work inside the WSL Linux filesystem (`~/omnetpp-workspace/`).
Do NOT work from `/mnt/c/` — it is much slower for compilation.

---

### Phase 7: Import and Build UAV_IoT_Demo

In the OMNeT++ IDE:

1. **Import the project:**
   - File → Import → General → Existing Projects into Workspace
   - Select `~/omnetpp-workspace/UAV_IoT_Demo`
   - Click Finish

2. **Set Project References:**
   - Right-click `UAV_IoT_Demo` → Properties → Project References
   - Check:
     ```
     ☑ inet
     ☑ simu5G
     ```
   - Click Apply and Close

3. **Build the project:**
   - Right-click `UAV_IoT_Demo` → Build Project
   - Should produce 0 errors

4. **Run the simulation:**
   - Expand `simulations/` → Open `omnetpp.ini`
   - Right-click → Run As → OMNeT++ Simulation
   - Select config: `Demo`
   - The Qtenv GUI should show the UAV-IoT network

---

### Phase 8: Python Bridge Setup

Inside WSL:

```bash
cd ~/omnetpp-workspace/UAV_IoT_Demo/python_bridge

# Install Python dependencies
pip install --user -r requirements.txt

# Start the bridge (run this FIRST before OMNeT++)
python3 omnetpp_bridge.py
```

The bridge listens on `127.0.0.1:6543` for OMNeT++ connections.

---

### Phase 9: Run the Full System

In **two separate terminals** (both inside `opp_env shell simu5g-1.4.3`):

**Terminal 1 — Python Bridge:**
```bash
cd ~/omnetpp-workspace/UAV_IoT_Demo/python_bridge
python3 omnetpp_bridge.py
```

**Terminal 2 — OMNeT++ Simulation:**
```bash
cd ~/omnetpp-workspace
opp_env shell simu5g-1.4.3
cd UAV_IoT_Demo
opp_run -u Qtenv -c Demo -f simulations/omnetpp.ini
```

Or from the IDE: Run → Run Configurations → Select Demo config.

---

## Quick Demo (for Professor Presentation)

```bash
cd ~/omnetpp-workspace/UAV_IoT_Demo
chmod +x demo.sh
./demo.sh
```

This builds the project, starts the bridge, and runs a 5-minute simulation demo.

---

## Project File Structure

```
UAV_IoT_Demo/
├── src/uav_iot_demo/
│   ├── UAV.ned                 # UAV compound module definition
│   ├── UAVBattery.ned          # Battery model (NED)
│   ├── UAVBattery.h            # Battery model (C++ header)
│   ├── UAVBattery.cc           # Battery model (C++ implementation)
│   ├── ChargingStation.ned     # Charging station (NED)
│   ├── ChargingStation.h       # Charging station (C++ header)
│   ├── ChargingStation.cc      # Charging station (C++ implementation)
│   └── UAVIoTNetwork.ned       # Full network topology
├── simulations/
│   └── omnetpp.ini             # Simulation configuration
├── python_bridge/
│   ├── omnetpp_bridge.py       # TCP bridge (Python ↔ OMNeT++)
│   └── requirements.txt        # Python dependencies
├── Makefile                    # Build configuration
├── demo.sh                     # Quick demo script
└── README.md                   # This file
```

---

## Troubleshooting

### `undefined symbol` errors
You have a version mismatch. Re-enter the correct opp_env shell:
```bash
opp_env shell simu5g-1.4.3
```

### `Cannot load library libsimu5g.so`
Check your environment:
```bash
which opp_run
echo $LD_LIBRARY_PATH
```
Make sure they point to the `opp_env` installation.

### `no such module type` for UAV/Battery
Ensure:
- The `src/uav_iot_demo/` directory contains all `.ned` files
- Each `.ned` file starts with `package uav_iot_demo;`
- The project has been rebuilt after adding files

### Slow compilation from `/mnt/c/`
Always work inside the WSL Linux filesystem (`~/omnetpp-workspace/`), NOT `/mnt/c/`.

### Python bridge connection refused
Make sure `omnetpp_bridge.py` is running BEFORE you start the OMNeT++ simulation.

---

## Key Concepts for MAPPO Integration

1. **State (OMNeT++ → Python):** Each step, OMNeT++ sends UAV battery levels,
   positions, IoT node coverage, and charging station status as JSON.

2. **Action (Python → OMNeT++):** The MAPPO agent responds with movement vectors
   and actions (patrol, charge, return-to-base) for each UAV.

3. **Reward function (computed in Python):**
   - +IoT coverage rate
   - -Battery penalty for low charge
   - -Failure penalty for UAV downtime
   - +Charge efficiency reward

4. **Training loop:**
   ```
   for episode in range(num_episodes):
       state = bridge.receive_state()
       while not done:
           actions = agent.select_actions(state)
           bridge.send_actions(actions)
           next_state = bridge.receive_state()
           reward = compute_reward(state, actions, next_state)
           agent.store_transition(state, actions, reward, next_state)
           state = next_state
       agent.update_policy()
   ```

---

## Useful Documentation Links

- OMNeT++ 6.4: https://docs.omnetpp.org/6.4/installguide/ch-intro
- OMNeT++ Downloads: https://omnetpp.org/download/
- INET 4.6: https://inet.omnetpp.org/Installation.html
- Simu5G: https://simu5g.org/install
- Simu5G GitHub: https://github.com/Unipisa/Simu5G
