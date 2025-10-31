#!/bin/bash
echo "🚀 CREATING ALL TXT TESTS FOR MOBILE VIEWING"
echo "============================================="
echo ""

echo "🧪 Running quick test..."
python3 quick_txt_test.py

echo ""
echo "🧪 Running comprehensive tests..."
python3 run_all_txt_tests.py

echo ""
echo "📁 All text files created:"
echo "=========================="
ls -la *.txt | grep -E "(QUICK|MASTER|SIMPLE|FINAL|ULTIMATE)" | head -10

echo ""
echo "✅ ALL TESTS COMPLETED!"
echo "📱 Perfect for mobile viewing on iPod browser!"
echo "🎯 No more command line issues!"