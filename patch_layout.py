"""Layout patch: fix column justification, Table I balance, two overflowing equations."""
import io, sys, re
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

P = 'Mlawn-midsem-tex.tex'
s = io.open(P, encoding='utf-8').read()
orig = s
n = 0

def sub(old, new, why):
    global s, n
    if old not in s:
        print(f'  !! NOT FOUND: {why}')
        print(f'     {old[:80]}')
        return False
    s = s.replace(old, new, 1)
    n += 1
    print(f'  ok  {why}')
    return True

print('F1  add ragged-right fixed-width column type')
sub(r'\newcolumntype{Y}{>{\raggedright\arraybackslash}X}',
    '\\newcolumntype{Y}{>{\\raggedright\\arraybackslash}X}\n'
    '\\newcolumntype{L}[1]{>{\\raggedright\\arraybackslash}p{#1}}',
    'define L{...} = ragged-right p-column')

print('F2  convert p{} -> L{} in all 7 tabularx specs, rebalance Table I')
sub(r'\begin{tabularx}{\textwidth}{@{}p{0.45cm}p{2.45cm}p{2.25cm}Y p{2.55cm}Y@{}}',
    '\\begin{tabularx}{\\textwidth}{@{}L{0.5cm}L{2.5cm}L{1.9cm}L{4.6cm}L{4.0cm}Y@{}}',
    'Table I: ragged + rebalanced (Limitation 2.55cm -> 4.0cm)')
sub(r'\begin{tabularx}{\columnwidth}{@{}p{1.3cm}p{1.7cm}Y@{}}',
    '\\begin{tabularx}{\\columnwidth}{@{}L{1.3cm}L{1.7cm}Y@{}}',
    'Table II: ragged')
sub(r'\begin{tabularx}{\columnwidth}{@{}p{1.35cm}Y@{}}',
    '\\begin{tabularx}{\\columnwidth}{@{}L{1.35cm}Y@{}}',
    'Table III: ragged')
sub(r'\begin{tabularx}{\columnwidth}{@{}p{1.38cm}p{2.05cm}Y@{}}',
    '\\begin{tabularx}{\\columnwidth}{@{}L{1.38cm}L{2.05cm}Y@{}}',
    'Table VIII: ragged')
sub(r'\begin{tabularx}{\columnwidth}{@{}p{1.55cm}p{1.20cm}Y@{}}',
    '\\begin{tabularx}{\\columnwidth}{@{}L{1.55cm}L{1.20cm}Y@{}}',
    'Table VI: ragged')
sub(r'\begin{tabularx}{\columnwidth}{@{}p{0.65cm}p{1.75cm}Y@{}}',
    '\\begin{tabularx}{\\columnwidth}{@{}L{0.65cm}L{1.75cm}Y@{}}',
    'Table IX: ragged')

print('F3  split Eq. (15) -- was 49.3pt too wide')
sub(r"""\begin{equation}
P_i(t)=P_{\mathrm{hover}}\mathbb 1[a_i=\mathrm{Hover}] + P_{\mathrm{move}}\mathbb 1[a_i\in\{+x,-x,+y,-y\}] + P_{\mathrm{comm}}.
\label{eq:power}""",
    r"""\begin{equation}
\begin{split}
P_i(t)={}&P_{\mathrm{hover}}\,\mathbb 1[a_i=\mathrm{Hover}]\\
&+P_{\mathrm{move}}\,\mathbb 1[a_i\in\{+x,-x,+y,-y\}]+P_{\mathrm{comm}}.
\end{split}
\label{eq:power}""",
    'Eq. (15) split across two lines')

print('F4  split Eq. (19) -- was 10.8pt too wide')
sub(r"""\begin{equation}
\|\mathbf v_i(t)\|\le v_{\max},\quad \mathbf p_i(t)\in\Omega,
\quad \|\mathbf p_i(t)-\mathbf p_j(t)\|\ge d_{\mathrm{safe}},\ \forall i\ne j.
\label{eq:safety}""",
    r"""\begin{equation}
\begin{split}
&\|\mathbf v_i(t)\|\le v_{\max},\qquad \mathbf p_i(t)\in\Omega,\\
&\|\mathbf p_i(t)-\mathbf p_j(t)\|\ge d_{\mathrm{safe}},\ \forall i\ne j.
\end{split}
\label{eq:safety}""",
    'Eq. (19) split across two lines')

io.open(P, 'w', encoding='utf-8').write(s)
print(f'\napplied {n}/9 edits; file {len(orig)} -> {len(s)} bytes')
