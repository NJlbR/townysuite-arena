import os
import json
import zipfile
import base64
import hashlib
from datetime import datetime

os.makedirs("public/models", exist_ok=True)
os.makedirs("dist/models", exist_ok=True)
os.makedirs("src/data", exist_ok=True)

# 1. Generate Minecraft Java Item/Block JSON model
minecraft_model = {
    "credit": "Made with Blockbench for SiegeCannon & TownyArchitecture",
    "texture_size": [64, 64],
    "textures": {
        "0": "block/dark_oak_planks",
        "1": "block/dark_oak_log",
        "2": "block/iron_block",
        "3": "block/blackstone",
        "4": "block/gold_block",
        "particle": "block/dark_oak_planks"
    },
    "elements": [
        # === CARRIAGE BASE & FRAME ===
        {
            "name": "carriage_bed",
            "from": [3, 1, 3],
            "to": [13, 3, 14],
            "faces": {
                "north": {"uv": [3, 1, 13, 3], "texture": "#0"},
                "east": {"uv": [3, 1, 14, 3], "texture": "#0"},
                "south": {"uv": [3, 1, 13, 3], "texture": "#0"},
                "west": {"uv": [3, 1, 14, 3], "texture": "#0"},
                "up": {"uv": [3, 3, 13, 14], "texture": "#0"},
                "down": {"uv": [3, 3, 13, 14], "texture": "#0"}
            }
        },
        {
            "name": "carriage_left_wall",
            "from": [2, 2, 2],
            "to": [4, 8, 14],
            "faces": {
                "north": {"uv": [2, 2, 4, 8], "texture": "#1"},
                "east": {"uv": [2, 2, 14, 8], "texture": "#1"},
                "south": {"uv": [2, 2, 4, 8], "texture": "#1"},
                "west": {"uv": [2, 2, 14, 8], "texture": "#1"},
                "up": {"uv": [2, 2, 4, 14], "texture": "#2"},
                "down": {"uv": [2, 2, 4, 14], "texture": "#1"}
            }
        },
        {
            "name": "carriage_right_wall",
            "from": [12, 2, 2],
            "to": [14, 8, 14],
            "faces": {
                "north": {"uv": [12, 2, 14, 8], "texture": "#1"},
                "east": {"uv": [2, 2, 14, 8], "texture": "#1"},
                "south": {"uv": [12, 2, 14, 8], "texture": "#1"},
                "west": {"uv": [2, 2, 14, 8], "texture": "#1"},
                "up": {"uv": [12, 2, 14, 14], "texture": "#2"},
                "down": {"uv": [12, 2, 14, 14], "texture": "#1"}
            }
        },
        {
            "name": "front_bumper_iron",
            "from": [3, 1, 1],
            "to": [13, 3, 3],
            "faces": {
                "north": {"uv": [3, 1, 13, 3], "texture": "#2"},
                "east": {"uv": [1, 1, 3, 3], "texture": "#2"},
                "south": {"uv": [3, 1, 13, 3], "texture": "#2"},
                "west": {"uv": [1, 1, 3, 3], "texture": "#2"},
                "up": {"uv": [3, 1, 13, 3], "texture": "#2"},
                "down": {"uv": [3, 1, 13, 3], "texture": "#2"}
            }
        },
        {
            "name": "rear_trail_spade",
            "from": [5, 0.5, 13.5],
            "to": [11, 2.5, 16],
            "faces": {
                "north": {"uv": [5, 0, 11, 2], "texture": "#1"},
                "east": {"uv": [13, 0, 16, 2], "texture": "#1"},
                "south": {"uv": [5, 0, 11, 2], "texture": "#2"},
                "west": {"uv": [13, 0, 16, 2], "texture": "#1"},
                "up": {"uv": [5, 13, 11, 16], "texture": "#2"},
                "down": {"uv": [5, 13, 11, 16], "texture": "#1"}
            }
        },
        {
            "name": "elevation_wedge",
            "from": [6, 3, 9],
            "to": [10, 5.5, 12],
            "faces": {
                "north": {"uv": [6, 3, 10, 5], "texture": "#3"},
                "east": {"uv": [9, 3, 12, 5], "texture": "#3"},
                "south": {"uv": [6, 3, 10, 5], "texture": "#3"},
                "west": {"uv": [9, 3, 12, 5], "texture": "#3"},
                "up": {"uv": [6, 9, 10, 12], "texture": "#4"},
                "down": {"uv": [6, 9, 10, 12], "texture": "#3"}
            }
        },
        # === WHEELS & AXLE ===
        {
            "name": "axle_rod",
            "from": [1, 3.5, 6.5],
            "to": [15, 5, 8],
            "faces": {
                "north": {"uv": [1, 3, 15, 5], "texture": "#2"},
                "east": {"uv": [6, 3, 8, 5], "texture": "#4"},
                "south": {"uv": [1, 3, 15, 5], "texture": "#2"},
                "west": {"uv": [6, 3, 8, 5], "texture": "#4"},
                "up": {"uv": [1, 6, 15, 8], "texture": "#2"},
                "down": {"uv": [1, 6, 15, 8], "texture": "#2"}
            }
        },
        {
            "name": "left_wheel_main",
            "from": [0.5, 0.5, 4],
            "to": [2.5, 8, 10.5],
            "faces": {
                "north": {"uv": [0, 0, 2, 7], "texture": "#2"},
                "east": {"uv": [4, 1, 10, 8], "texture": "#1"},
                "south": {"uv": [0, 0, 2, 7], "texture": "#2"},
                "west": {"uv": [4, 1, 10, 8], "texture": "#1"},
                "up": {"uv": [0, 4, 2, 10], "texture": "#2"},
                "down": {"uv": [0, 4, 2, 10], "texture": "#2"}
            }
        },
        {
            "name": "left_hubcap",
            "from": [0, 3.25, 6.25],
            "to": [0.5, 5.25, 8.25],
            "faces": {
                "north": {"uv": [0, 0, 1, 2], "texture": "#4"},
                "east": {"uv": [6, 6, 8, 8], "texture": "#4"},
                "south": {"uv": [0, 0, 1, 2], "texture": "#4"},
                "west": {"uv": [6, 6, 8, 8], "texture": "#4"},
                "up": {"uv": [0, 0, 1, 2], "texture": "#4"},
                "down": {"uv": [0, 0, 1, 2], "texture": "#4"}
            }
        },
        {
            "name": "right_wheel_main",
            "from": [13.5, 0.5, 4],
            "to": [15.5, 8, 10.5],
            "faces": {
                "north": {"uv": [13, 0, 15, 7], "texture": "#2"},
                "east": {"uv": [4, 1, 10, 8], "texture": "#1"},
                "south": {"uv": [13, 0, 15, 7], "texture": "#2"},
                "west": {"uv": [4, 1, 10, 8], "texture": "#1"},
                "up": {"uv": [13, 4, 15, 10], "texture": "#2"},
                "down": {"uv": [13, 4, 15, 10], "texture": "#2"}
            }
        },
        {
            "name": "right_hubcap",
            "from": [15.5, 3.25, 6.25],
            "to": [16, 5.25, 8.25],
            "faces": {
                "north": {"uv": [0, 0, 1, 2], "texture": "#4"},
                "east": {"uv": [6, 6, 8, 8], "texture": "#4"},
                "south": {"uv": [0, 0, 1, 2], "texture": "#4"},
                "west": {"uv": [6, 6, 8, 8], "texture": "#4"},
                "up": {"uv": [0, 0, 1, 2], "texture": "#4"},
                "down": {"uv": [0, 0, 1, 2], "texture": "#4"}
            }
        },
        # === CANNON BARREL (ELEVATED -10 DEG) ===
        {
            "name": "cascabel_knob",
            "from": [7, 5.5, 12],
            "to": [9, 7.5, 13.5],
            "rotation": {"angle": -11.25, "axis": "x", "origin": [8, 6.5, 7.5]},
            "faces": {
                "north": {"uv": [7, 5, 9, 7], "texture": "#3"},
                "east": {"uv": [12, 5, 13, 7], "texture": "#3"},
                "south": {"uv": [7, 5, 9, 7], "texture": "#4"},
                "west": {"uv": [12, 5, 13, 7], "texture": "#3"},
                "up": {"uv": [7, 12, 9, 13], "texture": "#3"},
                "down": {"uv": [7, 12, 9, 13], "texture": "#3"}
            }
        },
        {
            "name": "breech_body",
            "from": [5, 4.5, 7],
            "to": [11, 8.5, 12],
            "rotation": {"angle": -11.25, "axis": "x", "origin": [8, 6.5, 7.5]},
            "faces": {
                "north": {"uv": [5, 4, 11, 8], "texture": "#3"},
                "east": {"uv": [7, 4, 12, 8], "texture": "#3"},
                "south": {"uv": [5, 4, 11, 8], "texture": "#3"},
                "west": {"uv": [7, 4, 12, 8], "texture": "#3"},
                "up": {"uv": [5, 7, 11, 12], "texture": "#3"},
                "down": {"uv": [5, 7, 11, 12], "texture": "#3"}
            }
        },
        {
            "name": "breech_ring",
            "from": [4.75, 4.25, 9.5],
            "to": [11.25, 8.75, 11],
            "rotation": {"angle": -11.25, "axis": "x", "origin": [8, 6.5, 7.5]},
            "faces": {
                "north": {"uv": [4, 4, 11, 8], "texture": "#4"},
                "east": {"uv": [9, 4, 11, 8], "texture": "#4"},
                "south": {"uv": [4, 4, 11, 8], "texture": "#4"},
                "west": {"uv": [9, 4, 11, 8], "texture": "#4"},
                "up": {"uv": [4, 9, 11, 11], "texture": "#4"},
                "down": {"uv": [4, 9, 11, 11], "texture": "#4"}
            }
        },
        {
            "name": "trunnions_pivot",
            "from": [3, 5.5, 6.5],
            "to": [13, 7.5, 8.5],
            "rotation": {"angle": -11.25, "axis": "x", "origin": [8, 6.5, 7.5]},
            "faces": {
                "north": {"uv": [3, 5, 13, 7], "texture": "#2"},
                "east": {"uv": [6, 5, 8, 7], "texture": "#4"},
                "south": {"uv": [3, 5, 13, 7], "texture": "#2"},
                "west": {"uv": [6, 5, 8, 7], "texture": "#4"},
                "up": {"uv": [3, 6, 13, 8], "texture": "#2"},
                "down": {"uv": [3, 6, 13, 8], "texture": "#2"}
            }
        },
        {
            "name": "barrel_mid",
            "from": [5.5, 5, 1],
            "to": [10.5, 8, 7],
            "rotation": {"angle": -11.25, "axis": "x", "origin": [8, 6.5, 7.5]},
            "faces": {
                "north": {"uv": [5, 5, 10, 8], "texture": "#3"},
                "east": {"uv": [1, 5, 7, 8], "texture": "#3"},
                "south": {"uv": [5, 5, 10, 8], "texture": "#3"},
                "west": {"uv": [1, 5, 7, 8], "texture": "#3"},
                "up": {"uv": [5, 1, 10, 7], "texture": "#3"},
                "down": {"uv": [5, 1, 10, 7], "texture": "#3"}
            }
        },
        {
            "name": "barrel_chase",
            "from": [6, 5.25, -3],
            "to": [10, 7.75, 1],
            "rotation": {"angle": -11.25, "axis": "x", "origin": [8, 6.5, 7.5]},
            "faces": {
                "north": {"uv": [6, 5, 10, 7], "texture": "#3"},
                "east": {"uv": [0, 5, 4, 7], "texture": "#3"},
                "south": {"uv": [6, 5, 10, 7], "texture": "#3"},
                "west": {"uv": [0, 5, 4, 7], "texture": "#3"},
                "up": {"uv": [6, 0, 10, 4], "texture": "#3"},
                "down": {"uv": [6, 0, 10, 4], "texture": "#3"}
            }
        },
        {
            "name": "muzzle_swell_ring",
            "from": [5.5, 4.75, -5],
            "to": [10.5, 8.25, -3],
            "rotation": {"angle": -11.25, "axis": "x", "origin": [8, 6.5, 7.5]},
            "faces": {
                "north": {"uv": [5, 4, 10, 8], "texture": "#4"},
                "east": {"uv": [0, 4, 2, 8], "texture": "#3"},
                "south": {"uv": [5, 4, 10, 8], "texture": "#3"},
                "west": {"uv": [0, 4, 2, 8], "texture": "#3"},
                "up": {"uv": [5, 0, 10, 2], "texture": "#4"},
                "down": {"uv": [5, 0, 10, 2], "texture": "#4"}
            }
        },
        {
            "name": "muzzle_bore_interior",
            "from": [6.5, 5.75, -5.05],
            "to": [9.5, 7.25, -4.95],
            "rotation": {"angle": -11.25, "axis": "x", "origin": [8, 6.5, 7.5]},
            "faces": {
                "north": {"uv": [0, 0, 3, 1], "texture": "#3"},
                "east": {"uv": [0, 0, 1, 1], "texture": "#3"},
                "south": {"uv": [0, 0, 3, 1], "texture": "#3"},
                "west": {"uv": [0, 0, 1, 1], "texture": "#3"},
                "up": {"uv": [0, 0, 3, 1], "texture": "#3"},
                "down": {"uv": [0, 0, 3, 1], "texture": "#3"}
            }
        },
        {
            "name": "touchhole_fuse",
            "from": [7.5, 8.5, 9.5],
            "to": [8.5, 9.5, 10.5],
            "rotation": {"angle": -11.25, "axis": "x", "origin": [8, 6.5, 7.5]},
            "faces": {
                "north": {"uv": [7, 8, 8, 9], "texture": "#4"},
                "east": {"uv": [9, 8, 10, 9], "texture": "#4"},
                "south": {"uv": [7, 8, 8, 9], "texture": "#4"},
                "west": {"uv": [9, 8, 10, 9], "texture": "#4"},
                "up": {"uv": [7, 9, 8, 10], "texture": "#4"},
                "down": {"uv": [7, 9, 8, 10], "texture": "#4"}
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

# Write JSON model
json_str = json.dumps(minecraft_model, indent=2, ensure_ascii=False)
with open("public/models/cannon_1x1.json", "w", encoding="utf-8") as f:
    f.write(json_str)
with open("dist/models/cannon_1x1.json", "w", encoding="utf-8") as f:
    f.write(json_str)

# 2. Generate Blockbench Project (.bbmodel) file
bbmodel = {
    "meta": {
        "format_version": "4.10",
        "model_format": "java_block",
        "box_uv": False
    },
    "name": "siege_cannon_1x1",
    "model_identifier": "siege_cannon_1x1",
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
            "children": [0, 1, 2, 3, 4, 5]
        },
        {
            "name": "Wheels",
            "origin": [8, 4, 7],
            "color": 1,
            "children": [6, 7, 8, 9, 10]
        },
        {
            "name": "Barrel",
            "origin": [8, 6.5, 7.5],
            "color": 2,
            "children": [11, 12, 13, 14, 15, 16, 17, 18, 19]
        }
    ],
    "textures": [
        {
            "path": "block/dark_oak_planks",
            "name": "dark_oak_planks",
            "folder": "block",
            "namespace": "minecraft",
            "id": "0",
            "particle": True,
            "render_mode": "default",
            "visible": True,
            "mode": "bitmap",
            "saved": True,
            "uuid": "d1e2f3a4-b5c6-7d8e-9f0a-1b2c3d4e5f6a",
            "source": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAAXNSR0IArs4c6QAAAFNJREFUOE9jZGBg+M/AwMDACMV/GBgZGJkYqA7gUfQ/Kg4fRgwDYkQyAGQASQxkJlgKxkE8Bv8/GB40oQYQGgZgNxJvFJDNBdEAQ5gqGhkYGAD2HRIREo4s9QAAAABJRU5ErkJggg=="
        },
        {
            "path": "block/dark_oak_log",
            "name": "dark_oak_log",
            "folder": "block",
            "namespace": "minecraft",
            "id": "1",
            "particle": False,
            "render_mode": "default",
            "visible": True,
            "mode": "bitmap",
            "saved": True,
            "uuid": "a2b3c4d5-e6f7-8a9b-0c1d-2e3f4a5b6c7d",
            "source": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAAXNSR0IArs4c6QAAAEFJREFUOE9jZGBg+M8wCoYBwMAIxRAGKAGM1ABwGMA/Kg4fRgwDYkQyAGQASQxkJlgKxkE8Bv8/GB40oQYQGgZgNwIAt4YIEWwZ96oAAAAASUVORK5CYII="
        },
        {
            "path": "block/iron_block",
            "name": "iron_block",
            "folder": "block",
            "namespace": "minecraft",
            "id": "2",
            "particle": False,
            "render_mode": "default",
            "visible": True,
            "mode": "bitmap",
            "saved": True,
            "uuid": "b3c4d5e6-f7a8-9b0c-1d2e-3f4a5b6c7d8e",
            "source": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAAXNSR0IArs4c6QAAAEFJREFUOE9jZGBg+M8wCoYBwMAIxRAGKAGM1ABwGMA/Kg4fRgwDYkQyAGQASQxkJlgKxkE8Bv8/GB40oQYQGgZgNwIAt4YIEWwZ96oAAAAASUVORK5CYII="
        },
        {
            "path": "block/blackstone",
            "name": "blackstone",
            "folder": "block",
            "namespace": "minecraft",
            "id": "3",
            "particle": False,
            "render_mode": "default",
            "visible": True,
            "mode": "bitmap",
            "saved": True,
            "uuid": "c4d5e6f7-a8b9-0c1d-2e3f-4a5b6c7d8e9f",
            "source": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAAXNSR0IArs4c6QAAAEFJREFUOE9jZGBg+M8wCoYBwMAIxRAGKAGM1ABwGMA/Kg4fRgwDYkQyAGQASQxkJlgKxkE8Bv8/GB40oQYQGgZgNwIAt4YIEWwZ96oAAAAASUVORK5CYII="
        },
        {
            "path": "block/gold_block",
            "name": "gold_block",
            "folder": "block",
            "namespace": "minecraft",
            "id": "4",
            "particle": False,
            "render_mode": "default",
            "visible": True,
            "mode": "bitmap",
            "saved": True,
            "uuid": "d5e6f7a8-b9c0-1d2e-3f4a-5b6c7d8e9f0a",
            "source": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAAXNSR0IArs4c6QAAAEFJREFUOE9jZGBg+M8wCoYBwMAIxRAGKAGM1ABwGMA/Kg4fRgwDYkQyAGQASQxkJlgKxkE8Bv8/GB40oQYQGgZgNwIAt4YIEWwZ96oAAAAASUVORK5CYII="
        }
    ],
    "display": minecraft_model["display"]
}

# Convert elements to bbmodel format
for idx, el in enumerate(minecraft_model["elements"]):
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
    if "rotation" in el:
        bb_el["rotation"] = [el["rotation"]["angle"] if el["rotation"]["axis"] == "x" else 0,
                             el["rotation"]["angle"] if el["rotation"]["axis"] == "y" else 0,
                             el["rotation"]["angle"] if el["rotation"]["axis"] == "z" else 0]
        bb_el["origin"] = el["rotation"]["origin"]
    
    for face, face_data in el["faces"].items():
        tex_id = face_data["texture"].replace("#", "")
        bb_el["faces"][face] = {
            "uv": face_data["uv"],
            "texture": int(tex_id) if tex_id.isdigit() else 0
        }
    bbmodel["elements"].append(bb_el)

bbmodel_str = json.dumps(bbmodel, indent=2, ensure_ascii=False)
with open("public/models/cannon_1x1.bbmodel", "w", encoding="utf-8") as f:
    f.write(bbmodel_str)
with open("dist/models/cannon_1x1.bbmodel", "w", encoding="utf-8") as f:
    f.write(bbmodel_str)

# 3. Create Resourcepack with the Cannon Model
rp_zip_path = "public/SiegeCannon-3D-Model-RP.zip"
with zipfile.ZipFile(rp_zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
    # pack.mcmeta
    mcmeta = {
        "pack": {
            "pack_format": 34,
            "description": "3D Siege Cannon 1x1 Model for Minecraft 1.20-1.21+ (Blockbench)"
        }
    }
    zf.writestr("pack.mcmeta", json.dumps(mcmeta, indent=2))
    
    # Models
    zf.writestr("assets/minecraft/models/item/cannon_1x1.json", json_str)
    zf.writestr("assets/minecraft/models/block/cannon_1x1.json", json_str)
    
    # Example CustomModelData mapping on carrot_on_a_stick (CMD: 7001)
    coas_override = {
        "parent": "minecraft:item/handheld",
        "textures": {
            "layer0": "minecraft:item/carrot_on_a_stick"
        },
        "overrides": [
            {
                "predicate": {"custom_model_data": 7001},
                "model": "minecraft:item/cannon_1x1"
            }
        ]
    }
    zf.writestr("assets/minecraft/models/item/carrot_on_a_stick.json", json.dumps(coas_override, indent=2))
    zf.writestr("cannon_1x1.bbmodel", bbmodel_str)
    zf.writestr("README.txt", "3D Siege Cannon (1x1 Block) Model for Minecraft & Blockbench\nCustomModelData: 7001 (carrot_on_a_stick)\nCompatible with Item Display, ArmorStand, and Cannons plugins!")

import shutil
shutil.copy2(rp_zip_path, "dist/SiegeCannon-3D-Model-RP.zip")

# Base64 encodings
with open("public/models/cannon_1x1.json", "rb") as f:
    json_b64 = base64.b64encode(f.read()).decode("utf-8")
with open("public/models/cannon_1x1.bbmodel", "rb") as f:
    bbmodel_b64 = base64.b64encode(f.read()).decode("utf-8")
with open(rp_zip_path, "rb") as f:
    rp_b64 = base64.b64encode(f.read()).decode("utf-8")

# Export TS Data
ts_content = f"""// Auto-generated 3D Cannon Model Data
export const CANNON_MODEL_JSON = {json.dumps(minecraft_model, indent=2, ensure_ascii=False)};

export const CANNON_MODEL_JSON_STR = {json.dumps(json_str)};
export const CANNON_BBMODEL_JSON_STR = {json.dumps(bbmodel_str)};

export const CANNON_JSON_BASE64 = "{json_b64}";
export const CANNON_BBMODEL_BASE64 = "{bbmodel_b64}";
export const CANNON_RP_BASE64 = "{rp_b64}";

export const CANNON_METADATA = {{
  name: "3D Осадная Пушка (1x1 Блок)",
  fileJsonName: "cannon_1x1.json",
  fileBbmodelName: "cannon_1x1.bbmodel",
  fileRpName: "SiegeCannon-3D-Model-RP.zip",
  elementsCount: {len(minecraft_model["elements"])},
  format: "Blockbench / Minecraft Java 1.20 - 1.21+",
  customModelData: 7001,
  targetItem: "carrot_on_a_stick / iron_horse_armor / netherite_ingot",
  dimensions: "16x16x16 (В точности 1x1 блок Minecraft)",
  author: "TownyArchitecture & SiegeCannon Team",
  releaseDate: "{datetime.utcnow().strftime('%Y-%m-%d')}"
}};
"""

with open("src/data/cannonModelData.ts", "w", encoding="utf-8") as f:
    f.write(ts_content)

print("3D Cannon Model generated successfully!")
