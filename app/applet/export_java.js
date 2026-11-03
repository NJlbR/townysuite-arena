import fs from 'fs';
import path from 'path';

const sourcesPath = './src/data/javaSources.ts';
if (!fs.existsSync(sourcesPath)) {
    console.error("javaSources.ts not found");
    process.exit(1);
}

const content = fs.readFileSync(sourcesPath, 'utf8');

// The file contains: export const JAVA_SOURCES = [...];
// We want to extract the array content.
// Since it's valid TS (or was), we can use a simpler regex if it's mostly JSON.
const match = content.match(/export const JAVA_SOURCES = (\[[\s\S]*?\]);/);
if (!match) {
    console.error("Could not find JAVA_SOURCES array");
    process.exit(1);
}

try {
    const sources = JSON.parse(match[1]);
    for (const src of sources) {
        const fullPath = path.join('./tmp_java', src.path);
        fs.mkdirSync(path.dirname(fullPath), { recursive: true });
        fs.writeFileSync(fullPath, src.content);
        console.log(`Exported ${src.path}`);
    }
} catch (e) {
    console.error("JSON parse failed: " + e.message);
    // If JSON parse fails, it means the file IS indeed corrupted with literal newlines.
    // Fallback: use a more manual parser.
    console.log("Attempting manual extraction...");
    
    const entries = match[1].split('},');
    for (let entry of entries) {
        const pathMatch = entry.match(/"path":\s*"([^"]+)"/);
        const contentMatch = entry.match(/"content":\s*"([\s\S]*)"/);
        if (pathMatch && contentMatch) {
            const relPath = pathMatch[1];
            // Unescape \n and \"
            let rawContent = contentMatch[1].replace(/\\n/g, '\n').replace(/\\"/g, '"').replace(/\\\\/g, '\\');
            const fullPath = path.join('./tmp_java', relPath);
            fs.mkdirSync(path.dirname(fullPath), { recursive: true });
            fs.writeFileSync(fullPath, rawContent);
            console.log(`Manually Exported ${relPath}`);
        }
    }
}
