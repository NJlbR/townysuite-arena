import re

with open('tmp/minecraft-build/src/main/java/com/towny/architecture/hook/TownyHook.java', 'r') as f:
    content = f.read()

# Fix getRank
content = content.replace("town.getRank(res).contains", "res.hasTownRank")
content = content.replace("boolean isAssistant = town.getRank(town.getResident(player)).contains(\"assistant\");", "boolean isAssistant = TownyAPI.getInstance().getResident(player).hasTownRank(\"assistant\");")
content = content.replace("boolean isBuilder = town.getRank(town.getResident(player)).contains(\"builder\");", "boolean isBuilder = TownyAPI.getInstance().getResident(player).hasTownRank(\"builder\");")

# Fix getTownBlock(String, int, int)
old_tb = "TownBlock tb = TownyAPI.getInstance().getTownBlock(chunk.getWorld().getName(), chunk.getX(), chunk.getZ());"
new_tb = "TownBlock tb = TownyAPI.getInstance().getTownBlock(new Location(chunk.getWorld(), chunk.getX() * 16, 0, chunk.getZ() * 16));"
content = content.replace(old_tb, new_tb)

with open('tmp/minecraft-build/src/main/java/com/towny/architecture/hook/TownyHook.java', 'w') as f:
    f.write(content)
