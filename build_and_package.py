import os
import sys
import json
import shutil
import hashlib
import subprocess
import base64
import re
from datetime import datetime

# 1. Load and manage version
version_file = "version.json"
if os.path.exists(version_file):
    with open(version_file, "r", encoding="utf-8") as f:
        v_data = json.load(f)
else:
    v_data = {
        "major": 2,
        "minor": 1,
        "patch": 0,
        "version": "2.1.0",
        "build": 1,
        "release_name": "Full-Sized RP & Precision Laser Alignment",
        "last_updated": datetime.utcnow().isoformat() + "Z"
    }

if not shutil.which("javac"):
    raise SystemExit("Java build aborted: javac is required; refusing to change release metadata or package a stale JAR")
if not shutil.which("node"):
    raise SystemExit("Java build aborted: node is required to synchronize the website source viewer")
subprocess.run(["node", "update_java_sources.js"], check=True)

ver_str = v_data.get("version", "2.1.0")
v_data["build"] = v_data.get("build", 0) + 1
v_data["last_updated"] = datetime.utcnow().isoformat() + "Z"

with open(version_file, "w", encoding="utf-8") as f:
    json.dump(v_data, f, indent=2)

print(f"=== Building TownyArchitecture v{ver_str} (Build #{v_data['build']}) ===")

# 2. Update plugin.yml with exact version
plugin_yml_path = "tmp/minecraft-build-v2/src/main/resources/plugin.yml"
if os.path.exists(plugin_yml_path):
    with open(plugin_yml_path, "r", encoding="utf-8") as f:
        p_yml = f.read()
    p_yml = re.sub(r'(?m)^version:\s*[^\n]+', f'version: {ver_str}', p_yml)
    with open(plugin_yml_path, "w", encoding="utf-8") as f:
        f.write(p_yml)
    print(f"Updated plugin.yml version to {ver_str}")

# 3. Compile Java sources
print("Compiling Java sources...")
bin_dir = "tmp/minecraft-build-v2/bin"
shutil.rmtree(bin_dir, ignore_errors=True)
os.makedirs(bin_dir, exist_ok=True)

javac_cmd = [
    "javac",
    "-cp", "tmp/minecraft-build-v2/lib/*:tmp/minecraft-build/lib/*:tmp/minecraft-build-v1/lib/*",
    "-d", bin_dir,
    "@v2_sources.txt"
]
if not shutil.which("javac"):
    raise SystemExit("Java build aborted: javac is required; refusing to package a stale JAR")
subprocess.run(javac_cmd, check=True)
print("Java compilation succeeded!")

# 4. Copy resources to bin
print("Copying resources to bin...")
res_dir = "tmp/minecraft-build-v2/src/main/resources"
for item in os.listdir(res_dir):
    s = os.path.join(res_dir, item)
    d = os.path.join(bin_dir, item)
    if os.path.isfile(s):
        shutil.copy2(s, d)

# 5. Package JAR
jar_file_name = f"TownyArchitecture-{ver_str}.jar"
jar_path = f"tmp/minecraft-build-v2/{jar_file_name}"
if os.path.exists(jar_path):
    os.remove(jar_path)

try:
    subprocess.run(["jar", "cvf", jar_file_name, "-C", "bin", "."], cwd="tmp/minecraft-build-v2", check=True)
    print(f"JAR created at {jar_path}")
except Exception as e:
    raise SystemExit(f"JAR packaging failed; refusing to publish stale artifacts: {e}")

# Calculate JAR hash and size
with open(jar_path, "rb") as f:
    jar_bytes = f.read()
    jar_sha256 = hashlib.sha256(jar_bytes).hexdigest()
    jar_size = len(jar_bytes)
    jar_size_kb = f"{jar_size / 1024:.2f} KB"

# Distribute JAR to targets
targets = [
    "tmp/minecraft-build-v2/TownyArchitecture.jar",
    f"tmp/minecraft-build-v2/target/{jar_file_name}",
    f"tmp/bundle-v2/{jar_file_name}",
    f"dist/{jar_file_name}",
    "dist/TownyArchitecture.jar",
    f"public/{jar_file_name}",
    f"public/TownyArchitecture-v{ver_str}.jar",
    "public/TownyArchitecture.jar"
]
for t in targets:
    os.makedirs(os.path.dirname(t), exist_ok=True)
    shutil.copy2(jar_path, t)
    print(f"Copied JAR to {t}")

# 6. Create Bundle ZIP
import zipfile
bundle_file_name = f"TownyArchitecture-v{ver_str}-bundle.zip"
bundle_zip = f"public/{bundle_file_name}"

with zipfile.ZipFile(bundle_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
    zf.write(jar_path, jar_file_name)
    zf.write("tmp/minecraft-build-v2/src/main/resources/config.yml", "config.yml")
    zf.write("tmp/minecraft-build-v2/src/main/resources/buildings.yml", "buildings.yml")
    zf.write("tmp/minecraft-build-v2/src/main/resources/plugin.yml", "plugin.yml")

shutil.copy2(bundle_zip, "public/TownyArchitecture-bundle.zip")
print(f"Bundle ZIP created at {bundle_zip}")

# 7. Update Base64 ts files
print("Updating Base64 files...")
jar_b64 = base64.b64encode(jar_bytes).decode('utf-8')
with open("src/data/jarBase64.ts", "r", encoding="utf-8") as f:
    jb_content = f.read()
jb_content = re.sub(r'export const JAR_BASE64_V2 = "[^"]*";', f'export const JAR_BASE64_V2 = "{jar_b64}";', jb_content)
jb_content = re.sub(r'export const JAR_BASE64 = "[^"]*";', f'export const JAR_BASE64 = "{jar_b64}";', jb_content)
with open("src/data/jarBase64.ts", "w", encoding="utf-8") as f:
    f.write(jb_content)

with open(bundle_zip, "rb") as f:
    bundle_bytes = f.read()
bundle_b64 = base64.b64encode(bundle_bytes).decode('utf-8')
with open("src/data/bundleBase64.ts", "r", encoding="utf-8") as f:
    bb_content = f.read()
bb_content = re.sub(r'export const BUNDLE_BASE64_V2 = "[^"]*";', f'export const BUNDLE_BASE64_V2 = "{bundle_b64}";', bb_content)
bb_content = re.sub(r'export const BUNDLE_BASE64 = "[^"]*";', f'export const BUNDLE_BASE64 = "{bundle_b64}";', bb_content)
with open("src/data/bundleBase64.ts", "w", encoding="utf-8") as f:
    f.write(bb_content)

# 8. Update V2 release metadata without touching V1 metadata or source display.
print("Updating PLUGIN_METADATA_V2 in javaSources.ts...")
with open("src/data/javaSources.ts", "r", encoding="utf-8") as f:
    js_content = f.read()

metadata_match = re.search(r'(export const PLUGIN_METADATA_V2 = \{)([\s\S]*?)(\n\};)', js_content)
if not metadata_match:
    raise SystemExit("PLUGIN_METADATA_V2 not found; refusing to publish mismatched metadata")
metadata = metadata_match.group(2)
for field, value in {
    "version": ver_str,
    "jarFileName": jar_file_name,
    "bundleFileName": bundle_file_name,
    "fileSizeFormatted": jar_size_kb,
    "sha256": jar_sha256,
    "builtAt": datetime.utcnow().strftime("%Y-%m-%d"),
}.items():
    metadata, count = re.subn(rf'({field}: ")[^"]*(")', lambda m: m.group(1) + value + m.group(2), metadata, count=1)
    if count != 1:
        raise SystemExit(f"Metadata field {field} not found; refusing to publish mismatched metadata")
js_content = js_content[:metadata_match.start(2)] + metadata + js_content[metadata_match.end(2):]
with open("src/data/javaSources.ts", "w", encoding="utf-8") as f:
    f.write(js_content)

# Keep the filename/checksum constants aligned with the encoded bytes.
with open("src/data/jarBase64.ts", "r", encoding="utf-8") as f:
    content = f.read()
content = re.sub(r'export const JAR_FILE_NAME = "[^"]*";', f'export const JAR_FILE_NAME = "{jar_file_name}";', content)
content = re.sub(r'export const JAR_FILE_SIZE = \d+;', f'export const JAR_FILE_SIZE = {jar_size};', content)
content = re.sub(r'export const JAR_FILE_SIZE_FORMATTED = "[^"]*";', f'export const JAR_FILE_SIZE_FORMATTED = "{jar_size_kb}";', content)
content = re.sub(r'export const JAR_SHA256 = "[^"]*";', f'export const JAR_SHA256 = "{jar_sha256}";', content)
with open("src/data/jarBase64.ts", "w", encoding="utf-8") as f:
    f.write(content)
with open("src/data/bundleBase64.ts", "r", encoding="utf-8") as f:
    content = f.read()
content = re.sub(r'export const BUNDLE_FILE_NAME = "[^"]*";', f'export const BUNDLE_FILE_NAME = "{bundle_file_name}";', content)
with open("src/data/bundleBase64.ts", "w", encoding="utf-8") as f:
    f.write(content)

print(f"Build completed successfully: TownyArchitecture v{ver_str} ({jar_size_kb}, SHA256: {jar_sha256[:16]}...)")
