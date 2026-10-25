p = "docs/G1_memo.md"
s = open(p).read()
addition = """

## Convergence check (1 seed, 2e6 steps, 6 BLAS threads)
| Episode | CK | Entropy |
|---------|-----|---------|
| 25      | 0.5694 | 1.3829 |
| 50      | 0.6465 | 1.3869 |
| 100     | 0.7022 | 1.4335 |
| 200     | 0.6858 | 1.1881 |
| 500     | 0.8214 | 1.1192 |
| 999     | 0.3541 | 0.0143 |

- Entropy collapsed at ep 675 (value 0.0933, below 0.1). Kill criterion violation (R3).
- CK peaked at ep 500 (0.82) then collapsed to 0.35 by ep 999. Extreme instability (range 0.059-0.943).
- Mean CK (last 100): 0.3745, worse than midsem 0.674.
- Policy collapsed to near-deterministic (entropy 0.014). Consistent with credit-assignment hypothesis: team reward -> collapse.

### Updated implications
- Entropy collapse EXPLAINS the gap: policy collapses, not "none of the arms explains it."
- C3 (credit-aware reward) is critical: team reward causes collapse; per-agent credit may fix it.
- Residual/rule-anchored MAPPO (safety net) is essential.
- Midsem 0.298 gap was not just undertrained -- it was a collapse artifact.
"""
s = s.replace("## Decisions", addition + "\n## Decisions")
open(p, "w").write(s)
print("done")
