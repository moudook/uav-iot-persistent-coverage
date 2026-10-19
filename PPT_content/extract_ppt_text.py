from pptx import Presentation

prs = Presentation(r"PPT.pptx")

out_path = r"PPT_content_extracted.txt"

lines = []
lines.append("=" * 60)
lines.append("PPT.pptx Extracted Text (word-for-word)")
lines.append("=" * 60)

for i, slide in enumerate(prs.slides, 1):
    lines.append("")
    lines.append(f"--- Slide {i} ---")
    for shape in slide.shapes:
        if not shape.has_text_frame:
            continue
        for para in shape.text_frame.paragraphs:
            text = para.text.strip()
            if text:
                lines.append(text)

with open(out_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"Wrote {out_path}")
