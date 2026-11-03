with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/TownyArchitecturePlugin.java', 'r', encoding='utf-8') as f:
    content = f.read()

old_task = """        integrityTask = Bukkit.getScheduler().runTaskTimer(this, () -> {
            buildingManager.performPeriodicIntegrityCheck();
        }, 600L, 1200L);"""

new_task = """        int watchdogInterval = getConfig().getInt("settings.watchdog-interval-seconds", 30);
        integrityTask = Bukkit.getScheduler().runTaskTimer(this, () -> {
            buildingManager.performWatchdogAudit(null, false);
        }, 200L, Math.max(10, watchdogInterval) * 20L);"""

assert old_task in content, "old_task not found"
content = content.replace(old_task, new_task, 1)

content = content.replace(
    'getLogger().info(" Периодический аудит блоков: АКТИВЕН (каждые 60 сек)");',
    'getLogger().info(" Мониторинг построек (Watchdog): АКТИВЕН (каждые " + watchdogInterval + " сек)");'
)

with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/TownyArchitecturePlugin.java', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated TownyArchitecturePlugin.java successfully!")
