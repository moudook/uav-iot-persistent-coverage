p = "ml_impl/uav_wireless/train.py"
s = open(p).read()
old = '''    if bc_path:
        import torch, os
        if os.path.exists(bc_path):'''
new = '''    if bc_path:
        import os
        if os.path.exists(bc_path):'''
assert old in s, "not found"
s = s.replace(old, new)
open(p, "w").write(s)
print("done")
