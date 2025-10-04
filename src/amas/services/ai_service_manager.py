"""
AI Service Manager with Multi-Provider Fallback System
Handles 6 different AI providers with intelligent failover
"""

import asyncio
import logging
import os
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import aiohttp
import json
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class AIProvider(Enum):
    """AI Provider enumeration"""
    DEEPSEEK = "deepseek"
    GLM = "glm"
    GROK = "grok"
    KIMI = "kimi"
    QWEN = "qwen"
    GPTOSS = "gptoss"

@dataclass
class AIProviderConfig:
    """Configuration for AI provider"""
    name: str
    api_key: str
    base_url: str
    model: str
    max_tokens: int = 4000
    temperature: float = 0.7
    timeout: int = 30
    rate_limit: int = 60  # requests per minute
    priority: int = 1  # 1 = highest priority
    enabled: bool = True

@dataclass
class AIResponse:
    """Standardized AI response"""
    content: str
    provider: str
    model: str
    tokens_used: int
    response_time: float
    timestamp: datetime
    success: bool
    error: Optional[str] = None

class AIServiceManager:
    """AI Service Manager with intelligent fallback and load balancing"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.providers: Dict[AIProvider, AIProviderConfig] = {}
        self.provider_stats: Dict[AIProvider, Dict[str, Any]] = {}
        self.rate_limiters: Dict[AIProvider, Dict[str, Any]] = {}
        self.session: Optional[aiohttp.ClientSession] = None
        self._initialize_providers()
        self._initialize_stats()

    def _initialize_providers(self):
        """Initialize all AI providers from configuration"""
        try:
            # DeepSeek V3.1
            self.providers[AIProvider.DEEPSEEK] = AIProviderConfig(
                name="DeepSeek V3.1",
                api_key=os.getenv('DEEPSEEK_API_KEY', ''),
                base_url="https://openrouter.ai/api/v1",
                model="deepseek/deepseek-chat-v3.1:free",
                max_tokens=4000,
                temperature=0.7,
                timeout=30,
                rate_limit=60,
                priority=1,
                enabled=bool(os.getenv('DEEPSEEK_API_KEY'))
            )

            # GLM 4.5 Air
            self.providers[AIProvider.GLM] = AIProviderConfig(
                name="GLM 4.5 Air",
                api_key=os.getenv('GLM_API_KEY', ''),
                base_url="https://openrouter.ai/api/v1",
                model="z-ai/glm-4.5-air:free",
                max_tokens=4000,
                temperature=0.7,
                timeout=30,
                rate_limit=60,
                priority=2,
                enabled=bool(os.getenv('GLM_API_KEY'))
            )

            # Grok 4 Fast
            self.providers[AIProvider.GROK] = AIProviderConfig(
                name="Grok 4 Fast",
                api_key=os.getenv('GROK_API_KEY', ''),
                base_url="https://openrouter.ai/api/v1",
                model="x-ai/grok-4-fast:free",
                max_tokens=4000,
                temperature=0.7,
                timeout=30,
                rate_limit=60,
                priority=3,
                enabled=bool(os.getenv('GROK_API_KEY'))
            )

            # Kimi K2
            self.providers[AIProvider.KIMI] = AIProviderConfig(
                name="Kimi K2",
                api_key=os.getenv('KIMI_API_KEY', ''),
                base_url="https://openrouter.ai/api/v1",
                model="moonshotai/kimi-k2:free",
                max_tokens=4000,
                temperature=0.7,
                timeout=30,
                rate_limit=60,
                priority=4,
                enabled=bool(os.getenv('KIMI_API_KEY'))
            )

            # Qwen3 Coder
            self.providers[AIProvider.QWEN] = AIProviderConfig(
                name="Qwen3 Coder",
                api_key=os.getenv('QWEN_API_KEY', ''),
                base_url="https://openrouter.ai/api/v1",
                model="qwen/qwen3-coder:free",
                max_tokens=4000,
                temperature=0.7,
                timeout=30,
                rate_limit=60,
                priority=5,
                enabled=bool(os.getenv('QWEN_API_KEY'))
            )

            # GPT OSS 120B
            self.providers[AIProvider.GPTOSS] = AIProviderConfig(
                name="GPT OSS 120B",
                api_key=os.getenv('GPTOSS_API_KEY', ''),
                base_url="https://openrouter.ai/api/v1",
                model="openai/gpt-oss-120b:free",
                max_tokens=4000,
                temperature=0.7,
                timeout=30,
                rate_limit=60,
                priority=6,
                enabled=bool(os.getenv('GPTOSS_API_KEY'))
            )

            logger.info(f"Initialized {len([p for p in self.providers.values() if p.enabled])} AI providers")

        except Exception as e:
            logger.error(f"Error initializing AI providers: {e}")
            raise

    def _initialize_stats(self):
        """Initialize provider statistics"""
        for provider in AIProvider:
            self.provider_stats[provider] = {
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'average_response_time': 0.0,
                'last_used': None,
                'consecutive_failures': 0,
                'health_score': 100.0
            }
            self.rate_limiters[provider] = {
                'requests_this_minute': 0,
                'last_reset': time.time()
            }

    async def initialize(self):
        """Initialize the AI service manager"""
        try:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={'User-Agent': 'AMAS-AI-Service/1.0'}
            )
            logger.info("AI Service Manager initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing AI service manager: {e}")
            raise

    async def _check_rate_limit(self, provider: AIProvider) -> bool:
        """Check if provider is within rate limits"""
        now = time.time()
        limiter = self.rate_limiters[provider]
        config = self.providers[provider]

        # Reset counter if minute has passed
        if now - limiter['last_reset'] >= 60:
            limiter['requests_this_minute'] = 0
            limiter['last_reset'] = now

        return limiter['requests_this_minute'] < config.rate_limit

    async def _increment_rate_limit(self, provider: AIProvider):
        """Increment rate limit counter"""
        self.rate_limiters[provider]['requests_this_minute'] += 1

    def _get_available_providers(self) -> List[AIProvider]:
        """Get list of available providers sorted by priority and health"""
        available = []

        for provider in AIProvider:
            config = self.providers[provider]
            stats = self.provider_stats[provider]

            if (config.enabled and
                config.api_key and
                stats['consecutive_failures'] < 3 and
                stats['health_score'] > 20.0):
                available.append(provider)

        # Sort by priority and health score
        available.sort(key=lambda p: (
            self.providers[p].priority,
            -self.provider_stats[p]['health_score']
        ))

        return available

    async def _make_request(self, provider: AIProvider, messages: List[Dict[str, str]],
                          max_tokens: Optional[int] = None, temperature: Optional[float] = None) -> AIResponse:
        """Make request to specific provider"""
        config = self.providers[provider]
        start_time = time.time()

        try:
            # Check rate limit
            if not await self._check_rate_limit(provider):
                raise Exception(f"Rate limit exceeded for {provider.value}")

            # Prepare request
            payload = {
                "model": config.model,
                "messages": messages,
                "max_tokens": max_tokens or config.max_tokens,
                "temperature": temperature or config.temperature,
                "stream": False
            }

            headers = {
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System",
                "X-Title": "AMAS Intelligence System"
            }

            # Make request
            async with self.session.post(
                f"{config.base_url}/chat/completions",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=config.timeout)
            ) as response:

                await self._increment_rate_limit(provider)

                if response.status == 200:
                    data = await response.json()
                    content = data['choices'][0]['message']['content']
                    tokens_used = data.get('usage', {}).get('total_tokens', 0)

                    response_time = time.time() - start_time

                    # Update stats
                    self._update_provider_stats(provider, True, response_time)

                    return AIResponse(
                        content=content,
                        provider=provider.value,
                        model=config.model,
                        tokens_used=tokens_used,
                        response_time=response_time,
                        timestamp=datetime.now(),
                        success=True
                    )
                else:
                    error_text = await response.text()
                    raise Exception(f"HTTP {response.status}: {error_text}")

        except Exception as e:
            response_time = time.time() - start_time
            self._update_provider_stats(provider, False, response_time)

            return AIResponse(
                content="",
                provider=provider.value,
                model=config.model,
                tokens_used=0,
                response_time=response_time,
                timestamp=datetime.now(),
                success=False,
                error=str(e)
            )

    def _update_provider_stats(self, provider: AIProvider, success: bool, response_time: float):
        """Update provider statistics"""
        stats = self.provider_stats[provider]

        stats['total_requests'] += 1
        stats['last_used'] = datetime.now()

        if success:
            stats['successful_requests'] += 1
            stats['consecutive_failures'] = 0

            # Update average response time
            if stats['average_response_time'] == 0:
                stats['average_response_time'] = response_time
            else:
                stats['average_response_time'] = (
                    stats['average_response_time'] * 0.9 + response_time * 0.1
                )

            # Improve health score
            stats['health_score'] = min(100.0, stats['health_score'] + 5.0)
        else:
            stats['failed_requests'] += 1
            stats['consecutive_failures'] += 1

            # Decrease health score
            stats['health_score'] = max(0.0, stats['health_score'] - 10.0)

    async def generate_response(self, prompt: str, max_tokens: Optional[int] = None,
                              temperature: Optional[float] = None,
                              preferred_provider: Optional[AIProvider] = None) -> AIResponse:
        """Generate response using best available provider"""
        messages = [{"role": "user", "content": prompt}]

        # Get available providers
        available_providers = self._get_available_providers()

        if not available_providers:
            return AIResponse(
                content="",
                provider="none",
                model="none",
                tokens_used=0,
                response_time=0.0,
                timestamp=datetime.now(),
                success=False,
                error="No AI providers available"
            )

        # Use preferred provider if available
        if preferred_provider and preferred_provider in available_providers:
            available_providers.insert(0, preferred_provider)

        # Try providers in order
        last_error = None
        for provider in available_providers:
            try:
                response = await self._make_request(provider, messages, max_tokens, temperature)

                if response.success:
                    logger.info(f"Successfully used {provider.value} for AI request")
                    return response
                else:
                    last_error = response.error
                    logger.warning(f"Provider {provider.value} failed: {response.error}")

            except Exception as e:
                last_error = str(e)
                logger.warning(f"Provider {provider.value} error: {e}")
                continue

        # All providers failed
        return AIResponse(
            content="",
            provider="none",
            model="none",
            tokens_used=0,
            response_time=0.0,
            timestamp=datetime.now(),
            success=False,
            error=f"All providers failed. Last error: {last_error}"
        )

    async def generate_code(self, task_description: str, language: str = "python",
                          context: Optional[str] = None) -> AIResponse:
        """Generate code using specialized coding models"""
        # Prefer coding-specialized models
        coding_prompt = f"""You are an expert {language} developer.

Task: {task_description}

{f"Context: {context}" if context else ""}

Please provide:
1. Complete, production-ready code
2. Proper error handling
3. Documentation/comments
4. Best practices
5. Example usage if applicable

Return only the code with minimal explanation."""

        # Try coding-specialized providers first
        preferred_providers = [AIProvider.QWEN, AIProvider.DEEPSEEK, AIProvider.GLM]

        for provider in preferred_providers:
            if provider in self._get_available_providers():
                response = await self.generate_response(
                    coding_prompt,
                    preferred_provider=provider
                )
                if response.success:
                    return response

        # Fallback to any available provider
        return await self.generate_response(coding_prompt)

    async def analyze_code(self, code: str, language: str = "python") -> AIResponse:
        """Analyze code for improvements, bugs, and best practices"""
        analysis_prompt = f"""Analyze this {language} code for:
1. Potential bugs or issues
2. Performance improvements
3. Security vulnerabilities
4. Code quality and best practices
5. Optimization opportunities
6. Documentation needs

Code:
```{language}
{code}
```

Provide a detailed analysis with specific recommendations."""

        return await self.generate_response(analysis_prompt)

    async def improve_code(self, code: str, language: str = "python",
                         improvement_type: str = "general") -> AIResponse:
        """Improve existing code"""
        improvement_prompt = f"""Improve this {language} code for {improvement_type}:
1. Fix any bugs
2. Optimize performance
3. Improve readability
4. Add proper error handling
5. Follow best practices
6. Add documentation

Original code:
```{language}
{code}
```

Return the improved code with explanations of changes."""

        return await self.generate_response(improvement_prompt)

    async def generate_tests(self, code: str, language: str = "python") -> AIResponse:
        """Generate comprehensive tests for code"""
        test_prompt = f"""Generate comprehensive tests for this {language} code:
1. Unit tests for all functions/methods
2. Edge cases and error conditions
3. Integration tests if applicable
4. Performance tests if relevant
5. Use appropriate testing framework

Code:
```{language}
{code}
```

Return complete test code with setup and teardown."""

        return await self.generate_response(test_prompt)

    def get_provider_stats(self) -> Dict[str, Any]:
        """Get statistics for all providers"""
        stats = {}
        for provider, data in self.provider_stats.items():
            config = self.providers[provider]
            stats[provider.value] = {
                'name': config.name,
                'enabled': config.enabled,
                'priority': config.priority,
                'health_score': data['health_score'],
                'total_requests': data['total_requests'],
                'successful_requests': data['successful_requests'],
                'failed_requests': data['failed_requests'],
                'success_rate': (
                    data['successful_requests'] / data['total_requests'] * 100
                    if data['total_requests'] > 0 else 0
                ),
                'average_response_time': data['average_response_time'],
                'consecutive_failures': data['consecutive_failures'],
                'last_used': data['last_used'].isoformat() if data['last_used'] else None
            }
        return stats

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all providers"""
        health_status = {
            'overall_health': 'healthy',
            'providers': {},
            'timestamp': datetime.now().isoformat()
        }

        for provider in AIProvider:
            config = self.providers[provider]
            stats = self.provider_stats[provider]

            if not config.enabled or not config.api_key:
                health_status['providers'][provider.value] = {
                    'status': 'disabled',
                    'reason': 'Not configured'
                }
                continue

            # Test with simple request
            try:
                test_response = await self.generate_response(
                    "Hello, this is a health check. Respond with 'OK'.",
                    preferred_provider=provider
                )

                if test_response.success:
                    health_status['providers'][provider.value] = {
                        'status': 'healthy',
                        'response_time': test_response.response_time,
                        'health_score': stats['health_score']
                    }
                else:
                    health_status['providers'][provider.value] = {
                        'status': 'unhealthy',
                        'reason': test_response.error,
                        'health_score': stats['health_score']
                    }

            except Exception as e:
                health_status['providers'][provider.value] = {
                    'status': 'unhealthy',
                    'reason': str(e),
                    'health_score': stats['health_score']
                }

        # Determine overall health
        healthy_count = sum(1 for p in health_status['providers'].values()
                          if p['status'] == 'healthy')
        total_enabled = sum(1 for p in self.providers.values() if p.enabled)

        if healthy_count == 0:
            health_status['overall_health'] = 'critical'
        elif healthy_count < total_enabled * 0.5:
            health_status['overall_health'] = 'degraded'

        return health_status

    async def shutdown(self):
        """Shutdown the AI service manager"""
        if self.session:
            await self.session.close()
        logger.info("AI Service Manager shutdown complete")
