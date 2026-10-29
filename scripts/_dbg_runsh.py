import sys
sys.path.insert(0, r"C:\Users\gbust\Downloads\Academic\Courses\Machine_learning_in_wireless_network\Project1\scripts")
import inet_probe as ip
p = ip.write_ini("UavPair", {"simTrace": '"traces/_selftest.movements"'}, 2.0)
print("ini_path:", p)
print("wsl:", ip.ini_path_wsl(p))
sh = ip.RUN_SH.replace("__INI__", ip.ini_path_wsl(p)).replace("__RUN__", "0")
print("has -f:", "-f" in sh)
print(sh[:260])
