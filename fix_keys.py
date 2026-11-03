import re

with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace bx, by, bz with sb.getDx(), sb.getDy(), sb.getDz()
new_code = code.replace('matchedBlockKeys.add(bx + "," + by + "," + bz);', 'matchedBlockKeys.add(sb.getDx() + "," + sb.getDy() + "," + sb.getDz());')

with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'w', encoding='utf-8') as f:
    f.write(new_code)
print("Keys fixed")
