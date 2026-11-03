import zipfile

def inspect_class(jar_path):
    with zipfile.ZipFile(jar_path, 'r') as zf:
        with zf.open('com/towny/respawn/TownyRespawnPlugin.class') as f:
            content = f.read()
            print("Class file size:", len(content))
            # Just search for JavaPlugin in the binary content
            if b'org/bukkit/plugin/java/JavaPlugin' in content:
                print("Extends JavaPlugin: YES")
            else:
                print("Extends JavaPlugin: NO")

if __name__ == "__main__":
    inspect_class('public/TownyRespawn-1.1.2.jar')
