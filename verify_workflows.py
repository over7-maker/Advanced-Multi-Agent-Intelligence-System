"""
AMAS Intelligence System - Workflow Verification and Testing
Comprehensive verification of all workflows and their configurations
"""

import asyncio
import logging
import sys
import json
from datetime import datetime
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/workflow_verification.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Import the Phase 5 system
from main_phase5_complete import AMASPhase5System

class WorkflowVerifier:
    """Comprehensive workflow verification and testing"""
    
    def __init__(self):
        self.verification_results = []
        self.config = self._get_verification_config()
        self.system = None
        
    def _get_verification_config(self) -> Dict[str, Any]:
        """Get verification configuration"""
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
            'jwt_secret': 'verification_jwt_secret_key_2024_phase5',
            'encryption_key': 'verification_encryption_key_2024_secure_32_chars_phase5',
            'security_secret_key': 'verification_security_secret_key_2024_phase5',
            'audit_secret_key': 'verification_audit_secret_key_2024_phase5',
            
            # API keys (verification keys)
            'deepseek_api_key': 'verification_deepseek_key',
            'glm_api_key': 'verification_glm_key',
            'grok_api_key': 'verification_grok_key',
            
            # Phase 5 specific configuration
            'audit_retention_days': 30,
            'audit_rotation_size': 10 * 1024 * 1024,
            'audit_compression': True,
            'audit_encryption': True,
            'audit_tamper_detection': True,
            'audit_compliance_mode': 'strict',
            'audit_storage_path': 'logs/verification_audit',
            
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
    
    async def verify_all_workflows(self):
        """Verify all workflows are configured correctly"""
        try:
            logger.info("Starting AMAS Workflow Verification...")
            
            # Initialize system
            await self._initialize_system()
            
            # Verify core workflows
            await self._verify_core_workflows()
            
            # Verify security workflows
            await self._verify_security_workflows()
            
            # Verify agent workflows
            await self._verify_agent_workflows()
            
            # Verify integration workflows
            await self._verify_integration_workflows()
            
            # Verify monitoring workflows
            await self._verify_monitoring_workflows()
            
            # Test workflow execution
            await self._test_workflow_execution()
            
            # Generate verification report
            await self._generate_verification_report()
            
            logger.info("AMAS Workflow Verification completed")
            
        except Exception as e:
            logger.error(f"Workflow verification error: {e}")
            raise
        finally:
            # Cleanup
            if self.system:
                await self.system.shutdown()
    
    async def _initialize_system(self):
        """Initialize the AMAS system"""
        try:
            logger.info("Initializing AMAS system for workflow verification...")
            
            self.system = AMASPhase5System(self.config)
            await self.system.initialize()
            
            # Verify system is operational
            status = await self.system.get_system_status()
            assert status['system_status'] == 'operational'
            assert status['phase'] == 'phase5'
            
            self._record_verification_result('system_initialization', True, 'System initialized successfully')
            logger.info("✓ System initialization verified")
            
        except Exception as e:
            self._record_verification_result('system_initialization', False, str(e))
            logger.error(f"✗ System initialization failed: {e}")
            raise
    
    async def _verify_core_workflows(self):
        """Verify core workflows"""
        try:
            logger.info("Verifying core workflows...")
            
            # Check orchestrator workflows
            orchestrator = self.system.orchestrator
            assert hasattr(orchestrator, 'workflows')
            assert len(orchestrator.workflows) > 0
            
            # Verify workflow templates
            expected_workflows = ['osint_investigation', 'digital_forensics', 'threat_intelligence']
            for workflow_id in expected_workflows:
                assert workflow_id in orchestrator.workflows
                workflow = orchestrator.workflows[workflow_id]
                assert 'name' in workflow
                assert 'description' in workflow
                assert 'steps' in workflow
                assert len(workflow['steps']) > 0
                
                # Verify workflow steps
                for step in workflow['steps']:
                    assert 'step_id' in step
                    assert 'agent_type' in step
                    assert 'action' in step
                    assert 'parameters' in step
            
            self._record_verification_result('core_workflows', True, 'Core workflows verified')
            logger.info("✓ Core workflows verified")
            
        except Exception as e:
            self._record_verification_result('core_workflows', False, str(e))
            logger.error(f"✗ Core workflows verification failed: {e}")
            raise
    
    async def _verify_security_workflows(self):
        """Verify security workflows"""
        try:
            logger.info("Verifying security workflows...")
            
            # Test threat hunting workflow
            threat_hunting_config = {
                'user_id': 'verification_user',
                'target_systems': ['test_server1', 'test_server2'],
                'threat_indicators': ['malware', 'suspicious_network'],
                'osint_parameters': {'keywords': ['threat', 'malware']}
            }
            
            result = await self.system.execute_security_workflow('threat_hunting', threat_hunting_config)
            assert 'workflow_type' in result
            assert result['workflow_type'] == 'threat_hunting'
            assert 'incident_id' in result
            
            # Test incident response workflow
            incident_response_config = {
                'user_id': 'verification_user',
                'severity': 'high',
                'title': 'Verification Incident',
                'description': 'Workflow verification incident',
                'affected_systems': ['test_server1'],
                'threat_indicators': ['malware']
            }
            
            result = await self.system.execute_security_workflow('incident_response', incident_response_config)
            assert 'workflow_type' in result
            assert result['workflow_type'] == 'incident_response'
            assert 'incident_id' in result
            
            # Test security assessment workflow
            security_assessment_config = {
                'user_id': 'verification_user',
                'assessment_parameters': {'scope': 'full'},
                'compliance_standards': ['SOX', 'GDPR']
            }
            
            result = await self.system.execute_security_workflow('security_assessment', security_assessment_config)
            assert 'workflow_type' in result
            assert result['workflow_type'] == 'security_assessment'
            
            self._record_verification_result('security_workflows', True, 'Security workflows verified')
            logger.info("✓ Security workflows verified")
            
        except Exception as e:
            self._record_verification_result('security_workflows', False, str(e))
            logger.error(f"✗ Security workflows verification failed: {e}")
            raise
    
    async def _verify_agent_workflows(self):
        """Verify agent workflows"""
        try:
            logger.info("Verifying agent workflows...")
            
            # Test individual agent tasks
            agents = self.system.agents
            
            # Test OSINT agent
            osint_task = {
                'type': 'osint',
                'description': 'Verification OSINT task',
                'user_id': 'verification_user',
                'priority': 2,
                'parameters': {'keywords': ['verification', 'test']}
            }
            
            task_id = await self.system.submit_intelligence_task(osint_task)
            assert task_id is not None
            
            # Test investigation agent
            investigation_task = {
                'type': 'investigation',
                'description': 'Verification investigation task',
                'user_id': 'verification_user',
                'priority': 2,
                'parameters': {'entities': ['test_entity']}
            }
            
            task_id = await self.system.submit_intelligence_task(investigation_task)
            assert task_id is not None
            
            # Test forensics agent
            forensics_task = {
                'type': 'forensics',
                'description': 'Verification forensics task',
                'user_id': 'verification_user',
                'priority': 2,
                'parameters': {'evidence': ['test_evidence']}
            }
            
            task_id = await self.system.submit_intelligence_task(forensics_task)
            assert task_id is not None
            
            # Test data analysis agent
            data_analysis_task = {
                'type': 'data_analysis',
                'description': 'Verification data analysis task',
                'user_id': 'verification_user',
                'priority': 2,
                'parameters': {'data': ['test_data']}
            }
            
            task_id = await self.system.submit_intelligence_task(data_analysis_task)
            assert task_id is not None
            
            # Test reverse engineering agent
            reverse_engineering_task = {
                'type': 'reverse_engineering',
                'description': 'Verification reverse engineering task',
                'user_id': 'verification_user',
                'priority': 2,
                'parameters': {'binary': 'test_binary'}
            }
            
            task_id = await self.system.submit_intelligence_task(reverse_engineering_task)
            assert task_id is not None
            
            # Test metadata agent
            metadata_task = {
                'type': 'metadata',
                'description': 'Verification metadata task',
                'user_id': 'verification_user',
                'priority': 2,
                'parameters': {'files': ['test_file']}
            }
            
            task_id = await self.system.submit_intelligence_task(metadata_task)
            assert task_id is not None
            
            # Test reporting agent
            reporting_task = {
                'type': 'reporting',
                'description': 'Verification reporting task',
                'user_id': 'verification_user',
                'priority': 2,
                'parameters': {'report_type': 'verification_report'}
            }
            
            task_id = await self.system.submit_intelligence_task(reporting_task)
            assert task_id is not None
            
            # Test technology monitor agent
            technology_monitor_task = {
                'type': 'technology_monitor',
                'description': 'Verification technology monitor task',
                'user_id': 'verification_user',
                'priority': 2,
                'parameters': {'monitoring_type': 'verification'}
            }
            
            task_id = await self.system.submit_intelligence_task(technology_monitor_task)
            assert task_id is not None
            
            self._record_verification_result('agent_workflows', True, 'Agent workflows verified')
            logger.info("✓ Agent workflows verified")
            
        except Exception as e:
            self._record_verification_result('agent_workflows', False, str(e))
            logger.error(f"✗ Agent workflows verification failed: {e}")
            raise
    
    async def _verify_integration_workflows(self):
        """Verify integration workflows"""
        try:
            logger.info("Verifying integration workflows...")
            
            # Test service integration
            services = [
                self.system.security_service,
                self.system.security_monitoring_service,
                self.system.audit_logging_service,
                self.system.incident_response_service,
                self.system.monitoring_service,
                self.system.performance_service
            ]
            
            for service in services:
                assert service is not None
                # Test service health
                if hasattr(service, 'health_check'):
                    health = await service.health_check()
                    assert health['status'] == 'healthy'
                elif hasattr(service, 'get_security_status'):
                    status = await service.get_security_status()
                    assert 'monitoring_enabled' in status
                elif hasattr(service, 'get_audit_status'):
                    status = await service.get_audit_status()
                    assert 'logging_enabled' in status
                elif hasattr(service, 'get_incident_status'):
                    status = await service.get_incident_status()
                    assert 'response_enabled' in status
                elif hasattr(service, 'get_monitoring_status'):
                    status = await service.get_monitoring_status()
                    assert 'monitoring_enabled' in status
                elif hasattr(service, 'get_performance_status'):
                    status = await service.get_performance_status()
                    assert 'cache_stats' in status
            
            # Test database integration
            database_service = self.system.database_service
            assert database_service is not None
            
            # Test orchestrator integration
            orchestrator = self.system.orchestrator
            assert orchestrator is not None
            assert len(orchestrator.agents) == 8
            
            self._record_verification_result('integration_workflows', True, 'Integration workflows verified')
            logger.info("✓ Integration workflows verified")
            
        except Exception as e:
            self._record_verification_result('integration_workflows', False, str(e))
            logger.error(f"✗ Integration workflows verification failed: {e}")
            raise
    
    async def _verify_monitoring_workflows(self):
        """Verify monitoring workflows"""
        try:
            logger.info("Verifying monitoring workflows...")
            
            # Test system status monitoring
            system_status = await self.system.get_system_status()
            assert system_status['system_status'] == 'operational'
            assert 'orchestrator' in system_status
            assert 'security' in system_status
            assert 'security_monitoring' in system_status
            assert 'audit_logging' in system_status
            assert 'incident_response' in system_status
            assert 'monitoring' in system_status
            assert 'performance' in system_status
            
            # Test security dashboard
            security_dashboard = await self.system.get_security_dashboard()
            assert 'security_events' in security_dashboard
            assert 'active_incidents' in security_dashboard
            assert 'audit_events' in security_dashboard
            assert 'monitoring_metrics' in security_dashboard
            
            # Test monitoring service
            monitoring_status = await self.system.monitoring_service.get_monitoring_status()
            assert monitoring_status['monitoring_enabled'] == True
            
            # Test performance service
            performance_status = await self.system.performance_service.get_performance_status()
            assert 'cache_stats' in performance_status
            
            # Test security monitoring
            security_monitoring_status = await self.system.security_monitoring_service.get_security_status()
            assert security_monitoring_status['monitoring_enabled'] == True
            
            # Test audit logging
            audit_status = await self.system.audit_logging_service.get_audit_status()
            assert audit_status['logging_enabled'] == True
            
            # Test incident response
            incident_status = await self.system.incident_response_service.get_incident_status()
            assert incident_status['response_enabled'] == True
            
            self._record_verification_result('monitoring_workflows', True, 'Monitoring workflows verified')
            logger.info("✓ Monitoring workflows verified")
            
        except Exception as e:
            self._record_verification_result('monitoring_workflows', False, str(e))
            logger.error(f"✗ Monitoring workflows verification failed: {e}")
            raise
    
    async def _test_workflow_execution(self):
        """Test workflow execution"""
        try:
            logger.info("Testing workflow execution...")
            
            # Test orchestrator workflow execution
            orchestrator = self.system.orchestrator
            
            # Test OSINT investigation workflow
            osint_workflow_params = {
                'sources': ['web', 'social_media'],
                'keywords': ['verification', 'test'],
                'filters': {'date_range': 'last_7_days'}
            }
            
            workflow_id = await orchestrator.execute_workflow('osint_investigation', osint_workflow_params)
            assert workflow_id is not None
            
            # Test digital forensics workflow
            forensics_workflow_params = {
                'source': 'test_evidence',
                'acquisition_type': 'forensic',
                'files': ['test_file1', 'test_file2'],
                'analysis_depth': 'comprehensive'
            }
            
            workflow_id = await orchestrator.execute_workflow('digital_forensics', forensics_workflow_params)
            assert workflow_id is not None
            
            # Test threat intelligence workflow
            threat_intelligence_workflow_params = {
                'sources': ['threat_feeds', 'osint'],
                'keywords': ['malware', 'threat'],
                'monitoring_type': 'continuous',
                'analysis_type': 'threat_assessment',
                'indicators': ['malware_signature', 'suspicious_ip']
            }
            
            workflow_id = await orchestrator.execute_workflow('threat_intelligence', threat_intelligence_workflow_params)
            assert workflow_id is not None
            
            # Test end-to-end security workflow
            end_to_end_config = {
                'user_id': 'verification_user',
                'target_systems': ['verification_server'],
                'threat_indicators': ['verification_threat'],
                'osint_parameters': {'keywords': ['verification', 'test']}
            }
            
            result = await self.system.execute_security_workflow('threat_hunting', end_to_end_config)
            assert 'workflow_type' in result
            assert result['workflow_type'] == 'threat_hunting'
            
            self._record_verification_result('workflow_execution', True, 'Workflow execution tested')
            logger.info("✓ Workflow execution tested")
            
        except Exception as e:
            self._record_verification_result('workflow_execution', False, str(e))
            logger.error(f"✗ Workflow execution testing failed: {e}")
            raise
    
    async def _generate_verification_report(self):
        """Generate comprehensive verification report"""
        try:
            logger.info("Generating verification report...")
            
            total_verifications = len(self.verification_results)
            passed_verifications = len([r for r in self.verification_results if r['passed']])
            failed_verifications = total_verifications - passed_verifications
            
            report = {
                'verification_suite': 'AMAS Workflow Verification',
                'timestamp': datetime.utcnow().isoformat(),
                'summary': {
                    'total_verifications': total_verifications,
                    'passed_verifications': passed_verifications,
                    'failed_verifications': failed_verifications,
                    'success_rate': (passed_verifications / total_verifications * 100) if total_verifications > 0 else 0
                },
                'verification_results': self.verification_results,
                'workflow_status': {
                    'core_workflows': 'verified',
                    'security_workflows': 'verified',
                    'agent_workflows': 'verified',
                    'integration_workflows': 'verified',
                    'monitoring_workflows': 'verified',
                    'workflow_execution': 'tested'
                }
            }
            
            # Save report to file
            with open('logs/workflow_verification_report.json', 'w') as f:
                json.dump(report, f, indent=2)
            
            # Log summary
            logger.info(f"Workflow Verification Report Summary:")
            logger.info(f"  Total Verifications: {total_verifications}")
            logger.info(f"  Passed: {passed_verifications}")
            logger.info(f"  Failed: {failed_verifications}")
            logger.info(f"  Success Rate: {report['summary']['success_rate']:.1f}%")
            
            if failed_verifications > 0:
                logger.warning(f"  Failed Verifications:")
                for result in self.verification_results:
                    if not result['passed']:
                        logger.warning(f"    - {result['verification_name']}: {result['message']}")
            
            logger.info("Workflow verification report generated: logs/workflow_verification_report.json")
            
        except Exception as e:
            logger.error(f"Failed to generate verification report: {e}")
    
    def _record_verification_result(self, verification_name: str, passed: bool, message: str):
        """Record verification result"""
        self.verification_results.append({
            'verification_name': verification_name,
            'passed': passed,
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        })

async def main():
    """Main verification execution"""
    try:
        verifier = WorkflowVerifier()
        await verifier.verify_all_workflows()
        
    except Exception as e:
        logger.error(f"Workflow verification failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())