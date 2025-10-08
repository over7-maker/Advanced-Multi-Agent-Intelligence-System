#!/usr/bin/env python3
"""
AMAS Load Testing Framework
Comprehensive load testing for multi-agent system performance
"""

import asyncio
import json
import statistics
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any, Dict, List

import aiohttp
import matplotlib.pyplot as plt
import seaborn as sns


@dataclass
class LoadTestResult:
    test_name: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    p95_response_time: float
    requests_per_second: float
    error_rate: float


class AMASLoadTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.results = []

    async def setup_session(self):
        """Setup HTTP session for load testing"""
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=50)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)

    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()

    async def single_request(
        self, endpoint: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute single request and measure performance"""
        start_time = time.time()

        try:
            async with self.session.post(
                f"{self.base_url}{endpoint}", json=payload
            ) as response:
                response_data = await response.json()
                end_time = time.time()

                return {
                    "success": response.status == 200,
                    "response_time": end_time - start_time,
                    "status_code": response.status,
                    "response_size": len(str(response_data)),
                }
        except Exception as e:
            end_time = time.time()
            return {
                "success": False,
                "response_time": end_time - start_time,
                "error": str(e),
                "status_code": 0,
            }

    async def concurrent_requests(
        self,
        endpoint: str,
        payload: Dict[str, Any],
        concurrent_users: int,
        requests_per_user: int,
    ) -> List[Dict[str, Any]]:
        """Execute concurrent requests"""

        async def user_session():
            results = []
            for _ in range(requests_per_user):
                result = await self.single_request(endpoint, payload)
                results.append(result)
                await asyncio.sleep(0.1)  # Small delay between requests
            return results

        # Create tasks for concurrent users
        tasks = [user_session() for _ in range(concurrent_users)]

        # Execute all tasks concurrently
        all_results = await asyncio.gather(*tasks)

        # Flatten results
        flattened_results = []
        for user_results in all_results:
            flattened_results.extend(user_results)

        return flattened_results

    def analyze_results(
        self, test_name: str, results: List[Dict[str, Any]]
    ) -> LoadTestResult:
        """Analyze load test results"""

        successful = [r for r in results if r["success"]]
        failed = [r for r in results if not r["success"]]

        response_times = [r["response_time"] for r in successful]

        if not response_times:
            # All requests failed
            return LoadTestResult(
                test_name=test_name,
                total_requests=len(results),
                successful_requests=0,
                failed_requests=len(failed),
                avg_response_time=0,
                min_response_time=0,
                max_response_time=0,
                p95_response_time=0,
                requests_per_second=0,
                error_rate=1.0,
            )

        total_time = max([r["response_time"] for r in results])

        return LoadTestResult(
            test_name=test_name,
            total_requests=len(results),
            successful_requests=len(successful),
            failed_requests=len(failed),
            avg_response_time=statistics.mean(response_times),
            min_response_time=min(response_times),
            max_response_time=max(response_times),
            p95_response_time=(
                statistics.quantiles(response_times, n=20)[18]
                if len(response_times) > 20
                else max(response_times)
            ),
            requests_per_second=len(results) / total_time if total_time > 0 else 0,
            error_rate=len(failed) / len(results),
        )

    async def test_security_scan_load(
        self, concurrent_users: int = 10, requests_per_user: int = 5
    ):
        """Load test security scanning endpoint"""

        payload = {
            "type": "security_scan",
            "target": "example.com",
            "depth": "standard",
        }

        print(
            f"🔍 Load testing security scan: {concurrent_users} users, {requests_per_user} requests each"
        )

        results = await self.concurrent_requests(
            "/api/tasks", payload, concurrent_users, requests_per_user
        )

        analysis = self.analyze_results("Security Scan Load Test", results)
        self.results.append(analysis)

        return analysis

    async def test_code_analysis_load(
        self, concurrent_users: int = 8, requests_per_user: int = 3
    ):
        """Load test code analysis endpoint"""

        payload = {
            "type": "code_analysis",
            "target": "github.com/example/repo",
            "depth": "comprehensive",
        }

        print(
            f"📝 Load testing code analysis: {concurrent_users} users, {requests_per_user} requests each"
        )

        results = await self.concurrent_requests(
            "/api/tasks", payload, concurrent_users, requests_per_user
        )

        analysis = self.analyze_results("Code Analysis Load Test", results)
        self.results.append(analysis)

        return analysis

    async def test_mixed_workload(
        self, concurrent_users: int = 15, duration_minutes: int = 5
    ):
        """Test mixed workload simulating real usage"""

        task_types = [
            {"type": "security_scan", "target": "test1.com", "weight": 0.4},
            {"type": "code_analysis", "target": "github.com/test/repo1", "weight": 0.3},
            {"type": "intelligence_gathering", "target": "test-company", "weight": 0.2},
            {"type": "performance_analysis", "target": "app.test.com", "weight": 0.1},
        ]

        print(
            f"🌀 Mixed workload test: {concurrent_users} users for {duration_minutes} minutes"
        )

        async def mixed_user_session():
            results = []
            end_time = time.time() + (duration_minutes * 60)

            while time.time() < end_time:
                # Randomly select task type based on weight
                import random

                task = random.choices(
                    task_types, weights=[t["weight"] for t in task_types]
                )[0]

                payload = {
                    "type": task["type"],
                    "target": task["target"],
                    "depth": "standard",
                }

                result = await self.single_request("/api/tasks", payload)
                results.append(result)

                # Random delay between requests (0.5 to 2 seconds)
                await asyncio.sleep(random.uniform(0.5, 2.0))

            return results

        # Start all user sessions
        tasks = [mixed_user_session() for _ in range(concurrent_users)]
        all_results = await asyncio.gather(*tasks)

        # Flatten results
        flattened_results = []
        for user_results in all_results:
            flattened_results.extend(user_results)

        analysis = self.analyze_results("Mixed Workload Test", flattened_results)
        self.results.append(analysis)

        return analysis

    async def test_stress_breaking_point(
        self, max_users: int = 100, step_size: int = 10
    ):
        """Find the breaking point by gradually increasing load"""

        print(f"💥 Stress test: Finding breaking point up to {max_users} users")

        breaking_point_results = []

        for users in range(step_size, max_users + 1, step_size):
            print(f"  Testing with {users} concurrent users...")

            payload = {
                "type": "security_scan",
                "target": "stress-test.com",
                "depth": "quick",
            }

            results = await self.concurrent_requests("/api/tasks", payload, users, 2)
            analysis = self.analyze_results(f"Stress Test - {users} users", results)

            breaking_point_results.append(
                {
                    "users": users,
                    "success_rate": 1 - analysis.error_rate,
                    "avg_response_time": analysis.avg_response_time,
                    "requests_per_second": analysis.requests_per_second,
                }
            )

            # Stop if error rate exceeds 10% or response time exceeds 10 seconds
            if analysis.error_rate > 0.1 or analysis.avg_response_time > 10:
                print(f"  💥 Breaking point reached at {users} users")
                break

            await asyncio.sleep(2)  # Cool down between tests

        return breaking_point_results

    def generate_performance_report(self):
        """Generate comprehensive performance report"""

        if not self.results:
            print("❌ No test results to report")
            return

        print("\n" + "=" * 80)
        print("📊 AMAS LOAD TEST PERFORMANCE REPORT")
        print("=" * 80)

        for result in self.results:
            print(f"\n🎯 {result.test_name}")
            print(f"   Total Requests: {result.total_requests}")
            print(
                f"   Success Rate: {((result.successful_requests / result.total_requests) * 100):.1f}%"
            )
            print(f"   Avg Response Time: {result.avg_response_time:.3f}s")
            print(f"   95th Percentile: {result.p95_response_time:.3f}s")
            print(f"   Throughput: {result.requests_per_second:.1f} req/s")

            if result.error_rate > 0:
                print(f"   ⚠️ Error Rate: {(result.error_rate * 100):.1f}%")

        print("\n" + "=" * 80)

        # Performance recommendations
        print("\n💡 PERFORMANCE RECOMMENDATIONS:")

        avg_response_time = statistics.mean([r.avg_response_time for r in self.results])
        avg_throughput = statistics.mean([r.requests_per_second for r in self.results])
        max_error_rate = max([r.error_rate for r in self.results])

        if avg_response_time > 3:
            print("🔧 High response times detected. Consider:")
            print("   - Optimizing agent algorithms")
            print("   - Adding more worker processes")
            print("   - Implementing caching layer")

        if avg_throughput < 10:
            print("⚡ Low throughput detected. Consider:")
            print("   - Horizontal scaling")
            print("   - Database optimization")
            print("   - Connection pooling")

        if max_error_rate > 0.05:
            print("🚨 Error rate concerns. Consider:")
            print("   - Better error handling")
            print("   - Circuit breaker patterns")
            print("   - Graceful degradation")

        if avg_response_time < 2 and max_error_rate < 0.01:
            print("✅ Excellent performance! System is well optimized.")

    def visualize_results(self):
        """Create performance visualization charts"""

        if not self.results:
            return

        # Create subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle("AMAS Load Test Results", fontsize=16)

        test_names = [r.test_name for r in self.results]

        # Response times
        response_times = [r.avg_response_time for r in self.results]
        ax1.bar(test_names, response_times, color="skyblue")
        ax1.set_title("Average Response Time")
        ax1.set_ylabel("Seconds")
        ax1.tick_params(axis="x", rotation=45)

        # Throughput
        throughput = [r.requests_per_second for r in self.results]
        ax2.bar(test_names, throughput, color="lightgreen")
        ax2.set_title("Throughput")
        ax2.set_ylabel("Requests/Second")
        ax2.tick_params(axis="x", rotation=45)

        # Success rate
        success_rates = [
            (r.successful_requests / r.total_requests) * 100 for r in self.results
        ]
        ax3.bar(test_names, success_rates, color="orange")
        ax3.set_title("Success Rate")
        ax3.set_ylabel("Percentage")
        ax3.set_ylim(0, 100)
        ax3.tick_params(axis="x", rotation=45)

        # Error rate
        error_rates = [r.error_rate * 100 for r in self.results]
        ax4.bar(test_names, error_rates, color="salmon")
        ax4.set_title("Error Rate")
        ax4.set_ylabel("Percentage")
        ax4.tick_params(axis="x", rotation=45)

        plt.tight_layout()
        plt.savefig("amas_load_test_results.png", dpi=300, bbox_inches="tight")
        print("📊 Performance charts saved to 'amas_load_test_results.png'")

    async def run_full_load_test_suite(self):
        """Run comprehensive load test suite"""

        print("🚀 Starting AMAS comprehensive load test suite...")
        print("=" * 60)

        await self.setup_session()

        try:
            # Test 1: Security scan load test
            await self.test_security_scan_load(concurrent_users=10, requests_per_user=5)
            await asyncio.sleep(5)  # Cool down

            # Test 2: Code analysis load test
            await self.test_code_analysis_load(concurrent_users=8, requests_per_user=3)
            await asyncio.sleep(5)

            # Test 3: Mixed workload test
            await self.test_mixed_workload(concurrent_users=15, duration_minutes=2)
            await asyncio.sleep(10)

            # Test 4: Stress test (optional - comment out for quick testing)
            # breaking_points = await self.test_stress_breaking_point(max_users=50, step_size=10)

        finally:
            await self.cleanup_session()

        # Generate reports
        self.generate_performance_report()
        self.visualize_results()

        print("\n✅ Load testing complete!")


# CLI interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AMAS Load Testing Framework")
    parser.add_argument(
        "--base-url", default="http://localhost:8000", help="Base URL for AMAS API"
    )
    parser.add_argument("--quick", action="store_true", help="Run quick test suite")
    parser.add_argument(
        "--stress", action="store_true", help="Run stress test to find breaking point"
    )

    args = parser.parse_args()

    tester = AMASLoadTester(args.base_url)

    if args.stress:
        # Just run stress test
        async def run_stress():
            await tester.setup_session()
            try:
                await tester.test_stress_breaking_point()
            finally:
                await tester.cleanup_session()
            tester.generate_performance_report()

        asyncio.run(run_stress())
    elif args.quick:
        # Quick test
        async def run_quick():
            await tester.setup_session()
            try:
                await tester.test_security_scan_load(5, 2)
            finally:
                await tester.cleanup_session()
            tester.generate_performance_report()

        asyncio.run(run_quick())
    else:
        # Full suite
        asyncio.run(tester.run_full_load_test_suite())
