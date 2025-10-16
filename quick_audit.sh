#!/bin/bash
echo "🔍 QUICK AUDIT - RUNNING NOW..."
python3 .github/scripts/comprehensive_audit_engine.py --audit-type comprehensive --create-issues false --notify-on-failure false --output quick_audit.json && echo "✅ SUCCESS!" || echo "⚠️ ISSUES FOUND - Check results"
echo "📊 Results:"
python3 -c "import json; data=json.load(open('quick_audit.json')); stats=data['statistics']; print(f'Total: {stats[\"total_issues\"]}, Critical: {stats[\"critical_issues\"]}, High: {stats[\"high_priority_issues\"]}')"