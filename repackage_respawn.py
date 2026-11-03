import zipfile
import os
import shutil

def repackage_respawn():
    base_jar = 'tmp/respawn-extract/TownyRespawn-1.0.0.jar'
    extract_dir = 'tmp/respawn-repackage'
    target_jar = 'public/TownyRespawn-1.1.2.jar'
    
    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir)
    os.makedirs(extract_dir)
    
    with zipfile.ZipFile(base_jar, 'r') as zf:
        zf.extractall(extract_dir)
    
    # Write explicit, clean plugin.yml with hard depend on Towny
    plugin_yml_path = os.path.join(extract_dir, 'plugin.yml')
    plugin_yml_content = """name: TownyRespawn
version: 1.1.2
main: com.towny.respawn.TownyRespawnPlugin
api-version: 1.20
description: Interactive In-Game BlueMap-like Map (/map), Player Graphics Quality Settings, Multi-Bed System & Tactical Death Respawn Selector
author: TownyArchitectureTeam
depend: [Towny]
softdepend: [TownySieges, TownyArchitecture, TownyExplosionUnblocker]
commands:
  map:
    description: Открывает интерактивную внутриигровую карту мира с городами и осадами
    aliases: [townymap, bluemapgui, tmap]
    permission: townyrespawn.use
  respawn:
    description: Открывает меню выбора точек возрождения и списка кроватей
    aliases: [spawns, spawnselect, beds, mybeds]
    permission: townyrespawn.use
  townyrespawn:
    description: Главная администраторская команда плагина TownyRespawn
    aliases: [trespawn]
    permission: townyrespawn.admin
permissions:
  townyrespawn.use:
    description: Доступ к просмотру карты /map и выбору респавна
    default: true
  townyrespawn.beds.multiple:
    description: Право на использование нескольких кроватей
    default: true
  townyrespawn.admin:
    description: Администраторские права на перезагрузку и управление
    default: op
"""
    with open(plugin_yml_path, 'w', encoding='utf-8') as f:
        f.write(plugin_yml_content)
    
    # Repackage
    targets = [
        'public/TownyRespawn-1.1.2.jar',
        'public/TownyRespawn.jar',
        'public/TownyRespawn-v1.1.2.jar'
    ]
    
    for t in targets:
        if os.path.exists(t):
            os.remove(t)
            
    with zipfile.ZipFile(target_jar, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, extract_dir)
                zf.write(abs_path, rel_path)
    
    for t in targets[1:]:
        shutil.copy2(target_jar, t)
    
    # Create bundle zip for TownyRespawn
    bundle_zip = 'public/TownyRespawn-v1.1.2-bundle.zip'
    with zipfile.ZipFile(bundle_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(target_jar, 'TownyRespawn-1.1.2.jar')
        zf.write(os.path.join(extract_dir, 'config.yml'), 'config.yml')
        zf.write(os.path.join(extract_dir, 'plugin.yml'), 'plugin.yml')
    
    shutil.copy2(bundle_zip, 'public/TownyRespawn-bundle.zip')
    
    print(f"Repackaged TownyRespawn with explicit plugin.yml successfully.")

if __name__ == "__main__":
    repackage_respawn()
