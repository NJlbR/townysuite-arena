from collections import Counter
import re

# 1. BANK (14x14 footprint, Height: 6 layers [0..5])
def gen_bank():
    blocks = []
    # Layer 0: Ground Foundation (14x14, perimeter stone bricks, center quartz floor)
    for x in range(1, 15):
        for z in range(1, 15):
            if x == 1 or x == 14 or z == 1 or z == 14:
                blocks.append((x, 0, z, "STONE_BRICKS"))
            elif (x >= 4 and x <= 11 and z >= 4 and z <= 11):
                blocks.append((x, 0, z, "QUARTZ_BLOCK"))
            else:
                blocks.append((x, 0, z, "STONE_BRICKS"))

    # Layer 1: Banking Hall Walls, Double Doorway, Teller Counter Base, Corner Vault Base
    for x in range(1, 15):
        for z in range(1, 15):
            if x == 1 or x == 14 or z == 1 or z == 14:
                if not (z == 1 and (x == 7 or x == 8)): # Grand entrance
                    blocks.append((x, 1, z, "STONE_BRICKS"))
    # Minimal Interior: Teller desk base (x=4..11, z=6)
    for x in [4, 5, 6, 9, 10, 11]:
        blocks.append((x, 1, 6, "STONE_BRICKS"))
    # Vault Base (x=11..12, z=11..12) - 4 Gold Blocks
    blocks.append((11, 1, 11, "GOLD_BLOCK"))
    blocks.append((12, 1, 11, "GOLD_BLOCK"))
    blocks.append((11, 1, 12, "GOLD_BLOCK"))
    blocks.append((12, 1, 12, "GOLD_BLOCK"))
    # Teller grates & vault security bars
    for x in [4, 5, 6, 9, 10, 11]:
        blocks.append((x, 1, 5, "IRON_BARS")) # Teller window
    for z in [10, 11, 12]:
        blocks.append((10, 1, z, "IRON_BARS"))
    for x in [11, 12]:
        blocks.append((x, 1, 10, "IRON_BARS"))

    # Layer 2: Walls with Large Windows & Upper Bars
    for x in range(1, 15):
        for z in range(1, 15):
            if x == 1 or x == 14 or z == 1 or z == 14:
                is_win = (x in [1, 14] and z in [4, 5, 10, 11]) or (z == 14 and x in [4, 5, 10, 11]) or (z == 1 and x in [3, 4, 11, 12])
                if is_win:
                    blocks.append((x, 2, z, "IRON_BARS"))
                elif not (z == 1 and (x == 7 or x == 8)):
                    blocks.append((x, 2, z, "STONE_BRICKS"))
    # Teller upper bars
    for x in [4, 5, 6, 9, 10, 11]:
        blocks.append((x, 2, 6, "IRON_BARS"))
    for z in [10, 11, 12]:
        blocks.append((10, 2, z, "IRON_BARS"))
    for x in [11, 12]:
        blocks.append((x, 2, 10, "IRON_BARS"))

    # Layer 3: Upper Wall Archways
    for x in range(1, 15):
        for z in range(1, 15):
            if x == 1 or x == 14 or z == 1 or z == 14:
                is_win = (x in [1, 14] and z in [4, 5, 10, 11]) or (z == 14 and x in [4, 5, 10, 11])
                if is_win:
                    blocks.append((x, 3, z, "IRON_BARS"))
                else:
                    blocks.append((x, 3, z, "STONE_BRICKS"))

    # Layer 4: Grand Cornice / Entablature (14x14 perimeter)
    for x in range(1, 15):
        for z in range(1, 15):
            if x == 1 or x == 14 or z == 1 or z == 14:
                blocks.append((x, 4, z, "STONE_BRICKS"))

    # Layer 5: Classical White Quartz Roof (12x12 dome/ceiling)
    for x in range(2, 14):
        for z in range(2, 14):
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

    # Layer 1: Lower Walls, Medical Reception Desk, Double Entrance
    for x in range(1, 15):
        for z in range(1, 15):
            if x == 1 or x == 14 or z == 1 or z == 14:
                if not (z == 1 and (x == 7 or x == 8)): # Main Hospital Doors
                    blocks.append((x, 1, z, "STONE_BRICKS"))
    # Minimal Interior: Reception desk (x=6..9, z=5)
    for x in [6, 7, 8, 9]:
        blocks.append((x, 1, 5, "WHITE_CONCRETE"))

    # Layer 2: Main Walls with Medical Red Cross Facade and Windows
    for x in range(1, 15):
        for z in range(1, 15):
            if x == 1 or x == 14 or z == 1 or z == 14:
                # Medical Cross on North facade (z=1, x=6..9) and South facade (z=14, x=6..9)
                is_cross_v = (z in [1, 14]) and (x in [7, 8])
                is_cross_h = (z in [1, 14]) and (x in [5, 6, 9, 10])
                is_win = (x in [1, 14]) and (z in [3, 4, 5, 9, 10, 11])
                if is_cross_v or is_cross_h:
                    blocks.append((x, 2, z, "RED_WOOL"))
                elif is_win:
                    blocks.append((x, 2, z, "GLASS"))
                elif not (z == 1 and (x == 7 or x == 8)):
                    blocks.append((x, 2, z, "WHITE_CONCRETE"))

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

    # Layer 4: Upper Trim & Parapet
    for x in range(1, 15):
        for z in range(1, 15):
            if x == 1 or x == 14 or z == 1 or z == 14:
                blocks.append((x, 4, z, "STONE_BRICKS"))

    # Layer 5: Clean White Hospital Roof
    for x in range(2, 14):
        for z in range(2, 14):
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

    # Layer 1: Stone Brick Pillars & Cobblestone Walls, Grand Double Gate (z=2, x=7,8)
    for x in range(1, 15):
        for z in range(2, 30):
            if x == 1 or x == 14 or z == 2 or z == 29:
                if not (z == 2 and (x == 7 or x == 8)):
                    is_corner = (x in [1, 14] and z in [2, 15, 16, 29])
                    blocks.append((x, 1, z, "STONE_BRICKS" if is_corner else "COBBLESTONE"))
    # Minimal Interior: Armory heavy anvils / armor stations (4 IRON_BLOCK at back corner)
    blocks.append((12, 1, 26, "IRON_BLOCK"))
    blocks.append((13, 1, 26, "IRON_BLOCK"))
    blocks.append((12, 1, 27, "IRON_BLOCK"))
    blocks.append((13, 1, 27, "IRON_BLOCK"))
    # Bunk partition bases (minimal)
    for z in [8, 14, 20]:
        blocks.append((2, 1, z, "OAK_PLANKS"))
        blocks.append((13, 1, z, "OAK_PLANKS"))

    # Layer 2: Walls with Slit Windows
    for x in range(1, 15):
        for z in range(2, 30):
            if x == 1 or x == 14 or z == 2 or z == 29:
                if not (z == 2 and (x == 7 or x == 8)):
                    is_corner = (x in [1, 14] and z in [2, 15, 16, 29])
                    blocks.append((x, 2, z, "STONE_BRICKS" if is_corner else "COBBLESTONE"))

    # Layer 3: Upper Perimeter Truss Base
    for x in range(1, 15):
        for z in range(2, 30):
            if x == 1 or x == 14 or z == 2 or z == 29:
                blocks.append((x, 3, z, "STONE_BRICKS"))

    # Layer 4: Timber Roof (Oak Planks rafters & ceiling)
    for x in range(2, 14):
        for z in range(3, 29):
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
                blocks.append((x, 0, z, "OBSIDIAN")) # Arcane Altar Floor (16 blocks)
            else:
                blocks.append((x, 0, z, "DARK_OAK_PLANKS"))

    # Layer 1: Exterior Walls, Entrance, Bookcase Stacks, Lapis Mana Pillars
    for x in range(1, 15):
        for z in range(1, 15):
            if x == 1 or x == 14 or z == 1 or z == 14:
                if not (z == 1 and (x == 7 or x == 8)):
                    blocks.append((x, 1, z, "DARK_OAK_PLANKS"))
    # Perimeter Grand Bookcase Stacks (x=3..5, 10..12 along walls)
    for x in [3, 4, 5, 10, 11, 12]:
        blocks.append((x, 1, 3, "BOOKSHELF"))
        blocks.append((x, 1, 12, "BOOKSHELF"))
    for z in [6, 7, 8, 9]:
        blocks.append((3, 1, z, "BOOKSHELF"))
        blocks.append((12, 1, z, "BOOKSHELF"))
    # 4 Lapis Mana Pillars in center corners (x in [5,10], z in [5,10])
    for x in [5, 10]:
        for z in [5, 10]:
            blocks.append((x, 1, z, "LAPIS_BLOCK"))

    # Layer 2: Second Tier Bookshelves & Walls
    for x in range(1, 15):
        for z in range(1, 15):
            if x == 1 or x == 14 or z == 1 or z == 14:
                if not (z == 1 and (x == 7 or x == 8)):
                    blocks.append((x, 2, z, "DARK_OAK_PLANKS"))
    # Tier 2 Bookcases
    for x in [3, 4, 5, 10, 11, 12]:
        blocks.append((x, 2, 3, "BOOKSHELF"))
        blocks.append((x, 2, 12, "BOOKSHELF"))
    for z in [6, 7, 8, 9]:
        blocks.append((3, 2, z, "BOOKSHELF"))
        blocks.append((12, 2, z, "BOOKSHELF"))
    # Lapis Mana Pillars upper
    for x in [5, 10]:
        for z in [5, 10]:
            blocks.append((x, 2, z, "LAPIS_BLOCK"))

    # Layer 3: Upper Gallery Walls
    for x in range(1, 15):
        for z in range(1, 15):
            if x == 1 or x == 14 or z == 1 or z == 14:
                blocks.append((x, 3, z, "DARK_OAK_PLANKS"))

    # Layer 4: Grand Dark Oak Library Ceiling / Roof
    for x in range(2, 14):
        for z in range(2, 14):
            blocks.append((x, 4, z, "DARK_OAK_PLANKS"))

    return blocks

# 5. WATCHTOWER (10x10 base, 8x8 shaft, 10x10 battlement crown, Height: 12 layers [0..11])
def gen_watchtower():
    blocks = []
    # Layer 0: Ground Foundation (10x10, x: 3..12, z: 3..12)
    for x in range(3, 13):
        for z in range(3, 13):
            if x == 3 or x == 12 or z == 3 or z == 12:
                blocks.append((x, 0, z, "STONE_BRICKS"))
            else:
                blocks.append((x, 0, z, "COBBLESTONE"))

    # Layers 1..2: Base Bastion (10x10 with arched door at z=3, x=7,8)
    for y in [1, 2]:
        for x in range(3, 13):
            for z in range(3, 13):
                if x == 3 or x == 12 or z == 3 or z == 12:
                    if not (y <= 2 and z == 3 and (x == 7 or x == 8)):
                        is_corner = (x in [3, 12] and z in [3, 12])
                        blocks.append((x, y, z, "STONE_BRICKS" if is_corner else "COBBLESTONE"))
        # Central ladder shaft (at x=8, z=8)
        blocks.append((8, y, 8, "LADDER"))

    # Layers 3..8: Tower Shaft (8x8, x: 4..11, z: 4..11)
    for y in range(3, 9):
        for x in range(4, 12):
            for z in range(4, 12):
                if x == 4 or x == 11 or z == 4 or z == 11:
                    is_corner = (x in [4, 11] and z in [4, 11])
                    blocks.append((x, y, z, "STONE_BRICKS" if is_corner else "COBBLESTONE"))
        # Ladder up through tower
        blocks.append((8, y, 8, "LADDER"))

    # Layer 9: Observation Platform Floor (10x10, x: 3..12, z: 3..12)
    for x in range(3, 13):
        for z in range(3, 13):
            blocks.append((x, 9, z, "STONE_BRICKS"))
    blocks.append((8, 9, 8, "LADDER"))

    # Layer 10: Battlements / Crenellations & Lanterns
    for x in range(3, 13):
        for z in range(3, 13):
            if x == 3 or x == 12 or z == 3 or z == 12:
                if (x + z) % 2 == 0:
                    blocks.append((x, 10, z, "STONE_BRICKS"))
    # 8 Lanterns at corners and midpoints
    for x, z in [(3, 3), (12, 3), (3, 12), (12, 12), (7, 3), (8, 3), (7, 12), (8, 12)]:
        blocks.append((x, 10, z, "LANTERN"))

    return blocks

# 6. SUN PYRAMID (28x28 base on 2x2 chunks, Height: 8 layers [0..7])
def gen_sun_pyramid():
    blocks = []
    # Layer 0: Monumental Outer Base (28x28, x: 2..29, z: 2..29)
    for x in range(2, 30):
        for z in range(2, 30):
            if x == 2 or x == 29 or z == 2 or z == 29:
                blocks.append((x, 0, z, "SANDSTONE"))
            elif (x >= 13 and x <= 18 and z >= 13 and z <= 18):
                blocks.append((x, 0, z, "GOLD_BLOCK")) # Sanctuary floor (36 gold)
            else:
                blocks.append((x, 0, z, "SANDSTONE"))

    # Layer 1: Terrace 1 (26x26, x: 3..28, z: 3..28) with Central Grand Stairway
    for x in range(3, 29):
        for z in range(3, 29):
            if x == 3 or x == 28 or z == 3 or z == 28:
                blocks.append((x, 1, z, "SANDSTONE"))
    # Layer 2: Terrace 2 (24x24, x: 4..27, z: 4..27)
    for x in range(4, 28):
        for z in range(4, 27):
            if x == 4 or x == 27 or z == 4 or z == 27:
                blocks.append((x, 2, z, "SANDSTONE"))
    # Layer 3: Terrace 3 (20x20, x: 6..25, z: 6..25)
    for x in range(6, 26):
        for z in range(6, 26):
            if x == 6 or x == 25 or z == 6 or z == 25:
                blocks.append((x, 3, z, "SANDSTONE"))
    # Layer 4: Terrace 4 (16x16, x: 8..23, z: 8..23)
    for x in range(8, 24):
        for z in range(8, 24):
            if x == 8 or x == 23 or z == 8 or z == 23:
                blocks.append((x, 4, z, "SANDSTONE"))
    # Layer 5: High Sanctuary Apex Platform (12x12, x: 10..21, z: 10..21)
    for x in range(10, 22):
        for z in range(10, 22):
            blocks.append((x, 5, z, "SANDSTONE"))
    # Layer 6: Apex Sun Shrine (Altar of the Sun: 1 Beacon & 1 Netherite Block)
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

