#!/bin/bash

echo "🧪 RUNNING ACCURATE FINAL TEST"
echo "=============================="
echo ""

# Check if we're in the right directory
if [ ! -f "accurate_final_test.py" ]; then
    echo "❌ Error: accurate_final_test.py not found in current directory"
    echo "Current directory: $(pwd)"
    echo "Available files:"
    ls -la *test*.py 2>/dev/null || echo "No test files found"
    exit 1
fi

echo "✅ Found accurate_final_test.py"
echo "🚀 Running test..."
echo ""

# Run the test
python3 accurate_final_test.py

echo ""
echo "📁 Test completed! Check ACCURATE_FINAL_TEST_REPORT.txt for results"