with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/SchematicManager.java', 'r') as f:
    text = f.read()

idx = text.find('public BuildingSchematic generateTownHallSchematic()')
print("TownHall length from idx:", len(text[idx:]))
print(text[idx:idx+2500])

