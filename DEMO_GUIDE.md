# DEMO — commands only

## 1. INET headless (PowerShell)

```powershell
wsl -d Ubuntu -- bash -c "cd /home/gbust/omnetpp_ws && opp_env run inet-4.6.0 -c 'cd /home/gbust/omnetpp_ws/inet-4.6.0/examples/uav_omnet && opp_run -u Cmdenv -l /home/gbust/omnetpp_ws/inet-4.6.0/out/clang-release/src/libINET.so -n /home/gbust/omnetpp_ws/inet-4.6.0/src:/home/gbust/omnetpp_ws/inet-4.6.0/examples /home/gbust/omnetpp_ws/inet-4.6.0/examples/uav_omnet/omnetpp.ini 2>&1 | tail -8'"
```

## 2. INET visual Qtenv (PowerShell)

```powershell
wsl -d Ubuntu -- bash -c "cd /home/gbust/omnetpp_ws && DISPLAY=:0 timeout 60 opp_env run inet-4.6.0 -c 'cd /home/gbust/omnetpp_ws/inet-4.6.0/examples/uav_omnet && opp_run -u Qtenv -l /home/gbust/omnetpp_ws/inet-4.6.0/out/clang-release/src/libINET.so -n /home/gbust/omnetpp_ws/inet-4.6.0/src:/home/gbust/omnetpp_ws/inet-4.6.0/examples /home/gbust/omnetpp_ws/inet-4.6.0/examples/uav_omnet/omnetpp.ini' 2>&1 | tail -5"
```

## 3. Packet scalars (WSL)

```bash
cd /home/gbust/omnetpp_ws/inet-4.6.0/examples/uav_omnet && grep -E 'scalar.*(packets sent|received)' results/General-#0.sca | head -16
```

## 4. Energy certificate (PowerShell)

```powershell
python scripts/energy_certificate.py --T 400
python scripts/energy_certificate.py --T 2000
python scripts/energy_certificate.py --T 400 --sweep
```

## 5. Claim audit (PowerShell)

```powershell
python ml_impl/analysis/claim_audit.py
```