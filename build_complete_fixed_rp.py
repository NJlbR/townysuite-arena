import os
import json
import zipfile
import base64
import hashlib
import struct
import zlib
import shutil

print("=== 1. Building Complete Fixed Resource Pack ===")

# --- 1.1 Generate 64x64 Texture PNG ---
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

width, height = 64, 64
pixels = [[(40, 40, 45, 255) for _ in range(width)] for _ in range(height)]

c_wood_base = (76, 47, 27, 255)
c_wood_dark = (52, 30, 16, 255)
c_wood_light = (96, 61, 36, 255)
c_wood_rivet = (38, 22, 12, 255)

c_log_base = (50, 31, 16, 255)
c_log_dark = (36, 20, 10, 255)
c_log_light = (68, 41, 22, 255)

c_iron_base = (45, 47, 52, 255)
c_iron_dark = (30, 32, 36, 255)
c_iron_light = (62, 66, 73, 255)
c_iron_sheen = (82, 88, 97, 255)

c_gold_base = (222, 150, 16, 255)
c_gold_dark = (162, 102, 8, 255)
c_gold_light = (250, 192, 52, 255)
c_gold_shine = (255, 230, 130, 255)

c_wheel_rim = (80, 84, 92, 255)
c_wheel_dark = (54, 57, 63, 255)
c_wheel_stud = (140, 145, 156, 255)

c_black_bore = (12, 12, 15, 255)

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
            if y in (0, 15) or ix in (0, 15):
                pixels[y][x] = c_iron_dark
            elif y in (3, 4):
                pixels[y][x] = c_iron_sheen
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
                pixels[y][x] = c_gold_shine
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
                pixels[y][x] = c_wheel_stud
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
print("Generated cannon_tnt.png texture!")

# Save to public/models and dist/models
os.makedirs("public/models", exist_ok=True)
os.makedirs("dist/models", exist_ok=True)
with open("public/models/cannon_tnt.png", "wb") as f:
    f.write(png_bytes)
with open("dist/models/cannon_tnt.png", "wb") as f:
    f.write(png_bytes)

# --- 1.2 Cannon 3D Elements with Strict 0..16 UV and Ground Alignment ---
def n_uv(u1, v1, u2, v2):
    return [round(u1 / 4.0, 3), round(v1 / 4.0, 3), round(u2 / 4.0, 3), round(v2 / 4.0, 3)]

def make_faces_norm(raw_faces):
    faces = {}
    for face, uv in raw_faces.items():
        faces[face] = {
            "uv": n_uv(uv[0], uv[1], uv[2], uv[3]),
            "texture": "#0"
        }
    return faces

cannon_elements_raw = [
    # 1. carriage_bed
    {
        "name": "carriage_bed",
        "from": [3, 1, 2],
        "to": [13, 3, 15],
        "raw_faces": {
            "north": [0, 0, 10, 2],
            "east":  [0, 0, 13, 2],
            "south": [0, 0, 10, 2],
            "west":  [0, 0, 13, 2],
            "up":    [0, 0, 10, 13],
            "down":  [0, 0, 10, 13]
        }
    },
    # 2. carriage_left_cheek
    {
        "name": "carriage_left_cheek",
        "from": [2, 2, 2],
        "to": [4, 7, 15],
        "raw_faces": {
            "north": [16, 0, 18, 5],
            "east":  [16, 0, 29, 5],
            "south": [16, 0, 18, 5],
            "west":  [16, 0, 29, 5],
            "up":    [32, 0, 34, 13],
            "down":  [16, 0, 18, 13]
        }
    },
    # 3. carriage_right_cheek
    {
        "name": "carriage_right_cheek",
        "from": [12, 2, 2],
        "to": [14, 7, 15],
        "raw_faces": {
            "north": [16, 0, 18, 5],
            "east":  [16, 0, 29, 5],
            "south": [16, 0, 18, 5],
            "west":  [16, 0, 29, 5],
            "up":    [32, 0, 34, 13],
            "down":  [16, 0, 18, 13]
        }
    },
    # 4. rear_trail_spade
    {
        "name": "rear_trail_spade",
        "from": [5, 0.5, 13],
        "to": [11, 2.5, 16],
        "raw_faces": {
            "north": [32, 0, 38, 2],
            "east":  [32, 0, 35, 2],
            "south": [32, 0, 38, 2],
            "west":  [32, 0, 35, 2],
            "up":    [32, 0, 38, 3],
            "down":  [32, 0, 38, 3]
        }
    },
    # 5. elevation_wedge
    {
        "name": "elevation_wedge",
        "from": [6, 3, 9],
        "to": [10, 5, 13],
        "raw_faces": {
            "north": [32, 0, 36, 2],
            "east":  [32, 0, 36, 2],
            "south": [32, 0, 36, 2],
            "west":  [32, 0, 36, 2],
            "up":    [48, 0, 52, 4],
            "down":  [32, 0, 36, 4]
        }
    },
    # 6. axle_rod
    {
        "name": "axle_rod",
        "from": [1, 3.5, 7],
        "to": [15, 5, 8.5],
        "raw_faces": {
            "north": [32, 0, 46, 2],
            "east":  [48, 0, 50, 2],
            "south": [32, 0, 46, 2],
            "west":  [48, 0, 50, 2],
            "up":    [32, 0, 46, 2],
            "down":  [32, 0, 46, 2]
        }
    },
    # 7. left_wheel
    {
        "name": "left_wheel",
        "from": [0.5, 0.5, 4],
        "to": [2.5, 8.5, 11.5],
        "raw_faces": {
            "north": [0, 16, 2, 24],
            "east":  [0, 16, 8, 24],
            "south": [0, 16, 2, 24],
            "west":  [0, 16, 8, 24],
            "up":    [0, 16, 2, 24],
            "down":  [0, 16, 2, 24]
        }
    },
    # 8. left_hubcap
    {
        "name": "left_hubcap",
        "from": [0, 3.5, 6.75],
        "to": [0.5, 5.5, 8.75],
        "raw_faces": {
            "north": [48, 0, 49, 2],
            "east":  [48, 0, 50, 2],
            "south": [48, 0, 49, 2],
            "west":  [48, 0, 50, 2],
            "up":    [48, 0, 49, 2],
            "down":  [48, 0, 49, 2]
        }
    },
    # 9. right_wheel
    {
        "name": "right_wheel",
        "from": [13.5, 0.5, 4],
        "to": [15.5, 8.5, 11.5],
        "raw_faces": {
            "north": [0, 16, 2, 24],
            "east":  [0, 16, 8, 24],
            "south": [0, 16, 2, 24],
            "west":  [0, 16, 8, 24],
            "up":    [0, 16, 2, 24],
            "down":  [0, 16, 2, 24]
        }
    },
    # 10. right_hubcap
    {
        "name": "right_hubcap",
        "from": [15.5, 3.5, 6.75],
        "to": [16, 5.5, 8.75],
        "raw_faces": {
            "north": [48, 0, 49, 2],
            "east":  [48, 0, 50, 2],
            "south": [48, 0, 49, 2],
            "west":  [48, 0, 50, 2],
            "up":    [48, 0, 49, 2],
            "down":  [48, 0, 49, 2]
        }
    },
    # 11. cascabel_knob
    {
        "name": "cascabel_knob",
        "from": [7, 5.5, 13.5],
        "to": [9, 7.5, 15],
        "raw_faces": {
            "north": [32, 0, 34, 2],
            "east":  [32, 0, 34, 2],
            "south": [48, 0, 50, 2],
            "west":  [32, 0, 34, 2],
            "up":    [32, 0, 34, 2],
            "down":  [32, 0, 34, 2]
        }
    },
    # 12. breech_base
    {
        "name": "breech_base",
        "from": [5, 4.5, 8],
        "to": [11, 8.5, 13.5],
        "raw_faces": {
            "north": [32, 0, 38, 4],
            "east":  [32, 0, 38, 4],
            "south": [32, 0, 38, 4],
            "west":  [32, 0, 38, 4],
            "up":    [32, 0, 38, 6],
            "down":  [32, 0, 38, 6]
        }
    },
    # 13. breech_ring
    {
        "name": "breech_ring",
        "from": [4.75, 4.25, 10.5],
        "to": [11.25, 8.75, 12],
        "raw_faces": {
            "north": [48, 0, 54, 4],
            "east":  [48, 0, 50, 4],
            "south": [48, 0, 54, 4],
            "west":  [48, 0, 50, 4],
            "up":    [48, 0, 54, 2],
            "down":  [48, 0, 54, 2]
        }
    },
    # 14. trunnions_pivot
    {
        "name": "trunnions_pivot",
        "from": [2, 5.5, 7],
        "to": [14, 7.5, 9],
        "raw_faces": {
            "north": [32, 0, 44, 2],
            "east":  [48, 0, 50, 2],
            "south": [32, 0, 44, 2],
            "west":  [48, 0, 50, 2],
            "up":    [32, 0, 44, 2],
            "down":  [32, 0, 44, 2]
        }
    },
    # 15. barrel_mid
    {
        "name": "barrel_mid",
        "from": [5.5, 5, 3],
        "to": [10.5, 8, 8],
        "raw_faces": {
            "north": [32, 0, 37, 3],
            "east":  [32, 0, 37, 3],
            "south": [32, 0, 37, 3],
            "west":  [32, 0, 37, 3],
            "up":    [32, 0, 37, 5],
            "down":  [32, 0, 37, 5]
        }
    },
    # 16. barrel_chase
    {
        "name": "barrel_chase",
        "from": [6, 5.25, 0.5],
        "to": [10, 7.75, 3],
        "raw_faces": {
            "north": [32, 0, 36, 3],
            "east":  [32, 0, 35, 3],
            "south": [32, 0, 36, 3],
            "west":  [32, 0, 35, 3],
            "up":    [32, 0, 36, 3],
            "down":  [32, 0, 36, 3]
        }
    },
    # 17. muzzle_ring
    {
        "name": "muzzle_ring",
        "from": [5.5, 4.75, 0],
        "to": [10.5, 8.25, 1],
        "raw_faces": {
            "north": [48, 0, 53, 4],
            "east":  [32, 0, 33, 4],
            "south": [32, 0, 37, 4],
            "west":  [32, 0, 33, 4],
            "up":    [48, 0, 53, 1],
            "down":  [48, 0, 53, 1]
        }
    },
    # 18. muzzle_bore
    {
        "name": "muzzle_bore",
        "from": [6.5, 5.75, 0],
        "to": [9.5, 7.25, 0.1],
        "raw_faces": {
            "north": [16, 16, 19, 18],
            "east":  [16, 16, 17, 18],
            "south": [16, 16, 19, 18],
            "west":  [16, 16, 17, 18],
            "up":    [16, 16, 19, 17],
            "down":  [16, 16, 19, 17]
        }
    },
    # 19. touchhole_fuse
    {
        "name": "touchhole_fuse",
        "from": [7.5, 8.5, 10.5],
        "to": [8.5, 9.5, 11.5],
        "raw_faces": {
            "north": [48, 0, 49, 1],
            "east":  [48, 0, 49, 1],
            "south": [48, 0, 49, 1],
            "west":  [48, 0, 49, 1],
            "up":    [48, 0, 49, 1],
            "down":  [48, 0, 49, 1]
        }
    }
]

mc_elements = []
for item in cannon_elements_raw:
    mc_elements.append({
        "name": item["name"],
        "from": item["from"],
        "to": item["to"],
        "faces": make_faces_norm(item["raw_faces"])
    })

# --- CORRECT DISPLAY TRANSFORMATIONS ---
# CRITICAL:
# rotation [0, 0, 0] so cannon aims forward (not flipped 180 backwards!)
# scale [1, 1, 1] on head/fixed so it does NOT render 1.6x oversized!
display_settings = {
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
        "translation": [0, 2, 0],
        "scale": [0.5, 0.5, 0.5]
    },
    "gui": {
        "rotation": [30, 225, 0],
        "translation": [0, 0, 0],
        "scale": [0.625, 0.625, 0.625]
    },
    "head": {
        "rotation": [0, 0, 0],
        "translation": [0, 0, 0],
        "scale": [1.0, 1.0, 1.0]
    },
    "fixed": {
        "rotation": [0, 0, 0],
        "translation": [0, 0, 0],
        "scale": [1.0, 1.0, 1.0]
    }
}

# Model textures:
# Reference BOTH "minecraft:item/cannon_tnt" AND "siegecannon:item/cannon_tnt"
cannon_json_model = {
    "credit": "SiegeCannon 3D Model for Minecraft 1.20-1.21+ (Blockbench)",
    "textures": {
        "0": "minecraft:item/cannon_tnt",
        "particle": "minecraft:item/cannon_tnt"
    },
    "elements": mc_elements,
    "display": display_settings
}
json_str = json.dumps(cannon_json_model, indent=2, ensure_ascii=False)

with open("public/models/cannon_1x1.json", "w", encoding="utf-8") as f:
    f.write(json_str)
with open("dist/models/cannon_1x1.json", "w", encoding="utf-8") as f:
    f.write(json_str)

# --- 1.3 Blockbench Project (.bbmodel) with EMBEDDED TEXTURE ---
bbmodel = {
    "meta": {
        "format_version": "4.10",
        "model_format": "java_block",
        "box_uv": False
    },
    "name": "cannon_1x1",
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
            "namespace": "minecraft",
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
    "display": display_settings
}

for idx, el_raw in enumerate(cannon_elements_raw):
    bb_el = {
        "name": el_raw["name"],
        "box_uv": False,
        "rescale": False,
        "locked": False,
        "from": el_raw["from"],
        "to": el_raw["to"],
        "autouv": 0,
        "color": idx % 8,
        "uuid": f"c{idx:02d}e0000-0000-0000-0000-0000000000{idx:02d}",
        "type": "cube",
        "faces": {}
    }
    for face, raw_coords in el_raw["raw_faces"].items():
        bb_el["faces"][face] = {
            "uv": raw_coords,
            "texture": 0
        }
    bbmodel["elements"].append(bb_el)

bbmodel_str = json.dumps(bbmodel, indent=2, ensure_ascii=False)
with open("public/models/cannon_1x1.bbmodel", "w", encoding="utf-8") as f:
    f.write(bbmodel_str)
with open("dist/models/cannon_1x1.bbmodel", "w", encoding="utf-8") as f:
    f.write(bbmodel_str)

# --- 1.4 Vanilla Textures Model Variant ---
vanilla_elements = []
for item in cannon_elements_raw:
    name = item["name"]
    tex = "#wood"
    if "wheel" in name:
        tex = "#dark"
    elif "hubcap" in name or "ring" in name or "fuse" in name or "wedge" in name:
        tex = "#gold"
    elif "barrel" in name or "breech" in name or "cascabel" in name:
        tex = "#anvil"
    elif "cheek" in name:
        tex = "#log"
    elif "axle" in name or "spade" in name:
        tex = "#iron"
    elif "bore" in name:
        tex = "#black"

    v_faces = {}
    for face, fdata in item["raw_faces"].items():
        u1 = (fdata[0] % 16)
        v1 = (fdata[1] % 16)
        u2 = u1 + min(16 - u1, max(1, fdata[2] - fdata[0]))
        v2 = v1 + min(16 - v1, max(1, fdata[3] - fdata[1]))
        v_faces[face] = {
            "uv": [float(u1), float(v1), float(u2), float(v2)],
            "texture": tex
        }
    vanilla_elements.append({
        "name": item["name"],
        "from": item["from"],
        "to": item["to"],
        "faces": v_faces
    })

vanilla_cannon_model = {
    "credit": "SiegeCannon 3D Model (Vanilla Textures)",
    "textures": {
        "particle": "minecraft:block/dark_oak_planks",
        "wood": "minecraft:block/dark_oak_planks",
        "log": "minecraft:block/dark_oak_log",
        "iron": "minecraft:block/iron_block",
        "dark": "minecraft:block/deepslate",
        "anvil": "minecraft:block/anvil",
        "gold": "minecraft:block/gold_block",
        "black": "minecraft:block/black_concrete"
    },
    "elements": vanilla_elements,
    "display": display_settings
}
vanilla_json_str = json.dumps(vanilla_cannon_model, indent=2, ensure_ascii=False)
with open("public/models/cannon_vanilla.json", "w", encoding="utf-8") as f:
    f.write(vanilla_json_str)
with open("dist/models/cannon_vanilla.json", "w", encoding="utf-8") as f:
    f.write(vanilla_json_str)

# === 2. ASSEMBLE COMPLETE RESOURCE PACK WITH MENU + CANNON ===
rp_dir = "complete_rp"
shutil.rmtree(rp_dir, ignore_errors=True)

# Create all folders
folders = [
    f"{rp_dir}/assets/minecraft/font",
    f"{rp_dir}/assets/minecraft/atlases",
    f"{rp_dir}/assets/minecraft/models/item",
    f"{rp_dir}/assets/minecraft/textures/item",
    f"{rp_dir}/assets/minecraft/textures/block",
    f"{rp_dir}/assets/townyarchitecture/textures/gui",
    f"{rp_dir}/assets/townyarchitecture/textures/item",
    f"{rp_dir}/assets/townyarchitecture/models/item",
    f"{rp_dir}/assets/siegecannon/models/item",
    f"{rp_dir}/assets/siegecannon/models/block",
    f"{rp_dir}/assets/siegecannon/textures/item",
    f"{rp_dir}/assets/siegecannon/textures/block",
    f"{rp_dir}/assets/siegecannons/models/item",
    f"{rp_dir}/assets/siegecannons/models/block",
    f"{rp_dir}/assets/siegecannons/textures/item",
    f"{rp_dir}/assets/siegecannons/textures/block"
]
for folder in folders:
    os.makedirs(folder, exist_ok=True)

# 2.1 pack.mcmeta (compatible with 1.20 - 1.21+)
pack_mcmeta = {
    "pack": {
        "pack_format": 34,
        "supported_formats": {
            "min_inclusive": 15,
            "max_inclusive": 48
        },
        "description": "TownyArchitecture & SiegeCannon Complete Pack"
    }
}
with open(f"{rp_dir}/pack.mcmeta", "w", encoding="utf-8") as f:
    json.dump(pack_mcmeta, f, indent=2)

# 2.2 TownyArchitecture GUI & Font
with open("menu.png", "rb") as f:
    menu_bytes = f.read()
with open("invisible.png", "rb") as f:
    inv_bytes = f.read()

with open(f"{rp_dir}/assets/townyarchitecture/textures/gui/menu.png", "wb") as f:
    f.write(menu_bytes)
with open(f"{rp_dir}/assets/townyarchitecture/textures/item/invisible.png", "wb") as f:
    f.write(inv_bytes)

font_json = {
    "providers": [
        {
            "type": "space",
            "advances": {
                "\uE000": -8,
                "\uE002": -168
            }
        },
        {
            "type": "bitmap",
            "file": "townyarchitecture:gui/menu.png",
            "ascent": 13,
            "height": 256,
            "chars": [
                "\uE001"
            ]
        }
    ]
}
with open(f"{rp_dir}/assets/minecraft/font/default.json", "w", encoding="utf-8") as f:
    json.dump(font_json, f, indent=2)

paper_model = {
    "parent": "item/generated",
    "textures": {
        "layer0": "item/paper"
    },
    "overrides": [
        {"predicate": {"custom_model_data": 1}, "model": "townyarchitecture:item/invisible"}
    ]
}
with open(f"{rp_dir}/assets/minecraft/models/item/paper.json", "w", encoding="utf-8") as f:
    json.dump(paper_model, f, indent=2)

inv_model = {
    "parent": "item/generated",
    "textures": {
        "layer0": "townyarchitecture:item/invisible"
    }
}
with open(f"{rp_dir}/assets/townyarchitecture/models/item/invisible.json", "w", encoding="utf-8") as f:
    json.dump(inv_model, f, indent=2)

print("Restored TownyArchitecture GUI menu.png, default.json font, and invisible item!")

# 2.3 Cannon Textures in all locations
cannon_tex_destinations = [
    f"{rp_dir}/assets/minecraft/textures/item/cannon_tnt.png",
    f"{rp_dir}/assets/minecraft/textures/item/cannon.png",
    f"{rp_dir}/assets/minecraft/textures/block/cannon_tnt.png",
    f"{rp_dir}/assets/minecraft/textures/block/cannon.png",
    f"{rp_dir}/assets/siegecannon/textures/item/cannon_tnt.png",
    f"{rp_dir}/assets/siegecannon/textures/item/cannon.png",
    f"{rp_dir}/assets/siegecannon/textures/block/cannon_tnt.png",
    f"{rp_dir}/assets/siegecannons/textures/item/cannon_tnt.png",
    f"{rp_dir}/assets/siegecannons/textures/item/cannon.png"
]
for dst in cannon_tex_destinations:
    with open(dst, "wb") as f:
        f.write(png_bytes)

# 2.4 Cannon Models in all locations
cannon_model_destinations = [
    f"{rp_dir}/assets/siegecannon/models/item/cannon_tnt.json",
    f"{rp_dir}/assets/siegecannon/models/item/cannon.json",
    f"{rp_dir}/assets/siegecannon/models/block/cannon_tnt.json",
    f"{rp_dir}/assets/siegecannon/models/block/cannon.json",
    f"{rp_dir}/assets/siegecannons/models/item/cannon_tnt.json",
    f"{rp_dir}/assets/siegecannons/models/item/cannon.json",
    f"{rp_dir}/assets/siegecannons/models/block/cannon_tnt.json",
    f"{rp_dir}/assets/minecraft/models/item/cannon_tnt.json",
    f"{rp_dir}/assets/minecraft/models/item/cannon.json"
]
for dst in cannon_model_destinations:
    with open(dst, "w", encoding="utf-8") as f:
        f.write(json_str)

# 2.5 TNT & Carrot overrides for Minecraft namespace
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
with open(f"{rp_dir}/assets/minecraft/models/item/tnt.json", "w", encoding="utf-8") as f:
    json.dump(tnt_override, f, indent=2)

carrot_override = {
    "parent": "minecraft:item/handheld",
    "textures": {
        "layer0": "minecraft:item/carrot_on_a_stick"
    },
    "overrides": [
        {"predicate": {"custom_model_data": 7001}, "model": "siegecannon:item/cannon_tnt"}
    ]
}
with open(f"{rp_dir}/assets/minecraft/models/item/carrot_on_a_stick.json", "w", encoding="utf-8") as f:
    json.dump(carrot_override, f, indent=2)

# 2.6 Full Atlas definition (properly registering both directories AND single custom textures)
atlas_config = {
    "sources": [
        {
            "type": "directory",
            "source": "item",
            "prefix": "item/"
        },
        {
            "type": "directory",
            "source": "block",
            "prefix": "block/"
        },
        {
            "type": "single",
            "resource": "siegecannon:item/cannon_tnt",
            "sprite": "siegecannon:item/cannon_tnt"
        },
        {
            "type": "single",
            "resource": "siegecannon:item/cannon",
            "sprite": "siegecannon:item/cannon"
        }
    ]
}
with open(f"{rp_dir}/assets/minecraft/atlases/blocks.json", "w", encoding="utf-8") as f:
    json.dump(atlas_config, f, indent=2)

print("Created full atlas configuration in assets/minecraft/atlases/blocks.json!")

# === 3. PACKAGE ZIP ARCHIVES ===
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
        for root, dirs, files in sorted(os.walk(rp_dir)):
            for file in sorted(files):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, rp_dir).replace('\\', '/')
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
ts_content = f"""// Auto-generated 3D Cannon Model Data with Embedded Texture & Strict UV
export const CANNON_MODEL_JSON = {json.dumps(cannon_json_model, indent=2, ensure_ascii=False)};
export const CANNON_VANILLA_MODEL_JSON = {json.dumps(vanilla_cannon_model, indent=2, ensure_ascii=False)};

export const CANNON_MODEL_JSON_STR = {json.dumps(json_str)};
export const CANNON_VANILLA_JSON_STR = {json.dumps(vanilla_json_str)};
export const CANNON_BBMODEL_JSON_STR = {json.dumps(bbmodel_str)};

export const CANNON_JSON_BASE64 = "{base64.b64encode(json_str.encode('utf-8')).decode('ascii')}";
export const CANNON_VANILLA_JSON_BASE64 = "{base64.b64encode(vanilla_json_str.encode('utf-8')).decode('ascii')}";
export const CANNON_BBMODEL_BASE64 = "{base64.b64encode(bbmodel_str.encode('utf-8')).decode('ascii')}";
export const CANNON_PNG_BASE64 = "{png_b64}";
export const CANNON_RP_BASE64 = "{b64}";

export const CANNON_METADATA = {{
  name: "3D Осадная Пушка (1x1 Блок)",
  fileJsonName: "cannon_1x1.json",
  fileVanillaJsonName: "cannon_vanilla.json",
  fileBbmodelName: "cannon_1x1.bbmodel",
  filePngName: "cannon_tnt.png",
  fileRpName: "SiegeCannon-3D-Model-RP.zip",
  elementsCount: {len(cannon_json_model["elements"])},
  format: "Blockbench / Minecraft Java 1.20 - 1.21+ (Strict 0..16 UV & Embedded Textures)",
  customModelData: 7001,
  targetItem: "siegecannon:cannon_tnt / tnt",
  dimensions: "16x16x16 (В точности 1x1 блок Minecraft)",
  author: "TownyArchitecture & SiegeCannon Team",
  releaseDate: "2026-10-04"
}};
"""

with open("src/data/cannonModelData.ts", "w", encoding="utf-8") as f:
    f.write(ts_content)

print(f"=== Complete Pack built successfully! New SHA-1: {sha1} ===")
