from pptx import Presentation
src = "PPT.pptx"
prs = Presentation(src)
sldIdLst = prs.slides._sldIdLst
kids = list(sldIdLst)
order = list(range(10, 15)) + list(range(0, 10))
for k in kids:
    sldIdLst.remove(k)
for i in order:
    sldIdLst.append(kids[i])
prs.save("PPT_tail.pptx")
print("reordered")
