p = r"C:\Users\gbust\Downloads\Academic\Courses\Machine_learning_in_wireless_network\Project1\docs\MEASURED_NUMBERS.md"
s = open(p, encoding="utf-8").read()

ins = (
"## INNOVATION RESULTS (2026-11-02)\n\n"
"| innovation | config | regime | CK | vs anchor | vs rule |\n"
"|---|---|---|---|---|---|\n"
"| anchor (ego+shape) | base | nominal | 0.9522 | -- | +0.029 (resolved) |\n"
"| anchor (ego+shape) | base | small_battery | 0.7646 | -- | -0.064 |\n"
"| Innov 1+2+4 (curriculum+energy+R&F) | +curriculum+energy+R&F | small_battery | 0.8309 | +0.066 | +0.002 (tied) |\n"
"| Innov 6 (graph attention) | +attn | small_battery | 0.7530 | -0.012 | -0.076 |\n"
"| Innov 5 (diff credit beta=2) | diff2 | nominal | 0.9592 | +0.007 | +0.036 |\n"
"| no_w (W_t removed) | no_w | nominal | 0.9399 | -0.012 | +0.017 |\n"
"| full_obs (global state) | full_obs | nominal | 0.8625 | -0.090 | -0.060 |\n"
"| Innov 1+2+4+5 (combined) | combined | small_battery | 0.8164 | +0.051 | -0.013 |\n"
"| Innov 7 (intrinsic) | +intrinsic | small_battery | 0.8343 | +0.069 | +0.005 (tied) |\n\n"
"KEY FINDINGS:\n"
"1. Ego-centric observation is the main driver (+0.093 on nominal).\n"
"2. Full global state HURTS (-0.090) - more information is worse.\n"
"3. Attention HURTS (-0.078) - the MLP is better than attention here.\n"
"4. Curriculum helps on small_battery (+0.066) but doesn't close gap.\n"
"5. W_t penalty is NOT the bottleneck (no effect).\n"
"6. Difference credit is a small positive on nominal (+0.007) but HURTS on small_battery (-0.015).\n"
"7. Intrinsic motivation has no effect (+0.003).\n"
"8. The paper's thesis: 'the ego observation is sufficient and necessary;\n"
"   the remaining gap on energy regimes is a genuine limitation.'\n\n"
)

s = s.replace("## FINAL VERDICT (2026-11-02)", ins + "## FINAL VERDICT (2026-11-02)", 1)
open(p, "w", encoding="utf-8").write(s)
print("done")
"