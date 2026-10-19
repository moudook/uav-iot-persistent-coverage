"""Fig 3 return path + fix the dt inconsistency between Table VI and Table VII."""
import io, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
P = 'Mlawn-midsem-tex.tex'
s = io.open(P, encoding='utf-8').read()
n = 0
def sub(old, new, why):
    global s, n
    if old not in s:
        print(f'  !! NOT FOUND: {why}'); return False
    s = s.replace(old, new, 1); n += 1
    print(f'  ok  {why}'); return True

# --- Fig 3: replace the long diagonal with a clean 3-segment routed path ---
sub(r"""\draw[arr] (charge.east) -- ++(0.9,0) -- ++(0,-1.9)
      -- node[lab,above,pos=0.5] {battery restored} (serve.south |- charge.south);
\draw[arr] (transit.south) -- node[lab,right,pos=0.45] {failure detected} (recover.north);
\draw[arr] (charge.south) -- ++(0,-0.9) -| (recover.east);
\draw[arr] (recover.west) -| node[lab,below,pos=0.28] {reserve activated} (serve.south);""",
r"""\coordinate (rt) at ($(charge.east)+(0.9,0)$);
\draw[arr] (charge.east) -- (rt);
\draw[arr] (rt) -- ($(rt)+(0,-3.4)$);
\draw[arr] ($(rt)+(0,-3.4)$) -| node[lab,above,pos=0.30] {battery restored} (serve.south);
\draw[arr] (transit.south) -- node[lab,right,pos=0.40] {failure detected} (recover.north);
\draw[arr] (charge.south) -- ++(0,-0.55) -| (recover.east);
\draw[arr] (recover.west) -| node[lab,below,pos=0.28] {reserve activated} (serve.south);""",
    'Fig 3: route the return path cleanly instead of a long diagonal')

# --- Table VII still quotes dt = 1 s, contradicting Table VI ---------------
sub(r'Control interval & $\Delta t$ & 1 s \\',
    r'Control interval & $\Delta t$ & 0.2 s \\',
    'Table VII: dt 1 s -> 0.2 s (was contradicting Table VI)')

# --- episode length: keep 2000 s of mission now that dt is 0.2 s ----------
sub(r'Episode length & $T$ & 2000 steps \\',
    r'Episode length & $T$ & 10\,000 steps ($2000$ s) \\',
    'Table VI: T = 10,000 steps = 2000 s of simulated mission')

# --- state the charge-rate assumption explicitly --------------------------
sub(r'The charge increment is quoted per step and is therefore scaled with $\Delta t$, giving a full charge in 5000 steps and a charge-to-flight ratio near 1.4, comparable to a 1C pack.',
    r'The charge increment is quoted per step and is therefore scaled with $\Delta t$. The resulting charge time is shorter than a real constant-current pack of this capacity would require, because a real pack would not complete a full charge within a tractable episode; this is stated as a modelling assumption rather than a physical prediction, and it means the cost of charging contention in \eqref{tab:metrics} is a lower bound.',
    'state the charge-rate assumption honestly')

io.open(P, 'w', encoding='utf-8').write(s)
print(f'\napplied {n}/4')
