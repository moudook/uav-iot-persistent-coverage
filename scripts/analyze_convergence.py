import json
d = json.load(open("ml_impl/runs/g1/convergence_seed0.json"))
hist = d["hist"]
cks = [h.get("CK", 0.0) for h in hist]
ents = [h.get("entropy", 0.0) for h in hist]
print("episodes:", len(hist))
print("final CK: %.4f" % d["final_ck"])
print("CK mean (all): %.4f" % (sum(cks)/len(cks)))
print("CK mean (last 100): %.4f" % (sum(cks[-100:])/100))
print("CK min/max: %.4f / %.4f" % (min(cks), max(cks)))
print("entropy final: %.4f" % ents[-1])
print("entropy min: %.4f (at ep %d)" % (min(ents), ents.index(min(ents))))
# when did entropy drop below 0.1?
for i, e in enumerate(ents):
    if e < 0.1:
        print("entropy < 0.1 first at ep %d (value %.4f)" % (i, e))
        break
# CK at 25, 50, 100, 200, 500, 1000 episodes
for ep in [25, 50, 100, 200, 500, 999]:
    if ep < len(cks):
        print("  ep %4d: CK=%.4f ent=%.4f" % (ep, cks[ep], ents[ep]))
