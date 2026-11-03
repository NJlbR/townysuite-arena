with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'r', encoding='utf-8') as f:
    code = f.read()

idx1 = code.find('// 3. Wall and Roof air contact constraint: exterior walls and roof must touch air >= 50%')
idx2 = code.find('// Check flat ground requirement for fresh plots so no blocks are buried underground')

# Let's inspect the block between idx1 and idx2
print("Target start:")
print(code[idx1:idx1+300])

new_flow = """        // 2. Check flat ground requirement for fresh plots so no blocks are buried underground
        if (plugin.getConfig().getBoolean("settings.require-flat-plot", true)) {
            int maxDiff = plugin.getConfig().getInt("settings.max-allowed-height-diff", 1);
            TerrainFlatnessResult flatness = checkFootprintFlatness(world, minChunkX * 16, minChunkZ * 16, totalPlotWidthPx, totalPlotLengthPx, maxDiff);
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

        // 3. Wall and Roof air contact constraint: exterior walls and roof must touch air >= 50%
        if (schem != null && schem.getExteriorFaceCount() > 0) {
            double initialExposure = checkTerrainWallExposure(schem, world, originX, originY, originZ, rotationDeg);
            if (initialExposure < 50.0) {
                player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                        plugin.getMsg("prefix") + "&c[!] Ограничение планировки: Стены и крыша здания замурованы в ландшафт / защитную оболочку!"));
                player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                        plugin.getMsg("prefix") + "&cПо чертежу открытость стен и крыши воздуху составит лишь &e" + 
                        String.format("%.1f", initialExposure) + "% &c(требуется минимум 50%)."));
                player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                        plugin.getMsg("prefix") + "&cЗдания должны контактировать с воздухом (городская застройка), а не прятаться в бункерах или обстраиваться защитными оболочками снаружи!"));
                return null;
            }
        }

        Map<Material, Integer> req = (schem != null) ? schem.getTotalMaterials() : bp.getResources();
        String instanceId = "bld-" + bp.getId() + "-" + System.currentTimeMillis();
        ActiveBuilding building = new ActiveBuilding(
                instanceId,
                bp.getId(),
                townName,
                player.getUniqueId(),
                player.getWorld().getName(),
                assignedChunks,
                req,
                originX,
                originY,
                originZ
        );
        building.setRotationDeg(rotationDeg);
        building.setCurrentLayer(0);
        building.setStatus(ActiveBuilding.Status.CONSTRUCTING);

        activeBuildings.put(instanceId, building);
        saveData();

        for (ChunkCoord cc : assignedChunks) {
            Location sampleLoc = new Location(player.getWorld(), (cc.getX() << 4) + 8, 70, (cc.getZ() << 4) + 8);
            plugin.getTownyHook().tagPlotAsBuild(sampleLoc, "В процессе постройки: " + bp.getNameRu());
        }

        for (Player p : Bukkit.getOnlinePlayers()) {
            String pTown = plugin.getTownyHook().getPlayerTownName(p);
            if (pTown != null && pTown.equalsIgnoreCase(townName)) {
                p.sendMessage(ChatColor.translateAlternateColorCodes('&',
                        plugin.getMsg("prefix") + "&a[!] Мэр утвердил проект «&6" + bp.getNameRu() + 
                        "&a». Город приступает к строительству!"));
                p.sendMessage(ChatColor.translateAlternateColorCodes('&',
                        plugin.getMsg("prefix") + "&e✦ Начните установку блоков фундамента (&fСлой 1&e) по 3D-голограммам чертежа."));
                p.playSound(p.getLocation(), Sound.BLOCK_BEACON_ACTIVATE, 1.0f, 1.2f);
            }
        }

        plugin.getHologramDisplayManager().initHologramsForBuilding(building);
        return building;
    }"""

idx_end = code.find('return building;\n    }', idx1) + len('return building;\n    }')
code = code[:idx1] + new_flow + code[idx_end:]

with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'w', encoding='utf-8') as f:
    f.write(code)

print("Refactored startBuilding successfully!")
