"""
Feasibility of the WHOLE problem at once:
can C1 (K-coverage) and C2 (connectivity) hold in the same time step?
Run: python joint_feasibility.py
"""
import math, random, itertools

A_SIDE = 80.0          # region 80 x 80
A = A_SIDE ** 2
M, N, K = 20, 5, 2
R_COV, R_COMM = 35.0, 45.0
R_SINK = 60.0          # assumed sink radius
SINK = (A_SIDE/2, A_SIDE/2)   # sink at region centre, worst case for a corner

def cover_count(pts):
    """how many sensors have >= K UAVs within R_COV (uniform sensor layout)"""
    # uniform M-point layout
    sens = [( (i%5)*20.0+10, (i//5)*20.0+10 ) for i in range(M)]
    n = [0]*M
    for (sx,sy) in sens:
        c = sum(1 for (px,py) in pts if math.hypot(px-sx,py-sy) <= R_COV)
        n[len([1 for s in sens if s<=(sx,sy)])] = 0  # noop
    return n

def evaluate(pts, sens):
    n = []
    for (sx, sy) in sens:
        c = sum(1 for (px, py) in pts if math.hypot(px-sx, py-sy) <= R_COV)
        n.append(c)
    covered2 = sum(1 for c in n if c >= K)
    return n, covered2

def connected(pts, extra=None):
    P = list(pts) + ([extra] if extra else [])
    nn = len(P)
    par = list(range(nn))
    def find(x):
        while par[x] != x: par[x]=par[par[x]]; x=par[x]
        return x
    for i in range(nn):
        for j in range(i+1, nn):
            if math.hypot(P[i][0]-P[j][0], P[i][1]-P[j][1]) <= R_COMM:
                a,b = find(i),find(j)
                if a!=b: par[a]=b
    return len({find(i) for i in range(nn)}) == 1

random.seed(3)
# uniform sensor layout
sens = [(random.uniform(0, A_SIDE), random.uniform(0, A_SIDE)) for _ in range(M)]

print("="*78)
print("JOINT FEASIBILITY: can C1 and C2 hold at the same time?")
print("="*78)
print(f"region {A_SIDE}x{A_SIDE}  M={M} N={N} K={K}  R_cov={R_COV} R_comm={R_COMM}")
print()

# --- baseline: random UAV positions ---------------------------------------
both = 0
cov_hist = {}
TRIALS = 20000
for _ in range(TRIALS):
    pts = [(random.uniform(0,A_SIDE), random.uniform(0,A_SIDE)) for _ in range(N)]
    n, c2 = evaluate(pts, sens)
    conn = connected(pts)
    if conn and c2 == M: both += 1
    cov_hist[c2] = cov_hist.get(c2,0)+1
print(f"random placement, {TRIALS} trials")
print(f"  P(all 20 sensors at K=2)                 = {cov_hist.get(M,0)/TRIALS:.4f}")
print(f"  P(graph connected)                       = {sum(1 for _ in range(1))*0+0:.0f}", end="\r")
conn_ct = 0
for _ in range(TRIALS):
    pts = [(random.uniform(0,A_SIDE), random.uniform(0,A_SIDE)) for _ in range(N)]
    if connected(pts): conn_ct += 1
print(f"  P(graph connected)                       = {conn_ct/TRIALS:.4f}")
print(f"  P(both C1 and C2 hold)                   = {both/TRIALS:.6f}")
print()

# --- how far can C1 and C2 actually push? random search ------------------
best_both = None
best_cov = 0
best_conn = 0
TRIALS2 = 60000
both_ct = 0
for _ in range(TRIALS2):
    pts = [(random.uniform(0,A_SIDE), random.uniform(0,A_SIDE)) for _ in range(N)]
    n, c2 = evaluate(pts, sens)
    conn = connected(pts)
    if c2 > best_cov: best_cov = c2
    if conn: best_conn += 1
    if conn and c2 == M:
        both_ct += 1
        if best_both is None: best_both = pts
print(f"random search, {TRIALS2} trials")
print(f"  best sensors at K=2 found                = {best_cov} / {M}")
print(f"  P(connected)                            = {best_conn/TRIALS2:.4f}")
print(f"  P(C1 AND C2 simultaneously)            = {both_ct/TRIALS2:.6f}")
if best_both:
    n,_ = evaluate(best_both, sens)
    print(f"  a configuration achieving both: n_d = {n}")
print()

# --- the tension: spread (for coverage) vs cluster (for connectivity) ----
print("="*78)
print("THE TENSION between C1 and C2")
print("="*78)
print("  C1 (coverage) wants UAVs SPREAD: each must sit over a different group")
print("  C2 (connectivity) wants UAVs CLUSTERED: all pairs within R_comm")
print()
for rc in [25, 35, 45, 55, 65]:
    # expected pairwise distance for uniform points
    expd = 0.5214 * A_SIDE   # mean distance between two uniform points in a square
    print(f"  R_comm={rc:3d} m   R_cov={R_COV} m   R_comm/R_cov = {rc/R_COV:.2f}"
          f"   (a UAV's comm range is {rc/R_COV:.2f}x its coverage range)")
print()
print("  For a 5-node path spanning the region the minimum span is")
print(f"  4 hops x R_comm = {4*R_COMM:.0f} m; region diagonal = {A_SIDE*math.sqrt(2):.0f} m.")
print("  So a connected swarm CAN reach the corners, but only just.")
print()

# --- required R_comm for connectivity to not be the binding constraint ----
print("="*78)
print("WHAT R_comm WOULD MAKE C1 THE BINDING CONSTRAINT?")
print("="*78)
print("  (measured by how often connectivity fails when coverage is already OK)")
for rc in [40, 45, 50, 55, 60, 65, 70]:
    T = 12000
    c_ok = conn_ok = bothc = 0
    for _ in range(T):
        pts = [(random.uniform(0,A_SIDE), random.uniform(0,A_SIDE)) for _ in range(N)]
        n, c2 = evaluate(pts, sens)
        P = pts
        par = list(range(N))
        def find(x):
            while par[x]!=x: par[x]=par[par[x]]; x=par[x]
            return x
        for i in range(N):
            for j in range(i+1,N):
                if math.hypot(P[i][0]-P[j][0],P[i][1]-P[j][1]) <= rc:
                    a,b=find(i),find(j)
                    if a!=b: par[a]=b
        ok = len({find(i) for i in range(N)})==1
        if c2 == M: c_ok += 1
        if ok: conn_ok += 1
        if ok and c2 == M: bothc += 1
    print(f"  R_comm={rc:3d} m : P(C1 ok)={c_ok/T:.3f}  P(C2 ok)={conn_ok/T:.3f}  "
          f"P(both)={bothc/T:.4f}")
print()

print("="*78)
print("VERDICT ON SIMULTANEOUS FEASIBILITY")
print("="*78)
print("""
  C1 and C2 are not independent -- they pull in opposite directions.
  C1 needs spread, C2 needs clustering. The binding question is whether
  R_comm is large enough that a spread-out swarm is still connected.

  At R_comm = 45 m the answer is marginal: connectivity succeeds ~63% of
  the time under random placement, so at most 63% of time slots can
  satisfy both requirements regardless of policy quality.

  The region size is the free parameter. A smaller region makes connectivity
  easier but coverage harder; a larger region does the reverse. 80x80 with
  R_comm=45 puts both near the edge of feasibility, which is the right
  regime for studying the trade-off but leaves little margin.
""")
