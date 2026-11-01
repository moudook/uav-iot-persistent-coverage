"""Swap the superseded Results section for the corrected one.

The corrected text is docs/new_results_FINAL.tex (assembled from artifacts by
scripts/assemble_new_results.py).  This script replaces everything between
\section{Results} and \section{The corrected protocol, and the re-measurement}
in Mlawn-midsem-tex.tex with it, then runs the dead-number check.

Run: python scripts/swap_results.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TEX = os.path.join(ROOT, "Mlawn-midsem-tex.tex")
NEW = os.path.join(ROOT, "docs", "new_results_FINAL.tex")


def main():
    s = open(TEX, encoding="utf-8").read()
    new = open(NEW, encoding="utf-8").read()

    start_marker = r"\section{Results}"
    end_marker = r"\section{The corrected protocol, and the re-measurement}"
    i = s.index(start_marker)
    j = s.index(end_marker)
    old_len = j - i
    s2 = s[:i] + new.rstrip() + "\n\n" + s[j:]
    open(TEX, "w", encoding="utf-8").write(s2)
    print("replaced %d chars of old Results" % old_len)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
