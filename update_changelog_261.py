with open('src/components/ChangelogSection.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

new_entry = """  {
    version: 'v2.6.1',
    date: '27 сентября 2026',
    title: 'Dual-Verification Layer Advance & Missing Blocks Tracker',
    badge: 'Текущая',
    changes: [
      { type: 'fix', text: 'Исправлен переход на следующий слой: внедрена двойная валидация (память + сканирование реального мира). Если игрок уже установил блок или блок присутствовал в мире, он гарантированно засчитывается.' },
      { type: 'feature', text: 'Детальный счетчик слоя в реальном времени: в ActionBar и BossBar отображается точное количество установленных и оставшихся блоков в текущем слое (например, «Слой 2: 82/83 (Осталось: 1 бл.)»).' },
      { type: 'feature', text: 'Команда поиска недостроенных блоков (/build check / /build remaining): выводит точный список недостающих материалов и подсвечивает их координаты в мире оранжевыми маяками.' }
    ]
  },"""

idx = code.find('VERSIONS: VersionLog[] = [')
if idx != -1:
    insert_pos = idx + len('VERSIONS: VersionLog[] = [\n')
    code = code.replace("version: 'v2.6.0',\n    date: '27 сентября 2026',\n    title: 'Strict Sequential Auto-Detection & Adaptive Alignment',\n    badge: 'Текущая',", "version: 'v2.6.0',\n    date: '27 сентября 2026',\n    title: 'Strict Sequential Auto-Detection & Adaptive Alignment',")
    code = code[:insert_pos] + new_entry + "\n" + code[insert_pos:]

with open('src/components/ChangelogSection.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated ChangelogSection.tsx with v2.6.1!")
