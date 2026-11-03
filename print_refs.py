import zipfile

def print_all_refs(jar_path):
    with zipfile.ZipFile(jar_path, 'r') as zf:
        with zf.open('com/towny/respawn/TownyRespawnPlugin.class') as f:
            data = f.read()
            import re
            # Find all ASCII-like strings in the class file
            strings = re.findall(rb'([a-zA-Z0-9_/]{4,})', data)
            for s in strings:
                try:
                    text = s.decode('utf-8')
                    if '/' in text:
                        print(text)
                except:
                    pass

if __name__ == "__main__":
    print_all_refs('public/TownyRespawn-1.1.2.jar')
