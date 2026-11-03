import sys

with open('tmp/minecraft-build/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'r', encoding='utf-8') as f:
    content = f.read()

target1 = """                ConfigurationSection placedSec = item.getConfigurationSection("placed_materials");
                if (placedSec != null) {
                    for (String matKey : placedSec.getKeys(false)) {
                        Material m = Material.matchMaterial(matKey);
                        if (m != null) {
                            bld.setPlacedCount(m, placedSec.getInt(matKey, 0));
                        }
                    }
                }

                activeBuildings.put(instId, bld);"""

replacement1 = """                ConfigurationSection placedSec = item.getConfigurationSection("placed_materials");
                if (placedSec != null) {
                    for (String matKey : placedSec.getKeys(false)) {
                        Material m = Material.matchMaterial(matKey);
                        if (m != null) {
                            bld.setPlacedCount(m, placedSec.getInt(matKey, 0));
                        }
                    }
                }
                ConfigurationSection maxPlacedSec = item.getConfigurationSection("max_placed_materials");
                if (maxPlacedSec != null) {
                    for (String matKey : maxPlacedSec.getKeys(false)) {
                        Material m = Material.matchMaterial(matKey);
                        if (m != null) {
                            bld.setMaxPlacedCount(m, maxPlacedSec.getInt(matKey, 0));
                        }
                    }
                } else {
                    // Fallback for older saves
                    if (placedSec != null) {
                        for (String matKey : placedSec.getKeys(false)) {
                            Material m = Material.matchMaterial(matKey);
                            if (m != null) {
                                bld.setMaxPlacedCount(m, placedSec.getInt(matKey, 0));
                            }
                        }
                    }
                }

                activeBuildings.put(instId, bld);"""

target2 = """            for (Map.Entry<Material, Integer> pEntry : bld.getPlacedMaterials().entrySet()) {
                dataConfig.set(path + ".placed_materials." + pEntry.getKey().name(), pEntry.getValue());
            }"""

replacement2 = """            for (Map.Entry<Material, Integer> pEntry : bld.getPlacedMaterials().entrySet()) {
                dataConfig.set(path + ".placed_materials." + pEntry.getKey().name(), pEntry.getValue());
            }
            for (Map.Entry<Material, Integer> pEntry : bld.getRequiredMaterials().entrySet()) {
                int maxVal = bld.getMaxPlacedCount(pEntry.getKey());
                dataConfig.set(path + ".max_placed_materials." + pEntry.getKey().name(), maxVal);
            }"""

if target1 in content and target2 in content:
    content = content.replace(target1, replacement1).replace(target2, replacement2)
    with open('tmp/minecraft-build/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patched max_placed successfully.")
else:
    print("Target content not found!")
