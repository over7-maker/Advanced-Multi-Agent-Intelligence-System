from standalone_universal_ai_manager import get_api_key

#!/usr/bin/env python3
"""
AMAS AI API Manager - Comprehensive Multi-API Fallback System

This module provides a robust, intelligent API manager that handles multiple AI providers
with automatic fallback, health monitoring, and performance optimization.

Supported APIs:
- Cerebras, Codestral, DeepSeek, GeminiAI, GLM, GPTOSS, Grok, GroqAI, Kimi, NVIDIA, Qwen
- Gemini2, NVIDIA2, Groq2, Cohere, Chutes

Features:
- Automatic failover between APIs
- Health monitoring and performance tracking
- Rate limiting and quota management
- Intelligent API selection based on task type
- Comprehensive error handling and retry logic
"""

import asyncio
import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

import aiohttp
import httpx
from openai import AsyncOpenAI
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class APIType(Enum):
    """API provider types"""

    OPENAI_COMPATIBLE = "openai_compatible"
    CEREBRAS = "cerebras"
    COHERE = "cohere"
    CHUTES = "chutes"
    GEMINI = "gemini"
    NVIDIA = "nvidia"


@dataclass
class APIHealth:
    """API health status tracking"""

    is_healthy: bool = True
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    consecutive_failures: int = 0
    total_requests: int = 0
    successful_requests: int = 0
    average_response_time: float = 0.0
    error_rate: float = 0.0
    quota_remaining: Optional[int] = None
    rate_limit_until: Optional[datetime] = None


@dataclass
class APIConfig:
    """API configuration"""

    name: str
    api_key: str
    base_url: str
    model: str
    api_type: APIType
    max_tokens: int = 4000
    temperature: float = 0.7
    timeout: int = 30
    retry_attempts: int = 3
    priority: int = 1  # Lower number = higher priority
    capabilities: List[str] = field(default_factory=list)
    cost_per_token: float = 0.0
    rate_limit_per_minute: int = 60


class AIAPIManager:
    """Comprehensive AI API Manager with intelligent fallback"""

    def __init__(self):
        """Initialize the AI API Manager"""
        self.apis: Dict[str, APIConfig] = {}
        self.health_status: Dict[str, APIHealth] = {}
        self.session: Optional[aiohttp.ClientSession] = None
        self.http_client: Optional[httpx.AsyncClient] = None

        # Initialize all API configurations
        self._setup_apis()

        # Health monitoring
        self.health_check_interval = 300  # 5 minutes
        self.max_consecutive_failures = 3

        logger.info(f"AI API Manager initialized with {len(self.apis)} APIs")

    def _setup_apis(self):
        """Setup all available API configurations"""

        # Cerebras API
        if get_api_key("CEREBRAS_API_KEY"):
            self.apis["cerebras"] = APIConfig(
                name="Cerebras",
                api_key=get_api_key("CEREBRAS_API_KEY"),
                base_url="https://api.cerebras.ai/v1",
                model="qwen-3-235b-a22b-instruct-2507",
                api_type=APIType.CEREBRAS,
                capabilities=["reasoning", "code_generation", "analysis"],
                priority=1,
            )

        # Codestral API
        if get_api_key("CODESTRAL_API_KEY"):
            self.apis["codestral"] = APIConfig(
                name="Codestral",
                api_key=get_api_key("CODESTRAL_API_KEY"),
                base_url="https://codestral.mistral.ai/v1",
                model="codestral-latest",
                api_type=APIType.OPENAI_COMPATIBLE,
                capabilities=[
                    "code_analysis",
                    "vulnerability_detection",
                    "technical_assessment",
                ],
                priority=2,
            )

        # DeepSeek API
        if get_api_key("DEEPSEEK_API_KEY"):
            self.apis["deepseek"] = APIConfig(
                name="DeepSeek",
                api_key=get_api_key("DEEPSEEK_API_KEY"),
                base_url="https://api.deepseek.com/v1",
                model="deepseek-chat",
                api_type=APIType.OPENAI_COMPATIBLE,
                capabilities=["reasoning", "analysis", "code_generation"],
                priority=3,
            )

        # Gemini AI API
        if get_api_key("GEMINIAI_API_KEY"):
            self.apis["gemini"] = APIConfig(
                name="Gemini",
                api_key=get_api_key("GEMINIAI_API_KEY"),
                base_url="https://generativelanguage.googleapis.com/v1beta",
                model="gemini-pro",
                api_type=APIType.GEMINI,
                capabilities=["reasoning", "analysis", "multimodal"],
                priority=4,
            )

        # GLM API (via OpenRouter)
        if get_api_key("GLM_API_KEY"):
            self.apis["glm"] = APIConfig(
                name="GLM",
                api_key=get_api_key("GLM_API_KEY"),
                base_url="https://openrouter.ai/api/v1",
                model="deepseek/deepseek-chat",
                api_type=APIType.OPENAI_COMPATIBLE,
                capabilities=["reasoning", "analysis", "code_generation"],
                priority=5,
            )

        # GPTOSS API
        if get_api_key("GPTOSS_API_KEY"):
            self.apis["gptoss"] = APIConfig(
                name="GPTOSS",
                api_key=get_api_key("GPTOSS_API_KEY"),
                base_url="https://api.openai.com/v1",
                model="gpt-4",
                api_type=APIType.OPENAI_COMPATIBLE,
                capabilities=["reasoning", "analysis", "code_generation"],
                priority=6,
            )

        # Grok API (via OpenRouter)
        if get_api_key("GROK_API_KEY"):
            self.apis["grok"] = APIConfig(
                name="Grok",
                api_key=get_api_key("GROK_API_KEY"),
                base_url="https://openrouter.ai/api/v1",
                model="x-ai/grok-beta",
                api_type=APIType.OPENAI_COMPATIBLE,
                capabilities=["reasoning", "analysis", "synthesis"],
                priority=7,
            )

        # GroqAI API
        if get_api_key("GROQAI_API_KEY"):
            self.apis["groqai"] = APIConfig(
                name="GroqAI",
                api_key=get_api_key("GROQAI_API_KEY"),
                base_url="https://api.groq.com/openai/v1",
                model="llama3-8b-8192",
                api_type=APIType.OPENAI_COMPATIBLE,
                capabilities=["fast_inference", "reasoning", "analysis"],
                priority=8,
            )

        # Kimi API
        if get_api_key("KIMI_API_KEY"):
            self.apis["kimi"] = APIConfig(
                name="Kimi",
                api_key=get_api_key("KIMI_API_KEY"),
                base_url="https://api.moonshot.cn/v1",
                model="moonshot-v1-8k",
                api_type=APIType.OPENAI_COMPATIBLE,
                capabilities=["reasoning", "analysis", "chinese_support"],
                priority=9,
            )

        # NVIDIA API
        if get_api_key("NVIDIA_API_KEY"):
            self.apis["nvidia"] = APIConfig(
                name="NVIDIA",
                api_key=get_api_key("NVIDIA_API_KEY"),
                base_url="https://integrate.api.nvidia.com/v1",
                model="deepseek-ai/deepseek-r1",
                api_type=APIType.NVIDIA,
                capabilities=["reasoning", "code_generation", "analysis"],
                priority=10,
            )

        # Qwen API
        if get_api_key("QWEN_API_KEY"):
            self.apis["qwen"] = APIConfig(
                name="Qwen",
                api_key=get_api_key("QWEN_API_KEY"),
                base_url="https://dashscope.aliyuncs.com/api/v1",
                model="qwen-turbo",
                api_type=APIType.OPENAI_COMPATIBLE,
                capabilities=["reasoning", "analysis", "chinese_support"],
                priority=11,
            )

        # Gemini2 API
        if get_api_key("GEMINI2_API_KEY"):
            self.apis["gemini2"] = APIConfig(
                name="Gemini2",
                api_key=get_api_key("GEMINI2_API_KEY"),
                base_url="https://generativelanguage.googleapis.com/v1beta",
                model="gemini-2.0-flash",
                api_type=APIType.GEMINI,
                capabilities=["reasoning", "analysis", "multimodal"],
                priority=12,
            )

        # NVIDIA2 API
        if get_api_key("NVIDIA_API_KEY"):
            self.apis["nvidia2"] = APIConfig(
                name="NVIDIA2",
                api_key=get_api_key("NVIDIA_API_KEY"),
                base_url="https://integrate.api.nvidia.com/v1",
                model="qwen/qwen2.5-coder-32b-instruct",
                api_type=APIType.NVIDIA,
                capabilities=["code_generation", "analysis", "technical"],
                priority=13,
            )

        # Groq2 API
        if get_api_key("GROQ2_API_KEY"):
            self.apis["groq2"] = APIConfig(
                name="Groq2",
                api_key=get_api_key("GROQ2_API_KEY"),
                base_url="https://api.groq.com/openai/v1",
                model="llama3-70b-8192",
                api_type=APIType.OPENAI_COMPATIBLE,
                capabilities=["fast_inference", "reasoning", "analysis"],
                priority=14,
            )

        # Cohere API
        if get_api_key("COHERE_API_KEY"):
            self.apis["cohere"] = APIConfig(
                name="Cohere",
                api_key=get_api_key("COHERE_API_KEY"),
                base_url="https://api.cohere.ai/v1",
                model="command-a-03-2025",
                api_type=APIType.COHERE,
                capabilities=["reasoning", "analysis", "text_generation"],
                priority=15,
            )

        # Chutes API
        if get_api_key("CHUTES_API_KEY"):
            self.apis["chutes"] = APIConfig(
                name="Chutes",
                api_key=get_api_key("CHUTES_API_KEY"),
                base_url="https://llm.chutes.ai/v1",
                model="zai-org/GLM-4.5-Air",
                api_type=APIType.CHUTES,
                capabilities=["reasoning", "analysis", "code_generation"],
                priority=16,
            )

        # Initialize health status for all APIs
        for api_name in self.apis:
            self.health_status[api_name] = APIHealth()

        logger.info(f"Configured {len(self.apis)} APIs: {list(self.apis.keys())}")

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        self.http_client = httpx.AsyncClient(timeout=30.0)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
        if self.http_client:
            await self.http_client.aclose()

    def get_available_apis(self, task_type: str = None) -> List[str]:
        """Get list of available APIs, optionally filtered by task type"""
        available = []

        for api_name, api_config in self.apis.items():
            health = self.health_status[api_name]

            # Skip if API is unhealthy
            if not health.is_healthy:
                continue

            # Skip if rate limited
            if health.rate_limit_until and health.rate_limit_until > datetime.now():
                continue

            # Filter by task type if specified
            if task_type and task_type not in api_config.capabilities:
                continue

            available.append(api_name)

        # Sort by priority
        available.sort(key=lambda x: self.apis[x].priority)
        return available

    async def _make_openai_request(
        self, api_name: str, messages: List[Dict], **kwargs
    ) -> Dict:
        """Make request to OpenAI-compatible API"""
        api_config = self.apis[api_name]

        client = AsyncOpenAI(base_url=api_config.base_url, api_key=api_config.api_key)

        response = await client.chat.completions.create(
            model=api_config.model,
            messages=messages,
            max_tokens=kwargs.get("max_tokens", api_config.max_tokens),
            temperature=kwargs.get("temperature", api_config.temperature),
            timeout=kwargs.get("timeout", api_config.timeout),
        )

        return {
            "content": response.choices[0].message.content,
            "usage": response.usage.dict() if response.usage else None,
            "model": response.model,
        }

    async def _make_cerebras_request(
        self, api_name: str, messages: List[Dict], **kwargs
    ) -> Dict:
        """Make request to Cerebras API"""
        api_config = self.apis[api_name]

        # Convert messages to Cerebras format
        system_content = ""
        user_content = ""

        for msg in messages:
            if msg["role"] == "system":
                system_content = msg["content"]
            elif msg["role"] == "user":
                user_content = msg["content"]

        payload = {
            "messages": [{"role": "user", "content": user_content}],
            "model": api_config.model,
            "stream": False,
            "max_completion_tokens": kwargs.get("max_tokens", api_config.max_tokens),
            "temperature": kwargs.get("temperature", api_config.temperature),
        }

        if system_content:
            payload["messages"].insert(0, {"role": "system", "content": system_content})

        async with self.http_client.post(
            f"{api_config.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {api_config.api_key}"},
            json=payload,
        ) as response:
            result = await response.json()

            return {
                "content": result["choices"][0]["message"]["content"],
                "usage": result.get("usage"),
                "model": result["model"],
            }

    async def _make_cohere_request(
        self, api_name: str, messages: List[Dict], **kwargs
    ) -> Dict:
        """Make request to Cohere API"""
        api_config = self.apis[api_name]

        # Convert messages to Cohere format
        user_content = ""
        for msg in messages:
            if msg["role"] == "user":
                user_content = msg["content"]
                break

        payload = {
            "model": api_config.model,
            "messages": [{"role": "user", "content": user_content}],
            "max_tokens": kwargs.get("max_tokens", api_config.max_tokens),
            "temperature": kwargs.get("temperature", api_config.temperature),
        }

        async with self.http_client.post(
            f"{api_config.base_url}/chat",
            headers={"Authorization": f"Bearer {api_config.api_key}"},
            json=payload,
        ) as response:
            result = await response.json()

            return {
                "content": result["text"],
                "usage": result.get("meta"),
                "model": api_config.model,
            }

    async def _make_chutes_request(
        self, api_name: str, messages: List[Dict], **kwargs
    ) -> Dict:
        """Make request to Chutes API"""
        api_config = self.apis[api_name]

        payload = {
            "model": api_config.model,
            "messages": messages,
            "stream": False,
            "max_tokens": kwargs.get("max_tokens", api_config.max_tokens),
            "temperature": kwargs.get("temperature", api_config.temperature),
        }

        async with self.http_client.post(
            f"{api_config.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {api_config.api_key}"},
            json=payload,
        ) as response:
            result = await response.json()

            return {
                "content": result["choices"][0]["message"]["content"],
                "usage": result.get("usage"),
                "model": result["model"],
            }

    async def _make_gemini_request(
        self, api_name: str, messages: List[Dict], **kwargs
    ) -> Dict:
        """Make request to Gemini API"""
        api_config = self.apis[api_name]

        # Convert messages to Gemini format
        user_content = ""
        for msg in messages:
            if msg["role"] == "user":
                user_content = msg["content"]
                break

        payload = {
            "contents": [{"parts": [{"text": user_content}]}],
            "generationConfig": {
                "maxOutputTokens": kwargs.get("max_tokens", api_config.max_tokens),
                "temperature": kwargs.get("temperature", api_config.temperature),
            },
        }

        async with self.http_client.post(
            f"{api_config.base_url}/models/{api_config.model}:generateContent",
            headers={"X-goog-api-key": api_config.api_key},
            json=payload,
        ) as response:
            result = await response.json()

            return {
                "content": result["candidates"][0]["content"]["parts"][0]["text"],
                "usage": result.get("usageMetadata"),
                "model": api_config.model,
            }

    async def _make_nvidia_request(
        self, api_name: str, messages: List[Dict], **kwargs
    ) -> Dict:
        """Make request to NVIDIA API"""
        api_config = self.apis[api_name]

        client = AsyncOpenAI(base_url=api_config.base_url, api_key=api_config.api_key)

        response = await client.chat.completions.create(
            model=api_config.model,
            messages=messages,
            max_tokens=kwargs.get("max_tokens", api_config.max_tokens),
            temperature=kwargs.get("temperature", api_config.temperature),
            timeout=kwargs.get("timeout", api_config.timeout),
        )

        return {
            "content": response.choices[0].message.content,
            "usage": response.usage.dict() if response.usage else None,
            "model": response.model,
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(
            (aiohttp.ClientError, httpx.RequestError, asyncio.TimeoutError)
        ),
    )
    async def _call_api(self, api_name: str, messages: List[Dict], **kwargs) -> Dict:
        """Make API call with retry logic"""
        api_config = self.apis[api_name]
        start_time = time.time()

        try:
            if api_config.api_type == APIType.OPENAI_COMPATIBLE:
                result = await self._make_openai_request(api_name, messages, **kwargs)
            elif api_config.api_type == APIType.CEREBRAS:
                result = await self._make_cerebras_request(api_name, messages, **kwargs)
            elif api_config.api_type == APIType.COHERE:
                result = await self._make_cohere_request(api_name, messages, **kwargs)
            elif api_config.api_type == APIType.CHUTES:
                result = await self._make_chutes_request(api_name, messages, **kwargs)
            elif api_config.api_type == APIType.GEMINI:
                result = await self._make_gemini_request(api_name, messages, **kwargs)
            elif api_config.api_type == APIType.NVIDIA:
                result = await self._make_nvidia_request(api_name, messages, **kwargs)
            else:
                raise ValueError(f"Unsupported API type: {api_config.api_type}")

            # Update health status
            response_time = time.time() - start_time
            self._update_health_success(api_name, response_time)

            return result

        except Exception as e:
            self._update_health_failure(api_name, str(e))
            raise

    def _update_health_success(self, api_name: str, response_time: float):
        """Update health status after successful request"""
        health = self.health_status[api_name]
        health.last_success = datetime.now()
        health.consecutive_failures = 0
        health.total_requests += 1
        health.successful_requests += 1

        # Update average response time
        if health.average_response_time == 0:
            health.average_response_time = response_time
        else:
            health.average_response_time = (
                health.average_response_time + response_time
            ) / 2

        # Update error rate
        health.error_rate = 1 - (health.successful_requests / health.total_requests)

        # Mark as healthy if it was unhealthy
        if not health.is_healthy and health.consecutive_failures == 0:
            health.is_healthy = True
            logger.info(f"API {api_name} is now healthy")

    def _update_health_failure(self, api_name: str, error: str):
        """Update health status after failed request"""
        health = self.health_status[api_name]
        health.last_failure = datetime.now()
        health.consecutive_failures += 1
        health.total_requests += 1

        # Update error rate
        health.error_rate = 1 - (health.successful_requests / health.total_requests)

        # Mark as unhealthy if too many consecutive failures
        if health.consecutive_failures >= self.max_consecutive_failures:
            health.is_healthy = False
            logger.warning(
                f"API {api_name} marked as unhealthy after {health.consecutive_failures} consecutive failures"
            )

        # Check for rate limiting
        if "rate limit" in error.lower() or "quota" in error.lower():
            health.rate_limit_until = datetime.now() + timedelta(minutes=5)
            logger.warning(
                f"API {api_name} rate limited until {health.rate_limit_until}"
            )

    async def generate_response(
        self,
        prompt: str,
        system_prompt: str = None,
        task_type: str = None,
        max_tokens: int = None,
        temperature: float = None,
        timeout: int = None,
    ) -> Dict[str, Any]:
        """
        Generate response using available APIs with automatic fallback

        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            task_type: Type of task for API selection
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation
            timeout: Request timeout

        Returns:
            Dict containing response, metadata, and API used
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Get available APIs
        available_apis = self.get_available_apis(task_type)

        if not available_apis:
            raise Exception("No healthy APIs available")

        # Try each API in order of priority
        last_error = None

        for api_name in available_apis:
            try:
                logger.info(f"Attempting API: {api_name}")

                result = await self._call_api(
                    api_name,
                    messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    timeout=timeout,
                )

                # Add metadata
                result["api_used"] = api_name
                result["api_config"] = self.apis[api_name].name
                result["timestamp"] = datetime.now().isoformat()

                logger.info(f"Successfully used API: {api_name}")
                return result

            except Exception as e:
                last_error = e
                logger.warning(f"API {api_name} failed: {e}")
                continue

        # If all APIs failed
        raise Exception(f"All APIs failed. Last error: {last_error}")

    async def generate_streaming_response(
        self,
        prompt: str,
        system_prompt: str = None,
        task_type: str = None,
        max_tokens: int = None,
        temperature: float = None,
    ):
        """
        Generate streaming response using available APIs

        Note: Not all APIs support streaming, so this will fallback to non-streaming
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        available_apis = self.get_available_apis(task_type)

        if not available_apis:
            raise Exception("No healthy APIs available")

        for api_name in available_apis:
            try:
                # For now, we'll use non-streaming and yield the result
                # In a full implementation, you'd implement streaming for each API type
                result = await self._call_api(
                    api_name, messages, max_tokens=max_tokens, temperature=temperature
                )

                # Yield the complete response
                yield {
                    "content": result["content"],
                    "api_used": api_name,
                    "api_config": self.apis[api_name].name,
                    "timestamp": datetime.now().isoformat(),
                }
                return

            except Exception as e:
                logger.warning(f"API {api_name} failed: {e}")
                continue

        raise Exception("All APIs failed for streaming request")

    def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status of all APIs"""
        status = {
            "total_apis": len(self.apis),
            "healthy_apis": 0,
            "unhealthy_apis": 0,
            "rate_limited_apis": 0,
            "apis": {},
        }

        for api_name, health in self.health_status.items():
            api_status = {
                "name": self.apis[api_name].name,
                "is_healthy": health.is_healthy,
                "consecutive_failures": health.consecutive_failures,
                "total_requests": health.total_requests,
                "successful_requests": health.successful_requests,
                "error_rate": health.error_rate,
                "average_response_time": health.average_response_time,
                "last_success": (
                    health.last_success.isoformat() if health.last_success else None
                ),
                "last_failure": (
                    health.last_failure.isoformat() if health.last_failure else None
                ),
                "rate_limited_until": (
                    health.rate_limit_until.isoformat()
                    if health.rate_limit_until
                    else None
                ),
            }

            status["apis"][api_name] = api_status

            if health.is_healthy:
                status["healthy_apis"] += 1
            else:
                status["unhealthy_apis"] += 1

            if health.rate_limit_until and health.rate_limit_until > datetime.now():
                status["rate_limited_apis"] += 1

        return status

    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check on all APIs"""
        health_results = {}

        for api_name in self.apis:
            try:
                # Simple test request
                result = await self.generate_response(
                    "Hello, this is a health check. Please respond with 'OK'.",
                    max_tokens=10,
                    temperature=0.1,
                )

                health_results[api_name] = {
                    "status": "healthy",
                    "response_time": result.get("response_time", 0),
                    "timestamp": datetime.now().isoformat(),
                }

            except Exception as e:
                health_results[api_name] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }

        return health_results

    def reset_api_health(self, api_name: str = None):
        """Reset health status for specific API or all APIs"""
        if api_name:
            if api_name in self.health_status:
                self.health_status[api_name] = APIHealth()
                logger.info(f"Reset health status for API: {api_name}")
        else:
            for api_name in self.health_status:
                self.health_status[api_name] = APIHealth()
            logger.info("Reset health status for all APIs")


# Global instance for easy access
ai_api_manager = AIAPIManager()


async def get_ai_response(
    prompt: str, system_prompt: str = None, task_type: str = None, **kwargs
) -> Dict[str, Any]:
    """
    Convenience function to get AI response using the global API manager

    Args:
        prompt: User prompt
        system_prompt: System prompt (optional)
        task_type: Type of task for API selection
        **kwargs: Additional parameters (max_tokens, temperature, timeout)

    Returns:
        Dict containing response and metadata
    """
    async with ai_api_manager:
        return await ai_api_manager.generate_response(
            prompt=prompt, system_prompt=system_prompt, task_type=task_type, **kwargs
        )


# Example usage and testing
async def main():
    """Example usage of the AI API Manager"""
    print("🚀 AMAS AI API Manager - Testing Multi-API Fallback")
    print("=" * 60)

    # Test basic functionality
    try:
        async with ai_api_manager:
            # Test health status
            health = ai_api_manager.get_health_status()
            print("📊 Health Status:")
            print(f"  Total APIs: {health['total_apis']}")
            print(f"  Healthy APIs: {health['healthy_apis']}")
            print(f"  Unhealthy APIs: {health['unhealthy_apis']}")
            print(f"  Rate Limited APIs: {health['rate_limited_apis']}")

            # Test API call
            print("\n🤖 Testing API Call...")
            result = await ai_api_manager.generate_response(
                prompt="Explain artificial intelligence in one sentence.",
                system_prompt="You are a helpful AI assistant.",
                max_tokens=100,
                temperature=0.7,
            )

            print(f"✅ Success! Used API: {result['api_used']}")
            print(f"📝 Response: {result['content']}")
            print(f"🔧 Model: {result['model']}")
            print(f"⏰ Timestamp: {result['timestamp']}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
