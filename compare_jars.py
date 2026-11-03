import zipfile

for path in ['public/TownySieges-1.3.2.jar', 'public/TownyRespawn-1.1.2.jar']:
    print("---", path)
    with zipfile.ZipFile(path, 'r') as zf:
        print(zf.namelist()[:5])
