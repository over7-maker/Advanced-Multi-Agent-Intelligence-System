#!/usr/bin/env python3
"""
Debug Responder - Debug script for AI issue responder
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def debug_environment():
    """Debug environment variables and configuration"""
    print("🔍 DEBUGGING AI ISSUE RESPONDER ENVIRONMENT")
    print("="*60)
    
    # Check environment variables
    env_vars = [
        'GITHUB_TOKEN',
        'GITHUB_REPOSITORY',
        'ISSUE_NUMBER',
        'ISSUE_TITLE',
        'ISSUE_BODY',
        'ISSUE_ACTION',
        'ISSUE_AUTHOR'
    ]
    
    print("📋 Environment Variables:")
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # Truncate long values for security
            display_value = value[:50] + "..." if len(value) > 50 else value
            print(f"  ✅ {var}: {display_value}")
        else:
            print(f"  ❌ {var}: Not set")
    
    # Check API keys
    api_keys = [
        'DEEPSEEK_API_KEY',
        'GLM_API_KEY',
        'GROK_API_KEY',
        'KIMI_API_KEY',
        'QWEN_API_KEY',
        'GPTOSS_API_KEY',
        'GROQAI_API_KEY',
        'CEREBRAS_API_KEY',
        'GEMINIAI_API_KEY'
    ]
    
    print("\n🔑 API Keys Status:")
    active_keys = 0
    for key in api_keys:
        value = os.getenv(key)
        if value and value.strip():
            active_keys += 1
            print(f"  ✅ {key}: Available")
        else:
            print(f"  ❌ {key}: Not available")
    
    print(f"\n📊 Summary: {active_keys}/9 API keys available")
    
    # Check Python environment
    print("\n🐍 Python Environment:")
    print(f"  Python Version: {sys.version}")
    print(f"  Python Path: {sys.executable}")
    
    # Check if required modules are available
    print("\n📦 Required Modules:")
    modules = ['openai', 'aiohttp', 'requests', 'PyGithub']
    for module in modules:
        try:
            __import__(module)
            print(f"  ✅ {module}: Available")
        except ImportError:
            print(f"  ❌ {module}: Not available")
    
    print("\n✅ Debug completed successfully!")

if __name__ == "__main__":
    debug_environment()