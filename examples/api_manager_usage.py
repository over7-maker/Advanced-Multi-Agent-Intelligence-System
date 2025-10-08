#!/usr/bin/env python3
"""
AMAS AI API Manager - Comprehensive Usage Examples

This module demonstrates how to use the AMAS AI API Manager with all 16 API providers
and showcases the robust fallback mechanisms for maximum reliability.
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Any, Dict, List

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from amas.core.ai_api_manager import AIAPIManager, get_ai_response
from amas.core.api_integration import (
    EnhancedAgentOrchestrator,
    initialize_enhanced_system,
)
from amas.core.enhanced_orchestrator import (
    EnhancedOrchestrator,
    execute_task,
    run_investigation,
)

class APIManagerExamples:
    """Comprehensive examples of using the AI API Manager"""

    def __init__(self):
        self.api_manager = AIAPIManager()
        self.orchestrator = EnhancedOrchestrator()

    async def example_basic_usage(self):
        """Example 1: Basic API usage with automatic fallback"""
        print("🚀 Example 1: Basic API Usage with Automatic Fallback")
        print("=" * 60)

        try:
            # Simple AI request with automatic fallback
            response = await get_ai_response(
                prompt="Explain artificial intelligence in one paragraph.",
                system_prompt="You are a helpful AI assistant.",
                max_tokens=200,
                temperature=0.7,
            )

            print(f"✅ Success! API used: {response['api_used']}")
            print(f"📝 Response: {response['content']}")
            print(f"🔧 Model: {response['model']}")
            print(f"⏰ Timestamp: {response['timestamp']}")

        except Exception as e:
            print(f"❌ Error: {e}")

    async def example_task_specific_apis(self):
        """Example 2: Task-specific API selection"""
        print("\n🔍 Example 2: Task-Specific API Selection")
        print("=" * 60)

        tasks = [
            {
                "name": "OSINT Collection",
                "prompt": "Collect intelligence on recent cybersecurity threats targeting critical infrastructure.",
                "task_type": "osint",
                "system_prompt": "You are an OSINT specialist. Focus on accuracy and source verification.",
            },
            {
                "name": "Code Analysis",
                "prompt": 'Analyze this code for security vulnerabilities: def login(username, password): return username == "admin" and password == "password"',
                "task_type": "code_analysis",
                "system_prompt": "You are a code security expert. Identify vulnerabilities and provide remediation.",
            },
            {
                "name": "Threat Analysis",
                "prompt": "Analyze the threat landscape for advanced persistent threats targeting software supply chains.",
                "task_type": "analysis",
                "system_prompt": "You are a threat intelligence analyst. Provide detailed analysis with recommendations.",
            },
        ]

        for task in tasks:
            try:
                print(f"\n📋 Task: {task['name']}")
                response = await get_ai_response(
                    prompt=task["prompt"],
                    system_prompt=task["system_prompt"],
                    task_type=task["task_type"],
                    max_tokens=300,
                )

                print(f"✅ Success! API used: {response['api_used']}")
                print(f"📝 Response preview: {response['content'][:200]}...")

            except Exception as e:
                print(f"❌ Task failed: {e}")

    async def example_health_monitoring(self):
        """Example 3: API health monitoring"""
        print("\n🏥 Example 3: API Health Monitoring")
        print("=" * 60)

        # Get comprehensive health status
        health_status = self.api_manager.get_health_status()

        print(f"📊 Health Status Summary:")
        print(f"  Total APIs: {health_status['total_apis']}")
        print(f"  Healthy APIs: {health_status['healthy_apis']}")
        print(f"  Unhealthy APIs: {health_status['unhealthy_apis']}")
        print(f"  Rate Limited APIs: {health_status['rate_limited_apis']}")

        print(f"\n🔍 Individual API Status:")
        for api_name, status in health_status["apis"].items():
            health_icon = "✅" if status["is_healthy"] else "❌"
            print(f"  {health_icon} {status['name']}: {status['is_healthy']}")
            print(f"    - Requests: {status['total_requests']}")
            print(f"    - Success Rate: {(1 - status['error_rate']) * 100:.1f}%")
            print(f"    - Avg Response Time: {status['average_response_time']:.2f}s")

    async def example_parallel_processing(self):
        """Example 4: Parallel task processing"""
        print("\n⚡ Example 4: Parallel Task Processing")
        print("=" * 60)

        # Create multiple tasks
        tasks = [
            {
                "task_id": f"parallel_task_{i}",
                "task_type": "analysis",
                "prompt": f"Analyze threat vector {i} and provide security recommendations.",
                "agent_type": "analysis_agent",
            }
            for i in range(5)
        ]

        print(f"🚀 Executing {len(tasks)} tasks in parallel...")

        # Execute tasks in parallel
        results = await self.orchestrator.execute_parallel_tasks(
            tasks, max_concurrent=3
        )

        print(f"📊 Results:")
        successful = len([r for r in results if r.success])
        print(f"  Successful: {successful}/{len(results)}")
        print(f"  Success Rate: {(successful/len(results))*100:.1f}%")

        # Show API usage distribution
        api_usage = {}
        for result in results:
            if result.api_used:
                api_usage[result.api_used] = api_usage.get(result.api_used, 0) + 1

        print(f"  API Usage Distribution: {api_usage}")

    async def example_investigation_workflow(self):
        """Example 5: Comprehensive investigation workflow"""
        print("\n🔍 Example 5: Comprehensive Investigation Workflow")
        print("=" * 60)

        investigation_topic = (
            "Advanced Persistent Threats targeting software supply chains"
        )

        print(f"🎯 Investigation Topic: {investigation_topic}")
        print(f"🚀 Starting comprehensive investigation...")

        try:
            # Run comprehensive investigation
            investigation = await run_investigation(
                topic=investigation_topic, investigation_type="comprehensive"
            )

            print(f"✅ Investigation completed!")
            print(f"📊 Phases executed: {len(investigation['phases'])}")
            print(f"⏰ Started: {investigation['started_at']}")
            print(f"⏰ Completed: {investigation['completed_at']}")

            # Show phase results
            for i, phase in enumerate(investigation["phases"], 1):
                result = phase["result"]
                status_icon = "✅" if result.success else "❌"
                print(f"  {status_icon} Phase {i}: {phase['task_type']}")
                if result.success:
                    print(f"    - API used: {result.api_used}")
                    print(f"    - Execution time: {result.execution_time:.2f}s")
                else:
                    print(f"    - Error: {result.error}")

            # Show final report availability
            if investigation["final_report"]:
                print(
                    f"📄 Final report available: {len(investigation['final_report'])} characters"
                )
            else:
                print(f"📄 Final report: Not available")

        except Exception as e:
            print(f"❌ Investigation failed: {e}")

    async def example_streaming_response(self):
        """Example 6: Streaming response generation"""
        print("\n🌊 Example 6: Streaming Response Generation")
        print("=" * 60)

        try:
            print("🔄 Generating streaming response...")

            async for chunk in self.api_manager.generate_streaming_response(
                prompt="Write a short story about AI and cybersecurity.",
                system_prompt="You are a creative writer specializing in technology themes.",
                max_tokens=200,
            ):
                print(chunk["content"], end="", flush=True)

            print(f"\n✅ Streaming completed!")

        except Exception as e:
            print(f"❌ Streaming failed: {e}")

    async def example_error_handling(self):
        """Example 7: Error handling and recovery"""
        print("\n🛡️ Example 7: Error Handling and Recovery")
        print("=" * 60)

        # Test with a request that might fail
        try:
            response = await get_ai_response(
                prompt="This is a test request that might fail.",
                max_tokens=50,
                timeout=5,  # Short timeout to potentially trigger errors
            )

            print(f"✅ Request succeeded: {response['api_used']}")

        except Exception as e:
            print(f"❌ Request failed: {e}")
            print(f"🔄 The system will automatically retry with other APIs")

    async def example_performance_metrics(self):
        """Example 8: Performance metrics and optimization"""
        print("\n📈 Example 8: Performance Metrics and Optimization")
        print("=" * 60)

        # Get performance statistics
        stats = self.orchestrator.get_performance_stats()

        print(f"📊 Performance Statistics:")
        print(f"  Total tasks: {stats['total_tasks']}")
        print(f"  Successful tasks: {stats['successful_tasks']}")
        print(f"  Failed tasks: {stats['failed_tasks']}")
        print(f"  Success rate: {stats['success_rate']:.1f}%")
        print(f"  Average execution time: {stats['average_execution_time']:.2f}s")

        # Show API usage distribution
        if stats["api_usage"]:
            print(f"  API Usage Distribution:")
            for api, count in stats["api_usage"].items():
                print(f"    - {api}: {count} requests")

        # Show task type statistics
        if stats["task_type_stats"]:
            print(f"  Task Type Statistics:")
            for task_type, type_stats in stats["task_type_stats"].items():
                success_rate = (type_stats["successful"] / type_stats["total"]) * 100
                print(f"    - {task_type}: {success_rate:.1f}% success rate")

    async def example_custom_agent_workflow(self):
        """Example 9: Custom agent workflow"""
        print("\n🤖 Example 9: Custom Agent Workflow")
        print("=" * 60)

        try:
            # Initialize enhanced system
            await initialize_enhanced_system()

            # Create custom investigation
            investigation = await run_investigation(
                topic="AI-powered cyber attacks and defense strategies",
                investigation_type="focused",
            )

            print(f"✅ Custom investigation completed!")
            print(f"📊 Phases: {len(investigation['phases'])}")

            # Show results
            for phase in investigation["phases"]:
                result = phase["result"]
                if result.success:
                    print(f"✅ {phase['task_type']}: {result.api_used}")
                else:
                    print(f"❌ {phase['task_type']}: {result.error}")

        except Exception as e:
            print(f"❌ Custom workflow failed: {e}")

    async def example_api_health_check(self):
        """Example 10: Comprehensive API health check"""
        print("\n🏥 Example 10: Comprehensive API Health Check")
        print("=" * 60)

        try:
            # Perform health check
            health_results = await self.api_manager.health_check()

            print(f"🔍 Health Check Results:")
            for api_name, result in health_results.items():
                status_icon = "✅" if result["status"] == "healthy" else "❌"
                print(f"  {status_icon} {api_name}: {result['status']}")

                if result["status"] == "healthy":
                    print(f"    - Response time: {result.get('response_time', 0):.2f}s")
                else:
                    print(f"    - Error: {result.get('error', 'Unknown error')}")

        except Exception as e:
            print(f"❌ Health check failed: {e}")

async def main():
    """Run all examples"""
    print("🚀 AMAS AI API Manager - Comprehensive Usage Examples")
    print("=" * 80)
    print("This demonstrates the full capabilities of the multi-API fallback system")
    print("with 16 different AI providers for maximum reliability.")
    print("=" * 80)

    examples = APIManagerExamples()

    # Run all examples
    await examples.example_basic_usage()
    await examples.example_task_specific_apis()
    await examples.example_health_monitoring()
    await examples.example_parallel_processing()
    await examples.example_investigation_workflow()
    await examples.example_streaming_response()
    await examples.example_error_handling()
    await examples.example_performance_metrics()
    await examples.example_custom_agent_workflow()
    await examples.example_api_health_check()

    print("\n🎉 All examples completed!")
    print("=" * 80)
    print("The AMAS AI API Manager provides:")
    print("✅ Automatic fallback between 16 AI providers")
    print("✅ Intelligent API selection based on task type")
    print("✅ Health monitoring and performance tracking")
    print("✅ Parallel processing and concurrent execution")
    print("✅ Comprehensive error handling and recovery")
    print("✅ Streaming response generation")
    print("✅ Advanced investigation workflows")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
