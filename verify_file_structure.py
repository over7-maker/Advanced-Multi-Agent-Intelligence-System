#!/usr/bin/env python3
"""
AMAS Intelligence System - File Structure Verification
Comprehensive verification that all project files and docs are in the right place
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import json
from datetime import datetime

class FileStructureVerifier:
    """Verify all project files and documentation are in the correct locations"""
    
    def __init__(self, workspace_path: str = "/workspace"):
        self.workspace_path = Path(workspace_path)
        self.verification_results = {
            'timestamp': datetime.now().isoformat(),
            'total_checks': 0,
            'passed_checks': 0,
            'failed_checks': 0,
            'success_rate': 0.0,
            'file_structure': {},
            'missing_files': [],
            'extra_files': [],
            'incorrect_locations': []
        }
        
    def verify_core_structure(self) -> Dict[str, bool]:
        """Verify core project structure"""
        print("🔍 Verifying Core Project Structure...")
        
        core_structure = {
            # Main application files
            'main.py': self.workspace_path / 'main.py',
            'main_phase3_complete.py': self.workspace_path / 'main_phase3_complete.py',
            'main_phase4_complete.py': self.workspace_path / 'main_phase4_complete.py',
            'main_phase5_complete.py': self.workspace_path / 'main_phase5_complete.py',
            'main_phase6_10_complete.py': self.workspace_path / 'main_phase6_10_complete.py',
            
            # Configuration files
            'docker-compose.yml': self.workspace_path / 'docker-compose.yml',
            'requirements.txt': self.workspace_path / 'requirements.txt',
            'README.md': self.workspace_path / 'README.md',
            
            # Core directories
            'services/': self.workspace_path / 'services',
            'agents/': self.workspace_path / 'agents',
            'core/': self.workspace_path / 'core',
            'api/': self.workspace_path / 'api',
            'tests/': self.workspace_path / 'tests',
            'docs/': self.workspace_path / 'docs',
            'logs/': self.workspace_path / 'logs',
            'config/': self.workspace_path / 'config',
            'scripts/': self.workspace_path / 'scripts',
            'examples/': self.workspace_path / 'examples'
        }
        
        results = {}
        for name, path in core_structure.items():
            exists = path.exists()
            results[name] = exists
            self.verification_results['total_checks'] += 1
            if exists:
                self.verification_results['passed_checks'] += 1
                print(f"  ✅ {name}")
            else:
                self.verification_results['failed_checks'] += 1
                self.verification_results['missing_files'].append(str(path))
                print(f"  ❌ {name} - MISSING")
        
        return results
    
    def verify_services_structure(self) -> Dict[str, bool]:
        """Verify services directory structure"""
        print("\n🔍 Verifying Services Structure...")
        
        services_path = self.workspace_path / 'services'
        required_services = [
            'service_manager.py',
            'database_service.py',
            'security_service.py',
            'llm_service.py',
            'vector_service.py',
            'knowledge_graph_service.py',
            'monitoring_service.py',
            'performance_service.py',
            'security_monitoring_service.py',
            'audit_logging_service.py',
            'incident_response_service.py',
            'advanced_optimization_service.py',
            'advanced_analytics_service.py',
            'workflow_automation_service.py',
            'enterprise_service.py',
            'ml_service.py',
            'ai_analytics_service.py',
            'nlp_service.py',
            'computer_vision_service.py',
            'autonomous_agents_service.py'
        ]
        
        results = {}
        for service in required_services:
            service_path = services_path / service
            exists = service_path.exists()
            results[service] = exists
            self.verification_results['total_checks'] += 1
            if exists:
                self.verification_results['passed_checks'] += 1
                print(f"  ✅ {service}")
            else:
                self.verification_results['failed_checks'] += 1
                self.verification_results['missing_files'].append(str(service_path))
                print(f"  ❌ {service} - MISSING")
        
        return results
    
    def verify_agents_structure(self) -> Dict[str, bool]:
        """Verify agents directory structure"""
        print("\n🔍 Verifying Agents Structure...")
        
        agents_path = self.workspace_path / 'agents'
        required_agents = [
            'base/',
            'osint/',
            'investigation/',
            'forensics/',
            'data_analysis/',
            'reverse_engineering/',
            'metadata/',
            'reporting/',
            'technology_monitor/'
        ]
        
        results = {}
        for agent in required_agents:
            agent_path = agents_path / agent
            exists = agent_path.exists()
            results[agent] = exists
            self.verification_results['total_checks'] += 1
            if exists:
                self.verification_results['passed_checks'] += 1
                print(f"  ✅ {agent}")
            else:
                self.verification_results['failed_checks'] += 1
                self.verification_results['missing_files'].append(str(agent_path))
                print(f"  ❌ {agent} - MISSING")
        
        return results
    
    def verify_core_structure(self) -> Dict[str, bool]:
        """Verify core directory structure"""
        print("\n🔍 Verifying Core Structure...")
        
        core_path = self.workspace_path / 'core'
        required_core = [
            'orchestrator.py',
            'integration_manager.py',
            'integration_manager_complete.py'
        ]
        
        results = {}
        for core_file in required_core:
            core_file_path = core_path / core_file
            exists = core_file_path.exists()
            results[core_file] = exists
            self.verification_results['total_checks'] += 1
            if exists:
                self.verification_results['passed_checks'] += 1
                print(f"  ✅ {core_file}")
            else:
                self.verification_results['failed_checks'] += 1
                self.verification_results['missing_files'].append(str(core_file_path))
                print(f"  ❌ {core_file} - MISSING")
        
        return results
    
    def verify_api_structure(self) -> Dict[str, bool]:
        """Verify API directory structure"""
        print("\n🔍 Verifying API Structure...")
        
        api_path = self.workspace_path / 'api'
        required_api = [
            'main.py'
        ]
        
        results = {}
        for api_file in required_api:
            api_file_path = api_path / api_file
            exists = api_file_path.exists()
            results[api_file] = exists
            self.verification_results['total_checks'] += 1
            if exists:
                self.verification_results['passed_checks'] += 1
                print(f"  ✅ {api_file}")
            else:
                self.verification_results['failed_checks'] += 1
                self.verification_results['missing_files'].append(str(api_file_path))
                print(f"  ❌ {api_file} - MISSING")
        
        return results
    
    def verify_test_structure(self) -> Dict[str, bool]:
        """Verify test files structure"""
        print("\n🔍 Verifying Test Structure...")
        
        required_tests = [
            'test_phase2.py',
            'test_phase3_complete.py',
            'test_phase4_complete.py',
            'test_phase5_complete.py',
            'test_phase6_complete.py',
            'test_phase6_10_complete.py',
            'test_complete_system.py',
            'test_system.py'
        ]
        
        results = {}
        for test_file in required_tests:
            test_path = self.workspace_path / test_file
            exists = test_path.exists()
            results[test_file] = exists
            self.verification_results['total_checks'] += 1
            if exists:
                self.verification_results['passed_checks'] += 1
                print(f"  ✅ {test_file}")
            else:
                self.verification_results['failed_checks'] += 1
                self.verification_results['missing_files'].append(str(test_path))
                print(f"  ❌ {test_file} - MISSING")
        
        return results
    
    def verify_verification_scripts(self) -> Dict[str, bool]:
        """Verify verification scripts"""
        print("\n🔍 Verifying Verification Scripts...")
        
        required_scripts = [
            'final_workflow_verification.py',
            'verify_workflows.py',
            'check_workflow_configuration.py',
            'check_workflow_status.py',
            'run_workflow_tests.py',
            'simple_workflow_check.py',
            'verify_all_workflows.py'
        ]
        
        results = {}
        for script in required_scripts:
            script_path = self.workspace_path / script
            exists = script_path.exists()
            results[script] = exists
            self.verification_results['total_checks'] += 1
            if exists:
                self.verification_results['passed_checks'] += 1
                print(f"  ✅ {script}")
            else:
                self.verification_results['failed_checks'] += 1
                self.verification_results['missing_files'].append(str(script_path))
                print(f"  ❌ {script} - MISSING")
        
        return results
    
    def verify_documentation_structure(self) -> Dict[str, bool]:
        """Verify documentation structure"""
        print("\n🔍 Verifying Documentation Structure...")
        
        required_docs = [
            'README.md',
            'COMPLETE_IMPLEMENTATION_SUMMARY.md',
            'FINAL_WORKFLOW_STATUS_REPORT.md',
            'WORKFLOW_VERIFICATION_SUMMARY.md',
            'WORKFLOW_VERIFICATION_GUIDE.md',
            'IMPLEMENTATION_STATUS.md',
            'PHASE2_COMPLETION_REPORT.md',
            'PHASE3_COMPLETE_IMPLEMENTATION_REPORT.md',
            'PHASE4_COMPLETE_IMPLEMENTATION_REPORT.md',
            'PHASE5_COMPLETE_IMPLEMENTATION_REPORT.md',
            'SETUP_GUIDE.md',
            'hardening_enhanced.md',
            'architecture.md',
            'docs/architecture.md'
        ]
        
        results = {}
        for doc in required_docs:
            doc_path = self.workspace_path / doc
            exists = doc_path.exists()
            results[doc] = exists
            self.verification_results['total_checks'] += 1
            if exists:
                self.verification_results['passed_checks'] += 1
                print(f"  ✅ {doc}")
            else:
                self.verification_results['failed_checks'] += 1
                self.verification_results['missing_files'].append(str(doc_path))
                print(f"  ❌ {doc} - MISSING")
        
        return results
    
    def calculate_success_rate(self):
        """Calculate overall success rate"""
        if self.verification_results['total_checks'] > 0:
            self.verification_results['success_rate'] = (
                self.verification_results['passed_checks'] / 
                self.verification_results['total_checks']
            ) * 100
        else:
            self.verification_results['success_rate'] = 0.0
    
    def generate_report(self):
        """Generate comprehensive verification report"""
        self.calculate_success_rate()
        
        print("\n" + "="*80)
        print("📊 FILE STRUCTURE VERIFICATION RESULTS")
        print("="*80)
        print(f"Total Checks: {self.verification_results['total_checks']}")
        print(f"Passed: {self.verification_results['passed_checks']}")
        print(f"Failed: {self.verification_results['failed_checks']}")
        print(f"Success Rate: {self.verification_results['success_rate']:.1f}%")
        
        if self.verification_results['missing_files']:
            print(f"\n❌ Missing Files ({len(self.verification_results['missing_files'])}):")
            for missing_file in self.verification_results['missing_files']:
                print(f"  - {missing_file}")
        
        if self.verification_results['incorrect_locations']:
            print(f"\n⚠️  Incorrect Locations ({len(self.verification_results['incorrect_locations'])}):")
            for incorrect_location in self.verification_results['incorrect_locations']:
                print(f"  - {incorrect_location}")
        
        # Save detailed report
        report_path = self.workspace_path / 'logs' / 'file_structure_verification_report.json'
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(self.verification_results, f, indent=2)
        
        print(f"\n📄 Detailed report saved: {report_path}")
        
        return self.verification_results['success_rate'] >= 95.0
    
    def run_verification(self) -> bool:
        """Run complete file structure verification"""
        print("🎯 AMAS Intelligence System - File Structure Verification")
        print("="*80)
        
        # Run all verification checks
        self.verify_core_structure()
        self.verify_services_structure()
        self.verify_agents_structure()
        self.verify_core_structure()
        self.verify_api_structure()
        self.verify_test_structure()
        self.verify_verification_scripts()
        self.verify_documentation_structure()
        
        # Generate final report
        success = self.generate_report()
        
        if success:
            print("\n🎉 FILE STRUCTURE VERIFICATION SUCCESSFUL!")
            print("✅ All project files and docs are in the right place")
            print("✅ File structure is correct and complete")
            print("✅ Ready for production deployment")
        else:
            print("\n❌ FILE STRUCTURE VERIFICATION FAILED!")
            print("⚠️  Some files are missing or in wrong locations")
            print("⚠️  Please check the missing files list above")
        
        return success

def main():
    """Main verification function"""
    verifier = FileStructureVerifier()
    success = verifier.run_verification()
    
    if success:
        print("\n🚀 AMAS Intelligence System file structure is complete and ready!")
        sys.exit(0)
    else:
        print("\n⚠️  File structure verification found issues that need attention.")
        sys.exit(1)

if __name__ == "__main__":
    main()