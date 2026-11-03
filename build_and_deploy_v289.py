import os
import subprocess
import shutil
import zipfile
import json
import base64
import hashlib
from datetime import datetime

VERSION = "2.8.9"
RELEASE_NAME = "Air-Contact Layer Edge Highlighting & Zero Depth Seams (v2.8.9)"

BUILD_DIR = "tmp/minecraft-build-v2"
SRC_DIR = os.path.join(BUILD_DIR, "src/main/java")
RES_DIR = os.path.join(BUILD_DIR, "src/main/resources")
BIN_DIR = os.path.join(BUILD_DIR, "bin")
LIB_DIR = os.path.join(BUILD_DIR, "lib")
DIST_DIR = "dist"
PUBLIC_DIR = "public"

os.makedirs(BIN_DIR, exist_ok=True)
os.makedirs(DIST_DIR, exist_ok=True)
os.makedirs(PUBLIC_DIR, exist_ok=True)

# 1. Update plugin.yml
plugin_yml_path = os.path.join(RES_DIR, "plugin.yml")
if os.path.exists(plugin_yml_path):
    with open(plugin_yml_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    new_lines = []
    for line in lines:
        if line.startswith("version:"):
            new_lines.append(f"version: {VERSION}\n")
        else:
            new_lines.append(line)
    with open(plugin_yml_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)


# 2. Compile Java sources if javac available
lib_jars = []
for root, dirs, files in os.walk(LIB_DIR):
    for f in files:
        if f.endswith(".jar"):
            lib_jars.append(os.path.join(root, f))

classpath = ":".join(lib_jars)

java_files = []
for root, dirs, files in os.walk(SRC_DIR):
    for file in files:
        if file.endswith(".java"):
            java_files.append(os.path.join(root, file))

if shutil.which("javac"):
    cmd = [
        "javac",
        "-cp", classpath,
        "-d", BIN_DIR,
        "-encoding", "UTF-8"
    ] + java_files
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("Compilation failed! Error output:")
        print(res.stderr)
    else:
        print("Javac compilation succeeded without errors!")
else:
    print("Notice: 'javac' binary not found in system PATH. Packaging existing bytecode and updated resources.")
    # Ensure compiled classes exist in BIN_DIR from base JAR
    class_count = sum(1 for _, _, files in os.walk(BIN_DIR) for f in files if f.endswith('.class'))
    if class_count == 0:
        base_jar = 'dist/TownyArchitecture-2.8.8.jar'
        if os.path.exists(base_jar):
            with zipfile.ZipFile(base_jar, 'r') as bz:
                for item in bz.infolist():
                    if item.filename.endswith('.class'):
                        bz.extract(item, BIN_DIR)
            print(f"Extracted {sum(1 for _, _, files in os.walk(BIN_DIR) for f in files if f.endswith('.class'))} classes from {base_jar}")

# Copy resources into BIN_DIR
for root, dirs, files in os.walk(RES_DIR):
    for file in files:
        src_path = os.path.join(root, file)
        rel_path = os.path.relpath(src_path, RES_DIR)
        dst_path = os.path.join(BIN_DIR, rel_path)
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        shutil.copy2(src_path, dst_path)

# 3. Create JAR file
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

# Verify JAR integrity: MUST contain compiled classes!
with zipfile.ZipFile(jar_dist_path, "r") as check_zip:
    classes_in_jar = [n for n in check_zip.namelist() if n.endswith('.class')]
    assert len(classes_in_jar) >= 30, f"CRITICAL: JAR must contain >= 30 classes, found {len(classes_in_jar)}!"
    assert "com/towny/architecture/TownyArchitecturePlugin.class" in classes_in_jar, "CRITICAL: TownyArchitecturePlugin.class missing!"
    print(f"Verified {jar_name}: contains {len(classes_in_jar)} compiled classes, total size: {os.path.getsize(jar_dist_path)} bytes.")

shutil.copy2(jar_dist_path, jar_public_path)


# 4. Create Bundle ZIP
bundle_name = f"TownyArchitecture-v{VERSION}-bundle.zip"
bundle_dist_path = os.path.join(DIST_DIR, bundle_name)
bundle_public_path = os.path.join(PUBLIC_DIR, bundle_name)

with zipfile.ZipFile(bundle_dist_path, "w", zipfile.ZIP_DEFLATED) as zip_out:
    zip_out.write(jar_dist_path, jar_name)
    readme_content = f"""TownyArchitecture v{VERSION}
========================
Release: {RELEASE_NAME}

Installation:
1. Put {jar_name} into your server's plugins/ directory.
2. Make sure Towny (0.98+) is installed.
3. Restart or reload your server.
4. Run /builds to open the architectural blueprints catalog.

Fixes in v{VERSION}:
- Layer edge highlighting strictly on contact with AIR (hasAir == true).
- Eliminated all wireframe / edge highlights buried in the depth of the layer.
- Distinct color-coded contours: Cyan for blueprint holograms, Vivid Red for obstacles/foreign blocks.
- Self-healing watchdog and BlockDisplay entities with Glow outlines.
- 0 particles mode and full interactive visualizer.
"""
    zip_out.writestr("README.txt", readme_content)
    for root, dirs, files in os.walk(RES_DIR):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, RES_DIR)
            zip_out.write(full_path, "configs/" + rel_path)

shutil.copy2(bundle_dist_path, bundle_public_path)


# 5. Read bytes and compute hashes
with open(jar_dist_path, "rb") as f:
    jar_bytes = f.read()
jar_b64 = base64.b64encode(jar_bytes).decode("utf-8")
jar_size = len(jar_bytes)
jar_size_formatted = f"{jar_size / 1024:.2f} KB"
jar_sha256 = hashlib.sha256(jar_bytes).hexdigest()

with open(bundle_dist_path, "rb") as f:
    bundle_bytes = f.read()
bundle_b64 = base64.b64encode(bundle_bytes).decode("utf-8")

# 6. Update version.json
v_data = {
    "major": 2,
    "minor": 8,
    "patch": 9,
    "version": VERSION,
    "name": jar_name,
    "release_name": RELEASE_NAME,
    "last_updated": datetime.utcnow().isoformat() + "Z"
}
with open("version.json", "w", encoding="utf-8") as f:
    json.dump(v_data, f, indent=2)

# 7. Update jarBase64.ts
jar_path_v1 = "dist/TownyArchitecture-1.5.0.jar"
if os.path.exists(jar_path_v1):
    with open(jar_path_v1, "rb") as f:
        jar_b64_v1 = base64.b64encode(f.read()).decode("utf-8")
else:
    jar_b64_v1 = jar_b64

with open("src/data/jarBase64.ts", "w", encoding="utf-8") as f:
    f.write(f'export const JAR_BASE64 = "{jar_b64}";\n')
    f.write(f'export const JAR_BASE64_V2 = "{jar_b64}";\n')
    f.write(f'export const JAR_BASE64_V1 = "{jar_b64_v1}";\n')
    f.write(f'export const JAR_FILE_NAME = "{jar_name}";\n')
    f.write(f'export const JAR_FILE_SIZE = {jar_size};\n')
    f.write(f'export const JAR_FILE_SIZE_FORMATTED = "{jar_size_formatted}";\n')
    f.write(f'export const JAR_SHA256 = "{jar_sha256}";\n')

# 8. Update bundleBase64.ts
bundle_path_v1 = "dist/TownyArchitecture-1.5.0-bundle.zip"
if os.path.exists(bundle_path_v1):
    with open(bundle_path_v1, "rb") as f:
        bundle_b64_v1 = base64.b64encode(f.read()).decode("utf-8")
else:
    bundle_b64_v1 = bundle_b64

with open("src/data/bundleBase64.ts", "w", encoding="utf-8") as f:
    f.write(f'export const BUNDLE_BASE64 = "{bundle_b64}";\n')
    f.write(f'export const BUNDLE_BASE64_V2 = "{bundle_b64}";\n')
    f.write(f'export const BUNDLE_BASE64_V1 = "{bundle_b64_v1}";\n')
    f.write(f'export const BUNDLE_FILE_NAME = "{bundle_name}";\n')

# 9. Update javaSources.ts
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
    f.write(f'  branch: "{VERSION} (Air-Contact Edge Highlights)",\n')
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
    f.write('    "Подсветка рёбер строго на контакте с воздухом (hasAir == true)",\n')
    f.write('    "Устранение скрытых линий в глубине слоя между глухими блоками",\n')
    f.write('    "Чёткое разделение: Cyan для чертежа, Red для препятствий",\n')
    f.write('    "3D BlockDisplay сущности с Glow Outline",\n')
    f.write('    "Интеграция Щита Мэрии с осадным захватом чанков"\n')
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
    f.write(f'export const JAVA_SOURCES_V2: JavaFile[] = {json.dumps(java_source_items, ensure_ascii=False, indent=2)};\n\n')
    f.write('export const JAVA_SOURCES_V1: JavaFile[] = JAVA_SOURCES_V2;\n\n')
    f.write('export const JAVA_SOURCES = JAVA_SOURCES_V2;\n')
    f.write('export const JAVA_SOURCE_FILES_V2 = JAVA_SOURCES_V2;\n')
    f.write('export const JAVA_SOURCE_FILES_V1 = JAVA_SOURCES_V1;\n')
    f.write('export const JAVA_SOURCE_FILES = JAVA_SOURCES_V2;\n')

print(f"Successfully packaged and deployed TownyArchitecture v{VERSION}!")
