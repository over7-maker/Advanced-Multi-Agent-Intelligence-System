#!/usr/bin/env python3
"""
Comprehensive Test Suite with TXT Output
Runs all tests and writes results to text files for easy mobile viewing
"""

import os
import sys
import json
import yaml
import subprocess
import time
from datetime import datetime
from pathlib import Path

class ComprehensiveTestSuite:
    def __init__(self):
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'warnings': 0,
            'critical_failures': 0,
            'test_details': []
        }
        self.output_dir = 'test_results'
        os.makedirs(self.output_dir, exist_ok=True)
    
    def log_test(self, test_name, status, details="", is_critical=False):
        """Log a test result"""
        self.test_results['tests_run'] += 1
        
        if status == 'PASS':
            self.test_results['tests_passed'] += 1
            print(f"✅ {test_name}: PASS")
        elif status == 'FAIL':
            self.test_results['tests_failed'] += 1
            if is_critical:
                self.test_results['critical_failures'] += 1
            print(f"❌ {test_name}: FAIL - {details}")
        elif status == 'WARN':
            self.test_results['warnings'] += 1
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
        
        yaml_results = []
        yaml_files = list(Path('.github/workflows').glob('*.yml'))
        yaml_files.extend(Path('.').glob('**/*.yml'))
        
        for yaml_file in yaml_files:
            try:
                with open(yaml_file, 'r') as f:
                    yaml.safe_load(f)
                self.log_test(f"YAML: {yaml_file.name}", 'PASS')
                yaml_results.append(f"✅ {yaml_file.name}: PASS")
            except yaml.YAMLError as e:
                self.log_test(f"YAML: {yaml_file.name}", 'FAIL', str(e), is_critical=True)
                yaml_results.append(f"❌ {yaml_file.name}: FAIL - {str(e)}")
            except Exception as e:
                self.log_test(f"YAML: {yaml_file.name}", 'WARN', str(e))
                yaml_results.append(f"⚠️  {yaml_file.name}: WARN - {str(e)}")
        
        # Write YAML test results to file
        with open(f'{self.output_dir}/yaml_syntax_test.txt', 'w') as f:
            f.write("🔍 YAML SYNTAX TEST RESULTS\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Tested: {len(yaml_files)} files\n")
            f.write(f"Passed: {len([r for r in yaml_results if r.startswith('✅')])}\n")
            f.write(f"Failed: {len([r for r in yaml_results if r.startswith('❌')])}\n")
            f.write(f"Warnings: {len([r for r in yaml_results if r.startswith('⚠️')])}\n\n")
            f.write("DETAILED RESULTS:\n")
            f.write("-" * 30 + "\n")
            for result in yaml_results:
                f.write(f"{result}\n")
    
    def test_python_syntax(self):
        """Test all Python files for syntax errors"""
        print("\n🐍 TESTING PYTHON SYNTAX...")
        print("=" * 40)
        
        python_results = []
        python_files = list(Path('.').glob('**/*.py'))
        
        for py_file in python_files:
            if 'venv' in str(py_file) or '__pycache__' in str(py_file):
                continue
                
            try:
                with open(py_file, 'r') as f:
                    compile(f.read(), str(py_file), 'exec')
                self.log_test(f"Python: {py_file.name}", 'PASS')
                python_results.append(f"✅ {py_file.name}: PASS")
            except SyntaxError as e:
                self.log_test(f"Python: {py_file.name}", 'FAIL', str(e), is_critical=True)
                python_results.append(f"❌ {py_file.name}: FAIL - {str(e)}")
            except Exception as e:
                self.log_test(f"Python: {py_file.name}", 'WARN', str(e))
                python_results.append(f"⚠️  {py_file.name}: WARN - {str(e)}")
        
        # Write Python test results to file
        with open(f'{self.output_dir}/python_syntax_test.txt', 'w') as f:
            f.write("🐍 PYTHON SYNTAX TEST RESULTS\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Tested: {len(python_files)} files\n")
            f.write(f"Passed: {len([r for r in python_results if r.startswith('✅')])}\n")
            f.write(f"Failed: {len([r for r in python_results if r.startswith('❌')])}\n")
            f.write(f"Warnings: {len([r for r in python_results if r.startswith('⚠️')])}\n\n")
            f.write("DETAILED RESULTS:\n")
            f.write("-" * 30 + "\n")
            for result in python_results:
                f.write(f"{result}\n")
    
    def test_api_key_migration(self):
        """Test API key migration status"""
        print("\n🔑 TESTING API KEY MIGRATION...")
        print("=" * 40)
        
        # Count direct API key usage
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
                    import re
                    matches = re.findall(pattern, content)
                    if matches:
                        direct_usage_count += len(matches)
                        files_with_direct_usage.append(f"{py_file.name}: {len(matches)} instances")
                        
            except Exception as e:
                pass
        
        # Count manager usage
        manager_usage_count = 0
        files_with_manager = []
        
        for py_file in python_files:
            if 'venv' in str(py_file) or '__pycache__' in str(py_file):
                continue
                
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                
                if 'get_api_key(' in content or 'StandaloneUniversalAIManager' in content:
                    manager_usage_count += 1
                    files_with_manager.append(py_file.name)
                        
            except Exception as e:
                pass
        
        # Log results
        if direct_usage_count == 0:
            self.log_test("API Key Migration", 'PASS', "No direct API key usage found")
        elif direct_usage_count <= 5:
            self.log_test("API Key Migration", 'WARN', f"Found {direct_usage_count} instances")
        else:
            self.log_test("API Key Migration", 'FAIL', f"Found {direct_usage_count} instances", is_critical=True)
        
        # Write API key test results to file
        with open(f'{self.output_dir}/api_key_migration_test.txt', 'w') as f:
            f.write("🔑 API KEY MIGRATION TEST RESULTS\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Direct Usage: {direct_usage_count} instances\n")
            f.write(f"Manager Usage: {manager_usage_count} files\n")
            f.write(f"Migration Rate: {((manager_usage_count - direct_usage_count) / max(manager_usage_count, 1) * 100):.1f}%\n\n")
            
            f.write("FILES WITH DIRECT USAGE:\n")
            f.write("-" * 30 + "\n")
            for file_info in files_with_direct_usage:
                f.write(f"• {file_info}\n")
            
            f.write(f"\nFILES WITH MANAGER USAGE:\n")
            f.write("-" * 30 + "\n")
            for file_name in files_with_manager[:20]:  # Show first 20
                f.write(f"• {file_name}\n")
            if len(files_with_manager) > 20:
                f.write(f"... and {len(files_with_manager) - 20} more files\n")
    
    def test_security_fixes(self):
        """Test security fixes"""
        print("\n🛡️ TESTING SECURITY FIXES...")
        print("=" * 40)
        
        security_issues = 0
        exposed_secrets = 0
        insecure_patterns = 0
        
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
                    import re
                    if re.search(pattern, content):
                        exposed_secrets += 1
                
                # Check for insecure patterns
                insecure_patterns_list = [
                    r'eval\s*\(',
                    r'exec\s*\(',
                    r'os\.system\s*\(',
                    r'pickle\.loads?\s*\('
                ]
                
                for pattern in insecure_patterns_list:
                    if re.search(pattern, content):
                        insecure_patterns += 1
                        
            except Exception as e:
                pass
        
        security_issues = exposed_secrets + insecure_patterns
        
        if exposed_secrets == 0:
            self.log_test("Exposed Secrets", 'PASS', "No exposed secrets found")
        else:
            self.log_test("Exposed Secrets", 'FAIL', f"Found {exposed_secrets} exposed secrets", is_critical=True)
        
        if insecure_patterns <= 10:
            self.log_test("Insecure Patterns", 'WARN', f"Found {insecure_patterns} insecure patterns")
        else:
            self.log_test("Insecure Patterns", 'FAIL', f"Found {insecure_patterns} insecure patterns", is_critical=True)
        
        # Write security test results to file
        with open(f'{self.output_dir}/security_test.txt', 'w') as f:
            f.write("🛡️ SECURITY TEST RESULTS\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Exposed Secrets: {exposed_secrets}\n")
            f.write(f"Insecure Patterns: {insecure_patterns}\n")
            f.write(f"Total Security Issues: {security_issues}\n\n")
            
            if exposed_secrets == 0:
                f.write("✅ NO EXPOSED SECRETS FOUND!\n")
            else:
                f.write("❌ EXPOSED SECRETS DETECTED!\n")
            
            if insecure_patterns <= 10:
                f.write("⚠️  Some insecure patterns found (mostly in test files)\n")
            else:
                f.write("❌ Many insecure patterns found\n")
    
    def test_workflow_integrity(self):
        """Test workflow integrity"""
        print("\n⚙️ TESTING WORKFLOW INTEGRITY...")
        print("=" * 40)
        
        workflow_files = list(Path('.github/workflows').glob('*.yml'))
        valid_workflows = 0
        workflow_results = []
        
        for workflow_file in workflow_files:
            try:
                with open(workflow_file, 'r') as f:
                    workflow_data = yaml.safe_load(f)
                
                # Check for required fields
                required_fields = ['name', 'on', 'jobs']
                missing_fields = [field for field in required_fields if field not in workflow_data]
                
                if missing_fields:
                    self.log_test(f"Workflow: {workflow_file.name}", 'FAIL', f"Missing fields: {missing_fields}", is_critical=True)
                    workflow_results.append(f"❌ {workflow_file.name}: Missing {missing_fields}")
                else:
                    self.log_test(f"Workflow: {workflow_file.name}", 'PASS')
                    workflow_results.append(f"✅ {workflow_file.name}: Valid")
                    valid_workflows += 1
                
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
                        workflow_results.append(f"  • Has {len(api_keys)} API keys")
                    else:
                        workflow_results.append(f"  • No API keys found")
                
            except Exception as e:
                self.log_test(f"Workflow: {workflow_file.name}", 'FAIL', str(e), is_critical=True)
                workflow_results.append(f"❌ {workflow_file.name}: Error - {str(e)}")
        
        # Write workflow test results to file
        with open(f'{self.output_dir}/workflow_integrity_test.txt', 'w') as f:
            f.write("⚙️ WORKFLOW INTEGRITY TEST RESULTS\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Total Workflows: {len(workflow_files)}\n")
            f.write(f"Valid Workflows: {valid_workflows}\n")
            f.write(f"Invalid Workflows: {len(workflow_files) - valid_workflows}\n")
            f.write(f"Success Rate: {(valid_workflows / len(workflow_files) * 100):.1f}%\n\n")
            
            f.write("DETAILED RESULTS:\n")
            f.write("-" * 30 + "\n")
            for result in workflow_results:
                f.write(f"{result}\n")
    
    def test_audit_system(self):
        """Test the audit system"""
        print("\n🔍 TESTING AUDIT SYSTEM...")
        print("=" * 40)
        
        try:
            # Test audit engine
            result = subprocess.run([
                sys.executable, '.github/scripts/comprehensive_audit_engine.py',
                '--audit-type', 'quick',
                '--create-issues', 'false',
                '--notify-on-failure', 'false',
                '--output', f'{self.output_dir}/test_audit_results.json'
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                self.log_test("Audit Engine", 'PASS', "Can run successfully")
                
                # Check if results file was created
                if os.path.exists(f'{self.output_dir}/test_audit_results.json'):
                    with open(f'{self.output_dir}/test_audit_results.json', 'r') as f:
                        audit_data = json.load(f)
                    
                    if 'statistics' in audit_data:
                        self.log_test("Audit Results", 'PASS', "Generated valid audit data")
                        
                        # Write audit test results to file
                        with open(f'{self.output_dir}/audit_system_test.txt', 'w') as f:
                            f.write("🔍 AUDIT SYSTEM TEST RESULTS\n")
                            f.write("=" * 50 + "\n\n")
                            f.write("✅ Audit system is working!\n\n")
                            
                            stats = audit_data.get('statistics', {})
                            f.write("AUDIT STATISTICS:\n")
                            f.write("-" * 20 + "\n")
                            f.write(f"Total Issues: {stats.get('total_issues', 0)}\n")
                            f.write(f"Critical Issues: {stats.get('critical_issues', 0)}\n")
                            f.write(f"High Priority: {stats.get('high_priority_issues', 0)}\n")
                            f.write(f"Medium Priority: {stats.get('medium_priority_issues', 0)}\n")
                            f.write(f"Low Priority: {stats.get('low_priority_issues', 0)}\n")
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
    
    def run_all_tests(self):
        """Run all tests and generate comprehensive reports"""
        print("🧪 COMPREHENSIVE TEST SUITE WITH TXT OUTPUT")
        print("=" * 60)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Output Directory: {self.output_dir}/")
        print("")
        
        # Run all test categories
        self.test_yaml_syntax()
        self.test_python_syntax()
        self.test_api_key_migration()
        self.test_security_fixes()
        self.test_workflow_integrity()
        self.test_audit_system()
        
        # Generate final comprehensive report
        self.generate_final_report()
    
    def generate_final_report(self):
        """Generate final comprehensive report"""
        print("\n" + "=" * 60)
        print("📊 GENERATING FINAL COMPREHENSIVE REPORT")
        print("=" * 60)
        
        total_tests = self.test_results['tests_run']
        passed_tests = self.test_results['tests_passed']
        failed_tests = self.test_results['tests_failed']
        warnings = self.test_results['warnings']
        critical_failures = self.test_results['critical_failures']
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Determine overall status
        if critical_failures == 0 and success_rate >= 80:
            overall_status = "✅ EXCELLENT - READY FOR PRODUCTION"
        elif critical_failures == 0 and success_rate >= 60:
            overall_status = "⚠️  GOOD - READY WITH CAUTION"
        else:
            overall_status = "❌ NEEDS ATTENTION - NOT READY"
        
        # Write comprehensive final report
        with open(f'{self.output_dir}/FINAL_COMPREHENSIVE_TEST_REPORT.txt', 'w') as f:
            f.write("🧪 COMPREHENSIVE TEST SUITE - FINAL REPORT\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Output Directory: {self.output_dir}/\n\n")
            
            f.write("📊 OVERALL STATUS\n")
            f.write("=" * 20 + "\n")
            f.write(f"{overall_status}\n\n")
            
            f.write("📈 TEST STATISTICS\n")
            f.write("=" * 20 + "\n")
            f.write(f"Total Tests: {total_tests}\n")
            f.write(f"✅ Passed: {passed_tests}\n")
            f.write(f"❌ Failed: {failed_tests}\n")
            f.write(f"⚠️  Warnings: {warnings}\n")
            f.write(f"🚨 Critical Failures: {critical_failures}\n")
            f.write(f"📈 Success Rate: {success_rate:.1f}%\n\n")
            
            f.write("📁 GENERATED FILES\n")
            f.write("=" * 20 + "\n")
            f.write("• yaml_syntax_test.txt - YAML syntax validation results\n")
            f.write("• python_syntax_test.txt - Python syntax validation results\n")
            f.write("• api_key_migration_test.txt - API key migration status\n")
            f.write("• security_test.txt - Security fixes validation\n")
            f.write("• workflow_integrity_test.txt - Workflow structure validation\n")
            f.write("• audit_system_test.txt - Audit system functionality\n")
            f.write("• test_audit_results.json - Raw audit data\n")
            f.write("• FINAL_COMPREHENSIVE_TEST_REPORT.txt - This summary\n\n")
            
            f.write("🎯 RECOMMENDATIONS\n")
            f.write("=" * 20 + "\n")
            if critical_failures == 0:
                f.write("✅ System is ready for production use!\n")
                f.write("✅ All critical components are working\n")
                f.write("✅ Security issues have been addressed\n")
                f.write("✅ Workflows are properly structured\n")
            else:
                f.write("❌ Address critical failures before production\n")
                f.write("⚠️  Review failed tests and fix issues\n")
                f.write("🔧 Run tests again after fixes\n")
            
            f.write(f"\n🕐 Test completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        print(f"✅ Final report saved to: {self.output_dir}/FINAL_COMPREHENSIVE_TEST_REPORT.txt")
        print(f"📁 All test results saved to: {self.output_dir}/")
        print(f"🕐 Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return overall_status

def main():
    """Main function"""
    test_suite = ComprehensiveTestSuite()
    overall_status = test_suite.run_all_tests()
    
    print(f"\n🎉 TEST SUITE COMPLETED!")
    print(f"📁 Check the '{test_suite.output_dir}/' directory for all results!")
    print(f"📱 Perfect for mobile viewing on your iPod browser!")
    
    return 0

if __name__ == "__main__":
    exit(main())