"""
AMAS Intelligence System - Workflow Status Checker
Comprehensive checking of workflow status and runtime health
"""

import asyncio
import logging
import sys
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/workflow_status_check.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Import the Phase 5 system
from main_phase5_complete import AMASPhase5System

class WorkflowStatusChecker:
    """Comprehensive workflow status checker"""
    
    def __init__(self):
        self.status_results = []
        self.config = self._get_status_check_config()
        self.system = None
        
    def _get_status_check_config(self) -> Dict[str, Any]:
        """Get status check configuration"""
        return {
            # Core services
            'llm_service_url': 'http://localhost:11434',
            'vector_service_url': 'http://localhost:8001',
            'graph_service_url': 'bolt://localhost:7687',
            'postgres_host': 'localhost',
            'postgres_port': 5432,
            'postgres_user': 'amas',
            'postgres_password': 'amas123',
            'postgres_db': 'amas',
            'redis_host': 'localhost',
            'redis_port': 6379,
            'redis_db': 0,
            'neo4j_username': 'neo4j',
            'neo4j_password': 'amas123',
            'neo4j_database': 'neo4j',
            
            # Security configuration
            'jwt_secret': 'status_check_jwt_secret_key_2024_phase5',
            'encryption_key': 'status_check_encryption_key_2024_secure_32_chars_phase5',
            'security_secret_key': 'status_check_security_secret_key_2024_phase5',
            'audit_secret_key': 'status_check_audit_secret_key_2024_phase5',
            
            # API keys (status check keys)
            'deepseek_api_key': 'status_check_deepseek_key',
            'glm_api_key': 'status_check_glm_key',
            'grok_api_key': 'status_check_grok_key',
            
            # Phase 5 specific configuration
            'audit_retention_days': 30,
            'audit_rotation_size': 10 * 1024 * 1024,
            'audit_compression': True,
            'audit_encryption': True,
            'audit_tamper_detection': True,
            'audit_compliance_mode': 'strict',
            'audit_storage_path': 'logs/status_check_audit',
            
            # Security monitoring
            'auto_containment': True,
            'escalation_threshold': 5,
            'max_concurrent_incidents': 5,
            'notification_channels': ['email'],
            'response_timeout': 10,
            
            # Performance optimization
            'cache_max_size': 100,
            'cache_default_ttl': 300,
            'cache_strategy': 'lru',
            'cache_compression': True,
            'load_balance_strategy': 'round_robin',
            'health_check_interval': 10,
            'max_retries': 2,
            'timeout': 10,
            'max_memory': 100 * 1024 * 1024,
            'max_cpu': 50.0,
            'max_connections': 100
        }
    
    async def check_all_workflow_status(self):
        """Check all workflow status"""
        try:
            logger.info("Starting AMAS Workflow Status Check...")
            
            # Initialize system
            await self._initialize_system()
            
            # Check system status
            await self._check_system_status()
            
            # Check service status
            await self._check_service_status()
            
            # Check agent status
            await self._check_agent_status()
            
            # Check workflow status
            await self._check_workflow_status()
            
            # Check security status
            await self._check_security_status()
            
            # Check monitoring status
            await self._check_monitoring_status()
            
            # Test workflow execution
            await self._test_workflow_execution()
            
            # Generate status report
            await self._generate_status_report()
            
            logger.info("AMAS Workflow Status Check completed")
            
        except Exception as e:
            logger.error(f"Status check error: {e}")
            raise
        finally:
            # Cleanup
            if self.system:
                await self.system.shutdown()
    
    async def _initialize_system(self):
        """Initialize the AMAS system"""
        try:
            logger.info("Initializing AMAS system for status check...")
            
            self.system = AMASPhase5System(self.config)
            await self.system.initialize()
            
            # Verify system is operational
            status = await self.system.get_system_status()
            assert status['system_status'] == 'operational'
            assert status['phase'] == 'phase5'
            
            self._record_status_result('system_initialization', True, 'System initialized successfully')
            logger.info("✓ System initialization verified")
            
        except Exception as e:
            self._record_status_result('system_initialization', False, str(e))
            logger.error(f"✗ System initialization failed: {e}")
            raise
    
    async def _check_system_status(self):
        """Check overall system status"""
        try:
            logger.info("Checking system status...")
            
            # Get comprehensive system status
            system_status = await self.system.get_system_status()
            
            # Check system status
            if system_status['system_status'] == 'operational':
                self._record_status_result('system_operational', True, 'System is operational')
            else:
                self._record_status_result('system_operational', False, f'System status: {system_status["system_status"]}')
            
            # Check phase
            if system_status['phase'] == 'phase5':
                self._record_status_result('system_phase', True, 'System is in Phase 5')
            else:
                self._record_status_result('system_phase', False, f'System phase: {system_status["phase"]}')
            
            # Check agents
            if system_status['agents'] == 8:
                self._record_status_result('agent_count', True, f'All {system_status["agents"]} agents are active')
            else:
                self._record_status_result('agent_count', False, f'Expected 8 agents, found {system_status["agents"]}')
            
            # Check orchestrator
            if 'orchestrator' in system_status:
                orchestrator_status = system_status['orchestrator']
                if orchestrator_status.get('orchestrator_status') == 'active':
                    self._record_status_result('orchestrator_active', True, 'Orchestrator is active')
                else:
                    self._record_status_result('orchestrator_active', False, 'Orchestrator is not active')
            
            logger.info("✓ System status checked")
            
        except Exception as e:
            logger.error(f"Error checking system status: {e}")
            self._record_status_result('system_status_check', False, str(e))
    
    async def _check_service_status(self):
        """Check service status"""
        try:
            logger.info("Checking service status...")
            
            # Check security service
            security_status = await self.system.security_service.health_check()
            if security_status['status'] == 'healthy':
                self._record_status_result('security_service', True, 'Security service is healthy')
            else:
                self._record_status_result('security_service', False, f'Security service status: {security_status["status"]}')
            
            # Check security monitoring service
            security_monitoring_status = await self.system.security_monitoring_service.get_security_status()
            if security_monitoring_status['monitoring_enabled']:
                self._record_status_result('security_monitoring', True, 'Security monitoring is enabled')
            else:
                self._record_status_result('security_monitoring', False, 'Security monitoring is disabled')
            
            # Check audit logging service
            audit_status = await self.system.audit_logging_service.get_audit_status()
            if audit_status['logging_enabled']:
                self._record_status_result('audit_logging', True, 'Audit logging is enabled')
            else:
                self._record_status_result('audit_logging', False, 'Audit logging is disabled')
            
            # Check incident response service
            incident_status = await self.system.incident_response_service.get_incident_status()
            if incident_status['response_enabled']:
                self._record_status_result('incident_response', True, 'Incident response is enabled')
            else:
                self._record_status_result('incident_response', False, 'Incident response is disabled')
            
            # Check monitoring service
            monitoring_status = await self.system.monitoring_service.get_monitoring_status()
            if monitoring_status['monitoring_enabled']:
                self._record_status_result('monitoring_service', True, 'Monitoring service is enabled')
            else:
                self._record_status_result('monitoring_service', False, 'Monitoring service is disabled')
            
            # Check performance service
            performance_status = await self.system.performance_service.get_performance_status()
            if 'cache_stats' in performance_status:
                self._record_status_result('performance_service', True, 'Performance service is operational')
            else:
                self._record_status_result('performance_service', False, 'Performance service is not operational')
            
            logger.info("✓ Service status checked")
            
        except Exception as e:
            logger.error(f"Error checking service status: {e}")
            self._record_status_result('service_status_check', False, str(e))
    
    async def _check_agent_status(self):
        """Check agent status"""
        try:
            logger.info("Checking agent status...")
            
            # Check each agent
            agents = self.system.agents
            expected_agents = [
                'osint_001', 'investigation_001', 'forensics_001', 'data_analysis_001',
                'reverse_engineering_001', 'metadata_001', 'reporting_001', 'technology_monitor_001'
            ]
            
            for agent_id in expected_agents:
                if agent_id in agents:
                    agent = agents[agent_id]
                    if hasattr(agent, 'status') and agent.status.value == 'active':
                        self._record_status_result(f'agent_{agent_id}', True, f'Agent {agent_id} is active')
                    else:
                        self._record_status_result(f'agent_{agent_id}', False, f'Agent {agent_id} is not active')
                else:
                    self._record_status_result(f'agent_{agent_id}', False, f'Agent {agent_id} not found')
            
            logger.info("✓ Agent status checked")
            
        except Exception as e:
            logger.error(f"Error checking agent status: {e}")
            self._record_status_result('agent_status_check', False, str(e))
    
    async def _check_workflow_status(self):
        """Check workflow status"""
        try:
            logger.info("Checking workflow status...")
            
            # Check orchestrator workflows
            orchestrator = self.system.orchestrator
            
            # Check workflow templates
            if hasattr(orchestrator, 'workflows') and len(orchestrator.workflows) > 0:
                self._record_status_result('workflow_templates', True, f'Found {len(orchestrator.workflows)} workflow templates')
                
                # Check each workflow template
                for workflow_id, workflow in orchestrator.workflows.items():
                    if 'name' in workflow and 'steps' in workflow and len(workflow['steps']) > 0:
                        self._record_status_result(f'workflow_template_{workflow_id}', True, f'Workflow template {workflow_id} is valid')
                    else:
                        self._record_status_result(f'workflow_template_{workflow_id}', False, f'Workflow template {workflow_id} is invalid')
            else:
                self._record_status_result('workflow_templates', False, 'No workflow templates found')
            
            # Check workflow instances
            if hasattr(orchestrator, 'workflow_instances'):
                self._record_status_result('workflow_instances', True, f'Found {len(orchestrator.workflow_instances)} workflow instances')
            else:
                self._record_status_result('workflow_instances', False, 'No workflow instances found')
            
            logger.info("✓ Workflow status checked")
            
        except Exception as e:
            logger.error(f"Error checking workflow status: {e}")
            self._record_status_result('workflow_status_check', False, str(e))
    
    async def _check_security_status(self):
        """Check security status"""
        try:
            logger.info("Checking security status...")
            
            # Check security dashboard
            security_dashboard = await self.system.get_security_dashboard()
            
            if 'security_events' in security_dashboard:
                self._record_status_result('security_events', True, 'Security events are available')
            else:
                self._record_status_result('security_events', False, 'Security events are not available')
            
            if 'active_incidents' in security_dashboard:
                self._record_status_result('active_incidents', True, 'Active incidents are available')
            else:
                self._record_status_result('active_incidents', False, 'Active incidents are not available')
            
            if 'audit_events' in security_dashboard:
                self._record_status_result('audit_events', True, 'Audit events are available')
            else:
                self._record_status_result('audit_events', False, 'Audit events are not available')
            
            if 'monitoring_metrics' in security_dashboard:
                self._record_status_result('monitoring_metrics', True, 'Monitoring metrics are available')
            else:
                self._record_status_result('monitoring_metrics', False, 'Monitoring metrics are not available')
            
            logger.info("✓ Security status checked")
            
        except Exception as e:
            logger.error(f"Error checking security status: {e}")
            self._record_status_result('security_status_check', False, str(e))
    
    async def _check_monitoring_status(self):
        """Check monitoring status"""
        try:
            logger.info("Checking monitoring status...")
            
            # Check monitoring service
            monitoring_status = await self.system.monitoring_service.get_monitoring_status()
            
            if monitoring_status['monitoring_enabled']:
                self._record_status_result('monitoring_enabled', True, 'Monitoring is enabled')
            else:
                self._record_status_result('monitoring_enabled', False, 'Monitoring is disabled')
            
            if 'active_alerts' in monitoring_status:
                self._record_status_result('active_alerts', True, f'Found {monitoring_status["active_alerts"]} active alerts')
            else:
                self._record_status_result('active_alerts', False, 'No active alerts found')
            
            if 'system_metrics' in monitoring_status:
                self._record_status_result('system_metrics', True, 'System metrics are available')
            else:
                self._record_status_result('system_metrics', False, 'System metrics are not available')
            
            # Check performance service
            performance_status = await self.system.performance_service.get_performance_status()
            
            if 'cache_stats' in performance_status:
                self._record_status_result('cache_stats', True, 'Cache statistics are available')
            else:
                self._record_status_result('cache_stats', False, 'Cache statistics are not available')
            
            if 'resource_monitoring' in performance_status:
                self._record_status_result('resource_monitoring', True, 'Resource monitoring is available')
            else:
                self._record_status_result('resource_monitoring', False, 'Resource monitoring is not available')
            
            logger.info("✓ Monitoring status checked")
            
        except Exception as e:
            logger.error(f"Error checking monitoring status: {e}")
            self._record_status_result('monitoring_status_check', False, str(e))
    
    async def _test_workflow_execution(self):
        """Test workflow execution"""
        try:
            logger.info("Testing workflow execution...")
            
            # Test task submission
            task_data = {
                'type': 'osint',
                'description': 'Status check OSINT task',
                'user_id': 'status_check_user',
                'priority': 2,
                'parameters': {'keywords': ['status', 'check']}
            }
            
            task_id = await self.system.submit_intelligence_task(task_data)
            if task_id:
                self._record_status_result('task_submission', True, f'Task submitted successfully: {task_id}')
            else:
                self._record_status_result('task_submission', False, 'Task submission failed')
            
            # Test security workflow execution
            security_workflow_config = {
                'user_id': 'status_check_user',
                'target_systems': ['status_check_server'],
                'threat_indicators': ['status_check_threat'],
                'osint_parameters': {'keywords': ['status', 'check']}
            }
            
            workflow_result = await self.system.execute_security_workflow('threat_hunting', security_workflow_config)
            if 'workflow_type' in workflow_result and workflow_result['workflow_type'] == 'threat_hunting':
                self._record_status_result('security_workflow_execution', True, 'Security workflow executed successfully')
            else:
                self._record_status_result('security_workflow_execution', False, 'Security workflow execution failed')
            
            # Test orchestrator workflow execution
            orchestrator = self.system.orchestrator
            
            # Test OSINT investigation workflow
            osint_workflow_params = {
                'sources': ['web', 'social_media'],
                'keywords': ['status', 'check'],
                'filters': {'date_range': 'last_7_days'}
            }
            
            try:
                workflow_id = await orchestrator.execute_workflow('osint_investigation', osint_workflow_params)
                if workflow_id:
                    self._record_status_result('orchestrator_workflow_execution', True, f'Orchestrator workflow executed: {workflow_id}')
                else:
                    self._record_status_result('orchestrator_workflow_execution', False, 'Orchestrator workflow execution failed')
            except Exception as e:
                self._record_status_result('orchestrator_workflow_execution', False, f'Orchestrator workflow execution error: {e}')
            
            logger.info("✓ Workflow execution tested")
            
        except Exception as e:
            logger.error(f"Error testing workflow execution: {e}")
            self._record_status_result('workflow_execution_test', False, str(e))
    
    async def _generate_status_report(self):
        """Generate comprehensive status report"""
        try:
            logger.info("Generating status report...")
            
            total_checks = len(self.status_results)
            passed_checks = len([r for r in self.status_results if r['passed']])
            failed_checks = total_checks - passed_checks
            
            report = {
                'status_check_suite': 'AMAS Workflow Status Check',
                'timestamp': datetime.utcnow().isoformat(),
                'summary': {
                    'total_checks': total_checks,
                    'passed_checks': passed_checks,
                    'failed_checks': failed_checks,
                    'success_rate': (passed_checks / total_checks * 100) if total_checks > 0 else 0
                },
                'status_results': self.status_results,
                'workflow_status': {
                    'system_status': 'checked',
                    'service_status': 'checked',
                    'agent_status': 'checked',
                    'workflow_status': 'checked',
                    'security_status': 'checked',
                    'monitoring_status': 'checked',
                    'workflow_execution': 'tested'
                }
            }
            
            # Save report to file
            with open('logs/workflow_status_report.json', 'w') as f:
                json.dump(report, f, indent=2)
            
            # Log summary
            logger.info(f"Workflow Status Check Report Summary:")
            logger.info(f"  Total Checks: {total_checks}")
            logger.info(f"  Passed: {passed_checks}")
            logger.info(f"  Failed: {failed_checks}")
            logger.info(f"  Success Rate: {report['summary']['success_rate']:.1f}%")
            
            if failed_checks > 0:
                logger.warning(f"  Failed Checks:")
                for result in self.status_results:
                    if not result['passed']:
                        logger.warning(f"    - {result['check_name']}: {result['message']}")
            
            logger.info("Workflow status report generated: logs/workflow_status_report.json")
            
        except Exception as e:
            logger.error(f"Failed to generate status report: {e}")
    
    def _record_status_result(self, check_name: str, passed: bool, message: str):
        """Record status check result"""
        self.status_results.append({
            'check_name': check_name,
            'passed': passed,
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        })

async def main():
    """Main status check execution"""
    try:
        checker = WorkflowStatusChecker()
        await checker.check_all_workflow_status()
        
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())