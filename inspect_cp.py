import zipfile

def inspect_constant_pool(jar_path):
    with zipfile.ZipFile(jar_path, 'r') as zf:
        with zf.open('com/towny/respawn/TownyRespawnPlugin.class') as f:
            data = f.read()
            # Simple heuristic: search for strings starting with com/ or org/ or net/
            import re
            classes = re.findall(rb'([a-z0-9_/]+/[a-zA-Z0-9_/]+)', data)
            for c in set(classes):
                try:
                    s = c.decode('utf-8')
                    if any(s.startswith(p) for p in ['com/towny/', 'org/bukkit/', 'net/minecraft/']):
                        print(s)
                except:
                    pass

if __name__ == "__main__":
    inspect_constant_pool('public/TownyRespawn-1.1.2.jar')
