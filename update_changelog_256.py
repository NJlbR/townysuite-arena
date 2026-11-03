with open('src/components/ChangelogSection.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

new_entry = """  {
    version: 'v2.5.6',
    date: '27 сентября 2026',
    title: 'Mandatory Player Chunk Anchor & Robust Rotation',
    badge: 'Текущая',
    changes: [
      { type: 'feature', text: 'Строгое обязательное требование: утверждаемая постройка обязана включать тот самый чанк, на котором в данный момент стоит игрок.' },
      { type: 'improvement', text: 'Улучшена гибкость расчета вращения (rotationDeg) для 1x2 построек при любой ориентации свободных чанков.' },
      { type: 'fix', text: 'Устранены любые возможности утверждения построек на отдаленных участках без участия чанка игрока.' }
    ]
  },"""

idx = code.find('VERSIONS: VersionLog[] = [')
if idx != -1:
    insert_pos = idx + len('VERSIONS: VersionLog[] = [\n')
    code = code.replace("version: 'v2.5.5',\n    date: '27 сентября 2026',\n    title: 'Closest Anchor Plot & Preserved Rotation',\n    badge: 'Текущая',", "version: 'v2.5.5',\n    date: '27 сентября 2026',\n    title: 'Closest Anchor Plot & Preserved Rotation',")
    code = code[:insert_pos] + new_entry + "\n" + code[insert_pos:]

with open('src/components/ChangelogSection.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated ChangelogSection.tsx with v2.5.6!")
