"""Fig 1: route the critic->actor feedback above the tallest box.
Fig 2: anchor the R_comm label onto the U1-U2 link."""
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

# critic has 2 lines, env has 3 -> critic.north sits BELOW env.north, so a
# fixed +7mm offset still routed the horizontal segment through the env box.
# Reference env.north instead, which is the tallest box on that row.
sub(r"""\coordinate (cfb) at ($(critic.north)+(0,7mm)$);
\coordinate (afb) at (cfb |- actor.north);
\draw[darr] (critic.north) -- (cfb) -- (afb) -- (actor.north);""",
r"""\coordinate (cfb) at ($(env.north)+(0,5mm)$);
\draw[darr] (critic.north) -- (critic.north |- cfb)
      -- (actor.north |- cfb) -- (actor.north);""",
    'Fig 1: feedback routed above env.north (the tallest box), not critic.north')

# R_comm was floating unanchored above the scene
sub(r'\node[ann] at (2.62,1.46,1.6) {$R_{\mathrm{comm}}$};',
    r'\node[ann] at (0.8,-0.5,1.6) {$R_{\mathrm{comm}}$};',
    'Fig 2: R_comm label moved onto the U1-U2 comm link')

io.open(P, 'w', encoding='utf-8').write(s)
print(f'\napplied {n}/2')
