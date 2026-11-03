import sys

with open('tmp/minecraft-build/src/main/java/com/towny/architecture/command/BuildCommand.java', 'r', encoding='utf-8') as f:
    content = f.read()

target = """            case "resetxp": {
                if (!player.hasPermission("townyarchitecture.admin") && !player.isOp()) {
                    player.sendMessage(ChatColor.RED + "Недостаточно прав!");
                    return true;
                }
                plugin.getArchitectManager().resetStats(player);
                break;
            }"""

replacement = """            case "resetxp": {
                if (!player.hasPermission("townyarchitecture.admin") && !player.isOp()) {
                    player.sendMessage(ChatColor.RED + "Недостаточно прав!");
                    return true;
                }
                plugin.getArchitectManager().resetStats(player);
                break;
            }
            case "setlevel": {
                if (!player.hasPermission("townyarchitecture.admin") && !player.isOp()) {
                    player.sendMessage(ChatColor.RED + "Недостаточно прав!");
                    return true;
                }
                if (args.length < 2) {
                    player.sendMessage(ChatColor.RED + "Использование: /build setlevel <уровень>");
                    return true;
                }
                try {
                    int level = Integer.parseInt(args[1]);
                    plugin.getArchitectManager().setLevel(player, level);
                    player.sendMessage(ChatColor.GREEN + "Ваш уровень Архитектора установлен на " + level);
                } catch (NumberFormatException e) {
                    player.sendMessage(ChatColor.RED + "Неверный уровень!");
                }
                break;
            }"""

if target in content:
    with open('tmp/minecraft-build/src/main/java/com/towny/architecture/command/BuildCommand.java', 'w', encoding='utf-8') as f:
        f.write(content.replace(target, replacement))
    print("Patched setlevel successfully.")
else:
    print("Target content not found!")
