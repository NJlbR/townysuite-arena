import zipfile
import json
import base64
import os
from PIL import Image, ImageDraw, ImageFont

os.makedirs('tmp_rp/assets/minecraft/font', exist_ok=True)
os.makedirs('tmp_rp/assets/townyarchitecture/textures/gui', exist_ok=True)

# pack.mcmeta
mcmeta = {
    "pack": {
        "pack_format": 15,
        "description": "TownyArchitecture Resource Pack"
    }
}
with open('tmp_rp/pack.mcmeta', 'w') as f:
    json.dump(mcmeta, f, indent=4)

# default.json
font_json = {
    "providers": [
        {
            "type": "bitmap",
            "file": "townyarchitecture:gui/menu.png",
            "ascent": 7,
            "height": 256,
            "chars": [
                "\uE001"
            ]
        }
    ]
}
with open('tmp_rp/assets/minecraft/font/default.json', 'w') as f:
    json.dump(font_json, f, indent=4)

# menu.png
img = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
# Draw a basic nice GUI background
d.rectangle([0, 0, 255, 255], fill=(30, 30, 30, 255), outline=(200, 150, 50, 255), width=2)
# Draw slots (54 slots)
for row in range(6):
    for col in range(9):
        x = 8 + col * 18
        y = 18 + row * 18
        d.rectangle([x, y, x+16, y+16], fill=(50, 50, 50, 255), outline=(10, 10, 10, 255))
d.text((8, 5), "TownyArchitecture Menu", fill=(255, 200, 0, 255))

img.save('tmp_rp/assets/townyarchitecture/textures/gui/menu.png')

with zipfile.ZipFile('public/TownyArchitecture-ResourcePack.zip', 'w') as zf:
    for root, dirs, files in os.walk('tmp_rp'):
        for file in files:
            zf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), 'tmp_rp'))

print("Resource pack generated.")
