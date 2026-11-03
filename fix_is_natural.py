with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'r', encoding='utf-8') as f:
    code = f.read()

natural_method = """
    public static boolean isNaturalTerrainMaterial(Material mat) {
        if (mat == null) return false;
        String name = mat.name();
        return name.contains("GRASS") || name.contains("DIRT") || name.contains("STONE") || 
               name.contains("GRAVEL") || name.contains("SAND") || name.contains("WATER") || 
               name.contains("LAVA") || name.contains("LEAVES") || name.contains("LOG") || 
               name.contains("WOOD") || name.contains("SNOW") || name.contains("ICE");
    }
"""

idx_last_brace = code.rfind('}')
code = code[:idx_last_brace] + natural_method + "\n}\n"

with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'w', encoding='utf-8') as f:
    f.write(code)

print("Added isNaturalTerrainMaterial to BuildingManager.java")
