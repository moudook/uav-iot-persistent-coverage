"""Remove full-line LaTeX comments (%) from copies, carefully.

Only removes lines whose first non-whitespace character is '%'.
Preserves escaped '\\%' and inline comments after content.
Verifies the stripped file still parses by checking balanced environments
are unchanged is out of scope; compilation must be checked separately.
"""
import sys
from pathlib import Path

def strip_tex(src: str) -> str:
    out = []
    for line in src.splitlines(keepends=True):
        stripped = line.lstrip()
        if stripped.startswith("%"):
            continue
        # drop trailing pure-comment? keep inline content intact
        out.append(line)
    return "".join(out)

def main(root: str) -> int:
    for f in sorted(Path(root).rglob("*.tex")):
        if ".git" in f.parts:
            continue
        src = f.read_text(encoding="utf-8", errors="replace")
        stripped = strip_tex(src)
        if stripped != src:
            f.write_text(stripped, encoding="utf-8")
            print("stripped tex comments:", f.relative_to(root))
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
