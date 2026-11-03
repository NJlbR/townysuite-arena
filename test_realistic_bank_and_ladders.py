from collections import Counter

# 1. REALISTIC CENTRAL BANK (14x14 footprint, Height: 6 layers [0..5])
def gen_bank():
    blocks = []
    # Layer 0: Ground Foundation (14x14) - Stone Brick perimeter, polished checkered lobby floor
    for x in range(1, 15):
        for z in range(1, 15):
            if x == 1 or x == 14 or z == 1 or z == 14:
                blocks.append((x, 0, z, "STONE_BRICKS"))
            elif (x >= 4 and x <= 11 and z >= 3 and z <= 6): # Client main lobby
                blocks.append((x, 0, z, "QUARTZ_BLOCK"))
            else:
                blocks.append((x, 0, z, "STONE_BRICKS"))

    # Layer 1: Banking Hall (Client Lobby in front z=2..5, Teller Counter at z=6, Staff & Vault in back z=7..13)
    # Outer walls with 2-block wide grand entrance at z=1, x=7,8
    for x in range(1, 15):
        for z in range(1, 15):
            if x == 1 or x == 14 or z == 1 or z == 14:
                if not (z == 1 and (x == 7 or x == 8)):
                    blocks.append((x, 1, z, "STONE_BRICKS"))

    # Realistic Teller Counter (z=6, x=3..10 with staff service opening at x=11,12)
    for x in [3, 4, 5, 7, 8, 9]:
        blocks.append((x, 1, 6, "STONE_BRICKS")) # Solid teller desk base
    # Teller window glass/grate (x in [3,4,5, 7,8,9], z=6)
    for x in [3, 4, 5, 7, 8, 9]:
        blocks.append((x, 1, 5, "IRON_BARS")) # Customer service counter grill

    # Staff Security Partition Doorway at x=11, z=6
    blocks.append((11, 1, 6, "IRON_BARS"))

    # Realistic Reinforced Corner Bank Vault (x=10..13, z=9..13)
    # Vault outer security partition
    for z in [9, 10]:
        blocks.append((9, 1, z, "STONE_BRICKS"))
    for x in [10, 11, 12]:
        blocks.append((x, 1, 9, "STONE_BRICKS"))
    # Vault Doorway at x=9, z=11,12
    blocks.append((9, 1, 11, "IRON_BARS"))
    blocks.append((9, 1, 12, "IRON_BARS"))
    # Inside Vault: Gold bullion reserve (4 Gold blocks in corner)
    blocks.append((12, 1, 11, "GOLD_BLOCK"))
    blocks.append((13, 1, 11, "GOLD_BLOCK"))
    blocks.append((12, 1, 12, "GOLD_BLOCK"))
    blocks.append((13, 1, 12, "GOLD_BLOCK"))

    # Roof Access Ladder in Staff-only corner (x=2, z=13) - on Layer 1
    blocks.append((2, 1, 13, "LADDER"))

    # Layer 2: Main Walls, Large Windows, Upper Teller Grilles, Vault Walls
    for x in range(1, 15):
        for z in range(1, 15):
            if x == 1 or x == 14 or z == 1 or z == 14:
                is_win = (x in [1, 14] and z in [3, 4, 8, 9]) or (z == 14 and x in [4, 5, 10, 11])
                if is_win:
                    blocks.append((x, 2, z, "IRON_BARS"))
                elif not (z == 1 and (x == 7 or x == 8)): # Grand door open!
                    blocks.append((x, 2, z, "STONE_BRICKS"))

    # Upper teller window bars
    for x in [3, 4, 5, 7, 8, 9]:
        blocks.append((x, 2, 6, "IRON_BARS"))
    blocks.append((11, 2, 6, "IRON_BARS")) # Staff door upper

    # Upper vault partition walls & security gate
    for z in [9, 10]:
        blocks.append((9, 2, z, "STONE_BRICKS"))
    for x in [10, 11, 12]:
        blocks.append((x, 2, 9, "STONE_BRICKS"))
    blocks.append((9, 2, 11, "IRON_BARS"))
    blocks.append((9, 2, 12, "IRON_BARS"))

    # Roof Access Ladder on Layer 2
    blocks.append((2, 2, 13, "LADDER"))

    # Layer 3: Upper Wall Archways (Doorway topped with arch)
    for x in range(1, 15):
        for z in range(1, 15):
            if x == 1 or x == 14 or z == 1 or z == 14:
                is_win = (x in [1, 14] and z in [3, 4, 8, 9]) or (z == 14 and x in [4, 5, 10, 11])
                if is_win:
                    blocks.append((x, 3, z, "IRON_BARS"))
                else:
                    blocks.append((x, 3, z, "STONE_BRICKS"))

    # Vault reinforced ceiling / cap on layer 3
    for x in range(9, 14):
        for z in range(9, 14):
            blocks.append((x, 3, z, "STONE_BRICKS"))

    # Roof Access Ladder on Layer 3
    blocks.append((2, 3, 13, "LADDER"))

    # Layer 4: Grand Cornice / Entablature (14x14 perimeter)
    for x in range(1, 15):
        for z in range(1, 15):
            if x == 1 or x == 14 or z == 1 or z == 14:
                blocks.append((x, 4, z, "STONE_BRICKS"))
    # Roof Access Ladder on Layer 4 (top rung! stops BEFORE roof level 5)
    blocks.append((2, 4, 13, "LADDER"))

    # Layer 5: Classical White Quartz Roof with Open Hatch for Stairs/2nd floor (NO LADDER ON LAYER 5!)
    for x in range(2, 14):
        for z in range(2, 14):
            if not (x in [2, 3] and z in [12, 13]): # Hatch left completely clear for ceiling sealing
                blocks.append((x, 5, z, "QUARTZ_BLOCK"))

    return blocks

# 2. HOSPITAL (14x14 footprint, Height: 6 layers [0..5])
def gen_hospital():
    blocks = []
    # Layer 0: Foundation / Floor
    for x in range(1, 15):
        for z in range(1, 15):
            if x == 1 or x == 14 or z == 1 or z == 14:
                blocks.append((x, 0, z, "STONE_BRICKS"))
            else:
                blocks.append((x, 0, z, "WHITE_CONCRETE"))

    # Layer 1: Lower Walls (2-block tall double door at z=1, x=7,8 & back door at z=14, x=7,8)
    for x in range(1, 15):
        for z in range(1, 15):
            if x == 1 or x == 14 or z == 1 or z == 14:
                is_main_door = (z == 1 and (x == 7 or x == 8))
                is_back_door = (z == 14 and (x == 7 or x == 8))
                if not (is_main_door or is_back_door):
                    blocks.append((x, 1, z, "STONE_BRICKS"))
    # Reception desk
    for x in [5, 6]:
        blocks.append((x, 1, 5, "WHITE_CONCRETE"))
    # Ladder on Layer 1
    blocks.append((2, 1, 13, "LADDER"))

    # Layer 2: Main Walls with Full 2-block Tall Doors and Windows
    for x in range(1, 15):
        for z in range(1, 15):
            if x == 1 or x == 14 or z == 1 or z == 14:
                is_main_door = (z == 1 and (x == 7 or x == 8))
                is_back_door = (z == 14 and (x == 7 or x == 8))
                if is_main_door or is_back_door:
                    continue
                is_cross_h = (z in [1, 14]) and (x in [5, 6, 9, 10])
                is_win = (x in [1, 14]) and (z in [3, 4, 5, 9, 10, 11])
                if is_cross_h:
                    blocks.append((x, 2, z, "RED_WOOL"))
                elif is_win:
                    blocks.append((x, 2, z, "GLASS"))
                else:
                    blocks.append((x, 2, z, "WHITE_CONCRETE"))
    # Ladder on Layer 2
    blocks.append((2, 2, 13, "LADDER"))

    # Layer 3: Upper Walls with Windows and Red Cross top
    for x in range(1, 15):
        for z in range(1, 15):
            if x == 1 or x == 14 or z == 1 or z == 14:
                is_cross_v = (z in [1, 14]) and (x in [7, 8])
                is_win = (x in [1, 14]) and (z in [3, 4, 5, 9, 10, 11])
                if is_cross_v:
                    blocks.append((x, 3, z, "RED_WOOL"))
                elif is_win:
                    blocks.append((x, 3, z, "GLASS"))
                else:
                    blocks.append((x, 3, z, "WHITE_CONCRETE"))
    # Ladder on Layer 3
    blocks.append((2, 3, 13, "LADDER"))

    # Layer 4: Upper Trim & Parapet
    for x in range(1, 15):
        for z in range(1, 15):
            if x == 1 or x == 14 or z == 1 or z == 14:
                blocks.append((x, 4, z, "STONE_BRICKS"))
    # Ladder on Layer 4 (top rung! stops before roof level 5)
    blocks.append((2, 4, 13, "LADDER"))

    # Layer 5: Clean White Hospital Roof with 2x2 Hatch (NO LADDER ON LAYER 5!)
    for x in range(2, 14):
        for z in range(2, 14):
            if not (x in [2, 3] and z in [12, 13]):
                blocks.append((x, 5, z, "WHITE_CONCRETE"))

    return blocks

# 3. BARRACKS (14x28 footprint on 1x2 chunks, Height: 5 layers [0..4])
def gen_barracks():
    blocks = []
    # Layer 0: Ground Foundation (14x28)
    for x in range(1, 15):
        for z in range(2, 30):
            if x == 1 or x == 14 or z == 2 or z == 29:
                blocks.append((x, 0, z, "STONE_BRICKS"))
            elif (x + z) % 2 == 0:
                blocks.append((x, 0, z, "COBBLESTONE"))
            else:
                blocks.append((x, 0, z, "OAK_PLANKS"))

    # Layer 1: Stone Brick Pillars & Cobblestone Walls (2-block tall double gate)
    for x in range(1, 15):
        for z in range(2, 30):
            if x == 1 or x == 14 or z == 2 or z == 29:
                if not (z == 2 and (x == 7 or x == 8)):
                    is_corner = (x in [1, 14] and z in [2, 15, 16, 29])
                    blocks.append((x, 1, z, "STONE_BRICKS" if is_corner else "COBBLESTONE"))
    # Armory heavy anvils
    blocks.append((12, 1, 26, "IRON_BLOCK"))
    blocks.append((13, 1, 26, "IRON_BLOCK"))
    blocks.append((12, 1, 27, "IRON_BLOCK"))
    blocks.append((13, 1, 27, "IRON_BLOCK"))
    # Ladder on Layer 1
    blocks.append((2, 1, 28, "LADDER"))

    # Layer 2: Walls with Slit Windows (Gate open)
    for x in range(1, 15):
        for z in range(2, 30):
            if x == 1 or x == 14 or z == 2 or z == 29:
                if not (z == 2 and (x == 7 or x == 8)):
                    is_corner = (x in [1, 14] and z in [2, 15, 16, 29])
                    blocks.append((x, 2, z, "STONE_BRICKS" if is_corner else "COBBLESTONE"))
    # Ladder on Layer 2
    blocks.append((2, 2, 28, "LADDER"))

    # Layer 3: Upper Perimeter Truss Base
    for x in range(1, 15):
        for z in range(2, 30):
            if x == 1 or x == 14 or z == 2 or z == 29:
                blocks.append((x, 3, z, "STONE_BRICKS"))
    # Ladder on Layer 3 (top rung! stops before roof level 4)
    blocks.append((2, 3, 28, "LADDER"))

    # Layer 4: Timber Roof with Hatch (NO LADDER ON LAYER 4!)
    for x in range(2, 14):
        for z in range(3, 29):
            if not (x in [2, 3] and z in [27, 28]):
                blocks.append((x, 4, z, "OAK_PLANKS"))

    return blocks

# 4. LIBRARY (14x14 footprint, Height: 6 layers [0..5])
def gen_library():
    blocks = []
    # Layer 0: Dark Oak Parquet Floor & Obsidian Arcane Inlay
    for x in range(1, 15):
        for z in range(1, 15):
            if x == 1 or x == 14 or z == 1 or z == 14:
                blocks.append((x, 0, z, "DARK_OAK_PLANKS"))
            elif (x >= 6 and x <= 9 and z >= 6 and z <= 9):
                blocks.append((x, 0, z, "OBSIDIAN"))
            else:
                blocks.append((x, 0, z, "DARK_OAK_PLANKS"))

    # Layer 1: Exterior Walls (2-block tall double door at z=1, x=7,8)
    for x in range(1, 15):
        for z in range(1, 15):
            if x == 1 or x == 14 or z == 1 or z == 14:
                if not (z == 1 and (x == 7 or x == 8)):
                    blocks.append((x, 1, z, "DARK_OAK_PLANKS"))
    # Bookcase Stacks & Lapis Columns
    for x in [3, 4, 5, 10, 11, 12]:
        blocks.append((x, 1, 3, "BOOKSHELF"))
        blocks.append((x, 1, 12, "BOOKSHELF"))
    for z in [6, 7, 8, 9]:
        blocks.append((3, 1, z, "BOOKSHELF"))
        blocks.append((12, 1, z, "BOOKSHELF"))
    for x in [5, 10]:
        for z in [5, 10]:
            blocks.append((x, 1, z, "LAPIS_BLOCK"))
    # Ladder on Layer 1
    blocks.append((2, 1, 13, "LADDER"))

    # Layer 2: Tier 2 Bookcases & Walls (Door open)
    for x in range(1, 15):
        for z in range(1, 15):
            if x == 1 or x == 14 or z == 1 or z == 14:
                if not (z == 1 and (x == 7 or x == 8)):
                    blocks.append((x, 2, z, "DARK_OAK_PLANKS"))
    for x in [3, 4, 5, 10, 11, 12]:
        blocks.append((x, 2, 3, "BOOKSHELF"))
        blocks.append((x, 2, 12, "BOOKSHELF"))
    for z in [6, 7, 8, 9]:
        blocks.append((3, 2, z, "BOOKSHELF"))
        blocks.append((12, 2, z, "BOOKSHELF"))
    for x in [5, 10]:
        for z in [5, 10]:
            blocks.append((x, 2, z, "LAPIS_BLOCK"))
    # Ladder on Layer 2
    blocks.append((2, 2, 13, "LADDER"))

    # Layer 3: Upper Gallery Walls
    for x in range(1, 15):
        for z in range(1, 15):
            if x == 1 or x == 14 or z == 1 or z == 14:
                blocks.append((x, 3, z, "DARK_OAK_PLANKS"))
    # Ladder on Layer 3 (top rung! stops before roof level 4)
    blocks.append((2, 3, 13, "LADDER"))

    # Layer 4: Grand Dark Oak Library Ceiling / Roof with Hatch (NO LADDER ON LAYER 4!)
    for x in range(2, 14):
        for z in range(2, 14):
            if not (x in [2, 3] and z in [12, 13]):
                blocks.append((x, 4, z, "DARK_OAK_PLANKS"))

    return blocks

# 5. WATCHTOWER (10x10 base, 8x8 shaft, 10x10 battlement crown, Height: 12 layers [0..11])
def gen_watchtower():
    blocks = []
    # Layer 0: Ground Foundation (10x10)
    for x in range(3, 13):
        for z in range(3, 13):
            if x == 3 or x == 12 or z == 3 or z == 12:
                blocks.append((x, 0, z, "STONE_BRICKS"))
            else:
                blocks.append((x, 0, z, "COBBLESTONE"))

    # Layers 1..2: Base Bastion (10x10 with 2-block high door at z=3, x=7,8)
    for y in [1, 2]:
        for x in range(3, 13):
            for z in range(3, 13):
                if x == 3 or x == 12 or z == 3 or z == 12:
                    if not (z == 3 and (x == 7 or x == 8)):
                        is_corner = (x in [3, 12] and z in [3, 12])
                        blocks.append((x, y, z, "STONE_BRICKS" if is_corner else "COBBLESTONE"))
        blocks.append((8, y, 8, "LADDER"))

    # Layers 3..8: Tower Shaft (8x8)
    for y in range(3, 9):
        for x in range(4, 12):
            for z in range(4, 12):
                if x == 4 or x == 11 or z == 4 or z == 11:
                    is_corner = (x in [4, 11] and z in [4, 11])
                    blocks.append((x, y, z, "STONE_BRICKS" if is_corner else "COBBLESTONE"))
        blocks.append((8, y, 8, "LADDER"))

    # Layer 9: Observation Platform Floor (10x10) - ladder ends on Layer 8/9
    for x in range(3, 13):
        for z in range(3, 13):
            if not (x == 8 and z == 8):
                blocks.append((x, 9, z, "STONE_BRICKS"))

    # Layer 10: Battlements & Lanterns (NO LADDER ON LAYER 10!)
    for x in range(3, 13):
        for z in range(3, 13):
            if x == 3 or x == 12 or z == 3 or z == 12:
                if (x + z) % 2 == 0:
                    blocks.append((x, 10, z, "STONE_BRICKS"))
    for x, z in [(3, 3), (12, 3), (3, 12), (12, 12), (7, 3), (8, 3), (7, 12), (8, 12)]:
        blocks.append((x, 10, z, "LANTERN"))

    return blocks

# 6. SUN PYRAMID (28x28 base on 2x2 chunks, Height: 8 layers [0..7])
def gen_sun_pyramid():
    blocks = []
    # Layer 0: Monumental Outer Base (28x28)
    for x in range(2, 30):
        for z in range(2, 30):
            if x == 2 or x == 29 or z == 2 or z == 29:
                blocks.append((x, 0, z, "SANDSTONE"))
            elif (x >= 13 and x <= 18 and z >= 13 and z <= 18):
                blocks.append((x, 0, z, "GOLD_BLOCK"))
            else:
                blocks.append((x, 0, z, "SANDSTONE"))

    for x in range(3, 29):
        for z in range(3, 29):
            if x == 3 or x == 28 or z == 3 or z == 28:
                blocks.append((x, 1, z, "SANDSTONE"))
    for x in range(4, 28):
        for z in range(4, 27):
            if x == 4 or x == 27 or z == 4 or z == 27:
                blocks.append((x, 2, z, "SANDSTONE"))
    for x in range(6, 26):
        for z in range(6, 26):
            if x == 6 or x == 25 or z == 6 or z == 25:
                blocks.append((x, 3, z, "SANDSTONE"))
    for x in range(8, 24):
        for z in range(8, 24):
            if x == 8 or x == 23 or z == 8 or z == 23:
                blocks.append((x, 4, z, "SANDSTONE"))
    for x in range(10, 22):
        for z in range(10, 22):
            blocks.append((x, 5, z, "SANDSTONE"))
    blocks.append((15, 6, 15, "NETHERITE_BLOCK"))
    blocks.append((16, 6, 16, "BEACON"))

    return blocks

schems = {
    "bank": (gen_bank(), 16, 6, 16, "Central Bank", "Центральный Банк", "GOLD_INGOT", 5, False, 1, 1, 10, {"economy-access": True}, "#FFD700", "Позволяет жителям и мэру совершать финансовые операции (пополнять/снимать деньги казны) в радиусе 5 чанков."),
    "hospital": (gen_hospital(), 16, 6, 16, "City Hospital", "Городская Больница", "RED_WOOL", 20, False, 1, 1, 12, {"health-boost-hearts": 1, "regeneration-level": 1}, "#FF5555", "Дарует жителям +1 Сердце (2 HP) и регенерацию. Зона баффа: 5 чанков вокруг постройки (только гражданам города)."),
    "barracks": (gen_barracks(), 16, 5, 32, "Military Barracks", "Военные Казармы", "IRON_SWORD", 35, False, 1, 2, 10, {"strength-level": 1, "speed-level": 1}, "#FF4500", "Увеличивает силу и выносливость защитников. Зона баффа: ВСЯ ТЕРРИТОРИЯ ГОРОДА (только гражданам города)."),
    "library": (gen_library(), 16, 5, 16, "Arcane Library", "Библиотека Чар", "ENCHANTING_TABLE", 50, False, 1, 1, 14, {"haste-level": 1}, "#5555FF", "Бонус к опыту и спешка строителям. Зона баффа: 5 чанков вокруг постройки (только гражданам города)."),
    "watchtower": (gen_watchtower(), 16, 11, 16, "City Watchtower", "Дозорная Башня", "SPYGLASS", 15, False, 1, 1, 24, {"night-vision": True}, "#FFFF55", "Предупреждает о врагах и дает ночное зрение. Зона баффа: 5 чанков вокруг постройки (только гражданам города)."),
    "sun_pyramid": (gen_sun_pyramid(), 32, 7, 32, "Great Sun Pyramid", "Великая Пирамида Солнца", "GOLD_BLOCK", 80, True, 2, 2, 28, {"haste-level": 2, "resistance-level": 1}, "#FFAA00", "ЧУДО СВЕТА (2x2). 1 на весь мир! Спешка II и Сопротивление. Зона баффа: ВЕЗДЕ НА ВСЕЙ КАРТЕ (в любых мирах, но только для граждан этого города).")
}

for k, (blks, wx, hy, lz, name, name_ru, icon, req_lvl, is_wonder, cw, cl, dim_h, buffs, pcolor, desc) in schems.items():
    counts = Counter(b[3] for b in blks)
    print(f"=== {k} ({name_ru}) ===")
    print(f"Dimensions: {wx}x{hy}x{lz} (Chunks: {cw}x{cl})")
    print(f"Total Blocks: {len(blks)}")
    for mat, cnt in counts.items():
        print(f"  {mat}: {cnt}")
    print()

