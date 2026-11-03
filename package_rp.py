import zipfile
import os
import hashlib
import base64

base_dir = 'tmp_rp'
zip_targets = [
    'public/TownyArchitecture.zip',
    'public/TownyArchitecture-Modern-RP.zip',
    'public/TownyArchitecture-RP.zip'
]

for target in zip_targets:
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in sorted(os.walk(base_dir)):
            for file in sorted(files):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, base_dir)
                rel_path = rel_path.replace('\\', '/')
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

print(f"Success! ZIP size: {len(zip_bytes)} bytes")
print(f"SHA-1: {sha1}")
print(f"SHA-256: {sha256}")
