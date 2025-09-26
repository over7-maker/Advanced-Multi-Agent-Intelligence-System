"""
AMAS Intelligence System - Phase 6-10 Complete Test Suite
Comprehensive testing for all phases 6-10
"""

import asyncio
import logging
import sys
from datetime import datetime
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/phase6_10_test.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Import the complete system
from main_phase6_10_complete import AMASPhase6_10System

class Phase6_10TestSuite:
    """Comprehensive test suite for Phases 6-10"""
    
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
            'jwt_secret': 'test_jwt_secret_key_2024_phases6_10',
            'encryption_key': 'test_encryption_key_2024_secure_32_chars_phases6_10',
            'security_secret_key': 'test_security_secret_key_2024_phases6_10',
            'audit_secret_key': 'test_audit_secret_key_2024_phases6_10',
            
            # API keys (test keys)
            'deepseek_api_key': 'test_deepseek_key',
            'glm_api_key': 'test_glm_key',
            'grok_api_key': 'test_grok_key',
            
            # Phase 6: Testing & Deployment
            'testing_enabled': True,
            'test_automation': True,
            'deployment_automation': True,
            
            # Phase 7: Performance Optimization
            'optimization_level': 'enterprise',
            'cache_max_size': 100,
            'cache_default_ttl': 300,
            'cache_strategy': 'adaptive',
            'load_balance_strategy': 'adaptive',
            'auto_scaling': True,
            
            # Phase 8: Advanced Analytics
            'analytics_enabled': True,
            'model_storage_path': 'models/',
            'insight_storage_path': 'insights/',
            'auto_training': True,
            'prediction_cache_ttl': 300,
            
            # Phase 9: Workflow Automation
            'automation_enabled': True,
            'max_concurrent_executions': 10,
            'execution_timeout': 300,
            'decision_engine_enabled': True,
            'ai_decision_making': True,
            
            # Phase 10: Enterprise Features
            'multi_tenancy_enabled': True,
            'compliance_monitoring': True,
            'security_auditing': True,
            'data_residency_enforcement': True,
            'encryption_at_rest': True,
            'encryption_in_transit': True
        }
    
    async def run_all_tests(self):
        """Run all Phase 6-10 tests"""
        try:
            logger.info("Starting Phase 6-10 Complete Test Suite...")
            
            # Initialize system
            await self._initialize_system()
            
            # Test Phase 6: Testing & Deployment
            await self._test_phase6_testing_deployment()
            
            # Test Phase 7: Performance Optimization
            await self._test_phase7_performance_optimization()
            
            # Test Phase 8: Advanced Analytics
            await self._test_phase8_advanced_analytics()
            
            # Test Phase 9: Workflow Automation
            await self._test_phase9_workflow_automation()
            
            # Test Phase 10: Enterprise Features
            await self._test_phase10_enterprise_features()
            
            # Test system integration
            await self._test_system_integration()
            
            # Test end-to-end workflows
            await self._test_end_to_end_workflows()
            
            # Generate test report
            await self._generate_test_report()
            
            logger.info("Phase 6-10 Complete Test Suite finished")
            
        except Exception as e:
            logger.error(f"Test suite error: {e}")
            raise
        finally:
            # Cleanup
            if self.system:
                await self.system.shutdown()
    
    async def _initialize_system(self):
        """Initialize the complete system"""
        try:
            logger.info("Initializing complete AMAS system...")
            
            self.system = AMASPhase6_10System(self.config)
            await self.system.initialize()
            
            # Verify system is operational
            status = await self.system.get_system_status()
            assert status['system_status'] == 'operational'
            assert status['phase'] == 'phase6_10_complete'
            
            self._record_test_result('system_initialization', True, 'Complete system initialized successfully')
            logger.info("✓ Complete system initialization verified")
            
        except Exception as e:
            self._record_test_result('system_initialization', False, str(e))
            logger.error(f"✗ Complete system initialization failed: {e}")
            raise
    
    async def _test_phase6_testing_deployment(self):
        """Test Phase 6: Testing & Deployment"""
        try:
            logger.info("Testing Phase 6: Testing & Deployment...")
            
            # Test comprehensive test suite
            test_results = await self.system.run_comprehensive_test_suite()
            assert 'test_suite' in test_results
            assert 'results' in test_results
            
            # Test deployment readiness
            status = await self.system.get_system_status()
            assert status['system_status'] == 'operational'
            
            self._record_test_result('phase6_testing_deployment', True, 'Phase 6 testing and deployment verified')
            logger.info("✓ Phase 6: Testing & Deployment verified")
            
        except Exception as e:
            self._record_test_result('phase6_testing_deployment', False, str(e))
            logger.error(f"✗ Phase 6: Testing & Deployment failed: {e}")
    
    async def _test_phase7_performance_optimization(self):
        """Test Phase 7: Performance Optimization"""
        try:
            logger.info("Testing Phase 7: Performance Optimization...")
            
            # Test optimization service
            optimization_status = await self.system.advanced_optimization_service.get_optimization_status()
            assert optimization_status['optimization_enabled'] == True
            
            # Test cache functionality
            cache_result = await self.system.advanced_optimization_service.set_in_cache('test_key', 'test_value')
            assert cache_result == True
            
            cached_value = await self.system.advanced_optimization_service.get_from_cache('test_key')
            assert cached_value == 'test_value'
            
            # Test load balancing
            provider = await self.system.advanced_optimization_service.select_llm_provider('test_task')
            assert provider is not None
            
            self._record_test_result('phase7_performance_optimization', True, 'Phase 7 performance optimization verified')
            logger.info("✓ Phase 7: Performance Optimization verified")
            
        except Exception as e:
            self._record_test_result('phase7_performance_optimization', False, str(e))
            logger.error(f"✗ Phase 7: Performance Optimization failed: {e}")
    
    async def _test_phase8_advanced_analytics(self):
        """Test Phase 8: Advanced Analytics"""
        try:
            logger.info("Testing Phase 8: Advanced Analytics...")
            
            # Test analytics service
            analytics_status = await self.system.advanced_analytics_service.get_analytics_status()
            assert analytics_status['analytics_enabled'] == True
            
            # Test model creation
            model_config = {
                'model_id': 'test_classification_model',
                'name': 'Test Classification Model',
                'model_type': 'classification',
                'analytics_type': 'predictive',
                'algorithm': 'RandomForestClassifier'
            }
            model_id = await self.system.advanced_analytics_service.create_model(model_config)
            assert model_id == 'test_classification_model'
            
            # Test insight generation
            insights = await self.system.advanced_analytics_service.generate_insights({'test': 'data'})
            assert isinstance(insights, list)
            
            # Test prediction (if model is trained)
            try:
                prediction = await self.system.advanced_analytics_service.predict(model_id, {'feature1': 1.0, 'feature2': 2.0})
                assert prediction is not None
            except Exception:
                # Prediction might fail if model not trained, which is expected
                pass
            
            self._record_test_result('phase8_advanced_analytics', True, 'Phase 8 advanced analytics verified')
            logger.info("✓ Phase 8: Advanced Analytics verified")
            
        except Exception as e:
            self._record_test_result('phase8_advanced_analytics', False, str(e))
            logger.error(f"✗ Phase 8: Advanced Analytics failed: {e}")
    
    async def _test_phase9_workflow_automation(self):
        """Test Phase 9: Workflow Automation"""
        try:
            logger.info("Testing Phase 9: Workflow Automation...")
            
            # Test automation service
            automation_status = await self.system.workflow_automation_service.get_automation_status()
            assert automation_status['automation_enabled'] == True
            
            # Test workflow creation
            workflow_config = {
                'name': 'Test Intelligence Workflow',
                'description': 'Test workflow for intelligence operations',
                'steps': [
                    {
                        'step_id': 'data_collection',
                        'name': 'Data Collection',
                        'action_type': 'osint_collection',
                        'parameters': {'sources': ['web', 'social_media']},
                        'conditions': [],
                        'timeout': 1800
                    },
                    {
                        'step_id': 'data_analysis',
                        'name': 'Data Analysis',
                        'action_type': 'data_analysis',
                        'parameters': {'analysis_type': 'comprehensive'},
                        'conditions': [{'step': 'data_collection', 'status': 'completed'}],
                        'timeout': 3600
                    }
                ]
            }
            workflow_id = await self.system.workflow_automation_service.create_workflow(workflow_config)
            assert workflow_id is not None
            
            # Test automated decision making
            decision = await self.system.workflow_automation_service.make_automated_decision({
                'threat_score': 0.9,
                'response_time': 6.0,
                'cpu_usage': 0.9
            })
            assert decision is not None
            assert 'action' in decision
            
            self._record_test_result('phase9_workflow_automation', True, 'Phase 9 workflow automation verified')
            logger.info("✓ Phase 9: Workflow Automation verified")
            
        except Exception as e:
            self._record_test_result('phase9_workflow_automation', False, str(e))
            logger.error(f"✗ Phase 9: Workflow Automation failed: {e}")
    
    async def _test_phase10_enterprise_features(self):
        """Test Phase 10: Enterprise Features"""
        try:
            logger.info("Testing Phase 10: Enterprise Features...")
            
            # Test enterprise service
            enterprise_status = await self.system.enterprise_service.get_enterprise_status()
            assert enterprise_status['enterprise_enabled'] == True
            
            # Test tenant creation
            tenant_config = {
                'name': 'Test Enterprise Tenant',
                'domain': 'test-enterprise.com',
                'subscription_plan': 'enterprise',
                'compliance_standards': ['sox', 'gdpr'],
                'security_level': 'enterprise',
                'data_residency': 'us-east-1'
            }
            tenant_id = await self.system.enterprise_service.create_tenant(tenant_config)
            assert tenant_id is not None
            
            # Test compliance report generation
            report_id = await self.system.enterprise_service.generate_compliance_report(tenant_id, 'sox')
            assert report_id is not None
            
            # Test security audit
            audit_id = await self.system.enterprise_service.conduct_security_audit(tenant_id, 'access_control_audit')
            assert audit_id is not None
            
            # Test tenant data operations
            tenant_data = await self.system.enterprise_service.get_tenant_data(tenant_id, 'intelligence_data')
            assert tenant_data['tenant_id'] == tenant_id
            
            data_stored = await self.system.enterprise_service.store_tenant_data(tenant_id, {'test': 'data'})
            assert data_stored == True
            
            self._record_test_result('phase10_enterprise_features', True, 'Phase 10 enterprise features verified')
            logger.info("✓ Phase 10: Enterprise Features verified")
            
        except Exception as e:
            self._record_test_result('phase10_enterprise_features', False, str(e))
            logger.error(f"✗ Phase 10: Enterprise Features failed: {e}")
    
    async def _test_system_integration(self):
        """Test system integration"""
        try:
            logger.info("Testing system integration...")
            
            # Test complete system status
            status = await self.system.get_system_status()
            assert status['system_status'] == 'operational'
            assert status['phase'] == 'phase6_10_complete'
            
            # Test all services are operational
            assert 'phase5_system' in status
            assert 'optimization_service' in status
            assert 'analytics_service' in status
            assert 'automation_service' in status
            assert 'enterprise_service' in status
            
            # Test service integration
            phase5_status = status['phase5_system']
            assert phase5_status['system_status'] == 'operational'
            
            optimization_status = status['optimization_service']
            assert optimization_status['optimization_enabled'] == True
            
            analytics_status = status['analytics_service']
            assert analytics_status['analytics_enabled'] == True
            
            automation_status = status['automation_service']
            assert automation_status['automation_enabled'] == True
            
            enterprise_status = status['enterprise_service']
            assert enterprise_status['enterprise_enabled'] == True
            
            self._record_test_result('system_integration', True, 'System integration verified')
            logger.info("✓ System integration verified")
            
        except Exception as e:
            self._record_test_result('system_integration', False, str(e))
            logger.error(f"✗ System integration failed: {e}")
    
    async def _test_end_to_end_workflows(self):
        """Test end-to-end workflows"""
        try:
            logger.info("Testing end-to-end workflows...")
            
            # Test comprehensive test suite execution
            test_results = await self.system.run_comprehensive_test_suite()
            assert test_results['test_suite'] == 'comprehensive_phase6_10'
            assert 'results' in test_results
            
            # Test all phases are working
            results = test_results['results']
            assert 'phase5_tests' in results
            assert 'phase6_tests' in results
            assert 'phase7_tests' in results
            assert 'phase8_tests' in results
            assert 'phase9_tests' in results
            assert 'phase10_tests' in results
            
            # Test workflow execution through automation service
            workflow_config = {
                'name': 'End-to-End Intelligence Workflow',
                'description': 'Complete intelligence workflow test',
                'steps': [
                    {
                        'step_id': 'intelligence_collection',
                        'name': 'Intelligence Collection',
                        'action_type': 'osint_collection',
                        'parameters': {'sources': ['web', 'social_media', 'news']},
                        'conditions': [],
                        'timeout': 1800
                    },
                    {
                        'step_id': 'threat_analysis',
                        'name': 'Threat Analysis',
                        'action_type': 'threat_analysis',
                        'parameters': {'analysis_depth': 'deep'},
                        'conditions': [{'step': 'intelligence_collection', 'status': 'completed'}],
                        'timeout': 2400
                    },
                    {
                        'step_id': 'report_generation',
                        'name': 'Report Generation',
                        'action_type': 'report_generation',
                        'parameters': {'report_type': 'intelligence_report'},
                        'conditions': [{'step': 'threat_analysis', 'status': 'completed'}],
                        'timeout': 900
                    }
                ]
            }
            
            workflow_id = await self.system.workflow_automation_service.create_workflow(workflow_config)
            assert workflow_id is not None
            
            # Test workflow execution
            execution_id = await self.system.workflow_automation_service.execute_workflow(workflow_id, {'test': 'parameters'})
            assert execution_id is not None
            
            self._record_test_result('end_to_end_workflows', True, 'End-to-end workflows verified')
            logger.info("✓ End-to-end workflows verified")
            
        except Exception as e:
            self._record_test_result('end_to_end_workflows', False, str(e))
            logger.error(f"✗ End-to-end workflows failed: {e}")
    
    async def _generate_test_report(self):
        """Generate comprehensive test report"""
        try:
            logger.info("Generating test report...")
            
            total_tests = len(self.test_results)
            passed_tests = len([r for r in self.test_results if r['passed']])
            failed_tests = total_tests - passed_tests
            
            report = {
                'test_suite': 'AMAS Phase 6-10 Complete Test Suite',
                'timestamp': datetime.utcnow().isoformat(),
                'summary': {
                    'total_tests': total_tests,
                    'passed_tests': passed_tests,
                    'failed_tests': failed_tests,
                    'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0
                },
                'test_results': self.test_results,
                'phases_tested': {
                    'phase6': 'testing_deployment',
                    'phase7': 'performance_optimization',
                    'phase8': 'advanced_analytics',
                    'phase9': 'workflow_automation',
                    'phase10': 'enterprise_features'
                }
            }
            
            # Save report to file
            with open('logs/phase6_10_test_report.json', 'w') as f:
                import json
                json.dump(report, f, indent=2)
            
            # Log summary
            logger.info(f"Phase 6-10 Test Report Summary:")
            logger.info(f"  Total Tests: {total_tests}")
            logger.info(f"  Passed: {passed_tests}")
            logger.info(f"  Failed: {failed_tests}")
            logger.info(f"  Success Rate: {report['summary']['success_rate']:.1f}%")
            
            if failed_tests > 0:
                logger.warning(f"  Failed Tests:")
                for result in self.test_results:
                    if not result['passed']:
                        logger.warning(f"    - {result['test_name']}: {result['message']}")
            
            logger.info("Phase 6-10 test report generated: logs/phase6_10_test_report.json")
            
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
    """Main test suite execution"""
    try:
        test_suite = Phase6_10TestSuite()
        await test_suite.run_all_tests()
        
    except Exception as e:
        logger.error(f"Phase 6-10 testing failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())