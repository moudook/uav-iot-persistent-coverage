from pptx import Presentation
from pptx.util import Emu

path = r"C:\Users\gbust\Downloads\Academic\Courses\Machine_learning_in_wireless_network\Project1\PPT_content\PPT.pptx"
prs = Presentation(path)
print("Slide size:", prs.slide_width, "x", prs.slide_height)
print("Num slides:", len(prs.slides))
print("=" * 60)
for i, slide in enumerate(prs.slides):
    print(f"\n--- SLIDE {i+1} ---")
    for shape in slide.shapes:
        print(f"  shape id={shape.shape_id} name={shape.name!r} type={shape.shape_type} ph={shape.is_placeholder}")
        if shape.is_placeholder:
            print(f"     ph_type={shape.placeholder_format.type} idx={shape.placeholder_format.idx}")
        # print bbox
        try:
            print(f"     pos=({shape.left},{shape.top}) size=({shape.width}x{shape.height})")
        except Exception as e:
            print("     pos err", e)
        if shape.has_text_frame:
            txt = shape.text_frame.text
            if txt.strip():
                for p in shape.text_frame.paragraphs:
                    runs = p.runs
                    line = "".join(r.text for r in runs)
                    if line.strip():
                        print(f"     TEXT: {line[:160]}")
        if shape.has_table:
            print("     TABLE:")
            for r in shape.table.rows:
                print("       " + " | ".join(c.text for c in r.cells))
