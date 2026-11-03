import json
import os
import zipfile
import hashlib
import base64


# 1. Create directory structure
base_dir = 'tmp_rp'
if os.path.exists(base_dir):
    import shutil
    shutil.rmtree(base_dir)

os.makedirs(f'{base_dir}/assets/minecraft/font', exist_ok=True)
os.makedirs(f'{base_dir}/assets/minecraft/models/item', exist_ok=True)
os.makedirs(f'{base_dir}/assets/townyarchitecture/models/item', exist_ok=True)
os.makedirs(f'{base_dir}/assets/townyarchitecture/textures/gui', exist_ok=True)
os.makedirs(f'{base_dir}/assets/townyarchitecture/textures/item', exist_ok=True)

# 2. Generate authentic Minecraft Container GUI menu.png
menu_png_path = f'{base_dir}/assets/townyarchitecture/textures/gui/menu.png'
import zlib
import struct

def build_menu_gui_png(path):
    w, h = 256, 256
    pixels = [[(0, 0, 0, 0) for _ in range(w)] for _ in range(h)]
    
    # Fill container panel: 176x222 (standard 6-row container GUI)
    cw, ch = 176, 222
    for y in range(ch):
        for x in range(cw):
            if x == 0 or y == 0 or x == cw-1 or y == ch-1:
                pixels[y][x] = (30, 32, 38, 255)
            elif x == 1 or y == 1:
                pixels[y][x] = (75, 80, 92, 255) # Top-left light border
            elif x == cw-2 or y == ch-2:
                pixels[y][x] = (20, 22, 26, 255) # Bottom-right dark shadow
            elif y < 16:
                pixels[y][x] = (42, 45, 54, 255) # Header bar
            else:
                pixels[y][x] = (48, 52, 62, 255) # Main body
                
    # Draw slots helper
    def draw_slot(sx, sy, is_blueprint=False):
        for dy in range(18):
            for dx in range(18):
                px, py = sx + dx, sy + dy
                if dx == 0 or dy == 0:
                    pixels[py][px] = (22, 24, 28, 255) # Inset top-left shadow
                elif dx == 17 or dy == 17:
                    pixels[py][px] = (70, 75, 86, 255) # Inset bottom-right highlight
                else:
                    if is_blueprint:
                        pixels[py][px] = (32, 44, 56, 255) # Blueprint grid cyan-dark
                    else:
                        pixels[py][px] = (34, 36, 42, 255) # Standard slot recess
                        
    # Draw 54 container slots (6 rows of 9)
    # Slots in rows 1, 2, 3 are blueprint slots (columns 1..7: slots 10..16, 19..25, 28..34)
    for r in range(6):
        for c in range(9):
            sx = 7 + c * 18
            sy = 17 + r * 18
            is_bp = (1 <= r <= 3) and (1 <= c <= 7)
            draw_slot(sx, sy, is_bp)
            
    # Draw player inventory at bottom (rows 0..2) and hotbar
    for r in range(3):
        for c in range(9):
            sx = 7 + c * 18
            sy = 139 + r * 18
            draw_slot(sx, sy, False)
    for c in range(9):
        sx = 7 + c * 18
        sy = 197
        draw_slot(sx, sy, False)
        
    # Gold corner ornaments on the container
    gold_dark = (160, 110, 25, 255)
    gold_bright = (235, 185, 50, 255)
    corners = [(2, 2), (cw-6, 2), (2, ch-6), (cw-6, ch-6)]
    for cx, cy in corners:
        for dy in range(4):
            for dx in range(4):
                col = gold_bright if (dx+dy)%2 == 0 else gold_dark
                pixels[cy+dy][cx+dx] = col

    # Encode PNG
    raw_data = bytearray()
    for y in range(h):
        raw_data.append(0) # filter None
        for x in range(w):
            r, g, b, a = pixels[y][x]
            raw_data.extend((r, g, b, a))
            
    compressed = zlib.compress(raw_data, 9)
    
    def make_chunk(chunk_type, data):
        c = chunk_type + data
        crc = zlib.crc32(c) & 0xffffffff
        return struct.pack('>I', len(data)) + c + struct.pack('>I', crc)
        
    ihdr_data = struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0)
    png_bytes = b'\x89PNG\r\n\x1a\n' + make_chunk(b'IHDR', ihdr_data) + make_chunk(b'IDAT', compressed) + make_chunk(b'IEND', b'')
    
    with open(path, 'wb') as f:
        f.write(png_bytes)
    print(f"Generated complete custom menu.png: {len(png_bytes)} bytes")

build_menu_gui_png(menu_png_path)
# Also copy to unpack cache so it stays synced
os.makedirs('tmp/rp_unpack/assets/townyarchitecture/textures/gui', exist_ok=True)
build_menu_gui_png('tmp/rp_unpack/assets/townyarchitecture/textures/gui/menu.png')

# 3. Create invisible 1x1 item texture (No Pillow)
inv_img_path = f'{base_dir}/assets/townyarchitecture/textures/item/invisible.png'
with open(inv_img_path, 'wb') as f:
    # Transparent 1x1 PNG
    f.write(base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="))

# 4. pack.mcmeta with full modern format compatibility
mcmeta = {
    "pack": {
        "pack_format": 34,
        "supported_formats": {
            "min_inclusive": 15,
            "max_inclusive": 48
        },
        "description": "TownyArchitecture Modern GUI Texture Pack"
    }
}
with open(f'{base_dir}/pack.mcmeta', 'w', encoding='utf-8') as f:
    json.dump(mcmeta, f, indent=4)

# 5. default.json font
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
with open(f'{base_dir}/assets/minecraft/font/default.json', 'w', encoding='utf-8') as f:
    json.dump(font_json, f, indent=4)

# 6. Models
paper_model = {
    "parent": "item/generated",
    "textures": {
        "layer0": "item/paper"
    },
    "overrides": [
        { "predicate": { "custom_model_data": 1 }, "model": "townyarchitecture:item/invisible" }
    ]
}
with open(f'{base_dir}/assets/minecraft/models/item/paper.json', 'w', encoding='utf-8') as f:
    json.dump(paper_model, f, indent=4)

invisible_model = {
    "parent": "item/generated",
    "textures": {
        "layer0": "townyarchitecture:item/invisible"
    }
}
with open(f'{base_dir}/assets/townyarchitecture/models/item/invisible.json', 'w', encoding='utf-8') as f:
    json.dump(invisible_model, f, indent=4)

# 7. Create ZIP files
zip_targets = [
    'public/TownyArchitecture.zip',
    'public/TownyArchitecture-Modern-RP.zip',
    'public/TownyArchitecture-RP.zip'
]

for target in zip_targets:
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, base_dir)
                # Normalize slashes for Windows/Minecraft
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

print(f"Resource Pack ZIP created! Size: {len(zip_bytes)} bytes")
print(f"SHA-1: {sha1}")
print(f"SHA-256: {sha256}")
