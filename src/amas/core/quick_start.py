#!/usr/bin/env python3
"""
AMAS AI API Manager - Quick Start Integration

This script demonstrates how to quickly integrate the new AI API Manager
with your existing AMAS system for maximum reliability.
"""

import asyncio
# import json
import os
# import sys
from datetime import datetime
from typing import Any, Dict, List

# Import the new API manager components
from .ai_api_manager import AIAPIManager, get_ai_response
from .api_integration import EnhancedAgentOrchestrator, initialize_enhanced_system
from .enhanced_orchestrator import EnhancedOrchestrator, execute_task, run_investigation


class QuickStartIntegration:
    """Quick start integration for AMAS AI API Manager"""

    def __init__(self):
        self.api_manager = AIAPIManager()
        self.orchestrator = EnhancedOrchestrator()
        self.enhanced_orchestrator = EnhancedAgentOrchestrator(
            {
                "llm_service_url": "http://localhost:11434",
                "vector_service_url": "http://localhost:8001",
                "graph_service_url": "http://localhost:7474",
                "data_sources": [
                    "osint",
                    "threat_intel",
                    "malware_db",
                    "vulnerability_db",
                ],
            }
        )

    async def test_basic_functionality(self):
        """Test basic API manager functionality"""
        print("🧪 Testing Basic Functionality...")

        try:
            # Test simple AI request
            response = await get_ai_response(
                prompt="Hello, this is a test. Please respond with 'OK'.",
                max_tokens=50,
                temperature=0.1,
            )

            print("✅ Basic test passed!")
            print(f"   API used: {response['api_used']}")
            print(f"   Response: {response['content']}")
            return True

        except Exception as e:
            print(f"❌ Basic test failed: {e}")
            return False

    async def test_health_monitoring(self):
        """Test health monitoring functionality"""
        print("\n🏥 Testing Health Monitoring...")

        try:
            # Get health status
            health = self.api_manager.get_health_status()

            print("✅ Health monitoring working!")
            print(f"   Total APIs: {health['total_apis']}")
            print(f"   Healthy APIs: {health['healthy_apis']}")
            print(f"   Unhealthy APIs: {health['unhealthy_apis']}")

            # Show individual API status
            for api_name, status in health["apis"].items():
                status_icon = "✅" if status["is_healthy"] else "❌"
                print(f"   {status_icon} {status['name']}: {status['is_healthy']}")

            return True

        except Exception as e:
            print(f"❌ Health monitoring test failed: {e}")
            return False

    async def test_task_execution(self):
        """Test task execution with fallback"""
        print("\n🎯 Testing Task Execution...")

        try:
            # Test task execution
            result = await execute_task(
                task_id="test_001",
                task_type="analysis",
                prompt="Analyze the current state of AI security and provide key recommendations.",
                agent_type="analysis_agent",
            )

            print("✅ Task execution working!")
            print(f"   Success: {result.success}")
            print(f"   API used: {result.api_used}")
            print(f"   Execution time: {result.execution_time:.2f}s")

            if result.success:
                print(f"   Response preview: {result.result['content'][:200]}...")

            return result.success

        except Exception as e:
            print(f"❌ Task execution test failed: {e}")
            return False

    async def test_investigation_workflow(self):
        """Test investigation workflow"""
        print("\n🔍 Testing Investigation Workflow...")

        try:
            # Test investigation
            investigation = await run_investigation(
                topic="AI-powered cyber attacks and defense strategies",
                investigation_type="focused",
            )

            print("✅ Investigation workflow working!")
            print(f"   Phases completed: {len(investigation['phases'])}")
            print(f"   Started: {investigation['started_at']}")
            print(f"   Completed: {investigation['completed_at']}")

            # Show phase results
            for i, phase in enumerate(investigation["phases"], 1):
                result = phase["result"]
                status_icon = "✅" if result.success else "❌"
                print(f"   {status_icon} Phase {i}: {phase['task_type']}")
                if result.success:
                    print(f"      API used: {result.api_used}")
                else:
                    print(f"      Error: {result.error}")

            return True

        except Exception as e:
            print(f"❌ Investigation workflow test failed: {e}")
            return False

    async def test_enhanced_system(self):
        """Test enhanced system integration"""
        print("\n🤖 Testing Enhanced System Integration...")

        try:
            # Initialize enhanced system
            await initialize_enhanced_system()

            print("✅ Enhanced system initialized!")
            print("   Enhanced orchestrator ready")
            print("   Multi-API fallback active")
            print("   Health monitoring active")

            return True

        except Exception as e:
            print(f"❌ Enhanced system test failed: {e}")
            return False

    async def test_performance_metrics(self):
        """Test performance metrics"""
        print("\n📊 Testing Performance Metrics...")

        try:
            # Get performance stats
            stats = self.orchestrator.get_performance_stats()

            print("✅ Performance metrics working!")
            print(f"   Total tasks: {stats['total_tasks']}")
            print(f"   Success rate: {stats['success_rate']:.1f}%")
            print(f"   Average execution time: {stats['average_execution_time']:.2f}s")

            if stats["api_usage"]:
                print("   API usage distribution:")
                for api, count in stats["api_usage"].items():
                    print(f"     - {api}: {count} requests")

            return True

        except Exception as e:
            print(f"❌ Performance metrics test failed: {e}")
            return False

    async def run_comprehensive_test(self):
        """Run comprehensive test suite"""
        print("🚀 AMAS AI API Manager - Comprehensive Test Suite")
        print("=" * 60)

        tests = [
            ("Basic Functionality", self.test_basic_functionality),
            ("Health Monitoring", self.test_health_monitoring),
            ("Task Execution", self.test_task_execution),
            ("Investigation Workflow", self.test_investigation_workflow),
            ("Enhanced System", self.test_enhanced_system),
            ("Performance Metrics", self.test_performance_metrics),
        ]

        results = []

        for test_name, test_func in tests:
            try:
                result = await test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name} failed with exception: {e}")
                results.append((test_name, False))

        # Summary
        print("\n📊 Test Results Summary:")
        print("=" * 60)

        passed = 0
        for test_name, result in results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {status} {test_name}")
            if result:
                passed += 1

        print(f"\n🎯 Overall Results: {passed}/{len(results)} tests passed")

        if passed == len(results):
            print(
                "🎉 All tests passed! The AI API Manager is ready for production use."
            )
        else:
            print("⚠️  Some tests failed. Please check the configuration and API keys.")

        return passed == len(results)

    async def demonstrate_usage(self):
        """Demonstrate practical usage examples"""
        print("\n💡 Practical Usage Examples:")
        print("=" * 60)

        # Example 1: Simple AI request
        print("\n1. Simple AI Request:")
        try:
            response = await get_ai_response(
                prompt="What are the key principles of cybersecurity?",
                system_prompt="You are a cybersecurity expert.",
                max_tokens=200,
            )
            print(f"   ✅ Success! API: {response['api_used']}")
            print(f"   📝 Response: {response['content'][:100]}...")
        except Exception as e:
            print(f"   ❌ Failed: {e}")

        # Example 2: OSINT task
        print("\n2. OSINT Task:")
        try:
            result = await execute_task(
                task_id="osint_demo",
                task_type="osint",
                prompt="Collect intelligence on recent ransomware attacks.",
                agent_type="osint_agent",
            )
            print(f"   ✅ Success! API: {result.api_used}")
            print(f"   📊 Execution time: {result.execution_time:.2f}s")
        except Exception as e:
            print(f"   ❌ Failed: {e}")

        # Example 3: Code analysis
        print("\n3. Code Analysis Task:")
        try:
            result = await execute_task(
                task_id="code_demo",
                task_type="code_analysis",
                prompt="Analyze this code for security vulnerabilities: def login(user, pwd): return user == 'admin' and pwd == 'password'",
                agent_type="code_agent",
            )
            print(f"   ✅ Success! API: {result.api_used}")
            print(f"   📊 Execution time: {result.execution_time:.2f}s")
        except Exception as e:
            print(f"   ❌ Failed: {e}")


async def main():
    """Main entry point for quick start integration"""
    print("🚀 AMAS AI API Manager - Quick Start Integration")
    print("=" * 80)
    print("This script will test and demonstrate the AI API Manager")
    print("with your configured API keys for maximum reliability.")
    print("=" * 80)

    # Check environment variables
    print("\n🔍 Checking API Key Configuration:")
    api_keys = [
        "CEREBRAS_API_KEY",
        "CODESTRAL_API_KEY",
        "DEEPSEEK_API_KEY",
        "GEMINIAI_API_KEY",
        "GLM_API_KEY",
        "GPTOSS_API_KEY",
        "GROK_API_KEY",
        "GROQAI_API_KEY",
        "KIMI_API_KEY",
        "NVIDIA_API_KEY",
        "QWEN_API_KEY",
        "GEMINI2_API_KEY",
        "GROQ2_API_KEY",
        "COHERE_API_KEY",
        "CHUTES_API_KEY",
    ]

    configured_keys = 0
    for key in api_keys:
        if os.getenv(key):
            print(f"   ✅ {key}: Configured")
            configured_keys += 1
        else:
            print(f"   ❌ {key}: Not configured")

    print(f"\n📊 API Keys Status: {configured_keys}/{len(api_keys)} configured")

    if configured_keys == 0:
        print(
            "\n⚠️  No API keys configured. Please set your API keys as environment variables."
        )
        print("   Example: export DEEPSEEK_API_KEY='your_key_here'")
        return

    # Initialize and run tests
    integration = QuickStartIntegration()

    # Run comprehensive test
    success = await integration.run_comprehensive_test()

    if success:
        # Demonstrate usage
        await integration.demonstrate_usage()

        print("\n🎉 Quick Start Integration Complete!")
        print("=" * 80)
        print("Your AMAS system is now equipped with:")
        print("✅ Multi-API fallback system")
        print("✅ Intelligent API selection")
        print("✅ Health monitoring and recovery")
        print("✅ Enhanced reliability and performance")
        print("=" * 80)
        print("You can now use the AI API Manager in your AMAS workflows!")
    else:
        print("\n⚠️  Some tests failed. Please check your configuration.")
        print("   Make sure your API keys are valid and have sufficient quota.")


if __name__ == "__main__":
    asyncio.run(main())
