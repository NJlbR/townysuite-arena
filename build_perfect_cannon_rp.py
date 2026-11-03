import os
import json
import zipfile
import base64
import hashlib
import struct
import zlib
import shutil

print("=== 1. Generating 64x64 Pixel-Art Texture PNG for Cannon ===")

def create_png(width, height, pixels):
    raw = bytearray()
    for y in range(height):
        raw.append(0) # filter type none
        for x in range(width):
            raw.extend(pixels[y][x])
    compressed = zlib.compress(bytes(raw), 9)
    
    def chunk(tag, data):
        c = struct.pack('>I', len(data)) + tag + data
        crc = struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
        return c + crc
        
    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0))
    png += chunk(b'IDAT', compressed)
    png += chunk(b'IEND', b'')
    return png

# Create a 64x64 texture map
# Layout:
# [0..16, 0..16]: Dark Oak Wood Planks (rich warm wood with grain)
# [16..32, 0..16]: Dark Oak Log / Timber (dark bark & wood core)
# [32..48, 0..16]: Cast Iron Gunmetal (charcoal slate metal with sheen)
# [48..64, 0..16]: Polished Brass & Gold (warm metallic gold with specular sheen)
# [0..16, 16..32]: Steel Wheel Rim & Rivets (metallic iron rim)
# [16..32, 16..32]: Barrel Muzzle Void (deep black bore)
# [32..64, 16..64]: Shaded metal & wood panels

width, height = 64, 64
pixels = [[(40, 40, 45, 255) for _ in range(width)] for _ in range(height)]

# Palette definitions (RGBA)
c_wood_base = (72, 44, 25, 255)
c_wood_dark = (50, 28, 14, 255)
c_wood_light = (92, 57, 33, 255)
c_wood_rivet = (35, 20, 10, 255)

c_log_base = (48, 29, 15, 255)
c_log_dark = (34, 19, 9, 255)
c_log_light = (64, 38, 20, 255)

c_iron_base = (42, 44, 48, 255)
c_iron_dark = (28, 30, 33, 255)
c_iron_light = (58, 62, 68, 255)
c_iron_sheen = (75, 80, 88, 255)

c_gold_base = (218, 145, 12, 255)
c_gold_dark = (156, 96, 5, 255)
c_gold_light = (245, 185, 45, 255)
c_gold_shine = (255, 225, 120, 255)

c_wheel_rim = (75, 78, 85, 255)
c_wheel_dark = (50, 52, 58, 255)
c_wheel_stud = (130, 135, 145, 255)

c_black_bore = (10, 10, 12, 255)

for y in range(height):
    for x in range(width):
        # 1. Dark Oak Wood [0..16, 0..16]
        if x < 16 and y < 16:
            if y in (3, 7, 11, 15) or x in (0, 15):
                pixels[y][x] = c_wood_dark
            elif (x + y * 3) % 5 == 0:
                pixels[y][x] = c_wood_light
            elif (x * 7 + y) % 11 == 0:
                pixels[y][x] = c_wood_rivet
            else:
                pixels[y][x] = c_wood_base

        # 2. Dark Oak Log Timber [16..32, 0..16]
        elif 16 <= x < 32 and y < 16:
            lx = x - 16
            if lx % 4 == 0:
                pixels[y][x] = c_log_dark
            elif (lx + y) % 3 == 0:
                pixels[y][x] = c_log_light
            else:
                pixels[y][x] = c_log_base

        # 3. Cast Iron Barrel [32..48, 0..16]
        elif 32 <= x < 48 and y < 16:
            ix = x - 32
            if y == 0 or y == 15 or ix == 0 or ix == 15:
                pixels[y][x] = c_iron_dark
            elif y in (3, 4):
                pixels[y][x] = c_iron_sheen # metallic highlight band
            elif (ix + y * 2) % 4 == 0:
                pixels[y][x] = c_iron_light
            else:
                pixels[y][x] = c_iron_base

        # 4. Polished Brass & Gold [48..64, 0..16]
        elif 48 <= x < 64 and y < 16:
            gx = x - 48
            if gx in (0, 15) or y in (0, 15):
                pixels[y][x] = c_gold_dark
            elif y in (2, 3):
                pixels[y][x] = c_gold_shine # gold highlight
            elif (gx + y) % 3 == 0:
                pixels[y][x] = c_gold_light
            else:
                pixels[y][x] = c_gold_base

        # 5. Wheel Rim [0..16, 16..32]
        elif x < 16 and 16 <= y < 32:
            wy = y - 16
            if x in (0, 1, 14, 15) or wy in (0, 1, 14, 15):
                pixels[y][x] = c_wheel_dark
            elif (x in (4, 11) and wy in (4, 11)):
                pixels[y][x] = c_wheel_stud # rivet
            else:
                pixels[y][x] = c_wheel_rim

        # 6. Muzzle Bore [16..32, 16..32]
        elif 16 <= x < 32 and 16 <= y < 32:
            pixels[y][x] = c_black_bore

        # 7. Remaining palette variations
        elif y >= 32:
            if x < 32:
                pixels[y][x] = c_iron_base if (x + y) % 2 == 0 else c_iron_dark
            else:
                pixels[y][x] = c_wood_base if (x + y) % 2 == 0 else c_wood_dark

png_bytes = create_png(width, height, pixels)
png_b64 = base64.b64encode(png_bytes).decode('utf-8')

print(f"Texture PNG created ({len(png_bytes)} bytes)")

# Ensure texture folders
tex_dirs = [
    "tmp_rp/assets/siegecannon/textures/item",
    "tmp_rp/assets/siegecannon/textures/block",
    "tmp_rp/assets/siegecannons/textures/item",
    "tmp_rp/assets/minecraft/textures/item",
    "tmp_rp/assets/minecraft/textures/block",
    "public/models"
]
for d in tex_dirs:
    os.makedirs(d, exist_ok=True)

# Write texture files in all required locations
with open("tmp_rp/assets/siegecannon/textures/item/cannon_tnt.png", "wb") as f:
    f.write(png_bytes)
with open("tmp_rp/assets/siegecannon/textures/item/cannon.png", "wb") as f:
    f.write(png_bytes)
with open("tmp_rp/assets/siegecannons/textures/item/cannon_tnt.png", "wb") as f:
    f.write(png_bytes)
with open("tmp_rp/assets/minecraft/textures/item/cannon_tnt.png", "wb") as f:
    f.write(png_bytes)
with open("public/models/cannon_tnt.png", "wb") as f:
    f.write(png_bytes)

print("Saved texture PNG in resource pack locations!")

# === 2. Build 100% Strict Blockbench & Minecraft JSON Model ===
# All textures reference "#0" which points to "siegecannon:item/cannon_tnt"
# UV coordinates mapped into the 64x64 texture map:
# Wood: [0, 0, 16, 16]
# Log: [16, 0, 32, 16]
# Iron/Barrel: [32, 0, 48, 16]
# Gold/Brass: [48, 0, 64, 16]
# Wheels: [0, 16, 16, 32]
# Bore: [16, 16, 32, 32]

cannon_json_model = {
    "credit": "SiegeCannon 3D Model for Minecraft 1.20-1.21+ (Blockbench)",
    "texture_size": [64, 64],
    "textures": {
        "0": "siegecannon:item/cannon_tnt",
        "particle": "siegecannon:item/cannon_tnt"
    },
    "elements": [
        # === CARRIAGE BASE & FRAME ===
        {
            "name": "carriage_bed",
            "from": [3, 1, 2],
            "to": [13, 3, 15],
            "faces": {
                "north": {"uv": [0, 0, 10, 2],  "texture": "#0"},
                "east":  {"uv": [0, 0, 13, 2],  "texture": "#0"},
                "south": {"uv": [0, 0, 10, 2],  "texture": "#0"},
                "west":  {"uv": [0, 0, 13, 2],  "texture": "#0"},
                "up":    {"uv": [0, 0, 10, 13], "texture": "#0"},
                "down":  {"uv": [0, 0, 10, 13], "texture": "#0"}
            }
        },
        {
            "name": "carriage_left_cheek",
            "from": [2, 2, 2],
            "to": [4, 7, 15],
            "faces": {
                "north": {"uv": [16, 0, 18, 5],  "texture": "#0"},
                "east":  {"uv": [16, 0, 29, 5],  "texture": "#0"},
                "south": {"uv": [16, 0, 18, 5],  "texture": "#0"},
                "west":  {"uv": [16, 0, 29, 5],  "texture": "#0"},
                "up":    {"uv": [32, 0, 34, 13], "texture": "#0"},
                "down":  {"uv": [16, 0, 18, 13], "texture": "#0"}
            }
        },
        {
            "name": "carriage_right_cheek",
            "from": [12, 2, 2],
            "to": [14, 7, 15],
            "faces": {
                "north": {"uv": [16, 0, 18, 5],  "texture": "#0"},
                "east":  {"uv": [16, 0, 29, 5],  "texture": "#0"},
                "south": {"uv": [16, 0, 18, 5],  "texture": "#0"},
                "west":  {"uv": [16, 0, 29, 5],  "texture": "#0"},
                "up":    {"uv": [32, 0, 34, 13], "texture": "#0"},
                "down":  {"uv": [16, 0, 18, 13], "texture": "#0"}
            }
        },
        {
            "name": "rear_trail_spade",
            "from": [5, 0.5, 13],
            "to": [11, 2.5, 16],
            "faces": {
                "north": {"uv": [32, 0, 38, 2],  "texture": "#0"},
                "east":  {"uv": [32, 0, 35, 2],  "texture": "#0"},
                "south": {"uv": [32, 0, 38, 2],  "texture": "#0"},
                "west":  {"uv": [32, 0, 35, 2],  "texture": "#0"},
                "up":    {"uv": [32, 0, 38, 3],  "texture": "#0"},
                "down":  {"uv": [32, 0, 38, 3],  "texture": "#0"}
            }
        },
        {
            "name": "elevation_wedge",
            "from": [6, 3, 9],
            "to": [10, 5, 13],
            "faces": {
                "north": {"uv": [32, 0, 36, 2], "texture": "#0"},
                "east":  {"uv": [32, 0, 36, 2], "texture": "#0"},
                "south": {"uv": [32, 0, 36, 2], "texture": "#0"},
                "west":  {"uv": [32, 0, 36, 2], "texture": "#0"},
                "up":    {"uv": [48, 0, 52, 4], "texture": "#0"},
                "down":  {"uv": [32, 0, 36, 4], "texture": "#0"}
            }
        },

        # === WHEELS & AXLE ===
        {
            "name": "axle_rod",
            "from": [1, 3.5, 7],
            "to": [15, 5, 8.5],
            "faces": {
                "north": {"uv": [32, 0, 46, 2],  "texture": "#0"},
                "east":  {"uv": [48, 0, 50, 2],  "texture": "#0"},
                "south": {"uv": [32, 0, 46, 2],  "texture": "#0"},
                "west":  {"uv": [48, 0, 50, 2],  "texture": "#0"},
                "up":    {"uv": [32, 0, 46, 2],  "texture": "#0"},
                "down":  {"uv": [32, 0, 46, 2],  "texture": "#0"}
            }
        },
        {
            "name": "left_wheel",
            "from": [0.5, 0.5, 4],
            "to": [2.5, 8.5, 11.5],
            "faces": {
                "north": {"uv": [0, 16, 2, 24],  "texture": "#0"},
                "east":  {"uv": [0, 0, 8, 8],    "texture": "#0"},
                "south": {"uv": [0, 16, 2, 24],  "texture": "#0"},
                "west":  {"uv": [0, 0, 8, 8],    "texture": "#0"},
                "up":    {"uv": [0, 16, 2, 24],  "texture": "#0"},
                "down":  {"uv": [0, 16, 2, 24],  "texture": "#0"}
            }
        },
        {
            "name": "left_hubcap",
            "from": [0, 3.5, 6.75],
            "to": [0.5, 5.5, 8.75],
            "faces": {
                "north": {"uv": [48, 0, 49, 2], "texture": "#0"},
                "east":  {"uv": [48, 0, 50, 2], "texture": "#0"},
                "south": {"uv": [48, 0, 49, 2], "texture": "#0"},
                "west":  {"uv": [48, 0, 50, 2], "texture": "#0"},
                "up":    {"uv": [48, 0, 49, 2], "texture": "#0"},
                "down":  {"uv": [48, 0, 49, 2], "texture": "#0"}
            }
        },
        {
            "name": "right_wheel",
            "from": [13.5, 0.5, 4],
            "to": [15.5, 8.5, 11.5],
            "faces": {
                "north": {"uv": [0, 16, 2, 24],  "texture": "#0"},
                "east":  {"uv": [0, 0, 8, 8],    "texture": "#0"},
                "south": {"uv": [0, 16, 2, 24],  "texture": "#0"},
                "west":  {"uv": [0, 0, 8, 8],    "texture": "#0"},
                "up":    {"uv": [0, 16, 2, 24],  "texture": "#0"},
                "down":  {"uv": [0, 16, 2, 24],  "texture": "#0"}
            }
        },
        {
            "name": "right_hubcap",
            "from": [15.5, 3.5, 6.75],
            "to": [16, 5.5, 8.75],
            "faces": {
                "north": {"uv": [48, 0, 49, 2], "texture": "#0"},
                "east":  {"uv": [48, 0, 50, 2], "texture": "#0"},
                "south": {"uv": [48, 0, 49, 2], "texture": "#0"},
                "west":  {"uv": [48, 0, 50, 2], "texture": "#0"},
                "up":    {"uv": [48, 0, 49, 2], "texture": "#0"},
                "down":  {"uv": [48, 0, 49, 2], "texture": "#0"}
            }
        },

        # === CANNON BARREL ===
        {
            "name": "cascabel_knob",
            "from": [7, 5.5, 13.5],
            "to": [9, 7.5, 15],
            "faces": {
                "north": {"uv": [32, 0, 34, 2], "texture": "#0"},
                "east":  {"uv": [32, 0, 34, 2], "texture": "#0"},
                "south": {"uv": [48, 0, 50, 2], "texture": "#0"},
                "west":  {"uv": [32, 0, 34, 2], "texture": "#0"},
                "up":    {"uv": [32, 0, 34, 2], "texture": "#0"},
                "down":  {"uv": [32, 0, 34, 2], "texture": "#0"}
            }
        },
        {
            "name": "breech_base",
            "from": [5, 4.5, 8],
            "to": [11, 8.5, 13.5],
            "faces": {
                "north": {"uv": [32, 0, 38, 4], "texture": "#0"},
                "east":  {"uv": [32, 0, 38, 4], "texture": "#0"},
                "south": {"uv": [32, 0, 38, 4], "texture": "#0"},
                "west":  {"uv": [32, 0, 38, 4], "texture": "#0"},
                "up":    {"uv": [32, 0, 38, 6], "texture": "#0"},
                "down":  {"uv": [32, 0, 38, 6], "texture": "#0"}
            }
        },
        {
            "name": "breech_ring",
            "from": [4.75, 4.25, 10.5],
            "to": [11.25, 8.75, 12],
            "faces": {
                "north": {"uv": [48, 0, 54, 4], "texture": "#0"},
                "east":  {"uv": [48, 0, 50, 4], "texture": "#0"},
                "south": {"uv": [48, 0, 54, 4], "texture": "#0"},
                "west":  {"uv": [48, 0, 50, 4], "texture": "#0"},
                "up":    {"uv": [48, 0, 54, 2], "texture": "#0"},
                "down":  {"uv": [48, 0, 54, 2], "texture": "#0"}
            }
        },
        {
            "name": "trunnions_pivot",
            "from": [2, 5.5, 7],
            "to": [14, 7.5, 9],
            "faces": {
                "north": {"uv": [32, 0, 44, 2], "texture": "#0"},
                "east":  {"uv": [48, 0, 50, 2], "texture": "#0"},
                "south": {"uv": [32, 0, 44, 2], "texture": "#0"},
                "west":  {"uv": [48, 0, 50, 2], "texture": "#0"},
                "up":    {"uv": [32, 0, 44, 2], "texture": "#0"},
                "down":  {"uv": [32, 0, 44, 2], "texture": "#0"}
            }
        },
        {
            "name": "barrel_mid",
            "from": [5.5, 5, 3],
            "to": [10.5, 8, 8],
            "faces": {
                "north": {"uv": [32, 0, 37, 3], "texture": "#0"},
                "east":  {"uv": [32, 0, 37, 3], "texture": "#0"},
                "south": {"uv": [32, 0, 37, 3], "texture": "#0"},
                "west":  {"uv": [32, 0, 37, 3], "texture": "#0"},
                "up":    {"uv": [32, 0, 37, 5], "texture": "#0"},
                "down":  {"uv": [32, 0, 37, 5], "texture": "#0"}
            }
        },
        {
            "name": "barrel_chase",
            "from": [6, 5.25, 0.5],
            "to": [10, 7.75, 3],
            "faces": {
                "north": {"uv": [32, 0, 36, 3], "texture": "#0"},
                "east":  {"uv": [32, 0, 35, 3], "texture": "#0"},
                "south": {"uv": [32, 0, 36, 3], "texture": "#0"},
                "west":  {"uv": [32, 0, 35, 3], "texture": "#0"},
                "up":    {"uv": [32, 0, 36, 3], "texture": "#0"},
                "down":  {"uv": [32, 0, 36, 3], "texture": "#0"}
            }
        },
        {
            "name": "muzzle_ring",
            "from": [5.5, 4.75, 0],
            "to": [10.5, 8.25, 1],
            "faces": {
                "north": {"uv": [48, 0, 53, 4], "texture": "#0"},
                "east":  {"uv": [32, 0, 33, 4], "texture": "#0"},
                "south": {"uv": [32, 0, 37, 4], "texture": "#0"},
                "west":  {"uv": [32, 0, 33, 4], "texture": "#0"},
                "up":    {"uv": [48, 0, 53, 1], "texture": "#0"},
                "down":  {"uv": [48, 0, 53, 1], "texture": "#0"}
            }
        },
        {
            "name": "muzzle_bore",
            "from": [6.5, 5.75, 0],
            "to": [9.5, 7.25, 0.1],
            "faces": {
                "north": {"uv": [16, 16, 19, 18], "texture": "#0"},
                "east":  {"uv": [16, 16, 17, 18], "texture": "#0"},
                "south": {"uv": [16, 16, 19, 18], "texture": "#0"},
                "west":  {"uv": [16, 16, 17, 18], "texture": "#0"},
                "up":    {"uv": [16, 16, 19, 17], "texture": "#0"},
                "down":  {"uv": [16, 16, 19, 17], "texture": "#0"}
            }
        },
        {
            "name": "touchhole_fuse",
            "from": [7.5, 8.5, 10.5],
            "to": [8.5, 9.5, 11.5],
            "faces": {
                "north": {"uv": [48, 0, 49, 1], "texture": "#0"},
                "east":  {"uv": [48, 0, 49, 1], "texture": "#0"},
                "south": {"uv": [48, 0, 49, 1], "texture": "#0"},
                "west":  {"uv": [48, 0, 49, 1], "texture": "#0"},
                "up":    {"uv": [48, 0, 49, 1], "texture": "#0"},
                "down":  {"uv": [48, 0, 49, 1], "texture": "#0"}
            }
        }
    ],
    "display": {
        "thirdperson_righthand": {
            "rotation": [75, 45, 0],
            "translation": [0, 2.5, 0],
            "scale": [0.375, 0.375, 0.375]
        },
        "thirdperson_lefthand": {
            "rotation": [75, 45, 0],
            "translation": [0, 2.5, 0],
            "scale": [0.375, 0.375, 0.375]
        },
        "firstperson_righthand": {
            "rotation": [0, 45, 0],
            "translation": [0, 0, 0],
            "scale": [0.4, 0.4, 0.4]
        },
        "firstperson_lefthand": {
            "rotation": [0, 225, 0],
            "translation": [0, 0, 0],
            "scale": [0.4, 0.4, 0.4]
        },
        "ground": {
            "rotation": [0, 0, 0],
            "translation": [0, 3, 0],
            "scale": [0.55, 0.55, 0.55]
        },
        "gui": {
            "rotation": [30, 225, 0],
            "translation": [0, 0, 0],
            "scale": [0.625, 0.625, 0.625]
        },
        "head": {
            "rotation": [0, 180, 0],
            "translation": [0, 0, 0],
            "scale": [1.6, 1.6, 1.6]
        },
        "fixed": {
            "rotation": [0, 180, 0],
            "translation": [0, 0, 0],
            "scale": [1, 1, 1]
        }
    }
}

json_str = json.dumps(cannon_json_model, indent=2, ensure_ascii=False)

# Write to all JSON model paths
model_destinations = [
    "tmp_rp/assets/siegecannon/models/item/cannon_tnt.json",
    "tmp_rp/assets/siegecannon/models/item/cannon.json",
    "tmp_rp/assets/siegecannon/models/block/cannon_tnt.json",
    "tmp_rp/assets/siegecannons/models/item/cannon_tnt.json",
    "tmp_rp/assets/siegecannons/models/block/cannon_tnt.json",
    "tmp_rp/assets/minecraft/models/item/cannon_tnt.json",
    "public/models/cannon_1x1.json",
    "dist/models/cannon_1x1.json"
]

for p in model_destinations:
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(json_str)

# === 3. Create .bbmodel with EMBEDDED TEXTURE ===
# When opened in Blockbench, Blockbench immediately uses the embedded texture!
bbmodel = {
    "meta": {
        "format_version": "4.10",
        "model_format": "java_block",
        "box_uv": False
    },
    "name": "cannon_tnt",
    "model_identifier": "cannon_tnt",
    "visible_box": [1, 1, 0],
    "resolution": {
        "width": 64,
        "height": 64
    },
    "elements": [],
    "outliner": [
        {
            "name": "Carriage",
            "origin": [8, 4, 8],
            "color": 0,
            "children": [0, 1, 2, 3, 4]
        },
        {
            "name": "Wheels",
            "origin": [8, 4, 7],
            "color": 1,
            "children": [5, 6, 7, 8, 9]
        },
        {
            "name": "Barrel",
            "origin": [8, 6.5, 7.5],
            "color": 2,
            "children": [10, 11, 12, 13, 14, 15, 16, 17, 18]
        }
    ],
    "textures": [
        {
            "path": "item/cannon_tnt",
            "name": "cannon_tnt",
            "folder": "item",
            "namespace": "siegecannon",
            "id": "0",
            "particle": True,
            "render_mode": "default",
            "visible": True,
            "mode": "bitmap",
            "saved": True,
            "uuid": "e1f2a3b4-c5d6-7e8f-9a0b-1c2d3e4f5a6b",
            "source": f"data:image/png;base64,{png_b64}"
        }
    ],
    "display": cannon_json_model["display"]
}

for idx, el in enumerate(cannon_json_model["elements"]):
    bb_el = {
        "name": el["name"],
        "box_uv": False,
        "rescale": False,
        "locked": False,
        "from": el["from"],
        "to": el["to"],
        "autouv": 0,
        "color": idx % 8,
        "uuid": f"c{idx:02d}e0000-0000-0000-0000-0000000000{idx:02d}",
        "type": "cube",
        "faces": {}
    }
    for face, face_data in el["faces"].items():
        bb_el["faces"][face] = {
            "uv": face_data["uv"],
            "texture": 0
        }
    bbmodel["elements"].append(bb_el)

bbmodel_str = json.dumps(bbmodel, indent=2, ensure_ascii=False)
with open("public/models/cannon_1x1.bbmodel", "w", encoding="utf-8") as f:
    f.write(bbmodel_str)
with open("dist/models/cannon_1x1.bbmodel", "w", encoding="utf-8") as f:
    f.write(bbmodel_str)

# === 4. Create Texture Atlas Configuration (assets/minecraft/atlases/blocks.json) ===
# This tells modern Minecraft 1.20+ to explicitly register the siegecannon textures into the texture atlas!
atlas_dir = "tmp_rp/assets/minecraft/atlases"
os.makedirs(atlas_dir, exist_ok=True)
atlas_config = {
    "sources": [
        {
            "type": "directory",
            "source": "item",
            "prefix": "item/"
        },
        {
            "type": "single",
            "resource": "siegecannon:item/cannon_tnt"
        },
        {
            "type": "single",
            "resource": "siegecannon:item/cannon"
        }
    ]
}
with open(os.path.join(atlas_dir, "blocks.json"), "w", encoding="utf-8") as f:
    json.dump(atlas_config, f, indent=2)

# === 5. Create Overrides in tnt.json ===
tnt_override = {
    "parent": "minecraft:block/tnt",
    "overrides": [
        {"predicate": {"custom_model_data": 1}, "model": "siegecannon:item/cannon_tnt"},
        {"predicate": {"custom_model_data": 2}, "model": "siegecannon:item/cannon_tnt"},
        {"predicate": {"custom_model_data": 100}, "model": "siegecannon:item/cannon_tnt"},
        {"predicate": {"custom_model_data": 1001}, "model": "siegecannon:item/cannon_tnt"},
        {"predicate": {"custom_model_data": 7001}, "model": "siegecannon:item/cannon_tnt"}
    ]
}
with open("tmp_rp/assets/minecraft/models/item/tnt.json", "w", encoding="utf-8") as f:
    json.dump(tnt_override, f, indent=2)

# === 6. Package all Resource Packs ===
zip_targets = [
    'public/TownyArchitecture.zip',
    'dist/TownyArchitecture.zip',
    'public/TownyArchitecture-Modern-RP.zip',
    'dist/TownyArchitecture-Modern-RP.zip',
    'public/TownyArchitecture-RP.zip',
    'dist/TownyArchitecture-RP.zip',
    'public/SiegeCannon-3D-Model-RP.zip',
    'dist/SiegeCannon-3D-Model-RP.zip'
]

for target in zip_targets:
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in sorted(os.walk("tmp_rp")):
            for file in sorted(files):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, "tmp_rp").replace('\\', '/')
                zf.write(full_path, rel_path)

with open('public/TownyArchitecture.zip', 'rb') as f:
    zip_bytes = f.read()

sha1 = hashlib.sha1(zip_bytes).hexdigest()
sha256 = hashlib.sha256(zip_bytes).hexdigest()
b64 = base64.b64encode(zip_bytes).decode('ascii')

with open('src/data/resourcePackBase64.ts', 'w', encoding='utf-8') as f:
    f.write(f'export const RESOURCE_PACK_BASE64 = "{b64}";\n')
    f.write(f'export const RESOURCE_PACK_SHA1 = "{sha1}";\n')
    f.write(f'export const RESOURCE_PACK_SHA256 = "{sha256}";\n')
    f.write(f'export const RESOURCE_PACK_SIZE = {len(zip_bytes)};\n')

# Refresh bundles
bundle_targets = [
    'dist/TownyArchitecture-v2.8.2-bundle.zip',
    'public/TownyArchitecture-v2.8.2-bundle.zip',
    'dist/TownyArchitecture-bundle.zip',
    'public/TownyArchitecture-bundle.zip'
]

for bt in bundle_targets:
    with zipfile.ZipFile(bt, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write('dist/TownyArchitecture-2.8.2.jar', 'TownyArchitecture-2.8.2.jar')
        zf.write('dist/TownyArchitecture.jar', 'TownyArchitecture.jar')
        zf.write('public/TownyArchitecture.zip', 'TownyArchitecture.zip')
        zf.write('public/TownyArchitecture-RP.zip', 'TownyArchitecture-RP.zip')
        if os.path.exists('tmp/minecraft-build-v2/src/main/resources/config.yml'):
            zf.write('tmp/minecraft-build-v2/src/main/resources/config.yml', 'config.yml')
        if os.path.exists('tmp/minecraft-build-v2/src/main/resources/buildings.yml'):
            zf.write('tmp/minecraft-build-v2/src/main/resources/buildings.yml', 'buildings.yml')

# Update TS Data
ts_content = f"""// Auto-generated 3D Cannon Model Data with Embedded Texture
export const CANNON_MODEL_JSON = {json.dumps(cannon_json_model, indent=2, ensure_ascii=False)};

export const CANNON_MODEL_JSON_STR = {json.dumps(json_str)};
export const CANNON_BBMODEL_JSON_STR = {json.dumps(bbmodel_str)};

export const CANNON_JSON_BASE64 = "{base64.b64encode(json_str.encode('utf-8')).decode('ascii')}";
export const CANNON_BBMODEL_BASE64 = "{base64.b64encode(bbmodel_str.encode('utf-8')).decode('ascii')}";
export const CANNON_RP_BASE64 = "{b64}";

export const CANNON_METADATA = {{
  name: "3D Осадная Пушка (1x1 Блок)",
  fileJsonName: "cannon_1x1.json",
  fileBbmodelName: "cannon_1x1.bbmodel",
  fileRpName: "SiegeCannon-3D-Model-RP.zip",
  elementsCount: {len(cannon_json_model["elements"])},
  format: "Blockbench / Minecraft Java 1.20 - 1.21+ (Texture Atlas Embedded)",
  customModelData: 7001,
  targetItem: "siegecannon:cannon_tnt / tnt",
  dimensions: "16x16x16 (В точности 1x1 блок Minecraft)",
  author: "TownyArchitecture & SiegeCannon Team",
  releaseDate: "2026-10-04"
}};
"""

with open("src/data/cannonModelData.ts", "w", encoding="utf-8") as f:
    f.write(ts_content)

print(f"All done! New SHA-1: {sha1}")
