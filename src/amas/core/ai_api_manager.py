#!/usr/bin/env python3
"""
AMAS Intelligent AI API Manager
Comprehensive fallback system for maximum reliability across 16 AI providers
"""

import os
import sys
import asyncio
import aiohttp
import json
import time
import random
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import backoff
from openai import OpenAI, AsyncOpenAI
import cohere

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIProvider(Enum):
    """All supported AI API providers"""
    CEREBRAS = "cerebras"
    CODESTRAL = "codestral"
    DEEPSEEK = "deepseek"
    GEMINIAI = "geminiai"
    GLM = "glm"
    GPTOSS = "gptoss"
    GROK = "grok"
    GROQAI = "groqai"
    KIMI = "kimi"
    NVIDIA = "nvidia"
    QWEN = "qwen"
    GEMINI2 = "gemini2"
    GROQ2 = "groq2"
    COHERE = "cohere"
    CHUTES = "chutes"

class APIStatus(Enum):
    """API provider status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    RATE_LIMITED = "rate_limited"
    DISABLED = "disabled"
    UNKNOWN = "unknown"

class TaskType(Enum):
    """Types of AI tasks"""
    CHAT_COMPLETION = "chat_completion"
    CODE_ANALYSIS = "code_analysis"
    TEXT_GENERATION = "text_generation"
    REASONING = "reasoning"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"
    QUESTION_ANSWERING = "question_answering"

@dataclass
class APIEndpoint:
    """Configuration for an API endpoint"""
    provider: APIProvider
    name: str
    api_key: str
    base_url: str
    model: str
    max_tokens: int = 4000
    temperature: float = 0.7
    timeout: int = 30
    rate_limit_rpm: int = 60  # requests per minute
    priority: int = 1  # 1 = highest priority
    enabled: bool = True
    specialty: List[TaskType] = field(default_factory=list)
    
    # Health monitoring
    status: APIStatus = APIStatus.UNKNOWN
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    consecutive_failures: int = 0
    response_times: List[float] = field(default_factory=list)
    
    # Rate limiting
    requests_made: int = 0
    window_start: datetime = field(default_factory=datetime.now)
    
    def reset_rate_limit_window(self):
        """Reset rate limiting window"""
        if datetime.now() - self.window_start > timedelta(minutes=1):
            self.requests_made = 0
            self.window_start = datetime.now()
    
    def can_make_request(self) -> bool:
        """Check if we can make a request within rate limits"""
        self.reset_rate_limit_window()
        return self.requests_made < self.rate_limit_rpm
    
    def record_request(self):
        """Record a request for rate limiting"""
        self.reset_rate_limit_window()
        self.requests_made += 1
    
    def record_success(self, response_time: float):
        """Record successful request"""
        self.last_success = datetime.now()
        self.consecutive_failures = 0
        self.status = APIStatus.HEALTHY
        self.response_times.append(response_time)
        
        # Keep only last 10 response times
        if len(self.response_times) > 10:
            self.response_times = self.response_times[-10:]
    
    def record_failure(self, error: str = None):
        """Record failed request"""
        self.last_failure = datetime.now()
        self.consecutive_failures += 1
        
        # Update status based on failure count
        if self.consecutive_failures >= 5:
            self.status = APIStatus.UNHEALTHY
        elif self.consecutive_failures >= 3:
            self.status = APIStatus.DEGRADED
        
        logger.warning(f"API {self.provider.value} failure #{self.consecutive_failures}: {error}")
    
    def get_average_response_time(self) -> float:
        """Get average response time"""
        return sum(self.response_times) / len(self.response_times) if self.response_times else 0.0

class APIClient(ABC):
    """Abstract base class for API clients"""
    
    def __init__(self, endpoint: APIEndpoint):
        self.endpoint = endpoint
    
    @abstractmethod
    async def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Generate response from the API"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Perform health check"""
        pass

class OpenAICompatibleClient(APIClient):
    """Client for OpenAI-compatible APIs"""
    
    def __init__(self, endpoint: APIEndpoint):
        super().__init__(endpoint)
        self.client = AsyncOpenAI(
            base_url=endpoint.base_url,
            api_key=endpoint.api_key,
            timeout=endpoint.timeout
        )
    
    async def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Generate response using OpenAI-compatible API"""
        try:
            start_time = time.time()
            
            response = await self.client.chat.completions.create(
                model=self.endpoint.model,
                messages=messages,
                max_tokens=kwargs.get('max_tokens', self.endpoint.max_tokens),
                temperature=kwargs.get('temperature', self.endpoint.temperature),
                timeout=self.endpoint.timeout
            )
            
            response_time = time.time() - start_time
            self.endpoint.record_success(response_time)
            
            return {
                'content': response.choices[0].message.content,
                'model': self.endpoint.model,
                'provider': self.endpoint.provider.value,
                'response_time': response_time,
                'usage': response.usage.dict() if response.usage else None
            }
            
        except Exception as e:
            self.endpoint.record_failure(str(e))
            raise
    
    async def health_check(self) -> bool:
        """Perform health check"""
        try:
            await self.generate_response([{"role": "user", "content": "Hello"}])
            return True
        except:
            return False

class CerebrasClient(APIClient):
    """Client for Cerebras API"""
    
    def __init__(self, endpoint: APIEndpoint):
        super().__init__(endpoint)
        # Use specific Cerebras SDK if available, otherwise OpenAI-compatible
        self.client = AsyncOpenAI(
            base_url="https://api.cerebras.ai/v1",
            api_key=endpoint.api_key,
            timeout=endpoint.timeout
        )
    
    async def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Generate response using Cerebras API"""
        try:
            start_time = time.time()
            
            response = await self.client.chat.completions.create(
                model=self.endpoint.model,
                messages=messages,
                max_completion_tokens=kwargs.get('max_tokens', self.endpoint.max_tokens),
                temperature=kwargs.get('temperature', self.endpoint.temperature),
                stream=False
            )
            
            response_time = time.time() - start_time
            self.endpoint.record_success(response_time)
            
            return {
                'content': response.choices[0].message.content,
                'model': self.endpoint.model,
                'provider': self.endpoint.provider.value,
                'response_time': response_time,
                'usage': response.usage.dict() if response.usage else None
            }
            
        except Exception as e:
            self.endpoint.record_failure(str(e))
            raise
    
    async def health_check(self) -> bool:
        """Perform health check"""
        try:
            await self.generate_response([{"role": "user", "content": "Hello"}])
            return True
        except:
            return False

class GeminiClient(APIClient):
    """Client for Google Gemini API"""
    
    def __init__(self, endpoint: APIEndpoint):
        super().__init__(endpoint)
        self.session = None
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Generate response using Gemini API"""
        try:
            start_time = time.time()
            session = await self._get_session()
            
            # Convert messages to Gemini format
            text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
            
            url = f"{self.endpoint.base_url}/models/{self.endpoint.model}:generateContent"
            headers = {
                'Content-Type': 'application/json',
                'X-goog-api-key': self.endpoint.api_key
            }
            
            payload = {
                "contents": [{"parts": [{"text": text}]}],
                "generationConfig": {
                    "maxOutputTokens": kwargs.get('max_tokens', self.endpoint.max_tokens),
                    "temperature": kwargs.get('temperature', self.endpoint.temperature)
                }
            }
            
            async with session.post(url, headers=headers, json=payload, timeout=self.endpoint.timeout) as response:
                if response.status == 200:
                    data = await response.json()
                    content = data['candidates'][0]['content']['parts'][0]['text']
                    
                    response_time = time.time() - start_time
                    self.endpoint.record_success(response_time)
                    
                    return {
                        'content': content,
                        'model': self.endpoint.model,
                        'provider': self.endpoint.provider.value,
                        'response_time': response_time,
                        'usage': data.get('usageMetadata', {})
                    }
                else:
                    error_text = await response.text()
                    self.endpoint.record_failure(f"HTTP {response.status}: {error_text}")
                    raise Exception(f"Gemini API error: {response.status} - {error_text}")
                    
        except Exception as e:
            self.endpoint.record_failure(str(e))
            raise
    
    async def health_check(self) -> bool:
        """Perform health check"""
        try:
            await self.generate_response([{"role": "user", "content": "Hello"}])
            return True
        except:
            return False

class CohereClient(APIClient):
    """Client for Cohere API"""
    
    def __init__(self, endpoint: APIEndpoint):
        super().__init__(endpoint)
        self.client = cohere.AsyncClientV2(api_key=endpoint.api_key)
    
    async def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Generate response using Cohere API"""
        try:
            start_time = time.time()
            
            response = await self.client.chat(
                model=self.endpoint.model,
                messages=messages,
                max_tokens=kwargs.get('max_tokens', self.endpoint.max_tokens),
                temperature=kwargs.get('temperature', self.endpoint.temperature)
            )
            
            response_time = time.time() - start_time
            self.endpoint.record_success(response_time)
            
            return {
                'content': response.message.content[0].text,
                'model': self.endpoint.model,
                'provider': self.endpoint.provider.value,
                'response_time': response_time,
                'usage': response.usage.dict() if hasattr(response, 'usage') else None
            }
            
        except Exception as e:
            self.endpoint.record_failure(str(e))
            raise
    
    async def health_check(self) -> bool:
        """Perform health check"""
        try:
            await self.generate_response([{"role": "user", "content": "Hello"}])
            return True
        except:
            return False

class ChutesClient(APIClient):
    """Client for Chutes API"""
    
    def __init__(self, endpoint: APIEndpoint):
        super().__init__(endpoint)
        self.session = None
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Generate response using Chutes API"""
        try:
            start_time = time.time()
            session = await self._get_session()
            
            headers = {
                "Authorization": f"Bearer {self.endpoint.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.endpoint.model,
                "messages": messages,
                "stream": False,
                "max_tokens": kwargs.get('max_tokens', self.endpoint.max_tokens),
                "temperature": kwargs.get('temperature', self.endpoint.temperature)
            }
            
            async with session.post(
                f"{self.endpoint.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=self.endpoint.timeout
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    content = data['choices'][0]['message']['content']
                    
                    response_time = time.time() - start_time
                    self.endpoint.record_success(response_time)
                    
                    return {
                        'content': content,
                        'model': self.endpoint.model,
                        'provider': self.endpoint.provider.value,
                        'response_time': response_time,
                        'usage': data.get('usage', {})
                    }
                else:
                    error_text = await response.text()
                    self.endpoint.record_failure(f"HTTP {response.status}: {error_text}")
                    raise Exception(f"Chutes API error: {response.status} - {error_text}")
                    
        except Exception as e:
            self.endpoint.record_failure(str(e))
            raise
    
    async def health_check(self) -> bool:
        """Perform health check"""
        try:
            await self.generate_response([{"role": "user", "content": "Hello"}])
            return True
        except:
            return False

class IntelligentAPIManager:
    """Intelligent AI API Manager with comprehensive fallback system"""
    
    def __init__(self):
        self.endpoints: Dict[APIProvider, APIEndpoint] = {}
        self.clients: Dict[APIProvider, APIClient] = {}
        self.last_health_check = datetime.now()
        self.health_check_interval = timedelta(minutes=5)
        
        # Load configurations
        self._load_api_configurations()
        self._initialize_clients()
        
        # Statistics
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.fallback_usage = {provider: 0 for provider in APIProvider}
        
        logger.info(f"Initialized AI API Manager with {len(self.endpoints)} providers")
    
    def _load_api_configurations(self):
        """Load all API configurations"""
        configs = [
            # Cerebras
            {
                'provider': APIProvider.CEREBRAS,
                'name': 'Cerebras',
                'api_key_env': 'CEREBRAS_API_KEY',
                'base_url': 'https://api.cerebras.ai/v1',
                'model': 'qwen-3-235b-a22b-instruct-2507',
                'priority': 1,
                'specialty': [TaskType.REASONING, TaskType.CODE_ANALYSIS]
            },
            # Codestral
            {
                'provider': APIProvider.CODESTRAL,
                'name': 'Codestral (Mistral)',
                'api_key_env': 'CODESTRAL_API_KEY',
                'base_url': 'https://codestral.mistral.ai/v1',
                'model': 'codestral-latest',
                'priority': 2,
                'specialty': [TaskType.CODE_ANALYSIS, TaskType.TEXT_GENERATION]
            },
            # DeepSeek
            {
                'provider': APIProvider.DEEPSEEK,
                'name': 'DeepSeek',
                'api_key_env': 'DEEPSEEK_API_KEY',
                'base_url': 'https://api.deepseek.com/v1',
                'model': 'deepseek-chat',
                'priority': 3,
                'specialty': [TaskType.REASONING, TaskType.CHAT_COMPLETION]
            },
            # Gemini AI
            {
                'provider': APIProvider.GEMINIAI,
                'name': 'Gemini AI',
                'api_key_env': 'GEMINIAI_API_KEY',
                'base_url': 'https://generativelanguage.googleapis.com/v1beta',
                'model': 'gemini-2.0-flash',
                'priority': 4,
                'specialty': [TaskType.REASONING, TaskType.QUESTION_ANSWERING]
            },
            # GLM
            {
                'provider': APIProvider.GLM,
                'name': 'GLM',
                'api_key_env': 'GLM_API_KEY',
                'base_url': 'https://openrouter.ai/api/v1',
                'model': 'zai-org/GLM-4.5-Air',
                'priority': 5,
                'specialty': [TaskType.CHAT_COMPLETION, TaskType.TEXT_GENERATION]
            },
            # GPT OSS
            {
                'provider': APIProvider.GPTOSS,
                'name': 'GPT OSS',
                'api_key_env': 'GPTOSS_API_KEY',
                'base_url': 'https://openrouter.ai/api/v1',
                'model': 'openai/gpt-oss-120b',
                'priority': 6,
                'specialty': [TaskType.CHAT_COMPLETION, TaskType.TEXT_GENERATION]
            },
            # Grok
            {
                'provider': APIProvider.GROK,
                'name': 'Grok',
                'api_key_env': 'GROK_API_KEY',
                'base_url': 'https://openrouter.ai/api/v1',
                'model': 'x-ai/grok-4-fast',
                'priority': 7,
                'specialty': [TaskType.REASONING, TaskType.QUESTION_ANSWERING]
            },
            # Groq AI
            {
                'provider': APIProvider.GROQAI,
                'name': 'Groq AI',
                'api_key_env': 'GROQAI_API_KEY',
                'base_url': 'https://api.groq.com/openai/v1',
                'model': 'llama-3.3-70b-versatile',
                'priority': 8,
                'specialty': [TaskType.CHAT_COMPLETION, TaskType.TEXT_GENERATION]
            },
            # Kimi
            {
                'provider': APIProvider.KIMI,
                'name': 'Kimi',
                'api_key_env': 'KIMI_API_KEY',
                'base_url': 'https://openrouter.ai/api/v1',
                'model': 'moonshotai/kimi-k2',
                'priority': 9,
                'specialty': [TaskType.CHAT_COMPLETION, TaskType.TRANSLATION]
            },
            # NVIDIA
            {
                'provider': APIProvider.NVIDIA,
                'name': 'NVIDIA',
                'api_key_env': 'NVIDIA_API_KEY',
                'base_url': 'https://integrate.api.nvidia.com/v1',
                'model': 'deepseek-ai/deepseek-r1',
                'priority': 10,
                'specialty': [TaskType.REASONING, TaskType.CODE_ANALYSIS]
            },
            # Qwen
            {
                'provider': APIProvider.QWEN,
                'name': 'Qwen',
                'api_key_env': 'QWEN_API_KEY',
                'base_url': 'https://openrouter.ai/api/v1',
                'model': 'qwen/qwen2.5-coder-32b-instruct',
                'priority': 11,
                'specialty': [TaskType.CODE_ANALYSIS, TaskType.TEXT_GENERATION]
            },
            # Gemini 2
            {
                'provider': APIProvider.GEMINI2,
                'name': 'Gemini 2',
                'api_key_env': 'GEMINI2_API_KEY',
                'base_url': 'https://generativelanguage.googleapis.com/v1beta',
                'model': 'gemini-2.0-flash',
                'priority': 12,
                'specialty': [TaskType.REASONING, TaskType.QUESTION_ANSWERING]
            },
            # Groq 2
            {
                'provider': APIProvider.GROQ2,
                'name': 'Groq 2',
                'api_key_env': 'GROQ2_API_KEY',
                'base_url': 'https://api.groq.com/openai/v1',
                'model': 'llama-3.3-70b-versatile',
                'priority': 13,
                'specialty': [TaskType.CHAT_COMPLETION, TaskType.TEXT_GENERATION]
            },
            # Cohere
            {
                'provider': APIProvider.COHERE,
                'name': 'Cohere',
                'api_key_env': 'COHERE_API_KEY',
                'base_url': 'https://api.cohere.ai/v1',
                'model': 'command-a-03-2025',
                'priority': 14,
                'specialty': [TaskType.CHAT_COMPLETION, TaskType.SUMMARIZATION]
            },
            # Chutes
            {
                'provider': APIProvider.CHUTES,
                'name': 'Chutes',
                'api_key_env': 'CHUTES_API_KEY',
                'base_url': 'https://llm.chutes.ai/v1',
                'model': 'zai-org/GLM-4.5-Air',
                'priority': 15,
                'specialty': [TaskType.CHAT_COMPLETION, TaskType.TEXT_GENERATION]
            }
        ]
        
        for config in configs:
            api_key = os.getenv(config['api_key_env'])
            if api_key:
                endpoint = APIEndpoint(
                    provider=config['provider'],
                    name=config['name'],
                    api_key=api_key,
                    base_url=config['base_url'],
                    model=config['model'],
                    priority=config['priority'],
                    specialty=config.get('specialty', []),
                    enabled=True
                )
                self.endpoints[config['provider']] = endpoint
                logger.info(f"✅ {config['name']} API configured")
            else:
                logger.warning(f"❌ {config['name']} API key not found in environment")
    
    def _initialize_clients(self):
        """Initialize API clients for each endpoint"""
        for provider, endpoint in self.endpoints.items():
            try:
                if provider in [APIProvider.CEREBRAS]:
                    self.clients[provider] = CerebrasClient(endpoint)
                elif provider in [APIProvider.GEMINIAI, APIProvider.GEMINI2]:
                    self.clients[provider] = GeminiClient(endpoint)
                elif provider in [APIProvider.COHERE]:
                    self.clients[provider] = CohereClient(endpoint)
                elif provider in [APIProvider.CHUTES]:
                    self.clients[provider] = ChutesClient(endpoint)
                else:
                    # Default to OpenAI-compatible client
                    self.clients[provider] = OpenAICompatibleClient(endpoint)
                
                logger.info(f"✅ {endpoint.name} client initialized")
                
            except Exception as e:
                logger.error(f"❌ Failed to initialize {endpoint.name} client: {e}")
                endpoint.enabled = False
    
    def get_available_providers(self, task_type: TaskType = None) -> List[APIProvider]:
        """Get available providers, optionally filtered by task type"""
        providers = []
        
        for provider, endpoint in self.endpoints.items():
            if not endpoint.enabled or endpoint.status == APIStatus.UNHEALTHY:
                continue
            
            if task_type and task_type not in endpoint.specialty and endpoint.specialty:
                continue
            
            if not endpoint.can_make_request():
                continue
            
            providers.append(provider)
        
        # Sort by priority and health status
        def sort_key(provider):
            endpoint = self.endpoints[provider]
            status_priority = {
                APIStatus.HEALTHY: 0,
                APIStatus.DEGRADED: 1,
                APIStatus.RATE_LIMITED: 2,
                APIStatus.UNKNOWN: 3,
                APIStatus.UNHEALTHY: 4,
                APIStatus.DISABLED: 5
            }
            return (status_priority.get(endpoint.status, 10), endpoint.priority)
        
        providers.sort(key=sort_key)
        return providers
    
    @backoff.on_exception(backoff.expo, Exception, max_tries=3, max_time=30)
    async def generate_response_with_fallback(
        self,
        messages: List[Dict[str, str]],
        task_type: TaskType = TaskType.CHAT_COMPLETION,
        preferred_provider: APIProvider = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response with intelligent fallback"""
        self.total_requests += 1
        
        # Get available providers
        available_providers = self.get_available_providers(task_type)
        
        if not available_providers:
            self.failed_requests += 1
            raise Exception("No available API providers")
        
        # Try preferred provider first if specified
        if preferred_provider and preferred_provider in available_providers:
            available_providers.remove(preferred_provider)
            available_providers.insert(0, preferred_provider)
        
        last_error = None
        
        for provider in available_providers:
            try:
                endpoint = self.endpoints[provider]
                client = self.clients[provider]
                
                logger.info(f"🔄 Trying {endpoint.name} for {task_type.value}")
                
                # Record request for rate limiting
                endpoint.record_request()
                
                # Generate response
                response = await client.generate_response(messages, **kwargs)
                
                # Record success
                self.successful_requests += 1
                self.fallback_usage[provider] += 1
                
                # Add metadata
                response['fallback_attempts'] = available_providers.index(provider) + 1
                response['total_available'] = len(available_providers)
                
                logger.info(f"✅ {endpoint.name} succeeded in {response['response_time']:.2f}s")
                return response
                
            except Exception as e:
                last_error = e
                logger.warning(f"❌ {self.endpoints[provider].name} failed: {e}")
                continue
        
        # All providers failed
        self.failed_requests += 1
        raise Exception(f"All API providers failed. Last error: {last_error}")
    
    async def health_check_all_providers(self) -> Dict[APIProvider, bool]:
        """Perform health check on all providers"""
        results = {}
        
        tasks = []
        for provider, client in self.clients.items():
            task = asyncio.create_task(self._health_check_provider(provider, client))
            tasks.append(task)
        
        health_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, provider in enumerate(self.clients.keys()):
            result = health_results[i]
            if isinstance(result, Exception):
                results[provider] = False
                self.endpoints[provider].record_failure(str(result))
            else:
                results[provider] = result
                if result:
                    self.endpoints[provider].status = APIStatus.HEALTHY
                else:
                    self.endpoints[provider].record_failure("Health check failed")
        
        self.last_health_check = datetime.now()
        logger.info(f"Health check completed. Healthy providers: {sum(results.values())}/{len(results)}")
        
        return results
    
    async def _health_check_provider(self, provider: APIProvider, client: APIClient) -> bool:
        """Health check for a single provider"""
        try:
            return await client.health_check()
        except Exception as e:
            logger.warning(f"Health check failed for {provider.value}: {e}")
            return False
    
    def get_provider_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics"""
        healthy_providers = sum(1 for ep in self.endpoints.values() if ep.status == APIStatus.HEALTHY)
        total_providers = len(self.endpoints)
        
        provider_stats = {}
        for provider, endpoint in self.endpoints.items():
            provider_stats[provider.value] = {
                'name': endpoint.name,
                'status': endpoint.status.value,
                'enabled': endpoint.enabled,
                'priority': endpoint.priority,
                'consecutive_failures': endpoint.consecutive_failures,
                'last_success': endpoint.last_success.isoformat() if endpoint.last_success else None,
                'last_failure': endpoint.last_failure.isoformat() if endpoint.last_failure else None,
                'average_response_time': endpoint.get_average_response_time(),
                'usage_count': self.fallback_usage[provider],
                'rate_limit_remaining': endpoint.rate_limit_rpm - endpoint.requests_made,
                'specialty': [t.value for t in endpoint.specialty]
            }
        
        return {
            'overview': {
                'total_requests': self.total_requests,
                'successful_requests': self.successful_requests,
                'failed_requests': self.failed_requests,
                'success_rate': (self.successful_requests / self.total_requests * 100) if self.total_requests > 0 else 0,
                'healthy_providers': healthy_providers,
                'total_providers': total_providers,
                'health_percentage': (healthy_providers / total_providers * 100) if total_providers > 0 else 0
            },
            'providers': provider_stats,
            'last_health_check': self.last_health_check.isoformat()
        }
    
    async def auto_health_monitoring(self):
        """Automatic health monitoring loop"""
        while True:
            try:
                if datetime.now() - self.last_health_check > self.health_check_interval:
                    await self.health_check_all_providers()
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in health monitoring: {e}")
                await asyncio.sleep(60)
    
    def disable_provider(self, provider: APIProvider):
        """Disable a specific provider"""
        if provider in self.endpoints:
            self.endpoints[provider].enabled = False
            self.endpoints[provider].status = APIStatus.DISABLED
            logger.info(f"Disabled provider: {provider.value}")
    
    def enable_provider(self, provider: APIProvider):
        """Enable a specific provider"""
        if provider in self.endpoints:
            self.endpoints[provider].enabled = True
            self.endpoints[provider].status = APIStatus.UNKNOWN
            logger.info(f"Enabled provider: {provider.value}")
    
    async def optimize_provider_usage(self):
        """Optimize provider usage based on performance"""
        # Sort providers by performance metrics
        performance_scores = {}
        
        for provider, endpoint in self.endpoints.items():
            if not endpoint.enabled or endpoint.status == APIStatus.UNHEALTHY:
                continue
            
            # Calculate performance score
            success_rate = max(0, 10 - endpoint.consecutive_failures)
            response_time_score = max(0, 10 - endpoint.get_average_response_time())
            health_score = {
                APIStatus.HEALTHY: 10,
                APIStatus.DEGRADED: 5,
                APIStatus.RATE_LIMITED: 3,
                APIStatus.UNKNOWN: 1,
                APIStatus.UNHEALTHY: 0,
                APIStatus.DISABLED: 0
            }.get(endpoint.status, 0)
            
            performance_scores[provider] = (success_rate + response_time_score + health_score) / 3
        
        # Adjust priorities based on performance
        sorted_providers = sorted(performance_scores.items(), key=lambda x: x[1], reverse=True)
        
        for i, (provider, score) in enumerate(sorted_providers):
            self.endpoints[provider].priority = i + 1
        
        logger.info("Provider priorities optimized based on performance")

# Global instance
_api_manager = None

def get_api_manager() -> IntelligentAPIManager:
    """Get the global API manager instance"""
    global _api_manager
    if _api_manager is None:
        _api_manager = IntelligentAPIManager()
    return _api_manager

async def generate_ai_response(
    messages: List[Dict[str, str]],
    task_type: TaskType = TaskType.CHAT_COMPLETION,
    preferred_provider: APIProvider = None,
    **kwargs
) -> Dict[str, Any]:
    """Convenience function to generate AI response with fallback"""
    manager = get_api_manager()
    return await manager.generate_response_with_fallback(
        messages=messages,
        task_type=task_type,
        preferred_provider=preferred_provider,
        **kwargs
    )

if __name__ == "__main__":
    async def test_api_manager():
        """Test the API manager"""
        manager = IntelligentAPIManager()
        
        # Health check
        print("Performing health checks...")
        health_results = await manager.health_check_all_providers()
        print(f"Health check results: {health_results}")
        
        # Test generation
        try:
            response = await manager.generate_response_with_fallback(
                messages=[{"role": "user", "content": "Hello, how are you?"}],
                task_type=TaskType.CHAT_COMPLETION
            )
            print(f"Response: {response}")
        except Exception as e:
            print(f"Generation failed: {e}")
        
        # Get statistics
        stats = manager.get_provider_statistics()
        print(f"Statistics: {json.dumps(stats, indent=2)}")
    
    asyncio.run(test_api_manager())