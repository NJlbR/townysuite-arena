import re

with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'r', encoding='utf-8') as f:
    code = f.read()

debug_code = """
        System.out.println("[TownyArchitecture] Scanning at X:" + testOriginX + " Z:" + testOriginZ + " from Y:" + minY + " to " + maxY);
        int maxLayer0Matches = 0;
        int maxLayer0Total = layer0.size();

        for (int testOriginY = minY; testOriginY <= maxY; testOriginY++) {
            int layer0Matches = 0;
            for (SchematicBlock sb : layer0) {
                int bx = testOriginX + sb.getDx();
                int by = testOriginY + sb.getDy();
                int bz = testOriginZ + sb.getDz();

                if (world.getBlockAt(bx, by, bz).getType() == sb.getMaterial()) {
                    layer0Matches++;
                }
            }
            if (layer0Matches > maxLayer0Matches) maxLayer0Matches = layer0Matches;

            double layer0Ratio = (double) layer0Matches / layer0.size();
            if (layer0Ratio >= 0.50 || (layer0Matches >= 3 && layer0Ratio >= 0.30)) {
                System.out.println("[TownyArchitecture] Found layer 0 match at Y:" + testOriginY + " with " + layer0Matches + "/" + layer0.size() + " blocks.");
"""

code = code.replace("        for (int testOriginY = minY; testOriginY <= maxY; testOriginY++) {", debug_code, 1)

with open('tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingManager.java', 'w', encoding='utf-8') as f:
    f.write(code)

print("Debug injected")
