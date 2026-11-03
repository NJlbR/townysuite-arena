import zipfile
import re

def inspect_hook(jar_path, filename):
    with zipfile.ZipFile(jar_path, 'r') as zf:
        with zf.open(filename) as f:
            data = f.read()
            strings = re.findall(rb'([a-zA-Z0-9_/]{4,})', data)
            for s in strings:
                try:
                    text = s.decode('utf-8')
                    if '/' in text:
                        print(text)
                except:
                    pass

if __name__ == "__main__":
    print("=== TownyHook ===")
    inspect_hook('public/TownyRespawn-1.1.2.jar', 'com/towny/respawn/hook/TownyHook.class')
    print("=== TownySiegesHook ===")
    inspect_hook('public/TownyRespawn-1.1.2.jar', 'com/towny/respawn/hook/TownySiegesHook.class')
