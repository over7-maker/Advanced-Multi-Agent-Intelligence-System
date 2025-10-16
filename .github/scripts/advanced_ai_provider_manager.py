#!/usr/bin/env python3
"""
Advanced AI Provider Manager - 16 Provider Failover System
Comprehensive AI integration with intelligent fallback
"""

import os
import sys
import json
import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, List, Optional, Any
from openai import OpenAI
import cohere

class AdvancedAIProviderManager:
    def __init__(self):
        """Initialize with all 16 AI providers"""
        self.providers = {
            # OpenRouter-based providers
            'deepseek': {
                'api_key': os.getenv('DEEPSEEK_API_KEY'),
                'base_url': 'https://openrouter.ai/api/v1',
                'model': 'deepseek/deepseek-chat-v3.1:free',
                'priority': 1,
                'type': 'openrouter'
            },
            'glm': {
                'api_key': os.getenv('GLM_API_KEY'),
                'base_url': 'https://openrouter.ai/api/v1',
                'model': 'z-ai/glm-4.5-air:free',
                'priority': 2,
                'type': 'openrouter'
            },
            'grok': {
                'api_key': os.getenv('GROK_API_KEY'),
                'base_url': 'https://openrouter.ai/api/v1',
                'model': 'x-ai/grok-4-fast:free',
                'priority': 3,
                'type': 'openrouter'
            },
            'kimi': {
                'api_key': os.getenv('KIMI_API_KEY'),
                'base_url': 'https://openrouter.ai/api/v1',
                'model': 'moonshotai/kimi-k2:free',
                'priority': 4,
                'type': 'openrouter'
            },
            'qwen': {
                'api_key': os.getenv('QWEN_API_KEY'),
                'base_url': 'https://openrouter.ai/api/v1',
                'model': 'qwen/qwen3-coder:free',
                'priority': 5,
                'type': 'openrouter'
            },
            'gptoss': {
                'api_key': os.getenv('GPTOSS_API_KEY'),
                'base_url': 'https://openrouter.ai/api/v1',
                'model': 'openai/gpt-oss-120b:free',
                'priority': 6,
                'type': 'openrouter'
            },
            
            # Direct API providers
            'nvidia': {
                'api_key': os.getenv('NVIDIA_API_KEY'),
                'base_url': 'https://integrate.api.nvidia.com/v1',
                'model': 'deepseek-ai/deepseek-r1',
                'priority': 7,
                'type': 'nvidia'
            },
            'codestral': {
                'api_key': os.getenv('CODESTRAL_API_KEY'),
                'base_url': 'https://codestral.mistral.ai/v1',
                'model': 'codestral-latest',
                'priority': 8,
                'type': 'mistral'
            },
            'cerebras': {
                'api_key': os.getenv('CEREBRAS_API_KEY'),
                'base_url': 'https://api.cerebras.ai/v1',
                'model': 'qwen-3-235b-a22b-instruct-2507',
                'priority': 9,
                'type': 'cerebras'
            },
            'cohere': {
                'api_key': os.getenv('COHERE_API_KEY'),
                'base_url': 'https://api.cohere.ai/v1',
                'model': 'command-a-03-2025',
                'priority': 10,
                'type': 'cohere'
            },
            'chutes': {
                'api_key': os.getenv('CHUTES_API_KEY'),
                'base_url': 'https://llm.chutes.ai/v1',
                'model': 'zai-org/GLM-4.5-Air',
                'priority': 11,
                'type': 'chutes'
            },
            'gemini2': {
                'api_key': os.getenv('GEMINI2_API_KEY'),
                'base_url': 'https://generativelanguage.googleapis.com/v1beta',
                'model': 'gemini-2.0-flash',
                'priority': 12,
                'type': 'gemini'
            },
            'groq2': {
                'api_key': os.getenv('GROQ2_API_KEY'),
                'base_url': 'https://api.groq.com/openai/v1',
                'model': 'llama-3.1-70b-versatile',
                'priority': 13,
                'type': 'groq'
            },
            'geminiai': {
                'api_key': os.getenv('GEMINIAI_API_KEY'),
                'base_url': 'https://generativelanguage.googleapis.com/v1beta',
                'model': 'gemini-1.5-pro',
                'priority': 14,
                'type': 'gemini'
            },
            'groqai': {
                'api_key': os.getenv('GROQAI_API_KEY'),
                'base_url': 'https://api.groq.com/openai/v1',
                'model': 'llama-3.1-8b-instant',
                'priority': 15,
                'type': 'groq'
            },
            'claude': {
                'api_key': os.getenv('CLAUDE_API_KEY'),
                'base_url': 'https://api.anthropic.com/v1',
                'model': 'claude-3.5-sonnet-20241022',
                'priority': 16,
                'type': 'anthropic'
            }
        }
        
        # Filter out providers without API keys
        self.available_providers = {
            name: config for name, config in self.providers.items() 
            if config['api_key'] and config['api_key'].strip()
        }
        
        # Sort by priority
        self.available_providers = dict(sorted(
            self.available_providers.items(), 
            key=lambda x: x[1]['priority']
        ))
        
        print(f"✅ AI Provider Manager initialized with {len(self.available_providers)} providers")
        for name, config in self.available_providers.items():
            print(f"  - {name}: {config['model']} (Priority {config['priority']})")
    
    async def analyze_with_provider(self, provider_name: str, prompt: str, context: Dict = None) -> Dict:
        """Analyze with specific provider"""
        if provider_name not in self.available_providers:
            raise ValueError(f"Provider {provider_name} not available")
        
        config = self.available_providers[provider_name]
        
        try:
            if config['type'] == 'openrouter':
                return await self._call_openrouter(config, prompt, context)
            elif config['type'] == 'nvidia':
                return await self._call_nvidia(config, prompt, context)
            elif config['type'] == 'mistral':
                return await self._call_mistral(config, prompt, context)
            elif config['type'] == 'cerebras':
                return await self._call_cerebras(config, prompt, context)
            elif config['type'] == 'cohere':
                return await self._call_cohere(config, prompt, context)
            elif config['type'] == 'chutes':
                return await self._call_chutes(config, prompt, context)
            elif config['type'] == 'gemini':
                return await self._call_gemini(config, prompt, context)
            elif config['type'] == 'groq':
                return await self._call_groq(config, prompt, context)
            elif config['type'] == 'anthropic':
                return await self._call_anthropic(config, prompt, context)
            else:
                raise ValueError(f"Unknown provider type: {config['type']}")
                
        except Exception as e:
            return {
                'success': False,
                'provider': provider_name,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def _call_openrouter(self, config: Dict, prompt: str, context: Dict = None) -> Dict:
        """Call OpenRouter-based providers"""
        client = OpenAI(
            base_url=config['base_url'],
            api_key=config['api_key']
        )
        
        messages = [
            {"role": "system", "content": "You are an expert AI assistant providing detailed, actionable analysis."},
            {"role": "user", "content": prompt}
        ]
        
        response = client.chat.completions.create(
            model=config['model'],
            messages=messages,
            temperature=0.7,
            max_tokens=2000
        )
        
        return {
            'success': True,
            'provider': config['model'],
            'response': response.choices[0].message.content,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def _call_nvidia(self, config: Dict, prompt: str, context: Dict = None) -> Dict:
        """Call NVIDIA API"""
        client = OpenAI(
            base_url=config['base_url'],
            api_key=config['api_key']
        )
        
        response = client.chat.completions.create(
            model=config['model'],
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            top_p=0.7,
            max_tokens=4096
        )
        
        return {
            'success': True,
            'provider': config['model'],
            'response': response.choices[0].message.content,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def _call_mistral(self, config: Dict, prompt: str, context: Dict = None) -> Dict:
        """Call Mistral Codestral API"""
        client = OpenAI(
            base_url=config['base_url'],
            api_key=config['api_key']
        )
        
        response = client.chat.completions.create(
            model=config['model'],
            messages=[
                {"role": "system", "content": "You are Codestral, a specialized AI for code analysis."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        return {
            'success': True,
            'provider': config['model'],
            'response': response.choices[0].message.content,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def _call_cerebras(self, config: Dict, prompt: str, context: Dict = None) -> Dict:
        """Call Cerebras API"""
        client = OpenAI(
            base_url=config['base_url'],
            api_key=config['api_key']
        )
        
        response = client.chat.completions.create(
            model=config['model'],
            messages=[
                {"role": "system", "content": "You are an expert AI assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        return {
            'success': True,
            'provider': config['model'],
            'response': response.choices[0].message.content,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def _call_cohere(self, config: Dict, prompt: str, context: Dict = None) -> Dict:
        """Call Cohere API"""
        co = cohere.ClientV2(config['api_key'])
        
        response = co.chat(
            model=config['model'],
            messages=[{"role": "user", "content": prompt}]
        )
        
        return {
            'success': True,
            'provider': config['model'],
            'response': response.text,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def _call_chutes(self, config: Dict, prompt: str, context: Dict = None) -> Dict:
        """Call Chutes API"""
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }
        
        body = {
            "model": config['model'],
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "max_tokens": 1024,
            "temperature": 0.7
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{config['base_url']}/chat/completions",
                headers=headers,
                json=body
            ) as response:
                data = await response.json()
                
                return {
                    'success': True,
                    'provider': config['model'],
                    'response': data['choices'][0]['message']['content'],
                    'timestamp': datetime.utcnow().isoformat()
                }
    
    async def _call_gemini(self, config: Dict, prompt: str, context: Dict = None) -> Dict:
        """Call Google Gemini API"""
        headers = {
            'Content-Type': 'application/json',
            'X-goog-api-key': config['api_key']
        }
        
        body = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{config['base_url']}/models/{config['model']}:generateContent",
                headers=headers,
                json=body
            ) as response:
                data = await response.json()
                
                return {
                    'success': True,
                    'provider': config['model'],
                    'response': data['candidates'][0]['content']['parts'][0]['text'],
                    'timestamp': datetime.utcnow().isoformat()
                }
    
    async def _call_groq(self, config: Dict, prompt: str, context: Dict = None) -> Dict:
        """Call Groq API"""
        client = OpenAI(
            base_url=config['base_url'],
            api_key=config['api_key']
        )
        
        response = client.chat.completions.create(
            model=config['model'],
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2000
        )
        
        return {
            'success': True,
            'provider': config['model'],
            'response': response.choices[0].message.content,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def _call_anthropic(self, config: Dict, prompt: str, context: Dict = None) -> Dict:
        """Call Anthropic Claude API"""
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': config['api_key'],
            'Anthropic-Version': '2023-06-01'
        }
        
        body = {
            "model": config['model'],
            "max_tokens": 2000,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{config['base_url']}/messages",
                headers=headers,
                json=body
            ) as response:
                data = await response.json()
                
                return {
                    'success': True,
                    'provider': config['model'],
                    'response': data['content'][0]['text'],
                    'timestamp': datetime.utcnow().isoformat()
                }
    
    async def analyze_with_fallback(self, prompt: str, context: Dict = None) -> Dict:
        """Analyze with intelligent fallback through all providers"""
        print(f"🤖 Starting AI analysis with {len(self.available_providers)} providers...")
        
        for provider_name, config in self.available_providers.items():
            try:
                print(f"  🔄 Trying {provider_name} ({config['model']})...")
                result = await self.analyze_with_provider(provider_name, prompt, context)
                
                if result['success']:
                    print(f"  ✅ Success with {provider_name}")
                    result['fallback_used'] = provider_name
                    result['total_providers_tried'] = list(self.available_providers.keys()).index(provider_name) + 1
                    return result
                else:
                    print(f"  ❌ Failed with {provider_name}: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"  ❌ Error with {provider_name}: {str(e)}")
                continue
        
        # If all providers fail
        return {
            'success': False,
            'error': 'All AI providers failed',
            'providers_tried': len(self.available_providers),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def get_provider_status(self) -> Dict:
        """Get status of all providers"""
        return {
            'total_providers': len(self.providers),
            'available_providers': len(self.available_providers),
            'providers': {
                name: {
                    'available': name in self.available_providers,
                    'priority': config['priority'],
                    'model': config['model'],
                    'type': config['type']
                }
                for name, config in self.providers.items()
            }
        }

# Global instance
ai_manager = AdvancedAIProviderManager()

async def analyze_code_quality(files: List[str], mode: str = "comprehensive") -> Dict:
    """Analyze code quality using AI"""
    prompt = f"""
    Analyze the following code files for quality, security, and performance issues:
    
    Files: {', '.join(files)}
    Mode: {mode}
    
    Provide:
    1. Code quality assessment
    2. Security vulnerabilities found
    3. Performance optimization opportunities
    4. Specific recommendations with line numbers
    5. Priority levels for each issue
    
    Be specific and actionable in your analysis.
    """
    
    return await ai_manager.analyze_with_fallback(prompt)

async def generate_documentation(files: List[str], level: str = "expert") -> Dict:
    """Generate documentation using AI"""
    prompt = f"""
    Generate comprehensive documentation for the following code files:
    
    Files: {', '.join(files)}
    Level: {level}
    
    Create:
    1. Function/class documentation
    2. API documentation
    3. Usage examples
    4. Architecture overview
    5. Integration guidelines
    
    Make it professional and comprehensive.
    """
    
    return await ai_manager.analyze_with_fallback(prompt)

async def optimize_performance(files: List[str], strategy: str = "aggressive") -> Dict:
    """Optimize code performance using AI"""
    prompt = f"""
    Analyze and optimize the performance of the following code files:
    
    Files: {', '.join(files)}
    Strategy: {strategy}
    
    Provide:
    1. Performance bottlenecks identified
    2. Optimization recommendations
    3. Code refactoring suggestions
    4. Memory usage improvements
    5. Algorithm optimizations
    
    Be specific with code examples and expected improvements.
    """
    
    return await ai_manager.analyze_with_fallback(prompt)

if __name__ == "__main__":
    # Test the provider manager
    async def test():
        print("🧪 Testing AI Provider Manager...")
        
        # Test provider status
        status = ai_manager.get_provider_status()
        print(f"📊 Provider Status: {json.dumps(status, indent=2)}")
        
        # Test analysis
        result = await ai_manager.analyze_with_fallback("Hello, how are you?")
        print(f"🤖 Test Result: {json.dumps(result, indent=2)}")
    
    asyncio.run(test())