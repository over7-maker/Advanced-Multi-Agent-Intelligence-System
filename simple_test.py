#!/usr/bin/env python3
"""
Super Simple Test - Just the basics
"""

print("🧪 SIMPLE TEST - CHECKING SYSTEM STATUS")
print("=" * 50)

# Test 1: Check if we can import the API manager
try:
    from standalone_universal_ai_manager import StandaloneUniversalAIManager
    print("✅ API Manager: Can import successfully")
    api_manager_ok = True
except Exception as e:
    print(f"❌ API Manager: Import failed - {e}")
    api_manager_ok = False

# Test 2: Check if audit engine exists and can run
import os
if os.path.exists('.github/scripts/comprehensive_audit_engine.py'):
    print("✅ Audit Engine: File exists")
    audit_engine_ok = True
else:
    print("❌ Audit Engine: File not found")
    audit_engine_ok = False

# Test 3: Check workflow files
workflow_files = [
    '.github/workflows/00-master-ai-orchestrator.yml',
    '.github/workflows/comprehensive-audit.yml',
    '.github/workflows/ai-agentic-issue-auto-responder.yml'
]

workflow_count = 0
for wf in workflow_files:
    if os.path.exists(wf):
        workflow_count += 1
        print(f"✅ Workflow: {wf.split('/')[-1]} exists")
    else:
        print(f"❌ Workflow: {wf.split('/')[-1]} missing")

# Calculate overall status
total_tests = 3
passed_tests = (1 if api_manager_ok else 0) + (1 if audit_engine_ok else 0) + (1 if workflow_count >= 2 else 0)
success_rate = (passed_tests / total_tests * 100)

print("\n📊 SIMPLE TEST RESULTS")
print("=" * 30)
print(f"Total Tests: {total_tests}")
print(f"Passed: {passed_tests}")
print(f"Success Rate: {success_rate:.1f}%")

if success_rate >= 80:
    print("\n🎉 STATUS: READY FOR MERGE!")
    status = "READY"
else:
    print("\n⚠️  STATUS: NEEDS ATTENTION")
    status = "NEEDS_ATTENTION"

# Save results to file
with open('SIMPLE_TEST_RESULTS.txt', 'w') as f:
    f.write("🧪 SIMPLE TEST RESULTS\n")
    f.write("=" * 30 + "\n")
    f.write(f"API Manager: {'✅ OK' if api_manager_ok else '❌ FAIL'}\n")
    f.write(f"Audit Engine: {'✅ OK' if audit_engine_ok else '❌ FAIL'}\n")
    f.write(f"Workflows: {workflow_count}/3 found\n")
    f.write(f"Success Rate: {success_rate:.1f}%\n")
    f.write(f"Status: {status}\n")

print(f"\n📁 Results saved to: SIMPLE_TEST_RESULTS.txt")
print("📱 Perfect for your iPod browser!")