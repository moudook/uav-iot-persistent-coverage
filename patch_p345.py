"""Priority fixes 3, 4, 5."""
import io, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
P = 'Mlawn-midsem-tex.tex'
s = io.open(P, encoding='utf-8').read()
n = 0

def sub(old, new, why):
    global s, n
    if old not in s:
        print(f'  !! NOT FOUND: {why}')
        return False
    s = s.replace(old, new, 1)
    n += 1
    print(f'  ok  {why}')
    return True

NL = '\\\\'   # two literal backslashes in the .tex row terminator

print('=' * 70)
print('PRIORITY 3  --  make the reward reproducible')
print('=' * 70)

sub(r"""r_t=-\big(&\lambda_O U_t+\lambda_EE_t+\lambda_DD_t+\lambda_WW_t\\
&+\lambda_RR_t+\lambda_C\mathrm{Crit}_t\big).""",
r"""r_t=-\big(&\lambda_O U_t+\lambda_E E_t^{\mathrm{cons}}+
          \lambda_D D_t^{\mathrm{deg}}+\lambda_W W_t^{\mathrm{mov}}\\
&+\lambda_R R_t^{\mathrm{rec}}+\lambda_C\mathrm{Crit}_t\big).""",
    'Eq. (23) renamed: E_t,R_t collide; D_t,W_t undefined')

sub(r"""The weight $\lambda_O$ is chosen to dominate the secondary efficiency terms. Thus, the learned controller should not sacrifice persistent service merely to reduce energy consumption or flight distance. The individual objective components remain separate evaluation metrics rather than being hidden inside a single final score.""",
r"""Since the learner maximises expected return while the control objective of \eqref{eq:multiobjective} is a minimisation, the team reward of \eqref{eq:reward} is the negated weighted cost, and the two are equivalent up to sign. Table~\ref{tab:reward} defines each term and gives the initial weights used in this work. The weight $\lambda_O$ is chosen to dominate the secondary efficiency terms, so that the learned controller does not sacrifice persistent service merely to reduce energy consumption or flight distance. The individual objective components remain separate evaluation metrics rather than being hidden inside a single final score.

\begin{table}[t]
\caption{Team reward terms and their initial weights.}
\label{tab:reward}
\centering
\scriptsize
\renewcommand{\arraystretch}{1.06}
\begin{tabularx}{\columnwidth}{@{}L{1.55cm}L{3.10cm}Y@{}}
\toprule
Term & Definition & Weight \\
\midrule
$U_t$ & Under-coverage rate, \eqref{eq:Ut} & $\lambda_O = 1.00$ \\
$E_t^{\mathrm{cons}}$ & $(\sum_i [E_i(t)-E_i(t+1)]) / (N B^{\max})$ & $\lambda_E = 0.10$ \\
$D_t^{\mathrm{deg}}$ & $\mathbb 1[\text{any service requirement violated at } t]$ & $\lambda_D = 0.50$ \\
$W_t^{\mathrm{mov}}$ & distance flown divided by distance that changed coverage & $\lambda_W = 0.05$ \\
$R_t^{\mathrm{rec}}$ & normalized recovery delay over a recovery interval & $\lambda_R = 0.30$ \\
$\mathrm{Crit}_t$ & Articulation-point average, \eqref{eq:crit} & $\lambda_C = 0.20$ \\
\bottomrule
\end{tabularx}
\end{table}

All six quantities are dimensionless and lie in $[0,1]$, so the weights are directly comparable; $U_t$ and $\mathrm{Crit}_t$ are already normalized in \eqref{eq:Ut} and \eqref{eq:crit}. The values are initial settings to be tuned on a validation set; the ordering $\lambda_O \gg \lambda_D \ge \lambda_R > \lambda_C \ge \lambda_E \ge \lambda_W$ is the part on which the formulation depends.""",
    'reward definition table + sign-consistency sentence')

print()
print('=' * 70)
print('PRIORITY 4  --  remove the remaining symbol collisions')
print('=' * 70)

sub(r'a_i(t)=\mathbb 1\left[G_t-i\;\text{is disconnected}\right].',
    r'kappa_i(t)=\mathbb 1\left[G_t^{-i}\;\text{is disconnected}\right].',
    'Eq. (12) articulation indicator a_i -> kappa_i')
sub(r'\mathrm{Crit}_t=\frac{1}{|V_t^{\mathrm{act}}|}\sum_{i\in V_t^{\mathrm{act}}}a_i(t).',
    r'\mathrm{Crit}_t=\frac{1}{|V_t^{\mathrm{act}}|}\sum_{i\in V_t^{\mathrm{act}}}\kappa_i(t).',
    'Eq. (13) uses kappa_i')
sub(r'For analysis, the exact articulation-point indicator is',
    r'For analysis, the exact articulation-point indicator, where $G_t^{-i}$ denotes $G_t$ with vertex $i$ and its incident edges removed, is',
    'define G_t^{-i} in prose')
sub(r'where $\mathbf v_i$ is velocity, $b_i\in[0,1]$ is normalized battery level,',
    r'where $\mathcal{V}_t^{\mathrm{act}}=\{\,i\in\{1,\dots,N\}:F_i(t)=0\,\}$ is the set of active UAVs, from which any UAV with $F_i(t)=1$ is removed in all coverage, connectivity and energy sums. $\mathbf v_i$ is velocity, $b_i\in[0,1]$ is normalized battery level,',
    'define V_t^act formally after Eq. (3)')

print()
print('=' * 70)
print('PRIORITY 5  --  make Table IV physically self-consistent')
print('=' * 70)

sub('Control interval & $\\Delta t$ & 1 s ' + NL,
    'Control interval & $\\Delta t$ & 0.2 s ' + NL,
    'dt 1 s -> 0.2 s  (was 10 m/step against a 5 m threshold)')
sub('Communication power & $P_{\\mathrm{comm}}$ & 10 W ' + NL,
    'Avionics and comms power & $P_{\\mathrm{elec}}$ & 5 W ' + NL,
    'P_comm 10 W (40 dBm) -> P_elec 5 W')
sub('Coverage target & $K$ & 2 ' + NL,
    'Nominal altitude & $z_0$ & 50 m ' + NL + '\nCoverage target & $K$ & 2 ' + NL,
    'add altitude row (R_cov = 35 m needs z_0 near 50 m)')
sub('Charge increment & -- & 0.01 battery fraction/step ' + NL,
    'RF transmit power & $P_{\\mathrm{tx}}$ & 0.5 W ' + NL + '\n'
    'Charge increment & -- & 0.0002 battery fraction/step ' + NL + '\n'
    'Episode length & $T$ & 2000 steps ' + NL,
    'add RF TX + episode length rows, charge rescaled for dt')
sub('Within scope are spatial $K$-coverage,',
    'The control interval is chosen so that the relative displacement between two consecutive steps, $2 v_{\\max}\\Delta t = 2$ m, is smaller than the safety distance $d_{\\mathrm{safe}} = 5$ m; a coarser step would allow a closing pair to cross the separation constraint between two samples. The charge increment is quoted per step and is therefore scaled with $\\Delta t$, giving a full charge in 5000 steps and a charge-to-flight ratio near 1.4, comparable to a 1C pack. The nominal altitude is consistent with the coverage radius: a 74$\\degree$ downward sensor at 50 m yields a footprint half-width of 37 m. The two power entries are distinct: $P_{\\mathrm{elec}}$ is the total avionics and communications budget, whereas $P_{\\mathrm{tx}}$ is the radiated transmit power, which is bounded by the 1 W ceiling of IEEE 802.11 and is two orders of magnitude below the avionics budget.\n\nWithin scope are spatial $K$-coverage,',
    'parameter-consistency paragraph after Table IV')

io.open(P, 'w', encoding='utf-8').write(s)
print(f'\napplied {n}/12 edits')
