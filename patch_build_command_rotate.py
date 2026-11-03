with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/command/BuildCommand.java', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Add rotate case in switch
target_case = """            case "reload": {"""
rotate_case = """            case "rotate":
            case "turn":
            case "rot": {
                ActiveBuilding bld = plugin.getBuildingManager().getBuildingAt(player.getLocation());
                if (bld == null) {
                    player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                            plugin.getMsg("prefix") + "&c[!] Вы должны стоять на строительном участке постройки для ее поворота!"));
                    return true;
                }
                boolean success = plugin.getBuildingManager().rotateActiveBuilding(player, bld);
                if (success) {
                    BuildingBlueprint bp = plugin.getBuildingManager().getBlueprint(bld.getBlueprintId());
                    String name = (bp != null) ? bp.getNameRu() : bld.getBlueprintId();
                    player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                            plugin.getMsg("prefix") + "&a[!] Голограмма постройки «&6" + name + 
                            "&a» успешно повернута на &e" + bld.getRotationDeg() + "°&a!"));
                    player.playSound(player.getLocation(), Sound.BLOCK_NOTE_BLOCK_BELL, 1.0f, 1.2f);
                }
                break;
            }
            case "reload": {"""

if target_case in code:
    code = code.replace(target_case, rotate_case)
    print("Added rotate case to BuildCommand!")
else:
    print("Error: target_case not found")

# 2. Add to tab completion
old_tab = 'Arrays.asList("gui", "stats", "info", "plot", "repair", "highlight", "borders", "effects")'
new_tab = 'Arrays.asList("gui", "stats", "info", "plot", "rotate", "turn", "repair", "highlight", "borders", "effects")'

if old_tab in code:
    code = code.replace(old_tab, new_tab)
    print("Added rotate and turn to tab completion!")
else:
    print("Warning: old_tab not found")

# 3. Update default command help message
old_help = 'player.sendMessage(ChatColor.YELLOW + "Команды: /builds (меню), /build stats (уровень), /plot set build, /build info, /build plot list, /build repair");'
new_help = 'player.sendMessage(ChatColor.YELLOW + "Команды: /builds (меню), /build rotate (поворот голограммы), /build stats, /plot set build, /build info, /build repair");'

if old_help in code:
    code = code.replace(old_help, new_help)
    print("Updated command help text!")
else:
    print("Warning: old_help not found")

with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/command/BuildCommand.java', 'w', encoding='utf-8') as f:
    f.write(code)

print("BuildCommand.java successfully patched!")
