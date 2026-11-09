# DEMO GUIDE — Live Demonstration for Prof (OMNeT++/INET + MAPPO pipeline)

**Goal:** convince the professor that (a) the OMNeT++/INET simulation actually runs, (b) it is *our* code, and (c) it feeds the ML work described in the report.
**Total time: ~25 min demo. Preparation: 15 min before.**

---

## 0.5 VISUAL RUN — ONE COMMAND (show this to prof first)

Run this in PowerShell; a Qtenv window opens with the animated network:

```powershell
wsl -d Ubuntu -- bash -c "cd /home/gbust/omnetpp_ws && DISPLAY=:0 opp_env run inet-4.6.0 -c 'cd /home/gbust/omnetpp_ws/inet-4.6.0/examples/uav_omnet && opp_run -u Qtenv -l /home/gbust/omnetpp_ws/inet-4.6.0/out/clang-release/src/libINET.so -n /home/gbust/omnetpp_ws/inet-4.6.0/src:/home/gbust/omnetpp_ws/inet-4.6.0/examples /home/gbust/omnetpp_ws/inet-4.6.0/examples/uav_omnet/omnetpp.ini'"
```

Verified working Oct 27, 2026 — UAVs animate across the field. If it fails → §8 Fallback.

---

## 0. THE STORY IN ONE LINE (say this first)

> "Phase 1 is our Python MAPPO simulator; Phase 2 is this OMNeT++/INET network simulation — UAVs flying BonnMotion traces over 802.11, producing the beacons/PDR scalars we use to validate the physical layer. I'll show the IDE, our scenario code, a live run, and how it connects to the paper."

---

## 1. PRE-DEMO CHECKLIST (do 15 min before, run these yourself once)

Open **three** windows on Windows:

| # | Window | Command |
|---|---|---|
| 1 | PowerShell in repo | `cd C:\Users\gbust\Downloads\Academic\Courses\Machine_learning_in_wireless_network\Project1` |
| 2 | WSL terminal | `wsl -d Ubuntu` |
| 3 | The paper PDF | `Mlawn-midsem-tex.pdf` open, jump to p.28–30 (claim audit / PHY section) |

Then run the 60-second sanity check in the PowerShell window:

```powershell
wsl -d Ubuntu -- bash -c "cd /home/gbust/omnetpp_ws && opp_env run inet-4.6.0 -c 'cd /home/gbust/omnetpp_ws/inet-4.6.0/examples/uav_omnet && opp_run -u Cmdenv -l /home/gbust/omnetpp_ws/inet-4.6.0/out/clang-release/src/libINET.so -n /home/gbust/omnetpp_ws/inet-4.6.0/src:/home/gbust/omnetpp_ws/inet-4.6.0/examples /home/gbust/omnetpp_ws/inet-4.6.0/examples/uav_omnet/omnetpp.ini 2>&1 | tail -8'"
```

✅ You must see: `Simulation time limit reached -- at t=40s, event #71885` and `End.`
**Verified working: Tue Oct 27, 2026.** If this fails, see §8 Fallback.

---

## 2. PART A — THE OMNeT++ WINDOW (5–7 min) ← professor asked for this

### A1. Launch the OMNeT++ IDE (GUI opens on Windows via WSLg)

In the WSL terminal:

```bash
cd /home/gbust/omnetpp_ws
opp_env shell inet-4.6.0 -- bash -c "omnetpp &"   # option 1, if in PATH
# OR
/home/gbust/omnetpp_ws/omnetpp-6.4.0/ide/omnetpp &  # option 2, direct IDE launcher
```

- First launch takes ~30–60 s; a splash screen then the Eclipse-based IDE appears **as a normal Windows window** (WSLg).
- If it asks for a **workspace**, keep the default (`/home/gbust/omnetpp_ws`) — it already knows the INET project.

### A2. What to show inside the IDE (this order)

1. **Project Explorer** (left panel): expand `inet-4.6.0` → `examples/uav_omnet/`
   - Double-click **`UavNetwork.ned`** → shows the graphical network editor. Say: *"this is our network topology — N UAV nodes, one AP/sink, one IotNode group, wireless 802.11g."*
   - Click the **Source** tab at the bottom → the NED text (see §3 for what to say about the code).
2. Double-click **`omnetpp.ini`** → the run configuration. Point at:
   - the mobility trace line (`mobility ... traceFile = traces/episode_000.movements`) → *"traces exported from our Python simulator in BonnMotion format"*
   - the `sim-time-limit = 40s` and per-node packet rate lines.
3. **THE MONEY SHOT — animated run in Qtenv (GUI):**
   - With `omnetpp.ini` open, press the **Run** button (green ▶ / Ctrl+R). A Qtenv window opens with the network visualization: UAV nodes moving across the field, radio/link icons, message arrows (beacons + UDP app packets).
   - Let it animate ~20–30 s, then hit **Fast-run (F5)** or Express button so it finishes. Say: *"the UAVs follow the trajectories our RL/heuristic controllers produce; INET models the actual 802.11 MAC and PHY."*
   - When done, show the **results** folder refresh: `General-#0.sca` / `.vec` files.

> ⚠️ If the IDE/Qtenv refuses to open (WSLg hiccup): fallback is terminal Qtenv:
> ```powershell
> wsl -d Ubuntu -- bash -c "cd /home/gbust/omnetpp_ws && DISPLAY=:0 opp_env run inet-4.6.0 -c 'cd /home/gbust/omnetpp_ws/inet-4.6.0/examples/uav_omnet && opp_run -u Qtenv -l /home/gbust/omnetpp_ws/inet-4.6.0/out/clang-release/src/libINET.so -n /home/gbust/omnetpp_ws/inet-4.6.0/src:/home/gbust/omnetpp_ws/inet-4.6.0/examples /home/gbust/omnetpp_ws/inet-4.6.0/examples/uav_omnet/omnetpp.ini'"
> ```
> Verified working Oct 27, 2026 — UAVs animate across the field. If it still fails → §8.

---

## 2.5. PART A+ — WHAT'S HAPPENING INSIDE THE Qtenv WINDOW (internal working)

*Read this the morning before the demo. When the prof asks "how is this working internally?", walk top-down through this.*

### The simulation event machinery (OMNeT++ core)

- OMNeT++ is a **discrete-event simulator**. There is no wall-clock loop: there is a **Future Event Set (FES)** — a priority queue of future events ordered by simulation time. The kernel pops the earliest event, executes the corresponding module's handler, which may schedule new events, and pops again. Simulation time only advances when nothing happens between events — that's why 40 simulated seconds = tens of thousands of events and runs faster than real time.
- Each node (`uav[i]`, `sensor[i]`, `sink`) is a **simple module** (from the INET library); the composition is declared in **NED** (our `UavNetwork.ned`) and wired automatically. Each module's behaviour code runs only when an event reaches it.
- The Cmdenv speed you saw (~104 simsec/sec, ~72k events) is exactly this: everything is event-driven, nothing sleeps.

### What each piece of the Qtenv window IS

| Visual thing on screen | What it actually is |
|---|---|
| Blue circles moving | `uav[i]: AdhocHost` — full INET ad-hoc wireless stack (UDP → IPv4 → ARP → IEEE 802.11 MAC → radio). Their motion is **BonnMotionMobility** replaying our trace file (`traces/episode_000.movements`) — one "line = 8 UAVs × 3 columns" per waypoint, produced by our Python simulator. Node follows it at trace speed/altitude. |
| Grey circles scattered | `sensor[i]: AdhocHost`, `StationaryMobility`, positions drawn `uniform(0,80m)` — the 20 IoT nodes. |
| Red circle centre | `sink: StandardHost` at (40,40) — the ground data sink. |
| Thin grey circle outline around a node | The **radio's effective range annotation** (`@display("r="…)`). Not a packet — just a decoration showing communication radius. |
| Colored arrows / "radio waves" between nodes | Actual **radio signal transmissions** from `Ieee80211ScalarRadioMedium`. Each transmission is a physical event; the medium model decides per-receiver whether it arrives: computes path loss (BreakpointPathLoss), background noise (−94 dBm floor), SNR, and compares against the receiver's sensitivity (−85 dBm) and SNR threshold (4 dB). If SNR is good → delivered up to MAC; if not → dropped. |
| Green/grey checkmark-bubbles or drops in the log window | Frame level events: beacons, data frames, ACKs, retries, collisions & retransmissions from the 802.11 DCF. |

### The data path when ONE packet flies (say what happens, Step 1→7)

1. `UdpBasicApp` on drone i wakes on a self-message timer (`sendInterval = 1 s`, so 40 packets/node in a 40 s sim — that's the 40 you saw in the scalars), builds a 64 B payload,ätze sends it to `destAddresses` = all eight drones.
2. UDP → IPv4: if destination is on-one-hop neighbour, ARP resolves the MAC; if a neighbour is out of range, **IPv4 has no routes** (single flat ad-hoc net, no MANET routing protocol is loaded) and the packet dies at the network layer — worth mentioning because "why don't far packets arrive" is a fair prof question.
3. Wireless: `Ieee80211Mac` → DCF channel access (`cwMin=7`): if the medium is busy, it backs off with a random window and retries.
4. The radio transmits: 0.5 W (+27 dBm), 6 Mbps PHY mode. The `ScalarRadioMedium` creates a **transmission event** that every node's radio hears.
5. Per **receiving** radio: path-loss by distance (which is why the farther sensors drop), interference from concurrent senders → SNIR. `snirThreshold=4 dB` + sensitivity −85 dBm decide reception vs discard.
6. Success → frame climbs the stack on the receiver (MAC → IP → UDP → `UdpBasicApp`'s socket) → the app records "packet received".
7. `scalar-recording = true`/`vector-recording = true`: counted scalars (`packets sent`, `packets received`, PER-at-MAC, end-to-end delay) are written to `results/General-#0.sca` and `.vec` at finish — the files we `grep` after a Cmdenv run.

### Where OUR contributions sit in the machine

- The **UAV trajectories are our simulator's output** (Phase-1 Python env → BonnMotion mentioned).
- `numUavs = 8`, `numSensors = 20`, field 80×80 m, `transmitter.power = 0.5 W`, `bitrate = 6 Mbps` — all chosen to **mirror the constants in the report's Table VII**, so this file is the physical-layer twin of the Python model.
- The **claim audit / `phy_equivalence.py`** closes the loop: it verifies INET's path-loss formula and our Python's give identical curves (0.012 dB max). So "the same thing happens physically in both halves."

### Suggested 30-second narration while Qtenv animates

> "What you see: 8 UAVs replaying trajectories our RL simulator produced; a periodic UDP beacon from each UAV to all others every second, so 8 apps × 40 s = 320 beacons; the red is the ground sink; the radio arrows are real 802.11 frames at 0.5 W & 6 Mbps passing through INET's MAC/PHY models — path loss, noise, SNR, retransmissions — and the metrics this produces are the `packets sent/recv` scalars we later grep and feed into the paper's claim audit."

---

## 3. PART B — OUR CODE (5 min). What to open and the one-liner for each

Open these files (in IDE or VS Code — VS Code on Windows opens the repo directly):

| File | Say this |
|---|---|
| `Simulation/omnet_uav/UavNetwork.ned` | "Our network definition: UAV nodes, IoT sensor nodes, sink, 802.11 radio config." |
| `Simulation/omnet_uav/omnetpp.ini` | "Run configuration: which trace file, sim time, radio params. Copy of this lives inside the WSL INET examples dir." |
| `scripts/export_trajectories.py` (or trace-generating script) | "This exports UAV trajectories from our Python simulator into **BonnMotion `.movements` format** that INET's BonnMotionMobility consumes — this is the bridge between ML and OMNeT." |
| `ml_impl/uav_wireless/env.py` | "Phase 1: the simulator that produces those trajectories — K-coverage, connectivity graph, battery, charging." |
| `ml_impl/uav_wireless/mappo.py` | "The shared actor and centralized critic — CTDE MAPPO." |
| `ml_impl/uav_wireless/train.py` | "The PPO training loop with the feasibility mask." |
| `ml_impl/analysis/claim_audit.py` | "38-item automated claim audit — 0 failing. It recomputes every number in the paper." |
| `ml_impl/analysis/feasibility.py` | "The feasibility certificate + teleporting oracle from Sec. III-G." |
| `ml_impl/analysis/phy_equivalence.py` | "Proves our Python path-loss = INET's BreakpointPathLoss to 0.012 dB — this is the OMNeT↔ML link." |

**Key sentence to land:** *"Everything the OMNeT extension uses — traces, node counts — is generated by the same Python pipeline the paper's numbers come from. That's why the claim audit can check it."*

---

## 4. PART C — LIVE CMDENV RUN + SCALARS (4 min)

Already done in checklist, but if you want to re-run it live, use the §1 command. While it runs (~60–90 s), say: *"Cmdenv = command-line express mode; 72k events, 40 simulated seconds, ~104 simsec/sec CPU speed."*

Then read the outputs, in WSL:

```bash
cd /home/gbust/omnetpp_ws/inet-4.6.0/examples/uav_omnet
grep -E "scalar.*(packets sent|received)" results/General-#0.sca | head -10
```

Expected: `scalar UavNetwork.uav[0].app[0] "packets sent" 40` etc. Say: *"packet/application-level scalars — connectivity and delivery measured at the network layer, exactly the observables Sec. VIII-F audits."*

PDR number to quote: **98.75% unicast PDR** measured across the earlier scenario runs — from this output family.

---

## 5. PART D — THE ML SIDE IN 3 MIN (optional, if time)

Live smoke run in PowerShell (fast, ~30 s):

```powershell
cd C:\Users\gbust\Downloads\Academic\Courses\Machine_learning_in_wireless_network\Project1
python scripts/run_g3.py --regime low_comm --seeds 0 --episodes 3 --n-steps 200
```

Expected tail: `[MAPPO ep 2] ... CK=0.378 AG=1.000 ...` and `seed 0: DONE`. Say: *"a 3-episode smoke of the same trainer that produced the paper's runs — full runs are 200 episodes × 8 seeds, heavy, so we keep those in artefacts."*

Then show one number: `python scripts/analyze_g3.py small_battery` → `mean CK=0.371, headroom 0.629 OK`.

---

## 6. NUMBERS CHEAT SHEET (quote exactly, they're audited)

| Number | Where it comes from |
|---|---|
| N ≥ 4K = 8; old N=5 config infeasible | Feasibility certificate, paper §III-G [N pp.8–9], `feasibility.py` |
| Reactive 0.953 vs MAPPO 0.674 ± 0.060, **gap 0.298 [0.248, 0.349]** | Base comparison Table XII [N pp.20–21], `results_main.csv` |
| Claim audit: **38 items, 34 verified, 0 fail** | `claim_audit.py`, paper §VIII-F [N p.28] |
| PHY path-loss equivalence **0.012 dB** over 24 points | `phy_equivalence.py`, [N pp.28–29] |
| INET run: **t=40 s, event #71885**, ~implicit 90 s wall | live demo just now |
| Link margins +43.2 / +46.9 dB → geometry, not radio, binds | [N p.29] |
| 134-test suite, all passing | `ml_impl/tests/` |

---

## 7. LIKELY PROF QUESTIONS + 20-SECOND ANSWERS

1. **"Is this actually OMNeT++ or just your Python?"**
   → "Real OMNeT++ 6.4 + INET 4.6, built from source in WSL (libINET.so, 130 MB). Our Python produces the mobility traces; OMNeT's 802.11 MAC/PHY produces the network metrics. Neither replaces the other."
2. **"Why not do everything in OMNeT++?"**
   → "Phase 1 control-loop iteration is 100× faster in Python (~230 steps/s per env). OMNeT is fidelity: the MARL learns against the surrogate, INET validates the physical layer. That's the paper's three-phase audit-trail design [N p.18]."
3. **"What does the Qtenv animation show?"**
   → "UAV motion from our controller traces, 802.11 beacons and unicast app traffic, radio interference/propagation per INET's BreakpointPathLoss — the exact path loss our Python model reproduces to 0.012 dB."
4. **"Where does INET's config come from?"**
   → "`omnetpp.ini` in examples/uav_omnet — I can show it; trace file selector, sim-time 40 s, radio params. Identical copy in our repo under Simulation/omnet_uav/."
5. **"Show me one audited claim."**
   → Open claim audit output or `kilo/...`/`gate_final*.txt`; pick: "σ=1.503 passes area test yet N=5 is infeasible for region — audit item I1."
6. **"Why is MAPPO losing to a rule good news?"**
   → "It's a measured negative result with a 95% CI and arms ruling out the cheap explanations — that's the paper's contribution: the evaluation methodology, not a win number."
7. **"What hardware/timing?"**
   → "i5-11400H, RTX 2050 (CPU chosen — 1.26× faster for this workload), BLAS pinned to 1 thread per concurrent run."
8. **"What's left?"**
   → "Phase 3 Simu5G scaffolded, not run with the learned policy — stated as limitation (vii). Runtime SNR probe exists but not usable for cross-validation — limitation (vi), reported honestly."

### Visual / internals questions about the running Qtenv window

9. **"Why are the UAV circles moving on some curves / arc patterns, not straight lines?"**
   → "BonnMotion mobility replays waypoint traces from our Python simulator — the controllers produce curved paths because of sequential waypoint interpolation, not random walk."
10. **"What are the expanding circles from a node when it transmits?"**
    → "That's INET's radio animation: the transmission geomagnetic sphere of one 802.11 frame — visual only. The actual delivery decision is the ScalarRadioMedium's per-receiver SNR computation, not the picture."
11. **"Why do only some packets get through? / is that a bug?"**
    → "No — that's the physics doing its job: path loss grows with distance, so a receiver beyond the sensitivity (−85 dBm) or under the SNR threshold (4 dB) silently drops the frame. That's exactly the instrument the paper's Sec VIII-F probes."
12. **"What is that simulation clock running at the top?"**
    → "Simulated time vs real time — the discrete-event kernel advances time event-to-event, so a 40 s mission with ~72k events finishes in seconds of wall-clock."
13. **"Where does the number 8 / 20 come from?"**
    → "From the report's corrected deployment: N = 8 UAVs from the feasibility certificate (N ≥ 4K = 8), M = 20 sensors — matches Table VII, and the OMNeT ini mirrors it."
14. **"Why 6 Mbps and 0.5 W?"**
    → "6 Mbps is the lowest mandatory 802.11 OFDM rate (the paper's radio gate threshold), 0.5 W is the report's Ptx, two orders below the avionics budget and under the 1 W regulatory ceiling."
15. **"Can I change something and re-run live?"**
    → "Yes — change `sim-time-limit` or `sendInterval` in the ini, Ctrl+R. Also there's the negative-control run (PhyValidationControl) where transmitter.power is crushed by 60 dB and reception goes to zero — the demonstration that the observables respond to the physics."

### What the red arrows in the running window actually are (seen in the live recording)

- **Thick red arrows labelled `(WirelessSignal)UdpBasicAppData-0`** = the app packets (64 B, one per UAV per second) as **animated radio transmissions**; `UdpBasicApp` rotates through destination UAVs, so arrows fan out to different nodes.
- **Thick red arrows labelled `(WirelessSignal)WlanAck`** = the **802.11 MAC-layer ACKs**. Unicast data frames must be acknowledged after SIFS by the receiver — so what looks like a storm of red arrows after each data volley is *healthy* DCF acknowledgement traffic. This is exactly the mechanism behind the measured ~98.75% unicast PDR.
- **Dashed blue lines** = transmission→receiver relations of the shared medium (one send, everyone in range hears it), i.e. the fan-out visualization, not individual packets.
- **Small red rectangle around a node** (e.g., sensor[8]) = Qtenv's **mouse-selection highlight** on that module. Selected-node ring; nothing physical.
- **All UAVs bunched in the top-left corner early on** = our Python simulator's **initial connected-corner deployment** (Table VII of the report), about to follow the `episode_000.movements` trace — direct visual evidence the Python→OMNeT bridge is intact.
- **30-second narration:** "Red arrows are live 802.11 frames — the apps' UDP packets and the MAC-layer ACKs for unicast, so delivery is acknowledgement-based, which is why PDR is ~99%. Dotted blue is the shared medium fan-out; the UAVs are replaying the trajectories our RL simulator exported as BonnMotion — the red ring is just me having selected a node."



---

## 8. FALLBACK PLAN (if live anything fails)

| Failure | Fallback |
|---|---|
| IDE/Qtenv won't open (WSLg broken) | Run §1 Cmdenv in terminal + show `General-#0.sca`/`.vec` scalars live; say "GUI is WSLg presentation only — the simulation is headless-first." |
| Cmdenv run fails | Show last saved `results/General-#0.sca` + the earlier verified output: t=40 s, event #71885. Results are already on disk. |
| Python smoke hangs | Show `ml_impl/runs/g3/small_battery/team/seed_*.json` and results CSVs — artefacts exist. |
| Anything catastrophic | The paper PDF + `results_main.csv` + scalars are enough to narrate the whole story; never apologize, pivot to "the artefacts speak". |

---

## 9. FILES-ON-DISK MAP (if asked "where is X?")

```
Project1/
├─ Mlawn-midsem-tex.tex/.pdf          ← the paper (33 pp)
├─ Simulation/omnet_uav/              ← our OMNeT scenario copy (UavNetwork.ned, omnetpp.ini, traces/)
├─ ml_impl/
│  ├─ uav_wireless/ (env.py, mappo.py, train.py, wireless.py, runner.py)
│  ├─ analysis/ (claim_audit.py, feasibility.py, phy_equivalence.py, ...)
│  ├─ tests/ (134 unit tests)
│  └─ runs/ + results_*.csv           ← all experimental artefacts
├─ scripts/ (run_g3.py, analyze_g3.py, generate-trace helpers, run_stepB_*.py)
├─ REPORT_COMPARISON.md               ← old vs new report diff, page-cited
└─ DEMO_GUIDE.md                      ← this file
WSL side:
/home/gbust/omnetpp_ws/
├─ omnetpp-6.4.0/                     ← OMNeT++ + IDE
└─ inet-4.6.0/examples/uav_omnet/     ← the live scenario (libINET.so built at out/clang-release/src/)
```

---

## 10. DEMO FLOW SUMMARY (print this, tick as you go)

- [ ] 0:00 — One-line story + open paper at p.28
- [ ] 1:00 — OMNeT++ IDE open → `UavNetwork.ned` (graph view, then Source)
- [ ] 4:00 — `omnetpp.ini` → point at traceFile + sim-time
- [ ] 5:00 — **Qtenv animated run** (the money shot), fast-forward to finish
- [ ] 8:00 — Our code: env.py → mappo.py → trace exporter (bridge slide-mouth)
- [ ] 11:00 — claim_audit.py + feasibility.py (2 audited claims shown)
- [ ] 13:00 — Live Cmdenv rerun + grep scalars (PDR)
- [ ] 16:00 — MAPPO 3-episode smoke + analyze_g3 number
- [ ] 18:00 — Q&A loop w/ cheat sheet; end on the negative-result + audit story
