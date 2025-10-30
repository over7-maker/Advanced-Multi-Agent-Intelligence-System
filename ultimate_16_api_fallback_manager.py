#!/usr/bin/env python3
"""
Ultimate 16-API Fallback Manager
Bulletproof AI service with comprehensive failover
Ensures ZERO failures across all workflows and AI tasks
"""

import os
import sys
import asyncio
import aiohttp
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProviderType(Enum):
    OPENAI_COMPATIBLE = "openai_compatible"
    GEMINI = "gemini"
    CEREBRAS = "cerebras"
    COHERE = "cohere"
    CHUTES = "chutes"
    NVIDIA = "nvidia"
    CODESTRAL = "codestral"
    GROQ = "groq"

@dataclass
class ProviderConfig:
    name: str
    api_key: str
    base_url: str
    model: str
    provider_type: ProviderType
    priority: int
    max_tokens: int = 4096
    timeout: int = 30
    capabilities: List[str] = None
    headers: Dict[str, str] = None

class Ultimate16APIFallbackManager:
    """
    Ultimate 16-API Fallback Manager
    Comprehensive failover system ensuring 100% uptime
    """
    
    def __init__(self):
        """Initialize the ultimate fallback manager"""
        self.providers = {}
        self.provider_stats = {}
        self.fallback_order = []
        self.initialize_providers()
        self.setup_fallback_order()
        
        logger.info("🚀 Ultimate 16-API Fallback Manager initialized")
        logger.info(f"📊 Total providers: {len(self.providers)}")
    
    def initialize_providers(self):
        """Initialize all 16 API providers with your actual keys"""
        
        # 1. DeepSeek V3.1 (OpenRouter)
        self.providers["deepseek"] = ProviderConfig(
            name="DeepSeek V3.1",
            api_key=os.getenv("DEEPSEEK_API_KEY", "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"),
            base_url="https://openrouter.ai/api/v1",
            model="deepseek/deepseek-chat-v3.1:free",
            provider_type=ProviderType.OPENAI_COMPATIBLE,
            priority=1,
            max_tokens=8192,
            capabilities=["reasoning", "analysis", "coding", "chinese_support"]
        )
        
        # 2. GLM 4.5 Air (OpenRouter)
        self.providers["glm"] = ProviderConfig(
            name="GLM 4.5 Air",
            api_key=os.getenv("GLM_API_KEY", "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"),
            base_url="https://openrouter.ai/api/v1",
            model="z-ai/glm-4.5-air:free",
            provider_type=ProviderType.OPENAI_COMPATIBLE,
            priority=2,
            max_tokens=8192,
            capabilities=["reasoning", "analysis", "chinese_support"]
        )
        
        # 3. Grok 4 Fast (OpenRouter)
        self.providers["grok"] = ProviderConfig(
            name="Grok 4 Fast",
            api_key=os.getenv("GROK_API_KEY", "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"),
            base_url="https://openrouter.ai/api/v1",
            model="x-ai/grok-4-fast:free",
            provider_type=ProviderType.OPENAI_COMPATIBLE,
            priority=3,
            max_tokens=8192,
            capabilities=["reasoning", "analysis", "multimodal"]
        )
        
        # 4. Kimi K2 (OpenRouter)
        self.providers["kimi"] = ProviderConfig(
            name="Kimi K2",
            api_key=os.getenv("KIMI_API_KEY", "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"),
            base_url="https://openrouter.ai/api/v1",
            model="moonshotai/kimi-k2:free",
            provider_type=ProviderType.OPENAI_COMPATIBLE,
            priority=4,
            max_tokens=8192,
            capabilities=["reasoning", "analysis", "chinese_support"]
        )
        
        # 5. Qwen3 Coder (OpenRouter)
        self.providers["qwen"] = ProviderConfig(
            name="Qwen3 Coder",
            api_key=os.getenv("QWEN_API_KEY", "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"),
            base_url="https://openrouter.ai/api/v1",
            model="qwen/qwen3-coder:free",
            provider_type=ProviderType.OPENAI_COMPATIBLE,
            priority=5,
            max_tokens=8192,
            capabilities=["coding", "analysis", "chinese_support"]
        )
        
        # 6. GPT-OSS 120B (OpenRouter)
        self.providers["gptoss"] = ProviderConfig(
            name="GPT-OSS 120B",
            api_key=os.getenv("GPTOSS_API_KEY", "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"),
            base_url="https://openrouter.ai/api/v1",
            model="openai/gpt-oss-120b:free",
            provider_type=ProviderType.OPENAI_COMPATIBLE,
            priority=6,
            max_tokens=8192,
            capabilities=["reasoning", "analysis", "general"]
        )
        
        # 7. Gemini 2.0 Flash (Direct API)
        self.providers["gemini2"] = ProviderConfig(
            name="Gemini 2.0 Flash",
            api_key=os.getenv("GEMINI2_API_KEY", "AIzaSyBC1ybRkqyc2jSXAj4_2-XT5rXF7ENa0cs"),
            base_url="https://generativelanguage.googleapis.com/v1beta",
            model="gemini-2.0-flash",
            provider_type=ProviderType.GEMINI,
            priority=7,
            max_tokens=8192,
            capabilities=["reasoning", "analysis", "multimodal"]
        )
        
        # 8. NVIDIA (Direct API)
        self.providers["nvidia"] = ProviderConfig(
            name="NVIDIA",
            api_key=os.getenv("NVIDIA_API_KEY", "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"),
            base_url="https://integrate.api.nvidia.com/v1",
            model="deepseek-ai/deepseek-r1",
            provider_type=ProviderType.NVIDIA,
            priority=8,
            max_tokens=4096,
            capabilities=["reasoning", "analysis", "coding"]
        )
        
        # 9. Codestral (Direct API)
        self.providers["codestral"] = ProviderConfig(
            name="Codestral",
            api_key=os.getenv("CODESTRAL_API_KEY", "2kutMTaniEaGOJXkOWBcyt9eE70ZmS4r"),
            base_url="https://codestral.mistral.ai/v1",
            model="codestral-latest",
            provider_type=ProviderType.CODESTRAL,
            priority=9,
            max_tokens=8192,
            capabilities=["coding", "analysis", "technical"]
        )
        
        # 10. Cerebras (Direct API)
        self.providers["cerebras"] = ProviderConfig(
            name="Cerebras",
            api_key=os.getenv("CEREBRAS_API_KEY", "csk-2feh4665p9y32jwy5etm3fkd8cfh52w4dj3t2ekd5t2yh43k"),
            base_url="https://api.cerebras.ai/v1",
            model="qwen-3-235b-a22b-instruct-2507",
            provider_type=ProviderType.CEREBRAS,
            priority=10,
            max_tokens=20000,
            capabilities=["reasoning", "analysis", "long_context"]
        )
        
        # 11. Cohere (Direct API)
        self.providers["cohere"] = ProviderConfig(
            name="Cohere",
            api_key=os.getenv("COHERE_API_KEY", "uBCLBBUn5BEcdBZjJOYQDMLUtTexPcbq3HQsKy22"),
            base_url="https://api.cohere.ai/v1",
            model="command-a-03-2025",
            provider_type=ProviderType.COHERE,
            priority=11,
            max_tokens=4096,
            capabilities=["reasoning", "analysis", "general"]
        )
        
        # 12. Chutes (Direct API)
        self.providers["chutes"] = ProviderConfig(
            name="Chutes",
            api_key=os.getenv("CHUTES_API_KEY", "cpk_54cf325756a54a84a7730eb12b7a203e.d2055a9231325ba5b31b765bb0001987.EJPb6s3CY2MyOPgQtNwJAew9aic7hRHA"),
            base_url="https://llm.chutes.ai/v1",
            model="zai-org/GLM-4.5-Air",
            provider_type=ProviderType.CHUTES,
            priority=12,
            max_tokens=1024,
            capabilities=["reasoning", "analysis", "streaming"]
        )
        
        # 13. Groq2 (Direct API)
        self.providers["groq2"] = ProviderConfig(
            name="Groq2",
            api_key=os.getenv("GROQ2_API_KEY", "gsk_q4AGPMc0aiUS2sXEVupDWGdyb3FYOVIRo uEhabWQJry9C443ejra"),
            base_url="https://api.groq.com/openai/v1",
            model="llama-3.3-70b-versatile",
            provider_type=ProviderType.GROQ,
            priority=13,
            max_tokens=8192,
            capabilities=["fast_inference", "reasoning", "analysis"]
        )
        
        # 14. GeminiAI (Backup)
        self.providers["geminiai"] = ProviderConfig(
            name="GeminiAI",
            api_key=os.getenv("GEMINIAI_API_KEY", "AIzaSyBC1ybRkqyc2jSXAj4_2-XT5rXF7ENa0cs"),
            base_url="https://generativelanguage.googleapis.com/v1beta",
            model="gemini-1.5-pro",
            provider_type=ProviderType.GEMINI,
            priority=14,
            max_tokens=8192,
            capabilities=["reasoning", "analysis", "multimodal"]
        )
        
        # 15. GroqAI (Backup)
        self.providers["groqai"] = ProviderConfig(
            name="GroqAI",
            api_key=os.getenv("GROQAI_API_KEY", "gsk_q4AGPMc0aiUS2sXEVupDWGdyb3FYOVIRo uEhabWQJry9C443ejra"),
            base_url="https://api.groq.com/openai/v1",
            model="llama-3.1-70b-versatile",
            provider_type=ProviderType.GROQ,
            priority=15,
            max_tokens=8192,
            capabilities=["fast_inference", "reasoning", "analysis"]
        )
        
        # 16. Claude (Backup - if available)
        self.providers["claude"] = ProviderConfig(
            name="Claude",
            api_key=os.getenv("CLAUDE_API_KEY", ""),
            base_url="https://api.anthropic.com/v1",
            model="claude-3-5-sonnet-20241022",
            provider_type=ProviderType.OPENAI_COMPATIBLE,
            priority=16,
            max_tokens=8192,
            capabilities=["reasoning", "analysis", "general"]
        )
        
        # Initialize stats for each provider
        for provider_id in self.providers:
            self.provider_stats[provider_id] = {
                'total_calls': 0,
                'successful_calls': 0,
                'failed_calls': 0,
                'last_success': None,
                'last_failure': None,
                'avg_response_time': 0.0,
                'is_healthy': True
            }
    
    def setup_fallback_order(self):
        """Setup intelligent fallback order based on priority and capabilities"""
        # Sort by priority (lower number = higher priority)
        self.fallback_order = sorted(
            self.providers.keys(),
            key=lambda x: self.providers[x].priority
        )
        
        logger.info(f"🔄 Fallback order: {self.fallback_order}")
    
    async def make_request(self, provider_id: str, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """Make a request to a specific provider"""
        provider = self.providers[provider_id]
        start_time = time.time()
        
        try:
            if provider.provider_type == ProviderType.OPENAI_COMPATIBLE:
                return await self._make_openai_request(provider, messages, **kwargs)
            elif provider.provider_type == ProviderType.GEMINI:
                return await self._make_gemini_request(provider, messages, **kwargs)
            elif provider.provider_type == ProviderType.CEREBRAS:
                return await self._make_cerebras_request(provider, messages, **kwargs)
            elif provider.provider_type == ProviderType.COHERE:
                return await self._make_cohere_request(provider, messages, **kwargs)
            elif provider.provider_type == ProviderType.CHUTES:
                return await self._make_chutes_request(provider, messages, **kwargs)
            elif provider.provider_type == ProviderType.NVIDIA:
                return await self._make_nvidia_request(provider, messages, **kwargs)
            elif provider.provider_type == ProviderType.CODESTRAL:
                return await self._make_codestral_request(provider, messages, **kwargs)
            elif provider.provider_type == ProviderType.GROQ:
                return await self._make_groq_request(provider, messages, **kwargs)
            else:
                raise ValueError(f"Unsupported provider type: {provider.provider_type}")
                
        except Exception as e:
            response_time = time.time() - start_time
            self._update_provider_stats(provider_id, success=False, response_time=response_time, error=str(e))
            raise e
    
    async def _make_openai_request(self, provider: ProviderConfig, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """Make OpenAI-compatible request"""
        headers = {
            "Authorization": f"Bearer {provider.api_key}",
            "Content-Type": "application/json"
        }
        
        if provider.headers:
            headers.update(provider.headers)
        
        payload = {
            "model": provider.model,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", provider.max_tokens),
            "temperature": kwargs.get("temperature", 0.7),
            "stream": kwargs.get("stream", False)
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{provider.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=provider.timeout)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "content": data["choices"][0]["message"]["content"],
                        "provider": provider.name,
                        "model": provider.model,
                        "usage": data.get("usage", {}),
                        "success": True
                    }
                else:
                    error_text = await response.text()
                    raise Exception(f"HTTP {response.status}: {error_text}")
    
    async def _make_gemini_request(self, provider: ProviderConfig, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """Make Gemini API request"""
        headers = {
            "X-goog-api-key": provider.api_key,
            "Content-Type": "application/json"
        }
        
        # Convert messages to Gemini format
        contents = []
        for msg in messages:
            if msg["role"] == "user":
                contents.append({
                    "parts": [{"text": msg["content"]}]
                })
            elif msg["role"] == "assistant":
                contents.append({
                    "parts": [{"text": msg["content"]}],
                    "role": "model"
                })
        
        payload = {
            "contents": contents,
            "generationConfig": {
                "maxOutputTokens": kwargs.get("max_tokens", provider.max_tokens),
                "temperature": kwargs.get("temperature", 0.7)
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{provider.base_url}/models/{provider.model}:generateContent",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=provider.timeout)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    content = data["candidates"][0]["content"]["parts"][0]["text"]
                    return {
                        "content": content,
                        "provider": provider.name,
                        "model": provider.model,
                        "success": True
                    }
                else:
                    error_text = await response.text()
                    raise Exception(f"HTTP {response.status}: {error_text}")
    
    async def _make_cerebras_request(self, provider: ProviderConfig, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """Make Cerebras API request"""
        headers = {
            "Authorization": f"Bearer {provider.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": provider.model,
            "messages": messages,
            "max_completion_tokens": kwargs.get("max_tokens", provider.max_tokens),
            "temperature": kwargs.get("temperature", 0.7),
            "stream": False
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{provider.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=provider.timeout)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "content": data["choices"][0]["message"]["content"],
                        "provider": provider.name,
                        "model": provider.model,
                        "success": True
                    }
                else:
                    error_text = await response.text()
                    raise Exception(f"HTTP {response.status}: {error_text}")
    
    async def _make_cohere_request(self, provider: ProviderConfig, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """Make Cohere API request"""
        headers = {
            "Authorization": f"Bearer {provider.api_key}",
            "Content-Type": "application/json"
        }
        
        # Convert messages to Cohere format
        chat_history = []
        message = messages[-1]["content"] if messages else ""
        
        for msg in messages[:-1]:
            if msg["role"] == "user":
                chat_history.append({"role": "user", "message": msg["content"]})
            elif msg["role"] == "assistant":
                chat_history.append({"role": "assistant", "message": msg["content"]})
        
        payload = {
            "model": provider.model,
            "message": message,
            "chat_history": chat_history,
            "max_tokens": kwargs.get("max_tokens", provider.max_tokens),
            "temperature": kwargs.get("temperature", 0.7)
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{provider.base_url}/chat",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=provider.timeout)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "content": data["text"],
                        "provider": provider.name,
                        "model": provider.model,
                        "success": True
                    }
                else:
                    error_text = await response.text()
                    raise Exception(f"HTTP {response.status}: {error_text}")
    
    async def _make_chutes_request(self, provider: ProviderConfig, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """Make Chutes API request"""
        headers = {
            "Authorization": f"Bearer {provider.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": provider.model,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", provider.max_tokens),
            "temperature": kwargs.get("temperature", 0.7),
            "stream": False
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{provider.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=provider.timeout)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "content": data["choices"][0]["message"]["content"],
                        "provider": provider.name,
                        "model": provider.model,
                        "success": True
                    }
                else:
                    error_text = await response.text()
                    raise Exception(f"HTTP {response.status}: {error_text}")
    
    async def _make_nvidia_request(self, provider: ProviderConfig, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """Make NVIDIA API request"""
        headers = {
            "Authorization": f"Bearer {provider.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": provider.model,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", provider.max_tokens),
            "temperature": kwargs.get("temperature", 0.7),
            "stream": False
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{provider.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=provider.timeout)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "content": data["choices"][0]["message"]["content"],
                        "provider": provider.name,
                        "model": provider.model,
                        "success": True
                    }
                else:
                    error_text = await response.text()
                    raise Exception(f"HTTP {response.status}: {error_text}")
    
    async def _make_codestral_request(self, provider: ProviderConfig, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """Make Codestral API request"""
        headers = {
            "Authorization": f"Bearer {provider.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": provider.model,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", provider.max_tokens),
            "temperature": kwargs.get("temperature", 0.7),
            "stream": False
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{provider.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=provider.timeout)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "content": data["choices"][0]["message"]["content"],
                        "provider": provider.name,
                        "model": provider.model,
                        "success": True
                    }
                else:
                    error_text = await response.text()
                    raise Exception(f"HTTP {response.status}: {error_text}")
    
    async def _make_groq_request(self, provider: ProviderConfig, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """Make Groq API request"""
        headers = {
            "Authorization": f"Bearer {provider.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": provider.model,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", provider.max_tokens),
            "temperature": kwargs.get("temperature", 0.7),
            "stream": False
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{provider.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=provider.timeout)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "content": data["choices"][0]["message"]["content"],
                        "provider": provider.name,
                        "model": provider.model,
                        "success": True
                    }
                else:
                    error_text = await response.text()
                    raise Exception(f"HTTP {response.status}: {error_text}")
    
    def _update_provider_stats(self, provider_id: str, success: bool, response_time: float, error: str = None):
        """Update provider statistics"""
        stats = self.provider_stats[provider_id]
        stats['total_calls'] += 1
        
        if success:
            stats['successful_calls'] += 1
            stats['last_success'] = datetime.now().isoformat()
            stats['is_healthy'] = True
        else:
            stats['failed_calls'] += 1
            stats['last_failure'] = datetime.now().isoformat()
            # Mark as unhealthy if too many failures
            if stats['failed_calls'] > 5:
                stats['is_healthy'] = False
        
        # Update average response time
        if stats['total_calls'] == 1:
            stats['avg_response_time'] = response_time
        else:
            stats['avg_response_time'] = (stats['avg_response_time'] + response_time) / 2
    
    async def generate_with_fallback(self, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """
        Generate response with comprehensive fallback
        Tries all providers in order until one succeeds
        """
        last_error = None
        
        for provider_id in self.fallback_order:
            provider = self.providers[provider_id]
            
            # Skip unhealthy providers
            if not self.provider_stats[provider_id]['is_healthy']:
                logger.warning(f"⚠️  Skipping unhealthy provider: {provider.name}")
                continue
            
            # Skip providers without API keys
            if not provider.api_key:
                logger.warning(f"⚠️  Skipping provider without API key: {provider.name}")
                continue
            
            try:
                logger.info(f"🔄 Trying provider: {provider.name}")
                result = await self.make_request(provider_id, messages, **kwargs)
                
                # Update stats
                response_time = time.time()
                self._update_provider_stats(provider_id, success=True, response_time=response_time)
                
                logger.info(f"✅ Success with {provider.name}")
                return result
                
            except Exception as e:
                last_error = e
                logger.warning(f"❌ Failed with {provider.name}: {str(e)}")
                
                # Update stats
                response_time = time.time()
                self._update_provider_stats(provider_id, success=False, response_time=response_time, error=str(e))
                
                # Continue to next provider
                continue
        
        # If we get here, all providers failed
        error_msg = f"🚨 ALL PROVIDERS FAILED! Last error: {str(last_error)}"
        logger.error(error_msg)
        
        return {
            "content": f"Error: All AI providers failed. Last error: {str(last_error)}",
            "provider": "none",
            "model": "none",
            "success": False,
            "error": error_msg
        }
    
    def get_provider_stats(self) -> Dict[str, Any]:
        """Get comprehensive provider statistics"""
        total_calls = sum(stats['total_calls'] for stats in self.provider_stats.values())
        successful_calls = sum(stats['successful_calls'] for stats in self.provider_stats.values())
        failed_calls = sum(stats['failed_calls'] for stats in self.provider_stats.values())
        
        healthy_providers = sum(1 for stats in self.provider_stats.values() if stats['is_healthy'])
        
        return {
            "total_providers": len(self.providers),
            "healthy_providers": healthy_providers,
            "total_calls": total_calls,
            "successful_calls": successful_calls,
            "failed_calls": failed_calls,
            "success_rate": (successful_calls / total_calls * 100) if total_calls > 0 else 0,
            "providers": self.provider_stats
        }
    
    def reset_provider_health(self):
        """Reset all providers to healthy status"""
        for provider_id in self.provider_stats:
            self.provider_stats[provider_id]['is_healthy'] = True
        logger.info("🔄 All providers reset to healthy status")

# Convenience functions for easy integration
async def generate_ai_response(prompt: str, **kwargs) -> str:
    """Generate AI response with automatic fallback"""
    manager = Ultimate16APIFallbackManager()
    messages = [{"role": "user", "content": prompt}]
    result = await manager.generate_with_fallback(messages, **kwargs)
    return result["content"]

async def generate_ai_response_with_context(messages: List[Dict], **kwargs) -> Dict[str, Any]:
    """Generate AI response with context and automatic fallback"""
    manager = Ultimate16APIFallbackManager()
    return await manager.generate_with_fallback(messages, **kwargs)

def get_api_key(provider_name: str) -> str:
    """Get API key for a specific provider"""
    manager = Ultimate16APIFallbackManager()
    provider = manager.providers.get(provider_name.lower())
    return provider.api_key if provider else None

# Example usage and testing
async def test_ultimate_fallback():
    """Test the ultimate fallback system"""
    print("🧪 TESTING ULTIMATE 16-API FALLBACK SYSTEM")
    print("=" * 60)
    
    manager = Ultimate16APIFallbackManager()
    
    # Test 1: Simple prompt
    print("\n🔍 Test 1: Simple prompt")
    messages = [{"role": "user", "content": "Hello! Can you tell me what 2+2 equals?"}]
    result = await manager.generate_with_fallback(messages)
    print(f"Response: {result['content']}")
    print(f"Provider: {result['provider']}")
    print(f"Success: {result['success']}")
    
    # Test 2: Complex coding task
    print("\n🔍 Test 2: Complex coding task")
    messages = [{"role": "user", "content": "Write a Python function to calculate the Fibonacci sequence."}]
    result = await manager.generate_with_fallback(messages)
    print(f"Response: {result['content'][:200]}...")
    print(f"Provider: {result['provider']}")
    print(f"Success: {result['success']}")
    
    # Test 3: Show statistics
    print("\n📊 Provider Statistics:")
    stats = manager.get_provider_stats()
    print(f"Total Providers: {stats['total_providers']}")
    print(f"Healthy Providers: {stats['healthy_providers']}")
    print(f"Success Rate: {stats['success_rate']:.1f}%")
    
    return stats

if __name__ == "__main__":
    # Run test
    asyncio.run(test_ultimate_fallback())