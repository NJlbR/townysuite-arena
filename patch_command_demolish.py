import sys

with open('tmp/minecraft-build/src/main/java/com/towny/architecture/command/BuildCommand.java', 'r', encoding='utf-8') as f:
    content = f.read()

target = """            case "repair": {
                ActiveBuilding building = plugin.getBuildingManager().getBuildingAt(player.getLocation());"""

replacement = """            case "demolish": {
                if (!plugin.getTownyHook().isPlayerMayorOrAssistant(player)) {
                    player.sendMessage(ChatColor.RED + "Только мэр или помощник могут сносить здания!");
                    return true;
                }
                String town = plugin.getTownyHook().getPlayerTownName(player);
                if (town == null) return true;
                
                ChunkCoord cc = ChunkCoord.fromLocation(player.getLocation());
                ActiveBuilding bld = plugin.getBuildingManager().getBuildingOccupyingChunk(cc);
                if (bld == null || !bld.getTownName().equalsIgnoreCase(town)) {
                    player.sendMessage(ChatColor.RED + "Вы не стоите на территории здания вашего города.");
                    return true;
                }

                if (args.length >= 2 && args[1].equalsIgnoreCase("confirm")) {
                    plugin.getBuildingManager().demolishBuilding(bld);
                    player.sendMessage(ChatColor.GREEN + "Здание успешно снесено из базы данных. Физические блоки остались нетронутыми.");
                } else {
                    player.sendMessage(ChatColor.YELLOW + "Вы уверены, что хотите снести постройку «" + bld.getBlueprintId() + "»?");
                    player.sendMessage(ChatColor.YELLOW + "Она будет удалена из системы (лимиты обновятся), но физические блоки останутся.");
                    player.sendMessage(ChatColor.RED + "Для подтверждения введите: " + ChatColor.WHITE + "/build demolish confirm");
                }
                break;
            }
            case "repair": {
                ActiveBuilding building = plugin.getBuildingManager().getBuildingAt(player.getLocation());"""

target2 = """            if (sender.hasPermission("townyarchitecture.admin") || sender.isOp()) {
                list.add("reload");"""

replacement2 = """            if (plugin.getTownyHook().isPlayerMayorOrAssistant((Player) sender)) {
                list.add("demolish");
            }
            if (sender.hasPermission("townyarchitecture.admin") || sender.isOp()) {
                list.add("reload");"""


if target in content and target2 in content:
    with open('tmp/minecraft-build/src/main/java/com/towny/architecture/command/BuildCommand.java', 'w', encoding='utf-8') as f:
        f.write(content.replace(target, replacement).replace(target2, replacement2))
    print("Patched BuildCommand demolish successfully.")
else:
    print("Target content not found!")
