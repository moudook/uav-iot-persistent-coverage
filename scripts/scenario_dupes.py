import csv
from collections import defaultdict

rows = list(csv.DictReader(open('ml_impl/results_scenarios.csv', encoding='utf-8')))

print('=== exact duplicate config groups ===')
seen = defaultdict(list)
for i, r in enumerate(rows):
    key = (r['scenario'], r['config'])
    seen[key].append(i)
dups = {k: v for k, v in seen.items() if len(v) > 1}
if not dups:
    print('none')
for k, v in dups.items():
    print(k, '-> rows', v)

print()
print('=== per-row detail ===')
for r in rows:
    print(f"{r['scenario']} v{r['variant']:<2s} M={r['mappo_CK'][:5]} R={r['react_CK'][:5]} RL={r['reactlocal_CK'][:5]}  | {r['config']}")

print()
print('=== columns constant across all rows ===')
cols = rows[0].keys()
import math
for c in cols:
    vals = set(r[c] for r in rows)
    if len(vals) == 1 and c not in ('scenario', 'question'):
        print(c, '=', list(vals)[0])
