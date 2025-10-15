#!/usr/bin/env python3
"""
Real AI Analyzer - Ensures actual AI analysis instead of mock responses
This script provides real AI analysis with proper error handling and fallbacks
"""

import os
import sys
import json
import asyncio
import subprocess
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealAIAnalyzer:
    """Real AI analyzer that ensures actual AI responses"""
    
    def __init__(self):
        self.api_keys = {
            'openai': os.getenv('GPT4_API_KEY') or os.getenv('OPENAI_API_KEY'),
            'anthropic': os.getenv('CLAUDE_API_KEY'),
            'deepseek': os.getenv('DEEPSEEK_API_KEY'),
            'groq': os.getenv('GROQAI_API_KEY'),
            'cohere': os.getenv('COHERE_API_KEY'),
            'nvidia': os.getenv('NVIDIA_API_KEY'),
            'cerebras': os.getenv('CEREBRAS_API_KEY'),
            'codestral': os.getenv('CODESTRAL_API_KEY'),
            'glm': os.getenv('GLM_API_KEY'),
            'grok': os.getenv('GROK_API_KEY'),
            'kimi': os.getenv('KIMI_API_KEY'),
            'qwen': os.getenv('QWEN_API_KEY'),
            'gptoss': os.getenv('GPTOSS_API_KEY'),
            'geminiai': os.getenv('GEMINIAI_API_KEY'),
            'gemini2': os.getenv('GEMINI2_API_KEY'),
            'groq2': os.getenv('GROQ2_API_KEY'),
            'chutes': os.getenv('CHUTES_API_KEY')
        }
        
        # Filter out empty API keys
        self.available_keys = {k: v for k, v in self.api_keys.items() if v and v.strip()}
        
    def install_dependencies(self):
        """Install required dependencies for AI analysis"""
        try:
            logger.info("📦 Installing AI dependencies...")
            
            # Install core dependencies
            subprocess.run([
                sys.executable, "-m", "pip", "install", 
                "aiohttp", "openai", "cohere", "python-dotenv", "requests"
            ], check=True, capture_output=True)
            
            logger.info("✅ Dependencies installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to install dependencies: {e}")
            return False
    
    async def call_openai_api(self, prompt: str, api_key: str) -> Dict[str, Any]:
        """Call OpenAI API directly"""
        try:
            import openai
            
            client = openai.AsyncOpenAI(api_key=api_key)
            
            response = await client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.7
            )
            
            return {
                'success': True,
                'content': response.choices[0].message.content,
                'provider': 'openai',
                'model': 'gpt-4'
            }
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def call_anthropic_api(self, prompt: str, api_key: str) -> Dict[str, Any]:
        """Call Anthropic API directly"""
        try:
            import anthropic
            
            client = anthropic.AsyncAnthropic(api_key=api_key)
            
            response = await client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return {
                'success': True,
                'content': response.content[0].text,
                'provider': 'anthropic',
                'model': 'claude-3-sonnet'
            }
            
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def call_groq_api(self, prompt: str, api_key: str) -> Dict[str, Any]:
        """Call Groq API directly"""
        try:
            import openai
            
            client = openai.AsyncOpenAI(
                api_key=api_key,
                base_url="https://api.groq.com/openai/v1"
            )
            
            response = await client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.7
            )
            
            return {
                'success': True,
                'content': response.choices[0].message.content,
                'provider': 'groq',
                'model': 'llama3-8b-8192'
            }
            
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def call_cohere_api(self, prompt: str, api_key: str) -> Dict[str, Any]:
        """Call Cohere API directly"""
        try:
            import cohere
            
            client = cohere.AsyncClient(api_key=api_key)
            
            response = await client.chat(
                model="command-r-plus",
                message=prompt,
                max_tokens=2000,
                temperature=0.7
            )
            
            return {
                'success': True,
                'content': response.text,
                'provider': 'cohere',
                'model': 'command-r-plus'
            }
            
        except Exception as e:
            logger.error(f"Cohere API error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def analyze_with_real_ai(self, prompt: str, task_type: str = "analysis") -> Dict[str, Any]:
        """Perform real AI analysis using available providers"""
        logger.info(f"🚀 Starting REAL AI analysis for {task_type}")
        logger.info(f"📝 Prompt length: {len(prompt)} characters")
        logger.info(f"🔑 Available API keys: {len(self.available_keys)}")
        
        if not self.available_keys:
            return {
                'success': False,
                'error': 'No API keys available - check environment variables',
                'providers_tried': 0,
                'timestamp': datetime.utcnow().isoformat()
            }
        
        # Try each available provider
        for provider, api_key in self.available_keys.items():
            try:
                logger.info(f"🤖 Trying {provider}...")
                start_time = datetime.now()
                
                if provider == 'openai':
                    result = await self.call_openai_api(prompt, api_key)
                elif provider == 'anthropic':
                    result = await self.call_anthropic_api(prompt, api_key)
                elif provider in ['groq', 'groq2']:
                    result = await self.call_groq_api(prompt, api_key)
                elif provider == 'cohere':
                    result = await self.call_cohere_api(prompt, api_key)
                else:
                    # For other providers, try a generic approach
                    result = await self.call_generic_api(prompt, api_key, provider)
                
                if result['success']:
                    response_time = (datetime.now() - start_time).total_seconds()
                    logger.info(f"✅ Success with {provider} in {response_time:.2f}s")
                    
                    return {
                        'success': True,
                        'content': result['content'],
                        'provider_used': result['provider'],
                        'model_used': result['model'],
                        'response_time': response_time,
                        'task_type': task_type,
                        'timestamp': datetime.utcnow().isoformat(),
                        'providers_tried': list(self.available_keys.keys()).index(provider) + 1,
                        'total_available': len(self.available_keys)
                    }
                else:
                    logger.warning(f"❌ {provider} failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                logger.error(f"❌ Exception with {provider}: {e}")
                continue
        
        # All providers failed
        return {
            'success': False,
            'error': 'All AI providers failed',
            'providers_tried': len(self.available_keys),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def call_generic_api(self, prompt: str, api_key: str, provider: str) -> Dict[str, Any]:
        """Generic API call for other providers"""
        try:
            import aiohttp
            
            # Use OpenRouter as a generic endpoint for many providers
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System",
                "X-Title": "AMAS AI Workflow System"
            }
            
            # Map provider to model
            model_map = {
                'deepseek': 'deepseek/deepseek-chat-v3.1:free',
                'nvidia': 'meta/llama3-70b-instruct',
                'cerebras': 'cerebras-gpt-13b',
                'codestral': 'codestral-latest',
                'glm': 'z-ai/glm-4.5-air:free',
                'grok': 'x-ai/grok-4-fast:free',
                'kimi': 'moonshotai/kimi-k2:free',
                'qwen': 'qwen/qwen3-coder:free',
                'gptoss': 'openai/gpt-oss-120b:free',
                'geminiai': 'google/gemini-1.5-flash-latest',
                'gemini2': 'google/gemini-2.0-flash:generateContent',
                'chutes': 'zai-org/GLM-4.5-Air'
            }
            
            model = model_map.get(provider, 'openai/gpt-4')
            
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload, timeout=30) as response:
                    response.raise_for_status()
                    data = await response.json()
                    
                    return {
                        'success': True,
                        'content': data['choices'][0]['message']['content'],
                        'provider': provider,
                        'model': model
                    }
                    
        except Exception as e:
            return {'success': False, 'error': str(e)}

async def main():
    """Main function for testing"""
    analyzer = RealAIAnalyzer()
    
    # Install dependencies first
    if not analyzer.install_dependencies():
        print("❌ Failed to install dependencies")
        return
    
    # Test with a real prompt
    test_prompt = """
    Analyze this pull request for code quality, security issues, and potential improvements:
    
    The PR contains changes to fix YAML syntax errors and dependency issues in GitHub Actions workflows.
    Key changes include:
    - Fixed YAML parsing errors in custom actions
    - Added missing Python dependencies (aiohttp, multidict, yarl, etc.)
    - Enhanced AI output processing to handle truncation
    - Improved error handling and fallback mechanisms
    
    Please provide a detailed analysis with specific recommendations.
    """
    
    result = await analyzer.analyze_with_real_ai(test_prompt, "pr_analysis")
    
    if result['success']:
        print(f"✅ Real AI analysis successful!")
        print(f"🤖 Provider: {result['provider_used']}")
        print(f"⏱️ Response time: {result['response_time']:.2f}s")
        print(f"📊 Providers tried: {result['providers_tried']}/{result['total_available']}")
        print(f"\n📝 Analysis:\n{result['content']}")
    else:
        print(f"❌ Real AI analysis failed: {result['error']}")

if __name__ == "__main__":
    asyncio.run(main())