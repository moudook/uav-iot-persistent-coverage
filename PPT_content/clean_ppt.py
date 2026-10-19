import zipfile, re, shutil, os
from xml.etree import ElementTree as ET

path = r"C:\Users\gbust\Downloads\Academic\Courses\Machine_learning_in_wireless_network\Project1\PPT_content\PPT.pptx"
tmp = path + ".clean.zip"

z = zipfile.ZipFile(path, 'r')
names = z.namelist()
# find duplicate base names
from collections import Counter
base = Counter(n for n in names)
dups = [k for k,c in base.items() if c>1]
print("DUPLICATE ENTRIES:", dups[:20], "..." if len(dups)>20 else "")

# Parse presentation.xml to find referenced slide partnames
pres = z.read('ppt/presentation.xml').decode('utf-8')
rels = z.read('ppt/_rels/presentation.xml.rels').decode('utf-8')
rel_root = ET.fromstring(rels.encode('utf-8'))
ns = {'pr':'http://schemas.openxmlformats.org/package/2006/relationships'}
# map rId -> Target
rid_target = {}
for rel in rel_root.findall('pr:Relationship', ns):
    rid_target[rel.get('Id')] = rel.get('Target')
# sldId r:ids
sldIds = re.findall(r'<p:sldId[^>]*r:id="(rId\d+)"', pres)
referenced = set()
for rid in sldIds:
    t = rid_target.get(rid)
    if t:
        # Target like 'slides/slide21.xml' relative to ppt/
        referenced.add('ppt/' + t.lstrip('./'))
print("Referenced slide parts:", sorted(referenced))
print("Total slide entries in zip:", [n for n in names if re.match(r'ppt/slides/slide\d+\.xml$', n)])

# Build set of parts to KEEP
# Unreferenced slide parts + their rels are orphans to drop
slide_re = re.compile(r'ppt/slides/slide(\d+)\.xml$')
orphan_slides = set()
for n in names:
    m = slide_re.match(n)
    if m and n not in referenced:
        orphan_slides.add(n)
print("Orphan slide parts to remove:", sorted(orphan_slides))

# Write cleaned zip
keep = []
for n in names:
    if n in orphan_slides:
        continue
    if re.match(r'ppt/slides/_rels/slide\d+\.xml\.rels$', n):
        # keep only if corresponding slide kept
        m = re.search(r'slide(\d+)\.xml\.rels$', n)
        if m and f'ppt/slides/slide{m.group(1)}.xml' not in referenced:
            continue
    keep.append(n)

with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as out:
    for n in keep:
        out.writestr(n, z.read(n))
z.close()
shutil.move(tmp, path)
print("Cleaned file written. Kept entries:", len(keep))
