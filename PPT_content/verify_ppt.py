from pptx import Presentation
DST = r"C:\Users\gbust\Downloads\Academic\Courses\Machine_learning_in_wireless_network\Project1\PPT_content\PPT.pptx"
prs = Presentation(DST)
print("Opened OK. Slides:", len(prs.slides._sldIdLst))
for i, s in enumerate(prs.slides, 1):
    title = ""
    for ph in s.placeholders:
        if ph.placeholder_format.idx == 0 and ph.text_frame.text.strip():
            title = ph.text_frame.text.strip().replace("\n", " / ")
            break
    if not title:
        # fallback first non-empty
        for ph in s.placeholders:
            if ph.text_frame.text.strip():
                title = ph.text_frame.text.strip().replace("\n"," / ")[:60]
                break
    print(f"{i:2d}. {title[:80]}")
