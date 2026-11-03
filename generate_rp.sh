#!/bin/bash
mkdir -p tmp_rp/assets/minecraft/font
mkdir -p tmp_rp/assets/townyarchitecture/textures/gui

# mcmeta
cat << 'JSON' > tmp_rp/pack.mcmeta
{
    "pack": {
        "pack_format": 15,
        "description": "TownyArchitecture Modern GUI"
    }
}
JSON

# default.json
cat << 'JSON' > tmp_rp/assets/minecraft/font/default.json
{
    "providers": [
        {
            "type": "space",
            "advances": {
                "\uE000": -8,
                "\uE002": -256
            }
        },
        {
            "type": "bitmap",
            "file": "townyarchitecture:gui/menu.png",
            "ascent": -12,
            "height": 256,
            "chars": ["\uE001"]
        }
    ]
}
JSON

cp menu.png tmp_rp/assets/townyarchitecture/textures/gui/menu.png

cd tmp_rp
zip -r ../public/TownyArchitecture-Modern-RP.zip *
cd ..
rm -rf tmp_rp menu.png
