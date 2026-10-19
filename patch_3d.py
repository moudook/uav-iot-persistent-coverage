"""Replace Fig 2 with a 3D schematic (oblique axonometric, UAVs at z_0)."""
import io, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
P = 'Mlawn-midsem-tex.tex'
s = io.open(P, encoding='utf-8').read()

OLD = r"""\resizebox{\columnwidth}{!}{%
\begin{tikzpicture}[
pt/.style={circle,draw=uavblue,fill=uavblue!12,minimum size=7mm,font=\scriptsize},
sn/.style={circle,draw=uavgreen,fill=uavgreen!10,minimum size=5mm},
link/.style={draw=uavcyan,semithick},
covlink/.style={draw=uavgreen!70!black,semithick,dashed},
lab/.style={font=\scriptsize,align=center}
]
\node[pt] (u1) at (0,0)    {$U_1$};
\node[pt] (u2) at (1.6,0)  {$U_2$};
\node[pt] (u3) at (3.2,0)  {$U_3$};
\node[pt] (u4) at (1.6,-1.7) {$U_4$};
\node[sn] (s1) at (-0.35,-1.3) {};
\node[sn] (s2) at (0.5,-0.95)  {};
\node[sn] (s3) at (2.95,-0.95) {};
\node[sn] (s4) at (0.5,-2.6)  {};
\node[sn] (s5) at (2.7,-2.6)  {};
\draw[link] (u1)--(u2)--(u3);
\draw[link] (u2)--(u4);
\draw[covlink] (u1)--(s1);
\draw[covlink] (u1)--(s2);
\draw[covlink] (u2)--(s2);
\draw[covlink] (u2)--(s3);
\draw[covlink] (u3)--(s3);
\draw[covlink] (u4)--(s4);
\draw[covlink] (u4)--(s5);
\node[lab,text width=46mm] at (1.5,-3.35) {Green dashed: sensor coverage.\\Cyan solid: inter-UAV communication.};
\end{tikzpicture}%
}"""

NEW = r"""% 3D schematic: oblique axonometric. UAVs fly at z_0 above the sensor plane.
% No \resizebox here: it would scale line widths and dash patterns too.
% The unit vectors below give the natural size (about 73 x 51 mm), which fits
% the 88.9 mm IEEE column width at true line widths and font sizes.
\begin{tikzpicture}[
pt/.style={circle,draw=uavblue,fill=uavblue!12,line width=0.5pt,
           minimum size=5.2mm,inner sep=0pt,font=\scriptsize},
sn/.style={circle,draw=uavgreen,fill=uavgreen!12,line width=0.45pt,
           minimum size=3.2mm,inner sep=0pt},
link/.style={draw=uavcyan,line width=0.7pt},
covlink/.style={draw=uavgreen!70!black,line width=0.55pt,
                dash pattern=on 2.2pt off 1.6pt},
drop/.style={draw=gray!65,line width=0.35pt,dash pattern=on 1pt off 1.2pt},
foot/.style={draw=uavgreen!55,line width=0.3pt,fill=uavgreen!5},
guide/.style={draw=gray!70,line width=0.25pt},
ann/.style={font=\tiny,align=center,fill=white,inner sep=0.8pt},
x={(1.15cm,0cm)}, y={(-0.55cm,0.78cm)}, z={(0cm,1.05cm)},
line cap=round, line join=round
]
% ---- ground plane (sensors live on it) ---------------------------------
\begin{scope}[canvas is xy plane at z=0]
  \path[fill=gndgray] (-0.5,-3.0) rectangle (3.5,1.85);
  \draw[step=0.6,gray!35,line width=0.25pt] (-0.5,-3.0) grid (3.5,1.85);
  \draw[gray!65,line width=0.5pt] (-0.5,-3.0) rectangle (3.5,1.85);
\end{scope}
% ---- horizontal coverage footprint, drawn on the ground -----------------
\begin{scope}[canvas is xy plane at z=0.015]
  \draw[foot] (1.6,0) circle[radius=1.78];
  \draw[foot] (1.6,0) -- (1.6,1.78);
  \node[ann] at (0.86,0.75) {$R_{\mathrm{cov}}$};
\end{scope}
% ---- drop lines and ground shadows (depth cue) --------------------------
\foreach \cx/\cy in {0/0,1.6/0,3.2/0,1.6/-1.7}{
  \draw[drop] (\cx,\cy,0) -- (\cx,\cy,1.6);
  \fill[gray!55] (\cx,\cy,0) circle[radius=0.7pt];
}
% ---- coverage links ------------------------------------------------------
\draw[covlink] (0,0,1.6)      -- (-0.35,-1.3,0);
\draw[covlink] (0,0,1.6)      -- (0.5,-0.95,0);
\draw[covlink] (1.6,0,1.6)    -- (0.5,-0.95,0);
\draw[covlink] (1.6,0,1.6)    -- (2.95,-0.95,0);
\draw[covlink] (3.2,0,1.6)    -- (2.95,-0.95,0);
\draw[covlink] (1.6,-1.7,1.6) -- (0.5,-2.6,0);
\draw[covlink] (1.6,-1.7,1.6) -- (2.7,-2.6,0);
% ---- sensors on the plane ------------------------------------------------
\foreach \cx/\cy in {-0.35/-1.3,0.5/-0.95,2.95/-0.95,0.5/-2.6,2.7/-2.6}
  \node[sn] at (\cx,\cy,0) {};
% ---- inter-UAV communication (all at equal altitude) ---------------------
\draw[link] (0,0,1.6) -- (1.6,0,1.6) -- (3.2,0,1.6);
\draw[link] (1.6,0,1.6) -- (1.6,-1.7,1.6);
\node[ann] at (2.62,1.46,1.6) {$R_{\mathrm{comm}}$};
% ---- UAVs (drawn last so they sit on top) -------------------------------
\node[pt] at (0,0,1.6)      {$U_1$};
\node[pt] at (1.6,0,1.6)    {$U_2$};
\node[pt] at (3.2,0,1.6)    {$U_3$};
\node[pt] at (1.6,-1.7,1.6) {$U_4$};
% ---- altitude dimension z_0 ---------------------------------------------
\draw[guide] (0,0,0)     -- (0,1.3,0);
\draw[guide] (0,0,1.6)   -- (0,1.3,1.6);
\draw[{Latex[length=1.4mm]}-{Latex[length=1.4mm]},line width=0.4pt]
      (0,1.3,0) -- (0,1.3,1.6) node[ann,midway,left=2pt] {$z_0$};
\end{tikzpicture}"""

if OLD not in s:
    print('!! OLD block not found')
    sys.exit(1)
s = s.replace(OLD, NEW, 1)

# caption now describes the 3D view
OLDCAP = r"\caption{Illustrative coupling between coverage and connectivity. Green dashed edges indicate coverage relationships, whereas cyan edges form the communication graph. Removing a topologically critical UAV can reduce both service redundancy and network connectivity.}"
NEWCAP = r"\caption{Coupling between coverage and connectivity in three dimensions. UAVs operate at a common nominal altitude $z_0$ above the fixed sensor plane; dashed vertical lines mark each UAV's ground projection. The shaded disc on the ground is the horizontal coverage footprint $R_{\mathrm{cov}}$, and cyan edges at altitude are inter-UAV communication links of range $R_{\mathrm{comm}}$. Removing a topologically critical UAV can reduce both service redundancy and network connectivity.}"
if OLDCAP in s:
    s = s.replace(OLDCAP, NEWCAP, 1)
    print('  ok  Fig 2 caption updated for the 3D view')

io.open(P, 'w', encoding='utf-8').write(s)
print('  ok  Fig 2 replaced with 3D schematic')
