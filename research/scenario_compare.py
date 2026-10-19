"""Scenario comparison -- pick a defensible configuration. Run third."""
import math, random

dens = math.pi / (2*math.sqrt(3))

def conn_prob(R_comm, n, A, trials=8000, seed=11):
    random.seed(seed); side = math.sqrt(A); c = 0
    for _ in range(trials):
        pts = [(random.uniform(0,side), random.uniform(0,side)) for _ in range(n)]
        par = list(range(n))
        def find(x):
            while par[x]!=x: par[x]=par[par[x]]; x=par[x]
            return x
        r2 = R_comm**2
        for i in range(n):
            for j in range(i+1,n):
                dx,dy = pts[i][0]-pts[j][0], pts[i][1]-pts[j][1]
                if dx*dx+dy*dy <= r2:
                    a,b = find(i),find(j)
                    if a!=b: par[a]=b
        if len({find(i) for i in range(n)})==1: c+=1
    return c/trials

def slots(R_cov, N, M, A): return N*(M/A)*math.pi*R_cov**2

SCEN = [
    ("S-A  as-written      ", 100, 20, 5, 2, 15, 40),
    ("S-B  bigger radius  ", 100, 20, 5, 2, 40, 50),
    ("S-C  smaller region ",  60, 20, 5, 2, 30, 40),
    ("S-D  smaller region2",  60, 20, 5, 2, 35, 45),
    ("S-E  mid            ",  80, 20, 5, 2, 35, 45),
    ("S-F  mid alt        ",  80, 16, 5, 2, 35, 45),
]
print("="*96)
print(f"{'scenario':20} {'|Om|':>6} {'M':>3} {'N':>2} {'K':>2} {'Rcov':>5} {'Rcom':>5} "
      f"{'slots':>7} {'need':>5} {'surp':>6} {'P(conn)':>8} {'P(conn)N-1':>10} {'disk/Om':>9}")
print("="*96)
for name, side, M, N, K, Rc, Rcm in SCEN:
    A = side*side
    s = slots(Rc, N, M, A)
    need = K*M
    pc  = conn_prob(Rcm, N, A)
    pc1 = conn_prob(Rcm, N-1, A)
    print(f"{name:20} {A:6.0f} {M:3d} {N:2d} {K:2d} {Rc:5.0f} {Rcm:5.0f} "
          f"{s:7.1f} {need:5d} {s/need:6.2f} {pc:8.3f} {pc1:10.3f} "
          f"{100*math.pi*Rc*Rc/A:8.0f}%")
print("="*96)
print("surp   = expected coverage slots / required slots.  >=1.3 means K-coverage is")
print("         reachable with slack for movement + failure.")
print("disk/Om= coverage disk area as a fraction of the region. 30-80% means a UAV")
print("         covers a real but not trivial fraction of the area.")
print("P(conn) = probability the communication graph is connected (Monte-Carlo, 8k trials).")
print("P(conn)N-1 = same after one UAV fails. Want this > 0.5 so the reserve helps.")
print()

# --- Endurance / charging realism -------------------------------------------
B = 30000.0; Ph, Pm, Pc = 50.0, 75.0, 10.0; Pm_t = Pm+Pc
print("="*96); print("ENERGY: fixing the endurance and charge-rate problems"); print("="*96)
print(f"{'config':28} {'flight':>9} {'charge 0->1':>13} {'ratio':>7} {'return@':>9}")
print("-"*96)
for label, Bcap, Pmv, rate in [
    ("as-written 30kJ/85W/0.01ps", 30000.0, 85.0, 0.01),
    ("30kJ / 85W / 0.002 p-step ", 30000.0, 85.0, 0.002),
    ("60kJ / 85W / 0.001 p-step ", 60000.0, 85.0, 0.001),
    ("60kJ / 60W / 0.001 p-step ", 60000.0, 60.0, 0.001),
    ("120kJ/85W / 0.0005 p-step",120000.0,85.0, 0.0005),
]:
    tf = Bcap/Pmv; tc = 1.0/rate
    Ereq = 2404 + 1700 + 0.1*Bcap
    print(f"{label:28} {tf:6.0f}s={tf/60:3.1f}m {tc:8.0f}s={tc/60:5.1f}m "
          f"{tc/tf:7.2f} {100*Ereq/Bcap:8.0f}%")
print()
print("Target: ratio 5-15x (real Li-ion at 1C charges ~60 min; a 10-min endurance")
print("quadrotor gives ratio ~6). flight 8-20 min. return threshold 15-30%.")
print("=> '60kJ / 85W / 0.001 per step' is the most defensible row.")
print()

# --- dt / resolution --------------------------------------------------------
print("="*96); print("TIME-STEP: matching dt to the coverage radius"); print("="*96)
print(f"{'Rcov':>5} {'v':>4} {'dt':>5} {'m/step':>7} {'steps across 2*Rcov':>20} {'verdict':>10}")
for Rc, v, dt in [(15,5,1.0),(40,5,1.0),(40,5,0.5),(40,10,0.5),(40,10,1.0),
                  (30,10,1.0),(30,8,1.0)]:
    steps = 2*Rc/(v*dt)
    verdict = "too coarse" if steps<8 else "good"
    print(f"{Rc:5.0f} {v:4.0f} {dt:5.2f} {v*dt:7.1f} {steps:20.1f} {verdict:>10}")
print()
print("Rule of thumb: want >= 10 control steps across the coverage diameter,")
print("i.e. 2*R_cov / (v_max*dt) >= 10  ->  dt <= 2*R_cov / (10*v_max)")
print("With R_cov=40, v_max=5: dt <= 1.6 s. With v_max=10: dt <= 0.8 s.")
