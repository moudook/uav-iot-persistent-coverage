import io, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
P = 'Mlawn-midsem-tex.tex'
s = io.open(P, encoding='utf-8').read()
n = 0
def sub(old, new, why):
    global s, n
    if old not in s:
        print(f'  !! NOT FOUND: {why}'); return
    s = s.replace(old, new, 1); n += 1
    print(f'  ok  {why}')

# 1. \degree is from gensymb, which is not loaded -> use ^\circ
sub(r'a 74$\degree$ downward sensor at 50 m yields a footprint half-width of 37 m',
    r'a $74^\circ$ downward sensor at 50 m yields a footprint half-width of 37 m',
    r'\degree -> ^\circ')

# 2. reward table too wide: narrow the definition column, shorten entries,
#    and use a safe indicator glyph
sub(r'\begin{tabularx}{\columnwidth}{@{}L{1.55cm}L{3.10cm}Y@{}}',
    r'\begin{tabularx}{\columnwidth}{@{}L{1.45cm}L{2.95cm}Y@{}}',
    'reward table: narrow definition column')
sub(r'$E_t^{\mathrm{cons}}$ & $(\sum_i [E_i(t)-E_i(t+1)]) / (N B^{\max})$ & $\lambda_E = 0.10$ \\',
    r'$E_t^{\mathrm{cons}}$ & $\sum_i\Delta E_i(t)\,/\,(N B^{\max})$ & $\lambda_E = 0.10$ \\',
    'E_t^cons: shorten formula')
sub(r'$D_t^{\mathrm{deg}}$ & $\mathbb 1[\text{any service requirement violated at } t]$ & $\lambda_D = 0.50$ \\',
    r'$D_t^{\mathrm{deg}}$ & 1 if any service requirement is violated & $\lambda_D = 0.50$ \\',
    'D_t^deg: drop \mathbb 1, shorten')
sub(r'$W_t^{\mathrm{mov}}$ & distance flown divided by distance that changed coverage & $\lambda_W = 0.05$ \\',
    r'$W_t^{\mathrm{mov}}$ & distance flown $/$ distance that changed coverage & $\lambda_W = 0.05$ \\',
    'W_t^mov: shorten')
sub(r'$R_t^{\mathrm{rec}}$ & normalized recovery delay over a recovery interval & $\lambda_R = 0.30$ \\',
    r'$R_t^{\mathrm{rec}}$ & normalized recovery delay during recovery & $\lambda_R = 0.30$ \\',
    'R_t^rec: shorten')
sub(r'Term & Definition & Weight \\',
    r'Term & Definition & Weight \\'.replace('Weight', r'Weight'),
    'keep header')

io.open(P, 'w', encoding='utf-8').write(s)
print(f'\napplied {n} edits')
