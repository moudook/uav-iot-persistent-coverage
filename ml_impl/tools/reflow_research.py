"""Reflow the Qwen Deep Research markdown into readable, wrapped text.

The reports arrive as a single line with no newlines. This splits on heading
markers and wraps paragraphs while leaving fenced code blocks untouched.

Usage: python tools/reflow_research.py <in.md> [<out.md>]
"""

from __future__ import annotations

import os
import re
import sys
import textwrap

FENCE = "`" * 3


def reflow(text: str, width: int = 110) -> str:
    text = re.sub(r"(?<!\n)(#{1,4} )", r"\n\1", text)
    text = re.sub(r"(?<!\n)(--- DIAGNOSTIC)", r"\n\1", text)

    out: list[str] = []
    for block in text.split("\n"):
        block = block.strip()
        if not block:
            continue
        if block.startswith("#"):
            if "  " in block:
                head, body = block.split("  ", 1)
            else:
                head, body = block[:120], block[120:]
            out.append("")
            out.append(head.strip())
            out.append("")
            in_fence = False
            for line in body.split("\n"):
                s = line.strip()
                if s.startswith(FENCE):
                    in_fence = not in_fence
                    out.append(line)
                    continue
                if in_fence:
                    out.append(line)
                    continue
                if not s:
                    out.append("")
                    continue
                out.extend(textwrap.wrap(s, width=width) or [""])
        else:
            out.extend(textwrap.wrap(block, width=width) or [""])
    cleaned: list[str] = []
    for line in out:
        if line == "" and cleaned and cleaned[-1] == "":
            continue
        cleaned.append(line)
    return "\n".join(cleaned).strip() + "\n"


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    src = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) > 2 else (
        os.path.splitext(src)[0] + "_reflow.md"
    )
    with open(src, encoding="utf-8") as f:
        text = f.read()
    result = reflow(text)
    with open(dst, "w", encoding="utf-8") as f:
        f.write(result)
    print(f"{src} -> {dst}  ({len(result.splitlines())} lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
