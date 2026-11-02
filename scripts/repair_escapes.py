P = r"C:\Users\gbust\Downloads\Academic\Courses\Machine_learning_in_wireless_network\Project1\Mlawn-midsem-tex.tex"
s = open(P, encoding="utf-8").read()

# ---- R1: rebuild Local Observation lead-in + Eq(4) + para1 + para2 ----
start = s.index("At deployment, UAV $i$ uses only locally available information")
end = s.index("Unlike the idealized global articulation-point indicator", start)
new_block = r"""At deployment, UAV $i$ uses only locally available information:
\begin{equation}
\begin{split}
\mathbf o_i(t)=\bigl[&\mathbf p_i,\mathbf v_i,b_i,\mathcal N_i,C_i^{\mathrm{local}},\rho_i,\tau_i^{\mathrm{return}},\\
&E_i^{\mathrm{pad}},\{\hat{\mathbf u}_{i,j},d_{i,j}\}_{j=1}^{k},\mathbf r_i\bigr].
\end{split}
\label{eq:obs}
\end{equation}
Here $\mathcal N_i$ is the set of nearby UAVs, $C_i^{\mathrm{local}}$ is the number of nearby sensors currently covered, $\rho_i$ is a locally computed bridge-risk estimate, $\tau_i^{\mathrm{return}}$ is the estimated time until the return threshold is reached, and $E_i^{\mathrm{pad}}$ is the estimated energy needed to reach a feasible charging pad.  The final block is the ego-centric deficit summary: for the $k=3$ sensors nearest to $i$ whose coverage is below the required level ($n_d(t)<K$), the agent receives the unit bearing $\hat{\mathbf u}_{i,j}$ and the normalised distance $d_{i,j}$; $\mathbf r_i$ is a repulsion vector away from the centroid of the UAVs in communication range, which keeps a shared policy from collapsing all agents onto the same deficit.  Both are computable from local information under the communication model of Section~\ref{sec:radio}, so the observation is decentralised and has fixed size independent of $M$.

Three design alternatives to this observation were considered and measured.
A broadcast $G\times G$ deficit grid $\mathbf M_t^{\mathrm{def}}$ --- a cell
summary of the share of under-covered sensors --- was the original summary
term; it is not part of the evaluated configuration, and the value-of-
information row of Table~\ref{tab:knobs} prices exactly the information it
would have supplied: replacing the ego-centric summary by the exact
under-covered set costs $-0.090$, so the summary is neither free nor
decisive.  A one-hot agent identity is likewise not in the evaluated
observation; the ego terms depend on the agent's own position relative to the
deficit, so a parameter-shared network still receives agent-specific inputs.
The bearing to the charging pad is also not in the evaluated observation; the
return decision is driven by the energy features above.

"""
s = s[:start] + new_block + s[end:]

# ---- R2: remove the CONTRIB marker line ----
marker = "\nCONTRIB\n    \\item Corrected deployment parameters"
assert marker in s, "CONTRIB marker not found"
s = s.replace(marker, "\n    \\item Corrected deployment parameters", 1)
print("CONTRIB removed")

# ---- R3: shared-parameter sentence ----
old3 = r"""We therefore treat $\mathbf 1_i$ as part of the model rather than as an implementation detail, and Section~\ref{sec:results} reports the controlled comparison."""
new3 = r"""We therefore rely on the ego-centric terms of Eq.~\eqref{eq:obs}, which depend on the agent's own position relative to the deficit and so already identify agents; a one-hot identity is not needed and is not part of the evaluated configuration.  Section~\ref{sec:results} reports the value-of-information comparison that prices giving the policy the exact global coverage state instead."""
assert s.count(old3) == 1, "sentence not found"
s = s.replace(old3, new3, 1)
print("shared-parameter sentence updated")

# ---- R4: move the remeasured table into Section VIII (after results_corrected) ----
tstart = s.index("\\begin{table}[t]\n% the shared table style: analysis/theme_tables.tex")
tend = s.index("\\end{table}", tstart) + len("\\end{table}")
tbl = s[tstart:tend]

# remove from current location (keep a blank line where it was)
s = s[:tstart] + s[tend:]

# insert after the results_corrected label
anchor = "\\label{sec:results_corrected}"
assert anchor in s
pos = s.index(anchor) + len(anchor)
s = s[:pos] + "\n\n" + tbl + s[pos:]
print("remeasured table moved to Section VIII-A")

# ---- R5: teaser tweaks ----
T = r"C:\Users\gbust\Downloads\Academic\Courses\Machine_learning_in_wireless_network\Project1\ml_impl\analysis\fig_teaser.tex"
t = open(T, encoding="utf-8").read()
old5 = "\\node[anchor=east, font=\\tiny] at (3.96,1.28) {0.952};"
new5 = "\\node[anchor=east, font=\\tiny, fill=white, inner sep=0.8pt] at (3.96,1.28) {0.952};"
assert t.count(old5) == 1, "teaser 0.952 node not found"
t = t.replace(old5, new5, 1)
old6 = "\\node[anchor=south west, font=\\tiny] at (axis cs:3.43,2.99) {the two criteria disagree};"
new6 = "\\node[anchor=south west, font=\\tiny] at (axis cs:3.43,2.93) {the two criteria disagree};"
assert t.count(old6) == 1, "teaser criteria label not found"
t = t.replace(old6, new6, 1)
open(T, "w", encoding="utf-8").write(t)
print("teaser tweaked")

open(P, "w", encoding="utf-8").write(s)
print("ALL REPAIRS DONE")
