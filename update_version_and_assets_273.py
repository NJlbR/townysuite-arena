import os
import json
import base64
import hashlib
from datetime import datetime

# 1. Update version.json
with open("version.json", "r", encoding="utf-8") as f:
    v_data = json.load(f)

v_data["major"] = 2
v_data["minor"] = 7
v_data["patch"] = 3
v_data["version"] = "2.7.3"
v_data["release_name"] = "Full 3D Facet Hologram Outlines (All 6 Faces & 12 Edges)"
v_data["last_updated"] = datetime.utcnow().isoformat() + "Z"

with open("version.json", "w", encoding="utf-8") as f:
    json.dump(v_data, f, indent=2)

print("Updated version.json to 2.7.3")

# 2. Update jarBase64.ts
jar_path_v2 = "dist/TownyArchitecture-2.7.3.jar"
with open(jar_path_v2, "rb") as f:
    jar_bytes_v2 = f.read()

jar_b64_v2 = base64.b64encode(jar_bytes_v2).decode("utf-8")
jar_size = len(jar_bytes_v2)
jar_size_kb = f"{jar_size / 1024:.2f} KB"
jar_sha256 = hashlib.sha256(jar_bytes_v2).hexdigest()

jar_path_v1 = "dist/TownyArchitecture-1.5.0.jar"
if os.path.exists(jar_path_v1):
    with open(jar_path_v1, "rb") as f:
        jar_b64_v1 = base64.b64encode(f.read()).decode("utf-8")
else:
    jar_b64_v1 = jar_b64_v2

with open("src/data/jarBase64.ts", "w", encoding="utf-8") as f:
    f.write(f'export const JAR_BASE64 = "{jar_b64_v2}";\n')
    f.write(f'export const JAR_BASE64_V2 = "{jar_b64_v2}";\n')
    f.write(f'export const JAR_BASE64_V1 = "{jar_b64_v1}";\n')
    f.write(f'export const JAR_FILE_NAME = "TownyArchitecture-2.7.3.jar";\n')
    f.write(f'export const JAR_FILE_SIZE = {jar_size};\n')
    f.write(f'export const JAR_FILE_SIZE_FORMATTED = "{jar_size_kb}";\n')
    f.write(f'export const JAR_SHA256 = "{jar_sha256}";\n')

print(f"Updated jarBase64.ts ({jar_size_kb}, SHA256: {jar_sha256[:8]}...)")

# 3. Update bundleBase64.ts
bundle_path_v2 = "dist/TownyArchitecture-v2.7.3-bundle.zip"
with open(bundle_path_v2, "rb") as f:
    bundle_bytes_v2 = f.read()

bundle_b64_v2 = base64.b64encode(bundle_bytes_v2).decode("utf-8")

bundle_path_v1 = "dist/TownyArchitecture-v1.5.0-bundle.zip"
if os.path.exists(bundle_path_v1):
    with open(bundle_path_v1, "rb") as f:
        bundle_b64_v1 = base64.b64encode(f.read()).decode("utf-8")
else:
    bundle_b64_v1 = bundle_b64_v2

with open("src/data/bundleBase64.ts", "w", encoding="utf-8") as f:
    f.write(f'export const BUNDLE_BASE64 = "{bundle_b64_v2}";\n')
    f.write(f'export const BUNDLE_BASE64_V2 = "{bundle_b64_v2}";\n')
    f.write(f'export const BUNDLE_BASE64_V1 = "{bundle_b64_v1}";\n')
    f.write(f'export const BUNDLE_FILE_NAME = "TownyArchitecture-v2.7.3-bundle.zip";\n')

print("Updated bundleBase64.ts")

# 4. Scan java files for javaSources.ts
JAVA_ROOT = "tmp/minecraft-build-v2/src/main/java"
RES_ROOT = "tmp/minecraft-build-v2/src/main/resources"

java_files = []
for root, dirs, files in sorted(os.walk(JAVA_ROOT)):
    for file in sorted(files):
        if file.endswith(".java"):
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, JAVA_ROOT).replace("\\", "/")
            category = "Manager" if "manager" in rel_path else "Model" if "model" in rel_path else "Command" if "command" in rel_path else "GUI" if "gui" in rel_path else "Listener" if "listener" in rel_path else "Core"
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
            java_files.append({
                "name": file,
                "path": "src/main/java/" + rel_path,
                "category": category,
                "content": content
            })

for root, dirs, files in sorted(os.walk(RES_ROOT)):
    for file in sorted(files):
        if file.endswith(".yml") or file.endswith(".json") or file.endswith(".txt"):
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, RES_ROOT).replace("\\", "/")
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
            java_files.append({
                "name": file,
                "path": "src/main/resources/" + rel_path,
                "category": "Resource",
                "content": content
            })

ts_content = f"""// Auto-generated Java Source Code Catalog for v1 and v2 branches
export interface JavaFile {{
  name: string;
  path: string;
  category: string;
  content: string;
}}

export type JavaSourceItem = JavaFile;

export const PLUGIN_METADATA_V2 = {{
  name: 'TownyArchitecture',
  version: '2.7.3',
  branch: '2.7.3 (Full 3D Facet Hologram Outlines & Zero Particle Clutter)',
  jarFileName: 'TownyArchitecture-2.7.3.jar',
  bundleFileName: 'TownyArchitecture-v2.7.3-bundle.zip',
  jarDownloadUrl: '/TownyArchitecture-2.7.3.jar',
  bundleDownloadUrl: '/TownyArchitecture-v2.7.3-bundle.zip',
  fileSizeBytes: {jar_size},
  fileSizeFormatted: '{jar_size_kb}',
  sha256: '{jar_sha256}',
  supportedVersions: [
    'Paper 1.20 - 1.20.4',
    'Paper 1.20.6',
    'Paper 1.21+',
    'Purpur 1.20+',
    'Spigot 1.20+'
  ],
  softDependencies: [
    'Towny (0.98+)',
    'SiegeWar (опционально)'
  ],
  features: [
    '3D-Голограммы чертежей Litematica с полной 3D-обводкой всех граней (0.92 Scale)',
    'Послойное возведение (Layer-by-Layer) с раздельной синей и красной подсветкой',
    'Защита фасадов от подземных бункеров (Правило 50% открытости стен)',
    'Осадный динамит (Siege TNT) против обсидиановых укреплений',
    'Автономная система уровней Архитектора с защитой от абуза (High-Water Mark)',
    'Интерактивное меню чертежей /builds и команды /build facade'
  ]
}};

export const PLUGIN_METADATA_V1 = PLUGIN_METADATA_V2;

export const PLUGIN_METADATA = PLUGIN_METADATA_V2;

export const JAVA_SOURCES_V2: JavaFile[] = {json.dumps(java_files, ensure_ascii=False, indent=2)};

export const JAVA_SOURCES_V1: JavaFile[] = JAVA_SOURCES_V2;

export const JAVA_SOURCES: JavaFile[] = JAVA_SOURCES_V2;

export const JAVA_SOURCE_FILES_V2: JavaFile[] = JAVA_SOURCES_V2;

export const JAVA_SOURCE_FILES_V1: JavaFile[] = JAVA_SOURCES_V1;

export const JAVA_SOURCE_FILES: JavaFile[] = JAVA_SOURCES;
"""

with open("src/data/javaSources.ts", "w", encoding="utf-8") as f:
    f.write(ts_content)

print(f"Updated javaSources.ts with {len(java_files)} files.")
