import fs from 'fs';

let tsContent = fs.readFileSync('./src/data/javaSources.ts', 'utf8');

function updateFileInTs(fileName, sourcePath) {
    if (!fs.existsSync(sourcePath)) {
        console.log(`Source file not found: ${sourcePath}`);
        return;
    }
    const javaContent = fs.readFileSync(sourcePath, 'utf8');
    const jsonEscaped = JSON.stringify(javaContent);

    const searchStr = `"name": "${fileName}"`;
    const nameIdx = tsContent.indexOf(searchStr);
    if (nameIdx === -1) {
        console.log(`Key ${searchStr} not found in ts file`);
        return;
    }

    const contentMatch = tsContent.slice(nameIdx).match(/"content":\s*"/);
    if (!contentMatch) {
        console.log(`"content": not found after ${fileName}`);
        return;
    }

    const valStart = nameIdx + contentMatch.index + contentMatch[0].length - 1;
    let valEnd = -1;
    let inEscape = false;
    for (let i = valStart + 1; i < tsContent.length; i++) {
        const char = tsContent[i];
        if (inEscape) {
            inEscape = false;
        } else if (char === '\\') {
            inEscape = true;
        } else if (char === '"') {
            valEnd = i + 1;
            break;
        }
    }

    if (valEnd !== -1) {
        tsContent = tsContent.slice(0, valStart) + jsonEscaped + tsContent.slice(valEnd);
        console.log(`Successfully updated ${fileName} in javaSources.ts`);
    } else {
        console.log(`Could not find end of string for ${fileName}`);
    }
}

updateFileInTs('BuildingHudManager.java', '/tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingHudManager.java');
updateFileInTs('HologramDisplayManager.java', '/tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/HologramDisplayManager.java');

fs.writeFileSync('./src/data/javaSources.ts', tsContent);
console.log('Finished updating javaSources.ts');
