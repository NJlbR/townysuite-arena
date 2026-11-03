with open('src/components/ChangelogSection.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

new_entry = """  {
    version: 'v2.5.8',
    date: '27 сентября 2026',
    title: 'Aspect-Preserving 1x2 Rotation & Perfect Chunk Fit',
    badge: 'Текущая',
    changes: [
      { type: 'feature', text: 'Гарантированная посадка 1x2 чертежей: постройка строго привязывается к геометрии выделенных 2 чанков (горизонтальных 2x1 или вертикальных 1x2) без вылезания за границы.' },
      { type: 'improvement', text: 'Команда /build rotate теперь учитывает форму участка: для 2x1 чанков она переключает фасад (90° <-> 270°), а для 1x2 чанков (0° <-> 180°), всегда оставаясь внутри стройплощадки.' },
      { type: 'fix', text: 'Синхронизировано определение взгляда игрока (Player Yaw) между GUI /builds и командой утверждения.' }
    ]
  },"""

idx = code.find('VERSIONS: VersionLog[] = [')
if idx != -1:
    insert_pos = idx + len('VERSIONS: VersionLog[] = [\n')
    code = code.replace("version: 'v2.5.7',\n    date: '27 сентября 2026',\n    title: 'Smart Facing Alignment & /build rotate Command',\n    badge: 'Текущая',", "version: 'v2.5.7',\n    date: '27 сентября 2026',\n    title: 'Smart Facing Alignment & /build rotate Command',")
    code = code[:insert_pos] + new_entry + "\n" + code[insert_pos:]

with open('src/components/ChangelogSection.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated ChangelogSection.tsx with v2.5.8!")
