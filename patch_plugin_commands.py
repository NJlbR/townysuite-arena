import sys

with open('tmp/minecraft-build/src/main/java/com/towny/architecture/TownyArchitecturePlugin.java', 'r', encoding='utf-8') as f:
    content = f.read()

# I'll just find the exact string indices and slice it out
import re
content = re.sub(r'    @EventHandler\n    public void onPlayerCommandPreprocess\(org\.bukkit\.event\.player\.PlayerCommandPreprocessEvent event\).*?        if \(!nearBank\) {\n                event\.setCancelled\(true\);\n                player\.sendMessage\(org\.bukkit\.ChatColor\.RED \+ "Финансовые операции доступны только в здании Банка \(радиус 5 чанков\) или на Home-чанке города!"\);\n            }\n        }\n    }', '', content, flags=re.DOTALL)

target = """    @EventHandler(priority = EventPriority.HIGHEST)
    public void onPlayerCommandPreprocess(PlayerCommandPreprocessEvent event) {
        String msg = event.getMessage().trim().toLowerCase();
        
        if (msg.equals("/plot set build") || msg.equals("/plot set building") || """

replacement = """    @EventHandler(priority = EventPriority.HIGHEST)
    public void onPlayerCommandPreprocess(PlayerCommandPreprocessEvent event) {
        String msg = event.getMessage().trim().toLowerCase();
        Player player = event.getPlayer();

        if (msg.startsWith("/plot set bank")) {
            event.setCancelled(true);
            player.sendMessage(org.bukkit.ChatColor.RED + "[!] Ванильные банки Towny отключены. Вместо этого постройте здание Банка через /builds!");
            return;
        }

        if (msg.startsWith("/t deposit") || msg.startsWith("/town deposit") || 
            msg.startsWith("/t withdraw") || msg.startsWith("/town withdraw")) {
            
            String townName = townyHook.getPlayerTownName(player);
            if (townName != null) {
                org.bukkit.Location loc = player.getLocation();
                if (townyHook.isLocationInPlayerTown(loc, player)) {
                    boolean isHomeBlock = townyHook.isLocationTownHomeBlock(loc);
                    if (!isHomeBlock) {
                        boolean nearBank = false;
                        com.towny.architecture.model.ChunkCoord pCoord = com.towny.architecture.model.ChunkCoord.fromLocation(loc);
                        
                        for (com.towny.architecture.model.ActiveBuilding bld : buildingManager.getActiveBuildings()) {
                            if (bld.getTownName().equalsIgnoreCase(townName) && 
                                bld.getBlueprintId().equalsIgnoreCase("bank") && 
                                bld.getStatus() == com.towny.architecture.model.ActiveBuilding.Status.ACTIVE) {
                                
                                for (com.towny.architecture.model.ChunkCoord c : bld.getAssignedChunks()) {
                                    if (Math.abs(c.getX() - pCoord.getX()) <= 5 && Math.abs(c.getZ() - pCoord.getZ()) <= 5) {
                                        nearBank = true;
                                        break;
                                    }
                                }
                            }
                            if (nearBank) break;
                        }

                        if (!nearBank) {
                            event.setCancelled(true);
                            player.sendMessage(org.bukkit.ChatColor.RED + "Финансовые операции доступны только в здании Банка (радиус 5 чанков) или на Home-чанке города!");
                            return;
                        }
                    }
                } else {
                    event.setCancelled(true);
                    player.sendMessage(org.bukkit.ChatColor.RED + "Вы можете использовать банк только на территории своего города!");
                    return;
                }
            }
        }
        
        if (msg.equals("/plot set build") || msg.equals("/plot set building") || """

if target in content:
    with open('tmp/minecraft-build/src/main/java/com/towny/architecture/TownyArchitecturePlugin.java', 'w', encoding='utf-8') as f:
        f.write(content.replace(target, replacement))
    print("Patched TownyArchitecturePlugin.java successfully.")
else:
    print("Target content not found!")
