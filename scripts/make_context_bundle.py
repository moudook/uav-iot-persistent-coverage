"""
Bundle the project source code and useful context into one .txt file.

What is included:
  - source code: .py .tex .md .ps1 .sh .ned .h .cc .yml .yaml .ini .toml
  - small data/config context: .json .csv .jsonl (below MAX_JSON_BYTES)
  - small text context: .txt (below MAX_TXT_BYTES)
  - files named Makefile / Dockerfile / .gitignore

What is excluded:
  - git internals, venvs, __pycache__, build artefacts
  - ml_impl/runs (training/evaluation artifacts)
  - binaries: .pt .pkl .png .pdf .pptx etc.
  - LaTeX build outputs, logs, checkpoints

The output is PROJECT_CONTEXT.txt at the project root, with:
  1. a file tree of every included file
  2. for each file: a header line with path and length, then its contents

Run:
    python scripts/make_context_bundle.py
"""
import os
import sys
import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SKIP_DIRS = {
    ".git", ".venv", "venv", "node_modules", "__pycache__",
    ".mypy_cache", ".ruff_cache",
}
SKIP_DIR_PREFIXES = ("ml_impl/runs",)
SKIP_EXTS = {
    ".pt", ".pth", ".ckpt", ".pkl", ".gz", ".png", ".jpg", ".jpeg",
    ".pdf", ".pptx", ".pyc", ".sca", ".vec", ".vci", ".elog",
    ".movements", ".aux", ".log", ".out", ".err", ".toc", ".nav",
    ".snm", ".fls", ".fdb_latexmk", ".bbl", ".blg", ".xdv",
}
INCLUDE_EXTS = {
    ".py", ".tex", ".md", ".ps1", ".sh", ".ned", ".h", ".cc",
    ".yml", ".yaml", ".ini", ".toml", ".cfg",
}
SMALL_JSON_EXTS = {".json", ".jsonl", ".csv"}
MAX_JSON_BYTES = 120_000
MAX_TXT_BYTES = 300_000
MAX_FILE_BYTES = 512_000

def rel(path: str) -> str:
    return os.path.relpath(path, ROOT).replace("\\", "/")

def in_skipped_dir(path: str) -> bool:
    r = rel(path)
    parts = r.split("/")
    if any(p in SKIP_DIRS for p in parts):
        return True
    for prefix in SKIP_DIR_PREFIXES:
        if r == prefix or r.startswith(prefix + "/"):
            return True
    return False

def should_include(path: str) -> bool:
    if in_skipped_dir(path):
        return False
    ext = os.path.splitext(path)[1].lower()
    name = os.path.basename(path).lower()
    if name in ("makefile", "dockerfile", ".gitignore", "license", "readme"):
        return True
    if ext in SKIP_EXTS:
        return False
    size = os.path.getsize(path)
    if size > MAX_FILE_BYTES:
        return False
    if ext in INCLUDE_EXTS:
        return True
    if ext in SMALL_JSON_EXTS:
        return size <= MAX_JSON_BYTES
    if ext == ".txt":
        return size <= MAX_TXT_BYTES
    return False

def main() -> int:
    included = []
    skipped = []
    for dp, dn, fn in os.walk(ROOT, topdown=True):
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        if in_skipped_dir(dp):
            dn[:] = []
            continue
        for f in fn:
            p = os.path.join(dp, f)
            if should_include(p):
                included.append(p)
            else:
                skipped.append(p)

    included.sort(key=rel)
    out_path = os.path.join(ROOT, "PROJECT_CONTEXT.txt")
    with open(out_path, "w", encoding="utf-8", errors="replace") as out:
        out.write("PROJECT CONTEXT BUNDLE\n")
        out.write("Generated: %s\n" % datetime.datetime.now().isoformat(timespec="seconds"))
        out.write("Root: %s\n" % ROOT)
        out.write("Included files: %d\n" % len(included))
        total = sum(os.path.getsize(p) for p in included)
        out.write("Total content: %.2f MB\n" % (total / 1e6))
        out.write("\n" + "=" * 80 + "\nFILE TREE (included)\n" + "=" * 80 + "\n")
        for p in included:
            out.write(rel(p) + "  [%d bytes]\n" % os.path.getsize(p))
        out.write("\n\n" + "=" * 80 + "\nFILE CONTENTS\n" + "=" * 80 + "\n")
        for p in included:
            out.write("\n\n" + "=" * 80 + "\nPATH: " + rel(p) + "\n"
                      + "=" * 80 + "\n")
            try:
                with open(p, "r", encoding="utf-8", errors="replace") as f:
                    out.write(f.read())
            except Exception as e:
                out.write("<<UNREADABLE: %s>>\n" % e)

    print("included", len(included), "files")
    print("output:", out_path)
    print("bundle MB:", round(os.path.getsize(out_path) / 1e6, 2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())