"""Comprehensive diff between OLD_MIDSEM_REPORT.pdf and Mlawn-midsem-tex.pdf."""
import os, re, sys

PROJ = "C:\\Users\\gbust\\Downloads\\Academic\\Courses\\Machine_learning_in_wireless_network\\Project1"

def load(f):
    with open(os.path.join(PROJ, "docs", f), "r", encoding="utf-8-sig") as fh:
        return fh.read()

t1 = load("pdf1_text.txt")  # OLD
t2 = load("pdf2_text.txt")  # NEW

def clean(t):
    t = re.sub(r'=== PAGE \d+ ===\n', '', t)
    return t

t1c = clean(t1)
t2c = clean(t2)

def split_sections(t):
    sections = []
    pattern = r'\n((?:I|II|III|IV|V|VI|VII|VIII|IX|X|XI|XII|XIII|XIV|XV|XVI|XVII|XVIII|XIX|XX)\.\s+[A-Z][A-Z\s\-]+)\n'
    parts = re.split(pattern, t)
    for i in range(1, len(parts), 2):
        heading = parts[i].strip()
        content = parts[i+1] if i+1 < len(parts) else ""
        sections.append((heading, content))
    return sections, parts[0] if parts else ""

s1, pre1 = split_sections(t1c)
s2, pre2 = split_sections(t2c)

# Write output to file to avoid encoding issues
out_lines = []
def w(s=""):
    out_lines.append(str(s))

w("=" * 80)
w("COMPREHENSIVE DIFF: OLD_MIDSEM_REPORT.pdf vs Mlawn-midsem-tex.pdf")
w("=" * 80)
w(f"\nOLD: {len(t1c)} chars, {len(s1)} sections")
w(f"NEW: {len(t2c)} chars, {len(s2)} sections")
w(f"Ratio: {len(t2c)/len(t1c):.1f}x larger\n")

w("=" * 80)
w("1. STRUCTURAL DIFFERENCES")
w("=" * 80)
h1 = [h for h,_ in s1]
h2 = [h for h,_ in s2]
w("\nOLD sections:")
for h in h1: w(f"  - {h}")
w("\nNEW sections:")
for h in h2: w(f"  - {h}")
w(f"\nNEW only: {set(h2) - set(h1)}")
w(f"OLD only: {set(h1) - set(h2)}")

w("\n" + "=" * 80)
w("2. ABSTRACT COMPARISON")
w("=" * 80)
w(f"\nOLD abstract ({len(pre1)} chars):")
w(pre1[:1500])
w(f"\n\nNEW abstract ({len(pre2)} chars):")
w(pre2[:2500])

w("\n" + "=" * 80)
w("3. SECTION-BY-SECTION LENGTH COMPARISON")
w("=" * 80)
for h in h2:
    if h in set(h1):
        c1 = next((c for hh,c in s1 if hh==h), "")
        c2 = next((c for hh,c in s2 if hh==h), "")
        ratio = len(c2)/len(c1) if len(c1) > 0 else float('inf')
        w(f"  {h}:")
        w(f"    OLD: {len(c1):>6} chars")
        w(f"    NEW: {len(c2):>6} chars")
        w(f"    Ratio: {ratio:.2f}x")
    else:
        c2 = next((c for hh,c in s2 if hh==h), "")
        w(f"  {h}: NEW ONLY, {len(c2)} chars")

w("\n" + "=" * 80)
w("4. NEW SECTION VIII: RESULTS (full content)")
w("=" * 80)
for h,c in s2:
    if h == "VIII. RESULTS":
        w(c)

w("\n" + "=" * 80)
w("5. NEW SECTION IX: CONCLUSION (full content)")
w("=" * 80)
for h,c in s2:
    if h == "IX. CONCLUSION":
        w(c)

w("\n" + "=" * 80)
w("6. KEY QUANTITATIVE DIFFERENCES (numbers in NEW not in OLD)")
w("=" * 80)
# Extract all numbers from both
nums_old = set(re.findall(r'\d+\.?\d*%?', t1c))
nums_new = set(re.findall(r'\d+\.?\d*%?', t2c))
new_nums = nums_new - nums_old
w(f"Numbers in NEW but not OLD: {len(new_nums)}")
# Show notable ones
notable = [n for n in new_nums if len(n) >= 3 and n.replace('.','').replace('%','').isdigit()]
w(f"Notable (>=3 chars): {sorted(notable)[:50]}")

w("\n" + "=" * 80)
w("7. KEY TERMS IN NEW NOT IN OLD")
w("=" * 80)
terms_old = set(re.findall(r'[a-zA-Z\-]{4,}', t1c.lower()))
terms_new = set(re.findall(r'[a-zA-Z\-]{4,}', t2c.lower()))
new_terms = terms_new - terms_old
# Filter to significant terms
significant = [t for t in new_terms if len(t) > 6 and t not in ['from', 'that', 'with', 'this', 'they', 'their', 'which', 'would', 'could', 'should', 'about', 'these', 'those', 'there', 'where', 'when', 'what', 'how', 'into', 'over', 'under', 'more', 'some', 'than', 'then', 'also', 'only', 'other', 'such', 'after', 'before', 'between', 'through', 'during', 'while', 'because', 'before', 'above', 'below']]
w(f"Significant new terms ({len(significant)}):")
for t in sorted(significant)[:80]:
    w(f"  - {t}")

# Write output
with open(os.path.join(PROJ, "docs", "PDF_DIFF_REPORT.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(out_lines))

print(f"Wrote {len(out_lines)} lines to docs/PDF_DIFF_REPORT.md")
print(f"Done. OLD={len(t1c)} chars, NEW={len(t2c)} chars, ratio={len(t2c)/len(t1c):.1f}x")