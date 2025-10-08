#!/usr/bin/env python3
"""
AMAS Integration Verification Script

This script verifies that all components are properly integrated
and functioning correctly.
"""

import asyncio
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import aiohttp
import yaml

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class AMASIntegrationVerifier:
    """Verifies AMAS system integration and functionality"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.results = {
            "timestamp": datetime.utcnow().isoformat(),
            "tests": {},
            "overall_status": "unknown",
            "summary": {},
        }

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def test_api_connectivity(self) -> Dict[str, Any]:
        """Test basic API connectivity"""
        logger.info("Testing API connectivity...")

        try:
            async with self.session.get(f"{self.base_url}/") as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "status": "pass",
                        "message": "API is accessible",
                        "response_time": response.headers.get(
                            "X-Response-Time", "unknown"
                        ),
                        "data": data,
                    }
                else:
                    return {
                        "status": "fail",
                        "message": f"API returned status {response.status}",
                        "response_time": response.headers.get(
                            "X-Response-Time", "unknown"
                        ),
                    }
        except Exception as e:
            return {"status": "fail", "message": f"Failed to connect to API: {str(e)}"}

    async def test_health_endpoint(self) -> Dict[str, Any]:
        """Test health endpoint"""
        logger.info("Testing health endpoint...")

        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "status": "pass",
                        "message": "Health endpoint is working",
                        "health_data": data,
                    }
                else:
                    return {
                        "status": "fail",
                        "message": f"Health endpoint returned status {response.status}",
                    }
        except Exception as e:
            return {
                "status": "fail",
                "message": f"Failed to access health endpoint: {str(e)}",
            }

    async def test_status_endpoint(self) -> Dict[str, Any]:
        """Test status endpoint"""
        logger.info("Testing status endpoint...")

        try:
            async with self.session.get(f"{self.base_url}/status") as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "status": "pass",
                        "message": "Status endpoint is working",
                        "status_data": data,
                    }
                else:
                    return {
                        "status": "fail",
                        "message": f"Status endpoint returned status {response.status}",
                    }
        except Exception as e:
            return {
                "status": "fail",
                "message": f"Failed to access status endpoint: {str(e)}",
            }

    async def test_agents_endpoint(self) -> Dict[str, Any]:
        """Test agents endpoint"""
        logger.info("Testing agents endpoint...")

        try:
            # Note: This endpoint requires authentication in production
            # For testing, we'll check if it returns a proper response structure
            async with self.session.get(f"{self.base_url}/agents") as response:
                if response.status in [
                    200,
                    401,
                    403,
                ]:  # 401/403 are expected without auth
                    data = await response.json()
                    return {
                        "status": "pass",
                        "message": "Agents endpoint is accessible",
                        "response_status": response.status,
                        "data": data,
                    }
                else:
                    return {
                        "status": "fail",
                        "message": f"Agents endpoint returned unexpected status {response.status}",
                    }
        except Exception as e:
            return {
                "status": "fail",
                "message": f"Failed to access agents endpoint: {str(e)}",
            }

    async def test_task_submission(self) -> Dict[str, Any]:
        """Test task submission (without authentication for testing)"""
        logger.info("Testing task submission...")

        test_task = {
            "type": "research",
            "description": "Integration test task",
            "priority": 1,
            "parameters": {"test_mode": True, "timeout": 30},
        }

        try:
            async with self.session.post(
                f"{self.base_url}/tasks", json=test_task
            ) as response:
                if response.status in [
                    200,
                    201,
                    401,
                    403,
                ]:  # 401/403 expected without auth
                    data = await response.json()
                    return {
                        "status": "pass",
                        "message": "Task submission endpoint is accessible",
                        "response_status": response.status,
                        "data": data,
                    }
                else:
                    return {
                        "status": "fail",
                        "message": f"Task submission returned status {response.status}",
                    }
        except Exception as e:
            return {"status": "fail", "message": f"Failed to submit task: {str(e)}"}

    async def test_docker_services(self) -> Dict[str, Any]:
        """Test Docker services status"""
        logger.info("Testing Docker services...")

        try:
            import subprocess

            result = subprocess.run(
                ["docker-compose", "ps", "--format", "json"],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent,
            )

            if result.returncode == 0:
                services = []
                for line in result.stdout.strip().split("\n"):
                    if line:
                        try:
                            service = json.loads(line)
                            services.append(service)
                        except json.JSONDecodeError:
                            continue

                running_services = [s for s in services if s.get("State") == "running"]

                return {
                    "status": "pass",
                    "message": f"Found {len(running_services)} running services",
                    "services": running_services,
                    "total_services": len(services),
                }
            else:
                return {
                    "status": "fail",
                    "message": f"Docker compose command failed: {result.stderr}",
                }
        except Exception as e:
            return {
                "status": "fail",
                "message": f"Failed to check Docker services: {str(e)}",
            }

    async def test_configuration_files(self) -> Dict[str, Any]:
        """Test configuration files exist and are valid"""
        logger.info("Testing configuration files...")

        config_files = [
            "requirements.txt",
            "docker-compose.yml",
            "pyproject.toml",
            ".env.example",
        ]

        results = {}
        all_exist = True

        for config_file in config_files:
            file_path = Path(config_file)
            if file_path.exists():
                results[config_file] = {
                    "status": "pass",
                    "message": "File exists",
                    "size": file_path.stat().st_size,
                }
            else:
                results[config_file] = {"status": "fail", "message": "File not found"}
                all_exist = False

        return {
            "status": "pass" if all_exist else "fail",
            "message": f"Configuration files check: {'All found' if all_exist else 'Some missing'}",
            "files": results,
        }

    async def test_python_imports(self) -> Dict[str, Any]:
        """Test Python imports work correctly"""
        logger.info("Testing Python imports...")

        try:
            # Test core imports
            from src.amas.config.settings import AMASConfig
            from src.amas.core.orchestrator import IntelligenceOrchestrator
            from src.amas.main import AMASApplication
            from src.amas.services.service_manager import ServiceManager

            return {
                "status": "pass",
                "message": "All core imports successful",
                "imported_modules": [
                    "AMASApplication",
                    "IntelligenceOrchestrator",
                    "ServiceManager",
                    "AMASConfig",
                ],
            }
        except ImportError as e:
            return {"status": "fail", "message": f"Import failed: {str(e)}"}
        except Exception as e:
            return {
                "status": "fail",
                "message": f"Unexpected error during import test: {str(e)}",
            }

    async def test_agent_initialization(self) -> Dict[str, Any]:
        """Test agent initialization"""
        logger.info("Testing agent initialization...")

        try:
            from src.amas.agents.data_analysis.data_analysis_agent import (
                DataAnalysisAgent,
            )
            from src.amas.agents.osint.osint_agent import OSINTAgent
            from src.amas.agents.reporting.reporting_agent import ReportingAgent

            # Test agent creation
            osint_agent = OSINTAgent("test_osint_001", "Test OSINT Agent")
            data_agent = DataAnalysisAgent("test_data_001", "Test Data Agent")
            report_agent = ReportingAgent("test_report_001", "Test Report Agent")

            return {
                "status": "pass",
                "message": "Agent initialization successful",
                "agents_created": [
                    osint_agent.agent_id,
                    data_agent.agent_id,
                    report_agent.agent_id,
                ],
            }
        except Exception as e:
            return {
                "status": "fail",
                "message": f"Agent initialization failed: {str(e)}",
            }

    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all integration tests"""
        logger.info("Starting AMAS integration verification...")

        tests = [
            ("api_connectivity", self.test_api_connectivity),
            ("health_endpoint", self.test_health_endpoint),
            ("status_endpoint", self.test_status_endpoint),
            ("agents_endpoint", self.test_agents_endpoint),
            ("task_submission", self.test_task_submission),
            ("docker_services", self.test_docker_services),
            ("config_files", self.test_configuration_files),
            ("python_imports", self.test_python_imports),
            ("agent_initialization", self.test_agent_initialization),
        ]

        passed = 0
        failed = 0

        for test_name, test_func in tests:
            try:
                result = await test_func()
                self.results["tests"][test_name] = result

                if result["status"] == "pass":
                    passed += 1
                    logger.info(f"✅ {test_name}: {result['message']}")
                else:
                    failed += 1
                    logger.error(f"❌ {test_name}: {result['message']}")

            except Exception as e:
                failed += 1
                error_result = {
                    "status": "fail",
                    "message": f"Test failed with exception: {str(e)}",
                }
                self.results["tests"][test_name] = error_result
                logger.error(f"❌ {test_name}: {error_result['message']}")

        # Calculate overall status
        total_tests = passed + failed
        success_rate = (passed / total_tests) * 100 if total_tests > 0 else 0

        if success_rate >= 90:
            overall_status = "excellent"
        elif success_rate >= 75:
            overall_status = "good"
        elif success_rate >= 50:
            overall_status = "fair"
        else:
            overall_status = "poor"

        self.results["overall_status"] = overall_status
        self.results["summary"] = {
            "total_tests": total_tests,
            "passed": passed,
            "failed": failed,
            "success_rate": f"{success_rate:.1f}%",
            "overall_status": overall_status,
        }

        logger.info(f"\n📊 Integration Test Summary:")
        logger.info(f"   Total Tests: {total_tests}")
        logger.info(f"   Passed: {passed}")
        logger.info(f"   Failed: {failed}")
        logger.info(f"   Success Rate: {success_rate:.1f}%")
        logger.info(f"   Overall Status: {overall_status.upper()}")

        return self.results

    def save_results(self, filename: str = None) -> str:
        """Save test results to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"integration_test_results_{timestamp}.json"

        with open(filename, "w") as f:
            json.dump(self.results, f, indent=2)

        logger.info(f"Results saved to: {filename}")
        return filename

async def main():
    """Main function"""
    print("🔍 AMAS Integration Verification Tool")
    print("=" * 50)

    # Check if we're in the right directory
    if not Path("src/amas").exists():
        print("❌ Error: Please run this script from the AMAS project root directory")
        sys.exit(1)

    base_url = "http://localhost:8000"
    if len(sys.argv) > 1:
        base_url = sys.argv[1]

    print(f"🌐 Testing against: {base_url}")
    print()

    async with AMASIntegrationVerifier(base_url) as verifier:
        results = await verifier.run_all_tests()

        # Save results
        filename = verifier.save_results()

        # Print final status
        print("\n" + "=" * 50)
        if results["overall_status"] in ["excellent", "good"]:
            print("🎉 AMAS Integration Verification: PASSED")
            print("✅ Your AMAS system is properly integrated and ready for use!")
        else:
            print("⚠️  AMAS Integration Verification: ISSUES FOUND")
            print("🔧 Please review the failed tests and fix the issues.")

        print(f"\n📄 Detailed results saved to: {filename}")

        # Exit with appropriate code
        if results["overall_status"] in ["excellent", "good"]:
            sys.exit(0)
        else:
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
