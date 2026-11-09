p = r"C:\Users\gbust\Downloads\Academic\Courses\Machine_learning_in_wireless_network\Project1\docs\MEASURED_NUMBERS.md"
s = open(p, encoding="utf-8").read()
ins = '''## KNOB ABLATION (3 seeds, 200 ep, frozen eval, 20 held-out scenes)

| config | CK | sd | n | vs anchor |
|---|---|---|---|---|
| anchor (ego+shape) | 0.9522 | 0.0105 | 5 | -- |
| without W_t penalty | 0.9399 | 0.0070 | 3 | -0.0123 |
| diff credit beta=2 | 0.9592 | 0.0011 | 3 | +0.0070 |
| full coverage state (no ego) | 0.8625 | 0.0205 | 3 | -0.0897 |

READ: (i) W_t penalty is NOT the bottleneck (no effect); (ii) ego obs is
SUFFICIENT - full global state is worse (-0.090, resolved), i.e. more
information hurts at this budget; (iii) difference credit is a small
positive (+0.007), not resolved.

## BUDGET SWEEP (3 seeds, frozen eval, 20 held-out scenes)

| episodes | CK | sd | n |
|---|---|---|---|
| 25 | 0.8304 | 0.0074 | 3 |
| 50 | 0.8684 | 0.0106 | 3 |
| 100 | 0.9332 | 0.0087 | 3 |
| 200 | 0.9475 | 0.0026 | 3 |

Budget clearly matters: +0.1171 over the 25->200 range, monotonic, sd small.
This RETRACTS the old claim "budget is excluded as the explanation".

'''
s = s.replace('## FINAL VERDICT (2026-11-02)', ins + '## FINAL VERDICT (2026-11-02)', 1)
open(p, 'w', encoding="utf-8").write(s)
print('done')
'''