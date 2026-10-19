from pptx import Presentation
path = r"C:\Users\gbust\Downloads\Academic\Courses\Machine_learning_in_wireless_network\Project1\PPT_content\PPT.pptx"
prs = Presentation(path)
print("Num slide layouts:", len(prs.slide_layouts))
for i, layout in enumerate(prs.slide_layouts):
    print(f"\nLAYOUT {i}: name={layout.name!r}")
    for ph in layout.placeholders:
        print(f"   ph idx={ph.placeholder_format.idx} type={ph.placeholder_format.type} name={ph.name!r}")
