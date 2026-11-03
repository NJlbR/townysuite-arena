import sys

with open('tmp/minecraft-build/src/main/java/com/towny/architecture/TownyArchitecturePlugin.java', 'r', encoding='utf-8') as f:
    content = f.read()

target = """    @EventHandler(priority = EventPriority.HIGHEST)
    public void onPlayerCommandPreprocess(PlayerCommandPreprocessEvent event) {
        String msg = event.getMessage().trim().toLowerCase();"""

replacement = """    @EventHandler(priority = EventPriority.HIGHEST)
    public void onPlayerCommandPreprocess(PlayerCommandPreprocessEvent event) {
        String msg = event.getMessage().trim().toLowerCase();
        org.bukkit.entity.Player player = event.getPlayer();"""

if target in content:
    content = content.replace(target, replacement)
    
with open('tmp/minecraft-build/src/main/java/com/towny/architecture/TownyArchitecturePlugin.java', 'w', encoding='utf-8') as f:
    f.write(content)

with open('tmp/minecraft-build/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("plugin.getBuildingHudManager().removeHologram(bld.getInstanceId());", "// plugin.getBuildingHudManager().removeHologram(bld.getInstanceId());")

with open('tmp/minecraft-build/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'w', encoding='utf-8') as f:
    f.write(content)
