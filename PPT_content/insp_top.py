from pptx import Presentation
path = r"C:\Users\gbust\Downloads\Academic\Courses\Machine_learning_in_wireless_network\Project1\PPT_content\PPT.pptx"
prs = Presentation(path)
print("Total slides:", len(prs.slides._sldIdLst))
for i, slide in enumerate(prs.slides[:3], 1):
    print(f"\n=== SLIDE {i} ===")
    for sh in slide.shapes:
        if sh.has_text_frame and sh.text_frame.text.strip():
            t = sh.text_frame.text.strip().replace("\n"," | ")
            print(f"  [{sh.shape_type}] ph={sh.is_placeholder} idx={sh.placeholder_format.idx if sh.is_placeholder else '-'} : {t[:90]}")
