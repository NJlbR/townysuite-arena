import os
import subprocess
import shutil
import zipfile
import base64
import hashlib

ARCH_VERSION = "2.8.6"
ARCH_NAME = "TownyArchitecture"
ARCH_JAR_NAME = f"{ARCH_NAME}-{ARCH_VERSION}.jar"

BASE_DIR = os.path.abspath(".")
SRC_DIR = os.path.join(BASE_DIR, "tmp", "minecraft-build-v2", "src", "main", "java")
RES_DIR = os.path.join(BASE_DIR, "tmp", "minecraft-build-v2", "src", "main", "resources")
BIN_DIR = os.path.join(BASE_DIR, "tmp", "minecraft-build-v2", "bin")
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
    cp_list = []
    for r, d, fs in os.walk(LIB_DIR):
        for file in fs:
            if file.endswith(".jar"):
                cp_list.append(os.path.join(r, file))
    cp_str = ":".join(cp_list)
    
    cmd = ["javac", "-cp", cp_str, "-d", BIN_DIR, "-encoding", "UTF-8"] + java_files
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("TownyArchitecture javac compilation failed:")
        print(res.stderr)
        exit(1)
    else:
        print("TownyArchitecture Java compilation successful!")
else:
    print("Error: javac not available!")
    exit(1)

# Copy resources
for res_file in ["plugin.yml", "config.yml", "buildings.yml"]:
    src_res = os.path.join(RES_DIR, res_file)
    if os.path.exists(src_res):
        shutil.copy2(src_res, os.path.join(BIN_DIR, res_file))
        print(f"Copied resource: {res_file}")

jar_out = os.path.join(DIST_DIR, ARCH_JAR_NAME)

with zipfile.ZipFile(jar_out, "w", zipfile.ZIP_DEFLATED) as zf:
    manifest_content = f"Manifest-Version: 1.0\r\nCreated-By: TownyArchitectureTeam\r\nImplementation-Version: {ARCH_VERSION}\r\n\r\n"
    zf.writestr("META-INF/MANIFEST.MF", manifest_content)
    
    for root, dirs, files in os.walk(BIN_DIR):
        for file in sorted(files):
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, BIN_DIR)
            zf.write(full_path, rel_path)

shutil.copy2(jar_out, os.path.join(DIST_DIR, "TownyArchitecture.jar"))
shutil.copy2(jar_out, os.path.join(PUBLIC_DIR, ARCH_JAR_NAME))
shutil.copy2(jar_out, os.path.join(PUBLIC_DIR, "TownyArchitecture.jar"))

print(f"TownyArchitecture JAR built at {jar_out}")
