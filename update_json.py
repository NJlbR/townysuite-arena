import sys

with open('src/data/javaSources.ts', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('fileName: "TownyArchitecture-1.2.0.jar"', 'fileName: "TownyArchitecture-1.3.0.jar"')
content = content.replace('bundleFileName: "TownyArchitecture-v1.2.0-bundle.zip"', 'bundleFileName: "TownyArchitecture-v1.3.0-bundle.zip"')
content = content.replace('jarDownloadUrl: "/TownyArchitecture-1.2.0.jar"', 'jarDownloadUrl: "/TownyArchitecture-1.3.0.jar"')
content = content.replace('bundleDownloadUrl: "/TownyArchitecture-v1.2.0-bundle.zip"', 'bundleDownloadUrl: "/TownyArchitecture-v1.3.0-bundle.zip"')
content = content.replace('fileSizeBytes: 69485', 'fileSizeBytes: 71884')
content = content.replace('fileSizeFormatted: "67.86 KB"', 'fileSizeFormatted: "70.20 KB"')
content = content.replace('sha256: "013b972eb5e0a760bb2dd62506b209142e522969d345078420d794780cd47a98"', 'sha256: "5050d62165d6f0e2fd1f5103895ee23f4c638136a676865ba52b98cf311384da"')

with open('src/data/javaSources.ts', 'w', encoding='utf-8') as f:
    f.write(content)
