import zipfile
import json
import os

os.makedirs('tmp_rp/assets/minecraft/font', exist_ok=True)
os.makedirs('tmp_rp/assets/townyarchitecture/textures/gui', exist_ok=True)

# pack.mcmeta
mcmeta = {
    "pack": {
        "pack_format": 15,
        "description": "TownyArchitecture Menu Template"
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

with open('tmp_rp/README.txt', 'w', encoding='utf-8') as f:
    f.write("Поместите вашу текстуру меню 256x256 в assets/townyarchitecture/textures/gui/menu.png.\nЗатем активируйте ресурспак в игре и укажите gui.title: '\uE001' в config.yml.")

with zipfile.ZipFile('public/TownyArchitecture-RP-Template.zip', 'w') as zf:
    for root, dirs, files in os.walk('tmp_rp'):
        for file in files:
            zf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), 'tmp_rp'))

print("Template RP created.")
