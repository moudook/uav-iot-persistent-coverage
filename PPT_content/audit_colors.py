from pptx import Presentation
prs = Presentation(r"C:\Users\gbust\Downloads\Academic\Courses\Machine_learning_in_wireless_network\Project1\PPT_content\PPT.pptx")
issues = []
for i, s in enumerate(prs.slides, 1):
    for sh in s.shapes:
        if not sh.has_text_frame:
            continue
        fill = None
        try:
            if sh.fill.type is not None and sh.fill.fore_color.type is not None:
                fill = sh.fill.fore_color.rgb
        except Exception:
            fill = None
        for p in sh.text_frame.paragraphs:
            for r in p.runs:
                rc = None
                try:
                    rc = r.font.color.rgb
                except Exception:
                    rc = None
                if rc is not None and fill is not None and rc == fill:
                    issues.append((i, repr(r.text[:40]), str(rc)))
print("COLOR==FILL (text invisible) issues:", len(issues))
for x in issues:
    print("  slide", x[0], x[1], "color", x[2])
# also flag very small fonts (<8pt) which hurt readability
small = []
for i, s in enumerate(prs.slides, 1):
    for sh in s.shapes:
        if not sh.has_text_frame:
            continue
        for p in sh.text_frame.paragraphs:
            for r in p.runs:
                try:
                    if r.font.size and r.font.size.pt < 8:
                        small.append((i, r.font.size.pt, repr(r.text[:30])))
                except Exception:
                    pass
print("FONTS <8pt:", len(small))
for x in small:
    print("  slide", x[0], "size", x[1], x[2])
