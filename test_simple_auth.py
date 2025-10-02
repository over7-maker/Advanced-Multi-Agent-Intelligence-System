#!/usr/bin/env python3
"""
Simple authentication test for AMAS AI providers
"""

import os
import asyncio
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    logger.info("✓ Loaded .env file")
except ImportError:
    logger.warning("python-dotenv not installed, using environment variables directly")

# OpenAI client for OpenRouter
from openai import AsyncOpenAI

async def test_openrouter_auth():
    """Test OpenRouter authentication"""
    logger.info("=== Testing OpenRouter Authentication ===")
    
    # Get API key
    api_key = os.getenv('OPENROUTER_API_KEY', '')
    
    if not api_key or api_key == 'your_openrouter_api_key_here':
        logger.error("❌ No valid OpenRouter API key found!")
        logger.info("\nTo fix this:")
        logger.info("1. Get a free API key from: https://openrouter.ai/keys")
        logger.info("2. Update the .env file:")
        logger.info("   OPENROUTER_API_KEY=your_actual_key_here")
        return False
    
    logger.info(f"✓ Found API key: {api_key[:8]}...{api_key[-4:]}")
    
    # Test API call
    try:
        client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        
        logger.info("Testing API connection...")
        response = await client.chat.completions.create(
            model="deepseek/deepseek-chat-v3.1:free",
            messages=[{"role": "user", "content": "Say 'Hello, AMAS is working!'"}],
            max_tokens=50
        )
        
        result = response.choices[0].message.content
        logger.info(f"✓ API Response: {result}")
        return True
        
    except Exception as e:
        logger.error(f"❌ API Error: {e}")
        return False

async def test_all_providers():
    """Test all configured providers"""
    logger.info("\n=== Testing All AI Providers ===")
    
    api_key = os.getenv('OPENROUTER_API_KEY', '')
    if not api_key or api_key == 'your_openrouter_api_key_here':
        logger.error("❌ No valid API key configured")
        return False
    
    providers = [
        ("DeepSeek V3.1", "deepseek/deepseek-chat-v3.1:free"),
        ("GLM 4.5 Air", "z-ai/glm-4.5-air:free"),
        ("Grok 4 Fast", "x-ai/grok-4-fast:free"),
        ("Kimi K2", "moonshotai/kimi-k2:free"),
        ("Qwen3 Coder", "qwen/qwen3-coder:free"),
        ("GPT OSS 120B", "openai/gpt-oss-120b:free")
    ]
    
    client = AsyncOpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )
    
    results = {}
    for name, model in providers:
        try:
            logger.info(f"Testing {name}...")
            response = await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "Say 'Working!'"}],
                max_tokens=10
            )
            results[name] = "✓ Working"
            logger.info(f"  ✓ {name} is working!")
        except Exception as e:
            results[name] = f"✗ Error: {str(e)[:50]}..."
            logger.error(f"  ✗ {name} failed: {e}")
    
    # Summary
    working = sum(1 for r in results.values() if r.startswith("✓"))
    logger.info(f"\nSummary: {working}/{len(providers)} providers working")
    
    return working > 0

async def create_simple_agent_test():
    """Create a simple agent test using working AI"""
    logger.info("\n=== Simple Agent Test ===")
    
    api_key = os.getenv('OPENROUTER_API_KEY', '')
    if not api_key or api_key == 'your_openrouter_api_key_here':
        logger.error("❌ No API key configured")
        return False
    
    try:
        client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        
        # Simulate a simple agent task
        agent_prompt = """You are an OSINT (Open Source Intelligence) agent.
        Task: Analyze the following information and provide a brief intelligence summary.
        
        Information: "Recent reports indicate increased cyber activity targeting financial institutions."
        
        Provide a 2-3 sentence intelligence assessment."""
        
        logger.info("Running OSINT agent task...")
        response = await client.chat.completions.create(
            model="deepseek/deepseek-chat-v3.1:free",
            messages=[{"role": "system", "content": "You are an intelligence analyst."},
                     {"role": "user", "content": agent_prompt}],
            max_tokens=150
        )
        
        result = response.choices[0].message.content
        logger.info(f"✓ Agent Response:\n{result}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Agent test failed: {e}")
        return False

async def main():
    """Main test function"""
    logger.info("AMAS Simple Authentication Test")
    logger.info("=" * 50)
    
    # Test basic authentication
    auth_ok = await test_openrouter_auth()
    
    if auth_ok:
        # Test all providers
        providers_ok = await test_all_providers()
        
        # Test simple agent
        agent_ok = await create_simple_agent_test()
        
        # Summary
        logger.info("\n" + "=" * 50)
        logger.info("Test Summary:")
        logger.info(f"  Authentication: ✓ PASS")
        logger.info(f"  Providers Test: {'✓ PASS' if providers_ok else '✗ FAIL'}")
        logger.info(f"  Agent Test: {'✓ PASS' if agent_ok else '✗ FAIL'}")
        
        if providers_ok and agent_ok:
            logger.info("\n✓ All tests passed! You can now proceed with creating a proper PR.")
            logger.info("\nNext steps:")
            logger.info("1. Update the multi-agent orchestrator with working API keys")
            logger.info("2. Run a successful analysis")
            logger.info("3. Create a PR with actual improvements")
            return 0
    else:
        logger.error("\n❌ Authentication failed. Please configure your API key first.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)