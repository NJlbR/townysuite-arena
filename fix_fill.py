import re

with open('tmp/minecraft-build/src/main/java/com/towny/architecture/gui/BuildsMenuGui.java', 'r', encoding='utf-8') as f:
    code = f.read()

# I messed up the replacement. Let's fix the block manually.
bad_block = """        if (plugin.getConfig().getBoolean("gui.fill-empty-slots", true)) {
            int size = plugin.getConfig().getInt("gui.size", 54);
        boolean fillEmpty = plugin.getConfig().getBoolean("gui.fill-empty-slots", true);
        for (int i = 0; i < size; i++) {
                if (i < 9 || i >= 45 || i % 9 == 0 || i % 9 == 8) {
                    inv.setItem(i, borderPane);
                }
            }
            inv.setItem(0, cornerPane);
            inv.setItem(8, cornerPane);
            inv.setItem(45, cornerPane);
            inv.setItem(53, cornerPane);
        }"""

good_block = """        if (plugin.getConfig().getBoolean("gui.fill-empty-slots", true)) {
            int size = plugin.getConfig().getInt("gui.size", 54);
            for (int i = 0; i < size; i++) {
                if (i < 9 || i >= size - 9 || i % 9 == 0 || i % 9 == 8) {
                    inv.setItem(i, borderPane);
                }
            }
            inv.setItem(0, cornerPane);
            inv.setItem(8, cornerPane);
            inv.setItem(size - 9, cornerPane);
            inv.setItem(size - 1, cornerPane);
        }"""

code = code.replace(bad_block, good_block)

with open('tmp/minecraft-build/src/main/java/com/towny/architecture/gui/BuildsMenuGui.java', 'w', encoding='utf-8') as f:
    f.write(code)

print("Fixed fill-empty-slots")
