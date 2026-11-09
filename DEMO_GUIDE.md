# DEMO GUIDE — command list (what to run, what you will see)

Read this top to bottom during the meeting. Every box is: console, command, expected result.

---

## 1. INET headless check — Windows PowerShell (30 seconds)

Console: PowerShell in repo.

```powershell
wsl -d Ubuntu -- bash -c "cd /home/gbust/omnetpp_ws && opp_env run inet-4.6.0 -c 'cd /home/gbust/omnetpp_ws/inet-4.6.0/examples/uav_omnet && opp_run -u Cmdenv -l /home/gbust/omnetpp_ws/inet-4.6.0/out/clang-release/src/libINET.so -n /home/gbust/omnetpp_ws/inet-4.6.0/src:/home/gbust/omnetpp_ws/inet-4.6.0/examples /home/gbust/omnetpp_ws/inet-4.6.0/examples/uav_omnet/omnetpp.ini 2>&1 | tail -8'"
```

You will see:
- `Simulation time limit reached -- at t=40s, event #71885`
- `End.`
- No window. Headless by design.

If this fails, stop. The machine needs Virtual Machine Platform enabled + reboot, then re-run.

## 2. INET visual (Qtenv) — PowerShell (1 minute, opens a real window)

Console: PowerShell in repo. This one OPENS the OMNeT++ window on Windows.

```powershell
wsl -d Ubuntu -- bash -c "cd /home/gbust/omnetpp_ws && DISPLAY=:0 timeout 60 opp_env run inet-4.6.0 -c 'cd /home/gbust/omnetpp_ws/inet-4.6.0/examples/uav_omnet && opp_run -u Qtenv -l /home/gbust/omnetpp_ws/inet-4.6.0/out/clang-release/src/libINET.so -n /home/gbust/omnetpp_ws/inet-4.6.0/src:/home/gbust/omnetpp_ws/inet-4.6.0/examples /home/gbust/omnetpp_ws/inet-4.6.0/examples/uav_omnet/omnetpp.ini' 2>&1 | tail -5"
```

You will see:
- A Qtenv window appears: 8 blue UAV nodes following BonnMotion paths, 20 grey sensor nodes, red sink at centre.
- Arrows are live 802.11 frames (UDP beacons + MAC ACKs).
- Press the fast-run button so the 40 s run finishes in seconds.

## 3. Packet scalars — WSL (10 seconds)

Console: WSL (`wsl -d Ubuntu`).

```powershell
cd /home/gbust/omnetpp_ws/inet-4.6.0/examples/uav_omnet && grep -E 'scalar.*(packets sent|received)' results/General-#0.sca | head -16
```

You will see:
- `scalar UavNetwork.uav[i].app[0] "packets sent" 40` for i = 0..7
- `packets received` values per UAV.

Say: "INET produced these at the MAC/PHY level. The Python side produced the trajectories. Neither alone proves the claim; the two agree to 0.012 dB."

## 4. Energy certificate — PowerShell (seconds, no WSL)

```powershell
python scripts/energy_certificate.py --T 400
```

You will see:
- `persistent CK ceiling = 0.113   feasible = False`
- Finite-horizon ceiling `1.000` at T=400 s.

Then:

```powershell
python scripts/energy_certificate.py --T 2000
```

You will see ceiling `0.367`. That number is why the mission cannot persist.

## 5. Claim audit — PowerShell (seconds)

```powershell
python ml_impl/analysis/claim_audit.py
```

You will see tail: `34 claims verified, 0 FAILED, 4 recorded for transparency`. PHY equivalence `0.012 dB`, determinism 170/170.

Note: the audit covers physical/feasibility/protocol claims, not the tuned result table.

## 6. Report + deck

- `Mlawn-midsem-tex.pdf` — the 25-page report (self-contained).
- `PPT_SI_CHANGES.pdf` — the deck.

---

## One-line answers

- Live INET? Yes, verified 2026-11-09 (`t=40 s, event #71885, End`), plus Qtenv window.
- Uniform win? No. Wins: nominal, low comm, failures. Loses: small battery, spread start.
- Persistent? No. Ceiling 0.113 steady state; 400 s drains packs.
- New contribution? Certificate + frozen-policy protocol + honest negatives.
