with open('src/components/ChangelogSection.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

new_entry = """  {
    version: 'v2.5.7',
    date: '27 сентября 2026',
    title: 'Smart Facing Alignment & /build rotate Command',
    badge: 'Текущая',
    changes: [
      { type: 'feature', text: 'Добавлена команда /build rotate (и /build turn): позволяет мэру или строителю в любой момент повернуть голограмму постройки на 90° (0° -> 90° -> 180° -> 270°).' },
      { type: 'feature', text: 'Интеллектуальный учет направления взгляда (Player Yaw): при закладке 1x2 здания плагин автоматически выбирает горизонтальную или вертикальную ориентацию в зависимости от того, куда смотрит игрок.' },
      { type: 'fix', text: 'Устранены ошибки определения габаритов участка при проверке плоскостности грунта для неквадратных построек.' }
    ]
  },"""

idx = code.find('VERSIONS: VersionLog[] = [')
if idx != -1:
    insert_pos = idx + len('VERSIONS: VersionLog[] = [\n')
    code = code.replace("version: 'v2.5.6',\n    date: '27 сентября 2026',\n    title: 'Mandatory Player Chunk Anchor & Robust Rotation',\n    badge: 'Текущая',", "version: 'v2.5.6',\n    date: '27 сентября 2026',\n    title: 'Mandatory Player Chunk Anchor & Robust Rotation',")
    code = code[:insert_pos] + new_entry + "\n" + code[insert_pos:]

with open('src/components/ChangelogSection.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated ChangelogSection.tsx with v2.5.7!")
