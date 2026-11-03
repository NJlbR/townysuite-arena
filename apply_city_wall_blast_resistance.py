import os
import json
import zipfile
import base64
import hashlib
import shutil

print("=== Updating TownyArchitecture with 2x Blast Resistance for City Wall Blueprint Blocks ===")

# 1. Update buildings.yml
buildings_yml_path = "tmp/minecraft-build-v2/src/main/resources/buildings.yml"
bin_buildings_yml_path = "tmp/minecraft-build-v2/bin/buildings.yml"

with open(buildings_yml_path, "r", encoding="utf-8") as f:
    b_content = f.read()

# Update description for city_wall
old_desc = 'description: "Фортификационный вал (2x1). Массивная модульная каменная стена с угловыми стыковочными башнями и зубцами. Сдерживает снаряды и осады за счет толщины кладки и своевременного ремонта защитниками. Стены стыкуются в единую цепь."'
new_desc = 'description: "Фортификационный вал (2x1). Массивная модульная каменная стена с угловыми стыковочными башнями и зубцами. Блоки стены, установленные строго на свои места по чертежу, обладают двойной взрывоустойчивостью (2x) от оригинальной взрывоустойчивости блока. Стены стыкуются в единую цепь."'

if old_desc in b_content:
    b_content = b_content.replace(old_desc, new_desc)

with open(buildings_yml_path, "w", encoding="utf-8") as f:
    f.write(b_content)

if os.path.exists(bin_buildings_yml_path):
    with open(bin_buildings_yml_path, "w", encoding="utf-8") as f:
        f.write(b_content)

print("Updated buildings.yml resources")

# 2. Update defaultBuildings.ts
with open("src/data/defaultBuildings.ts", "r", encoding="utf-8") as f:
    db_content = f.read()

target_wall_desc = "description: 'Фортификационный вал (2x1 чанка). Модульная стена с угловыми стыковочными башнями и зубцами. Каждая построенная стена дает +100 ед. к Щиту Мэрии вашего города в военное время! Стены стыкуются в единую цепь.'"
new_wall_desc = "description: 'Фортификационный вал (2x1 чанка). Модульная стена с угловыми стыковочными башнями и зубцами. Блоки стены, установленные строго на свои места по чертежу, обладают двойной взрывоустойчивостью (2x) от оригинальной взрывоустойчивости блока. Каждая построенная стена дает +100 ед. к Щиту Мэрии вашего города в военное время!'"

if target_wall_desc in db_content:
    db_content = db_content.replace(target_wall_desc, new_wall_desc)

# Also ensure buff list has 2x blast resistance
old_buffs = """    buffs: [
      {
        id: 'wall_shield_boost',
        type: 'town_shield',
        value: 100,
        unit: '+100 HP Щита',
        descriptionRu: 'Увеличивает прочность Щита Мэрии на +100 единиц здоровья во время войны',
      },
    ],"""

new_buffs = """    buffs: [
      {
        id: 'wall_shield_boost',
        type: 'town_shield',
        value: 100,
        unit: '+100 HP Щита',
        descriptionRu: 'Увеличивает прочность Щита Мэрии на +100 единиц здоровья во время войны',
      },
      {
        id: 'wall_blast_resistance',
        type: 'fortification',
        value: 2,
        unit: '2x Blast Res',
        descriptionRu: 'Двойная взрывоустойчивость (2x) для всех блоков, стоящих на своих местах по чертежу',
      },
    ],"""

if old_buffs in db_content:
    db_content = db_content.replace(old_buffs, new_buffs)

with open("src/data/defaultBuildings.ts", "w", encoding="utf-8") as f:
    f.write(db_content)

print("Updated defaultBuildings.ts")

# 3. Update ChangelogSection.tsx
with open("src/components/ChangelogSection.tsx", "r", encoding="utf-8") as f:
    cl_content = f.read()

new_log_entry = """  {
    version: 'v2.8.3',
    date: '5 октября 2026',
    title: 'Патч v2.8.3: Двойная взрывоустойчивость (2x) для чертежа «Городская Стена»',
    badge: 'Текущая',
    changes: [
      { type: 'feature', text: 'Двойная взрывоустойчивость по чертежу: блоки постройки «Городская Стена» получают 2x взрывоустойчивость от оригинальной прочности блока (Stone Bricks = 12.0, Cobblestone = 12.0, Iron Bars = 12.0, Lantern = 7.0).' },
      { type: 'feature', text: 'Строгая проверка расположения: двойная защита применяется исключительно к блокам, стоящим на своих точных координатах по 3D-чертежу (isProperCityWallBlock). Сторонние или произвольно установленные блоки имеют стандартную взрывоустойчивость.' },
      { type: 'improvement', text: 'Двухэтапное поглощение осадных взрывов: укрепленные блоки стены поглощают первый взрыв с искрами и звуком наковальни, требуя повторного концентрированного попадания для пробития кладки.' }
    ]
  },
"""

# Replace badge: 'Текущая' in previous top version
cl_content = cl_content.replace("    badge: 'Текущая',", "")
marker = "const VERSIONS: VersionLog[] = [\n"
if marker in cl_content and "v2.8.3" not in cl_content:
    cl_content = cl_content.replace(marker, marker + new_log_entry)

with open("src/components/ChangelogSection.tsx", "w", encoding="utf-8") as f:
    f.write(cl_content)

print("Updated ChangelogSection.tsx")

# 4. Packaging and regenerating JavaSources.ts, jar, bundle
VERSION = "2.8.3"
BUILD_DIR = "tmp/minecraft-build-v2"
SRC_DIR = os.path.join(BUILD_DIR, "src/main/java")
RES_DIR = os.path.join(BUILD_DIR, "src/main/resources")
BIN_DIR = os.path.join(BUILD_DIR, "bin")
DIST_DIR = "dist"
PUBLIC_DIR = "public"

os.makedirs(BIN_DIR, exist_ok=True)
os.makedirs(DIST_DIR, exist_ok=True)
os.makedirs(PUBLIC_DIR, exist_ok=True)

# Copy all resources into BIN_DIR
for root, dirs, files in os.walk(RES_DIR):
    for file in files:
        src_path = os.path.join(root, file)
        rel_path = os.path.relpath(src_path, RES_DIR)
        dst_path = os.path.join(BIN_DIR, rel_path)
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        shutil.copy2(src_path, dst_path)

jar_name = f"TownyArchitecture-{VERSION}.jar"
jar_dist_path = os.path.join(DIST_DIR, jar_name)
jar_public_path = os.path.join(PUBLIC_DIR, jar_name)

manifest_path = os.path.join(BUILD_DIR, "MANIFEST.MF")
with open(manifest_path, "w", encoding="utf-8") as f:
    f.write("Manifest-Version: 1.0\nCreated-By: TownyArchitecture Build Tool\n\n")

with zipfile.ZipFile(jar_dist_path, "w", zipfile.ZIP_DEFLATED) as zip_out:
    zip_out.write(manifest_path, "META-INF/MANIFEST.MF")
    for root, dirs, files in os.walk(BIN_DIR):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, BIN_DIR)
            zip_out.write(full_path, rel_path)

shutil.copy2(jar_dist_path, jar_public_path)

# Also update generic TownyArchitecture.jar
shutil.copy2(jar_dist_path, os.path.join(PUBLIC_DIR, "TownyArchitecture.jar"))

jar_size = os.path.getsize(jar_dist_path)
jar_size_formatted = f"{jar_size / 1024:.2f} KB"

with open(jar_dist_path, "rb") as f:
    jar_bytes = f.read()
    jar_sha256 = hashlib.sha256(jar_bytes).hexdigest()
    jar_b64 = base64.b64encode(jar_bytes).decode("utf-8")

# Update jarBase64.ts
with open("src/data/jarBase64.ts", "w", encoding="utf-8") as f:
    f.write(f'export const JAR_BASE64 = "{jar_b64}";\n')
    f.write(f'export const JAR_BASE64_V2 = "{jar_b64}";\n')
    f.write(f'export const JAR_BASE64_V1 = "{jar_b64}";\n')
    f.write(f'export const JAR_FILE_NAME = "{jar_name}";\n')

# Create Bundle ZIP
bundle_name = f"TownyArchitecture-v{VERSION}-bundle.zip"
bundle_dist_path = os.path.join(DIST_DIR, bundle_name)
bundle_public_path = os.path.join(PUBLIC_DIR, bundle_name)

with zipfile.ZipFile(bundle_dist_path, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(jar_dist_path, arcname=jar_name)
    if os.path.exists("public/TownyArchitecture.zip"):
        z.write("public/TownyArchitecture.zip", arcname="TownyArchitecture-ResourcePack.zip")
    for root, dirs, files in os.walk(RES_DIR):
        for file in files:
            full = os.path.join(root, file)
            rel = os.path.relpath(full, RES_DIR)
            z.write(full, arcname=f"config/{rel}")

shutil.copy2(bundle_dist_path, bundle_public_path)
shutil.copy2(bundle_dist_path, os.path.join(PUBLIC_DIR, "TownyArchitecture-bundle.zip"))

with open(bundle_dist_path, "rb") as f:
    bundle_bytes = f.read()
    bundle_b64 = base64.b64encode(bundle_bytes).decode("utf-8")

with open("src/data/bundleBase64.ts", "w", encoding="utf-8") as f:
    f.write(f'export const BUNDLE_BASE64 = "{bundle_b64}";\n')
    f.write(f'export const BUNDLE_BASE64_V2 = "{bundle_b64}";\n')
    f.write(f'export const BUNDLE_BASE64_V1 = "{bundle_b64}";\n')
    f.write(f'export const BUNDLE_FILE_NAME = "{bundle_name}";\n')

# Update javaSources.ts
java_source_items = []
for root, dirs, files in sorted(os.walk(SRC_DIR)):
    for file in sorted(files):
        if file.endswith(".java"):
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, SRC_DIR).replace("\\", "/")
            category = "Manager" if "manager" in rel_path else "Model" if "model" in rel_path else "Command" if "command" in rel_path else "GUI" if "gui" in rel_path else "Listener" if "listener" in rel_path else "Core"
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
            java_source_items.append({
                "name": file,
                "path": "src/main/java/" + rel_path,
                "category": category,
                "content": content
            })

for root, dirs, files in sorted(os.walk(RES_DIR)):
    for file in sorted(files):
        if file.endswith(".yml") or file.endswith(".json") or file.endswith(".txt"):
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, RES_DIR).replace("\\", "/")
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
            java_source_items.append({
                "name": file,
                "path": "src/main/resources/" + rel_path,
                "category": "Resource",
                "content": content
            })

with open("src/data/javaSources.ts", "w", encoding="utf-8") as f:
    f.write('// Auto-generated Java Source Code Catalog for v1 and v2 branches\n')
    f.write('export interface JavaFile {\n')
    f.write('  name: string;\n')
    f.write('  path: string;\n')
    f.write('  category: string;\n')
    f.write('  content: string;\n')
    f.write('}\n\n')
    f.write('export type JavaSourceItem = JavaFile;\n\n')
    f.write('export const PLUGIN_METADATA_V2 = {\n')
    f.write(f'  name: "TownyArchitecture",\n')
    f.write(f'  version: "{VERSION}",\n')
    f.write(f'  branch: "{VERSION} (City Wall 2x Blast Resistance & Blueprint Precision)",\n')
    f.write(f'  jarFileName: "{jar_name}",\n')
    f.write(f'  bundleFileName: "{bundle_name}",\n')
    f.write(f'  jarDownloadUrl: "/{jar_name}",\n')
    f.write(f'  bundleDownloadUrl: "/{bundle_name}",\n')
    f.write(f'  fileSizeBytes: {jar_size},\n')
    f.write(f'  fileSizeFormatted: "{jar_size_formatted}",\n')
    f.write(f'  sha256: "{jar_sha256}",\n')
    f.write('  supportedVersions: [\n')
    f.write('    "Paper 1.20 - 1.20.4",\n')
    f.write('    "Paper 1.20.6",\n')
    f.write('    "Paper 1.21+",\n')
    f.write('    "Purpur 1.20+",\n')
    f.write('    "Spigot 1.20+"\n')
    f.write('  ],\n')
    f.write('  softDependencies: [\n')
    f.write('    "Towny (0.98+)",\n')
    f.write('    "SiegeWar (опционально)"\n')
    f.write('  ],\n')
    f.write('  features: [\n')
    f.write('    "Двойная взрывоустойчивость (2x Blast Resistance) для блоков «Городская Стена», установленных по чертежу",\n')
    f.write('    "Строгая проверка чертежа: случайные блоки не получают двойную защиту",\n')
    f.write('    "Двухэтапное поглощение осадных взрывов с искрами и звуком наковальни",\n')
    f.write('    "3D-Голограммы чертежей с постоянной подсветкой по граням (Glow Outline)",\n')
    f.write('    "Послойное возведение (Layer-by-Layer) с сохранением голограмм до конца постройки",\n')
    f.write('    "Механика Щита Мэрии: +100 HP за каждую построенную стену в военное время",\n')
    f.write('    "Защита фасадов от подземных бункеров (Правило 50% открытости стен)",\n')
    f.write('    "Осадный динамит (Siege TNT) против обсидиановых укреплений",\n')
    f.write('    "Автономная система уровней Архитектора с защитой от абуза (High-Water Mark)"\n')
    f.write('  ]\n')
    f.write('};\n\n')
    f.write('export const PLUGIN_METADATA = PLUGIN_METADATA_V2;\n\n')
    f.write('export const PLUGIN_METADATA_V1 = {\n')
    f.write('  name: "TownyArchitecture",\n')
    f.write('  version: "1.5.0",\n')
    f.write('  branch: "1.5.0 (Legacy Mode)",\n')
    f.write('  jarFileName: "TownyArchitecture-1.5.0.jar",\n')
    f.write('  bundleFileName: "TownyArchitecture-v1.5.0-bundle.zip",\n')
    f.write('  jarDownloadUrl: "/TownyArchitecture-1.5.0.jar",\n')
    f.write('  bundleDownloadUrl: "/TownyArchitecture-v1.5.0-bundle.zip",\n')
    f.write('  fileSizeBytes: 86319,\n')
    f.write('  fileSizeFormatted: "84.30 KB",\n')
    f.write('  sha256: "legacy-v1-sha256",\n')
    f.write('  supportedVersions: ["Paper 1.20+"],\n')
    f.write('  softDependencies: ["Towny"],\n')
    f.write('  features: ["Классический режим"]\n')
    f.write('};\n\n')
    f.write('export const JAVA_FILES_V2: JavaFile[] = ' + json.dumps(java_source_items, ensure_ascii=False, indent=2) + ';\n\n')
    f.write('export const JAVA_FILES = JAVA_FILES_V2;\n\n')
    f.write('export const JAVA_FILES_V1: JavaFile[] = JAVA_FILES_V2;\n\n')
    f.write('export const JAVA_SOURCE_FILES_V2: JavaSourceItem[] = JAVA_FILES_V2;\n')
    f.write('export const JAVA_SOURCE_FILES_V1: JavaSourceItem[] = JAVA_FILES_V1;\n')
    f.write('export const JAVA_SOURCE_FILES: JavaSourceItem[] = JAVA_FILES_V2;\n')

print(f"Successfully generated javaSources.ts with {len(java_source_items)} items!")
