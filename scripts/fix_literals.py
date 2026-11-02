P = r"C:\Users\gbust\Downloads\Academic\Courses\Machine_learning_in_wireless_network\Project1\Mlawn-midsem-tex.tex"
s = open(P, encoding="utf-8").read()

def rep(old, new, tag):
    global s
    n = s.count(old)
    assert n == 1, (tag, n)
    s = s.replace(old, new, 1)

rep("against $0.952$: the difference-credit arm",
    "against $0.951$: the difference-credit arm", "credit literal")
rep("($0.959$ vs $0.952$, $+0.007$, not resolved)",
    "($0.959$ vs $0.951$, $+0.008$, not resolved)", "innov diff literal")
rep("beats the rule by $+0.029$; the stress",
    "beats the rule by $+0.028$; the stress", "innov gap literal")
rep("The increment is $\\approx 0.093$ of persistent",
    "The increment is $\\approx 0.092$ of persistent", "abl increment literal")

open(P, "w", encoding="utf-8").write(s)
print("tex literals updated")
