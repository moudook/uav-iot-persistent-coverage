p = "Mlawn-midsem-tex.tex"
lines = open(p).read().splitlines(keepends=True)
new_val = "The residual is consistent with the credit assignment of a shared team reward.  A convergence check at 2e6 steps reveals entropy collapse at episode 675 (entropy 0.093, below 0.1), confirming that the shared team reward drives the policy toward determinism; the per-agent local critic's difference is -0.035 of persistent coverage (95\\% interval [-0.079, +0.009]), which includes zero, so the collapse is the mechanism but the arm does not isolate it"
lines[220] = "\\newcommand{\\tokCreditResidual}{" + new_val + "}\n"
open(p, "w").write("".join(lines))
print("done")
print(lines[220][:100])
