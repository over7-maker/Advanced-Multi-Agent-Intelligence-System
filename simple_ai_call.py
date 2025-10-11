#!/usr/bin/env python3
"""
Simple AI Call - Easy integration for workflows
Uses the Ultimate 16-API Fallback Manager
"""

import asyncio
import sys
from ultimate_16_api_fallback_manager import generate_ai_response, generate_ai_response_with_context

async def simple_ai_call(prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
    """
    Simple AI call with automatic fallback
    Returns the response text or error message
    """
    try:
        response = await generate_ai_response(prompt, max_tokens=max_tokens, temperature=temperature)
        return response
    except Exception as e:
        return f"Error: {str(e)}"

async def main():
    """Main function for command line usage"""
    if len(sys.argv) < 2:
        print("Usage: python3 simple_ai_call.py 'Your prompt here'")
        print("Example: python3 simple_ai_call.py 'What is the meaning of life?'")
        sys.exit(1)
    
    prompt = sys.argv[1]
    max_tokens = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
    temperature = float(sys.argv[3]) if len(sys.argv) > 3 else 0.7
    
    print(f"🤖 AI Response:")
    print("=" * 50)
    
    response = await simple_ai_call(prompt, max_tokens, temperature)
    print(response)
    
    print("\n" + "=" * 50)
    print("✅ AI call completed!")

if __name__ == "__main__":
    asyncio.run(main())