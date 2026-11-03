import yaml
from collections import Counter

# Let's design full-sized, spacious RP-ready schematics with minimal interiors

# 1. Central Bank (1x1 chunk: 16x16)
# Footprint: 14x14 (x: 1..14, z: 1..14), Height: 6 layers (0..5)
def gen_bank():
    blocks = []
    # Layer 0 (Foundation/Floor): 14x14 floor perimeter & stone tiles
    for x in range(1, 15):
        for z in range(1, 15):
            if x == 1 or x == 14 or z == 1 or z == 14:
                blocks.append((x, 0, z, "STONE_BRICKS"))
            elif (x + z) % 2 == 0:
                blocks.append((x, 0, z, "STONE_BRICKS"))
            else:
                blocks.append((x, 0, z, "QUARTZ_BLOCK"))

    # Layer 1 (Walls, Entrance, Teller Counter & Vault)
    # Walls perimeter (entrance at z=1, x=7,8)
    for x in range(1, 15):
        for z in range(1, 15):
            if x == 1 or x == 14 or z == 1 or z == 14:
                if not (z == 1 and (x == 7 or x == 8)): # Grand entrance
                    blocks.append((x, 1, z, "STONE_BRICKS"))

    # Minimal Interior: Teller Counter (z=6, x=4..11) & Corner Vault (x=10..13, z=10..13)
    for x in range(4, 12):
        if x == 7: continue # Walkway behind counter
        blocks.append((x, 1, 6, "STONE_BRICKS"))
        blocks.append((x, 1, 6, "IRON_BARS")) # will be placed on layer 2
    # Corner Vault base (4 GOLD_BLOCK)
    blocks.append((11, 1, 11, "GOLD_BLOCK"))
    blocks.append((12, 1, 11, "GOLD_BLOCK"))
    blocks.append((11, 1, 12, "GOLD_BLOCK"))
    blocks.append((12, 1, 12, "GOLD_BLOCK"))

    # Vault partition bars
    blocks.append((10, 1, 11, "IRON_BARS"))
    blocks.append((10, 1, 12, "IRON_BARS"))
    blocks.append((11, 1, 10, "IRON_BARS"))
    blocks.append((12, 1, 10, "IRON_BARS"))

    # Layer 2 (Walls with windows, teller grates)
    for x in range(1, 15):
        for z in range(1, 15):
            if x == 1 or x == 14 or z == 1 or z == 14:
                # Windows on sides and back
                is_window = (x == 1 or x == 14) and (z in [4, 5, 10, 11]) or (z == 14 and x in [4, 5, 10, 11])
                if is_window:
                    blocks.append((x, 2, z, "IRON_BARS"))
                elif not (z == 1 and (x == 7 or x == 8)):
                    blocks.append((x, 2, z, "STONE_BRICKS"))

    # Teller grates (x=4..11, z=6)
    for x in range(4, 12):
        if x != 7:
            blocks.append((x, 2, 6, "IRON_BARS"))

    # Vault upper bars
    blocks.append((10, 2, 11, "IRON_BARS"))
    blocks.append((10, 2, 12, "IRON_BARS"))
    blocks.append((11, 2, 10, "IRON_BARS"))
    blocks.append((12, 2, 10, "IRON_BARS"))

    # Layer 3 (Upper Walls with window arches)
    for x in range(1, 15):
        for z in range(1, 15):
            if x == 1 or x == 14 or z == 1 or z == 14:
                is_window = (x == 1 or x == 14) and (z in [4, 5, 10, 11]) or (z == 14 and x in [4, 5, 10, 11])
                if is_window:
                    blocks.append((x, 3, z, "IRON_BARS"))
                else:
                    blocks.append((x, 3, z, "STONE_BRICKS"))

    # Layer 4 (Cornice / Architrave / Pillars top)
    for x in range(1, 15):
        for z in range(1, 15):
            if x == 1 or x == 14 or z == 1 or z == 14:
                blocks.append((x, 4, z, "STONE_BRICKS"))

    # Layer 5 (Spacious Classical Quartz Dome / Roof)
    for x in range(2, 14):
        for z in range(2, 14):
            blocks.append((x, 5, z, "QUARTZ_BLOCK"))

    return blocks

bank_blocks = gen_bank()
counts = Counter(b[3] for b in bank_blocks)
print("Bank total:", len(bank_blocks), counts)

