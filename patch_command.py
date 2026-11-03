import sys

with open('tmp/minecraft-build/src/main/java/com/towny/architecture/command/BuildCommand.java', 'r', encoding='utf-8') as f:
    content = f.read()

target = """            case "reload": {
                if (!player.hasPermission("townyarchitecture.admin")) {"""

replacement = """            case "resetxp": {
                if (!player.hasPermission("townyarchitecture.admin") && !player.isOp()) {
                    player.sendMessage(ChatColor.RED + "Недостаточно прав!");
                    return true;
                }
                plugin.getArchitectManager().resetStats(player);
                break;
            }
            case "reload": {
                if (!player.hasPermission("townyarchitecture.admin")) {"""

if target in content:
    with open('tmp/minecraft-build/src/main/java/com/towny/architecture/command/BuildCommand.java', 'w', encoding='utf-8') as f:
        f.write(content.replace(target, replacement))
    print("Patched BuildCommand.java successfully.")
else:
    print("Target content not found!")
