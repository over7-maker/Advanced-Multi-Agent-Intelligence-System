#!/usr/bin/env python3
"""
AMAS Enhanced System Demonstration
Showcase the intelligent AI API manager with 16 provider fallback system
"""

import os
import sys
import asyncio
import json
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from amas.core.ai_api_manager import (
    IntelligentAPIManager, APIProvider, TaskType, 
    get_api_manager, generate_ai_response
)
from amas.core.enhanced_orchestrator import (
    EnhancedMultiAgentOrchestrator, 
    get_orchestrator, conduct_ai_investigation
)
from amas.core.api_testing_suite import (
    APITestingSuite, run_comprehensive_validation
)

async def demo_basic_fallback():
    """Demonstrate basic fallback functionality"""
    print("🔄 Demonstrating Basic Fallback System")
    print("=" * 50)
    
    try:
        # Simple chat completion with automatic fallback
        response = await generate_ai_response(
            messages=[{"role": "user", "content": "Hello! Please introduce yourself as an AI assistant."}],
            task_type=TaskType.CHAT_COMPLETION
        )
        
        print(f"✅ Response from {response['provider']} using {response['model']}:")
        print(f"🕐 Response time: {response['response_time']:.2f} seconds")
        print(f"🔄 Fallback attempts: {response.get('fallback_attempts', 1)}")
        print(f"📝 Response: {response['content'][:200]}...")
        
    except Exception as e:
        print(f"❌ All providers failed: {e}")
    
    print()

async def demo_specialized_tasks():
    """Demonstrate specialized task routing"""
    print("🎯 Demonstrating Specialized Task Routing")
    print("=" * 50)
    
    tasks = [
        {
            "name": "Code Analysis",
            "type": TaskType.CODE_ANALYSIS,
            "prompt": "Analyze this Python code for security issues:\n\ndef authenticate(username, password):\n    if username == 'admin' and password == 'password123':\n        return True\n    return False"
        },
        {
            "name": "Logical Reasoning",
            "type": TaskType.REASONING,
            "prompt": "If A implies B, and B implies C, and A is true, what can we conclude about C? Explain your reasoning."
        },
        {
            "name": "Text Summarization", 
            "type": TaskType.SUMMARIZATION,
            "prompt": "Summarize in 3 bullet points: Cybersecurity involves protecting digital systems from threats. Common threats include malware, phishing, and data breaches. Organizations implement firewalls, encryption, and training to defend against these threats."
        }
    ]
    
    for task in tasks:
        try:
            print(f"📋 Task: {task['name']}")
            
            response = await generate_ai_response(
                messages=[{"role": "user", "content": task["prompt"]}],
                task_type=task["type"]
            )
            
            print(f"✅ Completed by {response['provider']} in {response['response_time']:.2f}s")
            print(f"📝 Response: {response['content'][:150]}...")
            print()
            
        except Exception as e:
            print(f"❌ Task failed: {e}")
            print()

async def demo_system_status():
    """Demonstrate system status and monitoring"""
    print("📊 System Status and Health Monitoring")
    print("=" * 50)
    
    api_manager = get_api_manager()
    
    # Get comprehensive statistics
    stats = api_manager.get_provider_statistics()
    
    print(f"🤖 Total Providers: {stats['overview']['total_providers']}")
    print(f"✅ Healthy Providers: {stats['overview']['healthy_providers']}")
    print(f"📈 Overall Success Rate: {stats['overview']['success_rate']:.1f}%")
    print(f"📊 Total Requests: {stats['overview']['total_requests']}")
    print()
    
    print("🔍 Provider Details:")
    for provider, details in stats['providers'].items():
        status_emoji = {
            'healthy': '✅',
            'degraded': '⚠️',
            'unhealthy': '❌',
            'disabled': '🚫',
            'unknown': '❓'
        }.get(details['status'], '❓')
        
        print(f"{status_emoji} {details['name']}: {details['status']} | "
              f"Priority: {details['priority']} | "
              f"Usage: {details['usage_count']} | "
              f"Avg Time: {details['average_response_time']:.2f}s")
    
    print()

async def demo_multi_agent_investigation():
    """Demonstrate multi-agent investigation"""
    print("🕵️ Multi-Agent Investigation Demonstration")
    print("=" * 50)
    
    topic = "AI security vulnerabilities in modern applications"
    
    try:
        print(f"🔍 Starting investigation: {topic}")
        
        # Run comprehensive investigation
        investigation = await conduct_ai_investigation(topic, "comprehensive")
        
        print(f"✅ Investigation completed in {investigation.get('duration', 0):.2f} seconds")
        print(f"📋 Phases completed: {len(investigation['phases'])}")
        print(f"🤖 Agents used: {', '.join(investigation['agents_used'])}")
        print(f"🔧 API providers used: {', '.join(investigation['api_usage'].keys())}")
        
        # Show summary of each phase
        print("\n📄 Phase Summary:")
        for phase in investigation['phases']:
            print(f"  • {phase['phase'].replace('_', ' ').title()}: "
                  f"{phase['agent']} using {phase.get('provider_used', 'Unknown')} "
                  f"({phase['duration']:.1f}s)")
        
        print(f"\n📊 Performance Metrics:")
        if 'performance_metrics' in investigation:
            metrics = investigation['performance_metrics']
            print(f"  • Unique providers used: {metrics.get('unique_providers_used', 0)}")
            print(f"  • Successful phases: {metrics.get('successful_phases', 0)}/{metrics.get('total_phases', 0)}")
        
    except Exception as e:
        print(f"❌ Investigation failed: {e}")
    
    print()

async def demo_stress_test():
    """Demonstrate system resilience under load"""
    print("🔥 Stress Testing and Resilience")
    print("=" * 50)
    
    try:
        # Create simple stress test
        concurrent_requests = 5
        print(f"🚀 Running {concurrent_requests} concurrent requests...")
        
        start_time = datetime.now()
        
        # Run multiple requests concurrently
        tasks = []
        for i in range(concurrent_requests):
            task = generate_ai_response(
                messages=[{"role": "user", "content": f"Stress test request #{i+1}. Please respond briefly."}],
                task_type=TaskType.CHAT_COMPLETION
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Analyze results
        successful = sum(1 for r in results if isinstance(r, dict))
        failed = len(results) - successful
        
        providers_used = {}
        total_response_time = 0
        
        for result in results:
            if isinstance(result, dict):
                provider = result.get('provider', 'unknown')
                providers_used[provider] = providers_used.get(provider, 0) + 1
                total_response_time += result.get('response_time', 0)
        
        print(f"✅ Stress test completed in {duration:.2f} seconds")
        print(f"📊 Results: {successful} successful, {failed} failed")
        print(f"⚡ Average response time: {total_response_time/successful:.2f}s" if successful > 0 else "⚡ No successful responses")
        print(f"🔧 Providers used: {', '.join(f'{p}({c})' for p, c in providers_used.items())}")
        
    except Exception as e:
        print(f"❌ Stress test failed: {e}")
    
    print()

async def main():
    """Main demonstration function"""
    print("🚀 AMAS Enhanced AI API Management System")
    print("🔧 Intelligent Fallback with 16 AI Providers")
    print("=" * 60)
    print()
    
    # Check API key availability
    print("🔑 Checking API Key Availability:")
    api_keys = [
        "CEREBRAS_API_KEY", "CODESTRAL_API_KEY", "DEEPSEEK_API_KEY", 
        "GEMINIAI_API_KEY", "GLM_API_KEY", "GPTOSS_API_KEY", "GROK_API_KEY",
        "GROQAI_API_KEY", "KIMI_API_KEY", "NVIDIA_API_KEY", "QWEN_API_KEY",
        "GEMINI2_API_KEY", "GROQ2_API_KEY", "COHERE_API_KEY", "CHUTES_API_KEY"
    ]
    
    available_keys = 0
    for key in api_keys:
        if os.getenv(key):
            available_keys += 1
            print(f"  ✅ {key}")
        else:
            print(f"  ❌ {key} (not set)")
    
    print(f"\n📊 Available API Keys: {available_keys}/{len(api_keys)}")
    
    if available_keys == 0:
        print("⚠️  No API keys found. Please set at least one API key to test the system.")
        print("   Example: export DEEPSEEK_API_KEY='your-api-key-here'")
        return
    
    print("\n" + "=" * 60)
    
    # Run demonstrations
    await demo_system_status()
    await demo_basic_fallback()
    await demo_specialized_tasks()
    await demo_stress_test()
    
    # Only run investigation if we have multiple providers
    if available_keys > 1:
        await demo_multi_agent_investigation()
    else:
        print("🕵️ Multi-Agent Investigation")
        print("=" * 50)
        print("⚠️  Multi-agent investigation requires multiple API providers.")
        print("   Please configure additional API keys for full demonstration.")
        print()
    
    print("🎉 Demonstration completed!")
    print("💡 The system automatically handles:")
    print("   • Intelligent provider selection based on task type")
    print("   • Automatic failover when providers are unavailable") 
    print("   • Rate limit management and request distribution")
    print("   • Performance monitoring and optimization")
    print("   • Multi-agent orchestration with specialized roles")
    print()
    print("📄 For detailed testing, run: python -m amas.core.api_testing_suite")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Demonstration interrupted by user")
    except Exception as e:
        print(f"\n❌ Demonstration failed: {e}")
        import traceback
        traceback.print_exc()