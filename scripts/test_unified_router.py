#!/usr/bin/env python3
"""
Test script for the Unified AI Router
Validates the router can handle OpenRouter keys and fallback properly
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from amas.agents.unified_ai_router import UnifiedAIRouter, get_ai_router
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


async def test_router():
    """Test the unified AI router"""
    print("\n" + "=" * 60)
    print("Testing Unified AI Router")
    print("=" * 60 + "\n")

    # Initialize router
    router = get_ai_router()

    # Display current configuration
    print("Current Model Configuration:")
    print("-" * 40)
    status = router.get_status()
    for model_id, info in status["models"].items():
        print(
            f"{model_id}: {info['provider']} - {info['model']} (Available: {info['available']})"
        )

    print(f"\nTotal configured models: {len(status['models'])}")
    print(f"Available models: {status['available_models']}")

    # Test each model
    print("\n" + "=" * 60)
    print("Testing Individual Models")
    print("=" * 60 + "\n")

    test_results = await router.test_all_models()

    working_models = sum(1 for v in test_results.values() if v)
    print(f"\nWorking models: {working_models}/{len(test_results)}")

    # Test fallback mechanism
    if working_models > 0:
        print("\n" + "=" * 60)
        print("Testing Fallback Mechanism")
        print("=" * 60 + "\n")

        messages = [
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": "What is 2+2? Reply with just the number."},
        ]

        try:
            response, model_used, metadata = await router.complete(
                messages, max_tokens=10
            )
            print(f"✓ Fallback test successful!")
            print(f"  Model used: {model_used}")
            print(f"  Response: {response}")
            print(f"  Provider: {metadata['provider']}")
            if metadata.get("cost_estimate"):
                print(f"  Estimated cost: ${metadata['cost_estimate']:.6f}")
        except Exception as e:
            print(f"✗ Fallback test failed: {e}")

    # Test agent helper function
    print("\n" + "=" * 60)
    print("Testing Agent Integration")
    print("=" * 60 + "\n")

    from amas.agents.unified_ai_router import agent_complete

    try:
        agent_messages = [
            {"role": "system", "content": "You are a code analysis agent."},
            {
                "role": "user",
                "content": "Is Python a good language? Answer in 5 words or less.",
            },
        ]

        response, metadata = await agent_complete(
            "test_agent", agent_messages, max_tokens=20
        )

        print(f"✓ Agent integration test successful!")
        print(f"  Response: {response}")
        print(f"  Model: {metadata.get('model_used', 'unknown')}")
    except Exception as e:
        print(f"✗ Agent integration test failed: {e}")

    # Final status
    print("\n" + "=" * 60)
    print("Final Router Status")
    print("=" * 60 + "\n")

    final_status = router.get_status()
    print(f"Total requests: {final_status['total_requests']}")
    print(f"Total failures: {final_status['total_failures']}")
    print(f"Available models: {final_status['available_models']}")

    # Recommendations
    print("\n" + "=" * 60)
    print("Recommendations")
    print("=" * 60 + "\n")

    if working_models == 0:
        print("❌ No working models found!")
        print("\nTo fix this:")
        print("1. Ensure you have valid API keys in your .env file")
        print("2. For OpenRouter: Use keys starting with 'sk-or-v1-'")
        print("3. For direct APIs: Use the provider's actual API keys")
        print("4. Consider setting up Ollama locally for offline fallback")
    elif working_models < 3:
        print("⚠️  Limited models available")
        print("\nConsider:")
        print("1. Adding more API keys for redundancy")
        print("2. Setting up local models with Ollama")
        print("3. Getting API keys from multiple providers")
    else:
        print("✅ Good model coverage!")
        print("The system has sufficient redundancy for reliable operation.")


if __name__ == "__main__":
    asyncio.run(test_router())
