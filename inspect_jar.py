import zipfile
import sys

def inspect_jar(jar_path):
    try:
        with zipfile.ZipFile(jar_path, 'r') as zf:
            print(f"Contents of {jar_path}:")
            for info in zf.infolist():
                print(f"{info.file_size:10d}  {info.filename}")
            
            # Also try to read plugin.yml
            if 'plugin.yml' in zf.namelist():
                with zf.open('plugin.yml') as f:
                    print("\nplugin.yml content:")
                    print(f.read().decode('utf-8'))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_jar(sys.argv[1])
