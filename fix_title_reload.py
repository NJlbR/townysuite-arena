import re

with open('tmp/minecraft-build/src/main/java/com/towny/architecture/gui/BuildsMenuGui.java', 'r', encoding='utf-8') as f:
    code = f.read()

# Remove this.title from constructor
code = code.replace(
    'this.title = ChatColor.translateAlternateColorCodes(\'&\', plugin.getConfig().getString("gui.title", "&8Чертежи и постройки"));',
    ''
)

# And in open(), calculate title
code = code.replace(
    'Inventory inv = Bukkit.createInventory(null, plugin.getConfig().getInt("gui.size", 54), title);',
    'this.title = ChatColor.translateAlternateColorCodes(\'&\', plugin.getConfig().getString("gui.title", "&8Чертежи и постройки"));\n        Inventory inv = Bukkit.createInventory(null, plugin.getConfig().getInt("gui.size", 54), title);'
)

with open('tmp/minecraft-build/src/main/java/com/towny/architecture/gui/BuildsMenuGui.java', 'w', encoding='utf-8') as f:
    f.write(code)

print("GUI title reloading fixed")
