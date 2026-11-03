import re

with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/command/BuildCommand.java', 'r', encoding='utf-8') as f:
    s = f.read()

# 1. Add cases to switch (sub)
switch_target = '''            case "effects":
            case "effect": {
                boolean enabled = plugin.getBuildingHudManager().toggleEffectParticles(player);
                player.playSound(player.getLocation(), Sound.UI_BUTTON_CLICK, 0.7f, 1.2f);
                player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                        plugin.getMsg("prefix") + (enabled ? "&aПодсветка зон эффектов &2ВКЛЮЧЕНА&a (видна только вам)!" : "&cПодсветка зон эффектов &4ВЫКЛЮЧЕНА&c.")));
                break;
            }'''

new_cases = '''            case "effects":
            case "effect": {
                boolean enabled = plugin.getBuildingHudManager().toggleEffectParticles(player);
                player.playSound(player.getLocation(), Sound.UI_BUTTON_CLICK, 0.7f, 1.2f);
                player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                        plugin.getMsg("prefix") + (enabled ? "&aПодсветка зон эффектов &2ВКЛЮЧЕНА&a (видна только вам)!" : "&cПодсветка зон эффектов &4ВЫКЛЮЧЕНА&c.")));
                break;
            }

            case "war": {
                handleWarCommand(player, args);
                break;
            }

            case "shield":
            case "townhall":
            case "hall": {
                handleShieldCommand(player, args);
                break;
            }

            case "damage": {
                handleDamageCommand(player, args);
                break;
            }'''

assert switch_target in s, 'switch_target not found'
s = s.replace(switch_target, new_cases, 1)

# 2. Add handler methods before renderProgressBar
handlers = '''
    private void handleWarCommand(Player player, String[] args) {
        String town = plugin.getTownyHook().getPlayerTownName(player);
        if (args.length >= 2 && args[1].equalsIgnoreCase("damage")) {
            String[] dmgArgs = new String[args.length - 1];
            dmgArgs[0] = "damage";
            for (int i = 2; i < args.length; i++) dmgArgs[i - 1] = args[i];
            handleDamageCommand(player, dmgArgs);
            return;
        }

        if (args.length >= 2 && args[1].equalsIgnoreCase("global")) {
            boolean cur = plugin.getTownHallShieldManager().isGlobalWarActive();
            boolean next = !cur;
            if (args.length >= 3) {
                if (args[2].equalsIgnoreCase("on") || args[2].equalsIgnoreCase("true")) next = true;
                else if (args[2].equalsIgnoreCase("off") || args[2].equalsIgnoreCase("false")) next = false;
            }
            plugin.getTownHallShieldManager().setGlobalWarActive(next);
            player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                    plugin.getMsg("prefix") + "&6[Симуляция] Глобальный режим войны для всех городов: " + 
                    (next ? "&c&lВКЛЮЧЕН (АКТИВЕН)" : "&a&lВЫКЛЮЧЕН (МИРНОЕ ВРЕМЯ)")));
            return;
        }

        if (args.length >= 2 && (args[1].equalsIgnoreCase("status") || args[1].equalsIgnoreCase("info"))) {
            handleShieldCommand(player, args);
            return;
        }

        if (town == null) {
            player.sendMessage(ChatColor.RED + "Вы должны состоять в городе (или используйте /build war global on|off)!");
            return;
        }

        boolean next = !plugin.getTownHallShieldManager().isWarActive(town);
        if (args.length >= 2) {
            if (args[1].equalsIgnoreCase("on") || args[1].equalsIgnoreCase("true")) next = true;
            else if (args[1].equalsIgnoreCase("off") || args[1].equalsIgnoreCase("false")) next = false;
        }

        plugin.getTownHallShieldManager().setTownWarActive(town, next);
        player.playSound(player.getLocation(), next ? Sound.EVENT_RAID_HORN : Sound.UI_TOAST_CHALLENGE_COMPLETE, 1.0f, 1.0f);
        player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                plugin.getMsg("prefix") + "&6[Симуляция Войны] Режим войны для города «&e" + town + "&6»: " + 
                (next ? "&c&lАКТИВЕН &7(Осадный урон наносится, щит Мэрии активен)" : "&a&lМИРНОЕ ВРЕМЯ &7(Мэрия и щит неуязвимы к осаде)")));
    }

    private void handleShieldCommand(Player player, String[] args) {
        String town = plugin.getTownyHook().getPlayerTownName(player);
        if (args.length >= 2 && !args[1].equalsIgnoreCase("status") && !args[1].equalsIgnoreCase("info")) {
            town = args[1];
        }
        if (town == null) {
            player.sendMessage(ChatColor.RED + "Вы должны состоять в городе для просмотра Щита Мэрии!");
            return;
        }

        ActiveBuilding th = plugin.getTownHallShieldManager().getTownHall(town);
        int wallCount = plugin.getTownHallShieldManager().getWallCount(town);
        double maxShield = plugin.getTownHallShieldManager().getMaxShieldHp(town);
        double currentShield = plugin.getTownHallShieldManager().getShieldHp(town);
        double integrity = plugin.getTownHallShieldManager().getTownHallIntegrityPercent(town);
        boolean war = plugin.getTownHallShieldManager().isWarActive(town);

        player.sendMessage(ChatColor.GOLD + "══════ Оборона и Щит Мэрии: " + ChatColor.YELLOW + town + ChatColor.GOLD + " ══════");
        if (th != null) {
            String statusStr = th.getStatus() == ActiveBuilding.Status.ACTIVE ? ChatColor.GREEN + "Построена (2x2 чанка)" : ChatColor.YELLOW + "В процессе возведения (" + th.getProgressPercent() + "%)";
            player.sendMessage(ChatColor.WHITE + " • Здание Мэрии: " + statusStr);
            player.sendMessage(ChatColor.WHITE + " • Целостность конструкции: " + ChatColor.DARK_GRAY + "[" + 
                    renderProgressBar((int) integrity, 100, 10) + ChatColor.DARK_GRAY + "] " + ChatColor.GREEN + String.format("%.1f", integrity) + "%");
        } else {
            player.sendMessage(ChatColor.WHITE + " • Здание Мэрии: " + ChatColor.RED + "Не построена (утвердите чертеж Мэрии в /builds)");
        }

        player.sendMessage(ChatColor.WHITE + " • Городские Стены (2x1): " + ChatColor.AQUA + wallCount + " шт." + 
                ChatColor.GRAY + " (+" + String.format("%.0f", maxShield) + " HP к щиту)");

        if (maxShield > 0) {
            player.sendMessage(ChatColor.WHITE + " • Прочность Щита: " + ChatColor.DARK_GRAY + "[" + 
                    renderProgressBar((int) currentShield, (int) maxShield, 10) + ChatColor.DARK_GRAY + "] " + 
                    ChatColor.YELLOW + String.format("%.1f", currentShield) + ChatColor.GRAY + "/" + ChatColor.YELLOW + String.format("%.1f", maxShield) + " HP");
        } else {
            player.sendMessage(ChatColor.WHITE + " • Прочность Щита: " + ChatColor.RED + "0.0 HP " + ChatColor.GRAY + "(постройте Городские Стены 2x1 для усиления щита!)");
        }

        player.sendMessage(ChatColor.WHITE + " • Состояние безопасности: " + (war ? ChatColor.RED + "[В РЕЖИМЕ ВОЙНЫ]" : ChatColor.GREEN + "[МИРНОЕ ВРЕМЯ - ЗАЩИТА]"));
        player.sendMessage(ChatColor.DARK_GRAY + "───────────────────────────────────");
        player.sendMessage(ChatColor.YELLOW + "Бонусы Мэрии: " + ChatColor.WHITE + "Дипломатический центр, Герой Деревни, Щит крепости.");
        player.sendMessage(ChatColor.GRAY + "Тестирование симуляции: " + ChatColor.AQUA + "/build war [on|off] " + ChatColor.GRAY + "| " + ChatColor.AQUA + "/build damage <урон>");
        player.sendMessage(ChatColor.GOLD + "════════════════════════════════════════");
    }

    private void handleDamageCommand(Player player, String[] args) {
        String town = plugin.getTownyHook().getPlayerTownName(player);
        if (town == null) {
            player.sendMessage(ChatColor.RED + "Вы должны состоять в городе для тестирования осадного урона!");
            return;
        }

        double amount = 50.0;
        if (args.length >= 2) {
            try {
                amount = Double.parseDouble(args[1]);
            } catch (NumberFormatException e) {
                player.sendMessage(ChatColor.RED + "Некорректная сумма урона: " + args[1]);
                return;
            }
        }

        com.towny.architecture.manager.TownHallShieldManager.DamageResult res = plugin.getTownHallShieldManager().simulateDamage(town, amount, player);
        player.sendMessage(ChatColor.translateAlternateColorCodes('&', plugin.getMsg("prefix") + res.message));
    }
'''

pb_target = '    private String renderProgressBar(int current, int max, int totalBars) {'
assert pb_target in s, 'pb_target not found'
s = s.replace(pb_target, handlers + '\n' + pb_target, 1)

# 3. Add to tab completions
tab_old = '''        if (args.length == 1) {
            List<String> list = new ArrayList<>(Arrays.asList("gui", "stats", "info", "check", "plot", "rotate", "turn", "repair", "highlight", "borders", "effects", "audit", "monitor"));'''

tab_new = '''        if (args.length == 1) {
            List<String> list = new ArrayList<>(Arrays.asList("gui", "stats", "info", "check", "plot", "rotate", "turn", "repair", "highlight", "borders", "effects", "war", "shield", "townhall", "damage", "audit", "monitor"));'''

assert tab_old in s, 'tab_old not found'
s = s.replace(tab_old, tab_new, 1)

tab_ext_old = '''        } else if (args.length == 2 && args[0].equalsIgnoreCase("setlevel")) {'''

tab_ext_new = '''        } else if (args.length == 2 && args[0].equalsIgnoreCase("war")) {
            return Arrays.asList("on", "off", "toggle", "status", "damage", "global");
        } else if (args.length == 2 && args[0].equalsIgnoreCase("damage")) {
            return Arrays.asList("25", "50", "100", "200", "500");
        } else if (args.length == 2 && args[0].equalsIgnoreCase("setlevel")) {'''

assert tab_ext_old in s, 'tab_ext_old not found'
s = s.replace(tab_ext_old, tab_ext_new, 1)

with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/command/BuildCommand.java', 'w', encoding='utf-8') as f:
    f.write(s)

print('Updated BuildCommand.java successfully!')
