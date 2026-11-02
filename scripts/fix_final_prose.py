P = r"C:\Users\gbust\Downloads\Academic\Courses\Machine_learning_in_wireless_network\Project1\Mlawn-midsem-tex.tex"
s = open(P, encoding="utf-8").read()

old1 = "and it is the reason the broadcast summary of the deficit is part of the observation model."
new1 = "and it is the reason the ego-centric summary of the deficit is part of the observation model."
assert s.count(old1) == 1
s = s.replace(old1, new1, 1)

old2 = "Section~VIII reports the results and the claim audit, and Section~IX concludes the paper."
new2 = "Section~VIII reports the results and the claim audit, Section~IX details the protocol correction and re-measurement, and Section~X concludes the paper."
assert s.count(old2) == 1
s = s.replace(old2, new2, 1)

open(P, "w", encoding="utf-8").write(s)
print("prose updated")

T = r"C:\Users\gbust\Downloads\Academic\Courses\Machine_learning_in_wireless_network\Project1\ml_impl\analysis\fig_teaser.tex"
t = open(T, encoding="utf-8").read()
old3 = "\\node[anchor=south west, font=\\tiny] at (axis cs:3.43,2.93) {the two criteria disagree};"
new3 = "\\node[anchor=south west, font=\\tiny, fill=white, inner sep=1pt] at (axis cs:3.43,2.93) {the two criteria disagree};"
assert t.count(old3) == 1
t = t.replace(old3, new3, 1)
open(T, "w", encoding="utf-8").write(t)
print("teaser label updated")
