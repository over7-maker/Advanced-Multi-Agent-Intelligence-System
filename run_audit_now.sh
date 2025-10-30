#!/bin/bash

echo "🚀 RUNNING COMPREHENSIVE AUDIT NOW"
echo "=================================="
echo ""

# Check if we're in the right directory
if [ ! -f ".github/scripts/comprehensive_audit_engine.py" ]; then
    echo "❌ Error: Not in the correct directory"
    echo "Please run this script from the project root"
    exit 1
fi

echo "🔍 Starting Comprehensive Audit..."
echo ""

# Run the audit
python3 .github/scripts/comprehensive_audit_engine.py \
  --audit-type comprehensive \
  --create-issues false \
  --notify-on-failure false \
  --output audit_results_$(date +%Y%m%d_%H%M%S).json

# Check if audit completed successfully
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ AUDIT COMPLETED SUCCESSFULLY!"
    echo ""
    echo "📊 QUICK SUMMARY:"
    echo "================="
    
    # Show quick summary
    python3 -c "
import json
import sys
try:
    with open('audit_results_$(date +%Y%m%d_%H%M%S).json', 'r') as f:
        data = json.load(f)
    stats = data.get('statistics', {})
    print(f'Total Issues: {stats.get(\"total_issues\", 0)}')
    print(f'Critical Issues: {stats.get(\"critical_issues\", 0)}')
    print(f'High Priority: {stats.get(\"high_priority_issues\", 0)}')
    print(f'Medium Priority: {stats.get(\"medium_priority_issues\", 0)}')
    print(f'Low Priority: {stats.get(\"low_priority_issues\", 0)}')
    print('')
    print('Top Recommendations:')
    for i, rec in enumerate(data.get('recommendations', [])[:3], 1):
        print(f'  {i}. [{rec[\"priority\"].upper()}] {rec[\"title\"]}')
except Exception as e:
    print(f'Error reading results: {e}')
    sys.exit(1)
"
    
    echo ""
    echo "📁 Results saved to: audit_results_$(date +%Y%m%d_%H%M%S).json"
    echo ""
    echo "🎯 NEXT STEPS:"
    echo "1. Review the audit results"
    echo "2. Fix critical issues identified"
    echo "3. Run the audit again to verify fixes"
    echo ""
    echo "🚀 To run via GitHub Actions:"
    echo "1. Go to your repository on GitHub"
    echo "2. Click 'Actions' tab"
    echo "3. Find 'Simple Audit Test' workflow"
    echo "4. Click 'Run workflow'"
    
else
    echo ""
    echo "❌ AUDIT FAILED!"
    echo "Please check the error messages above"
    exit 1
fi

echo ""
echo "🎉 AUDIT COMPLETE!"