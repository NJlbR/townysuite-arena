import sys

with open('tmp/minecraft-build/src/main/java/com/towny/architecture/manager/ArchitectManager.java', 'r', encoding='utf-8') as f:
    content = f.read()

target = """    public void resetStats(Player player) {
        statsMap.remove(player.getUniqueId());
        removeBossBar(player);
        player.sendMessage(ChatColor.GREEN + "Ваш опыт архитектора и лимит блоков успешно сброшены.");
        save();
    }"""

replacement = """    public void resetStats(Player player) {
        statsMap.remove(player.getUniqueId());
        removeBossBar(player);
        player.sendMessage(ChatColor.GREEN + "Ваш опыт архитектора и лимит блоков успешно сброшены.");
        save();
    }

    public void setLevel(Player player, int level) {
        ArchitectStats stats = getStats(player);
        stats.xp = getXpForLevel(level);
        save();
        updateBossBar(player);
    }"""

if target in content:
    with open('tmp/minecraft-build/src/main/java/com/towny/architecture/manager/ArchitectManager.java', 'w', encoding='utf-8') as f:
        f.write(content.replace(target, replacement))
    print("Patched setLevel successfully.")
else:
    print("Target content not found!")
