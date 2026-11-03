import fs from 'fs';

const filePath = '/src/data/javaSources.ts';
let content = fs.readFileSync(filePath, 'utf8');

// The issue is literal newlines inside double-quoted strings.
// We need to find "content": "..." and replace internal literal newlines with \n.

// A regex to find the content value
const contentRegex = /"content":\s*"([\s\S]*?)"(?=\s*,\s*"category")/g;

let fixedContent = content.replace(contentRegex, (match, p1) => {
    // p1 is the content of the string. We need to replace literal newlines with \n
    // but be careful not to double-escape existing \n.
    
    // First, if there are literal newlines, they are the problem.
    const sanitized = p1.replace(/\n/g, '\\n').replace(/\r/g, '');
    return `"content": "${sanitized}"`;
});

fs.writeFileSync(filePath, fixedContent);
console.log("Sanitized javaSources.ts");
