import shutil
import zipfile
import os

def rollback():
    # Restore original 2.8k TownyRespawn-1.0.0.jar to 1.1.2 and others
    orig = 'public/TownyRespawn-1.0.0.jar'
    targets = [
        'public/TownyRespawn-1.1.2.jar',
        'public/TownyRespawn.jar',
        'public/TownyRespawn-v1.1.2.jar'
    ]
    for t in targets:
        shutil.copy2(orig, t)
        print(f"Rolled back {t} to original stub.")
        
    # Recreate TownySuite-All-Plugins.zip to match original state
    suite_zip = 'public/TownySuite-All-Plugins.zip'
    if os.path.exists(suite_zip):
        os.remove(suite_zip)
        
    with zipfile.ZipFile(suite_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write('public/TownyArchitecture-2.8.6.jar', 'TownyArchitecture-2.8.6.jar')
        zf.write('public/TownySieges-1.3.2.jar', 'TownySieges-1.3.2.jar')
        zf.write('public/TownyRespawn-1.1.2.jar', 'TownyRespawn-1.1.2.jar')
        zf.write('public/TownyExplosionUnblocker-1.1.2.jar', 'TownyExplosionUnblocker-1.1.2.jar')
        zf.writestr('README.txt', 'TownySuite All Plugins Bundle\n')
        
    print("Rollback completed successfully.")

if __name__ == "__main__":
    rollback()
