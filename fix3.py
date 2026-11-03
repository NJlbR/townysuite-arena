import sys

with open('tmp/minecraft-build/src/main/java/com/towny/architecture/TownyArchitecturePlugin.java', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("Player player = event.getPlayer();\n            String town = townyHook.getPlayerTown(player);", "String town = townyHook.getPlayerTown(player);")

with open('tmp/minecraft-build/src/main/java/com/towny/architecture/TownyArchitecturePlugin.java', 'w', encoding='utf-8') as f:
    f.write(content)
