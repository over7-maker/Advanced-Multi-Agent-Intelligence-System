#!/usr/bin/env python3
"""
Test script for Universal AI Workflow that handles failures properly
"""
import asyncio
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path.cwd()))

from standalone_universal_ai_manager import get_manager as get_universal_ai_manager


async def main():
    manager = get_universal_ai_manager()
    
    # Show configuration
    print(manager.get_config_summary())
    print()
    
    # Test generation with all strategies
    strategies = ["priority", "intelligent", "fastest"]
    
    for strategy in strategies:
        print(f"🧪 Testing {strategy} strategy...")
        result = await manager.generate(
            prompt="Write a brief test message confirming the AI system is working.",
            system_prompt="You are a helpful AI assistant.",
            strategy=strategy,
            max_tokens=100,
        )
        
        if result and result.get("success"):
            print(f"✅ {strategy.upper()} - Success with {result['provider_name']}")
            # Only access 'content' if the request was successful
            if "content" in result:
                print(f"   Response: {result['content'][:100]}...")
            else:
                print("   Response: <No content returned>")
            print(f"   Time: {result.get('response_time', 0):.2f}s")
        else:
            error_msg = result.get("error", "Unknown error") if result else "No result returned"
            print(f"❌ {strategy.upper()} - Failed: {error_msg}")
        print()
    
    # Show final stats
    print("=" * 80)
    print("📊 FINAL STATISTICS")
    print("=" * 80)
    stats = manager.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    print()
    
    # Show provider health
    print("=" * 80)
    print("🏥 PROVIDER HEALTH")
    print("=" * 80)
    health = manager.get_provider_health()
    for provider_id, info in health.items():
        status_emoji = "✅" if info["available"] else "❌"
        print(
            f"{status_emoji} {info['name']:25s} | Success: {info['success_rate']:6s} | Avg Time: {info['avg_response_time']:8s}"
        )


if __name__ == "__main__":
    asyncio.run(main())