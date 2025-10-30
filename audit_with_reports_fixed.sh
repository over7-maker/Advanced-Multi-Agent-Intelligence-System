#!/bin/bash

echo "🚀 COMPREHENSIVE AUDIT WITH REPORTS"
echo "==================================="
echo ""

# Create timestamp for unique filename
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_FILE="audit_results_${TIMESTAMP}.json"

# Run the audit
echo "🔍 Running comprehensive audit..."
python3 .github/scripts/comprehensive_audit_engine.py \
  --audit-type comprehensive \
  --create-issues false \
  --notify-on-failure false \
  --output "$OUTPUT_FILE"

# Store exit code
AUDIT_EXIT_CODE=$?

# Check if results file was created (regardless of exit code)
if [ -f "$OUTPUT_FILE" ]; then
    echo ""
    echo "📊 Generating HTML and text reports..."
    
    # Generate reports
    python3 generate_audit_report.py
    
    echo ""
    echo "✅ AUDIT AND REPORTS COMPLETED!"
    echo ""
    echo "📁 FILES CREATED:"
    echo "================="
    ls -la audit_report_*.html audit_report_*.txt audit_results_*.json 2>/dev/null | head -10
    
    echo ""
    echo "🌐 VIEW REPORTS:"
    echo "==============="
    echo "1. Open the HTML file in your browser for a beautiful report"
    echo "2. Open the text file for mobile-friendly viewing"
    echo "3. Check the JSON file for detailed data"
    echo ""
    echo "📱 FOR MOBILE VIEWING:"
    echo "====================="
    echo "The .txt file is perfect for your iPod browser!"
    echo "It contains all the audit results in a simple text format."
    
    # Show quick summary
    echo ""
    echo "📊 QUICK SUMMARY:"
    echo "================="
    python3 -c "
import json
try:
    with open('$OUTPUT_FILE', 'r') as f:
        data = json.load(f)
    stats = data.get('statistics', {})
    print(f'Total Issues: {stats.get(\"total_issues\", 0)}')
    print(f'Critical Issues: {stats.get(\"critical_issues\", 0)}')
    print(f'High Priority: {stats.get(\"high_priority_issues\", 0)}')
    print(f'Medium Priority: {stats.get(\"medium_priority_issues\", 0)}')
    print(f'Low Priority: {stats.get(\"low_priority_issues\", 0)}')
except Exception as e:
    print(f'Error reading results: {e}')
"
    
else
    echo "❌ Audit failed! No results file created."
    echo "Please check the error messages above."
    exit 1
fi

echo ""
echo "🎉 ALL DONE!"