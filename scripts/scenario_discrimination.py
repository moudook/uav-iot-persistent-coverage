import csv
from collections import defaultdict

rows = list(csv.DictReader(open('ml_impl/results_scenarios.csv', encoding='utf-8')))
by = defaultdict(list)
for r in rows:
    by[r['scenario']].append(r)

print('scen variants  M CK range        R CK range        RL CK range       M-RL    configs')
for sid in sorted(by):
    rs = by[sid]
    def rng(k):
        v = [float(r[k]) for r in rs]
        return min(v), max(v)
    m, rr, rl = rng('mappo_CK'), rng('react_CK'), rng('reactlocal_CK')
    mmean = sum(float(x['mappo_CK']) for x in rs) / len(rs)
    rlmean = sum(float(x['reactlocal_CK']) for x in rs) / len(rs)
    cfgs = ' | '.join(x['config'].replace('N=8 ', '').replace('Rcov=35 Rcomm=40 ', '') for x in rs)
    print(f'{sid:4s} {len(rs):<8d} {m[0]:.3f}-{m[1]:.3f}      {rr[0]:.3f}-{rr[1]:.3f}      {rl[0]:.3f}-{rl[1]:.3f}      {mmean - rlmean:+.3f}  {cfgs[:110]}')
