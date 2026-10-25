# Information Channel Model (Step B design)

## Purpose
Fit a model that gives, for a UAV link:
- Delivery probability (PDR)
- Delay/age distribution

as a function of:
- Distance between sender and receiver (d)
- Hop count (h)
- Neighbour count (degree, k)
- Traffic load (lambda)
- Topology state (connected/disconnected, articulation)

## Data collection
Run INET scenarios with varying:
- UAV counts (N=4,6,8,10)
- Random initial positions (50 seeds)
- Traffic loads (beacon interval 0.5s, 1s, 2s)
- Radio ranges (R_comm = 25, 30, 40)

For each scenario, extract per-link:
- sender_id, receiver_id
- distance (Euclidean)
- delivery (0/1 per packet)
- delay (seconds)

## Model
Option A: Logistic regression for PDR, linear regression for delay.
  PDR = sigmoid(beta0 + beta1*d + beta2*h + beta3*k + beta4*load)
  delay = alpha0 + alpha1*d + alpha2*h + alpha3*load

Option B: Lookup table (bin distance into 5m bins, compute empirical PDR per bin).

Option C: Small GLM with interaction terms.

## Validation
- Held-out INET runs (20% of scenarios)
- Plot predicted vs simulated PDR
- Report R^2 and calibration

## Integration with Python sim
- Replace ideal information with channel model
- Training: use channel model to compute received observations (probabilistic)
- Evaluation: closed-loop INET (Step C/D)

## Status
- Step A: basic scenario runs, beacons work (unicast PDR 98.75%)
- Step B: NOT STARTED. Need to collect data and fit model.
---
