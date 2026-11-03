with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/command/BuildCommand.java', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Console support
old_console = """        if (!(sender instanceof Player)) {
            sender.sendMessage("Команда доступна только игрокам в игре!");
            return true;
        }"""

new_console = """        if (!(sender instanceof Player)) {
            if (args.length > 0 && (args[0].equalsIgnoreCase("audit") || args[0].equalsIgnoreCase("monitor") || args[0].equalsIgnoreCase("verify") || args[0].equalsIgnoreCase("sync"))) {
                plugin.getBuildingManager().performWatchdogAudit(sender, true);
                return true;
            }
            if (args.length > 0 && args[0].equalsIgnoreCase("reload")) {
                plugin.reloadPluginConfig();
                sender.sendMessage("Конфигурация TownyArchitecture успешно перезагружена!");
                return true;
            }
            sender.sendMessage("Команда доступна только игрокам в игре!");
            return true;
        }"""

assert old_console in content, "old_console not found"
content = content.replace(old_console, new_console, 1)

# 2. Add audit case
target_case = "            case \"reload\": {"
new_case = """            case "audit":
            case "monitor":
            case "verify":
            case "sync": {
                player.sendMessage(ChatColor.YELLOW + "Запуск аудита и синхронизации построек...");
                plugin.getBuildingManager().performWatchdogAudit(player, true);
                player.playSound(player.getLocation(), Sound.BLOCK_NOTE_BLOCK_BELL, 1.0f, 1.2f);
                break;
            }

            case "reload": {"""

assert target_case in content, "target_case not found"
content = content.replace(target_case, new_case, 1)

# 3. Add to tab complete
old_tab = 'List<String> list = new ArrayList<>(Arrays.asList("gui", "stats", "info", "plot", "rotate", "turn", "repair", "highlight", "borders", "effects"));'
new_tab = 'List<String> list = new ArrayList<>(Arrays.asList("gui", "stats", "info", "check", "plot", "rotate", "turn", "repair", "highlight", "borders", "effects", "audit", "monitor"));'

assert old_tab in content, "old_tab not found"
content = content.replace(old_tab, new_tab, 1)

with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/command/BuildCommand.java', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated BuildCommand.java successfully!")
