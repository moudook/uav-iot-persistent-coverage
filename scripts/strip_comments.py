"""Strip Python # comments from copies, preserving docstrings and semantics.

Uses tokenize so strings containing '#' are untouched. Verifies that
ast.dump of the stripped code equals ast.dump of the original.
"""
import ast, io, sys, tokenize
from pathlib import Path

def strip_py(src: str) -> str:
    toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    out = []
    for tok in toks:
        if tok.type == tokenize.COMMENT:
            continue
        out.append(tok)
    return tokenize.untokenize(out)

def main(root: str) -> int:
    fails = 0
    for f in sorted(Path(root).rglob("*.py")):
        if ".git" in f.parts:
            continue
        src = f.read_text(encoding="utf-8", errors="replace")
        if "#" not in src:
            continue
        try:
            stripped = strip_py(src)
            # semantic check: AST must be identical
            a1 = ast.dump(ast.parse(src))
            a2 = ast.dump(ast.parse(stripped))
            if a1 != a2:
                print("AST MISMATCH:", f)
                fails += 1
                continue
            f.write_text(stripped, encoding="utf-8")
            print("stripped:", f.relative_to(root))
        except Exception as e:
            print("ERROR:", f, e)
            fails += 1
    print("done, fails =", fails)
    return 1 if fails else 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
