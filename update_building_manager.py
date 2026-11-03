with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add CommandSender import if missing
if 'import org.bukkit.command.CommandSender;' not in content:
    content = content.replace(
        "import org.bukkit.*;",
        "import org.bukkit.*;\nimport org.bukkit.command.CommandSender;"
    )

# 2. Define the new Watchdog implementation
old_integrity = """    public void performPeriodicIntegrityCheck() {
        double threshold = plugin.getConfig().getDouble("settings.buff-suspension-health-percent", 70.0);

        for (ActiveBuilding bld : activeBuildings.values()) {
            World world = Bukkit.getWorld(bld.getWorldName());
            if (world == null) continue;

            BuildingSchematic schem = plugin.getSchematicManager().getSchematic(bld.getBlueprintId());
            if (schem == null) continue;

            int total = schem.getTotalBlockCount();
            int intact = 0;
            Map<Material, Integer> currentCounts = new HashMap<>();

            for (SchematicBlock sb : schem.getBlocks()) {
                int wx = bld.getOriginX() + sb.getDx();
                int wy = bld.getOriginY() + sb.getDy();
                int wz = bld.getOriginZ() + sb.getDz();

                if (world.getBlockAt(wx, wy, wz).getType() == sb.getMaterial()) {
                    intact++;
                    bld.markBlockCompleted(sb.getDx(), sb.getDy(), sb.getDz());
                    currentCounts.put(sb.getMaterial(), currentCounts.getOrDefault(sb.getMaterial(), 0) + 1);
                } else {
                    bld.markBlockBroken(sb.getDx(), sb.getDy(), sb.getDz());
                    if (bld.getStatus() != ActiveBuilding.Status.CONSTRUCTING) {
                        plugin.getHologramDisplayManager().respawnHologramForMissingBlock(bld, sb.getDx(), sb.getDy(), sb.getDz(), sb.getMaterial());
                    }
                }
            }

            for (Map.Entry<Material, Integer> e : bld.getRequiredMaterials().entrySet()) {
                bld.setPlacedCount(e.getKey(), currentCounts.getOrDefault(e.getKey(), 0));
            }

            double health = (total > 0) ? ((double) intact / total) * 100.0 : 100.0;
            bld.setHealthPercent(health);

            double exposure = calculateWallExposurePercent(bld);

            if (bld.getStatus() == ActiveBuilding.Status.CONSTRUCTING) {
                if (bld.isFullyBuilt()) {
                    BuildingBlueprint bp = blueprints.get(bld.getBlueprintId());
                    completeBuilding(bld, bp, null);
                }
            } else {
                if (exposure < 50.0) {
                    if (bld.getStatus() == ActiveBuilding.Status.ACTIVE) {
                        bld.setStatus(ActiveBuilding.Status.ENTOMBED);
                        BuildingBlueprint bp = blueprints.get(bld.getBlueprintId());
                        String bpName = bp != null ? bp.getNameRu() : bld.getBlueprintId();
                        for (Player p : Bukkit.getOnlinePlayers()) {
                            String town = plugin.getTownyHook().getPlayerTownName(p);
                            if (town != null && town.equalsIgnoreCase(bld.getTownName())) {
                                p.sendMessage(ChatColor.translateAlternateColorCodes('&',
                                        plugin.getMsg("prefix") + "&c[!] Фасады постройки «&e" + bpName + 
                                        "&c» замурованы/засыпаны (< 50% открытости: &e" + String.format("%.1f", exposure) + 
                                        "%&c)! Баффы отключены до расчистки стен."));
                                p.playSound(p.getLocation(), Sound.BLOCK_ANVIL_LAND, 0.6f, 0.8f);
                            }
                        }
                    }
                } else if (bld.getStatus() == ActiveBuilding.Status.ENTOMBED) {
                    if (health >= threshold) {
                        bld.setStatus(ActiveBuilding.Status.ACTIVE);
                        BuildingBlueprint bp = blueprints.get(bld.getBlueprintId());
                        String bpName = bp != null ? bp.getNameRu() : bld.getBlueprintId();
                        for (Player p : Bukkit.getOnlinePlayers()) {
                            String town = plugin.getTownyHook().getPlayerTownName(p);
                            if (town != null && town.equalsIgnoreCase(bld.getTownName())) {
                                p.sendMessage(ChatColor.translateAlternateColorCodes('&',
                                        plugin.getMsg("prefix") + "&a[✔] Фасады постройки «&e" + bpName + 
                                        "&a» снова открыты (" + String.format("%.1f", exposure) + "% >= 50%)! Баффы города восстановлены."));
                                p.playSound(p.getLocation(), Sound.BLOCK_BEACON_ACTIVATE, 0.8f, 1.2f);
                            }
                        }
                    }
                } else if (health < threshold && bld.getStatus() == ActiveBuilding.Status.ACTIVE) {
                    bld.setStatus(ActiveBuilding.Status.DAMAGED);
                } else if (health >= 100.0 && bld.getStatus() == ActiveBuilding.Status.DAMAGED) {
                    bld.setStatus(ActiveBuilding.Status.ACTIVE);
                }
            }
            saveData();
        }
    }"""

new_integrity = """    public static class WatchdogAuditReport {
        public int totalBuildings = 0;
        public int constructingChecked = 0;
        public int activeChecked = 0;
        public int blocksReconciled = 0;
        public int layersAdvanced = 0;
        public int buildingsCompleted = 0;
        public int buildingsDamaged = 0;
        public int buildingsRestored = 0;
        public int hologramsHealed = 0;
        public long durationMs = 0;
    }

    /**
     * Regular watchdog monitoring & diagnostic audit:
     * - Scans constructing buildings, auto-reconciles placed blocks, advances layers, heals dead/missing holograms, and auto-completes finished buildings.
     * - Scans active buildings, calculates accurate rotated integrity, detects grief/damage, switches to DAMAGED with warning holograms.
     * - Detects repaired buildings and auto-restores them to ACTIVE with town buffs and fanfare.
     * - Checks exterior facade exposure to prevent buried bunkers (ENTOMBED).
     * - Commits validated state to disk, protecting against server crashes and desyncs.
     */
    public WatchdogAuditReport performWatchdogAudit(CommandSender feedbackRecipient, boolean verbose) {
        WatchdogAuditReport report = new WatchdogAuditReport();
        long startTime = System.currentTimeMillis();
        double threshold = plugin.getConfig().getDouble("settings.buff-suspension-health-percent", 70.0);
        report.totalBuildings = activeBuildings.size();

        for (ActiveBuilding bld : activeBuildings.values()) {
            World world = Bukkit.getWorld(bld.getWorldName());
            if (world == null) continue;

            BuildingSchematic schem = plugin.getSchematicManager().getSchematic(bld.getBlueprintId());
            if (schem == null) continue;

            int rot = bld.getRotationDeg();
            int wX = schem.getWidthX();
            int lZ = schem.getLengthZ();

            // Safety check: skip buildings whose chunks are not loaded during automated background runs to prevent TPS drops
            boolean anyChunkLoaded = false;
            if (bld.getAssignedChunks() != null && !bld.getAssignedChunks().isEmpty()) {
                for (ChunkCoord cc : bld.getAssignedChunks()) {
                    if (world.isChunkLoaded(cc.getX(), cc.getZ())) {
                        anyChunkLoaded = true;
                        break;
                    }
                }
            } else {
                anyChunkLoaded = world.isChunkLoaded(bld.getOriginX() >> 4, bld.getOriginZ() >> 4);
            }

            if (!anyChunkLoaded && feedbackRecipient == null) {
                continue;
            }

            BuildingBlueprint bp = blueprints.get(bld.getBlueprintId());
            String bpName = bp != null ? bp.getNameRu() : bld.getBlueprintId();

            // 1. Handling for CONSTRUCTING buildings
            if (bld.getStatus() == ActiveBuilding.Status.CONSTRUCTING) {
                report.constructingChecked++;

                // A. Auto-reconcile physical blocks up to current layer
                int currentLayer = bld.getCurrentLayer();
                for (int l = 0; l <= currentLayer && l <= schem.getMaxLayer(); l++) {
                    List<SchematicBlock> lBlocks = schem.getBlocksAtLayer(l);
                    if (lBlocks == null) continue;

                    for (SchematicBlock sb : lBlocks) {
                        int[] rPos = rotateRelativeCoords(sb.getDx(), sb.getDz(), rot, wX, lZ);
                        int wx = bld.getOriginX() + rPos[0];
                        int wy = bld.getOriginY() + sb.getDy();
                        int wz = bld.getOriginZ() + rPos[1];

                        if (wy < world.getMinHeight() || wy >= world.getMaxHeight()) continue;
                        Material wm = world.getBlockAt(wx, wy, wz).getType();

                        if (isMaterialMatch(wm, sb.getMaterial())) {
                            if (!bld.isBlockCompleted(sb.getDx(), sb.getDy(), sb.getDz())) {
                                bld.markBlockCompleted(sb.getDx(), sb.getDy(), sb.getDz());
                                bld.addPlacedBlock(sb.getMaterial());
                                report.blocksReconciled++;
                            }
                        } else {
                            if (bld.isBlockCompleted(sb.getDx(), sb.getDy(), sb.getDz())) {
                                bld.markBlockBroken(sb.getDx(), sb.getDy(), sb.getDz());
                                bld.removePlacedBlock(sb.getMaterial());
                            }
                        }
                    }
                }

                // B. Layer advance check
                boolean advanced = plugin.getHologramDisplayManager().checkAndAdvanceLayer(bld, schem, world);
                if (advanced) {
                    report.layersAdvanced++;
                }

                // C. Full completion check
                if (bld.isFullyBuilt()) {
                    completeBuilding(bld, bp, null);
                    report.buildingsCompleted++;
                } else {
                    // D. Hologram Self-Healing (re-spawns lost or despawned BlockDisplays)
                    int healed = plugin.getHologramDisplayManager().healOrRefreshLayerHolograms(bld);
                    report.hologramsHealed += healed;
                }
            } 
            // 2. Handling for ACTIVE, DAMAGED, and ENTOMBED buildings
            else {
                report.activeChecked++;
                int total = schem.getTotalBlockCount();
                int intact = 0;
                Map<Material, Integer> currentCounts = new HashMap<>();

                for (SchematicBlock sb : schem.getBlocks()) {
                    int[] rPos = rotateRelativeCoords(sb.getDx(), sb.getDz(), rot, wX, lZ);
                    int wx = bld.getOriginX() + rPos[0];
                    int wy = bld.getOriginY() + sb.getDy();
                    int wz = bld.getOriginZ() + rPos[1];

                    if (wy < world.getMinHeight() || wy >= world.getMaxHeight()) continue;
                    Material wm = world.getBlockAt(wx, wy, wz).getType();

                    if (isMaterialMatch(wm, sb.getMaterial())) {
                        intact++;
                        bld.markBlockCompleted(sb.getDx(), sb.getDy(), sb.getDz());
                        currentCounts.put(sb.getMaterial(), currentCounts.getOrDefault(sb.getMaterial(), 0) + 1);
                    } else {
                        bld.markBlockBroken(sb.getDx(), sb.getDy(), sb.getDz());
                        if (bld.getStatus() == ActiveBuilding.Status.DAMAGED) {
                            plugin.getHologramDisplayManager().respawnHologramForMissingBlock(bld, sb.getDx(), sb.getDy(), sb.getDz(), sb.getMaterial());
                        }
                    }
                }

                for (Map.Entry<Material, Integer> e : bld.getRequiredMaterials().entrySet()) {
                    bld.setPlacedCount(e.getKey(), currentCounts.getOrDefault(e.getKey(), 0));
                }

                double health = (total > 0) ? ((double) intact / total) * 100.0 : 100.0;
                bld.setHealthPercent(health);

                double exposure = calculateWallExposurePercent(bld);

                if (exposure < 50.0) {
                    if (bld.getStatus() == ActiveBuilding.Status.ACTIVE) {
                        bld.setStatus(ActiveBuilding.Status.ENTOMBED);
                        for (Player p : Bukkit.getOnlinePlayers()) {
                            String town = plugin.getTownyHook().getPlayerTownName(p);
                            if (town != null && town.equalsIgnoreCase(bld.getTownName())) {
                                p.sendMessage(ChatColor.translateAlternateColorCodes('&',
                                        plugin.getMsg("prefix") + "&c[!] Фасады постройки «&e" + bpName + 
                                        "&c» замурованы/засыпаны (< 50% открытости: &e" + String.format("%.1f", exposure) + 
                                        "%&c)! Баффы отключены до расчистки стен."));
                                p.playSound(p.getLocation(), Sound.BLOCK_ANVIL_LAND, 0.6f, 0.8f);
                            }
                        }
                    }
                } else if (bld.getStatus() == ActiveBuilding.Status.ENTOMBED) {
                    if (health >= threshold) {
                        bld.setStatus(ActiveBuilding.Status.ACTIVE);
                        for (Player p : Bukkit.getOnlinePlayers()) {
                            String town = plugin.getTownyHook().getPlayerTownName(p);
                            if (town != null && town.equalsIgnoreCase(bld.getTownName())) {
                                p.sendMessage(ChatColor.translateAlternateColorCodes('&',
                                        plugin.getMsg("prefix") + "&a[✔] Фасады постройки «&e" + bpName + 
                                        "&a» снова открыты (" + String.format("%.1f", exposure) + "% >= 50%)! Баффы города восстановлены."));
                                p.playSound(p.getLocation(), Sound.BLOCK_BEACON_ACTIVATE, 0.8f, 1.2f);
                            }
                        }
                    }
                } else if (health < threshold && bld.getStatus() == ActiveBuilding.Status.ACTIVE) {
                    bld.setStatus(ActiveBuilding.Status.DAMAGED);
                    report.buildingsDamaged++;
                    for (Player p : Bukkit.getOnlinePlayers()) {
                        String town = plugin.getTownyHook().getPlayerTownName(p);
                        if (town != null && town.equalsIgnoreCase(bld.getTownName())) {
                            p.sendMessage(ChatColor.translateAlternateColorCodes('&',
                                    plugin.getMsg("prefix") + "&c[⚠] Постройка «&e" + bpName + 
                                    "&c» повреждена (&e" + String.format("%.1f", health) + 
                                    "%&c < " + threshold + "%)! Баффы отключены до починки."));
                            p.playSound(p.getLocation(), Sound.BLOCK_ANVIL_LAND, 0.8f, 0.7f);
                        }
                    }
                } else if (health >= 100.0 && bld.getStatus() == ActiveBuilding.Status.DAMAGED) {
                    bld.setStatus(ActiveBuilding.Status.ACTIVE);
                    plugin.getHologramDisplayManager().clearHologramsForBuilding(bld.getInstanceId());
                    report.buildingsRestored++;
                    for (Player p : Bukkit.getOnlinePlayers()) {
                        String town = plugin.getTownyHook().getPlayerTownName(p);
                        if (town != null && town.equalsIgnoreCase(bld.getTownName())) {
                            p.sendMessage(ChatColor.translateAlternateColorCodes('&',
                                    plugin.getMsg("prefix") + "&a[✔] Постройка «&e" + bpName + 
                                    "&a» полностью восстановлена (&e100%&a)! Баффы города возобновлены."));
                            p.playSound(p.getLocation(), Sound.BLOCK_BEACON_ACTIVATE, 0.9f, 1.2f);
                        }
                    }
                }
            }
        }

        saveData();
        report.durationMs = System.currentTimeMillis() - startTime;

        if (feedbackRecipient != null) {
            feedbackRecipient.sendMessage(ChatColor.GOLD + "══════ Аудит и мониторинг построек ══════");
            feedbackRecipient.sendMessage(ChatColor.WHITE + " • Проверено построек: " + ChatColor.YELLOW + report.totalBuildings + 
                    ChatColor.GRAY + " (Строящихся: " + report.constructingChecked + ", Завершенных: " + report.activeChecked + ")");
            feedbackRecipient.sendMessage(ChatColor.WHITE + " • Синхронизировано блоков в мире: " + ChatColor.GREEN + report.blocksReconciled + " шт.");
            feedbackRecipient.sendMessage(ChatColor.WHITE + " • Переведено слоев строительства: " + ChatColor.AQUA + report.layersAdvanced);
            feedbackRecipient.sendMessage(ChatColor.WHITE + " • Восстановлено голограмм: " + ChatColor.LIGHT_PURPLE + report.hologramsHealed + " шт.");
            if (report.buildingsCompleted > 0) {
                feedbackRecipient.sendMessage(ChatColor.GREEN + " • Завершено зданий: " + report.buildingsCompleted);
            }
            if (report.buildingsDamaged > 0) {
                feedbackRecipient.sendMessage(ChatColor.RED + " • Обнаружено поврежденных зданий: " + report.buildingsDamaged);
            }
            if (report.buildingsRestored > 0) {
                feedbackRecipient.sendMessage(ChatColor.GREEN + " • Отремонтировано зданий: " + report.buildingsRestored);
            }
            feedbackRecipient.sendMessage(ChatColor.GRAY + " • Время выполнения: " + ChatColor.WHITE + report.durationMs + " ms " + ChatColor.DARK_GRAY + "(База синхронизирована ✔)");
            feedbackRecipient.sendMessage(ChatColor.GOLD + "══════════════════════════════════════════");
        } else if (verbose || report.blocksReconciled > 0 || report.layersAdvanced > 0 || report.buildingsCompleted > 0 || report.buildingsDamaged > 0 || report.buildingsRestored > 0 || report.hologramsHealed > 0) {
            plugin.getLogger().info(String.format("[Watchdog] Аудит (%dms): зданий: %d, синхронизировано блоков: %d, слоев: %d, голограмм: %d, завершено: %d, повреждено: %d, починено: %d",
                    report.durationMs, report.totalBuildings, report.blocksReconciled, report.layersAdvanced, report.hologramsHealed, report.buildingsCompleted, report.buildingsDamaged, report.buildingsRestored));
        }

        return report;
    }

    public void performPeriodicIntegrityCheck() {
        performWatchdogAudit(null, false);
    }"""

assert old_integrity in content, "old_integrity not found in BuildingManager.java"
content = content.replace(old_integrity, new_integrity, 1)

with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated BuildingManager.java with performWatchdogAudit successfully!")
