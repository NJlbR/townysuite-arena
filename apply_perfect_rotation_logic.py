with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update initial rotationDeg calculation in startBuilding
old_rot_init = """        int rotationDeg = 0;
        if (bp.getChunkWidth() != bp.getChunkLength()) {
            if (spanX > spanZ && bp.getChunkWidth() < bp.getChunkLength()) {
                rotationDeg = 90;
            } else if (spanX < spanZ && bp.getChunkWidth() > bp.getChunkLength()) {
                rotationDeg = 90;
            } else if (spanX == bp.getChunkLength() && spanZ == bp.getChunkWidth()) {
                rotationDeg = 90;
            }
        }"""

new_rot_init = """        int rotationDeg = 0;
        float normYaw = (player.getLocation().getYaw() % 360 + 360) % 360;
        if (bp.getChunkWidth() != bp.getChunkLength()) {
            if (spanX > spanZ) {
                // Horizontal 2x1 plot: must be 90° or 270°
                rotationDeg = (normYaw >= 45 && normYaw < 135) ? 90 : 270;
            } else {
                // Vertical 1x2 plot: must be 0° or 180°
                rotationDeg = (normYaw >= 135 && normYaw < 225) ? 0 : 180;
            }
        } else {
            // Square 1x1 or 2x2: align with facing quadrant
            if (normYaw >= 45 && normYaw < 135) rotationDeg = 90;
            else if (normYaw >= 135 && normYaw < 225) rotationDeg = 180;
            else if (normYaw >= 225 && normYaw < 315) rotationDeg = 270;
            else rotationDeg = 0;
        }"""

if old_rot_init in code:
    code = code.replace(old_rot_init, new_rot_init)
    print("Updated initial rotation calculation with yaw & plot geometry!")
else:
    print("Warning: old_rot_init not found")

# 2. Update rotateActiveBuilding to preserve plot aspect ratio
old_rotate_impl = """        int currentRot = building.getRotationDeg();
        int newRot = (currentRot + 90) % 360;

        int minCX = Integer.MAX_VALUE, maxCX = Integer.MIN_VALUE;"""

new_rotate_impl = """        int currentRot = building.getRotationDeg();
        int minCX = Integer.MAX_VALUE, maxCX = Integer.MIN_VALUE;
        int minCZ = Integer.MAX_VALUE, maxCZ = Integer.MIN_VALUE;
        for (ChunkCoord cc : building.getAssignedChunks()) {
            minCX = Math.min(minCX, cc.getX());
            maxCX = Math.max(maxCX, cc.getX());
            minCZ = Math.min(minCZ, cc.getZ());
            maxCZ = Math.max(maxCZ, cc.getZ());
        }
        int totalWidthPx = (maxCX - minCX + 1) * 16;
        int totalLengthPx = (maxCZ - minCZ + 1) * 16;

        int newRot;
        if (bp.getChunkWidth() != bp.getChunkLength()) {
            // Rectangular building: preserve plot footprint (horizontal: 90 <-> 270, vertical: 0 <-> 180)
            if (totalWidthPx > totalLengthPx) {
                newRot = (currentRot == 90) ? 270 : 90;
            } else {
                newRot = (currentRot == 0) ? 180 : 0;
            }
        } else {
            // Square building: full 360 rotation
            newRot = (currentRot + 90) % 360;
        }"""

# Find rotateActiveBuilding start and replace up to totalWidthPx
idx = code.find('public boolean rotateActiveBuilding')
if idx != -1:
    idx2 = code.find('int schemW = schem != null', idx)
    if idx2 != -1:
        prefix = code[:idx]
        method_header = code[idx:code.find('int currentRot =', idx)]
        suffix = code[idx2:]
        code = prefix + method_header + new_rotate_impl + "\n\n        " + suffix
        print("Updated rotateActiveBuilding method cleanly!")

with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'w', encoding='utf-8') as f:
    f.write(code)

# 3. Update BuildsMenuGui.java
with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/gui/BuildsMenuGui.java', 'r', encoding='utf-8') as f:
    gui_code = f.read()

old_gui_find = """ChunkCoord pChunk = ChunkCoord.fromLocation(player.getLocation());
                    Set<ChunkCoord> freeArea = plugin.getBuildingManager().findFreePlotArea(
                            townName, player.getWorld().getName(), bp.getChunkWidth(), bp.getChunkLength(), pChunk
                    );"""

new_gui_find = """ChunkCoord pChunk = ChunkCoord.fromLocation(player.getLocation());
                    Set<ChunkCoord> freeArea = plugin.getBuildingManager().findFreePlotArea(
                            townName, player.getWorld().getName(), bp.getChunkWidth(), bp.getChunkLength(), pChunk, player.getLocation().getYaw()
                    );"""

if old_gui_find in gui_code:
    gui_code = gui_code.replace(old_gui_find, new_gui_find)
    with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/gui/BuildsMenuGui.java', 'w', encoding='utf-8') as f:
        f.write(gui_code)
    print("Updated BuildsMenuGui.java with player yaw!")
else:
    print("Warning: old_gui_find not found")

print("All files updated successfully!")
