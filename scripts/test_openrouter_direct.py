#!/usr/bin/env python3
"""
Direct test of OpenRouter API with the existing keys
"""

import os
import asyncio
from openai import AsyncOpenAI
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_openrouter():
    """Test OpenRouter directly with the keys from .env"""
    
    # Load the keys - they appear to be OpenRouter keys based on the sk-or-v1- prefix
    deepseek_key = os.getenv('DEEPSEEK_API_KEY', '').strip()
    glm_key = os.getenv('GLM_API_KEY', '').strip()
    grok_key = os.getenv('GROK_API_KEY', '').strip()
    
    print("Testing OpenRouter API Keys...")
    print("=" * 60)
    
    # Test configurations
    test_configs = [
        {
            'name': 'DeepSeek via OpenRouter',
            'api_key': deepseek_key,
            'model': 'deepseek/deepseek-chat'
        },
        {
            'name': 'GLM via OpenRouter',
            'api_key': glm_key,
            'model': 'glm/glm-4'
        },
        {
            'name': 'GPT-3.5 via OpenRouter',
            'api_key': deepseek_key,  # Try with first key
            'model': 'openai/gpt-3.5-turbo'
        },
        {
            'name': 'Claude via OpenRouter',
            'api_key': deepseek_key,
            'model': 'anthropic/claude-3-haiku-20240307'
        }
    ]
    
    working_configs = []
    
    for config in test_configs:
        if not config['api_key'] or not config['api_key'].startswith('sk-or-v1-'):
            print(f"\n❌ {config['name']}: Invalid or missing OpenRouter key")
            continue
            
        print(f"\nTesting {config['name']}...")
        
        try:
            client = AsyncOpenAI(
                api_key=config['api_key'],
                base_url="https://openrouter.ai/api/v1",
            )
            
            response = await client.chat.completions.create(
                model=config['model'],
                messages=[
                    {"role": "user", "content": "Say 'Hello AMAS' if you can hear me."}
                ],
                max_tokens=20,
                extra_headers={
                    "HTTP-Referer": "https://github.com/over7-maker/AMAS",
                    "X-Title": "AMAS Test"
                }
            )
            
            result = response.choices[0].message.content
            print(f"✅ Success! Response: {result}")
            working_configs.append(config)
            
        except Exception as e:
            print(f"❌ Failed: {str(e)}")
    
    print("\n" + "=" * 60)
    print(f"Summary: {len(working_configs)}/{len(test_configs)} configurations working")
    
    if working_configs:
        print("\nWorking configurations:")
        for config in working_configs:
            print(f"  - {config['name']}")
        
        print("\n✅ OpenRouter integration is functional!")
        print("The system can use these models through the unified router.")
    else:
        print("\n❌ No working configurations found.")
        print("\nPossible issues:")
        print("1. API keys might be invalid or expired")
        print("2. OpenRouter account might need credits")
        print("3. Network connectivity issues")
        
    return len(working_configs) > 0


async def test_unified_approach():
    """Test a unified approach using OpenRouter for multiple models"""
    
    print("\n\n" + "=" * 60)
    print("Testing Unified Multi-Model Approach")
    print("=" * 60)
    
    # Use the first available key
    api_key = os.getenv('DEEPSEEK_API_KEY', '').strip()
    
    if not api_key or not api_key.startswith('sk-or-v1-'):
        print("❌ No valid OpenRouter key found")
        return
    
    client = AsyncOpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
    )
    
    # Define agent scenarios with different models
    agent_scenarios = [
        {
            'agent': 'Code Analyst',
            'model': 'openai/gpt-3.5-turbo',
            'prompt': 'Analyze this code snippet: def hello(): print("world")'
        },
        {
            'agent': 'Security Expert',
            'model': 'deepseek/deepseek-chat',
            'prompt': 'What are common web security vulnerabilities?'
        },
        {
            'agent': 'Documentation Specialist',
            'model': 'anthropic/claude-3-haiku-20240307',
            'prompt': 'Write a brief API documentation template'
        }
    ]
    
    print("\nSimulating multi-agent coordination through OpenRouter:\n")
    
    for scenario in agent_scenarios:
        print(f"{scenario['agent']} (using {scenario['model']}):")
        print(f"Task: {scenario['prompt'][:50]}...")
        
        try:
            response = await client.chat.completions.create(
                model=scenario['model'],
                messages=[
                    {"role": "system", "content": f"You are a {scenario['agent']}."},
                    {"role": "user", "content": scenario['prompt']}
                ],
                max_tokens=100,
                extra_headers={
                    "HTTP-Referer": "https://github.com/over7-maker/AMAS",
                    "X-Title": f"AMAS - {scenario['agent']}"
                }
            )
            
            result = response.choices[0].message.content[:200] + "..."
            print(f"✅ Response: {result}\n")
            
        except Exception as e:
            print(f"❌ Failed: {str(e)}\n")


async def main():
    """Run all tests"""
    print("\n🤖 AMAS OpenRouter Integration Test\n")
    
    # First test basic connectivity
    openrouter_works = await test_openrouter()
    
    # If basic test works, try unified approach
    if openrouter_works:
        await test_unified_approach()
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)


if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    asyncio.run(main())