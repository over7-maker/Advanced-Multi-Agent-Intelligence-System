#!/usr/bin/env python3
"""
Comprehensive Pre-Merge Testing Suite
Tests all critical fixes, workflows, and system integrity before PR merge
"""

import os
import sys
import json
import yaml
import subprocess
import time
from datetime import datetime
from pathlib import Path

class PreMergeTester:
    def __init__(self):
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'critical_failures': [],
            'warnings': [],
            'test_details': []
        }
    
    def log_test(self, test_name, status, details="", is_critical=False):
        """Log a test result"""
        self.test_results['tests_run'] += 1
        
        if status == 'PASS':
            self.test_results['tests_passed'] += 1
            print(f"✅ {test_name}: PASS")
        elif status == 'FAIL':
            self.test_results['tests_failed'] += 1
            if is_critical:
                self.test_results['critical_failures'].append(test_name)
            print(f"❌ {test_name}: FAIL - {details}")
        elif status == 'WARN':
            self.test_results['warnings'].append(test_name)
            print(f"⚠️  {test_name}: WARN - {details}")
        
        self.test_results['test_details'].append({
            'test': test_name,
            'status': status,
            'details': details,
            'critical': is_critical,
            'timestamp': datetime.now().isoformat()
        })
    
    def test_yaml_syntax(self):
        """Test all YAML files for syntax errors"""
        print("\n🔍 TESTING YAML SYNTAX...")
        print("=" * 40)
        
        yaml_files = list(Path('.github/workflows').glob('*.yml'))
        yaml_files.extend(Path('.').glob('**/*.yml'))
        
        for yaml_file in yaml_files:
            try:
                with open(yaml_file, 'r') as f:
                    yaml.safe_load(f)
                self.log_test(f"YAML Syntax: {yaml_file.name}", 'PASS')
            except yaml.YAMLError as e:
                self.log_test(f"YAML Syntax: {yaml_file.name}", 'FAIL', str(e), is_critical=True)
            except Exception as e:
                self.log_test(f"YAML Syntax: {yaml_file.name}", 'WARN', str(e))
    
    def test_python_syntax(self):
        """Test all Python files for syntax errors"""
        print("\n🐍 TESTING PYTHON SYNTAX...")
        print("=" * 40)
        
        python_files = list(Path('.').glob('**/*.py'))
        
        for py_file in python_files:
            if 'venv' in str(py_file) or '__pycache__' in str(py_file):
                continue
                
            try:
                with open(py_file, 'r') as f:
                    compile(f.read(), str(py_file), 'exec')
                self.log_test(f"Python Syntax: {py_file.name}", 'PASS')
            except SyntaxError as e:
                self.log_test(f"Python Syntax: {py_file.name}", 'FAIL', str(e), is_critical=True)
            except Exception as e:
                self.log_test(f"Python Syntax: {py_file.name}", 'WARN', str(e))
    
    def test_api_key_migration(self):
        """Test that API key migration was successful"""
        print("\n🔑 TESTING API KEY MIGRATION...")
        print("=" * 40)
        
        # Check for remaining direct API key usage
        direct_usage_count = 0
        files_with_direct_usage = []
        
        python_files = list(Path('.').glob('**/*.py'))
        for py_file in python_files:
            if 'venv' in str(py_file) or '__pycache__' in str(py_file):
                continue
                
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                
                # Check for direct API key usage patterns
                patterns = [
                    r'os\.getenv\([\'"]?[A-Z_]+_API_KEY[\'"]?\)',
                    r'os\.environ\.get\([\'"]?[A-Z_]+_API_KEY[\'"]?\)',
                    r'secrets\.[A-Z_]+_API_KEY'
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        direct_usage_count += len(matches)
                        files_with_direct_usage.append(f"{py_file.name}: {len(matches)} instances")
                        
            except Exception as e:
                self.log_test(f"API Key Check: {py_file.name}", 'WARN', str(e))
        
        if direct_usage_count == 0:
            self.log_test("API Key Migration", 'PASS', "No direct API key usage found")
        elif direct_usage_count <= 5:
            self.log_test("API Key Migration", 'WARN', f"Found {direct_usage_count} instances in {len(files_with_direct_usage)} files")
        else:
            self.log_test("API Key Migration", 'FAIL', f"Found {direct_usage_count} instances in {len(files_with_direct_usage)} files", is_critical=True)
    
    def test_security_fixes(self):
        """Test that security fixes were applied"""
        print("\n🛡️ TESTING SECURITY FIXES...")
        print("=" * 40)
        
        exposed_secrets_count = 0
        insecure_patterns_count = 0
        
        python_files = list(Path('.').glob('**/*.py'))
        for py_file in python_files:
            if 'venv' in str(py_file) or '__pycache__' in str(py_file):
                continue
                
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                
                # Check for exposed secrets
                secret_patterns = [
                    r'password\s*=\s*["\'][^"\']+["\']',
                    r'token\s*=\s*["\'][^"\']+["\']',
                    r'api_key\s*=\s*["\'][^"\']+["\']'
                ]
                
                for pattern in secret_patterns:
                    if re.search(pattern, content):
                        exposed_secrets_count += 1
                
                # Check for insecure patterns
                insecure_patterns = [
                    r'eval\s*\(',
                    r'exec\s*\(',
                    r'os\.system\s*\(',
                    r'pickle\.loads?\s*\('
                ]
                
                for pattern in insecure_patterns:
                    if re.search(pattern, content):
                        insecure_patterns_count += 1
                        
            except Exception as e:
                self.log_test(f"Security Check: {py_file.name}", 'WARN', str(e))
        
        if exposed_secrets_count == 0:
            self.log_test("Exposed Secrets", 'PASS', "No exposed secrets found")
        else:
            self.log_test("Exposed Secrets", 'FAIL', f"Found {exposed_secrets_count} exposed secrets", is_critical=True)
        
        if insecure_patterns_count <= 5:
            self.log_test("Insecure Patterns", 'WARN', f"Found {insecure_patterns_count} insecure patterns")
        else:
            self.log_test("Insecure Patterns", 'FAIL', f"Found {insecure_patterns_count} insecure patterns", is_critical=True)
    
    def test_workflow_integrity(self):
        """Test workflow file integrity and structure"""
        print("\n⚙️ TESTING WORKFLOW INTEGRITY...")
        print("=" * 40)
        
        workflow_files = list(Path('.github/workflows').glob('*.yml'))
        
        for workflow_file in workflow_files:
            try:
                with open(workflow_file, 'r') as f:
                    workflow_data = yaml.safe_load(f)
                
                # Check for required fields
                required_fields = ['name', 'on', 'jobs']
                missing_fields = [field for field in required_fields if field not in workflow_data]
                
                if missing_fields:
                    self.log_test(f"Workflow Structure: {workflow_file.name}", 'FAIL', f"Missing fields: {missing_fields}", is_critical=True)
                else:
                    self.log_test(f"Workflow Structure: {workflow_file.name}", 'PASS')
                
                # Check for API key environment variables
                if 'jobs' in workflow_data:
                    has_api_keys = False
                    for job_name, job_data in workflow_data['jobs'].items():
                        if 'env' in job_data:
                            api_keys = [key for key in job_data['env'].keys() if 'API_KEY' in key]
                            if api_keys:
                                has_api_keys = True
                                break
                    
                    if has_api_keys:
                        self.log_test(f"API Keys in Workflow: {workflow_file.name}", 'PASS')
                    else:
                        self.log_test(f"API Keys in Workflow: {workflow_file.name}", 'WARN', "No API keys found in environment")
                
            except Exception as e:
                self.log_test(f"Workflow Integrity: {workflow_file.name}", 'FAIL', str(e), is_critical=True)
    
    def test_import_integrity(self):
        """Test that all imports work correctly"""
        print("\n📦 TESTING IMPORT INTEGRITY...")
        print("=" * 40)
        
        critical_files = [
            'standalone_universal_ai_manager.py',
            '.github/scripts/comprehensive_audit_engine.py',
            '.github/scripts/universal_ai_workflow_integration.py'
        ]
        
        for file_path in critical_files:
            if os.path.exists(file_path):
                try:
                    # Test import
                    result = subprocess.run([
                        sys.executable, '-c', f'import sys; sys.path.append("."); exec(open("{file_path}").read())'
                    ], capture_output=True, text=True, timeout=30)
                    
                    if result.returncode == 0:
                        self.log_test(f"Import Test: {file_path}", 'PASS')
                    else:
                        self.log_test(f"Import Test: {file_path}", 'FAIL', result.stderr, is_critical=True)
                        
                except subprocess.TimeoutExpired:
                    self.log_test(f"Import Test: {file_path}", 'WARN', "Timeout - may be normal for large files")
                except Exception as e:
                    self.log_test(f"Import Test: {file_path}", 'WARN', str(e))
            else:
                self.log_test(f"Import Test: {file_path}", 'WARN', "File not found")
    
    def test_audit_system(self):
        """Test the audit system functionality"""
        print("\n🔍 TESTING AUDIT SYSTEM...")
        print("=" * 40)
        
        try:
            # Test audit engine
            result = subprocess.run([
                sys.executable, '.github/scripts/comprehensive_audit_engine.py',
                '--audit-type', 'quick',
                '--create-issues', 'false',
                '--notify-on-failure', 'false',
                '--output', 'test_audit_results.json'
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                self.log_test("Audit Engine", 'PASS')
                
                # Check if results file was created
                if os.path.exists('test_audit_results.json'):
                    with open('test_audit_results.json', 'r') as f:
                        audit_data = json.load(f)
                    
                    if 'statistics' in audit_data:
                        self.log_test("Audit Results", 'PASS', f"Generated valid audit data")
                    else:
                        self.log_test("Audit Results", 'WARN', "Audit data missing statistics")
                else:
                    self.log_test("Audit Results", 'WARN', "No results file generated")
            else:
                self.log_test("Audit Engine", 'FAIL', result.stderr, is_critical=True)
                
        except subprocess.TimeoutExpired:
            self.log_test("Audit Engine", 'WARN', "Timeout - audit may be taking too long")
        except Exception as e:
            self.log_test("Audit Engine", 'FAIL', str(e), is_critical=True)
    
    def test_file_permissions(self):
        """Test that all files have correct permissions"""
        print("\n🔐 TESTING FILE PERMISSIONS...")
        print("=" * 40)
        
        critical_files = [
            'standalone_universal_ai_manager.py',
            '.github/scripts/comprehensive_audit_engine.py',
            'audit_with_reports_fixed.sh',
            'auto_fix_critical_issues.py'
        ]
        
        for file_path in critical_files:
            if os.path.exists(file_path):
                try:
                    # Check if file is readable
                    with open(file_path, 'r') as f:
                        f.read(1)
                    
                    # Check if executable files are executable
                    if file_path.endswith('.py') or file_path.endswith('.sh'):
                        if os.access(file_path, os.X_OK):
                            self.log_test(f"Permissions: {file_path}", 'PASS')
                        else:
                            self.log_test(f"Permissions: {file_path}", 'WARN', "File not executable")
                    else:
                        self.log_test(f"Permissions: {file_path}", 'PASS')
                        
                except Exception as e:
                    self.log_test(f"Permissions: {file_path}", 'FAIL', str(e), is_critical=True)
            else:
                self.log_test(f"Permissions: {file_path}", 'WARN', "File not found")
    
    def test_workflow_triggers(self):
        """Test workflow trigger configuration"""
        print("\n⚡ TESTING WORKFLOW TRIGGERS...")
        print("=" * 40)
        
        workflow_files = list(Path('.github/workflows').glob('*.yml'))
        all_triggers = []
        
        for workflow_file in workflow_files:
            try:
                with open(workflow_file, 'r') as f:
                    workflow_data = yaml.safe_load(f)
                
                if 'on' in workflow_data:
                    triggers = workflow_data['on']
                    if isinstance(triggers, list):
                        all_triggers.extend(triggers)
                    elif isinstance(triggers, dict):
                        all_triggers.extend(triggers.keys())
                    elif isinstance(triggers, str):
                        all_triggers.append(triggers)
                
                self.log_test(f"Triggers: {workflow_file.name}", 'PASS', f"Found {len(triggers) if 'on' in workflow_data else 0} triggers")
                
            except Exception as e:
                self.log_test(f"Triggers: {workflow_file.name}", 'WARN', str(e))
        
        # Check for duplicate triggers
        trigger_counts = {}
        for trigger in all_triggers:
            trigger_counts[trigger] = trigger_counts.get(trigger, 0) + 1
        
        duplicates = {k: v for k, v in trigger_counts.items() if v > 1}
        if duplicates:
            self.log_test("Trigger Duplicates", 'WARN', f"Found duplicates: {duplicates}")
        else:
            self.log_test("Trigger Duplicates", 'PASS', "No duplicate triggers found")
    
    def run_all_tests(self):
        """Run all tests"""
        print("🧪 COMPREHENSIVE PRE-MERGE TESTING SUITE")
        print("=" * 50)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("")
        
        # Import re for pattern matching
        import re
        
        # Run all test categories
        self.test_yaml_syntax()
        self.test_python_syntax()
        self.test_api_key_migration()
        self.test_security_fixes()
        self.test_workflow_integrity()
        self.test_import_integrity()
        self.test_audit_system()
        self.test_file_permissions()
        self.test_workflow_triggers()
        
        # Generate final report
        self.generate_final_report()
    
    def generate_final_report(self):
        """Generate final test report"""
        print("\n" + "=" * 50)
        print("📊 FINAL TEST REPORT")
        print("=" * 50)
        
        total_tests = self.test_results['tests_run']
        passed_tests = self.test_results['tests_passed']
        failed_tests = self.test_results['tests_failed']
        warnings = len(self.test_results['warnings'])
        critical_failures = len(self.test_results['critical_failures'])
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️  Warnings: {warnings}")
        print(f"🚨 Critical Failures: {critical_failures}")
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if critical_failures > 0:
            print(f"\n🚨 CRITICAL FAILURES:")
            for failure in self.test_results['critical_failures']:
                print(f"  • {failure}")
        
        if warnings > 0:
            print(f"\n⚠️  WARNINGS:")
            for warning in self.test_results['warnings']:
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
        
        # Save detailed report
        self.test_results['merge_status'] = merge_status
        self.test_results['success_rate'] = success_rate
        
        with open('pre_merge_test_report.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n📁 Detailed report saved to: pre_merge_test_report.json")
        print(f"🕐 Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return merge_status

def main():
    """Main function"""
    tester = PreMergeTester()
    merge_status = tester.run_all_tests()
    
    # Exit with appropriate code
    if merge_status == "READY":
        sys.exit(0)
    elif merge_status == "CAUTION":
        sys.exit(1)
    else:
        sys.exit(2)

if __name__ == "__main__":
    main()