# build_bundle.py  --  markdown -> latex fragments -> RESEARCH_BUNDLE.pdf
import pypandoc, glob, io, re, os, subprocess, sys

FILES = ['00_INDEX', '10_REPORT_BACKBONE', '00_MATH_AUDIT',
         '01_PROBLEM_FORMULATION', '02_FEASIBILITY_AND_PARAMETERS',
         '09_REFERENCES_VERIFIED', '04_MARL_THEORY',
         '05_07_THEORY_COVERAGE_GRAPH_ENERGY', '03_WIRELESS_MODELS',
         '08_SIMULATION_STACK']

REPL = {
    '\u5e84': '', '\u2705': '[OK]', '\u274c': '[X]', '\u2b50': '',
    '\u26a0': '[!]', '\u2713': r'$\checkmark$', '\u2714': r'$\checkmark$',
    '\u2717': r'$\times$', '\u2718': r'$\times$', '\u2248': r'$\approx$',
    '\u2260': r'$\neq$', '\u2264': r'$\leq$', '\u2265': r'$\geq$',
    '\u2192': r'$\rightarrow$', '\u2190': r'$\leftarrow$',
    '\u21d2': r'$\Rightarrow$', '\u21d4': r'$\Leftrightarrow$',
    '\u00a0': ' ', '\u2018': "`", '\u2019': "'", '\u201c': '``',
    '\u201d': "''", '\u2013': '--', '\u2014': '---', '\u2026': r'\ldots{}',
    '\u00b1': r'$\pm$', '\u00d7': r'$\times$', '\u00b0': r'$^\circ$',
    '\u03a3': r'$\Sigma$', '\u03c3': r'$\sigma$', '\u03b5': r'$\varepsilon$',
    '\u03bb': r'$\lambda$', '\u03c0': r'$\pi$', '\u03bc': r'$\mu$',
    '\u2208': r'$\in$', '\u2209': r'$\notin$', '\u2200': r'$\forall$',
    '\u2203': r'$\exists$', '\u2229': r'$\cap$', '\u222a': r'$\cup$',
    '\u2211': r'$\sum$', '\u220f': r'$\prod$', '\u2261': r'$\equiv$',
    '\u2245': r'$\cong$', '\u221a': r'$\sqrt{}$', '\u00b7': r'$\cdot$',
    '\u210f': r'$\hbar$', '\u00bd': r'$\frac12$', '\u2153': '3/4',
    '\u2154': '1/4', '\u2044': '/', '\u2212': '-', '\u25cf': '*',
    '\u25cb': 'o', '\u00ac': 'EUR', '\u20ac': 'EUR', '\u266a': '',
    '\ufeff': '',
}

def convert(f):
    out = f'src_{f}.tex'
    pypandoc.convert_file(f'{f}.md', 'latex', outputfile=out,
                          extra_args=['--from=markdown+pipe_tables+tex_math_dollars',
                                       '--to=latex', '--wrap=none'])
    return out

def clean(path):
    s = io.open(path, encoding='utf-8').read()
    s = s.replace(r'\begin{Shaded}', '').replace(r'\end{Shaded}', '')
    s = re.sub(r'\\begin\{Highlighting\}\[[^\]]*\]', '', s)
    s = re.sub(r'\\end\{Highlighting\}', '', s)
    s = re.sub(r'^\s*%?\s*\[syntax-highlighting\].*$', '', s, flags=re.M)
    s = s.replace(r'\begin{none}', r'\begin{longtable}')
    s = s.replace(r'\end{none}',   r'\end{longtable}')
    for k, v in REPL.items():
        s = s.replace(k, v)
    s = s.encode('ascii', 'ignore').decode('ascii')
    s = re.sub(r'\n{4,}', '\n\n\n', s)
    io.open(path, 'w', encoding='utf-8').write(s)
    return len(s)

print('converting...')
for f in FILES:
    p = convert(f)
    n = clean(p)
    print(f'  {p:46} {n/1024:8.1f} KB')

if os.path.exists('RESEARCH_BUNDLE.pdf'):
    os.remove('RESEARCH_BUNDLE.pdf')

pdflatex = (r'C:\Users\gbust\AppData\Local\Programs\MiKTeX\miktex\bin\x64\pdflatex.exe')
print('compiling (3 passes)...')
for i in range(3):
    r = subprocess.run([pdflatex, '-interaction=nonstopmode', 'bundle.tex'],
                       capture_output=True, text=True)
    m = re.search(r'Output written.*', r.stdout)
    if m:
        print('  pass', i + 1, ':', m.group(0)[:90])

errs = []
if os.path.exists('bundle.log'):
    for line in io.open('bundle.log', encoding='utf-8', errors='ignore'):
        if line.startswith('! '):
            errs.append(line.strip())
seen, uniq = set(), []
for e in errs:
    if e not in seen:
        seen.add(e); uniq.append(e)
print(f'remaining errors: {len(uniq)}')
for e in uniq[:10]:
    print('   ', e)
