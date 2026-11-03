import sys

with open('tmp/minecraft-build/src/main/java/com/towny/architecture/TownyArchitecturePlugin.java', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("Player player = event.getPlayer();\n\n        if (msg.startsWith(\"/plot set bank\")) {", "if (msg.startsWith(\"/plot set bank\")) {")
with open('tmp/minecraft-build/src/main/java/com/towny/architecture/TownyArchitecturePlugin.java', 'w', encoding='utf-8') as f:
    f.write(content)

with open('tmp/minecraft-build/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("activeBuildings.remove(bld.getId());", "activeBuildings.remove(bld.getInstanceId());")
content = content.replace("plugin.getBuildingHudManager().removeHologram(bld.getId());", "plugin.getBuildingHudManager().removeHologram(bld.getInstanceId());")

with open('tmp/minecraft-build/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'w', encoding='utf-8') as f:
    f.write(content)
