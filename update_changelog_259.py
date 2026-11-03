with open('src/components/ChangelogSection.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

new_entry = """  {
    version: 'v2.5.9',
    date: '27 сентября 2026',
    title: 'Clean 0% Start & Layer Progression Fix',
    badge: 'Текущая',
    changes: [
      { type: 'fix', text: 'Исправлен старт постройки с 0%: удалено ложное автораспознавание подземных/ландшафтных блоков при закладке здания, счетчик ресурсов теперь строго начинается с 0.' },
      { type: 'fix', text: 'Исправлена смена слоев/этапов строительства: после установки всех блоков Слой 1 гарантированно переходит в Слой 2 с воспроизведением эффектов и отображением голограмм следующего уровня.' },
      { type: 'improvement', text: 'Добавлено оповещение в чат города о завершении каждого слоя и открытии нового этапа постройки.' }
    ]
  },"""

idx = code.find('VERSIONS: VersionLog[] = [')
if idx != -1:
    insert_pos = idx + len('VERSIONS: VersionLog[] = [\n')
    code = code.replace("version: 'v2.5.8',\n    date: '27 сентября 2026',\n    title: 'Aspect-Preserving 1x2 Rotation & Perfect Chunk Fit',\n    badge: 'Текущая',", "version: 'v2.5.8',\n    date: '27 сентября 2026',\n    title: 'Aspect-Preserving 1x2 Rotation & Perfect Chunk Fit',")
    code = code[:insert_pos] + new_entry + "\n" + code[insert_pos:]

with open('src/components/ChangelogSection.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated ChangelogSection.tsx with v2.5.9!")
