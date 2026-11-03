import subprocess
import os

cp = "tmp/minecraft-build-v2/lib/*"
cmd = ["javac", "-cp", cp, "-d", "/tmp/test_bin", "-encoding", "UTF-8", "tmp/towny-sieges/src/main/java/com/towny/sieges/model/NationWar.java"]
os.makedirs("/tmp/test_bin", exist_ok=True)
res = subprocess.run(cmd, capture_output=True, text=True)
print("Return code:", res.returncode)
if res.returncode != 0:
    print(res.stderr)
else:
    print("NationWar.java compiled successfully!")
