import zipfile

for path in ['public/TownySieges-1.3.2.jar', 'public/TownyRespawn-1.1.2.jar']:
    print("=== " + path + " ===")
    with zipfile.ZipFile(path, 'r') as zf:
        for info in zf.infolist():
            print(f"{info.filename} ({info.file_size} bytes, CRC: {info.CRC})")
