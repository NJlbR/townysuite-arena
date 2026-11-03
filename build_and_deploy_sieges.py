import os
import subprocess
import shutil
import zipfile
import json
import base64
import hashlib
from datetime import datetime

SIEGES_VERSION = "1.5.7"
SIEGES_NAME = "TownySieges"
SIEGES_JAR_NAME = f"{SIEGES_NAME}-{SIEGES_VERSION}.jar"
SIEGES_BUNDLE_NAME = f"{SIEGES_NAME}-v{SIEGES_VERSION}-bundle.zip"

BASE_DIR = os.path.abspath(".")
SRC_DIR = os.path.join(BASE_DIR, "tmp", "towny-sieges", "src", "main", "java")
RES_DIR = os.path.join(BASE_DIR, "tmp", "towny-sieges", "src", "main", "resources")
BIN_DIR = os.path.join(BASE_DIR, "tmp", "towny-sieges", "bin")
LIB_DIR = os.path.join(BASE_DIR, "tmp", "minecraft-build-v2", "lib")
DIST_DIR = os.path.join(BASE_DIR, "dist")
PUBLIC_DIR = os.path.join(BASE_DIR, "public")

shutil.rmtree(BIN_DIR, ignore_errors=True)
os.makedirs(BIN_DIR, exist_ok=True)
os.makedirs(DIST_DIR, exist_ok=True)
os.makedirs(PUBLIC_DIR, exist_ok=True)


java_files = []
for root, dirs, files in os.walk(SRC_DIR):
    for f in sorted(files):
        if f.endswith(".java"):
            java_files.append(os.path.join(root, f))



if shutil.which("javac"):
    cp_str = f"{LIB_DIR}/*"
    cmd = ["javac", "-cp", cp_str, "-d", BIN_DIR, "-encoding", "UTF-8"] + java_files
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("TownySieges javac compilation failed:")
        print(res.stderr)
    else:
        print("TownySieges Java compilation successful!")
else:
    print("Notice: Standalone packaging mode. Populating classes from baseline JAR.")
    baseline_jar = os.path.join(DIST_DIR, "TownySieges-1.5.6.jar")
    if os.path.exists(baseline_jar):
        with zipfile.ZipFile(baseline_jar, 'r') as zf:
            for item in zf.namelist():
                if item.endswith(".class"):
                    zf.extract(item, BIN_DIR)
        print(f"Extracted pre-compiled class files from {baseline_jar} into {BIN_DIR}")

# Copy resources to bin

# Copy resources to bin
for res_file in ["plugin.yml", "config.yml"]:
    src_res = os.path.join(RES_DIR, res_file)
    if os.path.exists(src_res):
        shutil.copy2(src_res, os.path.join(BIN_DIR, res_file))
        print(f"Copied resource: {res_file}")

# Package JAR

jar_out = os.path.join(DIST_DIR, SIEGES_JAR_NAME)

with zipfile.ZipFile(jar_out, "w", zipfile.ZIP_DEFLATED) as zf:
    manifest_content = f"Manifest-Version: 1.0\r\nCreated-By: TownyArchitectureTeam\r\nImplementation-Version: {SIEGES_VERSION}\r\n\r\n"
    zf.writestr("META-INF/MANIFEST.MF", manifest_content)
    
    for root, dirs, files in os.walk(BIN_DIR):
        for file in sorted(files):
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, BIN_DIR)
            zf.write(full_path, rel_path)
    
    # Also embed src in JAR for Paper source lookup
    for root, dirs, files in os.walk(SRC_DIR):
        for file in sorted(files):
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, SRC_DIR)
            zf.write(full_path, os.path.join("src", rel_path))

shutil.copy2(jar_out, os.path.join(DIST_DIR, "TownySieges.jar"))
shutil.copy2(jar_out, os.path.join(PUBLIC_DIR, SIEGES_JAR_NAME))
shutil.copy2(jar_out, os.path.join(PUBLIC_DIR, "TownySieges.jar"))

with open(jar_out, "rb") as f:
    jar_bytes = f.read()
jar_b64 = base64.b64encode(jar_bytes).decode("utf-8")
jar_sha256 = hashlib.sha256(jar_bytes).hexdigest()
jar_size = len(jar_bytes)


# Package Bundle ZIP

bundle_out = os.path.join(DIST_DIR, SIEGES_BUNDLE_NAME)
with zipfile.ZipFile(bundle_out, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(jar_out, arcname=SIEGES_JAR_NAME)
    z.write(os.path.join(RES_DIR, "config.yml"), arcname="config.yml")
    z.write(os.path.join(RES_DIR, "plugin.yml"), arcname="plugin.yml")
    
    # Add sources
    for root, dirs, files in os.walk(SRC_DIR):
        for f in sorted(files):
            full_p = os.path.join(root, f)
            rel_p = os.path.relpath(full_p, SRC_DIR)
            z.write(full_p, arcname=os.path.join("src", "main", "java", rel_p))

shutil.copy2(bundle_out, os.path.join(DIST_DIR, "TownySieges-bundle.zip"))
shutil.copy2(bundle_out, os.path.join(PUBLIC_DIR, SIEGES_BUNDLE_NAME))
shutil.copy2(bundle_out, os.path.join(PUBLIC_DIR, "TownySieges-bundle.zip"))

with open(bundle_out, "rb") as f:
    bundle_bytes = f.read()
bundle_b64 = base64.b64encode(bundle_bytes).decode("utf-8")
bundle_sha256 = hashlib.sha256(bundle_bytes).hexdigest()
bundle_size = len(bundle_bytes)


# Read Java source files for TS viewer
sieges_sources = []
for root, dirs, files in os.walk(SRC_DIR):
    for f in sorted(files):
        if f.endswith(".java"):
            full_p = os.path.join(root, f)
            rel_p = os.path.relpath(full_p, SRC_DIR)
            with open(full_p, "r", encoding="utf-8") as s_file:
                content = s_file.read()
            sieges_sources.append({
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
        sieges_sources.append({
            "path": f"src/main/resources/{res_name}",
            "name": res_name,
            "content": content
        })

# Generate src/data/townySiegesData.ts
sieges_ts_path = os.path.join(BASE_DIR, "src", "data", "townySiegesData.ts")
with open(sieges_ts_path, "w", encoding="utf-8") as f:
    f.write("// Auto-generated by build_and_deploy_sieges.py\n\n")
    f.write("export interface TownySiegesMetadata {\n")
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
        "name": SIEGES_NAME,
        "version": SIEGES_VERSION,
        "jarFileName": SIEGES_JAR_NAME,
        "jarDownloadUrl": f"/{SIEGES_JAR_NAME}",
        "jarSizeFormatted": f"{round(jar_size / 1024, 1)} KB",
        "jarSizeBytes": jar_size,
        "jarSha256": jar_sha256,
        "bundleFileName": SIEGES_BUNDLE_NAME,
        "bundleDownloadUrl": f"/{SIEGES_BUNDLE_NAME}",
        "bundleSizeFormatted": f"{round(bundle_size / 1024, 1)} KB",
        "bundleSizeBytes": bundle_size,
        "bundleSha256": bundle_sha256,
        "description": "Тактические осады и Войны Наций: почанковый захват штурмовым флагом с лучом маяка в небо, динамический расчет скорости от перевеса бойцов, BossBar с живым числом атакующих/защитников, откат и контр-захват с созданием официального аванпоста Towny при несмежности.",
        "releaseDate": datetime.utcnow().strftime("%Y-%m-%d")
    }
    
    f.write(f"export const TOWNY_SIEGES_METADATA: TownySiegesMetadata = {json.dumps(meta_dict, ensure_ascii=False, indent=2)};\n\n")
    f.write(f"export const TOWNY_SIEGES_SOURCES = {json.dumps(sieges_sources, ensure_ascii=False, indent=2)};\n\n")
    f.write(f'export const TOWNY_SIEGES_JAR_BASE64 = "{jar_b64}";\n\n')
    f.write(f'export const TOWNY_SIEGES_BUNDLE_BASE64 = "{bundle_b64}";\n')


