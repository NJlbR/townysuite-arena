import re
from collections import Counter
from generate_all_fullsized import gen_bank, gen_hospital, gen_barracks, gen_library, gen_watchtower, gen_sun_pyramid, schems

# 1. Update buildings.yml
yml_lines = [
    "# ========================================================",
    "# TownyArchitecture Blueprints Database",
    "# Full-Sized RP-Ready Buildings (Spacious 14x14, 14x28, 28x28 footprints)",
    "# Minimal interior elements for player-customized RP decorating!",
    "# ========================================================",
    "blueprints:"
]

for k, (blks, wx, hy, lz, name, name_ru, icon, req_lvl, is_wonder, cw, cl, dim_h, buffs, pcolor, desc) in schems.items():
    counts = Counter(b[3] for b in blks)
    yml_lines.append(f"  {k}:")
    yml_lines.append(f'    name: "{name}"')
    yml_lines.append(f'    name-ru: "{name_ru}"')
    yml_lines.append(f'    description: "{desc}"')
    yml_lines.append(f'    icon: "{icon}"')
    yml_lines.append(f"    required-skill-level: {req_lvl}")
    yml_lines.append(f"    is-world-wonder: {'true' if is_wonder else 'false'}")
    yml_lines.append("    chunk-footprint:")
    yml_lines.append(f"      width-chunks: {cw}")
    yml_lines.append(f"      length-chunks: {cl}")
    yml_lines.append("    dimensions:")
    yml_lines.append(f"      height-y: {hy}")
    yml_lines.append("    resources:")
    for mat, cnt in counts.items():
        yml_lines.append(f"      {mat}: {cnt}")
    yml_lines.append("    buffs:")
    for bk, bv in buffs.items():
        if isinstance(bv, bool):
            yml_lines.append(f"      {bk}: {'true' if bv else 'false'}")
        else:
            yml_lines.append(f"      {bk}: {bv}")
    yml_lines.append(f'    particle-color: "{pcolor}"')

with open("tmp/minecraft-build-v2/src/main/resources/buildings.yml", "w", encoding="utf-8") as f:
    f.write("\n".join(yml_lines) + "\n")

print("Updated buildings.yml successfully!")

# 2. Generate Java methods for SchematicManager.java
def blocks_to_java(method_name, blueprint_id, wx, hy, lz, blocks):
    lines = []
    lines.append(f"    public BuildingSchematic {method_name}() {{")
    lines.append("        List<SchematicBlock> blocks = new ArrayList<>();")
    
    # Sort blocks by layer (dy), then x, then z
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

# Replace in SchematicManager.java
with open("tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/SchematicManager.java", "r", encoding="utf-8") as f:
    code = f.read()

# Replace all generators starting from generateBankSchematic
start_sig = "public BuildingSchematic generateBankSchematic"
if start_sig not in code:
    start_sig = "BuildingSchematic generateBankSchematic"
start_idx = code.find(start_sig)

# Find the end of class before loadFromYaml or closing brace
end_sig = "public BuildingSchematic loadFromYaml"
if end_sig in code:
    end_idx = code.find(end_sig)
else:
    end_idx = code.rfind("}")

new_java_code = "\n\n".join(java_methods) + "\n\n"

code = code[:start_idx] + new_java_code + code[end_idx:]

with open("tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/SchematicManager.java", "w", encoding="utf-8") as f:
    f.write(code)

print("Updated SchematicManager.java successfully!")
