import zipfile

with zipfile.ZipFile('public/TownyRespawn-1.1.2.jar', 'r') as zf:
    for name in zf.namelist():
        print(repr(name))
