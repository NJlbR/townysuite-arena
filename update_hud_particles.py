with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingHudManager.java', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace from renderParticles() down to end of file
start_idx = code.find('public void renderParticles()')

new_section = """public void renderParticles() {
        if (!plugin.getConfig().getBoolean("settings.particles-enabled", true)) return;

        int radiusChunks = plugin.getConfig().getInt("settings.buff-1x1-chunk-radius", 2);

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

            // 1. Render active building boundaries and effect zones
            for (ActiveBuilding bld : plugin.getBuildingManager().getActiveBuildings()) {
                if (!bld.getWorldName().equals(pWorld.getName())) continue;
                if (bld.getAssignedChunks().isEmpty()) continue;

                BuildingBlueprint bp = plugin.getBuildingManager().getBlueprint(bld.getBlueprintId());
                if (bp == null) continue;

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

                // A. Building footprint boundary (Thin crisp line)
                if (showBorders && pX >= bMinX - 50 && pX <= bMaxX + 50 && pZ >= bMinZ - 50 && pZ <= bMaxZ + 50) {
                    Particle.DustOptions buildingDust = new Particle.DustOptions(Color.fromRGB(255, 215, 0), 1.8f);
                    renderSolidLine(player, pWorld, bMinX, bMaxX, bMinZ, bMaxZ, pX, pY, pZ, buildingDust);
                }

                // B. Buff Zone boundary for 1x1 buildings (Clean, thin, continuous glowing line)
                // Vivid Electric Cyan / Sky Blue for utility/economy, Vivid Ruby Red for hospital/combat
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
                            buffColor = Color.fromRGB(0, 230, 255); // Vivid Electric Cyan / Neon Blue
                        }
                        Particle.DustOptions effectDust = new Particle.DustOptions(buffColor, 1.8f);
                        renderSolidLine(player, pWorld, effMinX, effMaxX, effMinZ, effMaxZ, pX, pY, pZ, effectDust);
                    }
                }
            }

            // 2. Render designated town build plots
            // Intense luminous Gold/Amber (RGB: 255, 170, 0)
            if (showBorders) {
                String playerTown = plugin.getTownyHook().getPlayerTownName(player);
                if (playerTown != null) {
                    Set<ChunkCoord> plots = plugin.getBuildingManager().getTownBuildPlots(playerTown);
                    if (!plots.isEmpty()) {
                        Particle.DustOptions plotAmberDust = new Particle.DustOptions(Color.fromRGB(255, 170, 0), 1.8f);
                        for (ChunkCoord cc : plots) {
                            if (plugin.getBuildingManager().isChunkOccupiedByBuilding(cc)) continue;
                            double minX = cc.getX() << 4;
                            double maxX = (cc.getX() + 1) << 4;
                            double minZ = cc.getZ() << 4;
                            double maxZ = (cc.getZ() + 1) << 4;

                            if (pX >= minX - 50 && pX <= maxX + 50 && pZ >= minZ - 50 && pZ <= maxZ + 50) {
                                renderSolidLine(player, pWorld, minX, maxX, minZ, maxZ, pX, pY, pZ, plotAmberDust);
                            }
                        }
                    }
                }
            }
        }
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
        // Ignore tree leaves, logs, stairs, fences, banners, scaffolding so line stays on the terrain
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

                BossBar bar = playerBossBars.computeIfAbsent(player.getUniqueId(), k -> {
                    BossBar b = Bukkit.createBossBar(
                            "",
                            BarColor.YELLOW,
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
                    
                    reqStr.append(done1 ? "§a✔ " : "§e■ ")
                          .append("§f").append(RussianTranslator.getShortMaterialRu(e1.getKey())).append(": ")
                          .append(done1 ? "§a" : "§e").append(placed1).append("§7/§a").append(need1);
                          
                    if (sortedList.size() > 1) {
                        int idx2 = (idx1 + 1) % sortedList.size();
                        Map.Entry<Material, Integer> e2 = sortedList.get(idx2);
                        int placed2 = building.getPlacedCount(e2.getKey());
                        int need2 = e2.getValue();
                        boolean done2 = placed2 >= need2;
                        
                        reqStr.append(" §8| ")
                              .append(done2 ? "§a✔ " : "§e■ ")
                              .append("§f").append(RussianTranslator.getShortMaterialRu(e2.getKey())).append(": ")
                              .append(done2 ? "§a" : "§e").append(placed2).append("§7/§a").append(need2);
                    }
                }

                String prefix = ChatColor.GOLD + "⚡ [" + building.getTownName() + "] " + ChatColor.YELLOW + bpName + ChatColor.DARK_GRAY + " | ";
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

print("Updated BuildingHudManager.java successfully!")
