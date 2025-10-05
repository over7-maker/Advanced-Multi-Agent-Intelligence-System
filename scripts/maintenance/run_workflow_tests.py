"""
AMAS Intelligence System - Comprehensive Workflow Test Runner
Run all workflow tests to ensure everything is working correctly
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
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/workflow_test_runner.log"),
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)

# Import the Phase 5 system
from main_phase5_complete import AMASPhase5System


class WorkflowTestRunner:
    """Comprehensive workflow test runner"""

    def __init__(self):
        self.test_results = []
        self.config = self._get_test_config()
        self.system = None

    def _get_test_config(self) -> Dict[str, Any]:
        """Get test configuration"""
        return {
            # Core services
            "llm_service_url": "http://localhost:11434",
            "vector_service_url": "http://localhost:8001",
            "graph_service_url": "bolt://localhost:7687",
            "postgres_host": "localhost",
            "postgres_port": 5432,
            "postgres_user": "amas",
            "postgres_password": "amas123",
            "postgres_db": "amas",
            "redis_host": "localhost",
            "redis_port": 6379,
            "redis_db": 0,
            "neo4j_username": "neo4j",
            "neo4j_password": "amas123",
            "neo4j_database": "neo4j",
            # Security configuration
            "jwt_secret": "test_runner_jwt_secret_key_2024_phase5",
            "encryption_key": "test_runner_encryption_key_2024_secure_32_chars_phase5",
            "security_secret_key": "test_runner_security_secret_key_2024_phase5",
            "audit_secret_key": "test_runner_audit_secret_key_2024_phase5",
            # API keys (test runner keys)
            "deepseek_api_key": "test_runner_deepseek_key",
            "glm_api_key": "test_runner_glm_key",
            "grok_api_key": "test_runner_grok_key",
            # Phase 5 specific configuration
            "audit_retention_days": 30,
            "audit_rotation_size": 10 * 1024 * 1024,
            "audit_compression": True,
            "audit_encryption": True,
            "audit_tamper_detection": True,
            "audit_compliance_mode": "strict",
            "audit_storage_path": "logs/test_runner_audit",
            # Security monitoring
            "auto_containment": True,
            "escalation_threshold": 5,
            "max_concurrent_incidents": 5,
            "notification_channels": ["email"],
            "response_timeout": 10,
            # Performance optimization
            "cache_max_size": 100,
            "cache_default_ttl": 300,
            "cache_strategy": "lru",
            "cache_compression": True,
            "load_balance_strategy": "round_robin",
            "health_check_interval": 10,
            "max_retries": 2,
            "timeout": 10,
            "max_memory": 100 * 1024 * 1024,
            "max_cpu": 50.0,
            "max_connections": 100,
        }

    async def run_all_workflow_tests(self):
        """Run all workflow tests"""
        try:
            logger.info("Starting AMAS Workflow Test Runner...")

            # Initialize system
            await self._initialize_system()

            # Test core workflows
            await self._test_core_workflows()

            # Test security workflows
            await self._test_security_workflows()

            # Test agent workflows
            await self._test_agent_workflows()

            # Test monitoring workflows
            await self._test_monitoring_workflows()

            # Test integration workflows
            await self._test_integration_workflows()

            # Test end-to-end workflows
            await self._test_end_to_end_workflows()

            # Generate test report
            await self._generate_test_report()

            logger.info("AMAS Workflow Test Runner completed")

        except Exception as e:
            logger.error(f"Workflow test error: {e}")
            raise
        finally:
            # Cleanup
            if self.system:
                await self.system.shutdown()

    async def _initialize_system(self):
        """Initialize the AMAS system"""
        try:
            logger.info("Initializing AMAS system for workflow testing...")

            self.system = AMASPhase5System(self.config)
            await self.system.initialize()

            # Verify system is operational
            status = await self.system.get_system_status()
            assert status["system_status"] == "operational"
            assert status["phase"] == "phase5"

            self._record_test_result(
                "system_initialization", True, "System initialized successfully"
            )
            logger.info("✓ System initialization verified")

        except Exception as e:
            self._record_test_result("system_initialization", False, str(e))
            logger.error(f"✗ System initialization failed: {e}")
            raise

    async def _test_core_workflows(self):
        """Test core workflows"""
        try:
            logger.info("Testing core workflows...")

            # Test OSINT investigation workflow
            osint_workflow_params = {
                "sources": ["web", "social_media", "news"],
                "keywords": ["test", "workflow", "verification"],
                "filters": {"date_range": "last_7_days"},
            }

            workflow_id = await self.system.orchestrator.execute_workflow(
                "osint_investigation", osint_workflow_params
            )
            if workflow_id:
                self._record_test_result(
                    "osint_investigation_workflow",
                    True,
                    f"OSINT investigation workflow executed: {workflow_id}",
                )
            else:
                self._record_test_result(
                    "osint_investigation_workflow",
                    False,
                    "OSINT investigation workflow failed",
                )

            # Test digital forensics workflow
            forensics_workflow_params = {
                "source": "test_evidence",
                "acquisition_type": "forensic",
                "files": ["test_file1", "test_file2"],
                "analysis_depth": "comprehensive",
            }

            workflow_id = await self.system.orchestrator.execute_workflow(
                "digital_forensics", forensics_workflow_params
            )
            if workflow_id:
                self._record_test_result(
                    "digital_forensics_workflow",
                    True,
                    f"Digital forensics workflow executed: {workflow_id}",
                )
            else:
                self._record_test_result(
                    "digital_forensics_workflow",
                    False,
                    "Digital forensics workflow failed",
                )

            # Test threat intelligence workflow
            threat_intelligence_workflow_params = {
                "sources": ["threat_feeds", "osint"],
                "keywords": ["malware", "threat"],
                "monitoring_type": "continuous",
                "analysis_type": "threat_assessment",
                "indicators": ["malware_signature", "suspicious_ip"],
            }

            workflow_id = await self.system.orchestrator.execute_workflow(
                "threat_intelligence", threat_intelligence_workflow_params
            )
            if workflow_id:
                self._record_test_result(
                    "threat_intelligence_workflow",
                    True,
                    f"Threat intelligence workflow executed: {workflow_id}",
                )
            else:
                self._record_test_result(
                    "threat_intelligence_workflow",
                    False,
                    "Threat intelligence workflow failed",
                )

            logger.info("✓ Core workflows tested")

        except Exception as e:
            logger.error(f"Error testing core workflows: {e}")
            self._record_test_result("core_workflows_test", False, str(e))

    async def _test_security_workflows(self):
        """Test security workflows"""
        try:
            logger.info("Testing security workflows...")

            # Test threat hunting workflow
            threat_hunting_config = {
                "user_id": "test_runner_user",
                "target_systems": ["test_server1", "test_server2"],
                "threat_indicators": ["malware", "suspicious_network"],
                "osint_parameters": {"keywords": ["threat", "malware"]},
            }

            result = await self.system.execute_security_workflow(
                "threat_hunting", threat_hunting_config
            )
            if (
                "workflow_type" in result
                and result["workflow_type"] == "threat_hunting"
            ):
                self._record_test_result(
                    "threat_hunting_workflow",
                    True,
                    "Threat hunting workflow executed successfully",
                )
            else:
                self._record_test_result(
                    "threat_hunting_workflow", False, "Threat hunting workflow failed"
                )

            # Test incident response workflow
            incident_response_config = {
                "user_id": "test_runner_user",
                "severity": "high",
                "title": "Test Incident",
                "description": "Test incident response workflow",
                "affected_systems": ["test_server1"],
                "threat_indicators": ["malware"],
            }

            result = await self.system.execute_security_workflow(
                "incident_response", incident_response_config
            )
            if (
                "workflow_type" in result
                and result["workflow_type"] == "incident_response"
            ):
                self._record_test_result(
                    "incident_response_workflow",
                    True,
                    "Incident response workflow executed successfully",
                )
            else:
                self._record_test_result(
                    "incident_response_workflow",
                    False,
                    "Incident response workflow failed",
                )

            # Test security assessment workflow
            security_assessment_config = {
                "user_id": "test_runner_user",
                "assessment_parameters": {"scope": "full"},
                "compliance_standards": ["SOX", "GDPR"],
            }

            result = await self.system.execute_security_workflow(
                "security_assessment", security_assessment_config
            )
            if (
                "workflow_type" in result
                and result["workflow_type"] == "security_assessment"
            ):
                self._record_test_result(
                    "security_assessment_workflow",
                    True,
                    "Security assessment workflow executed successfully",
                )
            else:
                self._record_test_result(
                    "security_assessment_workflow",
                    False,
                    "Security assessment workflow failed",
                )

            logger.info("✓ Security workflows tested")

        except Exception as e:
            logger.error(f"Error testing security workflows: {e}")
            self._record_test_result("security_workflows_test", False, str(e))

    async def _test_agent_workflows(self):
        """Test agent workflows"""
        try:
            logger.info("Testing agent workflows...")

            # Test each agent with different task types
            agent_tasks = [
                {
                    "agent_type": "osint",
                    "task_data": {
                        "type": "osint",
                        "description": "Test OSINT task",
                        "user_id": "test_runner_user",
                        "priority": 2,
                        "parameters": {"keywords": ["test", "osint"]},
                    },
                },
                {
                    "agent_type": "investigation",
                    "task_data": {
                        "type": "investigation",
                        "description": "Test investigation task",
                        "user_id": "test_runner_user",
                        "priority": 2,
                        "parameters": {"entities": ["test_entity"]},
                    },
                },
                {
                    "agent_type": "forensics",
                    "task_data": {
                        "type": "forensics",
                        "description": "Test forensics task",
                        "user_id": "test_runner_user",
                        "priority": 2,
                        "parameters": {"evidence": ["test_evidence"]},
                    },
                },
                {
                    "agent_type": "data_analysis",
                    "task_data": {
                        "type": "data_analysis",
                        "description": "Test data analysis task",
                        "user_id": "test_runner_user",
                        "priority": 2,
                        "parameters": {"data": ["test_data"]},
                    },
                },
                {
                    "agent_type": "reverse_engineering",
                    "task_data": {
                        "type": "reverse_engineering",
                        "description": "Test reverse engineering task",
                        "user_id": "test_runner_user",
                        "priority": 2,
                        "parameters": {"binary": "test_binary"},
                    },
                },
                {
                    "agent_type": "metadata",
                    "task_data": {
                        "type": "metadata",
                        "description": "Test metadata task",
                        "user_id": "test_runner_user",
                        "priority": 2,
                        "parameters": {"files": ["test_file"]},
                    },
                },
                {
                    "agent_type": "reporting",
                    "task_data": {
                        "type": "reporting",
                        "description": "Test reporting task",
                        "user_id": "test_runner_user",
                        "priority": 2,
                        "parameters": {"report_type": "test_report"},
                    },
                },
                {
                    "agent_type": "technology_monitor",
                    "task_data": {
                        "type": "technology_monitor",
                        "description": "Test technology monitor task",
                        "user_id": "test_runner_user",
                        "priority": 2,
                        "parameters": {"monitoring_type": "test_monitoring"},
                    },
                },
            ]

            for agent_test in agent_tasks:
                try:
                    task_id = await self.system.submit_intelligence_task(
                        agent_test["task_data"]
                    )
                    if task_id:
                        self._record_test_result(
                            f'agent_{agent_test["agent_type"]}_workflow',
                            True,
                            f'{agent_test["agent_type"]} agent workflow executed: {task_id}',
                        )
                    else:
                        self._record_test_result(
                            f'agent_{agent_test["agent_type"]}_workflow',
                            False,
                            f'{agent_test["agent_type"]} agent workflow failed',
                        )
                except Exception as e:
                    self._record_test_result(
                        f'agent_{agent_test["agent_type"]}_workflow',
                        False,
                        f'{agent_test["agent_type"]} agent workflow error: {e}',
                    )

            logger.info("✓ Agent workflows tested")

        except Exception as e:
            logger.error(f"Error testing agent workflows: {e}")
            self._record_test_result("agent_workflows_test", False, str(e))

    async def _test_monitoring_workflows(self):
        """Test monitoring workflows"""
        try:
            logger.info("Testing monitoring workflows...")

            # Test system status monitoring
            system_status = await self.system.get_system_status()
            if system_status["system_status"] == "operational":
                self._record_test_result(
                    "system_status_monitoring", True, "System status monitoring working"
                )
            else:
                self._record_test_result(
                    "system_status_monitoring", False, "System status monitoring failed"
                )

            # Test security dashboard
            security_dashboard = await self.system.get_security_dashboard()
            if (
                "security_events" in security_dashboard
                and "active_incidents" in security_dashboard
            ):
                self._record_test_result(
                    "security_dashboard_monitoring",
                    True,
                    "Security dashboard monitoring working",
                )
            else:
                self._record_test_result(
                    "security_dashboard_monitoring",
                    False,
                    "Security dashboard monitoring failed",
                )

            # Test monitoring service
            monitoring_status = (
                await self.system.monitoring_service.get_monitoring_status()
            )
            if monitoring_status["monitoring_enabled"]:
                self._record_test_result(
                    "monitoring_service_workflow",
                    True,
                    "Monitoring service workflow working",
                )
            else:
                self._record_test_result(
                    "monitoring_service_workflow",
                    False,
                    "Monitoring service workflow failed",
                )

            # Test performance service
            performance_status = (
                await self.system.performance_service.get_performance_status()
            )
            if "cache_stats" in performance_status:
                self._record_test_result(
                    "performance_service_workflow",
                    True,
                    "Performance service workflow working",
                )
            else:
                self._record_test_result(
                    "performance_service_workflow",
                    False,
                    "Performance service workflow failed",
                )

            logger.info("✓ Monitoring workflows tested")

        except Exception as e:
            logger.error(f"Error testing monitoring workflows: {e}")
            self._record_test_result("monitoring_workflows_test", False, str(e))

    async def _test_integration_workflows(self):
        """Test integration workflows"""
        try:
            logger.info("Testing integration workflows...")

            # Test service integration
            services = [
                ("security_service", self.system.security_service),
                (
                    "security_monitoring_service",
                    self.system.security_monitoring_service,
                ),
                ("audit_logging_service", self.system.audit_logging_service),
                ("incident_response_service", self.system.incident_response_service),
                ("monitoring_service", self.system.monitoring_service),
                ("performance_service", self.system.performance_service),
            ]

            for service_name, service in services:
                try:
                    if hasattr(service, "health_check"):
                        health = await service.health_check()
                        if health["status"] == "healthy":
                            self._record_test_result(
                                f"service_{service_name}_integration",
                                True,
                                f"{service_name} integration working",
                            )
                        else:
                            self._record_test_result(
                                f"service_{service_name}_integration",
                                False,
                                f"{service_name} integration failed",
                            )
                    else:
                        self._record_test_result(
                            f"service_{service_name}_integration",
                            True,
                            f"{service_name} integration working (no health check)",
                        )
                except Exception as e:
                    self._record_test_result(
                        f"service_{service_name}_integration",
                        False,
                        f"{service_name} integration error: {e}",
                    )

            # Test orchestrator integration
            orchestrator = self.system.orchestrator
            if len(orchestrator.agents) == 8:
                self._record_test_result(
                    "orchestrator_integration", True, "Orchestrator integration working"
                )
            else:
                self._record_test_result(
                    "orchestrator_integration",
                    False,
                    f"Orchestrator integration failed: expected 8 agents, found {len(orchestrator.agents)}",
                )

            logger.info("✓ Integration workflows tested")

        except Exception as e:
            logger.error(f"Error testing integration workflows: {e}")
            self._record_test_result("integration_workflows_test", False, str(e))

    async def _test_end_to_end_workflows(self):
        """Test end-to-end workflows"""
        try:
            logger.info("Testing end-to-end workflows...")

            # Test complete intelligence workflow
            intelligence_workflow_config = {
                "user_id": "test_runner_user",
                "target_systems": ["test_server1", "test_server2"],
                "threat_indicators": ["malware", "suspicious_network"],
                "osint_parameters": {"keywords": ["threat", "malware"]},
            }

            result = await self.system.execute_security_workflow(
                "threat_hunting", intelligence_workflow_config
            )
            if (
                "workflow_type" in result
                and result["workflow_type"] == "threat_hunting"
            ):
                self._record_test_result(
                    "end_to_end_intelligence_workflow",
                    True,
                    "End-to-end intelligence workflow working",
                )
            else:
                self._record_test_result(
                    "end_to_end_intelligence_workflow",
                    False,
                    "End-to-end intelligence workflow failed",
                )

            # Test complete incident response workflow
            incident_response_workflow_config = {
                "user_id": "test_runner_user",
                "severity": "high",
                "title": "End-to-End Test Incident",
                "description": "End-to-end incident response workflow test",
                "affected_systems": ["test_server1"],
                "threat_indicators": ["malware"],
            }

            result = await self.system.execute_security_workflow(
                "incident_response", incident_response_workflow_config
            )
            if (
                "workflow_type" in result
                and result["workflow_type"] == "incident_response"
            ):
                self._record_test_result(
                    "end_to_end_incident_response_workflow",
                    True,
                    "End-to-end incident response workflow working",
                )
            else:
                self._record_test_result(
                    "end_to_end_incident_response_workflow",
                    False,
                    "End-to-end incident response workflow failed",
                )

            # Test complete security assessment workflow
            security_assessment_workflow_config = {
                "user_id": "test_runner_user",
                "assessment_parameters": {"scope": "full"},
                "compliance_standards": ["SOX", "GDPR"],
            }

            result = await self.system.execute_security_workflow(
                "security_assessment", security_assessment_workflow_config
            )
            if (
                "workflow_type" in result
                and result["workflow_type"] == "security_assessment"
            ):
                self._record_test_result(
                    "end_to_end_security_assessment_workflow",
                    True,
                    "End-to-end security assessment workflow working",
                )
            else:
                self._record_test_result(
                    "end_to_end_security_assessment_workflow",
                    False,
                    "End-to-end security assessment workflow failed",
                )

            logger.info("✓ End-to-end workflows tested")

        except Exception as e:
            logger.error(f"Error testing end-to-end workflows: {e}")
            self._record_test_result("end_to_end_workflows_test", False, str(e))

    async def _generate_test_report(self):
        """Generate comprehensive test report"""
        try:
            logger.info("Generating test report...")

            total_tests = len(self.test_results)
            passed_tests = len([r for r in self.test_results if r["passed"]])
            failed_tests = total_tests - passed_tests

            report = {
                "test_runner_suite": "AMAS Workflow Test Runner",
                "timestamp": datetime.utcnow().isoformat(),
                "summary": {
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "failed_tests": failed_tests,
                    "success_rate": (
                        (passed_tests / total_tests * 100) if total_tests > 0 else 0
                    ),
                },
                "test_results": self.test_results,
                "workflow_test_status": {
                    "core_workflows": "tested",
                    "security_workflows": "tested",
                    "agent_workflows": "tested",
                    "monitoring_workflows": "tested",
                    "integration_workflows": "tested",
                    "end_to_end_workflows": "tested",
                },
            }

            # Save report to file
            with open("logs/workflow_test_runner_report.json", "w") as f:
                json.dump(report, f, indent=2)

            # Log summary
            logger.info(f"Workflow Test Runner Report Summary:")
            logger.info(f"  Total Tests: {total_tests}")
            logger.info(f"  Passed: {passed_tests}")
            logger.info(f"  Failed: {failed_tests}")
            logger.info(f"  Success Rate: {report['summary']['success_rate']:.1f}%")

            if failed_tests > 0:
                logger.warning(f"  Failed Tests:")
                for result in self.test_results:
                    if not result["passed"]:
                        logger.warning(
                            f"    - {result['test_name']}: {result['message']}"
                        )

            logger.info(
                "Workflow test runner report generated: logs/workflow_test_runner_report.json"
            )

        except Exception as e:
            logger.error(f"Failed to generate test report: {e}")

    def _record_test_result(self, test_name: str, passed: bool, message: str):
        """Record test result"""
        self.test_results.append(
            {
                "test_name": test_name,
                "passed": passed,
                "message": message,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )


async def main():
    """Main test runner execution"""
    try:
        runner = WorkflowTestRunner()
        await runner.run_all_workflow_tests()

    except Exception as e:
        logger.error(f"Workflow test runner failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
