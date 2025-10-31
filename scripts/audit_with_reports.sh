#!/bin/bash

echo "🚀 COMPREHENSIVE AUDIT WITH REPORTS"
echo "==================================="
echo ""

# Run the audit
echo "🔍 Running comprehensive audit..."
python3 .github/scripts/comprehensive_audit_engine.py \
  --audit-type comprehensive \
  --create-issues false \
  --notify-on-failure false \
  --output audit_results_$(date +%Y%m%d_%H%M%S).json

# Check if audit completed
if [ $? -eq 0 ] || [ -f audit_results_*.json ]; then
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
    
else
    echo "❌ Audit failed! Please check the error messages above."
    exit 1
fi

echo ""
echo "🎉 ALL DONE!"