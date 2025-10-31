"""
Load testing suite for AMAS
Implements RD-086: Implement load testing suite
Implements RD-087: Add performance benchmarks and thresholds
Implements RD-088: Create stress testing procedures
"""

import argparse
import asyncio
import json
import logging
import os
import random
import statistics
import string
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import aiohttp

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

logger = logging.getLogger(__name__)


@dataclass
class LoadTestResult:
    """Load test result data structure"""

    test_name: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    total_duration: float
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    p50_response_time: float
    p95_response_time: float
    p99_response_time: float
    requests_per_second: float
    error_rate: float
    timestamp: str


@dataclass
class LoadTestConfig:
    """Load test configuration"""

    base_url: str
    concurrent_users: int
    duration_seconds: int
    ramp_up_seconds: int
    ramp_down_seconds: int
    think_time_seconds: float
    timeout_seconds: int = 30
    max_retries: int = 3


class LoadTestScenario:
    """Base class for load test scenarios"""

    def __init__(self, name: str, weight: float = 1.0):
        self.name = name
        self.weight = weight

    async def execute(
        self, session: aiohttp.ClientSession, base_url: str
    ) -> Dict[str, Any]:
        """Execute the test scenario"""
        raise NotImplementedError


class HealthCheckScenario(LoadTestScenario):
    """Health check endpoint scenario"""

    def __init__(self):
        super().__init__("health_check", 0.1)

    async def execute(
        self, session: aiohttp.ClientSession, base_url: str
    ) -> Dict[str, Any]:
        start_time = time.time()
        try:
            async with session.get(f"{base_url}/health", timeout=10) as response:
                duration = time.time() - start_time
                return {
                    "success": response.status == 200,
                    "status_code": response.status,
                    "duration": duration,
                    "response_size": len(await response.text()),
                }
        except Exception as e:
            duration = time.time() - start_time
            return {
                "success": False,
                "status_code": 0,
                "duration": duration,
                "error": str(e),
            }


class APIEndpointScenario(LoadTestScenario):
    """API endpoint scenario"""

    def __init__(self, endpoint: str, method: str = "GET", data: Optional[Dict] = None):
        super().__init__(f"api_{endpoint.replace('/', '_')}", 0.3)
        self.endpoint = endpoint
        self.method = method.upper()
        self.data = data or {}

    async def execute(
        self, session: aiohttp.ClientSession, base_url: str
    ) -> Dict[str, Any]:
        start_time = time.time()
        try:
            url = f"{base_url}{self.endpoint}"

            if self.method == "GET":
                async with session.get(url, timeout=30) as response:
                    duration = time.time() - start_time
                    return {
                        "success": response.status == 200,
                        "status_code": response.status,
                        "duration": duration,
                        "response_size": len(await response.text()),
                    }
            elif self.method == "POST":
                async with session.post(url, json=self.data, timeout=30) as response:
                    duration = time.time() - start_time
                    return {
                        "success": response.status in [200, 201],
                        "status_code": response.status,
                        "duration": duration,
                        "response_size": len(await response.text()),
                    }
            else:
                return {
                    "success": False,
                    "status_code": 0,
                    "duration": time.time() - start_time,
                    "error": f"Unsupported method: {self.method}",
                }
        except Exception as e:
            duration = time.time() - start_time
            return {
                "success": False,
                "status_code": 0,
                "duration": duration,
                "error": str(e),
            }


class DatabaseScenario(LoadTestScenario):
    """Database operations scenario"""

    def __init__(self):
        super().__init__("database_operations", 0.2)

    async def execute(
        self, session: aiohttp.ClientSession, base_url: str
    ) -> Dict[str, Any]:
        # Simulate database operations through API
        scenarios = [
            APIEndpointScenario("/api/agents", "GET"),
            APIEndpointScenario("/api/tasks", "GET"),
            APIEndpointScenario(
                "/api/agents",
                "POST",
                {
                    "name": f"test_agent_{random.randint(1000, 9999)}",
                    "type": "test",
                    "status": "active",
                },
            ),
        ]

        results = []
        for scenario in scenarios:
            result = await scenario.execute(session, base_url)
            results.append(result)

        # Calculate aggregate results
        total_duration = sum(r["duration"] for r in results)
        success_count = sum(1 for r in results if r["success"])

        return {
            "success": success_count == len(results),
            "status_code": 200 if success_count == len(results) else 500,
            "duration": total_duration,
            "sub_operations": len(results),
            "successful_operations": success_count,
        }


class LoadTestRunner:
    """Load test runner"""

    def __init__(self, config: LoadTestConfig):
        self.config = config
        self.scenarios = []
        self.results: List[Dict[str, Any]] = []

    def add_scenario(self, scenario: LoadTestScenario):
        """Add a test scenario"""
        self.scenarios.append(scenario)

    async def run_load_test(self) -> LoadTestResult:
        """Run the load test"""
        logger.info(
            f"Starting load test: {self.config.concurrent_users} users for {self.config.duration_seconds}s"
        )

        start_time = time.time()

        # Create weighted scenario list
        weighted_scenarios = []
        for scenario in self.scenarios:
            for _ in range(int(scenario.weight * 100)):
                weighted_scenarios.append(scenario)

        if not weighted_scenarios:
            raise ValueError("No scenarios configured")

        # Run load test
        async with aiohttp.ClientSession() as session:
            tasks = []

            # Ramp up phase
            ramp_up_tasks = []
            for i in range(self.config.concurrent_users):
                delay = (i / self.config.concurrent_users) * self.config.ramp_up_seconds
                task = asyncio.create_task(
                    self._user_loop(session, weighted_scenarios, delay)
                )
                ramp_up_tasks.append(task)

            # Wait for ramp up
            await asyncio.sleep(self.config.ramp_up_seconds)

            # Main test phase
            main_tasks = []
            for i in range(self.config.concurrent_users):
                task = asyncio.create_task(
                    self._user_loop(session, weighted_scenarios, 0)
                )
                main_tasks.append(task)

            # Wait for main test duration
            await asyncio.sleep(self.config.duration_seconds)

            # Cancel all tasks
            for task in ramp_up_tasks + main_tasks:
                task.cancel()

        end_time = time.time()
        total_duration = end_time - start_time

        # Calculate results
        return self._calculate_results(total_duration)

    async def _user_loop(
        self,
        session: aiohttp.ClientSession,
        scenarios: List[LoadTestScenario],
        initial_delay: float = 0,
    ):
        """User simulation loop"""
        if initial_delay > 0:
            await asyncio.sleep(initial_delay)

        while True:
            try:
                # Select random scenario
                scenario = random.choice(scenarios)

                # Execute scenario
                result = await scenario.execute(session, self.config.base_url)
                result["scenario"] = scenario.name
                result["timestamp"] = time.time()

                self.results.append(result)

                # Think time
                if self.config.think_time_seconds > 0:
                    await asyncio.sleep(self.config.think_time_seconds)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in user loop: {e}")
                await asyncio.sleep(1)

    def _calculate_results(self, total_duration: float) -> LoadTestResult:
        """Calculate test results"""
        if not self.results:
            return LoadTestResult(
                test_name="load_test",
                total_requests=0,
                successful_requests=0,
                failed_requests=0,
                total_duration=total_duration,
                avg_response_time=0,
                min_response_time=0,
                max_response_time=0,
                p50_response_time=0,
                p95_response_time=0,
                p99_response_time=0,
                requests_per_second=0,
                error_rate=0,
                timestamp=datetime.now().isoformat(),
            )

        # Filter out results with errors
        valid_results = [
            r for r in self.results if "duration" in r and r["duration"] > 0
        ]

        if not valid_results:
            return LoadTestResult(
                test_name="load_test",
                total_requests=len(self.results),
                successful_requests=0,
                failed_requests=len(self.results),
                total_duration=total_duration,
                avg_response_time=0,
                min_response_time=0,
                max_response_time=0,
                p50_response_time=0,
                p95_response_time=0,
                p99_response_time=0,
                requests_per_second=0,
                error_rate=100,
                timestamp=datetime.now().isoformat(),
            )

        # Calculate metrics
        durations = [r["duration"] for r in valid_results]
        successful_requests = sum(1 for r in self.results if r.get("success", False))
        failed_requests = len(self.results) - successful_requests

        return LoadTestResult(
            test_name="load_test",
            total_requests=len(self.results),
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            total_duration=total_duration,
            avg_response_time=statistics.mean(durations),
            min_response_time=min(durations),
            max_response_time=max(durations),
            p50_response_time=statistics.quantiles(durations, n=2)[0],
            p95_response_time=statistics.quantiles(durations, n=20)[18],
            p99_response_time=statistics.quantiles(durations, n=100)[98],
            requests_per_second=len(self.results) / total_duration,
            error_rate=(failed_requests / len(self.results)) * 100,
            timestamp=datetime.now().isoformat(),
        )


class StressTestRunner:
    """Stress test runner - gradually increases load until failure"""

    def __init__(self, config: LoadTestConfig):
        self.config = config
        self.scenarios = []
        self.stress_results: List[LoadTestResult] = []

    def add_scenario(self, scenario: LoadTestScenario):
        """Add a test scenario"""
        self.scenarios.append(scenario)

    async def run_stress_test(self) -> List[LoadTestResult]:
        """Run stress test with increasing load"""
        logger.info("Starting stress test")

        # Start with low load and gradually increase
        max_users = self.config.concurrent_users * 3
        step_size = max(1, max_users // 10)

        for users in range(step_size, max_users + 1, step_size):
            logger.info(f"Testing with {users} concurrent users")

            # Create test config for this step
            step_config = LoadTestConfig(
                base_url=self.config.base_url,
                concurrent_users=users,
                duration_seconds=60,  # 1 minute per step
                ramp_up_seconds=10,
                ramp_down_seconds=5,
                think_time_seconds=self.config.think_time_seconds,
                timeout_seconds=self.config.timeout_seconds,
            )

            # Run load test
            runner = LoadTestRunner(step_config)
            for scenario in self.scenarios:
                runner.add_scenario(scenario)

            try:
                result = await runner.run_load_test()
                self.stress_results.append(result)

                # Check if we've hit failure threshold
                if result.error_rate > 10 or result.avg_response_time > 5.0:
                    logger.warning(
                        f"High error rate or response time at {users} users: "
                        f"Error rate: {result.error_rate:.2f}%, "
                        f"Avg response time: {result.avg_response_time:.2f}s"
                    )

                if result.error_rate > 50:
                    logger.error(
                        f"System failure at {users} users: {result.error_rate:.2f}% error rate"
                    )
                    break

            except Exception as e:
                logger.error(f"Stress test failed at {users} users: {e}")
                break

        return self.stress_results


class PerformanceBenchmarks:
    """Performance benchmarks and thresholds"""

    THRESHOLDS = {
        "response_time_p95": 2.0,  # 95th percentile response time in seconds
        "response_time_p99": 5.0,  # 99th percentile response time in seconds
        "error_rate": 1.0,  # Maximum error rate percentage
        "throughput": 100,  # Minimum requests per second
        "availability": 99.9,  # Minimum availability percentage
    }

    @classmethod
    def evaluate_result(cls, result: LoadTestResult) -> Dict[str, Any]:
        """Evaluate test result against benchmarks"""
        evaluation = {"passed": True, "score": 0, "violations": []}

        # Check response time thresholds
        if result.p95_response_time > cls.THRESHOLDS["response_time_p95"]:
            evaluation["violations"].append(
                {
                    "metric": "response_time_p95",
                    "threshold": cls.THRESHOLDS["response_time_p95"],
                    "actual": result.p95_response_time,
                    "severity": "high",
                }
            )
            evaluation["passed"] = False

        if result.p99_response_time > cls.THRESHOLDS["response_time_p99"]:
            evaluation["violations"].append(
                {
                    "metric": "response_time_p99",
                    "threshold": cls.THRESHOLDS["response_time_p99"],
                    "actual": result.p99_response_time,
                    "severity": "critical",
                }
            )
            evaluation["passed"] = False

        # Check error rate
        if result.error_rate > cls.THRESHOLDS["error_rate"]:
            evaluation["violations"].append(
                {
                    "metric": "error_rate",
                    "threshold": cls.THRESHOLDS["error_rate"],
                    "actual": result.error_rate,
                    "severity": "critical",
                }
            )
            evaluation["passed"] = False

        # Check throughput
        if result.requests_per_second < cls.THRESHOLDS["throughput"]:
            evaluation["violations"].append(
                {
                    "metric": "throughput",
                    "threshold": cls.THRESHOLDS["throughput"],
                    "actual": result.requests_per_second,
                    "severity": "medium",
                }
            )

        # Calculate score
        total_checks = 4
        passed_checks = total_checks - len(evaluation["violations"])
        evaluation["score"] = (passed_checks / total_checks) * 100

        return evaluation


def generate_report(results: List[LoadTestResult], output_file: str = None):
    """Generate load test report"""
    report = {
        "summary": {
            "total_tests": len(results),
            "avg_throughput": statistics.mean([r.requests_per_second for r in results]),
            "avg_error_rate": statistics.mean([r.error_rate for r in results]),
            "avg_response_time": statistics.mean(
                [r.avg_response_time for r in results]
            ),
        },
        "results": [asdict(r) for r in results],
        "benchmarks": PerformanceBenchmarks.THRESHOLDS,
        "generated_at": datetime.now().isoformat(),
    }

    if output_file:
        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)
        logger.info(f"Report saved to {output_file}")
    else:
        print(json.dumps(report, indent=2))


async def main():
    """Main function for running load tests"""
    parser = argparse.ArgumentParser(description="AMAS Load Testing Suite")
    parser.add_argument(
        "--url", default="http://localhost:8000", help="Base URL to test"
    )
    parser.add_argument(
        "--users", type=int, default=10, help="Number of concurrent users"
    )
    parser.add_argument(
        "--duration", type=int, default=60, help="Test duration in seconds"
    )
    parser.add_argument(
        "--ramp-up", type=int, default=10, help="Ramp up time in seconds"
    )
    parser.add_argument(
        "--think-time", type=float, default=1.0, help="Think time between requests"
    )
    parser.add_argument("--stress", action="store_true", help="Run stress test")
    parser.add_argument("--output", help="Output file for results")

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Create test configuration
    config = LoadTestConfig(
        base_url=args.url,
        concurrent_users=args.users,
        duration_seconds=args.duration,
        ramp_up_seconds=args.ramp_up,
        ramp_down_seconds=5,
        think_time_seconds=args.think_time,
    )

    # Create scenarios
    scenarios = [
        HealthCheckScenario(),
        APIEndpointScenario("/", "GET"),
        APIEndpointScenario("/docs", "GET"),
        DatabaseScenario(),
    ]

    if args.stress:
        # Run stress test
        stress_runner = StressTestRunner(config)
        for scenario in scenarios:
            stress_runner.add_scenario(scenario)

        results = await stress_runner.run_stress_test()
        generate_report(results, args.output)
    else:
        # Run load test
        runner = LoadTestRunner(config)
        for scenario in scenarios:
            runner.add_scenario(scenario)

        result = await runner.run_load_test()

        # Evaluate against benchmarks
        evaluation = PerformanceBenchmarks.evaluate_result(result)

        print(f"\nLoad Test Results:")
        print(f"Total Requests: {result.total_requests}")
        print(f"Successful: {result.successful_requests}")
        print(f"Failed: {result.failed_requests}")
        print(f"Error Rate: {result.error_rate:.2f}%")
        print(f"Avg Response Time: {result.avg_response_time:.3f}s")
        print(f"P95 Response Time: {result.p95_response_time:.3f}s")
        print(f"P99 Response Time: {result.p99_response_time:.3f}s")
        print(f"Throughput: {result.requests_per_second:.2f} req/s")
        print(f"Benchmark Score: {evaluation['score']:.1f}%")
        print(f"Passed: {evaluation['passed']}")

        if evaluation["violations"]:
            print(f"\nViolations:")
            for violation in evaluation["violations"]:
                print(
                    f"  {violation['metric']}: {violation['actual']:.3f} > {violation['threshold']:.3f} ({violation['severity']})"
                )

        generate_report([result], args.output)


if __name__ == "__main__":
    asyncio.run(main())
