import re

with open('tmp/minecraft-build/src/main/java/com/towny/architecture/gui/BuildsMenuGui.java', 'r', encoding='utf-8') as f:
    code = f.read()

# Let's just hardcode the fallback to include the unicode characters, so EVEN IF they don't delete the config, it works!
new_fallback = 'this.title = ChatColor.translateAlternateColorCodes(\'&\', plugin.getConfig().getString("gui.title", "&f\\uE000\\uE001\\uE002&fЧертежи и постройки"));'

code = code.replace(
    'this.title = ChatColor.translateAlternateColorCodes(\'&\', plugin.getConfig().getString("gui.title", "&8Чертежи и постройки"));',
    new_fallback
)

with open('tmp/minecraft-build/src/main/java/com/towny/architecture/gui/BuildsMenuGui.java', 'w', encoding='utf-8') as f:
    f.write(code)

print("Title fallback fixed")
