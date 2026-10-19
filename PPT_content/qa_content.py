from pptx import Presentation
DST = r"C:\Users\gbust\Downloads\Academic\Courses\Machine_learning_in_wireless_network\Project1\PPT_content\PPT.pptx"
prs = Presentation(DST)
print("SLIDES:", len(prs.slides._sldIdLst))
alltext = []
for i, s in enumerate(prs.slides, 1):
    txt = []
    for sh in s.shapes:
        if sh.has_text_frame:
            t = sh.text_frame.text.strip()
            if t: txt.append(t)
    alltext.append((i, "\n".join(txt)))
flat = "\n".join(t for _, t in alltext)
# key verbatim phrases that must survive
checks = [
    "Flying Ad-hoc Networks (FANETs)",
    "win-win case not only for UAVs",
    "protocol converters",
    "holistic view about the current state-of-the-art",
    "Releases 15 to 18",
    "Digital Twins (DT), Reconfigurable Intelligent Surfaces (RIS)",
    "three-dimensional free space movements",
    "niche topic to a key enabler",
    "UxNB (UAV as gNB)",
    "AERPAW", "SkyRAN", "EuroDRONE",
    "temporary aerial base stations",
    "Multi-Agent Q-Learning for dynamic formation",
    "Confidentiality, Integrity, Non-repudiation",
    "TTS-CGAN, MTS-CGAN",
]
print("\n=== CONTENT CHECKS ===")
missing = [c for c in checks if c not in flat]
for c in checks:
    print(("OK  " if c in flat else "MISS") + "  " + c)
print("\nMISSING:", missing if missing else "none")
print("\n=== PER-SLIDE TITLE ===")
for i, t in alltext:
    first = t.split("\n",1)[0][:70]
    print(f"{i:2d}. {first}")
