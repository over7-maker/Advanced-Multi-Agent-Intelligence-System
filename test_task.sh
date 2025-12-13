#!/bin/bash
# Quick test script to verify the task works

FILE="${1:-src/amas/agents/adaptive_personality.py}"

if [ ! -f "$FILE" ]; then
    echo "❌ File not found: $FILE"
    echo "Usage: $0 <python-file>"
    exit 1
fi

echo "🧪 Testing AI Analysis Task..."
echo "File: $FILE"
echo ""

python3 .github/scripts/cursor_ai_diagnostics.py "$FILE" 2>&1

echo ""
echo "✅ Test complete! Check output above."
