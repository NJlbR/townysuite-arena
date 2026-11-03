import zipfile
import re

def check_all_classes(jar_path):
    with zipfile.ZipFile(jar_path, 'r') as zf:
        for info in zf.infolist():
            if info.filename.endswith('.class'):
                data = zf.read(info.filename)
                refs = set(s.decode() for s in re.findall(rb'([a-z0-9_/]+/[a-zA-Z0-9_/]+)', data))
                for r in refs:
                    if 'towny' in r:
                        print(f"{info.filename} -> {r}")

if __name__ == "__main__":
    check_all_classes('public/TownyRespawn-1.1.2.jar')
