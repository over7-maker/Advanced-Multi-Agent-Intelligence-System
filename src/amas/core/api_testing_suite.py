#!/usr/bin/env python3
"""
AMAS API Testing Suite
Comprehensive testing and validation for all 16 AI providers
"""

import asyncio
import json
import logging
import os
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

# Import our API manager
from .ai_api_manager import (
    APIProvider,
    APIStatus,
    IntelligentAPIManager,
    TaskType,
    generate_ai_response,
    get_api_manager,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TestCase:
    """Test case for API validation"""

    id: str
    name: str
    description: str
    task_type: TaskType
    messages: List[Dict[str, str]]
    expected_response_keywords: List[str] = field(default_factory=list)
    max_response_time: float = 30.0
    min_response_length: int = 10

@dataclass
class TestResult:
    """Test result data structure"""

    test_case_id: str
    provider: APIProvider
    success: bool
    response_time: float
    response_content: str = ""
    error_message: str = ""
    response_length: int = 0
    contains_keywords: bool = False
    timestamp: datetime = field(default_factory=datetime.now)

class APITestingSuite:
    """Comprehensive API testing and validation suite"""

    def __init__(self):
        self.api_manager = get_api_manager()
        self.test_cases = self._create_test_cases()
        self.test_results: Dict[str, List[TestResult]] = {}

        logger.info(
            f"API Testing Suite initialized with {len(self.test_cases)} test cases"
        )

    def _create_test_cases(self) -> List[TestCase]:
        """Create comprehensive test cases"""
        return [
            TestCase(
                id="basic_chat",
                name="Basic Chat Completion",
                description="Simple conversational response",
                task_type=TaskType.CHAT_COMPLETION,
                messages=[{"role": "user", "content": "Hello, how are you today?"}],
                expected_response_keywords=["hello", "good", "fine", "well"],
                max_response_time=15.0,
                min_response_length=10,
            ),
            TestCase(
                id="code_analysis",
                name="Code Analysis",
                description="Analyze a simple Python function",
                task_type=TaskType.CODE_ANALYSIS,
                messages=[
                    {
                        "role": "user",
                        "content": """Analyze this Python function for potential issues:

def divide_numbers(a, b):
    return a / b

What are the potential problems and how would you fix them?""",
                    }
                ],
                expected_response_keywords=[
                    "zero",
                    "division",
                    "error",
                    "exception",
                    "validation",
                ],
                max_response_time=20.0,
                min_response_length=50,
            ),
            TestCase(
                id="reasoning_task",
                name="Logical Reasoning",
                description="Solve a logical reasoning problem",
                task_type=TaskType.REASONING,
                messages=[
                    {
                        "role": "user",
                        "content": """If all birds can fly, and penguins are birds, but penguins cannot fly, what can we conclude about the initial statement? Explain your reasoning.""",
                    }
                ],
                expected_response_keywords=[
                    "logical",
                    "contradiction",
                    "false",
                    "assumption",
                    "premise",
                ],
                max_response_time=25.0,
                min_response_length=100,
            ),
            TestCase(
                id="text_generation",
                name="Creative Text Generation",
                description="Generate creative content",
                task_type=TaskType.TEXT_GENERATION,
                messages=[
                    {
                        "role": "user",
                        "content": "Write a short story about an AI that helps solve cybersecurity threats. Keep it to 100 words.",
                    }
                ],
                expected_response_keywords=[
                    "AI",
                    "cybersecurity",
                    "threat",
                    "computer",
                    "security",
                ],
                max_response_time=20.0,
                min_response_length=50,
            ),
            TestCase(
                id="summarization",
                name="Text Summarization",
                description="Summarize complex text",
                task_type=TaskType.SUMMARIZATION,
                messages=[
                    {
                        "role": "user",
                        "content": """Summarize this text in 3 key points:

Artificial Intelligence has revolutionized many industries, from healthcare to finance. In cybersecurity, AI systems can detect anomalies, predict threats, and respond to incidents faster than human analysts. However, AI also introduces new vulnerabilities and attack vectors that organizations must consider. The balance between leveraging AI's benefits while mitigating its risks is crucial for modern cybersecurity strategies. Organizations need to implement proper AI governance, ensure data quality, and maintain human oversight of AI systems.""",
                    }
                ],
                expected_response_keywords=[
                    "AI",
                    "cybersecurity",
                    "benefits",
                    "risks",
                    "organizations",
                ],
                max_response_time=15.0,
                min_response_length=50,
            ),
            TestCase(
                id="question_answering",
                name="Question Answering",
                description="Answer specific questions accurately",
                task_type=TaskType.QUESTION_ANSWERING,
                messages=[
                    {
                        "role": "user",
                        "content": "What are the main components of a typical cybersecurity incident response plan?",
                    }
                ],
                expected_response_keywords=[
                    "preparation",
                    "detection",
                    "response",
                    "recovery",
                    "lessons",
                ],
                max_response_time=15.0,
                min_response_length=100,
            ),
            TestCase(
                id="complex_analysis",
                name="Complex Multi-Step Analysis",
                description="Perform complex analytical task",
                task_type=TaskType.REASONING,
                messages=[
                    {
                        "role": "user",
                        "content": """Analyze the following scenario: A company notices unusual network traffic patterns, increased failed login attempts, and suspicious file access patterns. What could be happening, what steps should they take, and what are the potential risks?""",
                    }
                ],
                expected_response_keywords=[
                    "attack",
                    "investigation",
                    "isolation",
                    "forensics",
                    "incident",
                ],
                max_response_time=30.0,
                min_response_length=200,
            ),
            TestCase(
                id="stress_test",
                name="Stress Test - Long Prompt",
                description="Handle long, complex prompts",
                task_type=TaskType.TEXT_GENERATION,
                messages=[
                    {
                        "role": "user",
                        "content": """This is a stress test with a very long prompt. """
                        * 20
                        + """Please provide a comprehensive analysis of modern cybersecurity challenges, including threat actors, attack vectors, defensive strategies, emerging technologies, regulatory considerations, and future trends. Be thorough and detailed.""",
                    }
                ],
                expected_response_keywords=[
                    "cybersecurity",
                    "threats",
                    "defense",
                    "technology",
                    "future",
                ],
                max_response_time=45.0,
                min_response_length=500,
            ),
        ]

    async def test_single_provider(
        self, provider: APIProvider, test_case: TestCase
    ) -> TestResult:
        """Test a single provider with a specific test case"""

        start_time = time.time()

        try:
            logger.info(f"🧪 Testing {provider.value} with {test_case.name}")

            # Generate response
            response = await generate_ai_response(
                messages=test_case.messages,
                task_type=test_case.task_type,
                preferred_provider=provider,
                max_tokens=2000,
                temperature=0.7,
            )

            response_time = time.time() - start_time
            response_content = response.get("content", "")
            response_length = len(response_content)

            # Check if response contains expected keywords
            contains_keywords = any(
                keyword.lower() in response_content.lower()
                for keyword in test_case.expected_response_keywords
            )

            # Determine success
            success = (
                response_time <= test_case.max_response_time
                and response_length >= test_case.min_response_length
                and (not test_case.expected_response_keywords or contains_keywords)
            )

            result = TestResult(
                test_case_id=test_case.id,
                provider=provider,
                success=success,
                response_time=response_time,
                response_content=response_content[:500],  # Truncate for storage
                response_length=response_length,
                contains_keywords=contains_keywords,
            )

            if success:
                logger.info(
                    f"✅ {provider.value} passed {test_case.name} in {response_time:.2f}s"
                )
            else:
                logger.warning(
                    f"⚠️ {provider.value} failed {test_case.name}: time={response_time:.2f}s, length={response_length}, keywords={contains_keywords}"
                )

            return result

        except Exception as e:
            response_time = time.time() - start_time

            result = TestResult(
                test_case_id=test_case.id,
                provider=provider,
                success=False,
                response_time=response_time,
                error_message=str(e),
            )

            logger.error(f"❌ {provider.value} failed {test_case.name}: {e}")
            return result

    async def test_all_providers(
        self, test_case_ids: List[str] = None
    ) -> Dict[str, List[TestResult]]:
        """Test all available providers with specified test cases"""

        if test_case_ids is None:
            test_cases_to_run = self.test_cases
        else:
            test_cases_to_run = [tc for tc in self.test_cases if tc.id in test_case_ids]

        logger.info(
            f"🚀 Starting comprehensive testing of {len(self.api_manager.endpoints)} providers with {len(test_cases_to_run)} test cases"
        )

        all_results = {}

        for test_case in test_cases_to_run:
            logger.info(f"📋 Running test case: {test_case.name}")

            test_results = []

            # Test each available provider
            for provider in self.api_manager.endpoints.keys():
                if self.api_manager.endpoints[provider].enabled:
                    result = await self.test_single_provider(provider, test_case)
                    test_results.append(result)

                    # Small delay between tests to respect rate limits
                    await asyncio.sleep(1)

            all_results[test_case.id] = test_results

            # Brief pause between test cases
            await asyncio.sleep(2)

        self.test_results = all_results
        logger.info("✅ Comprehensive testing completed")

        return all_results

    async def run_stress_test(self, concurrent_requests: int = 5) -> Dict[str, Any]:
        """Run stress test with concurrent requests"""

        logger.info(
            f"🔥 Running stress test with {concurrent_requests} concurrent requests"
        )

        # Use basic chat test for stress testing
        basic_test = next(tc for tc in self.test_cases if tc.id == "basic_chat")

        stress_results = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_response_time": 0.0,
            "provider_performance": {},
            "start_time": datetime.now().isoformat(),
        }

        async def stress_request():
            """Single stress test request"""
            try:
                start_time = time.time()
                response = await generate_ai_response(
                    messages=basic_test.messages, task_type=basic_test.task_type
                )
                response_time = time.time() - start_time

                return {
                    "success": True,
                    "response_time": response_time,
                    "provider": response.get("provider", "unknown"),
                }
            except Exception as e:
                return {
                    "success": False,
                    "response_time": time.time() - start_time,
                    "error": str(e),
                }

        # Run concurrent requests
        tasks = [stress_request() for _ in range(concurrent_requests)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        total_response_time = 0

        for result in results:
            if isinstance(result, dict):
                stress_results["total_requests"] += 1

                if result["success"]:
                    stress_results["successful_requests"] += 1
                    total_response_time += result["response_time"]

                    provider = result.get("provider", "unknown")
                    if provider not in stress_results["provider_performance"]:
                        stress_results["provider_performance"][provider] = {
                            "requests": 0,
                            "total_time": 0,
                        }

                    stress_results["provider_performance"][provider]["requests"] += 1
                    stress_results["provider_performance"][provider][
                        "total_time"
                    ] += result["response_time"]
                else:
                    stress_results["failed_requests"] += 1

        # Calculate averages
        if stress_results["successful_requests"] > 0:
            stress_results["average_response_time"] = (
                total_response_time / stress_results["successful_requests"]
            )

        for provider_stats in stress_results["provider_performance"].values():
            if provider_stats["requests"] > 0:
                provider_stats["average_time"] = (
                    provider_stats["total_time"] / provider_stats["requests"]
                )

        stress_results["end_time"] = datetime.now().isoformat()

        logger.info(
            f"✅ Stress test completed: {stress_results['successful_requests']}/{stress_results['total_requests']} successful"
        )

        return stress_results

    def generate_test_report(self) -> str:
        """Generate comprehensive test report"""

        if not self.test_results:
            return "No test results available. Run tests first."

        report_lines = [
            "# 🧪 AMAS API Testing Suite - Comprehensive Report",
            "",
            f"**Generated:** {datetime.now().isoformat()}",
            f"**Total Test Cases:** {len(self.test_results)}",
            f"**Total Providers:** {len(self.api_manager.endpoints)}",
            "",
            "---",
            "",
        ]

        # Overall Statistics
        total_tests = sum(len(results) for results in self.test_results.values())
        successful_tests = sum(
            sum(1 for r in results if r.success)
            for results in self.test_results.values()
        )

        report_lines.extend(
            [
                "## 📊 Overall Statistics",
                "",
                f"**Total Tests Executed:** {total_tests}",
                f"**Successful Tests:** {successful_tests}",
                f"**Failed Tests:** {total_tests - successful_tests}",
                f"**Overall Success Rate:** {(successful_tests / total_tests * 100):.1f}%",
                "",
                "---",
                "",
            ]
        )

        # Provider Performance Summary
        provider_stats = {}

        for test_case_id, results in self.test_results.items():
            for result in results:
                provider = result.provider.value
                if provider not in provider_stats:
                    provider_stats[provider] = {
                        "total_tests": 0,
                        "successful_tests": 0,
                        "total_response_time": 0.0,
                        "fastest_response": float("inf"),
                        "slowest_response": 0.0,
                    }

                stats = provider_stats[provider]
                stats["total_tests"] += 1

                if result.success:
                    stats["successful_tests"] += 1
                    stats["total_response_time"] += result.response_time
                    stats["fastest_response"] = min(
                        stats["fastest_response"], result.response_time
                    )
                    stats["slowest_response"] = max(
                        stats["slowest_response"], result.response_time
                    )

        # Calculate averages and format stats
        for provider, stats in provider_stats.items():
            if stats["successful_tests"] > 0:
                stats["average_response_time"] = (
                    stats["total_response_time"] / stats["successful_tests"]
                )
                stats["success_rate"] = (
                    stats["successful_tests"] / stats["total_tests"]
                ) * 100
            else:
                stats["average_response_time"] = 0
                stats["success_rate"] = 0
                stats["fastest_response"] = 0

        report_lines.extend(
            [
                "## 🤖 Provider Performance Summary",
                "",
                "| Provider | Success Rate | Avg Response Time | Fastest | Slowest | Tests |",
                "|----------|--------------|-------------------|---------|---------|-------|",
            ]
        )

        # Sort providers by success rate
        sorted_providers = sorted(
            provider_stats.items(), key=lambda x: x[1]["success_rate"], reverse=True
        )

        for provider, stats in sorted_providers:
            report_lines.append(
                f"| {provider} | {stats['success_rate']:.1f}% | {stats['average_response_time']:.2f}s | "
                f"{stats['fastest_response']:.2f}s | {stats['slowest_response']:.2f}s | {stats['total_tests']} |"
            )

        report_lines.extend(["", "---", ""])

        # Test Case Details
        report_lines.extend(["## 📋 Test Case Details", ""])

        for test_case_id, results in self.test_results.items():
            test_case = next(tc for tc in self.test_cases if tc.id == test_case_id)

            successful_providers = [r.provider.value for r in results if r.success]
            failed_providers = [r.provider.value for r in results if not r.success]

            avg_response_time = (
                sum(r.response_time for r in results if r.success)
                / len(successful_providers)
                if successful_providers
                else 0
            )

            report_lines.extend(
                [
                    f"### {test_case.name}",
                    f"**Description:** {test_case.description}",
                    f"**Task Type:** {test_case.task_type.value}",
                    f"**Success Rate:** {len(successful_providers)}/{len(results)} ({len(successful_providers)/len(results)*100:.1f}%)",
                    f"**Average Response Time:** {avg_response_time:.2f}s",
                    "",
                ]
            )

            if successful_providers:
                report_lines.extend(
                    [
                        "**✅ Successful Providers:**",
                        ", ".join(successful_providers),
                        "",
                    ]
                )

            if failed_providers:
                report_lines.extend(
                    ["**❌ Failed Providers:**", ", ".join(failed_providers), ""]
                )

            report_lines.extend(["---", ""])

        # API Manager Status
        api_stats = self.api_manager.get_provider_statistics()

        report_lines.extend(
            [
                "## 🔧 API Manager Status",
                "",
                f"**Healthy Providers:** {api_stats['overview']['healthy_providers']}/{api_stats['overview']['total_providers']}",
                f"**System Success Rate:** {api_stats['overview']['success_rate']:.1f}%",
                f"**Total API Requests:** {api_stats['overview']['total_requests']}",
                "",
                "---",
                "",
            ]
        )

        # Recommendations
        report_lines.extend(
            [
                "## 🎯 Recommendations",
                "",
                "### High-Performing Providers:",
            ]
        )

        top_providers = sorted_providers[:3]
        for provider, stats in top_providers:
            if stats["success_rate"] > 80:
                report_lines.append(
                    f"- **{provider}**: {stats['success_rate']:.1f}% success rate, {stats['average_response_time']:.2f}s avg response"
                )

        report_lines.extend(
            [
                "",
                "### Areas for Improvement:",
            ]
        )

        bottom_providers = sorted_providers[-3:]
        for provider, stats in bottom_providers:
            if stats["success_rate"] < 50:
                report_lines.append(
                    f"- **{provider}**: {stats['success_rate']:.1f}% success rate - investigate connectivity/configuration"
                )

        report_lines.extend(
            [
                "",
                "### Optimization Suggestions:",
                "1. Prioritize high-performing providers in fallback chains",
                "2. Increase timeout values for slower but reliable providers",
                "3. Implement caching for frequently requested content",
                "4. Monitor rate limits and implement smarter request distribution",
                "",
                "---",
                "",
                f"*Report generated by AMAS API Testing Suite*",
                f"*Timestamp: {datetime.now().isoformat()}*",
            ]
        )

        return "\n".join(report_lines)

    async def validate_fallback_system(self) -> Dict[str, Any]:
        """Validate the fallback system by forcing failures"""

        logger.info("🔄 Testing fallback system reliability")

        validation_results = {
            "start_time": datetime.now().isoformat(),
            "fallback_tests": [],
            "total_fallbacks_triggered": 0,
            "successful_fallbacks": 0,
            "system_resilience_score": 0.0,
        }

        # Test fallback by disabling providers one by one
        original_states = {}

        try:
            for provider in self.api_manager.endpoints.keys():
                # Store original state
                original_states[provider] = self.api_manager.endpoints[provider].enabled

                # Disable this provider temporarily
                self.api_manager.disable_provider(provider)

                logger.info(f"🔴 Disabled {provider.value} to test fallback")

                # Try to generate response (should fallback to other providers)
                try:
                    response = await generate_ai_response(
                        messages=[{"role": "user", "content": "Test fallback system"}],
                        task_type=TaskType.CHAT_COMPLETION,
                        preferred_provider=provider,  # Try the disabled provider first
                    )

                    fallback_test = {
                        "disabled_provider": provider.value,
                        "fallback_successful": True,
                        "actual_provider_used": response.get("provider"),
                        "fallback_attempts": response.get("fallback_attempts", 1),
                        "response_time": response.get("response_time", 0),
                    }

                    validation_results["total_fallbacks_triggered"] += 1
                    validation_results["successful_fallbacks"] += 1

                    logger.info(
                        f"✅ Fallback successful: {provider.value} → {response.get('provider')}"
                    )

                except Exception as e:
                    fallback_test = {
                        "disabled_provider": provider.value,
                        "fallback_successful": False,
                        "error": str(e),
                    }

                    validation_results["total_fallbacks_triggered"] += 1

                    logger.warning(f"❌ Fallback failed for {provider.value}: {e}")

                validation_results["fallback_tests"].append(fallback_test)

                # Re-enable the provider
                self.api_manager.enable_provider(provider)

                # Brief pause
                await asyncio.sleep(1)

        finally:
            # Restore all original states
            for provider, original_state in original_states.items():
                if original_state:
                    self.api_manager.enable_provider(provider)
                else:
                    self.api_manager.disable_provider(provider)

        # Calculate resilience score
        if validation_results["total_fallbacks_triggered"] > 0:
            validation_results["system_resilience_score"] = (
                validation_results["successful_fallbacks"]
                / validation_results["total_fallbacks_triggered"]
                * 100
            )

        validation_results["end_time"] = datetime.now().isoformat()

        logger.info(
            f"✅ Fallback validation completed: {validation_results['successful_fallbacks']}/{validation_results['total_fallbacks_triggered']} successful"
        )

        return validation_results

async def run_comprehensive_validation():
    """Run comprehensive validation of the entire system"""

    logger.info("🚀 Starting comprehensive API validation")

    # Initialize testing suite
    test_suite = APITestingSuite()

    # 1. Health check all providers
    logger.info("🏥 Running health checks...")
    health_results = await test_suite.api_manager.health_check_all_providers()

    # 2. Run all test cases
    logger.info("🧪 Running all test cases...")
    test_results = await test_suite.test_all_providers()

    # 3. Run stress test
    logger.info("🔥 Running stress test...")
    stress_results = await test_suite.run_stress_test(concurrent_requests=10)

    # 4. Validate fallback system
    logger.info("🔄 Validating fallback system...")
    fallback_results = await test_suite.validate_fallback_system()

    # 5. Generate comprehensive report
    logger.info("📄 Generating comprehensive report...")
    test_report = test_suite.generate_test_report()

    # Save all results
    os.makedirs("artifacts", exist_ok=True)

    # Save test report
    with open("artifacts/api_validation_report.md", "w") as f:
        f.write(test_report)

    # Save detailed results
    with open("artifacts/api_test_results.json", "w") as f:
        json.dump(
            {
                "health_results": {k.value: v for k, v in health_results.items()},
                "test_results": {
                    k: [r.__dict__ for r in v] for k, v in test_results.items()
                },
                "stress_results": stress_results,
                "fallback_results": fallback_results,
                "timestamp": datetime.now().isoformat(),
            },
            f,
            indent=2,
            default=str,
        )

    logger.info("✅ Comprehensive validation completed!")
    logger.info("📄 Report saved to artifacts/api_validation_report.md")
    logger.info("📋 Detailed results saved to artifacts/api_test_results.json")

    return {
        "health_results": health_results,
        "test_results": test_results,
        "stress_results": stress_results,
        "fallback_results": fallback_results,
        "report": test_report,
    }

if __name__ == "__main__":
    asyncio.run(run_comprehensive_validation())
