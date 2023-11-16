def get_sections():
  sections = {}
  anchors = [-1] * 6
  with open('../README.md', 'r') as f:
    lines = f.readlines()
  length = len(lines)
  for i in range(length+1):
    if i==length or lines[i].startswith('#') :
      level = 0 if i==length else len(lines[i].split(' ')[0])-1
      for j in range(level, 6):
        if anchors[j] >= 0:
          title = lines[anchors[j]].split(' ', 1)[1].strip()
          sections[title] = ''.join(lines[anchors[j]+2:i-1])
          anchors[j] = -1
      anchors[level] = i
  return sections
