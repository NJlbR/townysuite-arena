import fs from 'fs';
import path from 'path';

const sourcesTsPath = 'src/data/javaSources.ts';
let content = fs.readFileSync(sourcesTsPath, 'utf8');

const buildingHudPath = 'tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingHudManager.java';
const buildingHudContent = fs.readFileSync(buildingHudPath, 'utf8');

function escapeJava(str) {
    return str
        .replace(/\\/g, '\\\\')
        .replace(/"/g, '\\"')
        .replace(/\n/g, '\\n')
        .replace(/\r/g, '');
}

const escapedBuildingHud = escapeJava(buildingHudContent);

const hudRegex = /\{\s*"path":\s*"[^"]*BuildingHudManager\.java",\s*"name":\s*"BuildingHudManager\.java",\s*"content":\s*"[\s\S]*?",\s*"category":\s*"core"\s*\}/g;

const newHudObj = `{
    "path": "src/main/java/com/towny/architecture/manager/BuildingHudManager.java",
    "name": "BuildingHudManager.java",
    "content": "${escapedBuildingHud}",
    "category": "core"
  }`;

let fixedContent = content.replace(hudRegex, newHudObj);

fs.writeFileSync(sourcesTsPath, fixedContent);
console.log("Successfully updated BuildingHudManager.java in src/data/javaSources.ts");

