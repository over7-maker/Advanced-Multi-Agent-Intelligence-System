#!/usr/bin/env python3
"""
Production-ready AI Agent Fallback System for AMAS
Uses 16 AI providers with intelligent fallback and health monitoring
Based on expert-level implementation with correct API endpoints
"""

import os
import asyncio
import logging
import json
import time
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime

import aiohttp
from openai import AsyncOpenAI, OpenAIError
import cohere

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class AIAgentFallback:
    """Production-ready AI agent with 16-provider fallback system"""
    
    def __init__(self):
        self.providers = self._initialize_providers()
        self.circuit_breakers = {name: False for name in self.providers.keys()}
        self.health_scores = {name: 100 for name in self.providers.keys()}
        self.response_times = {name: [] for name in self.providers.keys()}
        self.success_counts = {name: 0 for name in self.providers.keys()}
        self.failure_counts = {name: 0 for name in self.providers.keys()}
        
    def _initialize_providers(self) -> Dict[str, Dict[str, Any]]:
        """Initialize all 16 AI providers with correct configurations matching your API keys"""
        return {
            'deepseek': {
                'api_key': os.getenv('DEEPSEEK_API_KEY'),
                'base_url': 'https://openrouter.ai/api/v1',
                'model': 'deepseek/deepseek-chat-v3.1:free',
                'priority': 1,
                'type': 'openrouter',
                'handler': self._handle_openrouter
            },
            'glm': {
                'api_key': os.getenv('GLM_API_KEY'),
                'base_url': 'https://openrouter.ai/api/v1',
                'model': 'z-ai/glm-4.5-air:free',
                'priority': 2,
                'type': 'openrouter',
                'handler': self._handle_openrouter
            },
            'grok': {
                'api_key': os.getenv('GROK_API_KEY'),
                'base_url': 'https://openrouter.ai/api/v1',
                'model': 'x-ai/grok-4-fast:free',
                'priority': 3,
                'type': 'openrouter',
                'handler': self._handle_openrouter
            },
            'kimi': {
                'api_key': os.getenv('KIMI_API_KEY'),
                'base_url': 'https://openrouter.ai/api/v1',
                'model': 'moonshotai/kimi-k2:free',
                'priority': 4,
                'type': 'openrouter',
                'handler': self._handle_openrouter
            },
            'qwen': {
                'api_key': os.getenv('QWEN_API_KEY'),
                'base_url': 'https://openrouter.ai/api/v1',
                'model': 'qwen/qwen3-coder:free',
                'priority': 5,
                'type': 'openrouter',
                'handler': self._handle_openrouter
            },
            'gptoss': {
                'api_key': os.getenv('GPTOSS_API_KEY'),
                'base_url': 'https://openrouter.ai/api/v1',
                'model': 'openai/gpt-oss-120b:free',
                'priority': 6,
                'type': 'openrouter',
                'handler': self._handle_openrouter
            },
            'groqai': {
                'api_key': os.getenv('GROQAI_API_KEY'),
                'base_url': 'https://api.groq.com/openai/v1',
                'model': 'llama3-8b-8192',
                'priority': 7,
                'type': 'openai_compatible',
                'handler': self._handle_openai_compatible
            },
            'cerebras': {
                'api_key': os.getenv('CEREBRAS_API_KEY'),
                'base_url': 'https://api.cerebras.ai/v1',
                'model': 'cerebras-gpt-13b',
                'priority': 8,
                'type': 'openai_compatible',
                'handler': self._handle_openai_compatible
            },
            'cohere': {
                'api_key': os.getenv('COHERE_API_KEY'),
                'base_url': 'https://api.cohere.ai/v1',
                'model': 'command-r-plus',
                'priority': 9,
                'type': 'cohere',
                'handler': self._handle_cohere
            },
            'nvidia': {
                'api_key': os.getenv('NVIDIA_API_KEY'),
                'base_url': 'https://integrate.api.nvidia.com/v1',
                'model': 'meta/llama3-70b-instruct',
                'priority': 10,
                'type': 'openai_compatible',
                'handler': self._handle_openai_compatible
            },
            'codestral': {
                'api_key': os.getenv('CODESTRAL_API_KEY'),
                'base_url': 'https://codestral.mistral.ai/v1',
                'model': 'codestral-latest',
                'priority': 11,
                'type': 'openai_compatible',
                'handler': self._handle_openai_compatible
            },
            'geminiai': {
                'api_key': os.getenv('GEMINIAI_API_KEY'),
                'base_url': 'https://generativelanguage.googleapis.com/v1beta',
                'model': 'gemini-1.5-flash-latest',
                'priority': 12,
                'type': 'gemini',
                'handler': self._handle_gemini
            },
            'gemini2': {
                'api_key': os.getenv('GEMINI2_API_KEY'),
                'base_url': 'https://generativelanguage.googleapis.com/v1beta',
                'model': 'gemini-2.0-flash:generateContent',
                'priority': 13,
                'type': 'gemini',
                'handler': self._handle_gemini
            },
            'groq2': {
                'api_key': os.getenv('GROQ2_API_KEY'),
                'base_url': 'https://api.groq.com/openai/v1',
                'model': 'llama3-70b-8192',
                'priority': 14,
                'type': 'openai_compatible',
                'handler': self._handle_openai_compatible
            },
            'chutes': {
                'api_key': os.getenv('CHUTES_API_KEY'),
                'base_url': 'https://llm.chutes.ai/v1',
                'model': 'zai-org/GLM-4.5-Air',
                'priority': 15,
                'type': 'chutes',
                'handler': self._handle_chutes
            }
        }
    
    def _get_available_providers(self) -> List[str]:
        """Get list of available providers sorted by priority"""
        available = []
        for name, config in self.providers.items():
            if config['api_key'] and config['api_key'].strip():
                available.append(name)
        
        # Sort by priority
        available.sort(key=lambda x: self.providers[x]['priority'])
        return available
    
    async def _handle_openrouter(self, provider_name: str, prompt: str) -> Dict[str, Any]:
        """Handle OpenRouter API calls"""
        config = self.providers[provider_name]
        
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System",
            "X-Title": "AMAS AI Workflow System"
        }
        
        payload = {
            "model": config['model'],
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{config['base_url']}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return {
                    'success': True,
                    'content': data['choices'][0]['message']['content'],
                    'provider': provider_name,
                    'model': config['model']
                }
    
    async def _handle_openai_compatible(self, provider_name: str, prompt: str) -> Dict[str, Any]:
        """Handle OpenAI-compatible API calls"""
        config = self.providers[provider_name]
        
        try:
            client = AsyncOpenAI(
                api_key=config['api_key'],
                base_url=config['base_url']
            )
            
            response = await client.chat.completions.create(
                model=config['model'],
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2000,
                timeout=30
            )
            
            return {
                'success': True,
                'content': response.choices[0].message.content,
                'provider': provider_name,
                'model': config['model']
            }
        except Exception as e:
            raise Exception(f"OpenAI-compatible API error: {str(e)}")
    
    async def _handle_cohere(self, provider_name: str, prompt: str) -> Dict[str, Any]:
        """Handle Cohere API calls"""
        config = self.providers[provider_name]
        
        try:
            client = cohere.AsyncClient(api_key=config['api_key'])
            response = await client.chat(
                model=config['model'],
                message=prompt,
                temperature=0.7,
                max_tokens=2000
            )
            
            return {
                'success': True,
                'content': response.text,
                'provider': provider_name,
                'model': config['model']
            }
        except Exception as e:
            raise Exception(f"Cohere API error: {str(e)}")
    
    async def _handle_gemini(self, provider_name: str, prompt: str) -> Dict[str, Any]:
        """Handle Google Gemini API calls"""
        config = self.providers[provider_name]
        
        url = f"{config['base_url']}/models/{config['model']}:generateContent?key={config['api_key']}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=30) as response:
                response.raise_for_status()
                data = await response.json()
                return {
                    'success': True,
                    'content': data['candidates'][0]['content']['parts'][0]['text'],
                    'provider': provider_name,
                    'model': config['model']
                }
    
    async def _handle_chutes(self, provider_name: str, prompt: str) -> Dict[str, Any]:
        """Handle Chutes API calls"""
        config = self.providers[provider_name]
        
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": config['model'],
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "max_tokens": 2000,
            "temperature": 0.7
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{config['base_url']}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return {
                    'success': True,
                    'content': data['choices'][0]['message']['content'],
                    'provider': provider_name,
                    'model': config['model']
                }
    
    def _update_health_scores(self, provider_name: str, success: bool, response_time: float):
        """Update provider health scores based on performance"""
        if success:
            self.success_counts[provider_name] += 1
            self.health_scores[provider_name] = min(100, self.health_scores[provider_name] + 5)
            self.circuit_breakers[provider_name] = False
        else:
            self.failure_counts[provider_name] += 1
            self.health_scores[provider_name] = max(0, self.health_scores[provider_name] - 10)
            
            # Circuit breaker: if too many failures, temporarily disable
            if self.failure_counts[provider_name] > 3:
                self.circuit_breakers[provider_name] = True
                logger.warning(f"Circuit breaker activated for {provider_name}")
        
        # Update response time tracking
        self.response_times[provider_name].append(response_time)
        if len(self.response_times[provider_name]) > 10:
            self.response_times[provider_name].pop(0)
    
    async def analyze_with_fallback(self, prompt: str, task_type: str = "analysis") -> Dict[str, Any]:
        """Main method to get AI analysis with intelligent fallback"""
        logger.info(f"🚀 Starting AI analysis with fallback system")
        logger.info(f"📋 Task type: {task_type}")
        logger.info(f"📝 Prompt length: {len(prompt)} characters")
        
        available_providers = self._get_available_providers()
        logger.info(f"🔍 Available providers: {len(available_providers)}")
        
        if not available_providers:
            return {
                'success': False,
                'error': 'No AI providers available - check API keys',
                'providers_tried': 0,
                'timestamp': datetime.utcnow().isoformat()
            }
        
        # Try providers in priority order
        for provider_name in available_providers:
            if self.circuit_breakers[provider_name]:
                logger.warning(f"⏸️ Skipping {provider_name} - circuit breaker active")
                continue
            
            logger.info(f"🤖 Attempting analysis with {provider_name}...")
            start_time = time.time()
            
            try:
                config = self.providers[provider_name]
                handler = config['handler']
                
                result = await handler(provider_name, prompt)
                response_time = time.time() - start_time
                
                # Update health scores
                self._update_health_scores(provider_name, True, response_time)
                
                logger.info(f"✅ Success with {provider_name} in {response_time:.2f}s")
                
                return {
                    'success': True,
                    'content': result['content'],
                    'provider_used': provider_name,
                    'model_used': result['model'],
                    'response_time': response_time,
                    'task_type': task_type,
                    'timestamp': datetime.utcnow().isoformat(),
                    'providers_tried': available_providers.index(provider_name) + 1,
                    'total_available': len(available_providers)
                }
                
            except Exception as e:
                response_time = time.time() - start_time
                self._update_health_scores(provider_name, False, response_time)
                
                logger.error(f"❌ Failed with {provider_name}: {str(e)}")
                continue
        
        # All providers failed
        return {
            'success': False,
            'error': 'All AI providers failed',
            'providers_tried': len(available_providers),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        available_providers = self._get_available_providers()
        
        return {
            'total_providers': len(self.providers),
            'available_providers': len(available_providers),
            'provider_status': {
                name: {
                    'available': name in available_providers,
                    'health_score': self.health_scores[name],
                    'circuit_breaker': self.circuit_breakers[name],
                    'success_count': self.success_counts[name],
                    'failure_count': self.failure_counts[name],
                    'avg_response_time': sum(self.response_times[name]) / len(self.response_times[name]) if self.response_times[name] else 0
                }
                for name in self.providers.keys()
            },
            'timestamp': datetime.utcnow().isoformat()
        }

# Global instance
ai_agent = AIAgentFallback()

async def main():
    """Test the AI agent fallback system"""
    print("🚀 Testing AI Agent Fallback System")
    print("=" * 50)
    
    # Test prompt
    test_prompt = """
    Analyze this code for potential improvements:
    
    def calculate_total(items):
        total = 0
        for item in items:
            total += item.price
        return total
    
    Provide specific recommendations for optimization.
    """
    
    try:
        result = await ai_agent.analyze_with_fallback(test_prompt, "code_analysis")
        
        if result['success']:
            print(f"✅ Analysis successful!")
            print(f"🤖 Provider: {result['provider_used']}")
            print(f"⏱️ Response time: {result['response_time']:.2f}s")
            print(f"📊 Providers tried: {result['providers_tried']}/{result['total_available']}")
            print(f"\n📝 Analysis:\n{result['content']}")
        else:
            print(f"❌ Analysis failed: {result['error']}")
        
        # Show system status
        status = ai_agent.get_system_status()
        print(f"\n📊 System Status:")
        print(f"Available providers: {status['available_providers']}/{status['total_providers']}")
        
    except Exception as e:
        print(f"❌ System error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())