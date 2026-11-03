from generate_all_fullsized import gen_bank, gen_hospital, gen_barracks, gen_library, gen_watchtower, gen_sun_pyramid

header = """package com.towny.architecture.manager;

import com.towny.architecture.TownyArchitecturePlugin;
import com.towny.architecture.model.BuildingSchematic;
import com.towny.architecture.model.SchematicBlock;
import org.bukkit.Material;
import org.bukkit.configuration.file.FileConfiguration;
import org.bukkit.configuration.file.YamlConfiguration;

import java.io.File;
import java.util.*;

public class SchematicManager {

    private final TownyArchitecturePlugin plugin;
    private final Map<String, BuildingSchematic> schematics = new HashMap<>();

    public SchematicManager(TownyArchitecturePlugin plugin) {
        this.plugin = plugin;
        loadSchematics();
    }

    public void loadSchematics() {
        schematics.clear();
        File folder = new File(plugin.getDataFolder(), "schematics");
        if (!folder.exists()) {
            folder.mkdirs();
        }

        // Generate and register built-in full-sized schematics
        registerDefaultSchematic(generateBankSchematic());
        registerDefaultSchematic(generateHospitalSchematic());
        registerDefaultSchematic(generateBarracksSchematic());
        registerDefaultSchematic(generateLibrarySchematic());
        registerDefaultSchematic(generateWatchtowerSchematic());
        registerDefaultSchematic(generateWonderColossusSchematic());

        // Aliases for compatibility
        schematics.put("hospital", generateHospitalSchematic());
        schematics.put("infirmary", generateHospitalSchematic());
        schematics.put("sun_pyramid", generateWonderColossusSchematic());

        // Also check if user has custom .yml schematics in the schematics folder
        File[] customFiles = folder.listFiles((dir, name) -> name.endsWith(".yml"));
        if (customFiles != null) {
            for (File file : customFiles) {
                try {
                    BuildingSchematic custom = loadFromYaml(file);
                    if (custom != null) {
                        schematics.put(custom.getBlueprintId().toLowerCase(), custom);
                        plugin.getLogger().info("Загружена кастомная схема: " + custom.getBlueprintId());
                    }
                } catch (Exception e) {
                    plugin.getLogger().warning("Ошибка загрузки схемы из " + file.getName() + ": " + e.getMessage());
                }
            }
        }
    }

    private void registerDefaultSchematic(BuildingSchematic s) {
        schematics.put(s.getBlueprintId().toLowerCase(), s);
    }

    public BuildingSchematic getSchematic(String blueprintId) {
        if (blueprintId == null) return null;
        String key = blueprintId.toLowerCase();
        if (key.equals("hospital")) key = "hospital";
        if (key.equals("infirmary")) key = "hospital";
        if (key.equals("sun_pyramid")) key = "sun_pyramid";
        return schematics.get(key);
    }

    public BuildingSchematic loadFromYaml(File file) {
        try {
            FileConfiguration cfg = YamlConfiguration.loadConfiguration(file);
            String bpId = cfg.getString("blueprint-id", file.getName().replace(".yml", ""));
            int width = cfg.getInt("width-x", 16);
            int height = cfg.getInt("height-y", 10);
            int length = cfg.getInt("length-z", 16);
            List<String> blockList = cfg.getStringList("blocks");
            List<SchematicBlock> blocks = new ArrayList<>();
            for (String str : blockList) {
                String[] parts = str.split(",");
                if (parts.length >= 4) {
                    int x = Integer.parseInt(parts[0].trim());
                    int y = Integer.parseInt(parts[1].trim());
                    int z = Integer.parseInt(parts[2].trim());
                    Material mat = Material.valueOf(parts[3].trim().toUpperCase());
                    blocks.add(new SchematicBlock(x, y, z, mat));
                }
            }
            return new BuildingSchematic(bpId, width, height, length, blocks);
        } catch (Exception e) {
            plugin.getLogger().warning("Не удалось распарсить файл схемы " + file.getName() + ": " + e.getMessage());
            return null;
        }
    }
"""

def blocks_to_java(method_name, blueprint_id, wx, hy, lz, blocks):
    lines = []
    lines.append(f"    public BuildingSchematic {method_name}() {{")
    lines.append("        List<SchematicBlock> blocks = new ArrayList<>();")
    
    sorted_blocks = sorted(blocks, key=lambda b: (b[1], b[0], b[2]))
    
    current_layer = -1
    for x, y, z, mat in sorted_blocks:
        if y != current_layer:
            current_layer = y
            lines.append(f"        // Layer {current_layer}")
        lines.append(f"        blocks.add(new SchematicBlock({x}, {y}, {z}, Material.{mat}));")
        
    lines.append(f'        return new BuildingSchematic("{blueprint_id}", {wx}, {hy}, {lz}, blocks);')
    lines.append("    }")
    return "\n".join(lines)

java_methods = [
    blocks_to_java("generateBankSchematic", "bank", 16, 6, 16, gen_bank()),
    blocks_to_java("generateHospitalSchematic", "hospital", 16, 6, 16, gen_hospital()),
    blocks_to_java("generateBarracksSchematic", "barracks", 16, 5, 32, gen_barracks()),
    blocks_to_java("generateLibrarySchematic", "library", 16, 5, 16, gen_library()),
    blocks_to_java("generateWatchtowerSchematic", "watchtower", 16, 11, 16, gen_watchtower()),
    blocks_to_java("generateWonderColossusSchematic", "sun_pyramid", 32, 7, 32, gen_sun_pyramid()),
]

full_code = header + "\n" + "\n\n".join(java_methods) + "\n}\n"

with open("tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/SchematicManager.java", "w", encoding="utf-8") as f:
    f.write(full_code)

print("Rewrote SchematicManager.java successfully!")
