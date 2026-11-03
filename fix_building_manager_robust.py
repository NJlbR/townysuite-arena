with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'r', encoding='utf-8') as f:
    code = f.read()

# Locate where assignedChunks is checked in startBuilding
old_check = """        if (assignedChunks == null || assignedChunks.isEmpty()) {
            player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                    plugin.getMsg("prefix") + "&c[!] Ошибка размещения: В текущем чанке и вокруг него нет достаточного количества свободных смежных чанков-стройплощадок для постройки «" + bp.getNameRu() + "» (требуется размер " + bp.getFootprintDisplay() + ")!"));
            player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                    plugin.getMsg("prefix") + "&eУбедитесь, что все необходимые чанки назначены через &f/plot set build&e и не заняты другими постройками."));
            return null;
        }"""

new_check = """        if (assignedChunks == null || assignedChunks.isEmpty() || !assignedChunks.contains(playerChunk)) {
            player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                    plugin.getMsg("prefix") + "&c[!] Ошибка размещения: Постройка должна в обязательном порядке включать чанк [" + playerChunk.getX() + "," + playerChunk.getZ() + "], на котором вы стоите!"));
            player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                    plugin.getMsg("prefix") + "&eУбедитесь, что текущий чанк и соседние свободные чанки назначены через &f/plot set build&e."));
            return null;
        }"""

if old_check in code:
    code = code.replace(old_check, new_check)
    print("Added strict playerChunk inclusion check!")
else:
    print("Warning: old_check not found")

# Also update rotationDeg calculation to be fully robust for any spanX / spanZ
old_rot_calc = """        int rotationDeg = 0;
        if (bp.getChunkWidth() != bp.getChunkLength()) {
            if (spanX == bp.getChunkLength() && spanZ == bp.getChunkWidth()) {
                rotationDeg = 90;
            }
        }"""

new_rot_calc = """        int rotationDeg = 0;
        if (bp.getChunkWidth() != bp.getChunkLength()) {
            if (spanX > spanZ && bp.getChunkWidth() < bp.getChunkLength()) {
                rotationDeg = 90;
            } else if (spanX < spanZ && bp.getChunkWidth() > bp.getChunkLength()) {
                rotationDeg = 90;
            } else if (spanX == bp.getChunkLength() && spanZ == bp.getChunkWidth()) {
                rotationDeg = 90;
            }
        }"""

if old_rot_calc in code:
    code = code.replace(old_rot_calc, new_rot_calc)
    print("Updated robust rotationDeg calculation!")
else:
    print("Warning: old_rot_calc not found")

with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'w', encoding='utf-8') as f:
    f.write(code)

print("BuildingManager.java updated successfully!")
