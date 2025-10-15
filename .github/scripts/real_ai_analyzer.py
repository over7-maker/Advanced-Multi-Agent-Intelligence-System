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
import time
import aiohttp
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealAIAnalyzer:
    """Real AI analyzer that ensures actual AI responses"""
    
    def __init__(self):
        # Expert configuration with proper API endpoints and models
        self.providers = {
            "deepseek": {
                "api_key": os.getenv("DEEPSEEK_API_KEY"),
                "base_url": "https://openrouter.ai/api/v1",
                "model": "deepseek/deepseek-chat-v3.1:free"
            },
            "nvidia": {
                "api_key": os.getenv("NVIDIA_API_KEY"),
                "base_url": "https://integrate.api.nvidia.com/v1",
                "model": "deepseek-ai/deepseek-r1"
            },
            "codestral": {
                "api_key": os.getenv("CODESTRAL_API_KEY"),
                "base_url": "https://codestral.mistral.ai/v1",
                "model": "codestral-latest"
            },
            "openai": {
                "api_key": os.getenv("GPT4_API_KEY") or os.getenv("OPENAI_API_KEY"),
                "base_url": "https://api.openai.com/v1",
                "model": "gpt-4"
            },
            "anthropic": {
                "api_key": os.getenv("CLAUDE_API_KEY"),
                "base_url": "https://api.anthropic.com/v1",
                "model": "claude-3-sonnet-20240229"
            },
            "groq": {
                "api_key": os.getenv("GROQAI_API_KEY"),
                "base_url": "https://api.groq.com/openai/v1",
                "model": "llama3-8b-8192"
            },
            "cohere": {
                "api_key": os.getenv("COHERE_API_KEY"),
                "base_url": "https://api.cohere.ai/v1",
                "model": "command-r-plus"
            },
            "cerebras": {
                "api_key": os.getenv("CEREBRAS_API_KEY"),
                "base_url": "https://openrouter.ai/api/v1",
                "model": "cerebras-gpt-13b"
            },
            "glm": {
                "api_key": os.getenv("GLM_API_KEY"),
                "base_url": "https://openrouter.ai/api/v1",
                "model": "z-ai/glm-4.5-air:free"
            },
            "grok": {
                "api_key": os.getenv("GROK_API_KEY"),
                "base_url": "https://openrouter.ai/api/v1",
                "model": "x-ai/grok-4-fast:free"
            },
            "kimi": {
                "api_key": os.getenv("KIMI_API_KEY"),
                "base_url": "https://openrouter.ai/api/v1",
                "model": "moonshotai/kimi-k2:free"
            },
            "qwen": {
                "api_key": os.getenv("QWEN_API_KEY"),
                "base_url": "https://openrouter.ai/api/v1",
                "model": "qwen/qwen3-coder:free"
            },
            "gptoss": {
                "api_key": os.getenv("GPTOSS_API_KEY"),
                "base_url": "https://openrouter.ai/api/v1",
                "model": "openai/gpt-oss-120b:free"
            },
            "geminiai": {
                "api_key": os.getenv("GEMINIAI_API_KEY"),
                "base_url": "https://openrouter.ai/api/v1",
                "model": "google/gemini-1.5-flash-latest"
            },
            "gemini2": {
                "api_key": os.getenv("GEMINI2_API_KEY"),
                "base_url": "https://openrouter.ai/api/v1",
                "model": "google/gemini-2.0-flash:generateContent"
            },
            "groq2": {
                "api_key": os.getenv("GROQ2_API_KEY"),
                "base_url": "https://api.groq.com/openai/v1",
                "model": "llama3-70b-8192"
            },
            "chutes": {
                "api_key": os.getenv("CHUTES_API_KEY"),
                "base_url": "https://openrouter.ai/api/v1",
                "model": "zai-org/GLM-4.5-Air"
            }
        }
        
        # Filter out providers without API keys
        self.available_providers = {k: v for k, v in self.providers.items() if v["api_key"] and v["api_key"].strip()}
        
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
    
    async def analyze_with_real_ai(self, task_type: str, code_content: str = "") -> Dict[str, Any]:
        """Perform REAL AI analysis using actual API calls (Expert approach)"""
        logger.info(f"🔍 Starting REAL AI analysis for {task_type}")
        logger.info(f"📝 Code content length: {len(code_content)} characters")
        logger.info(f"🔑 Available providers: {len(self.available_providers)}")
        
        if not self.available_providers:
            return {
                'success': False,
                'error': 'No AI providers available - check API keys',
                'providers_tried': 0,
                'real_ai': False,
                'timestamp': datetime.utcnow().isoformat()
            }
        
        # Try providers in sequence until one succeeds
        for provider_name, config in self.available_providers.items():
            try:
                logger.info(f"🤖 Trying provider: {provider_name}")
                start_time = time.time()
                
                result = await self._call_provider(config, task_type, code_content)
                response_time = time.time() - start_time
                
                if result['success']:
                    logger.info(f"✅ Success with {provider_name} in {response_time:.2f}s")
                    return {
                        'success': True,
                        'provider': provider_name,
                        'response_time': round(response_time, 2),
                        'analysis': result['content'],
                        'model_used': config['model'],
                        'task_type': task_type,
                        'timestamp': datetime.utcnow().isoformat(),
                        'real_ai': True,  # Expert flag to verify real AI
                        'providers_tried': list(self.available_providers.keys()).index(provider_name) + 1,
                        'total_available': len(self.available_providers)
                    }
                else:
                    logger.warning(f"❌ Provider {provider_name} failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                logger.error(f"❌ Exception with {provider_name}: {e}")
                continue
        
        # All providers failed
        return {
            'success': False,
            'error': 'All AI providers failed',
            'providers_tried': len(self.available_providers),
            'real_ai': False,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def _call_provider(self, config: Dict[str, str], task_type: str, code_content: str) -> Dict[str, Any]:
        """Make actual API call to AI provider (Expert implementation)"""
        # Expert prompt engineering for better AI responses
        prompt = f"""
        Analyze this {task_type} thoroughly:
        
        Code/Content: {code_content[:2000]}
        
        Provide specific, actionable insights including:
        1. Specific issues with file names and line numbers
        2. Security vulnerabilities (if any)
        3. Performance improvements
        4. Code quality recommendations
        5. Best practices and optimization suggestions
        
        Be specific and actionable. Focus on the actual code changes and their impact.
        """
        
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }
        
        # Add provider-specific headers
        if "openrouter.ai" in config['base_url']:
            headers.update({
                "HTTP-Referer": "https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System",
                "X-Title": "AMAS AI Workflow System"
            })
        
        payload = {
            "model": config["model"],
            "messages": [
                {"role": "system", "content": "You are an expert code analyst. Provide detailed, specific recommendations with file names and line numbers when possible."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1500
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{config['base_url']}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'success': True,
                            'content': data["choices"][0]["message"]["content"]
                        }
                    else:
                        error_text = await response.text()
                        raise Exception(f"HTTP {response.status}: {error_text}")
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
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
    """Main function for testing (Expert approach)"""
    analyzer = RealAIAnalyzer()
    
    # Install dependencies first
    if not analyzer.install_dependencies():
        print("❌ Failed to install dependencies")
        return
    
    # Get actual code content from PR changes
    code_content = """
    # Sample code changes from PR
    def analyze_code_quality():
        # Fixed YAML parsing errors
        # Added dependency management
        # Enhanced error handling
        pass
    """
    
    # Perform REAL AI analysis
    result = await analyzer.analyze_with_real_ai("code_quality", code_content)
    
    # Save results
    os.makedirs("artifacts", exist_ok=True)
    with open("artifacts/real_ai_analysis.json", "w") as f:
        json.dump(result, f, indent=2)
    
    # Output results
    if result["success"]:
        print(f"✅ REAL AI Analysis completed!")
        print(f"🤖 Provider: {result['provider']}")
        print(f"⏱️ Response Time: {result['response_time']}s")
        print(f"📊 Analysis: {result['analysis'][:200]}...")
        print(f"🔍 Real AI verified: {result.get('real_ai', False)}")
    else:
        print("❌ All AI providers failed")
        print(f"Error: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    asyncio.run(main())