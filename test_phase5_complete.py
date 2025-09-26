"""
AMAS Intelligence System - Phase 5 Complete Test Suite
Comprehensive testing for enhanced security and monitoring capabilities
"""

import asyncio
import logging
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/test_phase5.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Import the Phase 5 system
from main_phase5_complete import AMASPhase5System

class Phase5TestSuite:
    """Comprehensive test suite for AMAS Phase 5"""
    
    def __init__(self):
        self.test_results = []
        self.config = self._get_test_config()
        self.system = None
        
    def _get_test_config(self) -> Dict[str, Any]:
        """Get test configuration"""
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
            'jwt_secret': 'test_jwt_secret_key_2024_phase5',
            'encryption_key': 'test_encryption_key_2024_secure_32_chars_phase5',
            'security_secret_key': 'test_security_secret_key_2024_phase5',
            'audit_secret_key': 'test_audit_secret_key_2024_phase5',
            
            # API keys (test keys)
            'deepseek_api_key': 'test_deepseek_key',
            'glm_api_key': 'test_glm_key',
            'grok_api_key': 'test_grok_key',
            
            # Phase 5 specific configuration
            'audit_retention_days': 30,  # Shorter for testing
            'audit_rotation_size': 10 * 1024 * 1024,  # 10MB for testing
            'audit_compression': True,
            'audit_encryption': True,
            'audit_tamper_detection': True,
            'audit_compliance_mode': 'strict',
            'audit_storage_path': 'logs/test_audit',
            
            # Security monitoring
            'auto_containment': True,
            'escalation_threshold': 5,  # minutes for testing
            'max_concurrent_incidents': 5,
            'notification_channels': ['email'],
            'response_timeout': 10,  # minutes for testing
            
            # Performance optimization
            'cache_max_size': 100,
            'cache_default_ttl': 300,  # 5 minutes for testing
            'cache_strategy': 'lru',
            'cache_compression': True,
            'load_balance_strategy': 'round_robin',
            'health_check_interval': 10,  # seconds for testing
            'max_retries': 2,
            'timeout': 10,
            'max_memory': 100 * 1024 * 1024,  # 100MB for testing
            'max_cpu': 50.0,  # 50% for testing
            'max_connections': 100
        }
    
    async def run_all_tests(self):
        """Run all Phase 5 tests"""
        try:
            logger.info("Starting AMAS Phase 5 Complete Test Suite...")
            
            # Initialize system
            await self._test_system_initialization()
            
            # Test core functionality
            await self._test_core_functionality()
            
            # Test security services
            await self._test_security_services()
            
            # Test monitoring services
            await self._test_monitoring_services()
            
            # Test incident response
            await self._test_incident_response()
            
            # Test audit logging
            await self._test_audit_logging()
            
            # Test performance optimization
            await self._test_performance_optimization()
            
            # Test security workflows
            await self._test_security_workflows()
            
            # Test system integration
            await self._test_system_integration()
            
            # Generate test report
            await self._generate_test_report()
            
            logger.info("AMAS Phase 5 Complete Test Suite finished")
            
        except Exception as e:
            logger.error(f"Test suite error: {e}")
            raise
        finally:
            # Cleanup
            if self.system:
                await self.system.shutdown()
    
    async def _test_system_initialization(self):
        """Test system initialization"""
        try:
            logger.info("Testing system initialization...")
            
            self.system = AMASPhase5System(self.config)
            await self.system.initialize()
            
            # Verify system is initialized
            status = await self.system.get_system_status()
            assert status['system_status'] == 'operational'
            assert status['phase'] == 'phase5'
            assert len(status['agents']) == 8
            
            self._record_test_result('system_initialization', True, 'System initialized successfully')
            logger.info("✓ System initialization test passed")
            
        except Exception as e:
            self._record_test_result('system_initialization', False, str(e))
            logger.error(f"✗ System initialization test failed: {e}")
            raise
    
    async def _test_core_functionality(self):
        """Test core functionality"""
        try:
            logger.info("Testing core functionality...")
            
            # Test task submission
            task_data = {
                'type': 'osint',
                'description': 'Test OSINT task',
                'user_id': 'test_user',
                'priority': 2,
                'parameters': {'keywords': ['test']}
            }
            
            task_id = await self.system.submit_intelligence_task(task_data)
            assert task_id is not None
            
            # Test system status
            status = await self.system.get_system_status()
            assert 'orchestrator' in status
            assert 'security' in status
            assert 'monitoring' in status
            
            self._record_test_result('core_functionality', True, 'Core functionality working')
            logger.info("✓ Core functionality test passed")
            
        except Exception as e:
            self._record_test_result('core_functionality', False, str(e))
            logger.error(f"✗ Core functionality test failed: {e}")
            raise
    
    async def _test_security_services(self):
        """Test security services"""
        try:
            logger.info("Testing security services...")
            
            # Test security service health
            security_status = await self.system.security_service.health_check()
            assert security_status['status'] == 'healthy'
            
            # Test security monitoring
            security_monitoring_status = await self.system.security_monitoring_service.get_security_status()
            assert security_monitoring_status['monitoring_enabled'] == True
            
            # Test authentication
            auth_result = await self.system.security_service.authenticate_user('admin', 'admin123')
            assert auth_result['success'] == True
            assert 'token' in auth_result
            
            # Test JWT token verification
            token = auth_result['token']
            verify_result = await self.system.security_service.verify_jwt_token(token)
            assert verify_result['valid'] == True
            
            # Test data encryption
            test_data = "sensitive test data"
            encrypted_data = await self.system.security_service.encrypt_data(test_data)
            decrypted_data = await self.system.security_service.decrypt_data(encrypted_data)
            assert decrypted_data == test_data
            
            self._record_test_result('security_services', True, 'Security services working')
            logger.info("✓ Security services test passed")
            
        except Exception as e:
            self._record_test_result('security_services', False, str(e))
            logger.error(f"✗ Security services test failed: {e}")
            raise
    
    async def _test_monitoring_services(self):
        """Test monitoring services"""
        try:
            logger.info("Testing monitoring services...")
            
            # Test monitoring service
            monitoring_status = await self.system.monitoring_service.get_monitoring_status()
            assert monitoring_status['monitoring_enabled'] == True
            
            # Test performance service
            performance_status = await self.system.performance_service.get_performance_status()
            assert 'cache_stats' in performance_status
            
            # Test cache functionality
            cache_key = 'test_cache_key'
            cache_value = 'test_cache_value'
            await self.system.performance_service.set_in_cache(cache_key, cache_value)
            retrieved_value = await self.system.performance_service.get_from_cache(cache_key)
            assert retrieved_value == cache_value
            
            # Test load balancing
            llm_provider = await self.system.performance_service.select_llm_provider()
            assert llm_provider in ['ollama', 'deepseek', 'glm', 'grok']
            
            self._record_test_result('monitoring_services', True, 'Monitoring services working')
            logger.info("✓ Monitoring services test passed")
            
        except Exception as e:
            self._record_test_result('monitoring_services', False, str(e))
            logger.error(f"✗ Monitoring services test failed: {e}")
            raise
    
    async def _test_incident_response(self):
        """Test incident response"""
        try:
            logger.info("Testing incident response...")
            
            # Test incident creation
            incident_id = await self.system.incident_response_service.create_incident(
                severity='high',
                title='Test Security Incident',
                description='Test incident for validation',
                affected_systems=['test_server1', 'test_server2'],
                threat_indicators=['malware', 'suspicious_activity']
            )
            assert incident_id is not None
            
            # Test incident status
            incident_status = await self.system.incident_response_service.get_incident_status()
            assert incident_status['active_incidents'] >= 1
            
            # Test incident escalation
            escalation_result = await self.system.incident_response_service.escalate_incident(incident_id, 2)
            assert escalation_result == True
            
            # Test incident status update
            status_update = await self.system.incident_response_service.update_incident_status(
                incident_id, 'contained', {'containment_actions': ['isolated', 'quarantined']}
            )
            assert status_update == True
            
            self._record_test_result('incident_response', True, 'Incident response working')
            logger.info("✓ Incident response test passed")
            
        except Exception as e:
            self._record_test_result('incident_response', False, str(e))
            logger.error(f"✗ Incident response test failed: {e}")
            raise
    
    async def _test_audit_logging(self):
        """Test audit logging"""
        try:
            logger.info("Testing audit logging...")
            
            # Test audit event logging
            audit_event_id = await self.system.audit_logging_service.log_audit_event(
                event_type='user_action',
                audit_level='medium',
                user_id='test_user',
                action='test_action',
                resource='test_resource',
                result='success',
                details={'test': 'data'}
            )
            assert audit_event_id is not None
            
            # Test audit status
            audit_status = await self.system.audit_logging_service.get_audit_status()
            assert audit_status['logging_enabled'] == True
            assert audit_status['total_events'] >= 1
            
            # Test audit event retrieval
            audit_events = await self.system.audit_logging_service.get_audit_events()
            assert len(audit_events) >= 1
            
            # Test audit integrity verification
            integrity_status = await self.system.audit_logging_service.verify_audit_integrity()
            assert integrity_status['chain_integrity'] == True
            assert integrity_status['signature_verification'] == True
            assert integrity_status['tamper_detected'] == False
            
            self._record_test_result('audit_logging', True, 'Audit logging working')
            logger.info("✓ Audit logging test passed")
            
        except Exception as e:
            self._record_test_result('audit_logging', False, str(e))
            logger.error(f"✗ Audit logging test failed: {e}")
            raise
    
    async def _test_performance_optimization(self):
        """Test performance optimization"""
        try:
            logger.info("Testing performance optimization...")
            
            # Test cache performance
            cache_stats = await self.system.performance_service.get_cache_stats()
            assert 'hit_rate' in cache_stats
            assert 'size' in cache_stats
            
            # Test cache operations
            test_keys = ['key1', 'key2', 'key3']
            test_values = ['value1', 'value2', 'value3']
            
            for key, value in zip(test_keys, test_values):
                await self.system.performance_service.set_in_cache(key, value)
            
            for key, expected_value in zip(test_keys, test_values):
                retrieved_value = await self.system.performance_service.get_from_cache(key)
                assert retrieved_value == expected_value
            
            # Test cache clearing
            clear_result = await self.system.performance_service.clear_cache()
            assert clear_result == True
            
            # Test agent selection
            agent_id = await self.system.performance_service.select_agent('osint')
            assert agent_id in ['osint_001', 'investigation_001', 'forensics_001', 'data_analysis_001']
            
            self._record_test_result('performance_optimization', True, 'Performance optimization working')
            logger.info("✓ Performance optimization test passed")
            
        except Exception as e:
            self._record_test_result('performance_optimization', False, str(e))
            logger.error(f"✗ Performance optimization test failed: {e}")
            raise
    
    async def _test_security_workflows(self):
        """Test security workflows"""
        try:
            logger.info("Testing security workflows...")
            
            # Test threat hunting workflow
            threat_hunting_result = await self.system.execute_security_workflow(
                'threat_hunting',
                {
                    'user_id': 'test_security_analyst',
                    'target_systems': ['test_server1', 'test_server2'],
                    'threat_indicators': ['malware', 'suspicious_network'],
                    'osint_parameters': {'keywords': ['threat', 'malware']}
                }
            )
            assert 'workflow_type' in threat_hunting_result
            assert threat_hunting_result['workflow_type'] == 'threat_hunting'
            
            # Test incident response workflow
            incident_response_result = await self.system.execute_security_workflow(
                'incident_response',
                {
                    'user_id': 'test_incident_responder',
                    'severity': 'high',
                    'title': 'Test Incident',
                    'description': 'Test incident response workflow',
                    'affected_systems': ['test_server1'],
                    'threat_indicators': ['malware']
                }
            )
            assert 'workflow_type' in incident_response_result
            assert incident_response_result['workflow_type'] == 'incident_response'
            
            # Test security assessment workflow
            security_assessment_result = await self.system.execute_security_workflow(
                'security_assessment',
                {
                    'user_id': 'test_security_assessor',
                    'assessment_parameters': {'scope': 'full'},
                    'compliance_standards': ['SOX', 'GDPR']
                }
            )
            assert 'workflow_type' in security_assessment_result
            assert security_assessment_result['workflow_type'] == 'security_assessment'
            
            self._record_test_result('security_workflows', True, 'Security workflows working')
            logger.info("✓ Security workflows test passed")
            
        except Exception as e:
            self._record_test_result('security_workflows', False, str(e))
            logger.error(f"✗ Security workflows test failed: {e}")
            raise
    
    async def _test_system_integration(self):
        """Test system integration"""
        try:
            logger.info("Testing system integration...")
            
            # Test comprehensive system status
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
            
            # Test end-to-end security workflow
            end_to_end_result = await self.system.execute_security_workflow(
                'threat_hunting',
                {
                    'user_id': 'integration_test_user',
                    'target_systems': ['integration_test_server'],
                    'threat_indicators': ['integration_test_threat'],
                    'osint_parameters': {'keywords': ['integration', 'test']}
                }
            )
            assert 'workflow_type' in end_to_end_result
            assert end_to_end_result['workflow_type'] == 'threat_hunting'
            
            self._record_test_result('system_integration', True, 'System integration working')
            logger.info("✓ System integration test passed")
            
        except Exception as e:
            self._record_test_result('system_integration', False, str(e))
            logger.error(f"✗ System integration test failed: {e}")
            raise
    
    async def _generate_test_report(self):
        """Generate comprehensive test report"""
        try:
            logger.info("Generating test report...")
            
            total_tests = len(self.test_results)
            passed_tests = len([r for r in self.test_results if r['passed']])
            failed_tests = total_tests - passed_tests
            
            report = {
                'test_suite': 'AMAS Phase 5 Complete Test Suite',
                'timestamp': datetime.utcnow().isoformat(),
                'summary': {
                    'total_tests': total_tests,
                    'passed_tests': passed_tests,
                    'failed_tests': failed_tests,
                    'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0
                },
                'test_results': self.test_results
            }
            
            # Save report to file
            with open('logs/phase5_test_report.json', 'w') as f:
                json.dump(report, f, indent=2)
            
            # Log summary
            logger.info(f"Test Report Summary:")
            logger.info(f"  Total Tests: {total_tests}")
            logger.info(f"  Passed: {passed_tests}")
            logger.info(f"  Failed: {failed_tests}")
            logger.info(f"  Success Rate: {report['summary']['success_rate']:.1f}%")
            
            if failed_tests > 0:
                logger.warning(f"  Failed Tests:")
                for result in self.test_results:
                    if not result['passed']:
                        logger.warning(f"    - {result['test_name']}: {result['message']}")
            
            logger.info("Test report generated: logs/phase5_test_report.json")
            
        except Exception as e:
            logger.error(f"Failed to generate test report: {e}")
    
    def _record_test_result(self, test_name: str, passed: bool, message: str):
        """Record test result"""
        self.test_results.append({
            'test_name': test_name,
            'passed': passed,
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        })

async def main():
    """Main test execution"""
    try:
        test_suite = Phase5TestSuite()
        await test_suite.run_all_tests()
        
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())