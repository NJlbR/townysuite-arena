with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find start index around line 563
start_idx = -1
for i, l in enumerate(lines):
    if 'int minChunkX = Integer.MAX_VALUE;' in l:
        start_idx = i - 1
        break

end_idx = -1
for i in range(start_idx, len(lines)):
    if 'int rotationDeg = 0;' in lines[i] or 'int originZ =' in lines[i]:
        # let's find where originZ is
        pass
    if 'int originZ =' in lines[i]:
        end_idx = i + 1
        break

print(f"Replacing lines {start_idx} to {end_idx}")
print("Original section:")
for i in range(start_idx, end_idx):
    print(lines[i], end='')

new_snippet = [
    "        World world = player.getWorld();\n",
    "        int minChunkX = Integer.MAX_VALUE;\n",
    "        int maxChunkX = Integer.MIN_VALUE;\n",
    "        int minChunkZ = Integer.MAX_VALUE;\n",
    "        int maxChunkZ = Integer.MIN_VALUE;\n",
    "        for (ChunkCoord cc : assignedChunks) {\n",
    "            if (cc.getX() < minChunkX) minChunkX = cc.getX();\n",
    "            if (cc.getX() > maxChunkX) maxChunkX = cc.getX();\n",
    "            if (cc.getZ() < minChunkZ) minChunkZ = cc.getZ();\n",
    "            if (cc.getZ() > maxChunkZ) maxChunkZ = cc.getZ();\n",
    "        }\n",
    "        int spanX = (maxChunkX - minChunkX + 1);\n",
    "        int spanZ = (maxChunkZ - minChunkZ + 1);\n",
    "\n",
    "        // 1. Calculate natural terrain ground level (never roof!)\n",
    "        int terrainGroundY = calculateTerrainGroundY(world, assignedChunks);\n",
    "        if (terrainGroundY < 50) {\n",
    "            player.sendMessage(ChatColor.translateAlternateColorCodes('&',\n",
    "                    plugin.getMsg(\"prefix\") + \"&c[!] Защита от бункеров: Постройка не может быть заложена под землей (Y < 50)! Все здания должны возводиться на поверхности мира.\"));\n",
    "            return null;\n",
    "        }\n",
    "\n",
    "        BuildingSchematic schem = plugin.getSchematicManager().getSchematic(bp.getId());\n",
    "\n",
    "        int rotationDeg = 0;\n",
    "        if (bp.getChunkWidth() != bp.getChunkLength()) {\n",
    "            if (spanX == bp.getChunkLength() && spanZ == bp.getChunkWidth()) {\n",
    "                rotationDeg = 90;\n",
    "            }\n",
    "        }\n",
    "\n",
    "        ExistingStageAlignment alignment = null;\n",
    "        if (schem != null) {\n",
    "            alignment = detectExistingConstruction(schem, world, assignedChunks);\n",
    "        }\n",
    "\n",
    "        int schemW = schem != null ? schem.getWidthX() : (bp.getChunkWidth() * 16);\n",
    "        int schemL = schem != null ? schem.getLengthZ() : (bp.getChunkLength() * 16);\n",
    "        int effectiveW = (rotationDeg == 90 || rotationDeg == 270) ? schemL : schemW;\n",
    "        int effectiveL = (rotationDeg == 90 || rotationDeg == 270) ? schemW : schemL;\n",
    "\n",
    "        int totalPlotWidthPx = spanX * 16;\n",
    "        int totalPlotLengthPx = spanZ * 16;\n",
    "\n",
    "        int originX = minChunkX * 16 + Math.max(0, (totalPlotWidthPx - effectiveW) / 2);\n",
    "        int originY = terrainGroundY;\n",
    "        int originZ = minChunkZ * 16 + Math.max(0, (totalPlotLengthPx - effectiveL) / 2);\n"
]

lines[start_idx:end_idx] = new_snippet

with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Updated BuildingManager.java rotation successfully!")
