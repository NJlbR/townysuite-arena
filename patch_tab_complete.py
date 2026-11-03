import sys

with open('tmp/minecraft-build/src/main/java/com/towny/architecture/command/BuildCommand.java', 'r', encoding='utf-8') as f:
    content = f.read()

target = """            if (sender.hasPermission("townyarchitecture.admin")) {
                list.add("reload");
                list.add("wonder");
            }"""

replacement = """            if (sender.hasPermission("townyarchitecture.admin") || sender.isOp()) {
                list.add("reload");
                list.add("wonder");
                list.add("resetxp");
            }"""

if target in content:
    with open('tmp/minecraft-build/src/main/java/com/towny/architecture/command/BuildCommand.java', 'w', encoding='utf-8') as f:
        f.write(content.replace(target, replacement))
    print("Patched tab completion successfully.")
else:
    print("Target content not found!")
