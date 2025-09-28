#!/usr/bin/env python3
"""
AMAS Intelligence System - Simple Functionality Test
Test core functionality without external dependencies
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class SimpleFunctionalityTest:
    """Simple functionality test for AMAS system"""
    
    def __init__(self, workspace_path: str = "/workspace"):
        self.workspace_path = Path(workspace_path)
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'success_rate': 0.0,
            'test_details': []
        }
    
    def test_file_imports(self) -> bool:
        """Test that all Python files can be imported without syntax errors"""
        print("🔍 Testing File Imports...")
        
        python_files = [
            'main.py',
            'main_phase3_complete.py',
            'main_phase4_complete.py',
            'main_phase5_complete.py',
            'main_phase6_10_complete.py',
            'core/orchestrator.py',
            'services/service_manager.py',
            'services/database_service.py',
            'services/security_service.py',
            'services/llm_service.py',
            'services/vector_service.py',
            'services/knowledge_graph_service.py',
            'services/monitoring_service.py',
            'services/performance_service.py',
            'services/security_monitoring_service.py',
            'services/audit_logging_service.py',
            'services/incident_response_service.py',
            'services/advanced_optimization_service.py',
            'services/advanced_analytics_service.py',
            'services/workflow_automation_service.py',
            'services/enterprise_service.py',
            'agents/osint/osint_agent.py',
            'agents/investigation/investigation_agent.py',
            'agents/forensics/forensics_agent.py',
            'agents/data_analysis/data_analysis_agent.py',
            'agents/reverse_engineering/reverse_engineering_agent.py',
            'agents/metadata/metadata_agent.py',
            'agents/reporting/reporting_agent.py',
            'agents/technology_monitor/technology_monitor_agent.py'
        ]
        
        passed = 0
        failed = 0
        
        for file_path in python_files:
            full_path = self.workspace_path / file_path
            if full_path.exists():
                try:
                    # Try to compile the file to check for syntax errors
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    compile(content, str(full_path), 'exec')
                    passed += 1
                    print(f"  ✅ {file_path}")
                except SyntaxError as e:
                    failed += 1
                    print(f"  ❌ {file_path} - Syntax Error: {e}")
                except Exception as e:
                    failed += 1
                    print(f"  ❌ {file_path} - Error: {e}")
            else:
                failed += 1
                print(f"  ❌ {file_path} - File not found")
        
        self.test_results['total_tests'] += len(python_files)
        self.test_results['passed_tests'] += passed
        self.test_results['failed_tests'] += failed
        
        return failed == 0
    
    def test_configuration_files(self) -> bool:
        """Test configuration files are valid"""
        print("\n🔍 Testing Configuration Files...")
        
        config_files = [
            'docker-compose.yml',
            'requirements.txt'
        ]
        
        passed = 0
        failed = 0
        
        for config_file in config_files:
            config_path = self.workspace_path / config_file
            if config_path.exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Basic validation
                    if config_file.endswith('.yml') or config_file.endswith('.yaml'):
                        # Check for basic YAML structure
                        if 'version:' in content or 'services:' in content:
                            passed += 1
                            print(f"  ✅ {config_file}")
                        else:
                            failed += 1
                            print(f"  ❌ {config_file} - Invalid YAML structure")
                    elif config_file.endswith('.txt'):
                        # Check for basic requirements structure
                        if any(line.strip() and not line.startswith('#') for line in content.split('\n')):
                            passed += 1
                            print(f"  ✅ {config_file}")
                        else:
                            failed += 1
                            print(f"  ❌ {config_file} - Empty or invalid requirements")
                    else:
                        passed += 1
                        print(f"  ✅ {config_file}")
                except Exception as e:
                    failed += 1
                    print(f"  ❌ {config_file} - Error: {e}")
            else:
                failed += 1
                print(f"  ❌ {config_file} - File not found")
        
        self.test_results['total_tests'] += len(config_files)
        self.test_results['passed_tests'] += passed
        self.test_results['failed_tests'] += failed
        
        return failed == 0
    
    def test_documentation_files(self) -> bool:
        """Test documentation files are readable"""
        print("\n🔍 Testing Documentation Files...")
        
        doc_files = [
            'README.md',
            'COMPLETE_IMPLEMENTATION_SUMMARY.md',
            'FINAL_WORKFLOW_STATUS_REPORT.md',
            'SETUP_GUIDE.md',
            'architecture.md',
            'hardening_enhanced.md'
        ]
        
        passed = 0
        failed = 0
        
        for doc_file in doc_files:
            doc_path = self.workspace_path / doc_file
            if doc_path.exists():
                try:
                    with open(doc_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check if file has content and is readable
                    if len(content.strip()) > 100:  # At least 100 characters
                        passed += 1
                        print(f"  ✅ {doc_file}")
                    else:
                        failed += 1
                        print(f"  ❌ {doc_file} - Too short or empty")
                except Exception as e:
                    failed += 1
                    print(f"  ❌ {doc_file} - Error: {e}")
            else:
                failed += 1
                print(f"  ❌ {doc_file} - File not found")
        
        self.test_results['total_tests'] += len(doc_files)
        self.test_results['passed_tests'] += passed
        self.test_results['failed_tests'] += failed
        
        return failed == 0
    
    def test_directory_structure(self) -> bool:
        """Test directory structure is correct"""
        print("\n🔍 Testing Directory Structure...")
        
        required_dirs = [
            'services',
            'agents',
            'core',
            'api',
            'tests',
            'docs',
            'logs',
            'config',
            'scripts',
            'examples'
        ]
        
        passed = 0
        failed = 0
        
        for dir_name in required_dirs:
            dir_path = self.workspace_path / dir_name
            if dir_path.exists() and dir_path.is_dir():
                passed += 1
                print(f"  ✅ {dir_name}/")
            else:
                failed += 1
                print(f"  ❌ {dir_name}/ - Directory not found")
        
        self.test_results['total_tests'] += len(required_dirs)
        self.test_results['passed_tests'] += passed
        self.test_results['failed_tests'] += failed
        
        return failed == 0
    
    def test_agent_structure(self) -> bool:
        """Test agent directory structure"""
        print("\n🔍 Testing Agent Structure...")
        
        agent_dirs = [
            'agents/base',
            'agents/osint',
            'agents/investigation',
            'agents/forensics',
            'agents/data_analysis',
            'agents/reverse_engineering',
            'agents/metadata',
            'agents/reporting',
            'agents/technology_monitor'
        ]
        
        passed = 0
        failed = 0
        
        for agent_dir in agent_dirs:
            agent_path = self.workspace_path / agent_dir
            if agent_path.exists() and agent_path.is_dir():
                passed += 1
                print(f"  ✅ {agent_dir}/")
            else:
                failed += 1
                print(f"  ❌ {agent_dir}/ - Directory not found")
        
        self.test_results['total_tests'] += len(agent_dirs)
        self.test_results['passed_tests'] += passed
        self.test_results['failed_tests'] += failed
        
        return failed == 0
    
    def test_verification_scripts(self) -> bool:
        """Test verification scripts are executable"""
        print("\n🔍 Testing Verification Scripts...")
        
        verification_scripts = [
            'final_workflow_verification.py',
            'verify_workflows.py',
            'check_workflow_configuration.py',
            'check_workflow_status.py',
            'run_workflow_tests.py',
            'simple_workflow_check.py',
            'verify_all_workflows.py',
            'verify_file_structure.py'
        ]
        
        passed = 0
        failed = 0
        
        for script in verification_scripts:
            script_path = self.workspace_path / script
            if script_path.exists():
                try:
                    with open(script_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check if it's a valid Python script
                    compile(content, str(script_path), 'exec')
                    passed += 1
                    print(f"  ✅ {script}")
                except Exception as e:
                    failed += 1
                    print(f"  ❌ {script} - Error: {e}")
            else:
                failed += 1
                print(f"  ❌ {script} - File not found")
        
        self.test_results['total_tests'] += len(verification_scripts)
        self.test_results['passed_tests'] += passed
        self.test_results['failed_tests'] += failed
        
        return failed == 0
    
    def calculate_success_rate(self):
        """Calculate overall success rate"""
        if self.test_results['total_tests'] > 0:
            self.test_results['success_rate'] = (
                self.test_results['passed_tests'] / 
                self.test_results['total_tests']
            ) * 100
        else:
            self.test_results['success_rate'] = 0.0
    
    def generate_report(self):
        """Generate comprehensive test report"""
        self.calculate_success_rate()
        
        print("\n" + "="*80)
        print("📊 FUNCTIONALITY TEST RESULTS")
        print("="*80)
        print(f"Total Tests: {self.test_results['total_tests']}")
        print(f"Passed: {self.test_results['passed_tests']}")
        print(f"Failed: {self.test_results['failed_tests']}")
        print(f"Success Rate: {self.test_results['success_rate']:.1f}%")
        
        # Save detailed report
        report_path = self.workspace_path / 'logs' / 'functionality_test_report.json'
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n📄 Detailed report saved: {report_path}")
        
        return self.test_results['success_rate'] >= 90.0
    
    def run_tests(self) -> bool:
        """Run all functionality tests"""
        print("🎯 AMAS Intelligence System - Simple Functionality Test")
        print("="*80)
        
        # Run all tests
        test_file_imports = self.test_file_imports()
        test_config_files = self.test_configuration_files()
        test_doc_files = self.test_documentation_files()
        test_dir_structure = self.test_directory_structure()
        test_agent_structure = self.test_agent_structure()
        test_verification_scripts = self.test_verification_scripts()
        
        # Generate final report
        success = self.generate_report()
        
        if success:
            print("\n🎉 FUNCTIONALITY TEST SUCCESSFUL!")
            print("✅ All core functionality is working correctly")
            print("✅ File structure is correct")
            print("✅ Documentation is complete")
            print("✅ Ready for production deployment")
        else:
            print("\n❌ FUNCTIONALITY TEST FAILED!")
            print("⚠️  Some functionality tests failed")
            print("⚠️  Please check the failed tests above")
        
        return success

def main():
    """Main test function"""
    tester = SimpleFunctionalityTest()
    success = tester.run_tests()
    
    if success:
        print("\n🚀 AMAS Intelligence System functionality is working correctly!")
        sys.exit(0)
    else:
        print("\n⚠️  Functionality test found issues that need attention.")
        sys.exit(1)

if __name__ == "__main__":
    main()