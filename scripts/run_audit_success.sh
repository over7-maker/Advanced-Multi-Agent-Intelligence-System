#!/bin/bash

echo "🚀 RUNNING COMPREHENSIVE AUDIT - SUCCESS VERSION"
echo "================================================"
echo ""

# Check if we're in the right directory
if [ ! -f ".github/scripts/comprehensive_audit_engine.py" ]; then
    echo "❌ Error: Not in the correct directory"
    echo "Please run this script from the project root"
    exit 1
fi

echo "🔍 Starting Comprehensive Audit..."
echo ""

# Create timestamp for unique filename
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_FILE="audit_results_${TIMESTAMP}.json"

# Run the audit and capture the exit code
python3 .github/scripts/comprehensive_audit_engine.py \
  --audit-type comprehensive \
  --create-issues false \
  --notify-on-failure false \
  --output "$OUTPUT_FILE"

# Store the exit code
AUDIT_EXIT_CODE=$?

echo ""
echo "📊 AUDIT RESULTS SUMMARY"
echo "========================"

# Check if results file was created
if [ -f "$OUTPUT_FILE" ]; then
    echo "✅ Audit results file created: $OUTPUT_FILE"
    echo ""
    
    # Show detailed summary
    python3 -c "
import json
import sys
try:
    with open('$OUTPUT_FILE', 'r') as f:
        data = json.load(f)
    
    stats = data.get('statistics', {})
    print('📈 STATISTICS:')
    print(f'  Total Issues: {stats.get(\"total_issues\", 0)}')
    print(f'  Critical Issues: {stats.get(\"critical_issues\", 0)}')
    print(f'  High Priority: {stats.get(\"high_priority_issues\", 0)}')
    print(f'  Medium Priority: {stats.get(\"medium_priority_issues\", 0)}')
    print(f'  Low Priority: {stats.get(\"low_priority_issues\", 0)}')
    print('')
    
    # Show workflow audit results
    workflow_audit = data.get('workflow_audit', {})
    print('🔍 WORKFLOW AUDIT:')
    print(f'  Total Workflows: {workflow_audit.get(\"total_workflows\", 0)}')
    print(f'  Duplicate Triggers: {len(workflow_audit.get(\"duplicate_triggers\", []))}')
    print(f'  Conflicting Triggers: {len(workflow_audit.get(\"conflicting_triggers\", []))}')
    print('')
    
    # Show API key audit results
    api_audit = data.get('api_key_audit', {})
    print('🔑 API KEY AUDIT:')
    print(f'  Direct Usage: {len(api_audit.get(\"direct_usage\", []))}')
    print(f'  Manager Usage: {len(api_audit.get(\"manager_usage\", []))}')
    print(f'  Missing Manager: {len(api_audit.get(\"missing_manager\", []))}')
    print('')
    
    # Show legacy audit results
    legacy_audit = data.get('legacy_audit', {})
    print('🧹 LEGACY AUDIT:')
    print(f'  Stub Workflows: {len(legacy_audit.get(\"stub_workflows\", []))}')
    print(f'  Legacy Workflows: {len(legacy_audit.get(\"legacy_workflows\", []))}')
    print(f'  Minimal Workflows: {len(legacy_audit.get(\"minimal_workflows\", []))}')
    print(f'  Broken Workflows: {len(legacy_audit.get(\"broken_workflows\", []))}')
    print('')
    
    # Show security audit results
    security_audit = data.get('security_audit', {})
    print('🛡️ SECURITY AUDIT:')
    print(f'  Exposed Secrets: {len(security_audit.get(\"exposed_secrets\", []))}')
    print(f'  Insecure Patterns: {len(security_audit.get(\"insecure_patterns\", []))}')
    print(f'  Vulnerable Dependencies: {len(security_audit.get(\"vulnerable_dependencies\", []))}')
    print('')
    
    # Show recommendations
    recommendations = data.get('recommendations', [])
    if recommendations:
        print('🎯 TOP RECOMMENDATIONS:')
        for i, rec in enumerate(recommendations[:5], 1):
            print(f'  {i}. [{rec[\"priority\"].upper()}] {rec[\"title\"]}')
            print(f'     Description: {rec[\"description\"]}')
            print(f'     Action: {rec[\"action\"]}')
            print('')
    
    # Show critical issues
    critical_issues = data.get('critical_issues', [])
    if critical_issues:
        print('🚨 CRITICAL ISSUES:')
        for i, issue in enumerate(critical_issues, 1):
            print(f'  {i}. {issue[\"title\"]}')
        print('')
    
    print('✅ Audit analysis completed successfully!')
    
except Exception as e:
    print(f'❌ Error reading results: {e}')
    sys.exit(1)
"

    echo ""
    echo "📁 Detailed results saved to: $OUTPUT_FILE"
    echo ""
    
    # Determine overall status
    if [ $AUDIT_EXIT_CODE -eq 0 ]; then
        echo "🎉 AUDIT STATUS: SUCCESS - No critical issues found!"
    else
        echo "⚠️  AUDIT STATUS: ISSUES FOUND - Review recommendations above"
    fi
    
    echo ""
    echo "🎯 NEXT STEPS:"
    echo "1. Review the detailed audit results above"
    echo "2. Fix critical issues identified"
    echo "3. Run the audit again to verify fixes"
    echo ""
    echo "🚀 TO RUN VIA GITHUB ACTIONS:"
    echo "1. Go to your repository on GitHub"
    echo "2. Click 'Actions' tab"
    echo "3. Find 'Simple Audit Test' workflow"
    echo "4. Click 'Run workflow'"
    echo ""
    echo "📊 TO VIEW DETAILED RESULTS:"
    echo "cat $OUTPUT_FILE | jq '.'"
    
else
    echo "❌ Audit results file not found: $OUTPUT_FILE"
    echo "The audit may have failed to complete"
    exit 1
fi

echo ""
echo "🎉 AUDIT COMPLETE!"