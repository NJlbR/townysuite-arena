# Generate Java code for generateTownHallSchematic and generateCityWallSchematic
import sys

def gen_city_wall():
    # 2x1 chunk footprint: widthX = 32, lengthZ = 16, heightY = 6
    # Symmetrical modular wall with end connector towers and middle pathway
    # DX from 0 to 31, DZ from 0 to 15.
    # At dx=0..3 and dx=28..31, and dz=0..3 and dz=12..15: Corner / junction bastions (6x6)
    # Wall body: dx=0..31, dz=5..10 (width 6 in Z, length 32 in X)
    # Walkway on top (Y=4): dz=6..9
    # Crenellations/battlement (Y=5): dz=5 and dz=10, alternating teeth
    # Junction corners (dx=0..5 and dz=0..15, and dx=26..31 and dz=0..15):
    # allow seamless connection in X (row) and in Z (right angle turn)!
    lines = []
    lines.append("    public BuildingSchematic generateCityWallSchematic() {")
    lines.append("        List<SchematicBlock> blocks = new ArrayList<>();")
    
    blocks = []
    # Layer 0..3: Wall Foundation and Body
    # Wall runs across X from 0 to 31. In Z, main wall is 5..10.
    # To connect at right angle (corner junctions):
    # Tower 1 at X=0..5, Z=0..15 (spans full 16 in Z at the west end!)
    # Tower 2 at X=26..31, Z=0..15 (spans full 16 in Z at the east end!)
    # Middle wall: X=6..25, Z=5..10
    
    for y in range(4): # Y=0,1,2,3
        mat_base = "Material.COBBLESTONE" if y == 0 else "Material.STONE_BRICKS"
        for x in range(32):
            for z in range(16):
                is_west_junction = (x <= 5) and (z >= 4 and z <= 11 or (z <= 3 and x <= 4) or (z >= 12 and x <= 4))
                is_east_junction = (x >= 26) and (z >= 4 and z <= 11 or (z <= 3 and x >= 27) or (z >= 12 and x >= 27))
                is_mid_wall = (x >= 6 and x <= 25) and (z >= 5 and z <= 10)
                
                # Corner tower corners (to seamlessly connect with perpendicular walls):
                is_corner_node = (x <= 4 and (z <= 4 or z >= 11)) or (x >= 27 and (z <= 4 or z >= 11))
                
                if is_west_junction or is_east_junction or is_mid_wall or is_corner_node:
                    # Inner hollow vs solid: let's make stone bricks and cobblestone accents
                    mat = mat_base
                    if (x + z + y) % 7 == 0:
                        mat = "Material.CRACKED_STONE_BRICKS"
                    elif y == 0:
                        mat = "Material.COBBLESTONE"
                    blocks.append((x, y, z, mat))
                    
    # Layer 4: Walkway and battlements floor (Y=4)
    y = 4
    for x in range(32):
        for z in range(16):
            is_walkway = (x >= 6 and x <= 25) and (z >= 5 and z <= 10)
            is_tower = (x <= 5 or x >= 26) and (z >= 3 and z <= 12)
            if is_walkway or is_tower:
                blocks.append((x, y, z, "Material.STONE_BRICKS"))
                
    # Layer 5: Battlements / Crenellations & Lanterns (Y=5)
    y = 5
    for x in range(32):
        # Outer parapet at z=5 and z=10
        if x >= 6 and x <= 25:
            if x % 2 == 0:
                blocks.append((x, y, 5, "Material.STONE_BRICKS"))
                blocks.append((x, y, 10, "Material.STONE_BRICKS"))
            else:
                blocks.append((x, y, 5, "Material.IRON_BARS"))
                blocks.append((x, y, 10, "Material.IRON_BARS"))
        # Towers battlements (X<=5 and X>=26)
        if x <= 5 or x >= 26:
            for z in [3, 12]:
                if (x + z) % 2 == 0:
                    blocks.append((x, y, z, "Material.STONE_BRICKS"))
            if x in [0, 5, 26, 31]:
                for z in range(4, 12):
                    if (x + z) % 2 == 0:
                        blocks.append((x, y, z, "Material.STONE_BRICKS"))
                        
    # Lanterns on towers at Y=5
    blocks.append((2, 5, 7, "Material.LANTERN"))
    blocks.append((2, 5, 8, "Material.LANTERN"))
    blocks.append((29, 5, 7, "Material.LANTERN"))
    blocks.append((29, 5, 8, "Material.LANTERN"))
    
    # Sort blocks by layer Y then X then Z
    blocks.sort(key=lambda b: (b[1], b[0], b[2]))
    
    # Count materials
    mat_counts = {}
    for b in blocks:
        mat_counts[b[3]] = mat_counts.get(b[3], 0) + 1
        lines.append(f"        blocks.add(new SchematicBlock({b[0]}, {b[1]}, {b[2]}, {b[3]}));")
        
    lines.append(f"        return new BuildingSchematic(\"city_wall\", 32, 6, 16, blocks);")
    lines.append("    }")
    
    print(f"City Wall total blocks: {len(blocks)}, counts: {mat_counts}")
    return "\n".join(lines), mat_counts

city_wall_code, wall_counts = gen_city_wall()

def gen_town_hall():
    # 2x2 chunk footprint: widthX = 32, lengthZ = 32, heightY = 8
    # Grand Town Hall with central courtyard / assembly hall, clock/bell tower, columns, gold treasury
    lines = []
    lines.append("    public BuildingSchematic generateTownHallSchematic() {")
    lines.append("        List<SchematicBlock> blocks = new ArrayList<>();")
    
    blocks = []
    # Layer 0: Ground Foundation (perimeter & floor)
    y = 0
    for x in range(4, 28):
        for z in range(4, 28):
            # Outer foundation
            if x == 4 or x == 27 or z == 4 or z == 27:
                blocks.append((x, y, z, "Material.DEEPSLATE_BRICKS"))
            else:
                blocks.append((x, y, z, "Material.STONE_BRICKS"))
                
    # Layer 1..3: Main Walls, Entrance Columns, Interior
    for y in [1, 2, 3]:
        for x in range(4, 28):
            for z in range(4, 28):
                is_outer = (x == 4 or x == 27 or z == 4 or z == 27)
                # Entrance door gap at z=4, x=15,16
                if is_outer:
                    if z == 4 and (x == 15 or x == 16) and y <= 2:
                        continue # Entrance
                    if y == 2 and is_outer and (x % 3 == 0 or z % 3 == 0):
                        blocks.append((x, y, z, "Material.GLASS"))
                    elif is_outer:
                        blocks.append((x, y, z, "Material.STONE_BRICKS"))
                # Interior Pillars
                if (x == 10 or x == 21) and (z == 10 or z == 21):
                    blocks.append((x, y, z, "Material.DEEPSLATE_BRICKS"))
                    
    # Treasury / Diplomacy Dais in the center at Y=1
    blocks.append((15, 1, 15, "Material.GOLD_BLOCK"))
    blocks.append((16, 1, 15, "Material.GOLD_BLOCK"))
    blocks.append((15, 1, 16, "Material.GOLD_BLOCK"))
    blocks.append((16, 1, 16, "Material.GOLD_BLOCK"))
    # Second gold tier
    blocks.append((15, 2, 15, "Material.GOLD_BLOCK"))
    blocks.append((16, 2, 15, "Material.GOLD_BLOCK"))
    blocks.append((15, 2, 16, "Material.GOLD_BLOCK"))
    blocks.append((16, 2, 16, "Material.GOLD_BLOCK"))
    
    # Layer 4: First floor ceiling / Second floor (Dark oak planks)
    y = 4
    for x in range(4, 28):
        for z in range(4, 28):
            blocks.append((x, y, z, "Material.DARK_OAK_PLANKS"))
            
    # Layer 5: Second floor parapet & Bell tower base
    y = 5
    for x in range(5, 27):
        for z in range(5, 27):
            is_parapet = (x == 5 or x == 26 or z == 5 or z == 26)
            is_tower_base = (x >= 12 and x <= 19) and (z >= 12 and z <= 19)
            if is_parapet:
                if (x + z) % 2 == 0:
                    blocks.append((x, y, z, "Material.STONE_BRICKS"))
                else:
                    blocks.append((x, y, z, "Material.IRON_BARS"))
            elif is_tower_base:
                blocks.append((x, y, z, "Material.DEEPSLATE_BRICKS"))
                
    # Layer 6: Bell Tower Columns and Arch
    y = 6
    for x in [12, 19]:
        for z in [12, 19]:
            blocks.append((x, y, z, "Material.DEEPSLATE_BRICKS"))
    blocks.append((15, y, 15, "Material.IRON_BARS"))
    blocks.append((16, y, 15, "Material.IRON_BARS"))
    blocks.append((15, y, 16, "Material.IRON_BARS"))
    blocks.append((16, y, 16, "Material.IRON_BARS"))
    # Lanterns
    blocks.append((6, y, 6, "Material.LANTERN"))
    blocks.append((25, y, 6, "Material.LANTERN"))
    blocks.append((6, y, 25, "Material.LANTERN"))
    blocks.append((25, y, 25, "Material.LANTERN"))
    
    # Layer 7: Bell Tower Roof with the City Bell!
    y = 7
    for x in range(12, 20):
        for z in range(12, 20):
            blocks.append((x, y, z, "Material.DARK_OAK_PLANKS"))
            
    # The sacred City Bell in the tower center at (15, 6, 15) or (16, 6, 16)
    blocks.append((15, 6, 16, "Material.BELL"))
    
    # Corner lanterns on tower top
    blocks.append((12, 7, 12, "Material.LANTERN"))
    blocks.append((19, 7, 12, "Material.LANTERN"))
    blocks.append((12, 7, 19, "Material.LANTERN"))
    blocks.append((19, 7, 19, "Material.LANTERN"))
    
    blocks.sort(key=lambda b: (b[1], b[0], b[2]))
    mat_counts = {}
    for b in blocks:
        mat_counts[b[3]] = mat_counts.get(b[3], 0) + 1
        lines.append(f"        blocks.add(new SchematicBlock({b[0]}, {b[1]}, {b[2]}, {b[3]}));")
        
    lines.append(f"        return new BuildingSchematic(\"town_hall\", 32, 8, 32, blocks);")
    lines.append("    }")
    
    print(f"Town Hall total blocks: {len(blocks)}, counts: {mat_counts}")
    return "\n".join(lines), mat_counts

town_hall_code, th_counts = gen_town_hall()

with open('generated_schematics.txt', 'w', encoding='utf-8') as f:
    f.write(city_wall_code + "\n\n" + town_hall_code)

print("Generated schematics code saved to generated_schematics.txt")
