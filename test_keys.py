import re

with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'r', encoding='utf-8') as f:
    code = f.read()

idx = code.find("matchedBlockKeys.add")
print(code[idx-50:idx+50])
