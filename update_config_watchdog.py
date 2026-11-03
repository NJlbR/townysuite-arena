with open('tmp/minecraft-build-v2/src/main/resources/config.yml', 'r', encoding='utf-8') as f:
    content = f.read()

target = "  # Интервал (в секундах) проверки и наложения эффектов баффов на жителей\n  buff-check-interval-seconds: 5"

watchdog_cfg = """  # Интервал (в секундах) регулярного мониторинга и аудита всех построек мира (Watchdog)
  # Автоматически синхронизирует состояние блоков, восстанавливает сбившиеся голограммы,
  # переключает завершенные слои, актуализирует статусы (CONSTRUCTING/ACTIVE/DAMAGED) и спасает от сбоев/лага сервера.
  watchdog-interval-seconds: 30

  # Интервал (в секундах) проверки и наложения эффектов баффов на жителей
  buff-check-interval-seconds: 5"""

assert target in content, "target not found in config.yml"
content = content.replace(target, watchdog_cfg, 1)

with open('tmp/minecraft-build-v2/src/main/resources/config.yml', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated config.yml with watchdog-interval-seconds!")
