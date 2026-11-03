with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace startBuilding chunk finding logic
old_start_chunk = """        ChunkCoord playerChunk = ChunkCoord.fromLocation(player.getLocation());
        Set<ChunkCoord> assignedChunks = findFreePlotArea(
                townName,
                player.getWorld().getName(),
                bp.getChunkWidth(),
                bp.getChunkLength(),
                playerChunk
        );
        if (assignedChunks == null || assignedChunks.isEmpty()) {
            player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                    plugin.getMsg("prefix") + "&cВ вашем городе нет свободного строительного участка размера " +
                    bp.getFootprintDisplay() + "!"));
            player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                    plugin.getMsg("prefix") + "&eНазначьте нужные чанки города командой &f/plot set build&e."));
            return null;
        }"""

new_start_chunk = """        ChunkCoord playerChunk = ChunkCoord.fromLocation(player.getLocation());
        Set<ChunkCoord> assignedChunks = findFreePlotArea(
                townName,
                player.getWorld().getName(),
                bp.getChunkWidth(),
                bp.getChunkLength(),
                playerChunk
        );
        if (assignedChunks == null || assignedChunks.isEmpty()) {
            player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                    plugin.getMsg("prefix") + "&c[!] Ошибка размещения: В текущем чанке и вокруг него нет достаточного количества свободных смежных чанков-стройплощадок для постройки «" + bp.getNameRu() + "» (требуется размер " + bp.getFootprintDisplay() + ")!"));
            player.sendMessage(ChatColor.translateAlternateColorCodes('&',
                    plugin.getMsg("prefix") + "&eУбедитесь, что все необходимые чанки назначены через &f/plot set build&e и не заняты другими постройками."));
            return null;
        }"""

code = code.replace(old_start_chunk, new_start_chunk)

# Replace findFreePlotArea implementation to strictly anchor around preferredChunk for multi-chunk buildings
old_find_free = """public Set<ChunkCoord> findFreePlotArea(String townName, String worldName, int widthChunks, int lengthChunks, ChunkCoord preferredChunk) {
        Set<ChunkCoord> allPlots = getTownBuildPlots(townName);
        if (allPlots.isEmpty()) return null;

        Set<ChunkCoord> freePlots = new HashSet<>();
        for (ChunkCoord c : allPlots) {
            if (c.getWorldName().equals(worldName) && !isChunkOccupiedByBuilding(c)) {
                freePlots.add(c);
            }
        }
        if (freePlots.isEmpty()) return null;

        int[][] orientations = (widthChunks == lengthChunks) 
                ? new int[][]{{widthChunks, lengthChunks}}
                : new int[][]{{widthChunks, lengthChunks}, {lengthChunks, widthChunks}};

        if (preferredChunk != null && freePlots.contains(preferredChunk)) {
            for (int[] dim : orientations) {
                int w = dim[0];
                int l = dim[1];
                for (int dx = 0; dx < w; dx++) {
                    for (int dz = 0; dz < l; dz++) {
                        int originX = preferredChunk.getX() - dx;
                        int originZ = preferredChunk.getZ() - dz;
                        Set<ChunkCoord> candidate = checkRectangle(freePlots, worldName, originX, originZ, w, l);
                        if (candidate != null) return candidate;
                    }
                }
            }
        }

        for (ChunkCoord anchor : freePlots) {
            for (int[] dim : orientations) {
                Set<ChunkCoord> candidate = checkRectangle(freePlots, worldName, anchor.getX(), anchor.getZ(), dim[0], dim[1]);
                if (candidate != null) return candidate;
            }
        }

        return null;
    }"""

new_find_free = """public Set<ChunkCoord> findFreePlotArea(String townName, String worldName, int widthChunks, int lengthChunks, ChunkCoord preferredChunk) {
        Set<ChunkCoord> allPlots = getTownBuildPlots(townName);
        if (allPlots.isEmpty()) return null;

        Set<ChunkCoord> freePlots = new HashSet<>();
        for (ChunkCoord c : allPlots) {
            if (c.getWorldName().equals(worldName) && !isChunkOccupiedByBuilding(c)) {
                freePlots.add(c);
            }
        }
        if (freePlots.isEmpty()) return null;

        int[][] orientations = (widthChunks == lengthChunks) 
                ? new int[][]{{widthChunks, lengthChunks}}
                : new int[][]{{widthChunks, lengthChunks}, {lengthChunks, widthChunks}};

        int areaChunks = widthChunks * lengthChunks;

        // For multi-chunk buildings (2x1, 2x2, etc.), strictly scan around preferredChunk in all directions
        if (preferredChunk != null && freePlots.contains(preferredChunk)) {
            for (int[] dim : orientations) {
                int w = dim[0];
                int l = dim[1];
                for (int dx = 0; dx < w; dx++) {
                    for (int dz = 0; dz < l; dz++) {
                        int originX = preferredChunk.getX() - dx;
                        int originZ = preferredChunk.getZ() - dz;
                        Set<ChunkCoord> candidate = checkRectangle(freePlots, worldName, originX, originZ, w, l);
                        if (candidate != null) return candidate;
                    }
                }
            }
        }

        // If it's a 1x1 building, we can also fall back to any free plot in town if preferredChunk isn't free
        if (areaChunks == 1) {
            for (ChunkCoord anchor : freePlots) {
                for (int[] dim : orientations) {
                    Set<ChunkCoord> candidate = checkRectangle(freePlots, worldName, anchor.getX(), anchor.getZ(), dim[0], dim[1]);
                    if (candidate != null) return candidate;
                }
            }
        }

        return null;
    }"""

code = code.replace(old_find_free, new_find_free)

with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated BuildingManager.java successfully!")
