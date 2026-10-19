# OMNeT++ + INET + Simu5G Setup Guide

**Project environment used by our team**

- **OMNeT++:** 6.4.0
- **INET:** 4.6.0
- **Simu5G:** 1.4.3
- **Recommended Windows setup:** WSL2 + Linux environment
- **Recommended Linux setup:** `opp_env`
- **Recommended project workflow:** keep OMNeT++, INET, and Simu5G as separate installed projects and reference them from your own project.

> **Important:** For this project, use the exact versions above rather than mixing arbitrary OMNeT++, INET, and Simu5G versions. Version mismatches can produce errors such as undefined symbols, missing NED types, or stale project-reference paths.

---

# 1. What are these three components?

### OMNeT++

OMNeT++ is the discrete-event simulation framework and Simulation IDE. It provides the simulation kernel, NED language, C++ support, Qtenv GUI, and project/build environment.

### INET

INET is a network simulation framework built on OMNeT++. It provides ready-made models for:

- wireless hosts
- routers and switches
- IP networking
- mobility
- routing
- IEEE 802.11
- physical-layer models
- applications
- energy/power-related models
- visualization

### Simu5G

Simu5G is an OMNeT++/INET-based framework for 4G/5G system-level simulations. It provides LTE/NR models, gNodeB/eNB, UEs, protocol stacks, schedulers, and 5G-related functionality.

Our project can therefore be thought of as:

```text
                 Our UAV-IoT Project
                         |
             +-----------+-----------+
             |                       |
          INET                    Simu5G
             |                       |
             +-----------+-----------+
                         |
                      OMNeT++
```

---

# 2. Recommended version combination for this project

Use:

```text
OMNeT++ 6.4.0
INET    4.6.0
Simu5G  1.4.3
```

We installed this combination using `opp_env`.

Simu5G 1.4.3 was updated for INET 4.6.0 compatibility. The Simu5G release notes state that v1.4.3 was tested with INET 4.5.4/OMNeT++ 6.3 and updated for INET 4.6.0 compatibility.

> **Compatibility note:** INET's current compatibility page officially lists INET 4.6.0 with OMNeT++ 6.2/6.3, while the Simu5G 1.4.3 release specifically added INET 4.6.0 compatibility. Our `opp_env` environment successfully resolved and ran OMNeT++ 6.4.0 + INET 4.6.0 + Simu5G 1.4.3. If starting a completely new environment, keep the versions together as documented here rather than independently upgrading one component.

---

# 3. OPTION A — Linux installation (RECOMMENDED)

This is the easiest setup for Linux.

## 3.1 Check basic requirements

Open a terminal:

```bash
uname -m
```

For a normal Intel/AMD 64-bit machine, you should see:

```text
x86_64
```

Check Python:

```bash
python3 --version
```

Check Git:

```bash
git --version
```

---

# 4. Install `opp_env`

`opp_env` is the package manager provided for installing OMNeT++ and simulation frameworks together with their dependencies.

Install it with:

```bash
python3 -m pip install --user opp-env
```

If `opp_env` is not found afterwards, make sure your local Python binary directory is on PATH. For example:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Verify:

```bash
opp_env --version
```

---

# 5. Create a clean OMNeT++ workspace

Do NOT install the frameworks inside random project directories.

Create a dedicated workspace:

```bash
mkdir -p ~/omnetpp-workspace
cd ~/omnetpp-workspace
```

Initialize it:

```bash
opp_env init
```

---

# 6. Install the exact Simu5G environment

Instead of installing OMNeT++, INET, and Simu5G independently, let `opp_env` resolve the dependencies.

Run:

```bash
opp_env install simu5g-1.4.3
```

This installs the required environment, including the corresponding OMNeT++ and INET dependencies.

You should see an effective project set similar to:

```text
simu5g-1.4.3
inet-4.6.0
omnetpp-6.4.0
```

---

# 7. Enter the development shell

This step is important.

Run:

```bash
opp_env shell simu5g-1.4.3
```

This configures the environment variables and PATH for the installed OMNeT++/INET/Simu5G versions.

Inside this shell, run:

```bash
omnetpp
```

The OMNeT++ Simulation IDE should open.

> **Important:** Start OMNeT++ from this `opp_env` shell. Do not mix it with another OMNeT++ installation already present on the system.

---

# 8. Verify OMNeT++

Inside the same shell:

```bash
which omnetpp
```

and:

```bash
which opp_run
```

You should see paths belonging to the `opp_env` installation.

For example:

```text
/home/<user>/opp_env/omnetpp-6.4.0/bin/...
```

You can also check:

```bash
omnetpp --version
```

Expected version:

```text
6.4.0
```

---

# 9. Import INET into the IDE

After opening OMNeT++:

1. Open the **Project Explorer**.
2. Go to:

   **File → Import**
3. Select:

   **General → Existing Projects into Workspace**
4. Select the installed INET directory.
5. Import the `inet` project.
6. Make sure **Copy projects into workspace** is NOT selected.
7. Finish the import.

Then:

```text
Right-click inet
        ↓
Build Project
```

Wait for the build to finish.

You want:

```text
Build Finished.
0 errors
```

---

# 10. Import Simu5G

In the same workspace:

1. **File → Import**
2. **General → Existing Projects into Workspace**
3. Select the installed Simu5G directory.
4. Do NOT copy the project into the workspace.
5. Finish.

Then:

```text
Right-click simu5G
→ Properties
→ Project References
```

Make sure the INET project is referenced.

Then:

```text
Right-click simu5G
→ Build Project
```

You should get:

```text
Build Finished.
0 errors
```

---

# 11. Run a Simu5G test simulation

Before creating our own UAV project, always verify that Simu5G itself works.

Navigate to something like:

```text
simu5G
└── simulations
    └── nr
        └── tutorial
```

Open:

```text
omnetpp.ini
```

Then:

```text
Right-click omnetpp.ini
→ Run As
→ OMNeT++ Simulation
```

A Qtenv simulation window should appear.

If the Simu5G tutorial runs successfully, the installation is working.

---

# 12. Create our project

Do NOT modify INET or Simu5G directly.

Create a separate OMNeT++ project:

```text
File
→ New
→ OMNeT++ Project
```

Example:

```text
UAV_IoT_Demo
```

A clean project can look like:

```text
UAV_IoT_Demo
├── src
│   └── ...
└── simulations
    └── omnetpp.ini
```

Then:

```text
Right-click UAV_IoT_Demo
→ Properties
→ Project References
```

Enable:

```text
☑ inet
☑ simu5G
```

This allows our project to use INET/Simu5G modules without copying their source code.

---

# 13. OPTION B — Windows

There are TWO ways to run OMNeT++ on Windows.

## Recommended: Windows + WSL2

For our team, this is the preferred Windows setup.

OMNeT++'s documentation recommends WSL2 over the native MinGW64 Windows build because Linux/WSL2 generally gives better compilation performance and fewer compatibility surprises.

---

# 14. Windows — Install WSL2

Open **PowerShell as Administrator**.

Run:

```powershell
wsl --install
```

Restart Windows if requested.

Then check:

```powershell
wsl --version
```

Make sure WSL 2 is installed and up to date.

You can also run:

```powershell
wsl --update
```

---

# 15. Install Ubuntu in WSL2

If Ubuntu was not installed automatically:

```powershell
wsl --install -d Ubuntu
```

Launch Ubuntu from the Start Menu.

Create your Linux username and password when prompted.

From this point onward, the commands are essentially the same as the Linux instructions.

---

# 16. Windows + WSL2 — Install `opp_env`

Inside the Ubuntu/WSL terminal:

```bash
python3 --version
```

Then install:

```bash
python3 -m pip install --user opp-env
```

If required:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Check:

```bash
opp_env --version
```

---

# 17. Windows + WSL2 — Install our environment

Inside WSL:

```bash
mkdir -p ~/omnetpp-workspace
cd ~/omnetpp-workspace
```

Initialize:

```bash
opp_env init
```

Install:

```bash
opp_env install simu5g-1.4.3
```

Enter the environment:

```bash
opp_env shell simu5g-1.4.3
```

Then:

```bash
omnetpp
```

---

# 18. Windows + WSL2 — Important filesystem rule

For good performance, keep the OMNeT++ workspace **inside the WSL Linux filesystem**.

Prefer:

```text
/home/<username>/omnetpp-workspace
```

Avoid doing active compilation from:

```text
/mnt/c/Users/<username>/...
```

The Linux filesystem is much better for this workflow.

You can still access the files from Windows through File Explorer using:

```text
\\wsl$
```

or:

```text
\\wsl.localhost\
```

---

# 19. Windows — Native installation (Alternative)

A native Windows installation is possible, but it is **not our recommended setup**.

OMNeT++ provides a Windows MinGW64 package.

Download:

```text
omnetpp-6.4.0-windows-x86_64.7z
```

Extract it somewhere without spaces in the path.

Good:

```text
C:\omnetpp-6.4.0
```

Avoid:

```text
C:\Program Files\omnetpp-6.4.0
```

---

# 20. Configure native Windows OMNeT++

Open:

```text
C:\omnetpp-6.4.0\opp_shell.cmd
```

This opens the OMNeT++ MinGW shell.

Then:

```bash
./configure
```

Build:

```bash
make -j8
```

You can change `8` according to the number of CPU cores available.

Then launch the IDE:

```bash
omnetpp
```

---

# 21. Native Windows — Install INET

For a specific INET version:

1. Download/extract INET.
2. Open OMNeT++ IDE.
3. Use:

   **File → Import → General → Existing Projects into Workspace**
4. Select the INET directory.
5. Do NOT copy the project.
6. Build INET.

Then verify that an INET tutorial runs.

---

# 22. Native Windows — Install Simu5G

Extract Simu5G next to INET.

Example:

```text
C:\
├── inet-4.6.0
└── simu5g-1.4.3
```

Import Simu5G:

```text
File
→ Import
→ General
→ Existing Projects into Workspace
```

Then:

```text
Right-click simu5G
→ Properties
→ Project References
```

Enable the correct INET project.

Build:

```text
Project
→ Build All
```

Then run one of the Simu5G NR tutorial simulations.

---

# 23. Very important: Do not mix versions

This is one of the most common causes of problems.

For example, avoid having:

```text
Simu5G compiled against INET 4.5.4
        +
runtime loading INET 4.6.0
```

This can produce errors such as:

```text
undefined symbol
```

or:

```text
Cannot load library libsimu5g.so
```

Similarly, avoid accidentally importing an old INET project into the workspace.

Always check:

```text
Right-click inet
→ Properties
→ Resource
→ Location
```

and verify that it points to the intended INET installation.

---

# 24. Check Project References

For Simu5G:

```text
Right-click simu5G
→ Properties
→ Project References
```

Make sure the intended INET project is checked.

For our own project:

```text
Right-click UAV_IoT_Demo
→ Properties
→ Project References
```

Make sure:

```text
☑ inet
☑ simu5G
```

are enabled.

---

# 25. NED package/folder rule

OMNeT++ NED packages must match their directory structure.

For example:

```text
src/
└── uav_iot_demo/
    ├── UAV.ned
    ├── UAVBattery.ned
    └── UAVIoTNetwork.ned
```

Then each file can begin with:

```ned
package uav_iot_demo;
```

Do NOT put those files directly in:

```text
src/
```

while declaring:

```ned
package uav_iot_demo;
```

The package name and folder structure must agree.

---

# 26. Recommended project structure

For our UAV project:

```text
UAV_IoT_Demo/
│
├── src/
│   └── uav_iot_demo/
│       ├── UAV.ned
│       ├── UAVBattery.ned
│       ├── UAVBattery.h
│       ├── UAVBattery.cc
│       └── UAVIoTNetwork.ned
│
├── simulations/
│   └── omnetpp.ini
│
└── README.md
```

INET and Simu5G should remain separate:

```text
opp_env/
│
├── omnetpp-6.4.0/
├── inet-4.6.0/
└── simu5g-1.4.3/
```

Our project references these installations rather than copying them.

---

# 27. Basic verification checklist

Before starting development, every team member should be able to check all of these.

### OMNeT++

```bash
omnetpp
```

IDE opens successfully.

### INET

An INET example/tutorial runs successfully.

### Simu5G

A Simu5G NR tutorial runs successfully.

### Project references

Our project has:

```text
inet
simu5G
```

as project references.

### Build

Our project produces:

```text
0 errors
```

### Runtime

Our project's `omnetpp.ini` launches successfully.

---

# 28. Recommended first test for our project

After installation, create:

```text
UAV_IoT_Demo
```

Then:

```text
src/
└── uav_iot_demo/
    └── UAVIoTNetwork.ned

simulations/
└── omnetpp.ini
```

The first goal is simply:

```text
OMNeT++
   ↓
INET
   ↓
Wireless network
   ↓
UAV nodes
   ↓
IoT nodes
   ↓
Simulation runs
```

After that we add:

```text
UAV mobility
      ↓
battery model
      ↓
coverage/K-coverage
      ↓
predictive recharge
      ↓
charging station
      ↓
UAV failure
      ↓
reserve UAV
      ↓
swarm reconfiguration
      ↓
Python/MARL controller
```

---

# 29. Troubleshooting

## Error: `undefined symbol`

Most likely cause:

**INET/Simu5G binary mismatch.**

Check that the runtime is using the same INET version that Simu5G was built against.

For an `opp_env` setup, enter the correct shell again:

```bash
opp_env shell simu5g-1.4.3
```

Then launch OMNeT++ from that shell.

---

## Error: `Cannot load library libsimu5g.so`

Check:

```bash
which opp_run
```

and:

```bash
echo $LD_LIBRARY_PATH
```

Make sure they point to the active `opp_env` environment.

---

## Error: `UAV: no such module type`

Check:

1. `UAV.ned` exists.
2. It is inside the correct NED source/package directory.
3. The package matches the directory.
4. The project containing the NED file is open.
5. The project has been rebuilt.

For example:

```text
src/uav_iot_demo/UAV.ned
```

must contain:

```ned
package uav_iot_demo;
```

---

## Error: `declared package does not match expected package`

The directory and package name don't match.

For:

```text
src/uav_iot_demo/UAV.ned
```

use:

```ned
package uav_iot_demo;
```

---

## Error: `radioMedium` not found

Wireless INET nodes generally require a radio medium in the network.

For example:

```ned
radioMedium: Ieee80211ScalarRadioMedium;
```

must be present when using the corresponding IEEE 802.11 radio models.

---

## Simulation runs but immediately exits

Check:

```text
Run Configurations
```

and make sure the selected network is the intended network.

Also check the Qtenv console for the first error, rather than only looking at the final `exit code 1`.

---

# 30. Clean reinstall / reset strategy

If someone's environment becomes badly mixed:

**Do not start editing INET source files.**

Instead:

1. Close OMNeT++.
2. Exit the current `opp_env` shell.
3. Open a fresh terminal.
4. Enter the correct `opp_env` environment:

```bash
opp_env shell simu5g-1.4.3
```

5. Start:

```bash
omnetpp
```

6. Check the project locations.
7. Rebuild INET.
8. Rebuild Simu5G.
9. Rebuild our project.

Only reinstall if the actual installation is corrupted.

---

# 31. Quick setup — Linux

For someone who already has Python and the basic Linux environment:

```bash
mkdir -p ~/omnetpp-workspace
cd ~/omnetpp-workspace

opp_env init

opp_env install simu5g-1.4.3

opp_env shell simu5g-1.4.3

omnetpp
```

Then import:

```text
inet
simu5G
```

into the IDE and build both.

Finally create:

```text
UAV_IoT_Demo
```

and add project references:

```text
inet
simu5G
```

---

# 32. Quick setup — Windows with WSL2

From **PowerShell as Administrator**:

```powershell
wsl --install
wsl --update
```

Launch Ubuntu.

Then inside Ubuntu:

```bash
python3 -m pip install --user opp-env

export PATH="$HOME/.local/bin:$PATH"

mkdir -p ~/omnetpp-workspace
cd ~/omnetpp-workspace

opp_env init
opp_env install simu5g-1.4.3
opp_env shell simu5g-1.4.3

omnetpp
```

Then follow the same IDE steps as Linux.

---

# 33. Useful official documentation

OMNeT++ installation guide:

https://docs.omnetpp.org/6.4/installguide/ch-intro

OMNeT++ downloads:

https://omnetpp.org/download/

INET installation:

https://inet.omnetpp.org/Installation.html

INET 4.6 documentation:

https://inet.omnetpp.org/docs/users-guide/ch-usage.html

Simu5G installation:

https://simu5g.org/install

Simu5G GitHub:

https://github.com/Unipisa/Simu5G

---

# 34. Final recommendation for our team

For consistency, everyone should use:

```text
┌──────────────────────────────┐
│ Windows users                │
│                              │
│ Windows 11                   │
│      ↓                       │
│ WSL2 + Ubuntu                │
│      ↓                       │
│ opp_env                      │
└──────────────┬───────────────┘
               │
               ▼
       OMNeT++ 6.4.0
               │
               ▼
          INET 4.6.0
               │
               ▼
        Simu5G 1.4.3
               │
               ▼
        UAV_IoT_Demo
```

Linux users can directly use:

```text
Linux
  ↓
opp_env
  ↓
OMNeT++ 6.4.0
  ↓
INET 4.6.0
  ↓
Simu5G 1.4.3
  ↓
UAV_IoT_Demo
```

**Do not copy INET/Simu5G into the UAV project. Reference them as dependencies.**
