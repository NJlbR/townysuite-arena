with open('src/components/ChangelogSection.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

new_entry = """  {
    version: 'v2.6.2',
    date: '28 сентября 2026',
    title: 'Clean Holograms - Cyan Dust Particles Removed',
    badge: 'Текущая',
    changes: [
      { type: 'improvement', text: 'Убраны облака голубых пылевых частиц с голограмм блоков: теперь отображаются только четкие, эстетичные нативные голубые светящиеся границы (BlockDisplay Glowing Shader).' },
      { type: 'improvement', text: 'Красные частицы сохранены исключительно для реальных препятствий в мире (деревья, лишняя земля), мешающих установке.' }
    ]
  },"""

idx = code.find('VERSIONS: VersionLog[] = [')
if idx != -1:
    insert_pos = idx + len('VERSIONS: VersionLog[] = [\n')
    code = code.replace("version: 'v2.6.1',\n    date: '27 сентября 2026',\n    title: 'Dual-Verification Layer Advance & Missing Blocks Tracker',\n    badge: 'Текущая',", "version: 'v2.6.1',\n    date: '27 сентября 2026',\n    title: 'Dual-Verification Layer Advance & Missing Blocks Tracker',")
    code = code[:insert_pos] + new_entry + "\n" + code[insert_pos:]

with open('src/components/ChangelogSection.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated ChangelogSection.tsx with v2.6.2!")
