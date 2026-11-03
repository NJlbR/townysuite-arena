with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace calculateTerrainGroundY, detectExistingConstruction, and checkTerrainWallExposure
old_section_start = code.find('public ExistingStageAlignment detectExistingConstruction')
old_section_end = code.find('public ActiveBuilding startBuilding', old_section_start)

new_section = """public ExistingStageAlignment detectExistingConstruction(BuildingSchematic schem, World world, Set<ChunkCoord> assignedChunks) {
        if (schem == null || world == null || assignedChunks == null || assignedChunks.isEmpty()) {
            return null;
        }
        int minChunkX = Integer.MAX_VALUE;
        int minChunkZ = Integer.MAX_VALUE;
        int maxChunkX = Integer.MIN_VALUE;
        int maxChunkZ = Integer.MIN_VALUE;
        for (ChunkCoord cc : assignedChunks) {
            if (cc.getX() < minChunkX) minChunkX = cc.getX();
            if (cc.getZ() < minChunkZ) minChunkZ = cc.getZ();
            if (cc.getX() > maxChunkX) maxChunkX = cc.getX();
            if (cc.getZ() > maxChunkZ) maxChunkZ = cc.getZ();
        }
        int plotMinX = minChunkX * 16;
        int plotMinZ = minChunkZ * 16;
        int plotMaxX = (maxChunkX + 1) * 16;
        int plotMaxZ = (maxChunkZ + 1) * 16;
        int plotWidth = plotMaxX - plotMinX;
        int plotLength = plotMaxZ - plotMinZ;

        List<SchematicBlock> allBlocks = schem.getBlocks();
        if (allBlocks.isEmpty()) return null;

        int medianGroundY = calculateTerrainGroundY(world, assignedChunks);
        int minY = Math.max(world.getMinHeight() + 1, Math.max(50, medianGroundY - 5));
        int maxY = Math.min(world.getMaxHeight() - schem.getHeightY(), medianGroundY + 5);

        // Balanced anchor selection across layers (foundation, middle, and roof)
        List<SchematicBlock> anchorBlocks = new ArrayList<>();
        for (SchematicBlock sb : allBlocks) {
            if (sb.getDy() == 0 && !sb.getMaterial().isAir()) {
                anchorBlocks.add(sb);
                if (anchorBlocks.size() >= 6) break;
            }
        }
        int maxLayer = schem.getMaxLayer();
        for (SchematicBlock sb : allBlocks) {
            if (sb.getDy() == maxLayer && !sb.getMaterial().isAir()) {
                anchorBlocks.add(sb);
                if (anchorBlocks.size() >= 12) break;
            }
        }
        if (anchorBlocks.isEmpty()) {
            anchorBlocks.addAll(allBlocks.subList(0, Math.min(8, allBlocks.size())));
        }

        int[] rotations = {0, 90, 180, 270};
        ExistingStageAlignment bestAlignment = null;
        int bestMatchedCount = 0;

        for (int rot : rotations) {
            int effW = (rot == 90 || rot == 270) ? schem.getLengthZ() : schem.getWidthX();
            int effL = (rot == 90 || rot == 270) ? schem.getWidthX() : schem.getLengthZ();
            int maxOffsetX = plotWidth - effW;
            int maxOffsetZ = plotLength - effL;
            if (maxOffsetX < 0 || maxOffsetZ < 0) continue;

            for (int offX = 0; offX <= maxOffsetX; offX++) {
                int testOriginX = plotMinX + offX;
                for (int offZ = 0; offZ <= maxOffsetZ; offZ++) {
                    int testOriginZ = plotMinZ + offZ;

                    for (int testOriginY = minY; testOriginY <= maxY; testOriginY++) {
                        boolean anchorPassed = false;
                        for (SchematicBlock anchor : anchorBlocks) {
                            int[] arc = rotateRelativeCoords(anchor.getDx(), anchor.getDz(), rot, schem.getWidthX(), schem.getLengthZ());
                            int ax = testOriginX + arc[0];
                            int ay = testOriginY + anchor.getDy();
                            int az = testOriginZ + arc[1];
                            if (ay >= world.getMinHeight() && ay < world.getMaxHeight()) {
                                Material wm = world.getBlockAt(ax, ay, az).getType();
                                if (isMaterialMatch(wm, anchor.getMaterial())) {
                                    anchorPassed = true;
                                    break;
                                }
                            }
                        }
                        if (!anchorPassed) continue;

                        int matched = 0;
                        Set<String> matchedKeys = new HashSet<>();
                        for (SchematicBlock sb : allBlocks) {
                            int[] rc = rotateRelativeCoords(sb.getDx(), sb.getDz(), rot, schem.getWidthX(), schem.getLengthZ());
                            int wx = testOriginX + rc[0];
                            int wy = testOriginY + sb.getDy();
                            int wz = testOriginZ + rc[1];
                            if (wy >= world.getMinHeight() && wy < world.getMaxHeight()) {
                                Material wm = world.getBlockAt(wx, wy, wz).getType();
                                if (isMaterialMatch(wm, sb.getMaterial())) {
                                    matched++;
                                    matchedKeys.add(sb.getDx() + "," + sb.getDy() + "," + sb.getDz());
                                }
                            }
                        }

                        int completedLayers = 0;
                        for (int l = 0; l <= maxLayer; l++) {
                            List<SchematicBlock> layerBlocks = schem.getBlocksAtLayer(l);
                            if (layerBlocks.isEmpty()) continue;
                            boolean allDone = true;
                            for (SchematicBlock sb : layerBlocks) {
                                if (!matchedKeys.contains(sb.getDx() + "," + sb.getDy() + "," + sb.getDz())) {
                                    allDone = false;
                                    break;
                                }
                            }
                            if (allDone) {
                                completedLayers++;
                            }
                        }

                        // FULL COMPLETION CHECK (100% or >= 95% of blueprint blocks matched)
                        if (matched == allBlocks.size() || (allBlocks.size() >= 20 && matched >= (int)(allBlocks.size() * 0.95))) {
                            plugin.getLogger().info("[AutoAlign] FULL MATCH of " + matched + "/" + allBlocks.size() + " schematic blocks at " +
                                    testOriginX + "," + testOriginY + "," + testOriginZ + " rot=" + rot);
                            return new ExistingStageAlignment(
                                    testOriginX, testOriginY, testOriginZ, rot,
                                    completedLayers, matched, matchedKeys, true
                            );
                        }

                        if (matched > bestMatchedCount) {
                            bestMatchedCount = matched;
                            bestAlignment = new ExistingStageAlignment(
                                    testOriginX, testOriginY, testOriginZ, rot,
                                    completedLayers, matched, matchedKeys, false
                            );
                        }
                    }
                }
            }
        }
        return bestAlignment;
    }

    public int calculateTerrainGroundY(World world, Set<ChunkCoord> assignedChunks) {
        if (world == null || assignedChunks == null || assignedChunks.isEmpty()) return 64;
        int minChunkX = Integer.MAX_VALUE;
        int minChunkZ = Integer.MAX_VALUE;
        int maxChunkX = Integer.MIN_VALUE;
        int maxChunkZ = Integer.MIN_VALUE;
        for (ChunkCoord cc : assignedChunks) {
            if (cc.getX() < minChunkX) minChunkX = cc.getX();
            if (cc.getZ() < minChunkZ) minChunkZ = cc.getZ();
            if (cc.getX() > maxChunkX) maxChunkX = cc.getX();
            if (cc.getZ() > maxChunkZ) maxChunkZ = cc.getZ();
        }
        int minX = minChunkX * 16;
        int minZ = minChunkZ * 16;
        int maxX = (maxChunkX + 1) * 16 - 1;
        int maxZ = (maxChunkZ + 1) * 16 - 1;

        List<Integer> surfaceHeights = new ArrayList<>();
        int stepX = Math.max(1, (maxX - minX) / 4);
        int stepZ = Math.max(1, (maxZ - minZ) / 4);

        for (int x = minX + 2; x <= maxX - 2; x += stepX) {
            for (int z = minZ + 2; z <= maxZ - 2; z += stepZ) {
                int highestY = world.getHighestBlockYAt(x, z, HeightMap.MOTION_BLOCKING_NO_LEAVES);
                int checkY = Math.min(highestY, 130);
                while (checkY >= Math.max(50, world.getMinHeight())) {
                    Material mat = world.getBlockAt(x, checkY, z).getType();
                    if (isNaturalTerrainMaterial(mat)) {
                        // Foundation sits on TOP of the natural ground surface (+1)
                        surfaceHeights.add(checkY + 1);
                        break;
                    }
                    checkY--;
                }
            }
        }
        if (surfaceHeights.isEmpty()) {
            return world.getHighestBlockYAt((minX + maxX) / 2, (minZ + maxZ) / 2, HeightMap.MOTION_BLOCKING) + 1;
        }
        Collections.sort(surfaceHeights);
        return surfaceHeights.get(surfaceHeights.size() / 2);
    }

    public static boolean isNaturalTerrainMaterial(Material m) {
        if (m == null || m.isAir()) return false;
        String name = m.name();
        if (name.contains("BRICK") || name.contains("SLAB") || name.contains("STAIR") ||
            name.contains("WALL") || name.contains("PLANK") || name.contains("CONCRETE") ||
            name.contains("WOOL") || name.contains("GLASS") || name.contains("BARS") ||
            name.contains("IRON") || name.contains("GOLD") || name.contains("COPPER") ||
            name.contains("BOOKSHELF") || name.contains("BEACON") || name.contains("LANTERN") ||
            name.contains("LADDER") || name.contains("PILLAR") || name.contains("ANVIL") ||
            name.contains("FURNACE") || name.contains("PATH")) {
            return false;
        }
        return name.equals("GRASS_BLOCK") || name.contains("DIRT") || name.equals("STONE") ||
               name.equals("DEEPSLATE") || name.contains("SAND") || name.equals("GRAVEL") ||
               name.equals("CLAY") || name.contains("MUD") || name.equals("SNOW_BLOCK") ||
               name.equals("BEDROCK") || name.contains("TERRACOTTA");
    }

    public static boolean isMaterialMatch(Material worldMat, Material reqMat) {
        if (worldMat == reqMat) return true;
        if (worldMat == null || reqMat == null) return false;
        String w = worldMat.name();
        String r = reqMat.name();
        if (r.contains("STONE_BRICK") && (w.contains("STONE_BRICK") || w.contains("STONE_BRICKS"))) return true;
        if (r.contains("COBBLESTONE") && w.contains("COBBLESTONE")) return true;
        if (r.contains("DEEPSLATE") && w.contains("DEEPSLATE")) return true;
        if (r.contains("OAK") && w.contains("OAK")) return true;
        if (r.contains("SPRUCE") && w.contains("SPRUCE")) return true;
        if (r.contains("DARK_OAK") && w.contains("DARK_OAK")) return true;
        if (r.contains("QUARTZ") && w.contains("QUARTZ")) return true;
        if ((r.equals("WHITE_CONCRETE") || r.equals("CALCITE") || r.equals("WHITE_WOOL")) &&
            (w.equals("WHITE_CONCRETE") || w.equals("CALCITE") || w.equals("WHITE_WOOL") || w.contains("QUARTZ"))) return true;
        if ((r.equals("RED_CONCRETE") || r.equals("RED_WOOL")) &&
            (w.equals("RED_CONCRETE") || w.equals("RED_WOOL") || w.equals("RED_TERRACOTTA"))) return true;
        if (r.contains("GLASS") && w.contains("GLASS")) return true;
        if (r.contains("SANDSTONE") && w.contains("SANDSTONE")) return true;
        if (r.contains("BRICK") && w.contains("BRICK")) return true;
        if (r.contains("LANTERN") && w.contains("LANTERN")) return true;
        if (r.contains("WALL") && w.contains("WALL")) return true;
        if (r.contains("BOOKSHELF") && w.contains("BOOKSHELF")) return true;
        if (r.contains("LADDER") && w.contains("LADDER")) return true;
        if (r.contains("GOLD_BLOCK") && (w.contains("GOLD_BLOCK") || w.contains("RAW_GOLD"))) return true;
        if (r.contains("IRON_BARS") && (w.contains("IRON_BARS") || w.contains("CHAIN") || w.contains("DOOR"))) return true;
        if (r.contains("IRON_BLOCK") && w.contains("IRON_BLOCK")) return true;
        if (r.contains("SLAB") && (w.contains("PLANKS") || w.contains("STAIRS") || w.contains("SLAB"))) {
            String rBase = r.replace("_SLAB", "");
            if (w.contains(rBase)) return true;
        }
        return false;
    }

    public static int[] rotateRelativeCoords(int dx, int dz, int rotDeg, int w, int l) {
        switch (rotDeg) {
            case 90:
                return new int[]{dz, Math.max(0, w - 1 - dx)};
            case 180:
                return new int[]{Math.max(0, w - 1 - dx), Math.max(0, l - 1 - dz)};
            case 270:
                return new int[]{Math.max(0, l - 1 - dz), dx};
            case 0:
            default:
                return new int[]{dx, dz};
        }
    }

    public static int[] unrotateRelativeCoords(int rx, int rz, int rotDeg, int w, int l) {
        switch (rotDeg) {
            case 90:
                return rotateRelativeCoords(rx, rz, 270, l, w);
            case 180:
                return rotateRelativeCoords(rx, rz, 180, w, l);
            case 270:
                return rotateRelativeCoords(rx, rz, 90, l, w);
            case 0:
            default:
                return new int[]{rx, rz};
        }
    }

    public static int[] rotateDirection(int ox, int oz, int rotDeg) {
        switch (rotDeg) {
            case 90:
                return new int[]{oz, -ox};
            case 180:
                return new int[]{-ox, -oz};
            case 270:
                return new int[]{-oz, ox};
            case 0:
            default:
                return new int[]{ox, oz};
        }
    }

    private void applyExistingStageBlocks(ActiveBuilding building, BuildingSchematic schem, ExistingStageAlignment alignment) {
        if (building == null || schem == null || alignment == null) return;
        for (String key : alignment.matchedBlockKeys) {
            String[] parts = key.split(",");
            if (parts.length == 3) {
                try {
                    int dx = Integer.parseInt(parts[0]);
                    int dy = Integer.parseInt(parts[1]);
                    int dz = Integer.parseInt(parts[2]);
                    building.markBlockCompleted(dx, dy, dz);
                    SchematicBlock sb = schem.getBlock(dx, dy, dz);
                    if (sb != null) {
                        building.addPlacedBlock(sb.getMaterial());
                    }
                } catch (Exception ignored) {}
            }
        }
        int maxLayer = schem.getMaxLayer();
        int currentLayer = 0;
        for (int l = 0; l <= maxLayer; l++) {
            List<SchematicBlock> layerBlocks = schem.getBlocksAtLayer(l);
            if (layerBlocks.isEmpty()) continue;
            boolean allDone = true;
            for (SchematicBlock sb : layerBlocks) {
                if (!building.isBlockCompleted(sb.getDx(), sb.getDy(), sb.getDz())) {
                    allDone = false;
                    break;
                }
            }
            if (allDone) {
                currentLayer = Math.min(maxLayer + 1, l + 1);
            } else {
                currentLayer = l;
                break;
            }
        }
        building.setCurrentLayer(currentLayer);
    }

    """

code = code[:old_section_start] + new_section + code[old_section_end:]

face_start = code.find('public double checkTerrainWallExposure(')
face_end = code.find('public boolean wouldViolateWallExposure', face_start)

new_face_method = """public double checkTerrainWallExposure(BuildingSchematic schem, World world, int originX, int originY, int originZ, int rot) {
        if (schem == null || schem.getExteriorFaceCount() == 0 || world == null) return 100.0;
        int totalFaces = 0;
        int openFaces = 0;
        for (BuildingSchematic.ExteriorFace face : schem.getExteriorFaces()) {
            // Foundation bottom/sides at dy=0 rest on terrain; check dy >= 1 (walls & roof)
            if (face.getDy() == 0 && face.getOy() <= 0) {
                continue;
            }
            totalFaces++;
            int[] rPos = rotateRelativeCoords(face.getDx(), face.getDz(), rot, schem.getWidthX(), schem.getLengthZ());
            int[] rDir = rotateDirection(face.getOx(), face.getOz(), rot);
            int wx = originX + rPos[0] + rDir[0];
            int wy = originY + face.getDy() + face.getOy();
            int wz = originZ + rPos[1] + rDir[1];
            Material mat = world.getBlockAt(wx, wy, wz).getType();
            if (isNaturalOpenBlock(mat)) {
                openFaces++;
            }
        }
        if (totalFaces == 0) return 100.0;
        return ((double) openFaces / totalFaces) * 100.0;
    }

    """

code = code[:face_start] + new_face_method + code[face_end:]

with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'w', encoding='utf-8') as f:
    f.write(code)

print('Updated BuildingManager.java successfully!')
