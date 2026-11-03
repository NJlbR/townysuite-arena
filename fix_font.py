import json

font_json = {
    'providers': [
        {
            'type': 'space',
            'advances': {
                '\uE000': -8,
                '\uE002': -170
            }
        },
        {
            'type': 'bitmap',
            'file': 'townyarchitecture:gui/menu.png',
            'ascent': 5,
            'height': 256,
            'chars': ['\uE001']
        }
    ]
}
with open('tmp_rp/assets/minecraft/font/default.json', 'w') as f:
    json.dump(font_json, f, indent=4)
