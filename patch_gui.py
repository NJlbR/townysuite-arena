import re

with open('tmp/minecraft-build/src/main/java/com/towny/architecture/gui/BuildsMenuGui.java', 'r', encoding='utf-8') as f:
    code = f.read()

# Patch title and size
code = code.replace(
    'private final String title = ChatColor.DARK_BLUE + "✦ " + ChatColor.GOLD + "Архитектура Города" + ChatColor.DARK_BLUE + " ✦";',
    'private String title;'
)

code = code.replace(
    'public BuildsMenuGui(TownyArchitecturePlugin plugin) {\n        this.plugin = plugin;\n    }',
    '''public BuildsMenuGui(TownyArchitecturePlugin plugin) {
        this.plugin = plugin;
        this.title = ChatColor.translateAlternateColorCodes('&', plugin.getConfig().getString("gui.title", "&8Чертежи и постройки"));
    }'''
)

code = code.replace(
    'Inventory inv = Bukkit.createInventory(null, 54, title);',
    'Inventory inv = Bukkit.createInventory(null, plugin.getConfig().getInt("gui.size", 54), title);'
)

# Patch fill-empty-slots
code = code.replace(
    'for (int i = 0; i < 54; i++) {',
    'int size = plugin.getConfig().getInt("gui.size", 54);\n        boolean fillEmpty = plugin.getConfig().getBoolean("gui.fill-empty-slots", true);\n        for (int i = 0; i < size; i++) {'
)

code = code.replace(
    'ItemStack borderPane = createGlassPane(Material.CYAN_STAINED_GLASS_PANE, " ");\n            inv.setItem(i, borderPane);',
    'if (fillEmpty) {\n                ItemStack borderPane = createGlassPane(Material.CYAN_STAINED_GLASS_PANE, " ");\n                inv.setItem(i, borderPane);\n            }'
)

code = code.replace(
    'if (slot < 0 || slot >= 54) return;',
    'if (slot < 0 || slot >= plugin.getConfig().getInt("gui.size", 54)) return;'
)

with open('tmp/minecraft-build/src/main/java/com/towny/architecture/gui/BuildsMenuGui.java', 'w', encoding='utf-8') as f:
    f.write(code)

print("GUI patched")
