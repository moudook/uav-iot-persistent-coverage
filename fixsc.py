p='Mlawn-midsem-tex.tex'
s=open(p).read()
old = "SC(\\pi)=0\\quad\\text{for every policy }\\pi\n\\quad\\Longleftrightarrow\\quad\n\\mathcal{F}=\\varnothing,"
new = "\\mathcal{F}=\\varnothing \\quad\\Longrightarrow\\quad SC(\\pi)=0\\ \\text{for every policy }\\pi,"
assert old in s, "eq not found"
s = s.replace(old, new)
# fix the because sentence
old2 = "because $SC(\\pi)>0$ exactly when the trajectory visits $\\mathcal{F}$ at some\ninstant.  The statement is therefore about the best achievable value"
new2 = "because $SC(\\pi)>0$ requires the trajectory to visit $\\mathcal{F}$ at some\ninstant.  The converse does not hold: a poor policy on a feasible instance\nmay also score zero, so observing $SC(\\pi)=0$ does not prove infeasibility.\nThe statement is therefore about the best achievable value"
assert old2 in s, "because not found"
s = s.replace(old2, new2)
open(p,'w').write(s)
print('done')
