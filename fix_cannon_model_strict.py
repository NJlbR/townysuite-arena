import json
import os
import zipfile
import hashlib
import base64
import shutil

# Strictly compliant Minecraft Java Item/Block Model (100% crash-proof schema)
cannon_model = {
    "credit": "SiegeCannon 3D Model for Minecraft 1.20-1.21+",
    "parent": "minecraft:block/block",
    "textures": {
        "particle": "minecraft:block/dark_oak_planks",
        "wood": "minecraft:block/dark_oak_planks",
        "log": "minecraft:block/dark_oak_log",
        "iron": "minecraft:block/iron_block",
        "dark": "minecraft:block/blackstone",
        "gold": "minecraft:block/gold_block"
    },
    "elements": [
        # === CARRIAGE BASE & FRAME ===
        {
            "name": "carriage_bed",
            "from": [3, 1, 2],
            "to": [13, 3, 15],
            "faces": {
                "north": {"uv": [3, 13, 13, 15], "texture": "#wood"},
                "east":  {"uv": [2, 13, 15, 15], "texture": "#wood"},
                "south": {"uv": [3, 13, 13, 15], "texture": "#wood"},
                "west":  {"uv": [2, 13, 15, 15], "texture": "#wood"},
                "up":    {"uv": [3, 2, 13, 15],   "texture": "#wood"},
                "down":  {"uv": [3, 2, 13, 15],   "texture": "#wood"}
            }
        },
        {
            "name": "carriage_left_cheek",
            "from": [2, 2, 2],
            "to": [4, 7, 15],
            "faces": {
                "north": {"uv": [2, 9, 4, 14],  "texture": "#log"},
                "east":  {"uv": [2, 9, 15, 14], "texture": "#log"},
                "south": {"uv": [2, 9, 4, 14],  "texture": "#log"},
                "west":  {"uv": [2, 9, 15, 14], "texture": "#log"},
                "up":    {"uv": [2, 2, 4, 15],  "texture": "#iron"},
                "down":  {"uv": [2, 2, 4, 15],  "texture": "#log"}
            }
        },
        {
            "name": "carriage_right_cheek",
            "from": [12, 2, 2],
            "to": [14, 7, 15],
            "faces": {
                "north": {"uv": [12, 9, 14, 14], "texture": "#log"},
                "east":  {"uv": [2, 9, 15, 14],  "texture": "#log"},
                "south": {"uv": [12, 9, 14, 14], "texture": "#log"},
                "west":  {"uv": [2, 9, 15, 14],  "texture": "#log"},
                "up":    {"uv": [12, 2, 14, 15], "texture": "#iron"},
                "down":  {"uv": [12, 2, 14, 15], "texture": "#log"}
            }
        },
        {
            "name": "rear_trail_spade",
            "from": [5, 0.5, 13],
            "to": [11, 2.5, 16],
            "faces": {
                "north": {"uv": [5, 13, 11, 15], "texture": "#iron"},
                "east":  {"uv": [13, 13, 16, 15], "texture": "#iron"},
                "south": {"uv": [5, 13, 11, 15], "texture": "#iron"},
                "west":  {"uv": [13, 13, 16, 15], "texture": "#iron"},
                "up":    {"uv": [5, 13, 11, 16], "texture": "#iron"},
                "down":  {"uv": [5, 13, 11, 16], "texture": "#iron"}
            }
        },
        {
            "name": "elevation_wedge",
            "from": [6, 3, 9],
            "to": [10, 5, 13],
            "faces": {
                "north": {"uv": [6, 11, 10, 13], "texture": "#dark"},
                "east":  {"uv": [9, 11, 13, 13], "texture": "#dark"},
                "south": {"uv": [6, 11, 10, 13], "texture": "#dark"},
                "west":  {"uv": [9, 11, 13, 13], "texture": "#dark"},
                "up":    {"uv": [6, 9, 10, 13],  "texture": "#gold"},
                "down":  {"uv": [6, 9, 10, 13],  "texture": "#dark"}
            }
        },

        # === WHEELS & AXLE ===
        {
            "name": "axle_rod",
            "from": [1, 3.5, 7],
            "to": [15, 5, 8.5],
            "faces": {
                "north": {"uv": [1, 11, 15, 12], "texture": "#iron"},
                "east":  {"uv": [7, 11, 8, 12],  "texture": "#gold"},
                "south": {"uv": [1, 11, 15, 12], "texture": "#iron"},
                "west":  {"uv": [7, 11, 8, 12],  "texture": "#gold"},
                "up":    {"uv": [1, 7, 15, 8],   "texture": "#iron"},
                "down":  {"uv": [1, 7, 15, 8],   "texture": "#iron"}
            }
        },
        {
            "name": "left_wheel",
            "from": [0.5, 0.5, 4],
            "to": [2.5, 8.5, 11.5],
            "faces": {
                "north": {"uv": [0, 8, 2, 16],  "texture": "#iron"},
                "east":  {"uv": [4, 8, 11, 16], "texture": "#wood"},
                "south": {"uv": [0, 8, 2, 16],  "texture": "#iron"},
                "west":  {"uv": [4, 8, 11, 16], "texture": "#wood"},
                "up":    {"uv": [0, 4, 2, 11],  "texture": "#iron"},
                "down":  {"uv": [0, 4, 2, 11],  "texture": "#iron"}
            }
        },
        {
            "name": "left_hubcap",
            "from": [0, 3.5, 6.75],
            "to": [0.5, 5.5, 8.75],
            "faces": {
                "north": {"uv": [0, 14, 1, 16], "texture": "#gold"},
                "east":  {"uv": [6, 14, 8, 16], "texture": "#gold"},
                "south": {"uv": [0, 14, 1, 16], "texture": "#gold"},
                "west":  {"uv": [6, 14, 8, 16], "texture": "#gold"},
                "up":    {"uv": [0, 14, 1, 16], "texture": "#gold"},
                "down":  {"uv": [0, 14, 1, 16], "texture": "#gold"}
            }
        },
        {
            "name": "right_wheel",
            "from": [13.5, 0.5, 4],
            "to": [15.5, 8.5, 11.5],
            "faces": {
                "north": {"uv": [13, 8, 15, 16], "texture": "#iron"},
                "east":  {"uv": [4, 8, 11, 16],  "texture": "#wood"},
                "south": {"uv": [13, 8, 15, 16], "texture": "#iron"},
                "west":  {"uv": [4, 8, 11, 16],  "texture": "#wood"},
                "up":    {"uv": [13, 4, 15, 11], "texture": "#iron"},
                "down":  {"uv": [13, 4, 15, 11], "texture": "#iron"}
            }
        },
        {
            "name": "right_hubcap",
            "from": [15.5, 3.5, 6.75],
            "to": [16, 5.5, 8.75],
            "faces": {
                "north": {"uv": [0, 14, 1, 16], "texture": "#gold"},
                "east":  {"uv": [6, 14, 8, 16], "texture": "#gold"},
                "south": {"uv": [0, 14, 1, 16], "texture": "#gold"},
                "west":  {"uv": [6, 14, 8, 16], "texture": "#gold"},
                "up":    {"uv": [0, 14, 1, 16], "texture": "#gold"},
                "down":  {"uv": [0, 14, 1, 16], "texture": "#gold"}
            }
        },

        # === CANNON BARREL (HEAVY SIEGE CANNON) ===
        {
            "name": "cascabel_knob",
            "from": [7, 5.5, 13.5],
            "to": [9, 7.5, 15],
            "faces": {
                "north": {"uv": [7, 8, 9, 10],   "texture": "#dark"},
                "east":  {"uv": [13, 8, 15, 10], "texture": "#dark"},
                "south": {"uv": [7, 8, 9, 10],   "texture": "#gold"},
                "west":  {"uv": [13, 8, 15, 10], "texture": "#dark"},
                "up":    {"uv": [7, 13, 9, 15],  "texture": "#dark"},
                "down":  {"uv": [7, 13, 9, 15],  "texture": "#dark"}
            }
        },
        {
            "name": "breech_base",
            "from": [5, 4.5, 8],
            "to": [11, 8.5, 13.5],
            "faces": {
                "north": {"uv": [5, 7, 11, 11],  "texture": "#dark"},
                "east":  {"uv": [8, 7, 13, 11],  "texture": "#dark"},
                "south": {"uv": [5, 7, 11, 11],  "texture": "#dark"},
                "west":  {"uv": [8, 7, 13, 11],  "texture": "#dark"},
                "up":    {"uv": [5, 8, 11, 13],  "texture": "#dark"},
                "down":  {"uv": [5, 8, 11, 13],  "texture": "#dark"}
            }
        },
        {
            "name": "breech_reinforcement_ring",
            "from": [4.75, 4.25, 10.5],
            "to": [11.25, 8.75, 12],
            "faces": {
                "north": {"uv": [4, 7, 11, 11],  "texture": "#gold"},
                "east":  {"uv": [10, 7, 12, 11], "texture": "#gold"},
                "south": {"uv": [4, 7, 11, 11],  "texture": "#gold"},
                "west":  {"uv": [10, 7, 12, 11], "texture": "#gold"},
                "up":    {"uv": [4, 10, 11, 12], "texture": "#gold"},
                "down":  {"uv": [4, 10, 11, 12], "texture": "#gold"}
            }
        },
        {
            "name": "trunnions_pivot",
            "from": [2, 5.5, 7],
            "to": [14, 7.5, 9],
            "faces": {
                "north": {"uv": [2, 8, 14, 10], "texture": "#iron"},
                "east":  {"uv": [7, 8, 9, 10],  "texture": "#gold"},
                "south": {"uv": [2, 8, 14, 10], "texture": "#iron"},
                "west":  {"uv": [7, 8, 9, 10],  "texture": "#gold"},
                "up":    {"uv": [2, 7, 14, 9],  "texture": "#iron"},
                "down":  {"uv": [2, 7, 14, 9],  "texture": "#iron"}
            }
        },
        {
            "name": "barrel_mid",
            "from": [5.5, 5, 3],
            "to": [10.5, 8, 8],
            "faces": {
                "north": {"uv": [5, 8, 10, 11], "texture": "#dark"},
                "east":  {"uv": [3, 8, 8, 11],  "texture": "#dark"},
                "south": {"uv": [5, 8, 10, 11], "texture": "#dark"},
                "west":  {"uv": [3, 8, 8, 11],  "texture": "#dark"},
                "up":    {"uv": [5, 3, 10, 8],  "texture": "#dark"},
                "down":  {"uv": [5, 3, 10, 8],  "texture": "#dark"}
            }
        },
        {
            "name": "barrel_chase",
            "from": [6, 5.25, 0.5],
            "to": [10, 7.75, 3],
            "faces": {
                "north": {"uv": [6, 8, 10, 10], "texture": "#dark"},
                "east":  {"uv": [0, 8, 3, 10],  "texture": "#dark"},
                "south": {"uv": [6, 8, 10, 10], "texture": "#dark"},
                "west":  {"uv": [0, 8, 3, 10],  "texture": "#dark"},
                "up":    {"uv": [6, 0, 10, 3],  "texture": "#dark"},
                "down":  {"uv": [6, 0, 10, 3],  "texture": "#dark"}
            }
        },
        {
            "name": "muzzle_ring",
            "from": [5.5, 4.75, 0],
            "to": [10.5, 8.25, 1],
            "faces": {
                "north": {"uv": [5, 7, 10, 11], "texture": "#gold"},
                "east":  {"uv": [0, 7, 1, 11],  "texture": "#dark"},
                "south": {"uv": [5, 7, 10, 11], "texture": "#dark"},
                "west":  {"uv": [0, 7, 1, 11],  "texture": "#dark"},
                "up":    {"uv": [5, 0, 10, 1],  "texture": "#gold"},
                "down":  {"uv": [5, 0, 10, 1],  "texture": "#gold"}
            }
        },
        {
            "name": "muzzle_bore",
            "from": [6.5, 5.75, 0],
            "to": [9.5, 7.25, 0.1],
            "faces": {
                "north": {"uv": [6, 8, 9, 10], "texture": "#dark"},
                "east":  {"uv": [0, 8, 1, 10], "texture": "#dark"},
                "south": {"uv": [6, 8, 9, 10], "texture": "#dark"},
                "west":  {"uv": [0, 8, 1, 10], "texture": "#dark"},
                "up":    {"uv": [6, 0, 9, 1],  "texture": "#dark"},
                "down":  {"uv": [6, 0, 9, 1],  "texture": "#dark"}
            }
        },
        {
            "name": "touchhole_fuse",
            "from": [7.5, 8.5, 10.5],
            "to": [8.5, 9.5, 11.5],
            "faces": {
                "north": {"uv": [7, 14, 8, 15], "texture": "#gold"},
                "east":  {"uv": [10, 14, 11, 15], "texture": "#gold"},
                "south": {"uv": [7, 14, 8, 15], "texture": "#gold"},
                "west":  {"uv": [10, 14, 11, 15], "texture": "#gold"},
                "up":    {"uv": [7, 10, 8, 11], "texture": "#gold"},
                "down":  {"uv": [7, 10, 8, 11], "texture": "#gold"}
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

json_str = json.dumps(cannon_model, indent=2, ensure_ascii=False)

# Validate strictly:
for el in cannon_model["elements"]:
    assert len(el["from"]) == 3
    assert len(el["to"]) == 3
    for v in el["from"] + el["to"]:
        assert -16.0 <= v <= 32.0, f"Value {v} out of bounds"
    for face_name, face_data in el["faces"].items():
        assert len(face_data["uv"]) == 4
        for u in face_data["uv"]:
            assert 0.0 <= u <= 16.0, f"UV {u} out of bounds"
        assert face_data["texture"].startswith("#")
        tex_key = face_data["texture"][1:]
        assert tex_key in cannon_model["textures"], f"Texture {tex_key} not in textures dict"

print("All elements passed strict validation!")

# Write to public/models/ and dist/models/
os.makedirs("public/models", exist_ok=True)
os.makedirs("dist/models", exist_ok=True)
with open("public/models/cannon_1x1.json", "w", encoding="utf-8") as f:
    f.write(json_str)
with open("dist/models/cannon_1x1.json", "w", encoding="utf-8") as f:
    f.write(json_str)

# Write to tmp_rp/assets/siegecannon/models/item/cannon_tnt.json
sc_item_dir = "tmp_rp/assets/siegecannon/models/item"
mc_item_dir = "tmp_rp/assets/minecraft/models/item"
os.makedirs(sc_item_dir, exist_ok=True)
os.makedirs(mc_item_dir, exist_ok=True)

with open(os.path.join(sc_item_dir, "cannon_tnt.json"), "w", encoding="utf-8") as f:
    f.write(json_str)
with open(os.path.join(sc_item_dir, "cannon.json"), "w", encoding="utf-8") as f:
    f.write(json_str)
with open(os.path.join(mc_item_dir, "cannon_tnt.json"), "w", encoding="utf-8") as f:
    f.write(json_str)

# tnt.json with overrides
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
with open(os.path.join(mc_item_dir, "tnt.json"), "w", encoding="utf-8") as f:
    json.dump(tnt_override, f, indent=2)

# Repackage all resource packs
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

print(f"Packaged successfully! New Resource Pack SHA-1: {sha1}")
