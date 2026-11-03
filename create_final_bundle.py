import zipfile
import os
import shutil
import base64

def create_final_bundle():
    jars = [
        ('public/TownyArchitecture-2.8.7.jar', 'TownyArchitecture-2.8.7.jar'),
        ('public/TownySieges-1.5.7.jar', 'TownySieges-1.5.7.jar'),
        ('public/TownyRespawn-1.1.2.jar', 'TownyRespawn-1.1.2.jar'),
        ('public/TownyExplosionUnblocker-1.1.2.jar', 'TownyExplosionUnblocker-1.1.2.jar')
    ]
    
    bundle_name = 'public/TownySuite-v2.8.7-All-Plugins.zip'
    
    with zipfile.ZipFile(bundle_name, 'w', zipfile.ZIP_DEFLATED) as zf:
        for src, name in jars:
            if os.path.exists(src):
                zf.write(src, name)
                print(f"Added {src} to bundle.")
            else:
                print(f"Error: {src} not found!")
    
    shutil.copy2(bundle_name, 'public/Towny-Suite-All-Plugins.zip')
    shutil.copy2(bundle_name, 'public/TownySuite-All-Plugins.zip')
    shutil.copy2(bundle_name, 'public/All-Plugins-Bundle.zip')
    
    with open(bundle_name, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode('utf-8')
    
    with open('src/data/suiteZipBase64.ts', 'w', encoding='utf-8') as sf:
        sf.write(f'export const SUITE_ALL_PLUGINS_ZIP_BASE64 = "{b64}";\n')
    
    print(f"Final bundle created at {bundle_name} and updated src/data/suiteZipBase64.ts!")

if __name__ == "__main__":
    create_final_bundle()
