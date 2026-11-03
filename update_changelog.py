with open('src/components/ChangelogSection.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

new_entry = """  {
    version: 'v2.5.5',
    date: '27 сентября 2026',
    title: 'Closest Anchor Plot & Preserved Rotation',
    badge: 'Текущая',
    changes: [
      { type: 'feature', text: 'Умный выбор ближайшего участка: при утверждении постройки плагин выбирает самую близкую к игроку комбинацию смежных свободных чанков.' },
      { type: 'fix', text: 'Исправлен сброс угла поворота (rotationDeg), теперь голограмма 1x2 / 2x1 корректно поворачивается по сетке чанков.' },
      { type: 'improvement', text: 'Строгая проверка того, что чанк игрока является частью выбранного анкера.' }
    ]
  },"""

# Insert new entry right after VERSIONS = [
idx = code.find('VERSIONS: VersionLog[] = [')
if idx != -1:
    insert_pos = idx + len('VERSIONS: VersionLog[] = [\n')
    # mark old v2.5.4 as not current badge
    code = code.replace("version: 'v2.5.4',\n    date: '27 сентября 2026',\n    title: 'Strict Anchor Plot & Perfect Rotation Alignment',\n    badge: 'Текущая',", "version: 'v2.5.4',\n    date: '27 сентября 2026',\n    title: 'Strict Anchor Plot & Perfect Rotation Alignment',")
    code = code[:insert_pos] + new_entry + "\n" + code[insert_pos:]

with open('src/components/ChangelogSection.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated ChangelogSection.tsx with v2.5.5!")
