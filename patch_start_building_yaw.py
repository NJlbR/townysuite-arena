with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'r', encoding='utf-8') as f:
    code = f.read()

old_call = """        Set<ChunkCoord> assignedChunks = findFreePlotArea(
                townName,
                player.getWorld().getName(),
                bp.getChunkWidth(),
                bp.getChunkLength(),
                playerChunk
        );"""

new_call = """        Set<ChunkCoord> assignedChunks = findFreePlotArea(
                townName,
                player.getWorld().getName(),
                bp.getChunkWidth(),
                bp.getChunkLength(),
                playerChunk,
                player.getLocation().getYaw()
        );"""

if old_call in code:
    code = code.replace(old_call, new_call)
    print("Updated findFreePlotArea call to pass player yaw!")
else:
    print("Warning: old_call not found")

# Add rotate hint after building started
old_hint = 'plugin.getMsg("prefix") + "&b✦ 3D-Чертеж проецируется на строительной площадке (Слой 1)."));'
new_hint = """plugin.getMsg("prefix") + "&b✦ 3D-Чертеж проецируется на строительной площадке (Слой 1)."));
                p.sendMessage(ChatColor.translateAlternateColorCodes('&',
                        plugin.getMsg("prefix") + "&7✦ Совет: Вы можете повернуть чертеж командой &f/build rotate&7 (0°/90°/180°/270°)."));"""

if old_hint in code:
    code = code.replace(old_hint, new_hint)
    print("Added rotate hint message!")
else:
    print("Warning: old_hint not found")

with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'w', encoding='utf-8') as f:
    f.write(code)

print("BuildingManager.java patched successfully!")
