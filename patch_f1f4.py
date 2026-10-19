"""Fig 1 arrowhead gaps + drop redundant feedback; Fig 4 single chained path;
Fig 2 rebuilt as a 3D schematic."""
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

# ---- 3D library + ground colour ------------------------------------------
sub(r'\usetikzlibrary{positioning,arrows.meta,shapes.geometric,fit,calc,backgrounds,matrix}',
    '\\usetikzlibrary{positioning,arrows.meta,shapes.geometric,fit,calc,backgrounds,matrix,3d}',
    'load the 3d library')
sub(r'\definecolor{uavlight}{RGB}{241,245,249}',
    '\\definecolor{uavlight}{RGB}{241,245,249}\n'
    '\\definecolor{gndgray}{RGB}{234,238,243}',
    'ground-plane colour')

# ---- FIG 1 : shorten arrow tips, drop the redundant actor->env feedback ----
sub(r"""arr/.style={-{Latex[length=2mm]},semithick},
darr/.style={-{Latex[length=2mm]},semithick,dashed}
]
\node[box,fill=uavgray!8,draw=uavgray,text width=28mm] (sink) {Ground data sink\\/ base station};""",
r"""arr/.style={-{Latex[length=2mm]},semithick,shorten >=1.2pt,shorten <=1.2pt},
darr/.style={-{Latex[length=2mm]},semithick,dashed,shorten >=1.6pt,shorten <=1.6pt}
]
\node[box,fill=uavgray!8,draw=uavgray,text width=28mm] (sink) {Ground data sink\\/ base station};""",
    'Fig 1: shorten arrow tips so they clear the box borders')

sub(r"""\draw[darr] (env) -- (actor);
\draw[darr] (env) -- (critic);
\draw[darr] (critic.north) |- ++(0,8mm) -| (actor.south);
\draw[darr] (actor.south) |- ++(0,-6mm) -| (env.east);""",
r"""\draw[darr] (env) -- (actor);
\draw[darr] (env) -- (critic);
\coordinate (cfb) at ($(critic.north)+(0,7mm)$);
\coordinate (afb) at (cfb |- actor.north);
\draw[darr] (critic.north) -- (cfb) -- (afb) -- (actor.north);""",
    'Fig 1: single chained critic->actor feedback over the top; '
    'removed the duplicate actor->env arrow')

# ---- FIG 4 : collapse 3 draws into one path (was 3 stray arrowheads) -------
sub(r"""\coordinate (adr) at ($(actor.east)+(8mm,0)$);
\coordinate (ddr) at (adr |- deploy.east);
\draw[darr] (actor.east) -- (adr);
\draw[darr] (adr) -- (ddr);
\draw[darr] (ddr) -- (deploy.east);""",
r"""\coordinate (adr) at ($(actor.east)+(8mm,0)$);
\coordinate (ddr) at (adr |- deploy.east);
\draw[darr] (actor.east) -- (adr) -- (ddr) -- (deploy.east);""",
    'Fig 4: one chained path -> exactly one arrowhead')

io.open(P, 'w', encoding='utf-8').write(s)
print(f'\napplied {n}/5')
