with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update the long Action Bar message
old_msg = 'new TextComponent("§e[Чертёж] Строительство ведётся послойно! Текущий слой: §6" +\n                                         (building.getCurrentLayer() + 1) + "§e. Завершите его перед переходом к следующему!")'
new_msg = 'new TextComponent("§e[!] Стройте послойно! Слой: §6" + (building.getCurrentLayer() + 1) + "§e. Завершите его!")'

if old_msg in code:
    code = code.replace(old_msg, new_msg)
    print("Replaced Action Bar message (format 1)")
else:
    # try alternate formatting
    import re
    code = re.sub(
        r'new TextComponent\("§e\[Чертёж\] Строительство ведётся послойно! Текущий слой: §6"\s*\+\s*\(building\.getCurrentLayer\(\)\s*\+\s*1\)\s*\+\s*"§e\. Завершите его перед переходом к следующему!"\)',
        r'new TextComponent("§e[!] Стройте послойно! Слой: §6" + (building.getCurrentLayer() + 1) + "§e. Завершите его!")',
        code
    )
    print("Replaced Action Bar message (format regex)")

# 2. Add TerrainFlatnessResult class and checkFootprintFlatness method before startBuilding
target_anchor = "public ActiveBuilding startBuilding(Player player, BuildingBlueprint bp) {"
flatness_code = """public static class TerrainFlatnessResult {
        public final boolean isFlat;
        public final int minGroundY;
        public final int maxGroundY;
        public final int suggestedGroundY;
        public final int difference;

        public TerrainFlatnessResult(boolean isFlat, int minGroundY, int maxGroundY, int suggestedGroundY, int difference) {
            this.isFlat = isFlat;
            this.minGroundY = minGroundY;
            this.maxGroundY = maxGroundY;
            this.suggestedGroundY = suggestedGroundY;
            this.difference = difference;
        }
    }

    public TerrainFlatnessResult checkFootprintFlatness(World world, int plotMinX, int plotMinZ, int plotWidth, int plotLength, int maxAllowedDiff) {
        int minGround = Integer.MAX_VALUE;
        int maxGround = Integer.MIN_VALUE;
        Map<Integer, Integer> heightFreq = new HashMap<>();

        for (int x = plotMinX; x < plotMinX + plotWidth; x += 2) {
            for (int z = plotMinZ; z < plotMinZ + plotLength; z += 2) {
                int highestY = world.getHighestBlockYAt(x, z, HeightMap.MOTION_BLOCKING_NO_LEAVES);
                int checkY = Math.min(highestY, 130);
                while (checkY >= Math.max(50, world.getMinHeight())) {
                    Material mat = world.getBlockAt(x, checkY, z).getType();
                    if (isNaturalTerrainMaterial(mat)) {
                        break;
                    }
                    checkY--;
                }
                if (checkY >= 50) {
                    if (checkY < minGround) minGround = checkY;
                    if (checkY > maxGround) maxGround = checkY;
                    heightFreq.put(checkY, heightFreq.getOrDefault(checkY, 0) + 1);
                }
            }
        }

        if (minGround == Integer.MAX_VALUE) {
            return new TerrainFlatnessResult(true, 64, 64, 65, 0);
        }

        int mostCommon = minGround;
        int maxCount = 0;
        for (Map.Entry<Integer, Integer> entry : heightFreq.entrySet()) {
            if (entry.getValue() > maxCount) {
                maxCount = entry.getValue();
                mostCommon = entry.getKey();
            }
        }

        int diff = maxGround - minGround;
        boolean isFlat = diff <= maxAllowedDiff;
        return new TerrainFlatnessResult(isFlat, minGround, maxGround, mostCommon + 1, diff);
    }

    public ActiveBuilding startBuilding(Player player, BuildingBlueprint bp) {"""

code = code.replace(target_anchor, flatness_code, 1)

# 3. Add Flat plot check in startBuilding before creating fresh ActiveBuilding
fresh_anchor = "// CASE 3: FRESH START FROM GROUND FOUNDATION"
flat_check_snippet = """// Check flat ground requirement for fresh plots so no blocks are buried underground
        if (!isFullyConstructed && !isPartiallyConstructed) {
            if (plugin.getConfig().getBoolean("settings.require-flat-plot", true)) {
                int maxDiff = plugin.getConfig().getInt("settings.max-allowed-height-diff", 1);
                TerrainFlatnessResult flatness = checkFootprintFlatness(world, minChunkX * 16, minChunkZ * 16, plotWidth, plotLength, maxDiff);
                if (!flatness.isFlat) {
                    player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                            plugin.getMsg("prefix") + "&c[!] Строительная площадка не выровнена!"));
                    player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                            plugin.getMsg("prefix") + "&eРазница высот рельефа на участке: &6" + flatness.difference + " бл. &e(от Y=&f" + flatness.minGroundY + " &eдо Y=&f" + flatness.maxGroundY + "&e)"));
                    player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                            plugin.getMsg("prefix") + "&aРекомендация: &eРазровняйте поверхность площадки (на уровень &fY=" + (flatness.suggestedGroundY - 1) + "&e или любой желаемый уровень Y)."));
                    player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                            plugin.getMsg("prefix") + "&7(Ровная площадка гарантирует, что все блоки чертежа будут видны на поверхности)."));
                    return null;
                }
            }
        }

        // CASE 3: FRESH START FROM GROUND FOUNDATION"""

code = code.replace(fresh_anchor, flat_check_snippet, 1)

with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'w', encoding='utf-8') as f:
    f.write(code)

print("BuildingManager.java successfully updated!")
