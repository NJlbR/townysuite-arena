import os
import subprocess
import shutil
import zipfile
import glob

BUILD_DIR = "tmp/minecraft-build-v2"
SRC_DIR = os.path.join(BUILD_DIR, "src/main/java")
RES_DIR = os.path.join(BUILD_DIR, "src/main/resources")
BIN_DIR = os.path.join(BUILD_DIR, "bin")
LIB_DIR = os.path.join(BUILD_DIR, "lib")

os.makedirs(BIN_DIR, exist_ok=True)
os.makedirs("dist", exist_ok=True)
os.makedirs("public", exist_ok=True)
os.makedirs("tmp/minecraft-build-v2/target", exist_ok=True)
os.makedirs("tmp/bundle-v2", exist_ok=True)

# Find all lib jars
lib_jars = []
for root, dirs, files in os.walk(LIB_DIR):
    for f in files:
        if f.endswith(".jar"):
            lib_jars.append(os.path.join(root, f))

classpath = ":".join(lib_jars)

# Find all java files
java_files = []
for root, dirs, files in os.walk(SRC_DIR):
    for file in files:
        if file.endswith(".java"):
            java_files.append(os.path.join(root, file))

print(f"Compiling {len(java_files)} Java files with {len(lib_jars)} libraries...")

cmd = [
    "javac",
    "-cp", classpath,
    "-d", BIN_DIR,
    "-encoding", "UTF-8"
] + java_files

res = subprocess.run(cmd, capture_output=True, text=True)
if res.returncode != 0:
    print("Compilation failed:")
    print(res.stderr)
    exit(1)
print("Compilation succeeded!")

# Copy resources into BIN_DIR
for root, dirs, files in os.walk(RES_DIR):
    for file in files:
        src_path = os.path.join(root, file)
        rel_path = os.path.relpath(src_path, RES_DIR)
        dst_path = os.path.join(BIN_DIR, rel_path)
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        shutil.copy2(src_path, dst_path)

# Package into JAR
def create_jar(jar_path):
    with zipfile.ZipFile(jar_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(BIN_DIR):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, BIN_DIR)
                zf.write(full_path, rel_path)

jar_targets = [
    "dist/TownyArchitecture-2.7.3.jar",
    "public/TownyArchitecture-2.7.3.jar",
    "dist/TownyArchitecture.jar",
    "public/TownyArchitecture.jar",
    "tmp/minecraft-build-v2/TownyArchitecture-2.7.3.jar",
    "tmp/minecraft-build-v2/target/TownyArchitecture-2.7.3.jar",
    "tmp/bundle-v2/TownyArchitecture-2.7.3.jar"
]

for jt in jar_targets:
    create_jar(jt)
    print(f"Created {jt} ({os.path.getsize(jt)} bytes)")

# Also create bundle zips
bundle_targets = [
    "dist/TownyArchitecture-v2.7.3-bundle.zip",
    "public/TownyArchitecture-v2.7.3-bundle.zip",
    "dist/TownyArchitecture-bundle.zip",
    "public/TownyArchitecture-bundle.zip"
]

for bt in bundle_targets:
    with zipfile.ZipFile(bt, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write("dist/TownyArchitecture-2.7.3.jar", "TownyArchitecture.jar")
        if os.path.exists("dist/TownyArchitecture-RP.zip"):
            zf.write("dist/TownyArchitecture-RP.zip", "TownyArchitecture-RP.zip")
        if os.path.exists("dist/TownyArchitecture-Modern-RP.zip"):
            zf.write("dist/TownyArchitecture-Modern-RP.zip", "TownyArchitecture-Modern-RP.zip")
    print(f"Created {bt} ({os.path.getsize(bt)} bytes)")

print("Build v2.7.3 completed successfully!")
