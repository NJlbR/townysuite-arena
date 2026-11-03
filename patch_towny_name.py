import sys

with open('tmp/minecraft-build/src/main/java/com/towny/architecture/hook/TownyHook.java', 'r', encoding='utf-8') as f:
    content = f.read()

target = """                try {
                    java.lang.reflect.Method saveMethod = townBlock.getClass().getMethod("save");
                    saveMethod.invoke(townBlock);
                } catch (Exception ignored) {}"""

replacement = """                try {
                    java.lang.reflect.Method setNameMethod = townBlock.getClass().getMethod("setName", String.class);
                    setNameMethod.invoke(townBlock, name);
                } catch (Exception ignored) {}
                
                try {
                    java.lang.reflect.Method saveMethod = townBlock.getClass().getMethod("save");
                    saveMethod.invoke(townBlock);
                } catch (Exception ignored) {}"""

if target in content:
    with open('tmp/minecraft-build/src/main/java/com/towny/architecture/hook/TownyHook.java', 'w', encoding='utf-8') as f:
        f.write(content.replace(target, replacement))
    print("Patched towny name successfully.")
else:
    print("Target content not found!")
