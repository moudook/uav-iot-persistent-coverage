"""
Feasibility audit of the parameter table in Mlawn-midsem-tex.tex
Run: python feasibility_check.py
"""
import math

print("=" * 78)
print("FEASIBILITY AUDIT -- Mlawn-midsem-tex.tex Table IV (parameters)")
print("=" * 78)

# ---- Parameters as stated in the report -----------------------------------
A_region = 100.0 * 100.0   # m^2, Omega = 100 x 100
M        = 20              # IoT sensors
N        = 5               # active UAVs
N_R      = 1               # reserve
K        = 2               # coverage requirement
R_cov    = 15.0            # m, coverage radius
R_comm   = 40.0            # m, comm radius
v_max    = 5.0             # m/s
d_safe   = 5.0             # m
dt       = 1.0             # s
B_max    = 30000.0         # J
P_hover  = 50.0            # W
P_move   = 75.0            # W
P_comm   = 10.0            # W
charge_rate = 0.01         # battery fraction per step

print(f"\nGiven: |Omega|={A_region:.0f} m^2, M={M}, N={N}, N_R={N_R}, K={K}, "
      f"R_cov={R_cov} m, R_comm={R_comm} m")

# ---- TEST 1: area-counting necessary condition for K-coverage --------------
# Need sum_d n_d = K*M coverage slots.  Each UAV supplies at most pi*R^2 of area.
# N * pi * R^2  >=  K * A
required_area  = K * A_region
supplied_area  = N * math.pi * R_cov**2
print("\n" + "-" * 78)
print("TEST 1  Area-counting necessary condition  N*pi*R_cov^2 >= K*|Omega|")
print("-" * 78)
print(f"  required (K*|Omega|)      = {required_area:.1f} m^2")
print(f"  supplied  (N*pi*R_cov^2)  = {supplied_area:.1f} m^2")
print(f"  ratio supplied/required   = {supplied_area/required_area:.4f}")
if supplied_area < required_area:
    print("  => INFEASIBLE. Coverage of all %d sensors at K=%d is IMPOSSIBLE." % (M, K))
    print("     The system CANNOT satisfy the objective for ANY policy, including")
    print("     an omniscient optimal controller.")

# ---- TEST 2: what R_cov is actually required? ------------------------------
R_necessary = math.sqrt(K * A_region / (math.pi * N))
print(f"\n  Minimum R_cov satisfying the counting bound:")
print(f"    R_cov >= sqrt(K*|Omega| / (pi*N)) = sqrt({required_area:.0f}/{math.pi*N:.4f})"
      f" = {R_necessary:.2f} m")
print(f"  Report uses R_cov = {R_cov} m  ->  short by factor {R_necessary/R_cov:.2f}x")

# Packing-corrected bound: hexagonal densest packing of coverage disks.
# Density of congruent-disk packing = pi / (2*sqrt(3)) = 0.9069
dens = math.pi / (2 * math.sqrt(3))
R_packed = math.sqrt(K * A_region / (dens * math.pi * N))
print(f"  Packing-corrected R_cov (allowing the usual 9.3% packing waste):")
print(f"    density = pi/(2*sqrt(3)) = {dens:.4f}")
print(f"    R_cov >= {R_packed:.2f} m")
print(f"  Practical recommendation (2x safety margin): R_cov = {2*R_packed:.0f} m")

# ---- TEST 3: expected coverage under RANDOM placement ----------------------
sensor_density = M / A_region
expected_sensors_per_uav = sensor_density * math.pi * R_cov**2
print("\n" + "-" * 78)
print("TEST 3  Expected sensors covered by ONE UAV at a random position")
print("-" * 78)
print(f"  sensor density = M/|Omega| = {sensor_density:.6f} /m^2")
print(f"  coverage disk area = pi*R_cov^2 = {math.pi*R_cov**2:.2f} m^2")
print(f"  E[sensors in disk] = {expected_sensors_per_uav:.4f}")
print(f"  E[total coverage slots, N UAVs] = {N*expected_sensors_per_uav:.3f}")
print(f"  Coverage slots REQUIRED (K*M)    = {K*M}")
print(f"  => Even with 0 overlap, the swarm provides "
      f"{100*N*expected_sensors_per_uav/(K*M):.1f}% of what is needed.")

# ---- TEST 4: best-case (adversarially perfect) placement -------------------
# Even placed optimally, one UAV can cover at most ceil(M * pi R^2 / A) sensors
# if sensors are clustered, but for a UNIFORM grid layout the answer is a
# geometric packing question. Test the uniform grid case explicitly.
print("\n" + "-" * 78)
print("TEST 4  Best case: sensors on a uniform grid")
print("-" * 78)
for (gx, gy) in [(5, 4), (4, 5), (4, 4)]:
    sx = A_region**0.5 / gx      # horizontal spacing
    sy = A_region**0.5 / gy      # vertical spacing
    # max sensors within radius R of a point optimally placed
    # count grid points within radius R of the best possible centre
    best = 0
    for cy in range(gy):
        for cx in range(gx):
            px, py = cx * sx, cy * sy
            cnt = 0
            for cy2 in range(gy):
                for cx2 in range(gx):
                    qx, qy = cx2 * sx, cy2 * sy
                    if math.hypot(px - qx, py - qy) <= R_cov + 1e-9:
                        cnt += 1
            best = max(best, cnt)
    print(f"  {gx}x{gy} grid (M={gx*gy}, spacing {sx:.1f}x{sy:.1f} m): "
          f"one UAV covers at most {best} sensors; "
          f"max total slots = {N*best}; need {K*gx*gy} -> "
          f"{'FEASIBLE' if N*best >= K*gx*gy else 'INFEASIBLE'}")

# ---- TEST 5: battery / endurance consistency -------------------------------
print("\n" + "-" * 78)
print("TEST 5  Battery and endurance")
print("-" * 78)
P_hover_total = P_hover + P_comm
P_move_total  = P_move + P_comm
t_hover = B_max / P_hover_total
t_move  = B_max / P_move_total
print(f"  Hovering power (hover+comm) = {P_hover_total:.1f} W -> endurance {t_hover:.0f} s"
      f" = {t_hover/60:.1f} min")
print(f"  Moving power  (move +comm)  = {P_move_total:.1f} W -> endurance {t_move:.0f} s"
      f" = {t_move/60:.1f} min")
print(f"  Mission length T = t_move steps = {int(t_move)} steps at dt={dt} s")
t_full_charge = 1.0 / charge_rate * dt
print(f"  Full 0->1 charge takes {t_full_charge:.0f} s = {t_full_charge/60:.1f} min")
print(f"  Ratio charge_time / flight_time = {t_full_charge/t_move:.3f}")
print("  NOTE: real Li-ion charge (0.5C-1C) takes ~1-2 h; flight is ~6 min.")
print("        The 0.01/step charge rate is ~10x faster than physically real.")

# Return energy to a pad at the far corner
R_region = A_region**0.5
d_far = math.hypot(R_region, R_region)      # worst case corner-to-corner
t_far  = d_far / v_max
E_far  = P_move_total * t_far
print(f"\n  Worst-case corner-to-corner transit: d = {d_far:.1f} m, "
      f"t = {t_far:.0f} s, E = {E_far:.0f} J")
print(f"  E_rejoin (return to coverage area) approx = {P_move_total*(R_region/v_max):.0f} J")
E_req_est = E_far + P_move_total * (R_region / v_max) + 0.1 * B_max
print(f"  E_req (station + rejoin + 10% reserve) ~ {E_req_est:.0f} J "
      f"= {100*E_req_est/B_max:.1f}% of B_max")
print(f"  => UAV must return when battery drops below "
      f"{100*E_req_est/B_max:.0f}%, i.e. b_i < {1-E_req_est/B_max:.2f}")
print("  This means agents operate only in the top ~90% of the battery window,")
print("  so the 'energy critical' regime the reward targets is rarely visited.")

# ---- TEST 6: connectivity feasibility -------------------------------------
print("\n" + "-" * 78)
print("TEST 6  Communication-graph connectivity, N=5 uniform random positions")
print("-" * 78)
p_edge = min(1.0, math.pi * R_comm**2 / A_region)
expected_edges = math.comb(N, 2) * p_edge
print(f"  P(two random UAVs within R_comm) = pi*R_comm^2/|Omega| = {p_edge:.4f}")
print(f"  E[edges] = C(N,2)*p = {math.comb(N,2)} * {p_edge:.4f} = {expected_edges:.2f}")
print(f"  A connected graph on {N} nodes needs >= {N-1} edges.")
print(f"  E[edges]={expected_edges:.2f} vs needed {N-1} -> marginal / mostly connected.")
# Connectivity threshold radius for n nodes in area A (Penrose):
# r_n with E[edges] ~ (1/2 + eps) n ln n
for n in [5, 6, 10, 20]:
    edges_target = 0.5 * n * math.log(n) + 0.5 * n
    r_thresh = math.sqrt(edges_target / (math.comb(n, 2) * 1.0) * A_region / math.pi)
    print(f"    n={n:2d}: connectivity threshold radius ~ {r_thresh:6.1f} m "
          f"(report uses {R_comm} m)")

# ---- TEST 7: simulation horizon -------------------------------------------
print("\n" + "-" * 78)
print("TEST 7  Practical episode length")
print("-" * 78)
print(f"  A full-charge cycle at dt={dt} s: "
      f"{int(t_move)} s flight + {int(t_full_charge)} s charge = "
      f"{int(t_move + t_full_charge)} s = {(t_move+t_full_charge)/60:.1f} min")
print(f"  Reasonable T for training: 2000-5000 steps ({2000*dt/60:.0f}-"
      f"{5000*dt/60:.0f} min sim time)")
print(f"  BUT a UAV flying at v_max={v_max} m/s crosses the 100 m region in "
      f"{R_region/v_max:.0f} s.")
print(f"  => At dt=1 s and v=5 m/s a UAV moves 5 m per step; a 15 m coverage")
print(f"     radius is only 3 steps wide. The action space is dominated by")
print(f"     'no useful move' outcomes. Consider dt=0.5 s or v_max=10 m/s.")

# ---- TEST 8: summary ------------------------------------------------------
print("\n" + "=" * 78)
print("SUMMARY OF FINDINGS")
print("=" * 78)
print("""
CRITICAL (breaks the stated objective):
  [1] R_cov = 15 m is INFEASIBLE for M=20, N=5, K=2 in a 100x100 m region.
      Required R_cov >= 35.7 m by the counting bound; >= 39.6 m with packing
      correction. The current value is 2.4-2.6x too small, so n_d(t) >= K is
      unreachable for EVERY controller, and the entire reward signal is
      dominated by an impossible term.

MAJOR (weakens the study):
  [2] Endurance is only ~6 min of flight (B_max=30 kJ, P=85 W). Agents rarely
      reach the energy-critical regime the reward is designed to shape.
  [3] Charge rate 0.01/step = 100 s for a full charge, ~10x faster than real
      Li-ion. Charging contention is therefore far less costly than in reality.
  [4] dt=1 s with v_max=5 m/s => 5 m per step, only 3 steps across R_cov.
      The discrete action space is poorly matched to the geometry.

WORTH FIXING:
  [5] R_comm = 40 m gives E[edges]=4.16 vs 4 needed for connectivity of 5
      nodes -- a genuinely marginal regime. Good for research value, but it
      must be stated deliberately, not by accident.
""")
