with open('src/components/ChangelogSection.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

new_entry = """  {
    version: 'v2.7.0',
    date: '28 сентября 2026',
    title: 'Automated Watchdog & Building State Monitoring Engine',
    badge: 'Текущая',
    changes: [
      { type: 'feature', text: 'Фоновый Watchdog-мониторинг построек: каждые 30 секунд (настраивается в config.yml) плагин автоматически сверяет состояние блоков в реальном мире с чертежами всех строящихся и завершенных зданий.' },
      { type: 'feature', text: 'Защита от сбоев и рассинхронизаций (Self-Healing): если сервер лагал, перезагружался, или чанки выгружались, сторожевой сервис автоматически переключает готовые слои, засчитывает установленные блоки и мгновенно восстанавливает пропавшие голограммы BlockDisplay.' },
      { type: 'feature', text: 'Авто-актуализация статусов зданий: автоматическое завершение 100% готовых построек с салютами и баффами; детекция разрушений (взрывы/гриферство) с переводом в DAMAGED и созданием ремонтных меток; мгновенный авто-выход из DAMAGED в ACTIVE после починки.' },
      { type: 'feature', text: 'Команда ручного аудита /build audit (/build monitor / verify / sync): мгновенный диагностический отчет для игроков, мэров и консоли сервера с принудительной синхронизацией базы с миром.' }
    ]
  },"""

idx = code.find('VERSIONS: VersionLog[] = [')
if idx != -1:
    insert_pos = idx + len('VERSIONS: VersionLog[] = [\n')
    code = code.replace("version: 'v2.6.2',\n    date: '28 сентября 2026',\n    title: 'Clean Holograms - Cyan Dust Particles Removed',\n    badge: 'Текущая',", "version: 'v2.6.2',\n    date: '28 сентября 2026',\n    title: 'Clean Holograms - Cyan Dust Particles Removed',")
    code = code[:insert_pos] + new_entry + "\n" + code[insert_pos:]

with open('src/components/ChangelogSection.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated ChangelogSection.tsx with v2.7.0!")
