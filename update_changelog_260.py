with open('src/components/ChangelogSection.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

new_entry = """  {
    version: 'v2.6.0',
    date: '27 сентября 2026',
    title: 'Strict Sequential Auto-Detection & Adaptive Alignment',
    badge: 'Текущая',
    changes: [
      { type: 'feature', text: 'Интеллектуальное автораспознавание частично возведенных зданий: сканирует строго послойно от фундамента (Слой 0) вверх только при наличии реальной кладки игрока (>=40% блоков фундамента).' },
      { type: 'improvement', text: 'Автоподстройка чертежа: при утверждении проекта плагин сам поворачивает чертеж (0°, 90°, 180°, 270°) и подгоняет высоту Y под фундамент игрока.' },
      { type: 'fix', text: 'Полная защита от ложного срабатывания на естественный рельеф: ландшафтные породы больше не вызывают ложный прогресс.' }
    ]
  },"""

idx = code.find('VERSIONS: VersionLog[] = [')
if idx != -1:
    insert_pos = idx + len('VERSIONS: VersionLog[] = [\n')
    code = code.replace("version: 'v2.5.9',\n    date: '27 сентября 2026',\n    title: 'Clean 0% Start & Layer Progression Fix',\n    badge: 'Текущая',", "version: 'v2.5.9',\n    date: '27 сентября 2026',\n    title: 'Clean 0% Start & Layer Progression Fix',")
    code = code[:insert_pos] + new_entry + "\n" + code[insert_pos:]

with open('src/components/ChangelogSection.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated ChangelogSection.tsx with v2.6.0!")
