import zipfile

def get_class_name(jar_path):
    with zipfile.ZipFile(jar_path, 'r') as zf:
        with zf.open('com/towny/respawn/TownyRespawnPlugin.class') as f:
            data = f.read()
            # In a class file, the constant pool contains the internal name of the class.
            # Let's just print all strings that look like class/package names.
            import re
            print(re.findall(rb'(com/towny/[a-zA-Z0-9_/]+)', data))

if __name__ == "__main__":
    get_class_name('public/TownyRespawn-1.1.2.jar')
