import os
import json
import re

file_path = './src/data/javaSources.ts'
if not os.path.exists(file_path):
    print("File not found")
    exit(1)

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# This is a very aggressive fix.
# We find "content": " and then look for the NEXT ", "category"
# and we replace everything in between with a properly escaped version.

def fix_content(match):
    head = match.group(1)
    body = match.group(2)
    tail = match.group(3)
    
    # Body might have literal newlines. 
    # We want to replace them with \n
    # First, let's normalize: replace existing \n (escaped) with actual newlines to get raw text
    raw = body.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
    # Now re-escape properly for a JSON string
    escaped = raw.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '')
    
    return head + escaped + tail

# The regex looks for "content": " ... ", "category"
fixed_content = re.sub(r'("content":\s*")([\s\S]*?)("(?:\s*,\s*"category"|\s*\}))', fix_content, content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(fixed_content)

print("Fixed javaSources.ts via Python")
