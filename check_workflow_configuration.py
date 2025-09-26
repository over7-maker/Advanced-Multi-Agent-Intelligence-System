"""
AMAS Intelligence System - Workflow Configuration Checker
Comprehensive checking of workflow configurations and dependencies
"""

import asyncio
import logging
import sys
import json
import importlib
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/workflow_configuration_check.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class WorkflowConfigurationChecker:
    """Comprehensive workflow configuration checker"""
    
    def __init__(self):
        self.check_results = []
        self.workflow_configurations = {}
        self.dependencies = {}
        
    async def check_all_configurations(self):
        """Check all workflow configurations"""
        try:
            logger.info("Starting AMAS Workflow Configuration Check...")
            
            # Check core workflow configurations
            await self._check_core_workflow_configurations()
            
            # Check security workflow configurations
            await self._check_security_workflow_configurations()
            
            # Check agent workflow configurations
            await self._check_agent_workflow_configurations()
            
            # Check service configurations
            await self._check_service_configurations()
            
            # Check dependency configurations
            await self._check_dependency_configurations()
            
            # Check integration configurations
            await self._check_integration_configurations()
            
            # Generate configuration report
            await self._generate_configuration_report()
            
            logger.info("AMAS Workflow Configuration Check completed")
            
        except Exception as e:
            logger.error(f"Configuration check error: {e}")
            raise
    
    async def _check_core_workflow_configurations(self):
        """Check core workflow configurations"""
        try:
            logger.info("Checking core workflow configurations...")
            
            # Check orchestrator configuration
            orchestrator_config = {
                'file': 'core/orchestrator.py',
                'class': 'IntelligenceOrchestrator',
                'workflows': ['osint_investigation', 'digital_forensics', 'threat_intelligence'],
                'agents': ['osint_001', 'investigation_001', 'forensics_001', 'data_analysis_001', 
                          'reverse_engineering_001', 'metadata_001', 'reporting_001', 'technology_monitor_001']
            }
            
            # Verify orchestrator file exists
            orchestrator_path = Path('core/orchestrator.py')
            if orchestrator_path.exists():
                self._record_check_result('orchestrator_file', True, 'Orchestrator file exists')
            else:
                self._record_check_result('orchestrator_file', False, 'Orchestrator file not found')
                return
            
            # Check workflow templates
            try:
                from core.orchestrator import IntelligenceOrchestrator
                
                # Create a mock orchestrator to check workflow templates
                orchestrator = IntelligenceOrchestrator()
                
                # Check if workflows are properly initialized
                if hasattr(orchestrator, 'workflows') and len(orchestrator.workflows) > 0:
                    self._record_check_result('workflow_templates', True, f'Found {len(orchestrator.workflows)} workflow templates')
                    
                    # Check each workflow template
                    for workflow_id, workflow in orchestrator.workflows.items():
                        if 'name' in workflow and 'steps' in workflow:
                            self._record_check_result(f'workflow_{workflow_id}', True, f'Workflow {workflow_id} properly configured')
                        else:
                            self._record_check_result(f'workflow_{workflow_id}', False, f'Workflow {workflow_id} missing required fields')
                else:
                    self._record_check_result('workflow_templates', False, 'No workflow templates found')
                    
            except Exception as e:
                self._record_check_result('workflow_templates', False, f'Error checking workflow templates: {e}')
            
            logger.info("✓ Core workflow configurations checked")
            
        except Exception as e:
            logger.error(f"Error checking core workflow configurations: {e}")
            self._record_check_result('core_workflow_configurations', False, str(e))
    
    async def _check_security_workflow_configurations(self):
        """Check security workflow configurations"""
        try:
            logger.info("Checking security workflow configurations...")
            
            # Check security monitoring service
            security_monitoring_config = {
                'file': 'services/security_monitoring_service.py',
                'class': 'SecurityMonitoringService',
                'features': ['threat_detection', 'security_events', 'threat_intelligence']
            }
            
            security_monitoring_path = Path('services/security_monitoring_service.py')
            if security_monitoring_path.exists():
                self._record_check_result('security_monitoring_service', True, 'Security monitoring service file exists')
            else:
                self._record_check_result('security_monitoring_service', False, 'Security monitoring service file not found')
            
            # Check audit logging service
            audit_logging_config = {
                'file': 'services/audit_logging_service.py',
                'class': 'AuditLoggingService',
                'features': ['audit_logging', 'compliance_monitoring', 'tamper_detection']
            }
            
            audit_logging_path = Path('services/audit_logging_service.py')
            if audit_logging_path.exists():
                self._record_check_result('audit_logging_service', True, 'Audit logging service file exists')
            else:
                self._record_check_result('audit_logging_service', False, 'Audit logging service file not found')
            
            # Check incident response service
            incident_response_config = {
                'file': 'services/incident_response_service.py',
                'class': 'IncidentResponseService',
                'features': ['incident_management', 'response_procedures', 'escalation']
            }
            
            incident_response_path = Path('services/incident_response_service.py')
            if incident_response_path.exists():
                self._record_check_result('incident_response_service', True, 'Incident response service file exists')
            else:
                self._record_check_result('incident_response_service', False, 'Incident response service file not found')
            
            # Check security workflows in main application
            main_phase5_path = Path('main_phase5_complete.py')
            if main_phase5_path.exists():
                self._record_check_result('main_phase5_application', True, 'Main Phase 5 application file exists')
                
                # Check for security workflow methods
                with open(main_phase5_path, 'r') as f:
                    content = f.read()
                    
                security_workflow_methods = [
                    'execute_security_workflow',
                    '_execute_threat_hunting_workflow',
                    '_execute_incident_response_workflow',
                    '_execute_security_assessment_workflow'
                ]
                
                for method in security_workflow_methods:
                    if method in content:
                        self._record_check_result(f'security_method_{method}', True, f'Security method {method} found')
                    else:
                        self._record_check_result(f'security_method_{method}', False, f'Security method {method} not found')
            else:
                self._record_check_result('main_phase5_application', False, 'Main Phase 5 application file not found')
            
            logger.info("✓ Security workflow configurations checked")
            
        except Exception as e:
            logger.error(f"Error checking security workflow configurations: {e}")
            self._record_check_result('security_workflow_configurations', False, str(e))
    
    async def _check_agent_workflow_configurations(self):
        """Check agent workflow configurations"""
        try:
            logger.info("Checking agent workflow configurations...")
            
            # Check agent files
            agent_files = [
                'agents/osint/osint_agent.py',
                'agents/investigation/investigation_agent.py',
                'agents/forensics/forensics_agent.py',
                'agents/data_analysis/data_analysis_agent.py',
                'agents/reverse_engineering/reverse_engineering_agent.py',
                'agents/metadata/metadata_agent.py',
                'agents/reporting/reporting_agent.py',
                'agents/technology_monitor/technology_monitor_agent.py'
            ]
            
            for agent_file in agent_files:
                agent_path = Path(agent_file)
                if agent_path.exists():
                    self._record_check_result(f'agent_file_{agent_file}', True, f'Agent file {agent_file} exists')
                else:
                    self._record_check_result(f'agent_file_{agent_file}', False, f'Agent file {agent_file} not found')
            
            # Check agent base classes
            base_agent_files = [
                'agents/base/intelligence_agent.py',
                'agents/base/agent_communication.py'
            ]
            
            for base_file in base_agent_files:
                base_path = Path(base_file)
                if base_path.exists():
                    self._record_check_result(f'base_agent_file_{base_file}', True, f'Base agent file {base_file} exists')
                else:
                    self._record_check_result(f'base_agent_file_{base_file}', False, f'Base agent file {base_file} not found')
            
            logger.info("✓ Agent workflow configurations checked")
            
        except Exception as e:
            logger.error(f"Error checking agent workflow configurations: {e}")
            self._record_check_result('agent_workflow_configurations', False, str(e))
    
    async def _check_service_configurations(self):
        """Check service configurations"""
        try:
            logger.info("Checking service configurations...")
            
            # Check core services
            core_services = [
                'services/service_manager.py',
                'services/database_service.py',
                'services/security_service.py',
                'services/llm_service.py',
                'services/vector_service.py',
                'services/knowledge_graph_service.py'
            ]
            
            for service_file in core_services:
                service_path = Path(service_file)
                if service_path.exists():
                    self._record_check_result(f'core_service_{service_file}', True, f'Core service {service_file} exists')
                else:
                    self._record_check_result(f'core_service_{service_file}', False, f'Core service {service_file} not found')
            
            # Check monitoring services
            monitoring_services = [
                'services/monitoring_service_complete.py',
                'services/performance_service_complete.py'
            ]
            
            for service_file in monitoring_services:
                service_path = Path(service_file)
                if service_path.exists():
                    self._record_check_result(f'monitoring_service_{service_file}', True, f'Monitoring service {service_file} exists')
                else:
                    self._record_check_result(f'monitoring_service_{service_file}', False, f'Monitoring service {service_file} not found')
            
            # Check AI services
            ai_services = [
                'services/ml_service.py',
                'services/ai_analytics_service.py',
                'services/nlp_service.py',
                'services/computer_vision_service.py',
                'services/autonomous_agents_service.py'
            ]
            
            for service_file in ai_services:
                service_path = Path(service_file)
                if service_path.exists():
                    self._record_check_result(f'ai_service_{service_file}', True, f'AI service {service_file} exists')
                else:
                    self._record_check_result(f'ai_service_{service_file}', False, f'AI service {service_file} not found')
            
            logger.info("✓ Service configurations checked")
            
        except Exception as e:
            logger.error(f"Error checking service configurations: {e}")
            self._record_check_result('service_configurations', False, str(e))
    
    async def _check_dependency_configurations(self):
        """Check dependency configurations"""
        try:
            logger.info("Checking dependency configurations...")
            
            # Check requirements files
            requirements_files = [
                'requirements.txt',
                'requirements_phase3.txt',
                'requirements-phase2.txt',
                'requirements-minimal.txt'
            ]
            
            for req_file in requirements_files:
                req_path = Path(req_file)
                if req_path.exists():
                    self._record_check_result(f'requirements_file_{req_file}', True, f'Requirements file {req_file} exists')
                else:
                    self._record_check_result(f'requirements_file_{req_file}', False, f'Requirements file {req_file} not found')
            
            # Check Docker configuration
            docker_compose_path = Path('docker-compose.yml')
            if docker_compose_path.exists():
                self._record_check_result('docker_compose', True, 'Docker Compose file exists')
            else:
                self._record_check_result('docker_compose', False, 'Docker Compose file not found')
            
            # Check setup scripts
            setup_scripts = [
                'setup.py',
                'setup_venv.py',
                'setup_complete.py'
            ]
            
            for script in setup_scripts:
                script_path = Path(script)
                if script_path.exists():
                    self._record_check_result(f'setup_script_{script}', True, f'Setup script {script} exists')
                else:
                    self._record_check_result(f'setup_script_{script}', False, f'Setup script {script} not found')
            
            logger.info("✓ Dependency configurations checked")
            
        except Exception as e:
            logger.error(f"Error checking dependency configurations: {e}")
            self._record_check_result('dependency_configurations', False, str(e))
    
    async def _check_integration_configurations(self):
        """Check integration configurations"""
        try:
            logger.info("Checking integration configurations...")
            
            # Check API configuration
            api_path = Path('api/main.py')
            if api_path.exists():
                self._record_check_result('api_main', True, 'API main file exists')
            else:
                self._record_check_result('api_main', False, 'API main file not found')
            
            # Check test files
            test_files = [
                'test_phase5_complete.py',
                'test_phase4_complete.py',
                'test_phase3_complete.py',
                'test_system.py'
            ]
            
            for test_file in test_files:
                test_path = Path(test_file)
                if test_path.exists():
                    self._record_check_result(f'test_file_{test_file}', True, f'Test file {test_file} exists')
                else:
                    self._record_check_result(f'test_file_{test_file}', False, f'Test file {test_file} not found')
            
            # Check documentation files
            doc_files = [
                'README.md',
                'PHASE5_COMPLETE_IMPLEMENTATION_REPORT.md',
                'PHASE4_COMPLETE_IMPLEMENTATION_REPORT.md',
                'IMPLEMENTATION_STATUS.md'
            ]
            
            for doc_file in doc_files:
                doc_path = Path(doc_file)
                if doc_path.exists():
                    self._record_check_result(f'doc_file_{doc_file}', True, f'Documentation file {doc_file} exists')
                else:
                    self._record_check_result(f'doc_file_{doc_file}', False, f'Documentation file {doc_file} not found')
            
            logger.info("✓ Integration configurations checked")
            
        except Exception as e:
            logger.error(f"Error checking integration configurations: {e}")
            self._record_check_result('integration_configurations', False, str(e))
    
    async def _generate_configuration_report(self):
        """Generate comprehensive configuration report"""
        try:
            logger.info("Generating configuration report...")
            
            total_checks = len(self.check_results)
            passed_checks = len([r for r in self.check_results if r['passed']])
            failed_checks = total_checks - passed_checks
            
            report = {
                'configuration_check_suite': 'AMAS Workflow Configuration Check',
                'timestamp': datetime.utcnow().isoformat(),
                'summary': {
                    'total_checks': total_checks,
                    'passed_checks': passed_checks,
                    'failed_checks': failed_checks,
                    'success_rate': (passed_checks / total_checks * 100) if total_checks > 0 else 0
                },
                'check_results': self.check_results,
                'configuration_status': {
                    'core_workflows': 'checked',
                    'security_workflows': 'checked',
                    'agent_workflows': 'checked',
                    'service_configurations': 'checked',
                    'dependency_configurations': 'checked',
                    'integration_configurations': 'checked'
                }
            }
            
            # Save report to file
            with open('logs/workflow_configuration_report.json', 'w') as f:
                json.dump(report, f, indent=2)
            
            # Log summary
            logger.info(f"Workflow Configuration Check Report Summary:")
            logger.info(f"  Total Checks: {total_checks}")
            logger.info(f"  Passed: {passed_checks}")
            logger.info(f"  Failed: {failed_checks}")
            logger.info(f"  Success Rate: {report['summary']['success_rate']:.1f}%")
            
            if failed_checks > 0:
                logger.warning(f"  Failed Checks:")
                for result in self.check_results:
                    if not result['passed']:
                        logger.warning(f"    - {result['check_name']}: {result['message']}")
            
            logger.info("Workflow configuration report generated: logs/workflow_configuration_report.json")
            
        except Exception as e:
            logger.error(f"Failed to generate configuration report: {e}")
    
    def _record_check_result(self, check_name: str, passed: bool, message: str):
        """Record check result"""
        self.check_results.append({
            'check_name': check_name,
            'passed': passed,
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        })

async def main():
    """Main configuration check execution"""
    try:
        checker = WorkflowConfigurationChecker()
        await checker.check_all_configurations()
        
    except Exception as e:
        logger.error(f"Configuration check failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())