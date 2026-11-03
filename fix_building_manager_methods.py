with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'r', encoding='utf-8') as f:
    code = f.read()

helper_methods = """
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
        return false;
    }

    public int calculateTerrainGroundY(World world, Set<ChunkCoord> assignedChunks) {
        if (world == null || assignedChunks == null || assignedChunks.isEmpty()) return 64;
        List<Integer> heights = new ArrayList<>();
        for (ChunkCoord cc : assignedChunks) {
            int cx = cc.getX() << 4;
            int cz = cc.getZ() << 4;
            for (int x = 2; x < 16; x += 4) {
                for (int z = 2; z < 16; z += 4) {
                    int h = world.getHighestBlockYAt(cx + x, cz + z);
                    heights.add(h);
                }
            }
        }
        if (heights.isEmpty()) return 64;
        Collections.sort(heights);
        return heights.get(heights.size() / 2);
    }
"""

idx_last_brace = code.rfind('}')
code = code[:idx_last_brace] + helper_methods + "\n}\n"

with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'w', encoding='utf-8') as f:
    f.write(code)

print("Restored helper methods in BuildingManager.java")
