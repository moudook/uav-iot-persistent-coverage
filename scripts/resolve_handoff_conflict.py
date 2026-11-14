import io

p = 'docs/TEAM_HANDOFF_2026-11-11.md'
s = io.open(p, encoding='utf-8').read()
lines = s.splitlines(keepends=True)
start = next(i for i, l in enumerate(lines) if l.startswith('<<<<<<<'))
mid = next(i for i, l in enumerate(lines) if l.startswith('======='))
end = next(i for i, l in enumerate(lines) if l.startswith('>>>>>>>'))
head = ''.join(lines[start + 1:mid])
theirs = ''.join(lines[mid + 1:end])

idx5 = head.find('5. Table XIV')
head_125 = head[:idx5]
item5 = head[idx5:]

t3 = theirs[theirs.find('3. Dead ablation arms. **Fix done:**'):
             theirs.find('5. table XIV')]

new = ''.join(lines[:start]) + head_125 + t3 + item5 + ''.join(lines[end + 1:])
io.open(p, 'w', encoding='utf-8', newline='\n').write(new)
print('resolved, lines:', len(new.splitlines()))
