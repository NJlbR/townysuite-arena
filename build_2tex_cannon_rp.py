import os
import json
import zipfile
import base64
import hashlib
import struct
import zlib
import shutil

print("=== 1. Building 2-Texture Cannon Model & Complete Resource Pack ===")

# --- 1.1 Generate 16x16 Pixel-Art Textures for Wood and Metal ---
def create_png_16(pixels):
    raw = bytearray()
    for y in range(16):
        raw.append(0)
        for x in range(16):
            raw.extend(pixels[y][x])
    compressed = zlib.compress(bytes(raw), 9)
    def chunk(tag, data):
        c = struct.pack('>I', len(data)) + tag + data
        crc = struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
        return c + crc
    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', struct.pack('>IIBBBBB', 16, 16, 8, 6, 0, 0, 0))
    png += chunk(b'IDAT', compressed)
    png += chunk(b'IEND', b'')
    return png

# Wood: Dark Oak Planks palette
wood_pixels = []
for y in range(16):
    row = []
    for x in range(16):
        if y in (0, 7, 8, 15) or x in (0, 15):
            c = (52, 30, 16, 255) # Dark groove
        elif (x + y * 3) % 4 == 0:
            c = (96, 61, 36, 255) # Light grain
        else:
            c = (76, 47, 27, 255) # Base wood
        row.append(c)
    wood_pixels.append(row)

# Metal: Anvil / Cast Iron Gunmetal palette
metal_pixels = []
for y in range(16):
    row = []
    for x in range(16):
        if x in (0, 15) or y in (0, 15):
            c = (32, 34, 38, 255) # Dark edge
        elif y in (3, 4):
            c = (75, 80, 88, 255) # Sheen highlight
        elif (x * 3 + y) % 5 == 0:
            c = (58, 62, 68, 255) # Mid metal
        else:
            c = (45, 47, 52, 255) # Base iron
        row.append(c)
    metal_pixels.append(row)

png_wood = create_png_16(wood_pixels)
png_metal = create_png_16(metal_pixels)
b64_wood = base64.b64encode(png_wood).decode('utf-8')
b64_metal = base64.b64encode(png_metal).decode('utf-8')

os.makedirs("public/models", exist_ok=True)
os.makedirs("dist/models", exist_ok=True)
with open("public/models/cannon_wood.png", "wb") as f:
    f.write(png_wood)
with open("dist/models/cannon_wood.png", "wb") as f:
    f.write(png_wood)
with open("public/models/cannon_metal.png", "wb") as f:
    f.write(png_metal)
with open("dist/models/cannon_metal.png", "wb") as f:
    f.write(png_metal)

print("Created cannon_wood.png and cannon_metal.png!")

# --- 1.2 Elements Definition for 2-Texture Architecture ---
# Elements assigned strictly to:
# "#wood" (Carriage, Cheeks, Wedge)
# "#metal" (Spade, Axle, Wheels, Hubcaps, Barrel, Rings, Muzzle, Knob, Fuse)

elements_def = [
    # --- WOOD COMPONENTS ---
    {
        "name": "carriage_bed",
        "from": [3, 1, 2],
        "to": [13, 3, 15],
        "tex": "#wood",
        "faces": {
            "north": {"uv": [3, 13, 13, 15]},
            "south": {"uv": [3, 13, 13, 15]},
            "east":  {"uv": [2, 13, 15, 15]},
            "west":  {"uv": [2, 13, 15, 15]},
            "up":    {"uv": [3, 2, 13, 15]},
            "down":  {"uv": [3, 2, 13, 15]}
        }
    },
    {
        "name": "carriage_left_cheek",
        "from": [2, 2, 2],
        "to": [4, 7, 15],
        "tex": "#wood",
        "faces": {
            "north": {"uv": [2, 9, 4, 14]},
            "south": {"uv": [2, 9, 4, 14]},
            "east":  {"uv": [2, 9, 15, 14]},
            "west":  {"uv": [2, 9, 15, 14]},
            "up":    {"uv": [2, 2, 4, 15]},
            "down":  {"uv": [2, 2, 4, 15]}
        }
    },
    {
        "name": "carriage_right_cheek",
        "from": [12, 2, 2],
        "to": [14, 7, 15],
        "tex": "#wood",
        "faces": {
            "north": {"uv": [12, 9, 14, 14]},
            "south": {"uv": [12, 9, 14, 14]},
            "east":  {"uv": [2, 9, 15, 14]},
            "west":  {"uv": [2, 9, 15, 14]},
            "up":    {"uv": [12, 2, 14, 15]},
            "down":  {"uv": [12, 2, 14, 15]}
        }
    },
    {
        "name": "elevation_wedge",
        "from": [6, 3, 9],
        "to": [10, 5, 13],
        "tex": "#wood",
        "faces": {
            "north": {"uv": [6, 11, 10, 13]},
            "south": {"uv": [6, 11, 10, 13]},
            "east":  {"uv": [9, 11, 13, 13]},
            "west":  {"uv": [9, 11, 13, 13]},
            "up":    {"uv": [6, 9, 10, 13]},
            "down":  {"uv": [6, 9, 10, 13]}
        }
    },

    # --- METAL COMPONENTS ---
    {
        "name": "rear_trail_spade",
        "from": [5, 0.5, 13],
        "to": [11, 2.5, 16],
        "tex": "#metal",
        "faces": {
            "north": {"uv": [5, 13.5, 11, 15.5]},
            "south": {"uv": [5, 13.5, 11, 15.5]},
            "east":  {"uv": [13, 13.5, 16, 15.5]},
            "west":  {"uv": [13, 13.5, 16, 15.5]},
            "up":    {"uv": [5, 13, 11, 16]},
            "down":  {"uv": [5, 13, 11, 16]}
        }
    },
    {
        "name": "axle_rod",
        "from": [1, 3.5, 7],
        "to": [15, 5, 8.5],
        "tex": "#metal",
        "faces": {
            "north": {"uv": [1, 11, 15, 12.5]},
            "south": {"uv": [1, 11, 15, 12.5]},
            "east":  {"uv": [7, 11, 8.5, 12.5]},
            "west":  {"uv": [7, 11, 8.5, 12.5]},
            "up":    {"uv": [1, 7, 15, 8.5]},
            "down":  {"uv": [1, 7, 15, 8.5]}
        }
    },
    {
        "name": "left_wheel",
        "from": [0.5, 0.5, 4],
        "to": [2.5, 8.5, 11.5],
        "tex": "#metal",
        "faces": {
            "north": {"uv": [0.5, 7.5, 2.5, 15.5]},
            "south": {"uv": [0.5, 7.5, 2.5, 15.5]},
            "east":  {"uv": [4, 7.5, 11.5, 15.5]},
            "west":  {"uv": [4, 7.5, 11.5, 15.5]},
            "up":    {"uv": [0.5, 4, 2.5, 11.5]},
            "down":  {"uv": [0.5, 4, 2.5, 11.5]}
        }
    },
    {
        "name": "left_hubcap",
        "from": [0, 3.5, 6.75],
        "to": [0.5, 5.5, 8.75],
        "tex": "#metal",
        "faces": {
            "north": {"uv": [0, 10.5, 0.5, 12.5]},
            "south": {"uv": [0, 10.5, 0.5, 12.5]},
            "east":  {"uv": [6.75, 10.5, 8.75, 12.5]},
            "west":  {"uv": [6.75, 10.5, 8.75, 12.5]},
            "up":    {"uv": [0, 6.75, 0.5, 8.75]},
            "down":  {"uv": [0, 6.75, 0.5, 8.75]}
        }
    },
    {
        "name": "right_wheel",
        "from": [13.5, 0.5, 4],
        "to": [15.5, 8.5, 11.5],
        "tex": "#metal",
        "faces": {
            "north": {"uv": [13.5, 7.5, 15.5, 15.5]},
            "south": {"uv": [13.5, 7.5, 15.5, 15.5]},
            "east":  {"uv": [4, 7.5, 11.5, 15.5]},
            "west":  {"uv": [4, 7.5, 11.5, 15.5]},
            "up":    {"uv": [13.5, 4, 15.5, 11.5]},
            "down":  {"uv": [13.5, 4, 15.5, 11.5]}
        }
    },
    {
        "name": "right_hubcap",
        "from": [15.5, 3.5, 6.75],
        "to": [16, 5.5, 8.75],
        "tex": "#metal",
        "faces": {
            "north": {"uv": [15.5, 10.5, 16, 12.5]},
            "south": {"uv": [15.5, 10.5, 16, 12.5]},
            "east":  {"uv": [6.75, 10.5, 8.75, 12.5]},
            "west":  {"uv": [6.75, 10.5, 8.75, 12.5]},
            "up":    {"uv": [15.5, 6.75, 16, 8.75]},
            "down":  {"uv": [15.5, 6.75, 16, 8.75]}
        }
    },
    {
        "name": "cascabel_knob",
        "from": [7, 5.5, 13.5],
        "to": [9, 7.5, 15],
        "tex": "#metal",
        "faces": {
            "north": {"uv": [7, 8.5, 9, 10.5]},
            "south": {"uv": [7, 8.5, 9, 10.5]},
            "east":  {"uv": [13.5, 8.5, 15, 10.5]},
            "west":  {"uv": [13.5, 8.5, 15, 10.5]},
            "up":    {"uv": [7, 13.5, 9, 15]},
            "down":  {"uv": [7, 13.5, 9, 15]}
        }
    },
    {
        "name": "breech_base",
        "from": [5, 4.5, 8],
        "to": [11, 8.5, 13.5],
        "tex": "#metal",
        "faces": {
            "north": {"uv": [5, 7.5, 11, 11.5]},
            "south": {"uv": [5, 7.5, 11, 11.5]},
            "east":  {"uv": [8, 7.5, 13.5, 11.5]},
            "west":  {"uv": [8, 7.5, 13.5, 11.5]},
            "up":    {"uv": [5, 8, 11, 13.5]},
            "down":  {"uv": [5, 8, 11, 13.5]}
        }
    },
    {
        "name": "breech_ring",
        "from": [4.75, 4.25, 10.5],
        "to": [11.25, 8.75, 12],
        "tex": "#metal",
        "faces": {
            "north": {"uv": [4.75, 7.25, 11.25, 11.75]},
            "south": {"uv": [4.75, 7.25, 11.25, 11.75]},
            "east":  {"uv": [10.5, 7.25, 12, 11.75]},
            "west":  {"uv": [10.5, 7.25, 12, 11.75]},
            "up":    {"uv": [4.75, 10.5, 11.25, 12]},
            "down":  {"uv": [4.75, 10.5, 11.25, 12]}
        }
    },
    {
        "name": "trunnions_pivot",
        "from": [2, 5.5, 7],
        "to": [14, 7.5, 9],
        "tex": "#metal",
        "faces": {
            "north": {"uv": [2, 8.5, 14, 10.5]},
            "south": {"uv": [2, 8.5, 14, 10.5]},
            "east":  {"uv": [7, 8.5, 9, 10.5]},
            "west":  {"uv": [7, 8.5, 9, 10.5]},
            "up":    {"uv": [2, 7, 14, 9]},
            "down":  {"uv": [2, 7, 14, 9]}
        }
    },
    {
        "name": "barrel_mid",
        "from": [5.5, 5, 3],
        "to": [10.5, 8, 8],
        "tex": "#metal",
        "faces": {
            "north": {"uv": [5.5, 8, 10.5, 11]},
            "south": {"uv": [5.5, 8, 10.5, 11]},
            "east":  {"uv": [3, 8, 8, 11]},
            "west":  {"uv": [3, 8, 8, 11]},
            "up":    {"uv": [5.5, 3, 10.5, 8]},
            "down":  {"uv": [5.5, 3, 10.5, 8]}
        }
    },
    {
        "name": "barrel_chase",
        "from": [6, 5.25, 0.5],
        "to": [10, 7.75, 3],
        "tex": "#metal",
        "faces": {
            "north": {"uv": [6, 8.25, 10, 10.75]},
            "south": {"uv": [6, 8.25, 10, 10.75]},
            "east":  {"uv": [0.5, 8.25, 3, 10.75]},
            "west":  {"uv": [0.5, 8.25, 3, 10.75]},
            "up":    {"uv": [6, 0.5, 10, 3]},
            "down":  {"uv": [6, 0.5, 10, 3]}
        }
    },
    {
        "name": "muzzle_ring",
        "from": [5.5, 4.75, 0],
        "to": [10.5, 8.25, 1],
        "tex": "#metal",
        "faces": {
            "north": {"uv": [5.5, 7.75, 10.5, 11.25]},
            "south": {"uv": [5.5, 7.75, 10.5, 11.25]},
            "east":  {"uv": [0, 7.75, 1, 11.25]},
            "west":  {"uv": [0, 7.75, 1, 11.25]},
            "up":    {"uv": [5.5, 0, 10.5, 1]},
            "down":  {"uv": [5.5, 0, 10.5, 1]}
        }
    },
    {
        "name": "muzzle_bore",
        "from": [6.5, 5.75, 0],
        "to": [9.5, 7.25, 0.1],
        "tex": "#metal",
        "faces": {
            "north": {"uv": [6.5, 8.75, 9.5, 10.25]},
            "south": {"uv": [6.5, 8.75, 9.5, 10.25]},
            "east":  {"uv": [0, 8.75, 0.1, 10.25]},
            "west":  {"uv": [0, 8.75, 0.1, 10.25]},
            "up":    {"uv": [6.5, 0, 9.5, 0.1]},
            "down":  {"uv": [6.5, 0, 9.5, 0.1]}
        }
    },
    {
        "name": "touchhole_fuse",
        "from": [7.5, 8.5, 10.5],
        "to": [8.5, 9.5, 11.5],
        "tex": "#metal",
        "faces": {
            "north": {"uv": [7.5, 6.5, 8.5, 7.5]},
            "south": {"uv": [7.5, 6.5, 8.5, 7.5]},
            "east":  {"uv": [10.5, 6.5, 11.5, 7.5]},
            "west":  {"uv": [10.5, 6.5, 11.5, 7.5]},
            "up":    {"uv": [7.5, 10.5, 8.5, 11.5]},
            "down":  {"uv": [7.5, 10.5, 8.5, 11.5]}
        }
    }
]

# Build JSON elements
clean_elements = []
for el in elements_def:
    elem_faces = {}
    for face_dir, f_data in el["faces"].items():
        elem_faces[face_dir] = {
            "uv": f_data["uv"],
            "texture": el["tex"]
        }
    clean_elements.append({
        "name": el["name"],
        "from": el["from"],
        "to": el["to"],
        "faces": elem_faces
    })

# Verify all UVs
for el in clean_elements:
    for face, fdata in el["faces"].items():
        assert all(0.0 <= u <= 16.0 for u in fdata["uv"]), f"Bad UV in {el['name']} {face}: {fdata['uv']}"

# Display settings
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

# --- 1.3 Create Main 2-Texture Model with Vanilla Fallback ---
# Textures:
# "particle": "minecraft:block/dark_oak_planks"
# "wood": "minecraft:block/dark_oak_planks"
# "metal": "minecraft:block/anvil"
# (Guaranteed to NEVER fail loading in any Minecraft client!)
cannon_2tex_model = {
    "credit": "SiegeCannon 3D Model (2 Textures: Wood & Metal)",
    "parent": "minecraft:block/block",
    "textures": {
        "particle": "minecraft:block/dark_oak_planks",
        "wood": "minecraft:block/dark_oak_planks",
        "metal": "minecraft:block/anvil"
    },
    "elements": clean_elements,
    "display": display_settings
}
json_2tex_str = json.dumps(cannon_2tex_model, indent=2, ensure_ascii=False)

with open("public/models/cannon_1x1.json", "w", encoding="utf-8") as f:
    f.write(json_2tex_str)
with open("dist/models/cannon_1x1.json", "w", encoding="utf-8") as f:
    f.write(json_2tex_str)

# --- 1.4 Create Custom PNG 2-Texture Model Variant ---
cannon_2tex_custom_model = {
    "credit": "SiegeCannon 3D Model (2 Custom Textures)",
    "parent": "minecraft:block/block",
    "textures": {
        "particle": "siegecannon:item/cannon_wood",
        "wood": "siegecannon:item/cannon_wood",
        "metal": "siegecannon:item/cannon_metal"
    },
    "elements": clean_elements,
    "display": display_settings
}
json_2tex_custom_str = json.dumps(cannon_2tex_custom_model, indent=2, ensure_ascii=False)
with open("public/models/cannon_custom_textures.json", "w", encoding="utf-8") as f:
    f.write(json_2tex_custom_str)
with open("dist/models/cannon_custom_textures.json", "w", encoding="utf-8") as f:
    f.write(json_2tex_custom_str)

# --- 1.5 Create Blockbench Project (.bbmodel) with BOTH Textures Embedded ---
bbmodel_2tex = {
    "meta": {
        "format_version": "4.10",
        "model_format": "java_block",
        "box_uv": False
    },
    "name": "cannon_2tex",
    "model_identifier": "cannon_tnt",
    "visible_box": [1, 1, 0],
    "resolution": {
        "width": 16,
        "height": 16
    },
    "elements": [],
    "outliner": [
        {
            "name": "Carriage (Wood)",
            "origin": [8, 4, 8],
            "color": 0,
            "children": [0, 1, 2, 3]
        },
        {
            "name": "Chassis & Wheels (Metal)",
            "origin": [8, 4, 7],
            "color": 1,
            "children": [4, 5, 6, 7, 8, 9]
        },
        {
            "name": "Barrel (Metal)",
            "origin": [8, 6.5, 7.5],
            "color": 2,
            "children": [10, 11, 12, 13, 14, 15, 16, 17, 18]
        }
    ],
    "textures": [
        {
            "path": "item/cannon_wood",
            "name": "cannon_wood",
            "folder": "item",
            "namespace": "siegecannon",
            "id": "wood",
            "particle": True,
            "render_mode": "default",
            "visible": True,
            "mode": "bitmap",
            "saved": True,
            "uuid": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
            "source": f"data:image/png;base64,{b64_wood}"
        },
        {
            "path": "item/cannon_metal",
            "name": "cannon_metal",
            "folder": "item",
            "namespace": "siegecannon",
            "id": "metal",
            "particle": False,
            "render_mode": "default",
            "visible": True,
            "mode": "bitmap",
            "saved": True,
            "uuid": "b2c3d4e5-f6a7-8b9c-0d1e-2f3a4b5c6d7e",
            "source": f"data:image/png;base64,{b64_metal}"
        }
    ],
    "display": display_settings
}

for idx, el_def in enumerate(elements_def):
    tex_idx = 0 if el_def["tex"] == "#wood" else 1
    bb_el = {
        "name": el_def["name"],
        "box_uv": False,
        "rescale": False,
        "locked": False,
        "from": el_def["from"],
        "to": el_def["to"],
        "autouv": 0,
        "color": idx % 8,
        "uuid": f"c{idx:02d}e0000-0000-0000-0000-0000000000{idx:02d}",
        "type": "cube",
        "faces": {}
    }
    for face, f_data in el_def["faces"].items():
        bb_el["faces"][face] = {
            "uv": f_data["uv"],
            "texture": tex_idx
        }
    bbmodel_2tex["elements"].append(bb_el)

bbmodel_2tex_str = json.dumps(bbmodel_2tex, indent=2, ensure_ascii=False)
with open("public/models/cannon_1x1.bbmodel", "w", encoding="utf-8") as f:
    f.write(bbmodel_2tex_str)
with open("dist/models/cannon_1x1.bbmodel", "w", encoding="utf-8") as f:
    f.write(bbmodel_2tex_str)

print("Created 2-texture .bbmodel project with embedded wood and metal textures!")

# === 2. ASSEMBLE COMPLETE RESOURCE PACK ===
rp_dir = "complete_rp"
shutil.rmtree(rp_dir, ignore_errors=True)

folders = [
    f"{rp_dir}/assets/minecraft/font",
    f"{rp_dir}/assets/minecraft/atlases",
    f"{rp_dir}/assets/minecraft/items",
    f"{rp_dir}/assets/minecraft/models/item",
    f"{rp_dir}/assets/minecraft/textures/item",
    f"{rp_dir}/assets/minecraft/textures/block",
    f"{rp_dir}/assets/townyarchitecture/textures/gui",
    f"{rp_dir}/assets/townyarchitecture/textures/item",
    f"{rp_dir}/assets/townyarchitecture/models/item",
    f"{rp_dir}/assets/siegecannon/items",
    f"{rp_dir}/assets/siegecannon/models/item",
    f"{rp_dir}/assets/siegecannon/models/block",
    f"{rp_dir}/assets/siegecannon/textures/item",
    f"{rp_dir}/assets/siegecannon/textures/block",
    f"{rp_dir}/assets/siegecannons/items",
    f"{rp_dir}/assets/siegecannons/models/item",
    f"{rp_dir}/assets/siegecannons/models/block",
    f"{rp_dir}/assets/siegecannons/textures/item",
    f"{rp_dir}/assets/siegecannons/textures/block"
]
for folder in folders:
    os.makedirs(folder, exist_ok=True)

# 2.1 pack.mcmeta
pack_mcmeta = {
    "pack": {
        "pack_format": 34,
        "supported_formats": {
            "min_inclusive": 15,
            "max_inclusive": 48
        },
        "description": "TownyArchitecture & SiegeCannon 2-Texture Pack"
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

# 2.3 Write 2 Textures in All Item & Block Directories
tex_destinations = [
    f"{rp_dir}/assets/siegecannon/textures/item",
    f"{rp_dir}/assets/siegecannon/textures/block",
    f"{rp_dir}/assets/siegecannons/textures/item",
    f"{rp_dir}/assets/siegecannons/textures/block",
    f"{rp_dir}/assets/minecraft/textures/item",
    f"{rp_dir}/assets/minecraft/textures/block"
]
for dst in tex_destinations:
    with open(f"{dst}/cannon_wood.png", "wb") as f:
        f.write(png_wood)
    with open(f"{dst}/cannon_metal.png", "wb") as f:
        f.write(png_metal)

# 2.4 Write 2-Texture Model in All Target Locations
model_destinations = [
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
for dst in model_destinations:
    with open(dst, "w", encoding="utf-8") as f:
        f.write(json_2tex_str)

# 2.5 Minecraft 1.21.2+ items/ Support
items_121_def = {
    "model": {
        "type": "minecraft:model",
        "model": "siegecannon:item/cannon_tnt"
    }
}
with open(f"{rp_dir}/assets/siegecannon/items/cannon_tnt.json", "w", encoding="utf-8") as f:
    json.dump(items_121_def, f, indent=2)
with open(f"{rp_dir}/assets/siegecannons/items/cannon_tnt.json", "w", encoding="utf-8") as f:
    json.dump(items_121_def, f, indent=2)

# 2.6 TNT Overrides
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

# 2.7 Atlas Configuration
atlas_config = {
    "sources": [
        {"type": "directory", "source": "item", "prefix": "item/"},
        {"type": "directory", "source": "block", "prefix": "block/"},
        {"type": "single", "resource": "siegecannon:item/cannon_wood", "sprite": "siegecannon:item/cannon_wood"},
        {"type": "single", "resource": "siegecannon:item/cannon_metal", "sprite": "siegecannon:item/cannon_metal"}
    ]
}
with open(f"{rp_dir}/assets/minecraft/atlases/blocks.json", "w", encoding="utf-8") as f:
    json.dump(atlas_config, f, indent=2)

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
ts_content = f"""// Auto-generated 3D Cannon Model Data with 2 Textures (Wood & Metal)
export const CANNON_MODEL_JSON = {json.dumps(cannon_2tex_model, indent=2, ensure_ascii=False)};
export const CANNON_CUSTOM_MODEL_JSON = {json.dumps(cannon_2tex_custom_model, indent=2, ensure_ascii=False)};

export const CANNON_MODEL_JSON_STR = {json.dumps(json_2tex_str)};
export const CANNON_CUSTOM_JSON_STR = {json.dumps(json_2tex_custom_str)};
export const CANNON_BBMODEL_JSON_STR = {json.dumps(bbmodel_2tex_str)};

export const CANNON_JSON_BASE64 = "{base64.b64encode(json_2tex_str.encode('utf-8')).decode('ascii')}";
export const CANNON_CUSTOM_JSON_BASE64 = "{base64.b64encode(json_2tex_custom_str.encode('utf-8')).decode('ascii')}";
export const CANNON_BBMODEL_BASE64 = "{base64.b64encode(bbmodel_2tex_str.encode('utf-8')).decode('ascii')}";
export const CANNON_WOOD_PNG_BASE64 = "{b64_wood}";
export const CANNON_METAL_PNG_BASE64 = "{b64_metal}";
export const CANNON_RP_BASE64 = "{b64}";

export const CANNON_METADATA = {{
  name: "3D Осадная Пушка (2 Текстуры: Дерево и Металл)",
  fileJsonName: "cannon_1x1.json",
  fileCustomJsonName: "cannon_custom_textures.json",
  fileBbmodelName: "cannon_1x1.bbmodel",
  fileWoodPngName: "cannon_wood.png",
  fileMetalPngName: "cannon_metal.png",
  fileRpName: "SiegeCannon-3D-Model-RP.zip",
  elementsCount: {len(cannon_2tex_model["elements"])},
  format: "Blockbench / Minecraft Java 1.20 - 1.21+ (2-Texture Architecture: Wood + Metal)",
  customModelData: 7001,
  targetItem: "siegecannon:cannon_tnt / tnt",
  dimensions: "16x16x16 (В точности 1x1 блок Minecraft)",
  texturesUsed: ["minecraft:block/dark_oak_planks (#wood)", "minecraft:block/anvil (#metal)"],
  author: "TownyArchitecture & SiegeCannon Team",
  releaseDate: "2026-10-04"
}};
"""

with open("src/data/cannonModelData.ts", "w", encoding="utf-8") as f:
    f.write(ts_content)

print(f"=== 2-Texture Pack built successfully! New SHA-1: {sha1} ===")
