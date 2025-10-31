#!/bin/bash

echo "📝 GENERATING COMPREHENSIVE TXT REPORTS"
echo "======================================="
echo ""

# Create timestamp for unique filenames
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_DIR="comprehensive_reports_${TIMESTAMP}"

# Create report directory
mkdir -p "$REPORT_DIR"

echo "📁 Creating report directory: $REPORT_DIR"
echo ""

# 1. Run comprehensive audit and save results
echo "🔍 Running comprehensive audit..."
python3 .github/scripts/comprehensive_audit_engine.py \
  --audit-type comprehensive \
  --create-issues false \
  --notify-on-failure false \
  --output "$REPORT_DIR/audit_results.json" > "$REPORT_DIR/audit_output.txt" 2>&1

# 2. Run focused pre-merge test
echo "🎯 Running focused pre-merge test..."
python3 focused_pre_merge_test.py > "$REPORT_DIR/focused_test_output.txt" 2>&1

# 3. Run workflow execution test
echo "⚙️ Running workflow execution test..."
python3 test_workflow_execution.py > "$REPORT_DIR/workflow_execution_output.txt" 2>&1

# 4. Generate comprehensive test suite
echo "🧪 Running comprehensive test suite..."
python3 run_all_tests_with_txt_output.py > "$REPORT_DIR/test_suite_output.txt" 2>&1

# 5. Create a master summary report
echo "📊 Creating master summary report..."
cat > "$REPORT_DIR/MASTER_SUMMARY_REPORT.txt" << EOF
🧪 COMPREHENSIVE TESTING MASTER SUMMARY
=======================================
Generated: $(date)
Report Directory: $REPORT_DIR/

📁 AVAILABLE REPORTS:
====================
• audit_results.json - Raw audit data
• audit_output.txt - Audit execution output
• focused_test_output.txt - Focused pre-merge test results
• workflow_execution_output.txt - Workflow execution test results
• test_suite_output.txt - Comprehensive test suite output
• test_results/ - Directory with detailed test results
  - yaml_syntax_test.txt
  - python_syntax_test.txt
  - api_key_migration_test.txt
  - security_test.txt
  - workflow_integrity_test.txt
  - audit_system_test.txt
  - FINAL_COMPREHENSIVE_TEST_REPORT.txt

🎯 QUICK STATUS CHECK:
=====================
EOF

# Add quick status from audit results
if [ -f "$REPORT_DIR/audit_results.json" ]; then
    echo "✅ Audit completed successfully"
    echo "📊 Audit statistics:"
    python3 -c "
import json
try:
    with open('$REPORT_DIR/audit_results.json', 'r') as f:
        data = json.load(f)
    stats = data.get('statistics', {})
    print(f'  Total Issues: {stats.get(\"total_issues\", 0)}')
    print(f'  Critical Issues: {stats.get(\"critical_issues\", 0)}')
    print(f'  High Priority: {stats.get(\"high_priority_issues\", 0)}')
    print(f'  Medium Priority: {stats.get(\"medium_priority_issues\", 0)}')
    print(f'  Low Priority: {stats.get(\"low_priority_issues\", 0)}')
except Exception as e:
    print(f'  Error reading audit results: {e}')
" >> "$REPORT_DIR/MASTER_SUMMARY_REPORT.txt"
else
    echo "❌ Audit failed to complete" >> "$REPORT_DIR/MASTER_SUMMARY_REPORT.txt"
fi

# Add focused test status
if [ -f "$REPORT_DIR/focused_test_output.txt" ]; then
    echo "" >> "$REPORT_DIR/MASTER_SUMMARY_REPORT.txt"
    echo "🎯 Focused Test Status:" >> "$REPORT_DIR/MASTER_SUMMARY_REPORT.txt"
    if grep -q "MERGE READY" "$REPORT_DIR/focused_test_output.txt"; then
        echo "✅ MERGE READY!" >> "$REPORT_DIR/MASTER_SUMMARY_REPORT.txt"
    elif grep -q "MERGE WITH CAUTION" "$REPORT_DIR/focused_test_output.txt"; then
        echo "⚠️  MERGE WITH CAUTION" >> "$REPORT_DIR/MASTER_SUMMARY_REPORT.txt"
    else
        echo "❌ NOT READY FOR MERGE" >> "$REPORT_DIR/MASTER_SUMMARY_REPORT.txt"
    fi
fi

# Add test suite status
if [ -f "test_results/FINAL_COMPREHENSIVE_TEST_REPORT.txt" ]; then
    echo "" >> "$REPORT_DIR/MASTER_SUMMARY_REPORT.txt"
    echo "🧪 Test Suite Status:" >> "$REPORT_DIR/MASTER_SUMMARY_REPORT.txt"
    if grep -q "EXCELLENT - READY FOR PRODUCTION" "test_results/FINAL_COMPREHENSIVE_TEST_REPORT.txt"; then
        echo "✅ EXCELLENT - READY FOR PRODUCTION!" >> "$REPORT_DIR/MASTER_SUMMARY_REPORT.txt"
    elif grep -q "GOOD - READY WITH CAUTION" "test_results/FINAL_COMPREHENSIVE_TEST_REPORT.txt"; then
        echo "⚠️  GOOD - READY WITH CAUTION" >> "$REPORT_DIR/MASTER_SUMMARY_REPORT.txt"
    else
        echo "❌ NEEDS ATTENTION" >> "$REPORT_DIR/MASTER_SUMMARY_REPORT.txt"
    fi
fi

echo "" >> "$REPORT_DIR/MASTER_SUMMARY_REPORT.txt"
echo "📱 MOBILE VIEWING:" >> "$REPORT_DIR/MASTER_SUMMARY_REPORT.txt"
echo "==================" >> "$REPORT_DIR/MASTER_SUMMARY_REPORT.txt"
echo "All .txt files are perfect for viewing on your iPod browser!" >> "$REPORT_DIR/MASTER_SUMMARY_REPORT.txt"
echo "Start with MASTER_SUMMARY_REPORT.txt for an overview." >> "$REPORT_DIR/MASTER_SUMMARY_REPORT.txt"

# 6. Copy test results to report directory
if [ -d "test_results" ]; then
    cp -r test_results/* "$REPORT_DIR/"
    echo "📁 Copied test results to report directory"
fi

# 7. Create a simple index file
cat > "$REPORT_DIR/README.txt" << EOF
📱 COMPREHENSIVE TEST REPORTS - MOBILE FRIENDLY
===============================================

Start here: MASTER_SUMMARY_REPORT.txt

📁 FILE STRUCTURE:
==================
• MASTER_SUMMARY_REPORT.txt - Quick overview and status
• README.txt - This file
• audit_results.json - Raw audit data
• audit_output.txt - Audit execution details
• focused_test_output.txt - Pre-merge test results
• workflow_execution_output.txt - Workflow tests
• test_suite_output.txt - Comprehensive test suite
• yaml_syntax_test.txt - YAML validation results
• python_syntax_test.txt - Python validation results
• api_key_migration_test.txt - API key migration status
• security_test.txt - Security validation results
• workflow_integrity_test.txt - Workflow structure tests
• audit_system_test.txt - Audit system functionality
• FINAL_COMPREHENSIVE_TEST_REPORT.txt - Complete test summary

🎯 QUICK START:
===============
1. Read MASTER_SUMMARY_REPORT.txt for overview
2. Check FINAL_COMPREHENSIVE_TEST_REPORT.txt for details
3. Review specific test files as needed

📱 All files are optimized for mobile viewing!
EOF

echo ""
echo "✅ COMPREHENSIVE REPORTS GENERATED!"
echo "📁 Report directory: $REPORT_DIR/"
echo "📱 Perfect for your iPod browser!"
echo ""
echo "🎯 QUICK START:"
echo "1. Open: $REPORT_DIR/MASTER_SUMMARY_REPORT.txt"
echo "2. Check: $REPORT_DIR/FINAL_COMPREHENSIVE_TEST_REPORT.txt"
echo "3. Review specific test files as needed"
echo ""
echo "📊 FILES CREATED:"
ls -la "$REPORT_DIR/" | head -10
echo ""
echo "🎉 ALL DONE! Check the $REPORT_DIR/ directory!"