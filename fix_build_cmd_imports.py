with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/command/BuildCommand.java', 'r', encoding='utf-8') as f:
    code = f.read()

import_target = "package com.towny.architecture.command;"
new_imports = """package com.towny.architecture.command;

import com.towny.architecture.model.SchematicBlock;
import com.towny.architecture.manager.BuildingManager;
import org.bukkit.World;
import org.bukkit.Particle;
import org.bukkit.Color;"""

code = code.replace(import_target, new_imports)

with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/command/BuildCommand.java', 'w', encoding='utf-8') as f:
    f.write(code)

print("Added imports to BuildCommand.java!")
