import re
p = r"C:\Users\gbust\Downloads\Academic\Courses\Machine_learning_in_wireless_network\Project1\Mlawn-midsem-tex.tex"
s = open(p, encoding="utf-8").read()

start = s.index("\\subsection{Innovations: closing the small-battery and spread-start gaps}")
end = s.index("\\subsection{Network certificate}")

# Build one clean copy from the second (body is identical to first)
block = s[start:end]
# keep only the second copy: split on the subsection marker
parts = block.split("\\subsection{Innovations: closing the small-battery and spread-start gaps}")
assert len(parts) == 3, len(parts)  # ['', copy1, comment + copy2]
copy2 = parts[2]
# strip any leftover comment lines and trailing EOF
lines = [ln for ln in copy2.splitlines() if not ln.strip().startswith("% INNOVATION RESULTS")]
clean = "\n".join(lines).rstrip()
clean = clean.replace("\nEOF", "")
clean = clean.rstrip() + "\n\n"

s = s[:start] + clean + s[end:]
open(p, "w", encoding="utf-8").write(s)
print("dedup done; new count:", s.count("\\subsection{Innovations: closing the small-battery and spread-start gaps}"))
print("EOF count:", s.count("EOF"))
