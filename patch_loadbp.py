import sys

with open('tmp/minecraft-build/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'r', encoding='utf-8') as f:
    content = f.read()

target = """            BuildingBlueprint blueprint = new BuildingBlueprint(
                    key, name, nameRu, description, icon,
                    requiredLevel, isWonder, chunkWidth, chunkLength, heightY,
                    resources, buffs
            );"""

replacement = """            String pColor = section.getString("particle-color", "#00FF00");
            BuildingBlueprint blueprint = new BuildingBlueprint(
                    key, name, nameRu, description, icon,
                    requiredLevel, isWonder, chunkWidth, chunkLength, heightY,
                    resources, buffs, pColor
            );"""

if target in content:
    with open('tmp/minecraft-build/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'w', encoding='utf-8') as f:
        f.write(content.replace(target, replacement))
    print("Patched loadBlueprints successfully.")
else:
    print("Target content not found!")
