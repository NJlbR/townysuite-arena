import os
import json
import zipfile
import base64
import hashlib
import struct
import zlib
import shutil

print("=== Building Ground-Aligned (Y: -8..+8, No Z-Fighting) Siege Mortar & Pack ===")

# --- 1. Generate 16x16 HD Pixel-Art PNGs for Wood and Metal ---
def create_png_16(pixels):
    raw = bytearray()
    for y in range(16):
        raw.append(0)  # Filter type None
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

# 1.1 Wood: Rich Dark Oak Planks with woodgrain and nail rivets
wood_pixels = []
for y in range(16):
    row = []
    for x in range(16):
        if y in (0, 7, 8, 15) or x in (0, 15):
            c = (52, 30, 16, 255)  # Dark groove
        elif (x in (2, 13) and y in (2, 6, 10, 14)):
            c = (38, 22, 12, 255)  # Dark iron nail
        elif (x + y * 3) % 5 == 0:
            c = (96, 61, 36, 255)  # Light grain
        else:
            c = (76, 47, 27, 255)  # Base warm dark oak
        row.append(c)
    wood_pixels.append(row)

# 1.2 Metal: Forged Cast Iron / Gunmetal with edge sheen and specular highlights
metal_pixels = []
for y in range(16):
    row = []
    for x in range(16):
        if x in (0, 15) or y in (0, 15):
            c = (30, 32, 36, 255)  # Dark steel edge
        elif y in (3, 4):
            c = (82, 88, 97, 255)  # Metal sheen highlight
        elif (x * 3 + y) % 5 == 0:
            c = (62, 66, 73, 255)  # Mid sheen
        else:
            c = (45, 47, 52, 255)  # Base heavy iron
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

print("Generated cannon_wood.png and cannon_metal.png (16x16 HD Pixel-Art)!")

# --- 2. 3D Elements Definition (Ground-Aligned Y: [-8.0..+8.0], Zero Z-Fighting) ---
elements_def = [
    # --- WOOD COMPONENTS (Heavy Timber Carriage & Cheeks) ---
    {
        "name": "carriage_bed",
        "from": [2.5, -8.0, 1.8],
        "to": [13.5, -4.0, 14.8],
        "tex": "#wood",
        "tex_idx": 0,
        "faces": {
            "north": {"uv": [2.5, 12, 13.5, 16]},
            "south": {"uv": [2.5, 12, 13.5, 16]},
            "east":  {"uv": [1.8, 12, 14.8, 16]},
            "west":  {"uv": [1.8, 12, 14.8, 16]},
            "up":    {"uv": [2.5, 1.8, 13.5, 14.8]},
            "down":  {"uv": [2.5, 1.8, 13.5, 14.8]}
        }
    },
    {
        "name": "carriage_left_cheek",
        "from": [1.2, -6.0, 2.2],
        "to": [4.2, 6.0, 14.4],
        "tex": "#wood",
        "tex_idx": 0,
        "faces": {
            "north": {"uv": [1.2, 4, 4.2, 16]},
            "south": {"uv": [1.2, 4, 4.2, 16]},
            "east":  {"uv": [2.2, 4, 14.4, 16]},
            "west":  {"uv": [2.2, 4, 14.4, 16]},
            "up":    {"uv": [1.2, 2.2, 4.2, 14.4]},
            "down":  {"uv": [1.2, 2.2, 4.2, 14.4]}
        }
    },
    {
        "name": "carriage_right_cheek",
        "from": [11.8, -6.0, 2.2],
        "to": [14.8, 6.0, 14.4],
        "tex": "#wood",
        "tex_idx": 0,
        "faces": {
            "north": {"uv": [11.8, 4, 14.8, 16]},
            "south": {"uv": [11.8, 4, 14.8, 16]},
            "east":  {"uv": [2.2, 4, 14.4, 16]},
            "west":  {"uv": [2.2, 4, 14.4, 16]},
            "up":    {"uv": [11.8, 2.2, 14.8, 14.4]},
            "down":  {"uv": [11.8, 2.2, 14.8, 14.4]}
        }
    },
    {
        "name": "elevation_wedge",
        "from": [5.0, -3.95, 7.8],
        "to": [11.0, -1.2, 12.8],
        "tex": "#wood",
        "tex_idx": 0,
        "faces": {
            "north": {"uv": [5, 9, 11, 13]},
            "south": {"uv": [5, 9, 11, 13]},
            "east":  {"uv": [7.8, 9, 12.8, 13]},
            "west":  {"uv": [7.8, 9, 12.8, 13]},
            "up":    {"uv": [5, 7.8, 11, 12.8]},
            "down":  {"uv": [5, 7.8, 11, 12.8]}
        }
    },
    {
        "name": "crossbeam_front",
        "from": [4.0, -7.0, 0.8],
        "to": [12.0, -4.2, 2.4],
        "tex": "#wood",
        "tex_idx": 0,
        "faces": {
            "north": {"uv": [4, 12, 12, 15]},
            "south": {"uv": [4, 12, 12, 15]},
            "east":  {"uv": [0.8, 12, 2.4, 15]},
            "west":  {"uv": [0.8, 12, 2.4, 15]},
            "up":    {"uv": [4, 0.8, 12, 2.4]},
            "down":  {"uv": [4, 0.8, 12, 2.4]}
        }
    },

    # --- METAL COMPONENTS (Tall Wheels, Axle, Mortar Barrel, No Z-Fighting) ---
    {
        "name": "rear_trail_spade",
        "from": [4.2, -8.0, 13.2],
        "to": [11.8, -5.2, 16.0],
        "tex": "#metal",
        "tex_idx": 1,
        "faces": {
            "north": {"uv": [4.2, 13, 11.8, 16]},
            "south": {"uv": [4.2, 13, 11.8, 16]},
            "east":  {"uv": [13.2, 13, 16, 16]},
            "west":  {"uv": [13.2, 13, 16, 16]},
            "up":    {"uv": [4.2, 13.2, 11.8, 16]},
            "down":  {"uv": [4.2, 13.2, 11.8, 16]}
        }
    },
    {
        "name": "axle_rod",
        "from": [0.5, -2.0, 6.5],
        "to": [15.5, 1.0, 8.5],
        "tex": "#metal",
        "tex_idx": 1,
        "faces": {
            "north": {"uv": [0.5, 7, 15.5, 10]},
            "south": {"uv": [0.5, 7, 15.5, 10]},
            "east":  {"uv": [6.5, 7, 8.5, 10]},
            "west":  {"uv": [6.5, 7, 8.5, 10]},
            "up":    {"uv": [0.5, 6.5, 15.5, 8.5]},
            "down":  {"uv": [0.5, 6.5, 15.5, 8.5]}
        }
    },
    {
        "name": "left_wheel",
        "from": [0.2, -8.0, 1.0],
        "to": [2.2, 7.0, 14.0],
        "tex": "#metal",
        "tex_idx": 1,
        "faces": {
            "north": {"uv": [0.2, 1, 2.2, 16]},
            "south": {"uv": [0.2, 1, 2.2, 16]},
            "east":  {"uv": [1, 1, 14, 16]},
            "west":  {"uv": [1, 1, 14, 16]},
            "up":    {"uv": [0.2, 1, 2.2, 14]},
            "down":  {"uv": [0.2, 1, 2.2, 14]}
        }
    },
    {
        "name": "left_hubcap",
        "from": [0.0, -2.0, 6.0],
        "to": [0.4, 1.0, 9.0],
        "tex": "#metal",
        "tex_idx": 1,
        "faces": {
            "north": {"uv": [0, 7, 0.4, 10]},
            "south": {"uv": [0, 7, 0.4, 10]},
            "east":  {"uv": [6, 7, 9, 10]},
            "west":  {"uv": [6, 7, 9, 10]},
            "up":    {"uv": [0, 6, 0.4, 9]},
            "down":  {"uv": [0, 6, 0.4, 9]}
        }
    },
    {
        "name": "right_wheel",
        "from": [13.8, -8.0, 1.0],
        "to": [15.8, 7.0, 14.0],
        "tex": "#metal",
        "tex_idx": 1,
        "faces": {
            "north": {"uv": [13.8, 1, 15.8, 16]},
            "south": {"uv": [13.8, 1, 15.8, 16]},
            "east":  {"uv": [1, 1, 14, 16]},
            "west":  {"uv": [1, 1, 14, 16]},
            "up":    {"uv": [13.8, 1, 15.8, 14]},
            "down":  {"uv": [13.8, 1, 15.8, 14]}
        }
    },
    {
        "name": "right_hubcap",
        "from": [15.6, -2.0, 6.0],
        "to": [16.0, 1.0, 9.0],
        "tex": "#metal",
        "tex_idx": 1,
        "faces": {
            "north": {"uv": [15.6, 7, 16, 10]},
            "south": {"uv": [15.6, 7, 16, 10]},
            "east":  {"uv": [6, 7, 9, 10]},
            "west":  {"uv": [6, 7, 9, 10]},
            "up":    {"uv": [15.6, 6, 16, 9]},
            "down":  {"uv": [15.6, 6, 16, 9]}
        }
    },
    {
        "name": "trunnions_pivot",
        "from": [1.0, -0.5, 6.2],
        "to": [15.0, 2.5, 8.2],
        "tex": "#metal",
        "tex_idx": 1,
        "faces": {
            "north": {"uv": [1, 5.5, 15, 8.5]},
            "south": {"uv": [1, 5.5, 15, 8.5]},
            "east":  {"uv": [6.2, 5.5, 8.2, 8.5]},
            "west":  {"uv": [6.2, 5.5, 8.2, 8.5]},
            "up":    {"uv": [1, 6.2, 15, 8.2]},
            "down":  {"uv": [1, 6.2, 15, 8.2]}
        }
    },
    {
        "name": "cascabel_knob",
        "from": [6.5, -1.0, 13.9],
        "to": [9.5, 2.0, 15.6],
        "tex": "#metal",
        "tex_idx": 1,
        "faces": {
            "north": {"uv": [6.5, 6, 9.5, 9]},
            "south": {"uv": [6.5, 6, 9.5, 9]},
            "east":  {"uv": [13.9, 6, 15.6, 9]},
            "west":  {"uv": [13.9, 6, 15.6, 9]},
            "up":    {"uv": [6.5, 13.9, 9.5, 15.6]},
            "down":  {"uv": [6.5, 13.9, 9.5, 15.6]}
        }
    },
    {
        "name": "breech_base",
        "from": [4.2, -2.5, 7.2],
        "to": [11.8, 4.5, 13.8],
        "tex": "#metal",
        "tex_idx": 1,
        "faces": {
            "north": {"uv": [4.2, 3.5, 11.8, 10.5]},
            "south": {"uv": [4.2, 3.5, 11.8, 10.5]},
            "east":  {"uv": [7.2, 3.5, 13.8, 10.5]},
            "west":  {"uv": [7.2, 3.5, 13.8, 10.5]},
            "up":    {"uv": [4.2, 7.2, 11.8, 13.8]},
            "down":  {"uv": [4.2, 7.2, 11.8, 13.8]}
        }
    },
    {
        "name": "breech_reinforcing_band",
        "from": [3.8, -2.9, 9.6],
        "to": [12.2, 4.9, 11.8],
        "tex": "#metal",
        "tex_idx": 1,
        "faces": {
            "north": {"uv": [3.8, 3, 12.2, 11]},
            "south": {"uv": [3.8, 3, 12.2, 11]},
            "east":  {"uv": [9.6, 3, 11.8, 11]},
            "west":  {"uv": [9.6, 3, 11.8, 11]},
            "up":    {"uv": [3.8, 9.6, 12.2, 11.8]},
            "down":  {"uv": [3.8, 9.6, 12.2, 11.8]}
        }
    },
    {
        "name": "barrel_main",
        "from": [4.6, -1.5, 2.8],
        "to": [11.4, 6.5, 7.8],
        "tex": "#metal",
        "tex_idx": 1,
        "faces": {
            "north": {"uv": [4.6, 1.5, 11.4, 9.5]},
            "south": {"uv": [4.6, 1.5, 11.4, 9.5]},
            "east":  {"uv": [2.8, 1.5, 7.8, 9.5]},
            "west":  {"uv": [2.8, 1.5, 7.8, 9.5]},
            "up":    {"uv": [4.6, 2.8, 11.4, 7.8]},
            "down":  {"uv": [4.6, 2.8, 11.4, 7.8]}
        }
    },
    {
        "name": "muzzle_collar",
        "from": [4.0, -1.0, 0.2],
        "to": [12.0, 8.0, 3.2],
        "tex": "#metal",
        "tex_idx": 1,
        "faces": {
            "north": {"uv": [4, 0, 12, 9]},
            "south": {"uv": [4, 0, 12, 9]},
            "east":  {"uv": [0.2, 0, 3.2, 9]},
            "west":  {"uv": [0.2, 0, 3.2, 9]},
            "up":    {"uv": [4, 0.2, 12, 3.2]},
            "down":  {"uv": [4, 0.2, 12, 3.2]}
        }
    },
    {
        "name": "muzzle_bore",
        "from": [5.5, 0.5, 0.0],
        "to": [10.5, 6.5, 0.18],
        "tex": "#metal",
        "tex_idx": 1,
        "faces": {
            "north": {"uv": [0, 0, 5, 6]},
            "south": {"uv": [0, 0, 5, 6]},
            "east":  {"uv": [0, 0, 0.18, 6]},
            "west":  {"uv": [0, 0, 0.18, 6]},
            "up":    {"uv": [0, 0, 5, 0.18]},
            "down":  {"uv": [0, 0, 5, 0.18]}
        }
    },
    {
        "name": "touchhole_fuse",
        "from": [7.2, 4.95, 10.2],
        "to": [8.8, 8.0, 11.4],
        "tex": "#metal",
        "tex_idx": 1,
        "faces": {
            "north": {"uv": [7.2, 0, 8.8, 3.5]},
            "south": {"uv": [7.2, 0, 8.8, 3.5]},
            "east":  {"uv": [10.2, 0, 11.4, 3.5]},
            "west":  {"uv": [10.2, 0, 11.4, 3.5]},
            "up":    {"uv": [7.2, 10.2, 8.8, 11.4]},
            "down":  {"uv": [7.2, 10.2, 8.8, 11.4]}
        }
    }
]

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

# Verify all UV coordinates
for el in clean_elements:
    for face, fdata in el["faces"].items():
        assert all(0.0 <= u <= 16.0 for u in fdata["uv"]), f"Bad UV in {el['name']} {face}: {fdata['uv']}"

# Display settings centered around Y=0
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
        "translation": [0, 0, 0],
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

# --- 3. Model JSONs ---
cannon_custom_model = {
    "credit": "SiegeMortar 3D Model (Ground-Aligned Y: -8..+8, Zero Z-Fighting)",
    "textures": {
        "particle": "siegecannon:item/cannon_wood",
        "wood": "siegecannon:item/cannon_wood",
        "metal": "siegecannon:item/cannon_metal",
        "0": "siegecannon:item/cannon_wood",
        "1": "siegecannon:item/cannon_metal"
    },
    "elements": clean_elements,
    "display": display_settings
}
json_custom_str = json.dumps(cannon_custom_model, indent=2, ensure_ascii=False)

cannon_vanilla_model = {
    "credit": "SiegeMortar 3D Model (Ground-Aligned Y: -8..+8, Vanilla Dark Oak + Iron)",
    "textures": {
        "particle": "minecraft:block/dark_oak_planks",
        "wood": "minecraft:block/dark_oak_planks",
        "metal": "minecraft:block/iron_block",
        "0": "minecraft:block/dark_oak_planks",
        "1": "minecraft:block/iron_block"
    },
    "elements": clean_elements,
    "display": display_settings
}
json_vanilla_str = json.dumps(cannon_vanilla_model, indent=2, ensure_ascii=False)

# Write standalone JSON model files
with open("public/models/cannon_1x1.json", "w", encoding="utf-8") as f:
    f.write(json_custom_str)
with open("dist/models/cannon_1x1.json", "w", encoding="utf-8") as f:
    f.write(json_custom_str)
with open("public/models/cannon_custom_textures.json", "w", encoding="utf-8") as f:
    f.write(json_custom_str)
with open("dist/models/cannon_custom_textures.json", "w", encoding="utf-8") as f:
    f.write(json_custom_str)
with open("public/models/cannon_vanilla.json", "w", encoding="utf-8") as f:
    f.write(json_vanilla_str)
with open("dist/models/cannon_vanilla.json", "w", encoding="utf-8") as f:
    f.write(json_vanilla_str)

# --- 4. Blockbench Project (.bbmodel) with embedded textures ---
bbmodel_data = {
    "meta": {
        "format_version": "4.10",
        "model_format": "java_block",
        "box_uv": False
    },
    "name": "siege_mortar_ground",
    "model_identifier": "cannon_tnt",
    "visible_box": [1, 1, 1],
    "resolution": {
        "width": 16,
        "height": 16
    },
    "elements": [],
    "outliner": [
        {
            "name": "Carriage (Wood)",
            "origin": [8, 0, 8],
            "color": 0,
            "children": [0, 1, 2, 3, 4]
        },
        {
            "name": "Chassis & Wheels (Metal)",
            "origin": [8, -0.5, 7.5],
            "color": 1,
            "children": [5, 6, 7, 8, 9, 10, 11]
        },
        {
            "name": "Mortar Barrel (Metal)",
            "origin": [8, 2, 7],
            "color": 2,
            "children": [12, 13, 14, 15, 16, 17, 18]
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
            "texture": el_def["tex_idx"]
        }
    bbmodel_data["elements"].append(bb_el)

bbmodel_str = json.dumps(bbmodel_data, indent=2, ensure_ascii=False)
with open("public/models/cannon_1x1.bbmodel", "w", encoding="utf-8") as f:
    f.write(bbmodel_str)
with open("dist/models/cannon_1x1.bbmodel", "w", encoding="utf-8") as f:
    f.write(bbmodel_str)

print("Created ground-aligned .bbmodel with embedded base64 textures!")

# --- 5. Assemble Complete Resource Pack ---
rp_dir = "complete_rp"
shutil.rmtree(rp_dir, ignore_errors=True)

folders = [
    f"{rp_dir}/assets/minecraft/font",
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

# 5.1 pack.mcmeta (15 to 48: 1.20 - 1.21.4)
pack_mcmeta = {
    "pack": {
        "pack_format": 34,
        "supported_formats": {
            "min_inclusive": 15,
            "max_inclusive": 48
        },
        "description": "TownyArchitecture & SiegeCannon Ground-Aligned Pack"
    }
}
with open(f"{rp_dir}/pack.mcmeta", "w", encoding="utf-8") as f:
    json.dump(pack_mcmeta, f, indent=2)

# 5.2 TownyArchitecture GUI Menu & Font (Fixes /tb menu)
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

# 5.3 Write 2 Textures to ALL Item & Block directories
tex_dirs = [
    f"{rp_dir}/assets/siegecannon/textures/item",
    f"{rp_dir}/assets/siegecannon/textures/block",
    f"{rp_dir}/assets/siegecannons/textures/item",
    f"{rp_dir}/assets/siegecannons/textures/block",
    f"{rp_dir}/assets/minecraft/textures/item",
    f"{rp_dir}/assets/minecraft/textures/block"
]
for d in tex_dirs:
    with open(f"{d}/cannon_wood.png", "wb") as f:
        f.write(png_wood)
    with open(f"{d}/cannon_metal.png", "wb") as f:
        f.write(png_metal)
    with open(f"{d}/cannon_tnt.png", "wb") as f:
        f.write(png_metal)

# 5.4 Write Model to ALL required paths
model_paths = [
    f"{rp_dir}/assets/siegecannon/models/item/cannon_tnt.json",
    f"{rp_dir}/assets/siegecannon/models/item/cannon.json",
    f"{rp_dir}/assets/siegecannon/models/block/cannon_tnt.json",
    f"{rp_dir}/assets/siegecannon/models/block/cannon.json",
    f"{rp_dir}/assets/siegecannons/models/item/cannon_tnt.json",
    f"{rp_dir}/assets/siegecannons/models/item/cannon.json",
    f"{rp_dir}/assets/siegecannons/models/block/cannon_tnt.json",
    f"{rp_dir}/assets/siegecannons/models/block/cannon.json",
    f"{rp_dir}/assets/minecraft/models/item/cannon_tnt.json",
    f"{rp_dir}/assets/minecraft/models/item/cannon.json"
]
for p in model_paths:
    with open(p, "w", encoding="utf-8") as f:
        f.write(json_custom_str)

# 5.5 Minecraft 1.21.2+ Items definition
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

items_tnt_121 = {
    "model": {
        "type": "minecraft:select",
        "property": "minecraft:custom_model_data",
        "cases": [
            {"when": 1, "model": {"type": "minecraft:model", "model": "siegecannon:item/cannon_tnt"}},
            {"when": 2, "model": {"type": "minecraft:model", "model": "siegecannon:item/cannon_tnt"}},
            {"when": 100, "model": {"type": "minecraft:model", "model": "siegecannon:item/cannon_tnt"}},
            {"when": 1001, "model": {"type": "minecraft:model", "model": "siegecannon:item/cannon_tnt"}},
            {"when": 7001, "model": {"type": "minecraft:model", "model": "siegecannon:item/cannon_tnt"}}
        ],
        "fallback": {
            "type": "minecraft:model",
            "model": "minecraft:item/tnt"
        }
    }
}
with open(f"{rp_dir}/assets/minecraft/items/tnt.json", "w", encoding="utf-8") as f:
    json.dump(items_tnt_121, f, indent=2)

# 5.6 TNT & Carrot-on-a-stick Overrides for 1.20 - 1.21.1
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

# --- 6. Package ZIP Archives ---
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

os.makedirs('dist', exist_ok=True)
os.makedirs('public', exist_ok=True)

jar_282 = 'public/TownyArchitecture-2.8.2.jar' if os.path.exists('public/TownyArchitecture-2.8.2.jar') else 'dist/TownyArchitecture-2.8.2.jar'
jar_main = 'public/TownyArchitecture.jar' if os.path.exists('public/TownyArchitecture.jar') else 'dist/TownyArchitecture.jar'

for bt in bundle_targets:
    with zipfile.ZipFile(bt, 'w', zipfile.ZIP_DEFLATED) as zf:
        if os.path.exists(jar_282):
            zf.write(jar_282, 'TownyArchitecture-2.8.2.jar')
        if os.path.exists(jar_main):
            zf.write(jar_main, 'TownyArchitecture.jar')
        if os.path.exists('public/TownyArchitecture.zip'):
            zf.write('public/TownyArchitecture.zip', 'TownyArchitecture.zip')
        if os.path.exists('public/TownyArchitecture-RP.zip'):
            zf.write('public/TownyArchitecture-RP.zip', 'TownyArchitecture-RP.zip')
        if os.path.exists('tmp/minecraft-build-v2/src/main/resources/config.yml'):
            zf.write('tmp/minecraft-build-v2/src/main/resources/config.yml', 'config.yml')
        if os.path.exists('tmp/minecraft-build-v2/src/main/resources/buildings.yml'):
            zf.write('tmp/minecraft-build-v2/src/main/resources/buildings.yml', 'buildings.yml')

# --- 7. Update TypeScript cannonModelData.ts ---
ts_content = f"""// Auto-generated 3D Cannon/Mortar Model Data (Ground-Aligned Y: -8..+8, Zero Z-Fighting)
export const CANNON_MODEL_JSON = {json.dumps(cannon_custom_model, indent=2, ensure_ascii=False)};
export const CANNON_VANILLA_MODEL_JSON = {json.dumps(cannon_vanilla_model, indent=2, ensure_ascii=False)};
export const CANNON_CUSTOM_MODEL_JSON = {json.dumps(cannon_custom_model, indent=2, ensure_ascii=False)};

export const CANNON_MODEL_JSON_STR = {json.dumps(json_custom_str)};
export const CANNON_VANILLA_JSON_STR = {json.dumps(json_vanilla_str)};
export const CANNON_CUSTOM_JSON_STR = {json.dumps(json_custom_str)};
export const CANNON_BBMODEL_JSON_STR = {json.dumps(bbmodel_str)};

export const CANNON_JSON_BASE64 = "{base64.b64encode(json_custom_str.encode('utf-8')).decode('ascii')}";
export const CANNON_VANILLA_JSON_BASE64 = "{base64.b64encode(json_vanilla_str.encode('utf-8')).decode('ascii')}";
export const CANNON_CUSTOM_JSON_BASE64 = "{base64.b64encode(json_custom_str.encode('utf-8')).decode('ascii')}";
export const CANNON_BBMODEL_BASE64 = "{base64.b64encode(bbmodel_str.encode('utf-8')).decode('ascii')}";
export const CANNON_WOOD_PNG_BASE64 = "{b64_wood}";
export const CANNON_METAL_PNG_BASE64 = "{b64_metal}";
export const CANNON_RP_BASE64 = "{b64}";

export const CANNON_METADATA = {{
  name: "3D Осадная Мортира (Приземлена на блок, без мерцания граней)",
  fileJsonName: "cannon_1x1.json",
  fileVanillaJsonName: "cannon_vanilla.json",
  fileCustomJsonName: "cannon_custom_textures.json",
  fileBbmodelName: "cannon_1x1.bbmodel",
  fileWoodPngName: "cannon_wood.png",
  fileMetalPngName: "cannon_metal.png",
  fileRpName: "SiegeCannon-3D-Model-RP.zip",
  elementsCount: {len(clean_elements)},
  format: "Blockbench / Minecraft Java 1.20 - 1.21+ (Ground-Aligned Y: -8..+8, Anti-Z-Fighting)",
  customModelData: 7001,
  targetItem: "siegecannon:cannon_tnt / tnt",
  dimensions: "16×16×16 (Y: -8..+8, на поверхности земли)",
  texturesUsed: ["siegecannon:item/cannon_wood (#wood)", "siegecannon:item/cannon_metal (#metal)"],
  author: "TownyArchitecture & SiegeCannon Team",
  releaseDate: "2026-10-04"
}};
"""

with open("src/data/cannonModelData.ts", "w", encoding="utf-8") as f:
    f.write(ts_content)

print(f"=== Ground-aligned pack built successfully! SHA-1: {sha1} ===")
