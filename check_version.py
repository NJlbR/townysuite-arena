import zipfile

def check_class_version(jar_path):
    with zipfile.ZipFile(jar_path, 'r') as zf:
        with zf.open('com/towny/respawn/TownyRespawnPlugin.class') as f:
            header = f.read(8)
            magic = header[0:4]
            minor = int.from_bytes(header[4:6], 'big')
            major = int.from_bytes(header[6:8], 'big')
            print(f"Magic: {magic.hex()}, Minor: {minor}, Major: {major}")

if __name__ == "__main__":
    check_class_version('public/TownyRespawn-1.1.2.jar')
