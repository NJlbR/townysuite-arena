# 1. Fix flatness check in BuildingManager.java
with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'r', encoding='utf-8') as f:
    bm_code = f.read()

old_flatness = """        int diff = maxGround - minGround;
        boolean isFlat = diff <= maxAllowedDiff;
        return new TerrainFlatnessResult(isFlat, minGround, maxGround, mostCommon + 1, diff);"""

new_flatness = """        int diff = maxGround - minGround;
        // Allow up to 5 blocks variation for natural terrain micro-relief (prevent false positives on flat plots)
        boolean isFlat = diff <= Math.max(maxAllowedDiff, 5);
        return new TerrainFlatnessResult(isFlat, minGround, maxGround, mostCommon + 1, diff);"""

if old_flatness in bm_code:
    bm_code = bm_code.replace(old_flatness, new_flatness)
    with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'w', encoding='utf-8') as f:
        f.write(bm_code)
    print("Fixed flatness check in BuildingManager.java!")
else:
    print("Warning: old_flatness not found in BuildingManager.java")

# 2. Fix wireframes in BuildingHudManager.java
with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingHudManager.java', 'r', encoding='utf-8') as f:
    hud_code = f.read()

# Replace condition in renderParticles
old_cond = """                // A. Layer-by-layer Block Edge Highlighting (Cyan for Ghost Blocks, Red for Obstacles)
                // Always persistent: never disappears when blocks are placed or modified!
                if (!bld.isFullyBuilt() && showBorders) {
                    renderLayerBlockWireframes(player, pWorld, bld, pX, pY, pZ, ghostCyanDust, obstacleRedDust);
                }"""

new_cond = """                // A. Layer-by-layer Block Edge Highlighting (Cyan for Ghost Blocks, Red for Obstacles)
                // Always persistent whenever building is constructing or damaged
                if ((bld.getStatus() == ActiveBuilding.Status.CONSTRUCTING || bld.getStatus() == ActiveBuilding.Status.DAMAGED) && showBorders) {
                    renderLayerBlockWireframes(player, pWorld, bld, pX, pY, pZ, ghostCyanDust, obstacleRedDust);
                }"""

hud_code = hud_code.replace(old_cond, new_cond)

# Also increase view distance check in renderLayerBlockWireframes from 28.0 to 50.0
hud_code = hud_code.replace("Math.abs(wx - pX) > 28.0", "Math.abs(wx - pX) > 50.0")
hud_code = hud_code.replace("Math.abs(wz - pZ) > 28.0", "Math.abs(wz - pZ) > 50.0")

with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingHudManager.java', 'w', encoding='utf-8') as f:
    f.write(hud_code)

print("Fixed BuildingHudManager.java wireframes!")
