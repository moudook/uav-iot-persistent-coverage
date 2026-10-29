"""Extract text from both PDFs using pymupdf (fitz) - native Windows Python."""
import fitz  # pymupdf
import os

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF1 = os.path.join(PROJ, "OLD_REPORT", "OLD_MIDSEM_REPORT.pdf")
PDF2 = os.path.join(PROJ, "Mlawn-midsem-tex.pdf")
OUT = os.path.join(PROJ, "docs")

def extract(pdf_path):
    doc = fitz.open(pdf_path)
    pages = []
    for i, page in enumerate(doc):
        text = page.get_text()
        pages.append(f"=== PAGE {i+1} ===\n{text}")
    doc.close()
    return "\n\n".join(pages)

print("Extracting PDF1 (OLD_MIDSEM_REPORT.pdf)...")
t1 = extract(PDF1)
print(f"  Length: {len(t1)} chars, {t1.count(chr(10))} lines")

print("Extracting PDF2 (Mlawn-midsem-tex.pdf)...")
t2 = extract(PDF2)
print(f"  Length: {len(t2)} chars, {t2.count(chr(10))} lines")

# Save
os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "pdf1_text.txt"), "w", encoding="utf-8") as f:
    f.write(t1)
with open(os.path.join(OUT, "pdf2_text.txt"), "w", encoding="utf-8") as f:
    f.write(t2)

print(f"\nSaved to {OUT}/pdf1_text.txt and {OUT}/pdf2_text.txt")
print(f"\n=== PDF1 FIRST 4000 CHARS ===\n{t1[:4000]}")
print(f"\n=== PDF2 FIRST 4000 CHARS ===\n{t2[:4000]}")