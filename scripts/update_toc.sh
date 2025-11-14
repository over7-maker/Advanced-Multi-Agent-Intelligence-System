#!/bin/bash
# Pre-commit hook script to auto-generate TOC for PERFORMANCE_SCALING_GUIDE.md

set -e

FILE="docs/PERFORMANCE_SCALING_GUIDE.md"

if [ ! -f "$FILE" ]; then
    echo "Error: $FILE not found"
    exit 1
fi

# Generate TOC
npx --yes markdown-toc "$FILE" --bullets="-" --no-first-h1 > /tmp/toc_content.txt 2>/dev/null

# Extract TOC content (skip first line which is the title)
TOC_CONTENT=$(tail -n +2 /tmp/toc_content.txt)

# Replace TOC section in file
python3 << 'PYTHON_SCRIPT'
import re
import sys

file_path = "docs/PERFORMANCE_SCALING_GUIDE.md"

with open(file_path, 'r') as f:
    content = f.read()

# Read TOC from temp file
with open('/tmp/toc_content.txt', 'r') as f:
    toc_lines = f.readlines()

# Skip first line (title) and get TOC
toc_content = ''.join(toc_lines[1:]).strip()

# Replace TOC section
pattern = r'<!-- TOC -->.*?<!-- /TOC -->'
replacement = f'<!-- TOC -->\n{toc_content}\n<!-- /TOC -->'

new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(new_content)

print("TOC updated successfully")
PYTHON_SCRIPT

rm -f /tmp/toc_content.txt
