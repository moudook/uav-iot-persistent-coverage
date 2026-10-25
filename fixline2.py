p='Mlawn-midsem-tex.tex'
lines=open(p).read().splitlines(keepends=True)
for i,l in enumerate(lines):
    if 'actor.west' in l:
        lines[i]='\\draw[arr] (actor.west) -- node[above,font=\\scriptsize] {$a_i(t)$} (env.east);\n'
        print('fixed line', i+1)
open(p,'w').write(''.join(lines))
