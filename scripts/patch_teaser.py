P = r"C:\Users\gbust\Downloads\Academic\Courses\Machine_learning_in_wireless_network\Project1\ml_impl\analysis\fig_teaser.tex"
s = open(P, encoding="utf-8").read()

# 1) actor/arrow block: add obs + action nodes, retarget arrows
old = r"""  \node[box, fill=uavblue!9, draw=uavblue, minimum width=1.55cm, minimum height=0.40cm, inner sep=1pt] (actor) at (2.00,3.30) {shared actor $\pi_\theta$};
  \draw[arr] (actor.east) -- (3.45,3.30);
  \node[align=center, font=\tiny, text=uavred] (hardlbl) at (3.50,2.34) {connectivity mask\\reserve UAV\\charging\\\emph{not learned}};
  \draw[arr] (hardlbl.north) -- (3.45,3.10);"""
new = r"""  \node[box, fill=uavblue!9, draw=uavblue, minimum width=1.30cm, minimum height=0.40cm, inner sep=1pt] (obs) at (0.55,3.30) {obs.\ $o_i$};
  \node[box, fill=uavblue!9, draw=uavblue, minimum width=1.55cm, minimum height=0.40cm, inner sep=1pt] (actor) at (2.00,3.30) {shared actor $\pi_\theta$};
  \node[box, fill=uavblue!9, draw=uavblue, minimum width=1.30cm, minimum height=0.40cm, inner sep=1pt] (act) at (3.60,3.30) {action $a_i$};
  \draw[arr] (obs.east) -- (actor.west);
  \draw[arr] (actor.east) -- (act.west);
  \node[box, fill=uavpurple!8, draw=uavpurple, minimum width=1.50cm, minimum height=0.40cm, inner sep=1pt] (critic) at (0.55,2.25) {critic $V_\phi(s_t)$};
  \draw[darr] (critic.north) -- (actor.south west);
  \node[align=center, font=\tiny, text=uavred] (hardlbl) at (3.60,2.34) {connectivity mask\\reserve UAV\\charging\\\emph{not learned}};
  \draw[arr] (hardlbl.north) -- (actor.south east);"""
assert s.count(old) == 1, "actor block not found"
s = s.replace(old, new, 1)

# 2) 0.952 inside bar end; 1.000 kept right of the ceiling line
old2 = r"""  \node[anchor=west, font=\tiny] at (4.13,1.27) {0.952};
  \filldraw[fill=gray!55, draw=gray!70, line width=0.4pt] (0.05,0.40) rectangle (3.93,0.54);
  \node[anchor=north west, font=\tiny] at (0.05,0.36) {unprivileged reactive rule};
  \node[anchor=north, font=\tiny] at (3.93,0.38) {0.923};
  \draw[uavgreen, line width=0.9pt, <->] (3.93,0.90) -- (4.05,0.90);
  \node[anchor=north, font=\tiny, text=uavgreen, yshift=-1pt] at (3.99,0.88) {learner minus rule +0.029};
  \draw[black, dashed, line width=1.0pt] (4.25,0.22) -- (4.25,1.16);
  \node[anchor=west, font=\tiny] at (4.29,1.16) {1.000};"""
new2 = r"""  \node[anchor=east, font=\tiny] at (3.96,1.28) {0.952};
  \filldraw[fill=gray!55, draw=gray!70, line width=0.4pt] (0.05,0.40) rectangle (3.93,0.54);
  \node[anchor=north west, font=\tiny] at (0.05,0.36) {unprivileged reactive rule};
  \node[anchor=north, font=\tiny] at (3.93,0.38) {0.923};
  \draw[uavgreen, line width=0.9pt, <->] (3.93,0.90) -- (4.05,0.90);
  \node[anchor=north, font=\tiny, text=uavgreen, yshift=-1pt] at (3.99,0.88) {learner minus rule +0.029};
  \draw[black, dashed, line width=1.0pt] (4.25,0.22) -- (4.25,1.16);
  \node[anchor=west, font=\tiny] at (4.32,1.16) {1.000};"""
assert s.count(old2) == 1, "label block not found"
s = s.replace(old2, new2, 1)

open(P, "w", encoding="utf-8").write(s)
print("fig_teaser patched")
