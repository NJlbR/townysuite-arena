# 1. Update BuildingHudManager.java
with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingHudManager.java', 'r', encoding='utf-8') as f:
    c = f.read()

# Add imports
if 'import com.towny.architecture.model.BuildingSchematic;' not in c:
    c = c.replace('import com.towny.architecture.model.ActiveBuilding;', 'import com.towny.architecture.model.ActiveBuilding;\nimport com.towny.architecture.model.BuildingSchematic;\nimport com.towny.architecture.model.SchematicBlock;')

# Replace wm.isLiquid()
c = c.replace('wm.isLiquid()', '(wm == Material.WATER || wm == Material.LAVA)')

with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingHudManager.java', 'w', encoding='utf-8') as f:
    f.write(c)

# 2. Update HologramDisplayManager.java
with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/HologramDisplayManager.java', 'r', encoding='utf-8') as f:
    hc = f.read()

hc = hc.replace('worldMat.isLiquid()', '(worldMat == Material.WATER || worldMat == Material.LAVA)')
hc = hc.replace('currentWorldMat.isLiquid()', '(currentWorldMat == Material.WATER || currentWorldMat == Material.LAVA)')

with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/HologramDisplayManager.java', 'w', encoding='utf-8') as f:
    f.write(hc)

print("Fixed imports and liquid checks successfully!")
