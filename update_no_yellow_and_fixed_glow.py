# 1. Update BuildingHudManager.java
with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingHudManager.java', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace from renderParticles() down to end of file
start_idx = code.find('public void renderParticles()')

new_section = """public void renderParticles() {
        if (!plugin.getConfig().getBoolean("settings.particles-enabled", true)) return;

        int radiusChunks = plugin.getConfig().getInt("settings.buff-1x1-chunk-radius", 2);

        Particle.DustOptions ghostCyanDust = new Particle.DustOptions(Color.fromRGB(0, 220, 255), 1.6f);
        Particle.DustOptions obstacleRedDust = new Particle.DustOptions(Color.fromRGB(255, 30, 40), 1.8f);
        Particle.DustOptions plotAquaDust = new Particle.DustOptions(Color.fromRGB(0, 180, 255), 1.8f);
        Particle.DustOptions footprintCyanDust = new Particle.DustOptions(Color.fromRGB(0, 230, 255), 1.8f);

        for (Player player : Bukkit.getOnlinePlayers()) {
            boolean showBorders = hasParticlesEnabled(player);
            boolean showEffects = hasEffectParticlesEnabled(player);
            if (!showBorders && !showEffects) continue;

            Location pLoc = player.getLocation();
            World pWorld = pLoc.getWorld();
            if (pWorld == null) continue;

            double pX = pLoc.getX();
            double pY = pLoc.getY();
            double pZ = pLoc.getZ();

            // 1. Render active building boundaries, effect zones, and ghost/obstacle block wireframes
            for (ActiveBuilding bld : plugin.getBuildingManager().getActiveBuildings()) {
                if (!bld.getWorldName().equals(pWorld.getName())) continue;
                if (bld.getAssignedChunks().isEmpty()) continue;

                BuildingBlueprint bp = plugin.getBuildingManager().getBlueprint(bld.getBlueprintId());
                if (bp == null) continue;

                // A. Layer-by-layer Block Edge Highlighting (Cyan for Ghost Blocks, Red for Obstacles)
                // Always persistent: never disappears when blocks are placed or modified!
                if (!bld.isFullyBuilt() && showBorders) {
                    renderLayerBlockWireframes(player, pWorld, bld, pX, pY, pZ, ghostCyanDust, obstacleRedDust);
                }

                int minCX = Integer.MAX_VALUE, maxCX = Integer.MIN_VALUE;
                int minCZ = Integer.MAX_VALUE, maxCZ = Integer.MIN_VALUE;
                for (ChunkCoord c : bld.getAssignedChunks()) {
                    minCX = Math.min(minCX, c.getX());
                    maxCX = Math.max(maxCX, c.getX());
                    minCZ = Math.min(minCZ, c.getZ());
                    maxCZ = Math.max(maxCZ, c.getZ());
                }

                double bMinX = minCX << 4;
                double bMaxX = (maxCX + 1) << 4;
                double bMinZ = minCZ << 4;
                double bMaxZ = (maxCZ + 1) << 4;

                // B. Building footprint boundary (Clean Electric Cyan line - NO yellow!)
                if (showBorders && pX >= bMinX - 50 && pX <= bMaxX + 50 && pZ >= bMinZ - 50 && pZ <= bMaxZ + 50) {
                    renderSolidLine(player, pWorld, bMinX, bMaxX, bMinZ, bMaxZ, pX, pY, pZ, footprintCyanDust);
                }

                // C. Buff Zone boundary for 1x1 buildings (Clean, thin, continuous glowing line)
                // Vivid Electric Cyan / Neon Blue for utility/economy, Vivid Ruby Red for hospital/combat
                if (showEffects && bp.getChunkWidth() == 1 && bp.getChunkLength() == 1) {
                    double effMinX = (minCX - radiusChunks) << 4;
                    double effMaxX = (maxCX + radiusChunks + 1) << 4;
                    double effMinZ = (minCZ - radiusChunks) << 4;
                    double effMaxZ = (maxCZ + radiusChunks + 1) << 4;

                    if (pX >= effMinX - 50 && pX <= effMaxX + 50 && pZ >= effMinZ - 50 && pZ <= effMaxZ + 50) {
                        Color buffColor;
                        String bpId = bld.getBlueprintId().toLowerCase();
                        if (bpId.contains("hospital") || bpId.contains("infirmary") || bpId.contains("barracks")) {
                            buffColor = Color.fromRGB(255, 35, 65); // Vivid Crimson Red
                        } else {
                            buffColor = Color.fromRGB(0, 200, 255); // Vivid Electric Cyan
                        }
                        Particle.DustOptions effectDust = new Particle.DustOptions(buffColor, 1.8f);
                        renderSolidLine(player, pWorld, effMinX, effMaxX, effMinZ, effMaxZ, pX, pY, pZ, effectDust);
                    }
                }
            }

            // 2. Render designated town build plots (Vivid Aqua / Sky Blue - NO yellow!)
            if (showBorders) {
                String playerTown = plugin.getTownyHook().getPlayerTownName(player);
                if (playerTown != null) {
                    Set<ChunkCoord> plots = plugin.getBuildingManager().getTownBuildPlots(playerTown);
                    if (!plots.isEmpty()) {
                        for (ChunkCoord cc : plots) {
                            if (plugin.getBuildingManager().isChunkOccupiedByBuilding(cc)) continue;
                            double minX = cc.getX() << 4;
                            double maxX = (cc.getX() + 1) << 4;
                            double minZ = cc.getZ() << 4;
                            double maxZ = (cc.getZ() + 1) << 4;

                            if (pX >= minX - 50 && pX <= maxX + 50 && pZ >= minZ - 50 && pZ <= maxZ + 50) {
                                renderSolidLine(player, pWorld, minX, maxX, minZ, maxZ, pX, pY, pZ, plotAquaDust);
                            }
                        }
                    }
                }
            }
        }
    }

    /**
     * Renders crisp 3D edge wireframes around all active layer blocks:
     * - CYAN wireframe for required Ghost Blocks so they are clearly visible
     * - RED wireframe for Obstacle Blocks (trees, dirt, wrong blocks) that must be cleared
     */
    private void renderLayerBlockWireframes(Player player, World world, ActiveBuilding bld, 
                                           double pX, double pY, double pZ,
                                           Particle.DustOptions cyanDust, Particle.DustOptions redDust) {
        BuildingSchematic schem = plugin.getSchematicManager().getSchematic(bld.getBlueprintId());
        if (schem == null) return;

        int currentLayer = bld.getCurrentLayer();
        List<SchematicBlock> layerBlocks = schem.getBlocksAtLayer(currentLayer);
        if (layerBlocks == null || layerBlocks.isEmpty()) return;

        for (SchematicBlock sb : layerBlocks) {
            if (bld.isBlockCompleted(sb.getDx(), sb.getDy(), sb.getDz())) continue;

            int[] rPos = BuildingManager.rotateRelativeCoords(sb.getDx(), sb.getDz(), bld.getRotationDeg(), schem.getWidthX(), schem.getLengthZ());
            int wx = bld.getOriginX() + rPos[0];
            int wy = bld.getOriginY() + sb.getDy();
            int wz = bld.getOriginZ() + rPos[1];

            // Only check within player view range (28 blocks)
            if (Math.abs(wx - pX) > 28.0 || Math.abs(wz - pZ) > 28.0 || Math.abs(wy - pY) > 16.0) continue;

            Material wm = world.getBlockAt(wx, wy, wz).getType();
            if (BuildingManager.isMaterialMatch(wm, sb.getMaterial())) {
                continue; // Block placed and matching
            }

            boolean isObstacle = !wm.isAir() && !(wm == Material.WATER || wm == Material.LAVA);
            Particle.DustOptions dustToUse = isObstacle ? redDust : cyanDust;

            renderBlockWireframeBox(player, wx, wy, wz, dustToUse);
        }
    }

    /**
     * Renders a crisp 12-edge bounding wireframe on a single block
     */
    private void renderBlockWireframeBox(Player player, int bx, int by, int bz, Particle.DustOptions dust) {
        double minX = bx, maxX = bx + 1.0;
        double minY = by, maxY = by + 1.0;
        double minZ = bz, maxZ = bz + 1.0;

        // 8 corners
        for (double x : new double[]{minX, maxX}) {
            for (double y : new double[]{minY, maxY}) {
                for (double z : new double[]{minZ, maxZ}) {
                    player.spawnParticle(dustParticle, x, y, z, 1, 0, 0, 0, 0, dust);
                }
            }
        }

        // Edge midpoints for solid wireframe look
        player.spawnParticle(dustParticle, (minX + maxX) / 2.0, minY, minZ, 1, 0, 0, 0, 0, dust);
        player.spawnParticle(dustParticle, (minX + maxX) / 2.0, maxY, minZ, 1, 0, 0, 0, 0, dust);
        player.spawnParticle(dustParticle, (minX + maxX) / 2.0, minY, maxZ, 1, 0, 0, 0, 0, dust);
        player.spawnParticle(dustParticle, (minX + maxX) / 2.0, maxY, maxZ, 1, 0, 0, 0, 0, dust);

        player.spawnParticle(dustParticle, minX, minY, (minZ + maxZ) / 2.0, 1, 0, 0, 0, 0, dust);
        player.spawnParticle(dustParticle, maxX, minY, (minZ + maxZ) / 2.0, 1, 0, 0, 0, 0, dust);
        player.spawnParticle(dustParticle, minX, maxY, (minZ + maxZ) / 2.0, 1, 0, 0, 0, 0, dust);
        player.spawnParticle(dustParticle, maxX, maxY, (minZ + maxZ) / 2.0, 1, 0, 0, 0, 0, dust);

        player.spawnParticle(dustParticle, minX, (minY + maxY) / 2.0, minZ, 1, 0, 0, 0, 0, dust);
        player.spawnParticle(dustParticle, maxX, (minY + maxY) / 2.0, minZ, 1, 0, 0, 0, 0, dust);
        player.spawnParticle(dustParticle, minX, (minY + maxY) / 2.0, maxZ, 1, 0, 0, 0, 0, dust);
        player.spawnParticle(dustParticle, maxX, (minY + maxY) / 2.0, maxZ, 1, 0, 0, 0, 0, dust);
    }

    /**
     * Renders a smooth, dense, continuous solid perimeter line at terrain ground level
     */
    private void renderSolidLine(Player player, World world, double minX, double maxX, double minZ, double maxZ,
                                 double pX, double pY, double pZ, Particle.DustOptions dust) {
        double maxDist = 48.0;

        // North edge (Z = minZ)
        if (Math.abs(pZ - minZ) <= maxDist && pX >= minX - 32.0 && pX <= maxX + 32.0) {
            double start = Math.max(minX, pX - 36.0);
            double end = Math.min(maxX, pX + 36.0);
            for (double x = start; x <= end; x += 0.28) {
                spawnVisibleParticle(player, world, x, minZ, pY, dust);
            }
        }

        // South edge (Z = maxZ)
        if (Math.abs(pZ - maxZ) <= maxDist && pX >= minX - 32.0 && pX <= maxX + 32.0) {
            double start = Math.max(minX, pX - 36.0);
            double end = Math.min(maxX, pX + 36.0);
            for (double x = start; x <= end; x += 0.28) {
                spawnVisibleParticle(player, world, x, maxZ, pY, dust);
            }
        }

        // West edge (X = minX)
        if (Math.abs(pX - minX) <= maxDist && pZ >= minZ - 32.0 && pZ <= maxZ + 32.0) {
            double start = Math.max(minZ, pZ - 36.0);
            double end = Math.min(maxZ, pZ + 36.0);
            for (double z = start; z <= end; z += 0.28) {
                spawnVisibleParticle(player, world, minX, z, pY, dust);
            }
        }

        // East edge (X = maxX)
        if (Math.abs(pX - maxX) <= maxDist && pZ >= minZ - 32.0 && pZ <= maxZ + 32.0) {
            double start = Math.max(minZ, pZ - 36.0);
            double end = Math.min(maxZ, pZ + 36.0);
            for (double z = start; z <= end; z += 0.28) {
                spawnVisibleParticle(player, world, maxX, z, pY, dust);
            }
        }
    }

    private double findGroundY(World world, double x, double z, double playerY) {
        int bx = (int) Math.floor(x);
        int bz = (int) Math.floor(z);
        if (!world.isChunkLoaded(bx >> 4, bz >> 4)) return -1000;

        int py = (int) Math.floor(playerY);
        int startY = Math.min(py + 6, world.getMaxHeight() - 1);
        int minY = Math.max(py - 10, world.getMinHeight());

        for (int y = startY; y >= minY; y--) {
            org.bukkit.block.Block b = world.getBlockAt(bx, y, bz);
            Material m = b.getType();
            if (m.isSolid() && isTrueTerrainGround(m)) {
                return y + 1.05;
            }
        }
        return playerY + 0.1;
    }

    private boolean isTrueTerrainGround(Material m) {
        if (m == null || m.isAir()) return false;
        String name = m.name();
        if (name.contains("LEAVES") || name.contains("FENCE") || name.contains("GLASS") ||
            name.contains("SCAFFOLD") || name.contains("BANNER") || name.contains("CARPET") ||
            name.contains("CHAIN") || name.contains("LANTERN") || name.contains("TORCH") ||
            name.contains("WALL") || name.contains("STAIR") || name.contains("DOOR") ||
            name.contains("SLAB")) {
            return false;
        }
        return true;
    }

    private void spawnVisibleParticle(Player player, World world, double x, double z, double playerY, Particle.DustOptions dust) {
        double groundY = findGroundY(world, x, z, playerY);
        if (groundY < world.getMinHeight()) return;

        Location loc = new Location(world, x, groundY + 0.08, z);
        try {
            if (dustParticle.getDataType() == Particle.DustOptions.class) {
                player.spawnParticle(dustParticle, loc, 1, 0.0, 0.0, 0.0, 0.0, dust);
            } else {
                player.spawnParticle(dustParticle, loc, 1, 0.0, 0.0, 0.0, 0.0);
            }
        } catch (Exception ignored) {}
    }

    public void updateHud() {
        int cycleIntervalSeconds = plugin.getConfig().getInt("settings.hud-material-cycle-interval-seconds", 5);
        if (cycleIntervalSeconds < 1) cycleIntervalSeconds = 5;

        for (Player player : Bukkit.getOnlinePlayers()) {
            ActiveBuilding building = plugin.getBuildingManager().getBuildingAt(player.getLocation());
            if (building != null && !building.isFullyBuilt()) {
                BuildingBlueprint bp = plugin.getBuildingManager().getBlueprint(building.getBlueprintId());
                String bpName = bp != null ? bp.getNameRu() : building.getBlueprintId();
                int percent = building.getProgressPercent();

                // Clean Blue/Cyan BossBar instead of Yellow
                BossBar bar = playerBossBars.computeIfAbsent(player.getUniqueId(), k -> {
                    BossBar b = Bukkit.createBossBar(
                            "",
                            BarColor.BLUE,
                            BarStyle.SEGMENTED_10
                    );
                    b.addPlayer(player);
                    return b;
                });

                bar.setProgress(Math.max(0.0, Math.min(1.0, percent / 100.0)));
                bar.setVisible(true);

                StringBuilder reqStr = new StringBuilder();
                Map<Material, Integer> required = building.getRequiredMaterials();
                
                List<Map.Entry<Material, Integer>> uncompleted = new ArrayList<>();
                List<Map.Entry<Material, Integer>> completed = new ArrayList<>();
                for (Map.Entry<Material, Integer> entry : required.entrySet()) {
                    int placed = building.getPlacedCount(entry.getKey());
                    int need = entry.getValue();
                    if (placed < need) {
                        uncompleted.add(entry);
                    } else {
                        completed.add(entry);
                    }
                }
                
                List<Map.Entry<Material, Integer>> sortedList = new ArrayList<>(uncompleted);
                sortedList.addAll(completed);

                if (!sortedList.isEmpty()) {
                    int currentCycle = playerCycleIndex.getOrDefault(player.getUniqueId(), 0);
                    int ticksHeld = playerTicksHeld.getOrDefault(player.getUniqueId(), 0) + 1;
                    
                    if (ticksHeld >= cycleIntervalSeconds) {
                        ticksHeld = 0;
                        currentCycle = (currentCycle + 1) % sortedList.size();
                        playerCycleIndex.put(player.getUniqueId(), currentCycle);
                    }
                    playerTicksHeld.put(player.getUniqueId(), ticksHeld);
                    
                    int idx1 = currentCycle % sortedList.size();
                    Map.Entry<Material, Integer> e1 = sortedList.get(idx1);
                    int placed1 = building.getPlacedCount(e1.getKey());
                    int need1 = e1.getValue();
                    boolean done1 = placed1 >= need1;
                    
                    reqStr.append(done1 ? "§a✔ " : "§b■ ")
                          .append("§f").append(RussianTranslator.getShortMaterialRu(e1.getKey())).append(": ")
                          .append(done1 ? "§a" : "§b").append(placed1).append("§7/§a").append(need1);
                          
                    if (sortedList.size() > 1) {
                        int idx2 = (idx1 + 1) % sortedList.size();
                        Map.Entry<Material, Integer> e2 = sortedList.get(idx2);
                        int placed2 = building.getPlacedCount(e2.getKey());
                        int need2 = e2.getValue();
                        boolean done2 = placed2 >= need2;
                        
                        reqStr.append(" §8| ")
                              .append(done2 ? "§a✔ " : "§b■ ")
                              .append("§f").append(RussianTranslator.getShortMaterialRu(e2.getKey())).append(": ")
                              .append(done2 ? "§a" : "§b").append(placed2).append("§7/§a").append(need2);
                    }
                }

                // Crisp Aqua & White formatting - Zero Yellow!
                String prefix = ChatColor.AQUA + "⚡ [" + building.getTownName() + "] " + ChatColor.WHITE + bpName + ChatColor.DARK_GRAY + " | ";
                if (reqStr.length() > 0) {
                    bar.setTitle(prefix + reqStr.toString() + " §8| §a" + percent + "%");
                } else {
                    bar.setTitle(prefix + "§a" + percent + "%");
                }
            } else {
                BossBar bar = playerBossBars.remove(player.getUniqueId());
                if (bar != null) {
                    bar.removePlayer(player);
                    bar.setVisible(false);
                }
                playerTicksHeld.remove(player.getUniqueId());
            }
        }
    }

    public void removePlayer(Player player) {
        BossBar bar = playerBossBars.remove(player.getUniqueId());
        if (bar != null) {
            bar.removePlayer(player);
            bar.setVisible(false);
        }
        playerCycleIndex.remove(player.getUniqueId());
        playerTicksHeld.remove(player.getUniqueId());
        playersParticlesDisabled.remove(player.getUniqueId());
        playersEffectParticlesDisabled.remove(player.getUniqueId());
    }

    public void clearAll() {
        for (BossBar bar : playerBossBars.values()) {
            bar.removeAll();
            bar.setVisible(false);
        }
        playerBossBars.clear();
        playerCycleIndex.clear();
        playerTicksHeld.clear();
        playersParticlesDisabled.clear();
        playersEffectParticlesDisabled.clear();
    }
}
"""

code = code[:start_idx] + new_section

with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingHudManager.java', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated BuildingHudManager.java with persistent cyan/red wireframes and zero yellow!")

# 2. Update BuildingManager.java Action Bar messages to remove yellow
with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'r', encoding='utf-8') as f:
    bm_code = f.read()

bm_code = bm_code.replace('§e[!] Стройте послойно! Слой: §6', '§b[!] Стройте послойно! Слой: §f')
bm_code = bm_code.replace('§e. Завершите его!', '§b. Завершите его!')
bm_code = bm_code.replace('§c✖ Ошибка: Здесь по чертежу требуется §e', '§c✖ Ошибка: Здесь по чертежу требуется §b')

with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'w', encoding='utf-8') as f:
    f.write(bm_code)

print("Updated BuildingManager.java messages!")
