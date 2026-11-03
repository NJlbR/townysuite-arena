import os
import shutil
import zipfile
import hashlib
import base64
import json

base_dir = 'tmp_rp'
target_model_dir = os.path.join(base_dir, 'assets', 'siegecannon', 'models', 'item')
os.makedirs(target_model_dir, exist_ok=True)

# Copy the cannon model to the requested path: assets/siegecannon/models/item/cannon_tnt.json
src_model = 'public/models/cannon_1x1.json'
dst_model = os.path.join(target_model_dir, 'cannon_tnt.json')

shutil.copy2(src_model, dst_model)
print(f"Copied {src_model} to {dst_model}")

# Package resource packs
zip_targets = [
    'public/TownyArchitecture.zip',
    'dist/TownyArchitecture.zip',
    'public/TownyArchitecture-Modern-RP.zip',
    'dist/TownyArchitecture-Modern-RP.zip',
    'public/TownyArchitecture-RP.zip',
    'dist/TownyArchitecture-RP.zip'
]

os.makedirs('dist', exist_ok=True)
os.makedirs('public', exist_ok=True)

for target in zip_targets:
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in sorted(os.walk(base_dir)):
            for file in sorted(files):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, base_dir)
                rel_path = rel_path.replace('\\', '/')
                zf.write(full_path, rel_path)
    print(f"Created {target} ({os.path.getsize(target)} bytes)")

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

print(f"Success! Updated resourcePackBase64.ts (Size: {len(zip_bytes)} bytes, SHA-1: {sha1})")
