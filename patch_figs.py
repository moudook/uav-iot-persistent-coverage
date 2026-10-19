"""Fix TikZ overlap in Fig. 2, Fig. 3, Fig. 5."""
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

# ---------------------------------------------------------------- FIG 2
# cause: a text width=36mm node placed 1mm above u2 overlaps the UAV row
# fix:   delete the floating note, merge it into the legend at the bottom
sub(r"""\node[lab,below=1mm of s5,text width=44mm] {Green dashed lines: sensor coverage\\Cyan lines: inter-UAV communication};
\node[lab,above=1mm of u2,text width=36mm] {A UAV may simultaneously contribute to\\coverage redundancy and connectivity.};""",
r"""\node[lab,below=2.5mm of s5,text width=52mm] {Green dashed: sensor coverage. Cyan solid: inter-UAV\\
communication. A single UAV contributes to coverage redundancy and to\\
network connectivity at the same time, so removing a topologically\\
critical UAV can reduce both.};""",
    'Fig 2: remove overlapping note above u2, merge into bottom legend')

# ---------------------------------------------------------------- FIG 3
# cause 1: 11mm gaps are narrower than the arrow labels, so labels sit on the boxes
# cause 2: node[lab,right] on a |- path places the label outside the column
# fix: explicit coordinates, wider gaps, labels only on straight segments
sub(r"""\begin{tikzpicture}[
state/.style={draw,rounded corners=2pt,minimum width=23mm,minimum height=8mm,align=center,font=\scriptsize},
arr/.style={-{Latex[length=2mm]},semithick},
lab/.style={font=\scriptsize,fill=white,inner sep=1pt}
]
\node[state,fill=uavgreen!10,draw=uavgreen] (serve) {Serve / hover};
\node[state,right=11mm of serve,fill=uavblue!10,draw=uavblue] (transit) {Transit};
\node[state,right=11mm of transit,fill=uavorange!10,draw=uavorange] (charge) {Charge};
\node[state,below=11mm of transit,fill=uavred!8,draw=uavred] (recover) {Recover / reconfigure};
\draw[arr] (serve)--node[lab,above] {$E_i>E_i^{\mathrm{req}}$}(transit);
\draw[arr] (transit)--node[lab,above] {pad reached}(charge);
\draw[arr] (charge) |- node[lab,right] {battery restored}(serve);
\draw[arr] (transit)--node[lab,left] {failure detected}(recover);
\draw[arr] (charge) |- node[lab,right] {failure detected}(recover);
\draw[arr] (recover) -| node[lab,below] {reserve activated}(serve);
\end{tikzpicture}%""",
r"""\begin{tikzpicture}[
state/.style={draw,rounded corners=2pt,minimum width=25mm,minimum height=9mm,align=center,font=\scriptsize},
arr/.style={-{Latex[length=2mm]},semithick},
lab/.style={font=\scriptsize,fill=white,inner sep=1.5pt}
]
\node[state,fill=uavgreen!10,draw=uavgreen]  (serve)   at (0,0)     {Serve / hover};
\node[state,fill=uavblue!10,draw=uavblue]    (transit) at (4.0,0)   {Transit};
\node[state,fill=uavorange!10,draw=uavorange] (charge) at (8.0,0)   {Charge};
\node[state,fill=uavred!8,draw=uavred]       (recover) at (4.0,-2.8) {Recover / reconfigure};
\draw[arr] (serve)  -- node[lab,above] {$E_i>E_i^{\mathrm{req}}$} (transit);
\draw[arr] (transit) -- node[lab,above] {pad reached} (charge);
\draw[arr] (charge.east) -- ++(0.9,0) -- ++(0,-1.9)
      -- node[lab,above,pos=0.5] {battery restored} (serve.south |- charge.south);
\draw[arr] (transit.south) -- node[lab,right,pos=0.45] {failure detected} (recover.north);
\draw[arr] (charge.south) -- ++(0,-0.9) -| (recover.east);
\draw[arr] (recover.west) -| node[lab,below,pos=0.28] {reserve activated} (serve.south);
\end{tikzpicture}%""",
    'Fig 3: wider gaps, labels only on straight segments, no right-side bleed')

# ---------------------------------------------------------------- FIG 5
# cause: arrows connect node centres, so node[lab,above] lands mid-box on the text
# fix:   anchor the arrows at the top edges so labels sit in free space
sub(r"""\begin{tikzpicture}[
phase/.style={draw,rounded corners=3pt,align=left,text width=30mm,minimum height=20mm,font=\scriptsize,inner sep=4pt},
arr/.style={-{Latex[length=2mm]},semithick},
lab/.style={font=\scriptsize,fill=white,inner sep=1pt}
]
\node[phase,fill=uavgreen!10,draw=uavgreen] (p1) {\textbf{Phase 1 -- Python}\\Geometric movement, $K$-coverage, connectivity, battery, charging, failure/recovery, heuristic controller, MAPPO};
\node[phase,fill=uavblue!10,draw=uavblue,right=6mm of p1] (p2) {\textbf{Phase 2 -- OMNeT++ + INET}\\Wireless communication, mobility interaction, network-level metrics};
\node[phase,fill=uavpurple!10,draw=uavpurple,right=6mm of p2] (p3) {\textbf{Phase 3 -- Simu5G}\\PHY-aware communication and final integration};
\draw[arr] (p1)--node[lab,above]{validate control}(p2);
\draw[arr] (p2)--node[lab,above]{add network realism}(p3);
\end{tikzpicture}%""",
r"""\begin{tikzpicture}[
phase/.style={draw,rounded corners=3pt,align=left,text width=32mm,minimum height=24mm,font=\scriptsize,inner sep=4pt},
arr/.style={-{Latex[length=2mm]},semithick},
lab/.style={font=\scriptsize,fill=white,inner sep=1.5pt}
]
\node[phase,fill=uavgreen!10,draw=uavgreen] (p1) {\textbf{Phase 1 -- Python}\\Geometric movement, $K$-coverage, connectivity, battery, charging, failure/recovery, heuristic controller, MAPPO};
\node[phase,fill=uavblue!10,draw=uavblue,right=9mm of p1] (p2) {\textbf{Phase 2 -- OMNeT++ + INET}\\Wireless communication, mobility interaction, network-level metrics};
\node[phase,fill=uavpurple!10,draw=uavpurple,right=9mm of p2] (p3) {\textbf{Phase 3 -- Simu5G}\\PHY-aware communication and final integration};
\draw[arr] (p1.north east) -- node[lab,above] {validate control} (p2.north west);
\draw[arr] (p2.north east) -- node[lab,above] {add network realism} (p3.north west);
\end{tikzpicture}%""",
    'Fig 5: arrows anchored at top edges so labels clear the box text')

io.open(P, 'w', encoding='utf-8').write(s)
print(f'\napplied {n}/3 figure patches')
