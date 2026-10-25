p = "ml_impl/uav_wireless/env.py"
s = open(p).read()
old = '    failure_enabled: bool = False\n    failure_time: int = -1        # -1 = disabled\n'
new = '    failure_enabled: bool = False\n    failure_time: int = -1        # -1 = disabled\n    credit_mode: str = "team"   # "team" or "c3"\n    credit_weight: float = 0.10\n'
assert old in s, "not found"
s = s.replace(old, new)
open(p, "w").write(s)
print("done")
