import os
import subprocess
import shutil
import zipfile
import json
import base64
import hashlib
from datetime import datetime

UNBLOCKER_VERSION = "1.1.2"
UNBLOCKER_NAME = "TownyExplosionUnblocker"
UNBLOCKER_JAR_NAME = f"{UNBLOCKER_NAME}-{UNBLOCKER_VERSION}.jar"
UNBLOCKER_BUNDLE_NAME = f"{UNBLOCKER_NAME}-v{UNBLOCKER_VERSION}-bundle.zip"

BASE_DIR = os.path.abspath(".")
SRC_DIR = os.path.join(BASE_DIR, "tmp", "towny-explosion-unblocker", "src", "main", "java")
RES_DIR = os.path.join(BASE_DIR, "tmp", "towny-explosion-unblocker", "src", "main", "resources")
BIN_DIR = os.path.join(BASE_DIR, "tmp", "towny-explosion-unblocker", "bin")
LIB_DIR = os.path.join(BASE_DIR, "tmp", "minecraft-build-v2", "lib")
SIEGES_BIN = os.path.join(BASE_DIR, "tmp", "towny-sieges", "bin")
DIST_DIR = os.path.join(BASE_DIR, "dist")
PUBLIC_DIR = os.path.join(BASE_DIR, "public")

shutil.rmtree(BIN_DIR, ignore_errors=True)
os.makedirs(BIN_DIR, exist_ok=True)
os.makedirs(DIST_DIR, exist_ok=True)
os.makedirs(PUBLIC_DIR, exist_ok=True)

print("=== 1. Compiling TownyExplosionUnblocker with javac ===")
java_files = []
for root, dirs, files in os.walk(SRC_DIR):
    for f in sorted(files):
        if f.endswith(".java"):
            java_files.append(os.path.join(root, f))

print(f"Found {len(java_files)} Java files to compile in TownyExplosionUnblocker.")

if shutil.which("javac"):
    cp_str = f"{LIB_DIR}/*:{SIEGES_BIN}"
    cmd = ["javac", "-cp", cp_str, "-d", BIN_DIR, "-encoding", "UTF-8"] + java_files
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("TownyExplosionUnblocker javac compilation failed:")
        print(res.stderr)
    else:
        print("TownyExplosionUnblocker Java compilation successful!")
else:
    print("Notice: 'javac' binary not found in system PATH. Packaging source files and bundle zip directly.")

# Copy resources to bin
for res_file in ["plugin.yml", "config.yml"]:
    src_res = os.path.join(RES_DIR, res_file)
    if os.path.exists(src_res):
        shutil.copy2(src_res, os.path.join(BIN_DIR, res_file))
        print(f"Copied resource: {res_file}")

# Package JAR using python zipfile
print("=== 2. Creating Unblocker Jar ===")
jar_out = os.path.join(DIST_DIR, UNBLOCKER_JAR_NAME)

with zipfile.ZipFile(jar_out, "w", zipfile.ZIP_DEFLATED) as zf:
    manifest_content = "Manifest-Version: 1.0\r\nCreated-By: TownyArchitectureTeam\r\n\r\n"
    zf.writestr("META-INF/MANIFEST.MF", manifest_content)
    
    for root, dirs, files in os.walk(BIN_DIR):
        for file in sorted(files):
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, BIN_DIR)
            zf.write(full_path, rel_path)

shutil.copy2(jar_out, os.path.join(DIST_DIR, "TownyExplosionUnblocker.jar"))
shutil.copy2(jar_out, os.path.join(PUBLIC_DIR, UNBLOCKER_JAR_NAME))
shutil.copy2(jar_out, os.path.join(PUBLIC_DIR, "TownyExplosionUnblocker.jar"))

with open(jar_out, "rb") as f:
    jar_bytes = f.read()
jar_b64 = base64.b64encode(jar_bytes).decode("utf-8")
jar_sha256 = hashlib.sha256(jar_bytes).hexdigest()
jar_size = len(jar_bytes)
print(f"Unblocker JAR created: {jar_out} ({jar_size} bytes, SHA256: {jar_sha256[:12]}...)")

# Package Bundle ZIP
print("=== 3. Creating Unblocker Bundle ZIP ===")
bundle_out = os.path.join(DIST_DIR, UNBLOCKER_BUNDLE_NAME)
with zipfile.ZipFile(bundle_out, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(jar_out, arcname=UNBLOCKER_JAR_NAME)
    z.write(os.path.join(RES_DIR, "config.yml"), arcname="config.yml")
    z.write(os.path.join(RES_DIR, "plugin.yml"), arcname="plugin.yml")
    
    # Add sources
    for root, dirs, files in os.walk(SRC_DIR):
        for f in sorted(files):
            full_p = os.path.join(root, f)
            rel_p = os.path.relpath(full_p, SRC_DIR)
            z.write(full_p, arcname=os.path.join("src", "main", "java", rel_p))

shutil.copy2(bundle_out, os.path.join(DIST_DIR, "TownyExplosionUnblocker-bundle.zip"))
shutil.copy2(bundle_out, os.path.join(PUBLIC_DIR, UNBLOCKER_BUNDLE_NAME))
shutil.copy2(bundle_out, os.path.join(PUBLIC_DIR, "TownyExplosionUnblocker-bundle.zip"))

with open(bundle_out, "rb") as f:
    bundle_bytes = f.read()
bundle_b64 = base64.b64encode(bundle_bytes).decode("utf-8")
bundle_sha256 = hashlib.sha256(bundle_bytes).hexdigest()
bundle_size = len(bundle_bytes)

print(f"Unblocker Bundle ZIP created: {bundle_out} ({bundle_size} bytes)")

# Read Java source files for TS viewer
unblocker_sources = []
for root, dirs, files in os.walk(SRC_DIR):
    for f in sorted(files):
        if f.endswith(".java"):
            full_p = os.path.join(root, f)
            rel_p = os.path.relpath(full_p, SRC_DIR)
            with open(full_p, "r", encoding="utf-8") as s_file:
                content = s_file.read()
            unblocker_sources.append({
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
        unblocker_sources.append({
            "path": f"src/main/resources/{res_name}",
            "name": res_name,
            "content": content
        })

# Generate src/data/unblockerData.ts
unblocker_ts_path = os.path.join(BASE_DIR, "src", "data", "unblockerData.ts")
with open(unblocker_ts_path, "w", encoding="utf-8") as f:
    f.write("// Auto-generated by build_and_deploy_unblocker.py\n\n")
    f.write("export interface UnblockerMetadata {\n")
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
        "name": UNBLOCKER_NAME,
        "version": UNBLOCKER_VERSION,
        "jarFileName": UNBLOCKER_JAR_NAME,
        "jarDownloadUrl": f"/{UNBLOCKER_JAR_NAME}",
        "jarSizeFormatted": f"{round(jar_size / 1024, 1)} KB",
        "jarSizeBytes": jar_size,
        "jarSha256": jar_sha256,
        "bundleFileName": UNBLOCKER_BUNDLE_NAME,
        "bundleDownloadUrl": f"/{UNBLOCKER_BUNDLE_NAME}",
        "bundleSizeFormatted": f"{round(bundle_size / 1024, 1)} KB",
        "bundleSizeBytes": bundle_size,
        "bundleSha256": bundle_sha256,
        "description": "Независимый плагин-разблокировщик взрывов в городах Towny исключительно для снарядов пушек SiegeCannon во время 2-часовой активной осады TownySieges.",
        "releaseDate": datetime.utcnow().strftime("%Y-%m-%d")
    }
    
    f.write(f"export const UNBLOCKER_METADATA: UnblockerMetadata = {json.dumps(meta_dict, ensure_ascii=False, indent=2)};\n\n")
    f.write(f"export const UNBLOCKER_SOURCES = {json.dumps(unblocker_sources, ensure_ascii=False, indent=2)};\n\n")
    f.write(f'export const UNBLOCKER_JAR_BASE64 = "{jar_b64}";\n\n')
    f.write(f'export const UNBLOCKER_BUNDLE_BASE64 = "{bundle_b64}";\n')

print(f"Generated {unblocker_ts_path} successfully!")
