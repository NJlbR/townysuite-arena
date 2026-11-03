import zipfile
import os
import json

os.makedirs('tmp_rp/assets/minecraft/font', exist_ok=True)
os.makedirs('tmp_rp/assets/minecraft/models/item', exist_ok=True)
os.makedirs('tmp_rp/assets/townyarchitecture/models/item', exist_ok=True)
os.makedirs('tmp_rp/assets/townyarchitecture/textures/gui', exist_ok=True)
os.makedirs('tmp_rp/assets/townyarchitecture/textures/item', exist_ok=True)

mcmeta = {
    'pack': {
        'pack_format': 34,
        'supported_formats': [15, 34],
        'description': 'TownyArchitecture Modern GUI'
    }
}
with open('tmp_rp/pack.mcmeta', 'w') as f:
    json.dump(mcmeta, f, indent=4)

font_json = {
    'providers': [
        {
            'type': 'space',
            'advances': {
                '\uE000': -8,
                '\uE002': -256
            }
        },
        {
            'type': 'bitmap',
            'file': 'townyarchitecture:gui/menu.png',
            'ascent': -12,
            'height': 256,
            'chars': ['\uE001']
        }
    ]
}
with open('tmp_rp/assets/minecraft/font/default.json', 'w') as f:
    json.dump(font_json, f, indent=4)

paper_model = {
    'parent': 'item/generated',
    'textures': {
        'layer0': 'item/paper'
    },
    'overrides': [
        { 'predicate': { 'custom_model_data': 1 }, 'model': 'townyarchitecture:item/invisible' }
    ]
}
with open('tmp_rp/assets/minecraft/models/item/paper.json', 'w') as f:
    json.dump(paper_model, f, indent=4)

invisible_model = {
    'parent': 'item/generated',
    'textures': {
        'layer0': 'townyarchitecture:item/invisible'
    }
}
with open('tmp_rp/assets/townyarchitecture/models/item/invisible.json', 'w') as f:
    json.dump(invisible_model, f, indent=4)

os.system('cp menu.png tmp_rp/assets/townyarchitecture/textures/gui/menu.png')
os.system('cp invisible.png tmp_rp/assets/townyarchitecture/textures/item/invisible.png')

with zipfile.ZipFile('public/TownyArchitecture-Modern-RP.zip', 'w', zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk('tmp_rp'):
        for file in files:
            zf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), 'tmp_rp'))

print('ZIP created successfully')
