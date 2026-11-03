import os
import subprocess
import shutil
import zipfile
import json
import base64
import hashlib
from datetime import datetime

RESPAWN_VERSION = "1.1.2"
RESPAWN_NAME = "TownyRespawn"
RESPAWN_JAR_NAME = f"{RESPAWN_NAME}-{RESPAWN_VERSION}.jar"
RESPAWN_BUNDLE_NAME = f"{RESPAWN_NAME}-v{RESPAWN_VERSION}-bundle.zip"

BASE_DIR = os.path.abspath(".")
SRC_DIR = os.path.join(BASE_DIR, "tmp", "towny-respawn", "src", "main", "java")
RES_DIR = os.path.join(BASE_DIR, "tmp", "towny-respawn", "src", "main", "resources")
BIN_DIR = os.path.join(BASE_DIR, "tmp", "towny-respawn", "bin")
LIB_DIR = os.path.join(BASE_DIR, "tmp", "minecraft-build-v2", "lib")
DIST_DIR = os.path.join(BASE_DIR, "dist")
PUBLIC_DIR = os.path.join(BASE_DIR, "public")

os.makedirs(BIN_DIR, exist_ok=True)
os.makedirs(DIST_DIR, exist_ok=True)
os.makedirs(PUBLIC_DIR, exist_ok=True)

# Clean bin
shutil.rmtree(BIN_DIR, ignore_errors=True)
os.makedirs(BIN_DIR, exist_ok=True)

print("=== 1. Compiling TownyRespawn with javac ===")
java_files = []
for root, dirs, files in os.walk(SRC_DIR):
    for f in sorted(files):
        if f.endswith(".java"):
            java_files.append(os.path.join(root, f))

print(f"Found {len(java_files)} Java files to compile in TownyRespawn.")

# Build classpath: libs + TownySieges jar if present
lib_jars = [os.path.join(LIB_DIR, f) for f in os.listdir(LIB_DIR) if f.endswith(".jar")]
sieges_jar = os.path.join(PUBLIC_DIR, "TownySieges-1.0.0.jar")
if os.path.exists(sieges_jar):
    lib_jars.append(sieges_jar)

cp_str = f"{LIB_DIR}/*:{PUBLIC_DIR}/*"
if shutil.which("javac"):
    cmd = ["javac", "-cp", cp_str, "-d", BIN_DIR, "-encoding", "UTF-8"] + java_files
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("TownyRespawn javac compilation failed:")
        print(res.stderr)
    else:
        print("TownyRespawn Java compilation successful!")
else:
    print("Notice: 'javac' binary not found in system PATH. Packaging source files and bundle zip directly.")

# Copy compiled class files if available
if os.path.exists('tmp/respawn-classes/com'):
    shutil.copytree('tmp/respawn-classes/com', os.path.join(BIN_DIR, 'com'), dirs_exist_ok=True)
    print('Included compiled .class files from tmp/respawn-classes')
elif os.path.exists('tmp/respawn-repackage/com'):
    shutil.copytree('tmp/respawn-repackage/com', os.path.join(BIN_DIR, 'com'), dirs_exist_ok=True)
    print('Included compiled .class files from tmp/respawn-repackage')

# Copy resources to bin
for res_file in ["plugin.yml", "config.yml"]:
    src_res = os.path.join(RES_DIR, res_file)
    if os.path.exists(src_res):
        shutil.copy2(src_res, os.path.join(BIN_DIR, res_file))
        print(f"Copied resource: {res_file}")

# Package JAR
print("=== 2. Creating TownyRespawn Jar ===")
jar_out = os.path.join(DIST_DIR, RESPAWN_JAR_NAME)

with zipfile.ZipFile(jar_out, "w", zipfile.ZIP_DEFLATED) as zf:
    manifest_content = "Manifest-Version: 1.0\r\nCreated-By: TownyArchitectureTeam\r\n\r\n"
    zf.writestr("META-INF/MANIFEST.MF", manifest_content)
    
    for root, dirs, files in os.walk(BIN_DIR):
        for file in sorted(files):
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, BIN_DIR)
            zf.write(full_path, rel_path)

shutil.copy2(jar_out, os.path.join(DIST_DIR, "TownyRespawn.jar"))
shutil.copy2(jar_out, os.path.join(DIST_DIR, "TownyRespawn-1.0.0.jar"))
shutil.copy2(jar_out, os.path.join(PUBLIC_DIR, RESPAWN_JAR_NAME))
shutil.copy2(jar_out, os.path.join(PUBLIC_DIR, "TownyRespawn.jar"))
shutil.copy2(jar_out, os.path.join(PUBLIC_DIR, "TownyRespawn-1.0.0.jar"))

with open(jar_out, "rb") as f:
    jar_bytes = f.read()
jar_b64 = base64.b64encode(jar_bytes).decode("utf-8")
jar_sha256 = hashlib.sha256(jar_bytes).hexdigest()
jar_size = len(jar_bytes)
print(f"TownyRespawn JAR created: {jar_out} ({jar_size} bytes, SHA256: {jar_sha256[:12]}...)")

# Package Bundle ZIP
print("=== 3. Creating TownyRespawn Bundle ZIP ===")
bundle_out = os.path.join(DIST_DIR, RESPAWN_BUNDLE_NAME)
with zipfile.ZipFile(bundle_out, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(jar_out, arcname=RESPAWN_JAR_NAME)
    z.write(os.path.join(RES_DIR, "config.yml"), arcname="config.yml")
    z.write(os.path.join(RES_DIR, "plugin.yml"), arcname="plugin.yml")
    
    # Add sources
    for root, dirs, files in os.walk(SRC_DIR):
        for f in sorted(files):
            full_p = os.path.join(root, f)
            rel_p = os.path.relpath(full_p, SRC_DIR)
            z.write(full_p, arcname=os.path.join("src", "main", "java", rel_p))

shutil.copy2(bundle_out, os.path.join(DIST_DIR, "TownyRespawn-bundle.zip"))
shutil.copy2(bundle_out, os.path.join(PUBLIC_DIR, RESPAWN_BUNDLE_NAME))
shutil.copy2(bundle_out, os.path.join(PUBLIC_DIR, "TownyRespawn-bundle.zip"))

with open(bundle_out, "rb") as f:
    bundle_bytes = f.read()
bundle_b64 = base64.b64encode(bundle_bytes).decode("utf-8")
bundle_sha256 = hashlib.sha256(bundle_bytes).hexdigest()
bundle_size = len(bundle_bytes)
print(f"TownyRespawn Bundle ZIP created: {bundle_out} ({bundle_size} bytes)")

# Read Java source files for TS viewer
respawn_sources = []
for root, dirs, files in os.walk(SRC_DIR):
    for f in sorted(files):
        if f.endswith(".java"):
            full_p = os.path.join(root, f)
            rel_p = os.path.relpath(full_p, SRC_DIR)
            with open(full_p, "r", encoding="utf-8") as s_file:
                content = s_file.read()
            respawn_sources.append({
                "path": f"src/main/java/{rel_p}",
                "name": f,
                "content": content
            })

# Read resources
for res_name in ["plugin.yml", "config.yml"]:
    res_path = os.path.join(RES_DIR, res_name)
    if os.path.exists(res_path):
        with open(res_path, "r", encoding="utf-8") as r_file:
            content = r_file.read()
        respawn_sources.append({
            "path": f"src/main/resources/{res_name}",
            "name": res_name,
            "content": content
        })

# Generate src/data/townyRespawnData.ts
respawn_ts_path = os.path.join(BASE_DIR, "src", "data", "townyRespawnData.ts")
with open(respawn_ts_path, "w", encoding="utf-8") as f:
    f.write("// Auto-generated by build_and_deploy_respawn.py\n\n")
    f.write("export interface TownyRespawnMetadata {\n")
    f.write("  name: string;\n")
    f.write("  version: string;\n")
    f.write("  jarFileName: string;\n")
    f.write("  jarDownloadUrl: string;\n")
    f.write("  jarSizeFormatted: string;\n")
    f.write("  jarSizeBytes: number;\n")
    f.write("  jarSha256: string;\n")
    f.write("  bundleFileName: string;\n")
    f.write("  bundleDownloadUrl: string;\n")
    f.write("  bundleSizeFormatted: string;\n")
    f.write("  bundleSizeBytes: number;\n")
    f.write("  bundleSha256: string;\n")
    f.write("  description: string;\n")
    f.write("  releaseDate: string;\n")
    f.write("}\n\n")
    
    meta_dict = {
        "name": RESPAWN_NAME,
        "version": RESPAWN_VERSION,
        "jarFileName": RESPAWN_JAR_NAME,
        "jarDownloadUrl": f"/{RESPAWN_JAR_NAME}",
        "jarSizeFormatted": f"{round(jar_size / 1024, 1)} KB",
        "jarSizeBytes": jar_size,
        "jarSha256": jar_sha256,
        "bundleFileName": RESPAWN_BUNDLE_NAME,
        "bundleDownloadUrl": f"/{RESPAWN_BUNDLE_NAME}",
        "bundleSizeFormatted": f"{round(bundle_size / 1024, 1)} KB",
        "bundleSizeBytes": bundle_size,
        "bundleSha256": bundle_sha256,
        "description": "Система нескольких кроватей, переименование своих кроватей (ПКМ в меню /respawn или командой), выбор точки возрождения при смерти, спавны городов и наций Towny, чистый респавн без слепоты и замедления.",
        "releaseDate": datetime.utcnow().strftime("%Y-%m-%d")
    }
    
    f.write(f"export const TOWNY_RESPAWN_METADATA: TownyRespawnMetadata = {json.dumps(meta_dict, ensure_ascii=False, indent=2)};\n\n")
    f.write(f"export const TOWNY_RESPAWN_SOURCES = {json.dumps(respawn_sources, ensure_ascii=False, indent=2)};\n\n")
    f.write(f'export const TOWNY_RESPAWN_JAR_BASE64 = "{jar_b64}";\n\n')
    f.write(f'export const TOWNY_RESPAWN_BUNDLE_BASE64 = "{bundle_b64}";\n')

print(f"Generated {respawn_ts_path} successfully!")
