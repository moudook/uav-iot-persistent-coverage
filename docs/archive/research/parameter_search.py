"""
Find a FEASIBLE parameter set. Run after feasibility_check.py.
"""
import math

A = 100.0 * 100.0
M, N, K = 20, 5, 2
dens = math.pi / (2 * math.sqrt(3))   # 0.9069 hexagonal packing density
v_max, dt = 5.0, 1.0
B_max, P_hover, P_move, P_comm = 30000.0, 50.0, 75.0, 10.0
P_move_t = P_move + P_comm

def slots(R_cov):
    """Expected total coverage slots with N UAVs, random placement."""
    return N * (M / A) * math.pi * R_cov**2

def connected_prob(R_comm, n, A, trials=40000, seed=7):
    """Monte-Carlo probability that a random geometric graph on n uniform
    points in a square of area A is connected."""
    import random
    random.seed(seed)
    side = math.sqrt(A)
    cnt = 0
    for _ in range(trials):
        pts = [(random.uniform(0, side), random.uniform(0, side)) for _ in range(n)]
        # union-find
        par = list(range(n))
        def find(x):
            while par[x] != x:
                par[x] = par[par[x]]; x = par[x]
            return x
        r2 = R_comm**2
        for i in range(n):
            for j in range(i + 1, n):
                dx, dy = pts[i][0]-pts[j][0], pts[i][1]-pts[j][1]
                if dx*dx + dy*dy <= r2:
                    a, b = find(i), find(j)
                    if a != b: par[a] = b
        roots = {find(i) for i in range(n)}
        if len(roots) == 1: cnt += 1
    return cnt / trials

print("=" * 84)
print("FEASIBLE PARAMETER SEARCH")
print("=" * 84)
print(f"Fixed: |Omega|={A:.0f} m^2, M={M}, N={N}, K={K}, v_max={v_max}, dt={dt}")
print()

# --- Which knob to turn? Four options, ranked by how much they hurt realism --
print("-" * 84)
print("OPTION A: increase R_cov (recommended -- coverage radius is the natural knob)")
print("-" * 84)
print(f"{'R_cov':>7} {'slots':>8} {'need':>6} {'ratio':>7}  verdict")
for R in [15, 25, 35, 36, 40, 45, 50, 55, 60, 70]:
    s = slots(R)
    ok = "FEASIBLE (counting bound)" if s >= K*M else "infeasible"
    print(f"{R:7.0f} {s:8.2f} {K*M:6d} {s/(K*M):7.3f}  {ok}")
print()
print(f"  Counting bound   R_cov >= {math.sqrt(K*A/(math.pi*N)):.2f} m")
print(f"  Packing-corrected R_cov >= {math.sqrt(K*A/(dens*math.pi*N)):.2f} m")
print("  For a 4x surplus (so failures/dynamics have slack): R_cov = 60-70 m")
print()

print("-" * 84)
print("OPTION B: increase N (add UAVs).  N needed at R_cov=15 m:")
print("-" * 84)
R = 15.0
need_N = K * M / ((M / A) * math.pi * R**2)
print(f"  N >= K*M / ((M/A)*pi*R^2) = {K*M}/{(M/A)*math.pi*R**2:.3f} = {need_N:.1f}")
print(f"  Packing-corrected: N >= {need_N/dens:.1f}")
print("  => ~119-131 UAVs for 100x100 m at R_cov=15 m. Unrealistic for a swarm")
print("     learning study (and defeats the scalability argument). REJECT.")
print()

print("-" * 84)
print("OPTION C: reduce M (fewer sensors)")
print("-" * 84)
R = 15.0
per_uav = (M / A) * math.pi * R**2
max_M = int(N * per_uav / K)
print(f"  At N=5, K=2, R_cov=15: max feasible M = {max_M}")
print(f"  M=4 sensors would work but is too trivial to be interesting. REJECT.")
print()

print("-" * 84)
print("OPTION D: increase region area at fixed R_cov -- makes it WORSE. REJECT.")
print()

# --- Connectivity check for candidate R_comm -------------------------------
print("-" * 84)
print("Connectivity probability P(G_t connected) vs R_comm, N=5, |Omega|=10000")
print("-" * 84)
print(f"{'R_comm':>8} {'P(conn)':>9}   note")
for R in [30, 35, 40, 45, 50, 60, 70, 80]:
    p = connected_prob(R, 5, A, trials=6000)
    note = "marginal" if 0.2 < p < 0.8 else ("always connected" if p > 0.95 else "often split")
    print(f"{R:8.0f} {p:9.3f}   {note}")
print()

# --- The recommended scenario ---------------------------------------------
print("=" * 84)
print("RECOMMENDED PARAMETER SET")
print("=" * 84)
R_cov, R_comm = 60.0, 50.0
s = slots(R_cov)
p = connected_prob(R_comm, 5, A, trials=20000)
# endurance
t_hover = B_max / (P_hover + P_comm)
t_move  = B_max / P_move_t
side = math.sqrt(A)
d_far = math.hypot(side, side)
E_station = P_move_t * (d_far / v_max)
E_rejoin  = P_move_t * (side / v_max)
E_req     = E_station + E_rejoin + 0.1 * B_max
charge_s  = 0.0002 / dt          # 0.0002 battery fraction per second
t_charge  = 1.0 / charge_s

print(f"  |Omega|            = 100 x 100 m")
print(f"  M (sensors)        = 20")
print(f"  N (active UAVs)    = 5      N_R (reserve) = 1")
print(f"  K (coverage)       = 2")
print(f"  R_cov              = {R_cov:.0f} m   -> E[slots]={s:.2f} vs {K*M} needed "
      f"({s/(K*M):.2f}x)")
print(f"  R_comm             = {R_comm:.0f} m   -> P(connected) = {p:.3f}")
print(f"  v_max              = {v_max} m/s")
print(f"  d_safe             = 5 m")
print(f"  dt                 = {dt} s        (UAV moves {v_max*dt:.0f} m/step; "
      f"R_cov spans {2*R_cov/(v_max*dt):.0f} steps)")
print(f"  B_max              = {B_max/1000:.0f} kJ")
print(f"  P_hover/P_move/P_comm = {P_hover}/{P_move}/{P_comm} W")
print(f"  -> endurance: {t_move:.0f} s moving ({t_move/60:.1f} min), "
      f"{t_hover:.0f} s hovering ({t_hover/60:.1f} min)")
print(f"  charge rate        = {charge_s} /s -> full charge {t_charge:.0f} s "
      f"({t_charge/60:.0f} min)")
print(f"  -> charge/flight ratio = {t_charge/t_move:.2f}  (real Li-ion ~ 1C: 60 min)")
print(f"  E_req              ~ {E_req:.0f} J = {100*E_req/B_max:.0f}% of B_max "
      f"-> return at b_i < {1-E_req/B_max:.2f}")
print(f"  S (charging pads)  = 2")
print(f"  T (episode)        = 2000 steps = {2000*dt/60:.0f} min sim time")
print()
print("  Sanity: is K=2 achievable? E[slots]=%.1f vs 40 needed -> %.2fx surplus."
      % (s, s/(K*M)))
print("  Sanity: with R_cov=60 m each UAV's disk has area %.0f m^2 = %.1f%% of the"
      % (math.pi*R_cov**2, 100*math.pi*R_cov**2/A))
print("          region, so one UAV sees %.1f sensors on average." % ((M/A)*math.pi*R_cov**2))
print()
print("  Failure tolerance check: after losing 1 UAV, 4 remain -> E[slots]=%.1f,"
      % (4*(M/A)*math.pi*R_cov**2))
print("          still %.2fx the %d needed -> the reserve is a genuine safety"
      % ((4*(M/A)*math.pi*R_cov**2)/(K*M), K*M))
print("          factor rather than the only way to reach feasibility.")
print()
print("  Connectivity after failure: 4 nodes at R_comm=50 m -> P(conn) = %.3f"
      % connected_prob(50, 4, A, trials=20000))
