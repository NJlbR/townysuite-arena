with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/SchematicManager.java', 'r') as f:
    text = f.read()

# Let's inspect generateTownHallSchematic
idx = text.find('public BuildingSchematic generateTownHallSchematic()')
next_idx = text.find('public BuildingSchematic generateCityWallSchematic()')
print("=== TownHall code ===")
print(text[idx:next_idx])

