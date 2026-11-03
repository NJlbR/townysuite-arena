import sys

with open('tmp/minecraft-build/src/main/java/com/towny/architecture/command/BuildCommand.java', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('tagPlotAsBuild(loc, "Участок");', 'tagPlotAsBuild(loc, "Стройплощадка");')

with open('tmp/minecraft-build/src/main/java/com/towny/architecture/command/BuildCommand.java', 'w', encoding='utf-8') as f:
    f.write(content)
