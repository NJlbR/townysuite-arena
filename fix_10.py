import re

with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace("if (totalMatched > 10 && totalMatched > maxMatchedBlocks)", "if (totalMatched > 0 && totalMatched > maxMatchedBlocks)")

with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'w', encoding='utf-8') as f:
    f.write(code)
print("Replaced 10 with 0")
