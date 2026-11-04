import fs from 'node:fs';

const sourceMap = [
  ['tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/BuildingHudManager.java', 'BuildingHudManager.java'],
  ['tmp/minecraft-build-v2/src/main/java/com/towny/architecture/manager/HologramDisplayManager.java', 'HologramDisplayManager.java'],
  ['tmp/minecraft-build-v2/src/main/java/com/towny/architecture/util/ModelShapeUtil.java', 'ModelShapeUtil.java'],
];
const sourceFile = 'src/data/javaSources.ts';
let text = fs.readFileSync(sourceFile, 'utf8');
const declaration = 'export const JAVA_SOURCES: JavaSourceFile[] = [';
const arrayStart = text.indexOf(declaration) + declaration.length - 1;
const arrayEnd = text.indexOf('\n];', arrayStart) + 2;
if (arrayStart < declaration.length - 1 || arrayEnd < 2) throw new Error('JAVA_SOURCES array not found');
const sources = JSON.parse(text.slice(arrayStart, arrayEnd));

for (const [diskPath, name] of sourceMap) {
  const embeddedSource = sources.find(source => source.name === name);
  if (!embeddedSource) throw new Error(`Embedded source not found: ${name}`);
  const java = fs.readFileSync(diskPath, 'utf8');
  const nameMarker = `"name": "${name}"`;
  const markerIndex = text.indexOf(nameMarker);
  const serializedOldContent = JSON.stringify(embeddedSource.content);
  const contentIndex = text.indexOf(serializedOldContent, markerIndex);
  if (markerIndex < 0 || contentIndex < 0) throw new Error(`Embedded content token not found: ${name}`);
  const serializedNewContent = JSON.stringify(java);
  text = text.slice(0, contentIndex) + serializedNewContent + text.slice(contentIndex + serializedOldContent.length);
  console.log(`Synchronized ${name}`);
}
fs.writeFileSync(sourceFile, text);
