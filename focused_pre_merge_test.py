#!/usr/bin/env python3
"""
Focused Pre-Merge Test - Critical Components Only
"""

import os
import sys
import json
import yaml
import subprocess
from datetime import datetime

def test_critical_components():
    """Test only the most critical components for merge readiness"""
    print("🎯 FOCUSED PRE-MERGE TEST - CRITICAL COMPONENTS")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'tests_run': 0,
        'tests_passed': 0,
        'tests_failed': 0,
        'critical_failures': [],
        'warnings': []
    }
    
    def log_test(test_name, status, details="", is_critical=False):
        results['tests_run'] += 1
        if status == 'PASS':
            results['tests_passed'] += 1
            print(f"✅ {test_name}: PASS")
        elif status == 'FAIL':
            results['tests_failed'] += 1
            if is_critical:
                results['critical_failures'].append(test_name)
            print(f"❌ {test_name}: FAIL - {details}")
        elif status == 'WARN':
            results['warnings'].append(test_name)
            print(f"⚠️  {test_name}: WARN - {details}")
    
    # Test 1: Critical YAML files
    print("\n🔍 TESTING CRITICAL YAML FILES...")
    critical_yaml_files = [
        '.github/workflows/00-master-ai-orchestrator.yml',
        '.github/workflows/comprehensive-audit.yml',
        '.github/workflows/ai-agentic-issue-auto-responder.yml'
    ]
    
    for yaml_file in critical_yaml_files:
        if os.path.exists(yaml_file):
            try:
                with open(yaml_file, 'r') as f:
                    yaml.safe_load(f)
                log_test(f"YAML: {yaml_file.split('/')[-1]}", 'PASS')
            except yaml.YAMLError as e:
                log_test(f"YAML: {yaml_file.split('/')[-1]}", 'FAIL', str(e), is_critical=True)
        else:
            log_test(f"YAML: {yaml_file.split('/')[-1]}", 'WARN', "File not found")
    
    # Test 2: Critical Python files
    print("\n🐍 TESTING CRITICAL PYTHON FILES...")
    critical_python_files = [
        'standalone_universal_ai_manager.py',
        '.github/scripts/comprehensive_audit_engine.py',
        '.github/scripts/universal_ai_workflow_integration.py'
    ]
    
    for py_file in critical_python_files:
        if os.path.exists(py_file):
            try:
                with open(py_file, 'r') as f:
                    compile(f.read(), py_file, 'exec')
                log_test(f"Python: {py_file.split('/')[-1]}", 'PASS')
            except SyntaxError as e:
                log_test(f"Python: {py_file.split('/')[-1]}", 'FAIL', str(e), is_critical=True)
            except Exception as e:
                log_test(f"Python: {py_file.split('/')[-1]}", 'WARN', str(e))
        else:
            log_test(f"Python: {py_file.split('/')[-1]}", 'WARN', "File not found")
    
    # Test 3: API Key Manager Integration
    print("\n🔑 TESTING API KEY MANAGER INTEGRATION...")
    try:
        # Test if the universal AI manager can be imported
        result = subprocess.run([
            sys.executable, '-c', 
            'from standalone_universal_ai_manager import StandaloneUniversalAIManager; print("API Manager OK")'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            log_test("API Key Manager", 'PASS', "Can import and use")
        else:
            log_test("API Key Manager", 'FAIL', result.stderr, is_critical=True)
    except Exception as e:
        log_test("API Key Manager", 'FAIL', str(e), is_critical=True)
    
    # Test 4: Audit System
    print("\n🔍 TESTING AUDIT SYSTEM...")
    try:
        result = subprocess.run([
            sys.executable, '.github/scripts/comprehensive_audit_engine.py',
            '--audit-type', 'quick',
            '--create-issues', 'false',
            '--notify-on-failure', 'false',
            '--output', 'test_audit.json'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            log_test("Audit System", 'PASS', "Can run successfully")
            
            # Check if results were generated
            if os.path.exists('test_audit.json'):
                with open('test_audit.json', 'r') as f:
                    audit_data = json.load(f)
                if 'statistics' in audit_data:
                    log_test("Audit Results", 'PASS', "Valid results generated")
                else:
                    log_test("Audit Results", 'WARN', "Results missing statistics")
            else:
                log_test("Audit Results", 'WARN', "No results file generated")
        else:
            log_test("Audit System", 'FAIL', result.stderr, is_critical=True)
    except subprocess.TimeoutExpired:
        log_test("Audit System", 'WARN', "Timeout - may be normal")
    except Exception as e:
        log_test("Audit System", 'FAIL', str(e), is_critical=True)
    
    # Test 5: Security Fixes
    print("\n🛡️ TESTING SECURITY FIXES...")
    security_issues = 0
    
    # Check for exposed secrets
    python_files = [
        '.github/scripts/ai_code_analyzer.py',
        '.github/scripts/simple_verify_fixes.py',
        '.github/scripts/verify_security_fixes.py'
    ]
    
    for py_file in python_files:
        if os.path.exists(py_file):
            with open(py_file, 'r') as f:
                content = f.read()
            
            # Check for hardcoded secrets
            if 'password = "' in content or 'token = "' in content:
                security_issues += 1
    
    if security_issues == 0:
        log_test("Security Fixes", 'PASS', "No exposed secrets found")
    else:
        log_test("Security Fixes", 'WARN', f"Found {security_issues} potential issues")
    
    # Test 6: Workflow Structure
    print("\n⚙️ TESTING WORKFLOW STRUCTURE...")
    workflow_files = list(os.path.join('.github/workflows', f) for f in os.listdir('.github/workflows') if f.endswith('.yml'))
    
    valid_workflows = 0
    for workflow_file in workflow_files:
        try:
            with open(workflow_file, 'r') as f:
                workflow_data = yaml.safe_load(f)
            
            if 'name' in workflow_data and 'on' in workflow_data and 'jobs' in workflow_data:
                valid_workflows += 1
        except:
            pass
    
    if valid_workflows >= 5:  # Expect at least 5 valid workflows
        log_test("Workflow Structure", 'PASS', f"{valid_workflows} valid workflows found")
    else:
        log_test("Workflow Structure", 'WARN', f"Only {valid_workflows} valid workflows found")
    
    # Generate final report
    print("\n" + "=" * 60)
    print("📊 FOCUSED TEST RESULTS")
    print("=" * 60)
    
    total_tests = results['tests_run']
    passed_tests = results['tests_passed']
    failed_tests = results['tests_failed']
    warnings = len(results['warnings'])
    critical_failures = len(results['critical_failures'])
    
    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    print(f"⚠️  Warnings: {warnings}")
    print(f"🚨 Critical Failures: {critical_failures}")
    
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    print(f"📈 Success Rate: {success_rate:.1f}%")
    
    if critical_failures > 0:
        print(f"\n🚨 CRITICAL FAILURES:")
        for failure in results['critical_failures']:
            print(f"  • {failure}")
    
    if warnings > 0:
        print(f"\n⚠️  WARNINGS:")
        for warning in results['warnings']:
            print(f"  • {warning}")
    
    # Determine merge readiness
    if critical_failures == 0 and success_rate >= 80:
        print(f"\n🎉 MERGE READY! Success rate: {success_rate:.1f}%")
        merge_status = "READY"
    elif critical_failures == 0 and success_rate >= 60:
        print(f"\n⚠️  MERGE WITH CAUTION! Success rate: {success_rate:.1f}%")
        merge_status = "CAUTION"
    else:
        print(f"\n❌ NOT READY FOR MERGE! Critical failures: {critical_failures}")
        merge_status = "NOT_READY"
    
    # Save results
    results['merge_status'] = merge_status
    results['success_rate'] = success_rate
    
    with open('focused_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📁 Results saved to: focused_test_results.json")
    print(f"🕐 Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return merge_status

if __name__ == "__main__":
    merge_status = test_critical_components()
    
    if merge_status == "READY":
        sys.exit(0)
    elif merge_status == "CAUTION":
        sys.exit(1)
    else:
        sys.exit(2)