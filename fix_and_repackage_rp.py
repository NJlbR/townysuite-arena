import os
import json
import zipfile
import base64
import hashlib
import shutil

print("=== 1. Updating cannon_tnt.json with explicit minecraft: namespaces ===")

# Read cannon_1x1.json
with open("public/models/cannon_1x1.json", "r", encoding="utf-8") as f:
    model_data = json.load(f)

# Ensure all textures use explicit "minecraft:block/..."
model_data["textures"] = {
    "0": "minecraft:block/dark_oak_planks",
    "1": "minecraft:block/dark_oak_log",
    "2": "minecraft:block/iron_block",
    "3": "minecraft:block/blackstone",
    "4": "minecraft:block/gold_block",
    "particle": "minecraft:block/dark_oak_planks"
}

json_str = json.dumps(model_data, indent=2, ensure_ascii=False)

# Write to public/models/ and dist/models/
with open("public/models/cannon_1x1.json", "w", encoding="utf-8") as f:
    f.write(json_str)
with open("dist/models/cannon_1x1.json", "w", encoding="utf-8") as f:
    f.write(json_str)

# Ensure tmp_rp paths
siegecannon_model_dir = "tmp_rp/assets/siegecannon/models/item"
minecraft_model_dir = "tmp_rp/assets/minecraft/models/item"
os.makedirs(siegecannon_model_dir, exist_ok=True)
os.makedirs(minecraft_model_dir, exist_ok=True)

# Write cannon_tnt.json
dst_cannon_tnt = os.path.join(siegecannon_model_dir, "cannon_tnt.json")
with open(dst_cannon_tnt, "w", encoding="utf-8") as f:
    f.write(json_str)
print(f"Written: {dst_cannon_tnt}")

# Also create assets/minecraft/models/item/tnt.json with overrides for SiegeCannons CustomModelData
tnt_override_model = {
    "parent": "minecraft:block/tnt",
    "overrides": [
        {
            "predicate": {"custom_model_data": 1},
            "model": "siegecannon:item/cannon_tnt"
        },
        {
            "predicate": {"custom_model_data": 2},
            "model": "siegecannon:item/cannon_tnt"
        },
        {
            "predicate": {"custom_model_data": 100},
            "model": "siegecannon:item/cannon_tnt"
        },
        {
            "predicate": {"custom_model_data": 1001},
            "model": "siegecannon:item/cannon_tnt"
        },
        {
            "predicate": {"custom_model_data": 7001},
            "model": "siegecannon:item/cannon_tnt"
        }
    ]
}

dst_tnt_json = os.path.join(minecraft_model_dir, "tnt.json")
with open(dst_tnt_json, "w", encoding="utf-8") as f:
    json.dump(tnt_override_model, f, indent=2)
print(f"Written: {dst_tnt_json}")

# Also create assets/siegecannon/models/item/cannon.json and assets/minecraft/models/item/cannon_tnt.json as aliases
with open("tmp_rp/assets/siegecannon/models/item/cannon.json", "w", encoding="utf-8") as f:
    f.write(json_str)
with open("tmp_rp/assets/minecraft/models/item/cannon_tnt.json", "w", encoding="utf-8") as f:
    f.write(json_str)

# 2. Package Resource Packs
print("=== 2. Packaging Resource Packs ===")
zip_targets = [
    'public/TownyArchitecture.zip',
    'dist/TownyArchitecture.zip',
    'public/TownyArchitecture-Modern-RP.zip',
    'dist/TownyArchitecture-Modern-RP.zip',
    'public/TownyArchitecture-RP.zip',
    'dist/TownyArchitecture-RP.zip'
]

for target in zip_targets:
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in sorted(os.walk("tmp_rp")):
            for file in sorted(files):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, "tmp_rp").replace('\\', '/')
                zf.write(full_path, rel_path)
    print(f"Packaged: {target} ({os.path.getsize(target)} bytes)")

# Recreate SiegeCannon-3D-Model-RP.zip
with zipfile.ZipFile("public/SiegeCannon-3D-Model-RP.zip", "w", zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in sorted(os.walk("tmp_rp")):
        for file in sorted(files):
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, "tmp_rp").replace('\\', '/')
            zf.write(full_path, rel_path)
shutil.copy2("public/SiegeCannon-3D-Model-RP.zip", "dist/SiegeCannon-3D-Model-RP.zip")

# 3. Update resourcePackBase64.ts
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

# 4. Refresh bundles
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

print(f"All done! Resource Pack SHA-1: {sha1}")
