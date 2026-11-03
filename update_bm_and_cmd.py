with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'r', encoding='utf-8') as f:
    b_code = f.read()

# Update material matching in handleBlockPlaced
old_mat_check = """            if (sb.getMaterial() != mat) {
                // Wrong block placed!
                try {
                    player.spigot().sendMessage(ChatMessageType.ACTION_BAR, 
                            new TextComponent("§c✖ Ошибка: Здесь по чертежу требуется §b" + RussianTranslator.getMaterialRu(sb.getMaterial())));
                } catch (Exception ignored) {}
                player.playSound(loc, Sound.BLOCK_NOTE_BLOCK_BASS, 0.7f, 0.5f);
                return false;
            }"""

new_mat_check = """            if (!isMaterialMatch(mat, sb.getMaterial())) {
                // Wrong block placed!
                try {
                    player.spigot().sendMessage(ChatMessageType.ACTION_BAR, 
                            new TextComponent("§c✖ Ошибка: Здесь по чертежу требуется §b" + RussianTranslator.getMaterialRu(sb.getMaterial())));
                } catch (Exception ignored) {}
                player.playSound(loc, Sound.BLOCK_NOTE_BLOCK_BASS, 0.7f, 0.5f);
                return false;
            }"""

b_code = b_code.replace(old_mat_check, new_mat_check)

# Update actionbar in handleBlockPlaced
old_ab = """            try {
                player.spigot().sendMessage(ChatMessageType.ACTION_BAR, 
                        new TextComponent("§a✔ +" + RussianTranslator.getShortMaterialRu(mat) + " §8(Слой " + (building.getCurrentLayer() + 1) + ") §8| §6Прогресс: §a" + percent + "%"));
            } catch (Exception ignored) {}"""

new_ab = """            try {
                if (schem != null) {
                    int cLayer = building.getCurrentLayer();
                    List<SchematicBlock> curLayerBlocks = schem.getBlocksAtLayer(cLayer);
                    int layerTotal = curLayerBlocks.size();
                    int layerPlaced = countCompletedBlocksInLayer(building, schem, cLayer);
                    int layerRem = Math.max(0, layerTotal - layerPlaced);

                    player.spigot().sendMessage(ChatMessageType.ACTION_BAR, 
                            new TextComponent("§a✔ +" + RussianTranslator.getShortMaterialRu(mat) + 
                                    " §8| §fСлой " + (cLayer + 1) + ": §e" + layerPlaced + "/" + layerTotal + 
                                    (layerRem > 0 ? " §8(Осталось: §c" + layerRem + "§8)" : " §a✔") + 
                                    " §8| §6Всего: §a" + percent + "%"));
                } else {
                    player.spigot().sendMessage(ChatMessageType.ACTION_BAR, 
                            new TextComponent("§a✔ +" + RussianTranslator.getShortMaterialRu(mat) + " §8(Слой " + (building.getCurrentLayer() + 1) + ") §8| §6Прогресс: §a" + percent + "%"));
                }
            } catch (Exception ignored) {}"""

b_code = b_code.replace(old_ab, new_ab)

# Add helper methods in BuildingManager.java
helper_methods_add = """
    public int countCompletedBlocksInLayer(ActiveBuilding bld, BuildingSchematic schem, int layerY) {
        if (bld == null || schem == null) return 0;
        int count = 0;
        for (SchematicBlock sb : schem.getBlocksAtLayer(layerY)) {
            if (bld.isBlockCompleted(sb.getDx(), sb.getDy(), sb.getDz())) {
                count++;
            }
        }
        return count;
    }

    public List<SchematicBlock> getMissingBlocksInLayer(ActiveBuilding bld, BuildingSchematic schem, int layerY) {
        if (bld == null || schem == null) return Collections.emptyList();
        List<SchematicBlock> missing = new ArrayList<>();
        for (SchematicBlock sb : schem.getBlocksAtLayer(layerY)) {
            if (!bld.isBlockCompleted(sb.getDx(), sb.getDy(), sb.getDz())) {
                missing.add(sb);
            }
        }
        return missing;
    }
"""

idx_last_brace = b_code.rfind('}')
b_code = b_code[:idx_last_brace] + helper_methods_add + "\n}\n"

with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'w', encoding='utf-8') as f:
    f.write(b_code)

print("Updated BuildingManager.java successfully!")

# Now update BuildCommand.java to add 'check' and enhance 'info'
with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/command/BuildCommand.java', 'r', encoding='utf-8') as f:
    c_code = f.read()

old_info_block = """            case "info":
            case "progress":
            case "status": {"""

new_info_block = """            case "check":
            case "remaining":
            case "layer":
            case "info":
            case "progress":
            case "status": {"""

c_code = c_code.replace(old_info_block, new_info_block)

old_info_total = """                BuildingSchematic schem = plugin.getSchematicManager().getSchematic(building.getBlueprintId());
                int totalBlocks = (schem != null) ? schem.getTotalBlockCount() : building.getTotalRequiredBlocks();
                player.sendMessage(ChatColor.DARK_AQUA + "Общий прогресс: " + ChatColor.GREEN + building.getProgressPercent() + "% " +
                        ChatColor.GRAY + "(" + building.getCompletedBlockCount() + "/" + totalBlocks + " блоков на своих местах)");"""

new_info_total = """                BuildingSchematic schem = plugin.getSchematicManager().getSchematic(building.getBlueprintId());
                int totalBlocks = (schem != null) ? schem.getTotalBlockCount() : building.getTotalRequiredBlocks();
                player.sendMessage(ChatColor.DARK_AQUA + "Общий прогресс: " + ChatColor.GREEN + building.getProgressPercent() + "% " +
                        ChatColor.GRAY + "(" + building.getCompletedBlockCount() + "/" + totalBlocks + " блоков на своих местах)");

                if (schem != null && building.getStatus() == ActiveBuilding.Status.CONSTRUCTING) {
                    int cLayer = building.getCurrentLayer();
                    List<SchematicBlock> missing = plugin.getBuildingManager().getMissingBlocksInLayer(building, schem, cLayer);
                    int layerTotal = schem.getBlocksAtLayer(cLayer).size();
                    int layerPlaced = layerTotal - missing.size();

                    player.sendMessage(ChatColor.AQUA + "Текущий этап: " + ChatColor.YELLOW + "Слой " + (cLayer + 1) + 
                            ChatColor.WHITE + " (" + layerPlaced + "/" + layerTotal + " блоков установлено)");

                    if (!missing.isEmpty()) {
                        player.sendMessage(ChatColor.GOLD + "Осталось установить на Слое " + (cLayer + 1) + ":");
                        Map<Material, Integer> missingMatCounts = new LinkedHashMap<>();
                        for (SchematicBlock sb : missing) {
                            missingMatCounts.put(sb.getMaterial(), missingMatCounts.getOrDefault(sb.getMaterial(), 0) + 1);
                        }
                        for (Map.Entry<Material, Integer> me : missingMatCounts.entrySet()) {
                            player.sendMessage(ChatColor.YELLOW + " • " + ChatColor.WHITE + RussianTranslator.getMaterialRu(me.getKey()) + 
                                    ": " + ChatColor.RED + me.getValue() + " шт.");
                        }

                        // Spawn beacon dust on missing block positions for easy spotting
                        World w = player.getWorld();
                        Particle.DustOptions guideDust = new Particle.DustOptions(Color.fromRGB(255, 120, 0), 2.0f);
                        for (int i = 0; i < Math.min(10, missing.size()); i++) {
                            SchematicBlock sb = missing.get(i);
                            int[] rPos = BuildingManager.rotateRelativeCoords(sb.getDx(), sb.getDz(), building.getRotationDeg(), schem.getWidthX(), schem.getLengthZ());
                            double bx = building.getOriginX() + rPos[0] + 0.5;
                            double by = building.getOriginY() + sb.getDy() + 0.5;
                            double bz = building.getOriginZ() + rPos[1] + 0.5;
                            for (double dy = 0; dy <= 4.0; dy += 0.5) {
                                player.spawnParticle(Particle.valueOf("DUST"), bx, by + dy, bz, 1, 0, 0, 0, 0, guideDust);
                            }
                        }
                        player.sendMessage(ChatColor.GRAY + "(Местоположение недостроенных блоков подсвечено оранжевыми частицами)");
                    }
                }"""

c_code = c_code.replace(old_info_total, new_info_total)

with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/command/BuildCommand.java', 'w', encoding='utf-8') as f:
    f.write(c_code)

print("Updated BuildCommand.java successfully!")
