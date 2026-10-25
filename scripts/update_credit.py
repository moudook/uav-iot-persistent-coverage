p = "Mlawn-midsem-tex.tex"
s = open(p).read()
old = '\\newcommand{\\tokCreditResidual}{The residual is consistent with the credit assignment of a \nshared team reward, and the cheapest test of that diagnosis does not resolve it: the per-agent local critic\'s \ndifference is -0.035 of persistent coverage (95\\% interval [-0.079, +0.009]), which includes zero}'
# Try simpler: just replace the macro value
import re
# Find the tokCreditResidual line
for i, line in enumerate(s.splitlines()):
    if 'tokCreditResidual}' in line and 'newcommand' in line:
        print("FOUND at line", i+1)
        print(repr(line[:80]))
        break
---
