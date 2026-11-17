#!/usr/bin/env python3
"""Build only the standalone TownyJobs plugin; existing plugin artifacts are untouched."""
from pathlib import Path
import shutil
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parent
PLUGIN_ROOT = ROOT / "tmp" / "towny-jobs"
SOURCE_ROOT = PLUGIN_ROOT / "src" / "main" / "java"
RESOURCE_ROOT = PLUGIN_ROOT / "src" / "main" / "resources"
BIN_ROOT = PLUGIN_ROOT / "bin"
LIB_ROOT = ROOT / "tmp" / "minecraft-build-v2" / "lib"
VERSION = "1.0.0"
JAR_NAME = f"TownyJobs-{VERSION}.jar"
BUNDLE_NAME = f"TownyJobs-v{VERSION}-bundle.zip"

javac = shutil.which("javac")
if not javac:
    raise SystemExit("TownyJobs build aborted: javac is required; refusing to create a source-only or stale JAR")

if not (LIB_ROOT / "Towny.jar").is_file() or not (LIB_ROOT / "paper-api.jar").is_file():
    raise SystemExit("TownyJobs build aborted: expected Towny.jar and paper-api.jar in tmp/minecraft-build-v2/lib")

shutil.rmtree(BIN_ROOT, ignore_errors=True)
BIN_ROOT.mkdir(parents=True, exist_ok=True)
java_files = sorted(SOURCE_ROOT.rglob("*.java"))
if not java_files:
    raise SystemExit("TownyJobs build aborted: no Java sources found")

classpath = str(LIB_ROOT / "*")
subprocess.run([
    javac, "-encoding", "UTF-8", "-source", "17", "-target", "17",
    "-cp", classpath, "-d", str(BIN_ROOT), *map(str, java_files)
], check=True, cwd=ROOT)

for resource in RESOURCE_ROOT.iterdir():
    if resource.is_file():
        shutil.copy2(resource, BIN_ROOT / resource.name)

jar_bytes_path = ROOT / "dist" / JAR_NAME
jar_bytes_path.parent.mkdir(parents=True, exist_ok=True)
public_path = ROOT / "public" / JAR_NAME
public_path.parent.mkdir(parents=True, exist_ok=True)

with zipfile.ZipFile(jar_bytes_path, "w", zipfile.ZIP_DEFLATED) as jar:
    jar.writestr("META-INF/MANIFEST.MF", "Manifest-Version: 1.0\r\nCreated-By: TownyJobs Build\r\n\r\n")
    for file in sorted(BIN_ROOT.rglob("*")):
        if file.is_file():
            jar.write(file, file.relative_to(BIN_ROOT).as_posix())
shutil.copy2(jar_bytes_path, public_path)

bundle_path = ROOT / "public" / BUNDLE_NAME
with zipfile.ZipFile(bundle_path, "w", zipfile.ZIP_DEFLATED) as bundle:
    bundle.write(jar_bytes_path, JAR_NAME)
    bundle.write(RESOURCE_ROOT / "config.yml", "config.yml")
    bundle.write(PLUGIN_ROOT / "README.md", "README.md")
print(f"Built {public_path.relative_to(ROOT)} and {bundle_path.relative_to(ROOT)}")
