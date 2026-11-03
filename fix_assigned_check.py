with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'r', encoding='utf-8') as f:
    code = f.read()

old_snippet = """        if (assignedChunks == null || assignedChunks.isEmpty()) {
            player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                    plugin.getMsg("prefix") + "&cВ вашем городе нет свободного строительного участка размера " +
                    bp.getFootprintDisplay() + "!"));
            player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                    plugin.getMsg("prefix") + "&eНазначьте нужные чанки города командой &f/plot set build&e."));
            return null;
        }"""

new_snippet = """        if (assignedChunks == null || assignedChunks.isEmpty() || !assignedChunks.contains(playerChunk)) {
            player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                    plugin.getMsg("prefix") + "&c[!] Ошибка размещения: Постройка должна в обязательном порядке включать чанк [" + playerChunk.getX() + "," + playerChunk.getZ() + "], на котором вы стоите!"));
            player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                    plugin.getMsg("prefix") + "&eУбедитесь, что текущий чанк назначен через &f/plot set build&e и свободен."));
            return null;
        }"""

if old_snippet in code:
    code = code.replace(old_snippet, new_snippet)
    with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'w', encoding='utf-8') as f:
        f.write(code)
    print("Updated assignedChunks check successfully!")
else:
    print("Error: old_snippet not found")
