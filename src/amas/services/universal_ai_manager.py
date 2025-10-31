from standalone_universal_ai_manager import get_api_key

#!/usr/bin/env python3
"""
Universal AI Manager - Comprehensive fallback system for all 16 AI providers
Ensures maximum reliability and zero workflow failures due to API issues
"""

import asyncio
import logging
import os
import random
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

import aiohttp

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ProviderStatus(Enum):
    """Provider status states"""

    ACTIVE = "active"
    FAILED = "failed"
    TESTING = "testing"
    UNKNOWN = "unknown"
    RATE_LIMITED = "rate_limited"
    THROTTLED = "throttled"


class ProviderType(Enum):
    """Provider API types"""

    OPENAI_COMPATIBLE = "openai_compatible"
    GROQ = "groq"
    CEREBRAS = "cerebras"
    GEMINI = "gemini"
    NVIDIA = "nvidia"
    COHERE = "cohere"
    CHUTES = "chutes"
    CODESTRAL = "codestral"


@dataclass
class ProviderConfig:
    """Configuration for AI provider"""

    name: str
    api_key: str
    base_url: str
    model: str
    provider_type: ProviderType
    priority: int = 10
    timeout: int = 30
    max_retries: int = 3
    max_tokens: int = 4096
    temperature: float = 0.7
    status: ProviderStatus = ProviderStatus.UNKNOWN
    last_used: Optional[datetime] = None
    success_count: int = 0
    failure_count: int = 0
    avg_response_time: float = 0
    rate_limit_until: Optional[datetime] = None
    consecutive_failures: int = 0
    last_error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "name": self.name,
            "api_key_present": bool(self.api_key),
            "base_url": self.base_url,
            "model": self.model,
            "provider_type": self.provider_type.value,
            "priority": self.priority,
            "status": self.status.value,
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "avg_response_time": self.avg_response_time,
            "success_rate": self.get_success_rate(),
            "consecutive_failures": self.consecutive_failures,
            "last_error": self.last_error,
        }

    def get_success_rate(self) -> float:
        """Calculate success rate"""
        total = self.success_count + self.failure_count
        if total == 0:
            return 0.0
        return (self.success_count / total) * 100


class UniversalAIManager:
    """
    Universal AI Manager with comprehensive fallback support
    Supports 16+ AI providers with intelligent routing and error recovery
    """

    def __init__(self):
        """Initialize the Universal AI Manager"""
        self.providers: Dict[str, ProviderConfig] = {}
        self.active_providers: List[str] = []
        self.current_index = 0
        self.global_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_fallbacks": 0,
            "providers_usage": {},
            "average_response_time": 0,
            "total_response_time": 0,
            "last_reset": datetime.now(),
            "uptime": datetime.now(),
        }

        # Initialize all providers
        self._initialize_providers()

    def _initialize_providers(self):
        """Initialize all 16 AI providers"""
        logger.info("🚀 Initializing Universal AI Manager with 16 providers...")

        # 1. DeepSeek
        if get_api_key("DEEPSEEK_API_KEY"):
            self.providers["deepseek"] = ProviderConfig(
                name="DeepSeek V3.1",
                api_key=get_api_key("DEEPSEEK_API_KEY"),
                base_url="https://api.deepseek.com/v1",
                model="deepseek-chat",
                provider_type=ProviderType.OPENAI_COMPATIBLE,
                priority=1,
                max_tokens=8192,
            )

        # 2. GLM
        if get_api_key("GLM_API_KEY"):
            self.providers["glm"] = ProviderConfig(
                name="GLM 4.5 Air",
                api_key=get_api_key("GLM_API_KEY"),
                base_url="https://open.bigmodel.cn/api/paas/v4",
                model="glm-4-flash",
                provider_type=ProviderType.OPENAI_COMPATIBLE,
                priority=2,
                max_tokens=8192,
            )

        # 3. Grok
        if get_api_key("GROK_API_KEY"):
            self.providers["grok"] = ProviderConfig(
                name="xAI Grok Beta",
                api_key=get_api_key("GROK_API_KEY"),
                base_url="https://api.openrouter.ai/v1",
                model="x-ai/grok-beta",
                provider_type=ProviderType.OPENAI_COMPATIBLE,
                priority=3,
                max_tokens=4096,
            )

        # 4. Kimi
        if get_api_key("KIMI_API_KEY"):
            self.providers["kimi"] = ProviderConfig(
                name="MoonshotAI Kimi",
                api_key=get_api_key("KIMI_API_KEY"),
                base_url="https://api.moonshot.cn/v1",
                model="moonshot-v1-8k",
                provider_type=ProviderType.OPENAI_COMPATIBLE,
                priority=4,
                max_tokens=8192,
            )

        # 5. Qwen
        if get_api_key("QWEN_API_KEY"):
            self.providers["qwen"] = ProviderConfig(
                name="Qwen Plus",
                api_key=get_api_key("QWEN_API_KEY"),
                base_url="https://dashscope.aliyuncs.com/api/v1",
                model="qwen-plus",
                provider_type=ProviderType.OPENAI_COMPATIBLE,
                priority=5,
                max_tokens=8192,
            )

        # 6. GPT OSS
        if get_api_key("GPTOSS_API_KEY"):
            self.providers["gptoss"] = ProviderConfig(
                name="GPT OSS",
                api_key=get_api_key("GPTOSS_API_KEY"),
                base_url="https://api.openrouter.ai/v1",
                model="openai/gpt-4o",
                provider_type=ProviderType.OPENAI_COMPATIBLE,
                priority=6,
                max_tokens=4096,
            )

        # 7. Groq AI (primary)
        if get_api_key("GROQAI_API_KEY"):
            self.providers["groq"] = ProviderConfig(
                name="Groq AI",
                api_key=get_api_key("GROQAI_API_KEY"),
                base_url="https://api.groq.com/openai/v1",
                model="llama-3.3-70b-versatile",
                provider_type=ProviderType.GROQ,
                priority=7,
                max_tokens=8192,
            )

        # 8. Cerebras
        if get_api_key("CEREBRAS_API_KEY"):
            self.providers["cerebras"] = ProviderConfig(
                name="Cerebras AI",
                api_key=get_api_key("CEREBRAS_API_KEY"),
                base_url="https://api.cerebras.ai/v1",
                model="llama3.1-8b",
                provider_type=ProviderType.CEREBRAS,
                priority=8,
                max_tokens=8192,
            )

        # 9. Gemini AI (primary)
        if get_api_key("GEMINIAI_API_KEY"):
            self.providers["gemini"] = ProviderConfig(
                name="Gemini AI",
                api_key=get_api_key("GEMINIAI_API_KEY"),
                base_url="https://generativelanguage.googleapis.com/v1beta",
                model="gemini-2.0-flash",
                provider_type=ProviderType.GEMINI,
                priority=9,
                max_tokens=8192,
            )

        # 10. Codestral
        if get_api_key("CODESTRAL_API_KEY"):
            self.providers["codestral"] = ProviderConfig(
                name="Codestral",
                api_key=get_api_key("CODESTRAL_API_KEY"),
                base_url="https://codestral.mistral.ai/v1",
                model="codestral-latest",
                provider_type=ProviderType.CODESTRAL,
                priority=10,
                max_tokens=4096,
            )

        # 11. NVIDIA
        if get_api_key("NVIDIA_API_KEY"):
            self.providers["nvidia"] = ProviderConfig(
                name="NVIDIA AI",
                api_key=get_api_key("NVIDIA_API_KEY"),
                base_url="https://integrate.api.nvidia.com/v1",
                model="deepseek-ai/deepseek-r1",
                provider_type=ProviderType.NVIDIA,
                priority=11,
                max_tokens=4096,
            )

        # 12. Gemini 2 (secondary)
        if get_api_key("GEMINI2_API_KEY"):
            self.providers["gemini2"] = ProviderConfig(
                name="Gemini 2",
                api_key=get_api_key("GEMINI2_API_KEY"),
                base_url="https://generativelanguage.googleapis.com/v1beta",
                model="gemini-2.0-flash",
                provider_type=ProviderType.GEMINI,
                priority=12,
                max_tokens=8192,
            )

        # 13. Groq 2 (secondary)
        if get_api_key("GROQ2_API_KEY"):
            self.providers["groq2"] = ProviderConfig(
                name="Groq 2",
                api_key=get_api_key("GROQ2_API_KEY"),
                base_url="https://api.groq.com/openai/v1",
                model="llama-3.3-70b-versatile",
                provider_type=ProviderType.GROQ,
                priority=13,
                max_tokens=8192,
            )

        # 14. Cohere
        if get_api_key("COHERE_API_KEY"):
            self.providers["cohere"] = ProviderConfig(
                name="Cohere",
                api_key=get_api_key("COHERE_API_KEY"),
                base_url="https://api.cohere.ai/v1",
                model="command-r-plus",
                provider_type=ProviderType.COHERE,
                priority=14,
                max_tokens=4096,
            )

        # 15. Chutes AI
        if get_api_key("CHUTES_API_KEY"):
            self.providers["chutes"] = ProviderConfig(
                name="Chutes AI",
                api_key=get_api_key("CHUTES_API_KEY"),
                base_url="https://llm.chutes.ai/v1",
                model="zai-org/GLM-4.5-Air",
                provider_type=ProviderType.CHUTES,
                priority=15,
                max_tokens=1024,
            )

        # Get active providers
        self.active_providers = [
            pid
            for pid, config in self.providers.items()
            if config.api_key and config.api_key.strip()
        ]

        # Sort by priority
        self.active_providers.sort(key=lambda x: self.providers[x].priority)

        logger.info(
            f"✅ Initialized {len(self.active_providers)}/{len(self.providers)} providers"
        )
        for pid in self.active_providers:
            config = self.providers[pid]
            logger.info(
                f"  [{config.priority}] {config.name} ({config.provider_type.value})"
            )

        if not self.active_providers:
            logger.error(
                "❌ No active AI providers found! Please set at least one API key."
            )
            raise Exception("No active AI providers configured")

    async def _make_openai_request(
        self, provider_id: str, messages: List[Dict[str, str]], **kwargs
    ) -> Dict[str, Any]:
        """Make request to OpenAI-compatible providers"""
        config = self.providers[provider_id]
        start_time = time.time()

        try:
            headers = {
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json",
            }

            # Add provider-specific headers
            if "openrouter.ai" in config.base_url:
                headers["HTTP-Referer"] = "https://github.com/your-repo"
                headers["X-Title"] = "AMAS Universal AI Manager"

            payload = {
                "model": config.model,
                "messages": messages,
                "max_tokens": kwargs.get("max_tokens", config.max_tokens),
                "temperature": kwargs.get("temperature", config.temperature),
                "stream": False,
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{config.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=config.timeout),
                ) as response:
                    response_time = time.time() - start_time

                    if response.status == 200:
                        result = await response.json()
                        content = (
                            result.get("choices", [{}])[0]
                            .get("message", {})
                            .get("content", "")
                        )

                        return {
                            "success": True,
                            "content": content,
                            "response_time": response_time,
                            "provider": provider_id,
                            "provider_name": config.name,
                            "tokens_used": result.get("usage", {}).get(
                                "total_tokens", 0
                            ),
                            "raw_response": result,
                        }
                    elif response.status == 429:
                        config.rate_limit_until = datetime.now() + timedelta(minutes=5)
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"Rate limited: {error_text}",
                            "response_time": response_time,
                            "provider": provider_id,
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text}",
                            "response_time": response_time,
                            "provider": provider_id,
                        }

        except Exception as e:
            response_time = time.time() - start_time
            return {
                "success": False,
                "error": str(e),
                "response_time": response_time,
                "provider": provider_id,
            }

    async def _make_gemini_request(
        self, provider_id: str, messages: List[Dict[str, str]], **kwargs
    ) -> Dict[str, Any]:
        """Make request to Gemini providers"""
        config = self.providers[provider_id]
        start_time = time.time()

        try:
            # Convert messages to Gemini format
            content = messages[-1]["content"] if messages else "Hello"

            headers = {
                "Content-Type": "application/json",
                "X-goog-api-key": config.api_key,
            }

            payload = {"contents": [{"parts": [{"text": content}]}]}

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{config.base_url}/models/{config.model}:generateContent",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=config.timeout),
                ) as response:
                    response_time = time.time() - start_time

                    if response.status == 200:
                        result = await response.json()
                        content = (
                            result.get("candidates", [{}])[0]
                            .get("content", {})
                            .get("parts", [{}])[0]
                            .get("text", "")
                        )

                        return {
                            "success": True,
                            "content": content,
                            "response_time": response_time,
                            "provider": provider_id,
                            "provider_name": config.name,
                            "tokens_used": 0,
                            "raw_response": result,
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text}",
                            "response_time": response_time,
                            "provider": provider_id,
                        }

        except Exception as e:
            response_time = time.time() - start_time
            return {
                "success": False,
                "error": str(e),
                "response_time": response_time,
                "provider": provider_id,
            }

    async def _make_cohere_request(
        self, provider_id: str, messages: List[Dict[str, str]], **kwargs
    ) -> Dict[str, Any]:
        """Make request to Cohere"""
        config = self.providers[provider_id]
        start_time = time.time()

        try:
            headers = {
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json",
            }

            # Convert messages to Cohere format
            user_message = messages[-1]["content"] if messages else "Hello"

            payload = {"model": config.model, "message": user_message}

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{config.base_url}/chat",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=config.timeout),
                ) as response:
                    response_time = time.time() - start_time

                    if response.status == 200:
                        result = await response.json()
                        content = result.get("text", "")

                        return {
                            "success": True,
                            "content": content,
                            "response_time": response_time,
                            "provider": provider_id,
                            "provider_name": config.name,
                            "tokens_used": 0,
                            "raw_response": result,
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text}",
                            "response_time": response_time,
                            "provider": provider_id,
                        }

        except Exception as e:
            response_time = time.time() - start_time
            return {
                "success": False,
                "error": str(e),
                "response_time": response_time,
                "provider": provider_id,
            }

    async def _make_request(
        self, provider_id: str, messages: List[Dict[str, str]], **kwargs
    ) -> Dict[str, Any]:
        """Make request to any provider"""
        config = self.providers[provider_id]

        # Route to appropriate handler based on provider type
        if config.provider_type in [
            ProviderType.OPENAI_COMPATIBLE,
            ProviderType.GROQ,
            ProviderType.CEREBRAS,
            ProviderType.NVIDIA,
            ProviderType.CODESTRAL,
            ProviderType.CHUTES,
        ]:
            return await self._make_openai_request(provider_id, messages, **kwargs)
        elif config.provider_type == ProviderType.GEMINI:
            return await self._make_gemini_request(provider_id, messages, **kwargs)
        elif config.provider_type == ProviderType.COHERE:
            return await self._make_cohere_request(provider_id, messages, **kwargs)
        else:
            return {
                "success": False,
                "error": f"Unsupported provider type: {config.provider_type}",
                "provider": provider_id,
            }

    def _is_provider_available(self, provider_id: str) -> bool:
        """Check if provider is currently available"""
        config = self.providers[provider_id]

        # Check rate limiting
        if config.rate_limit_until and datetime.now() < config.rate_limit_until:
            return False

        # Check consecutive failures (circuit breaker)
        if config.consecutive_failures >= 5:
            # Allow retry after 10 minutes
            if config.last_used and (datetime.now() - config.last_used).seconds > 600:
                config.consecutive_failures = 0
            else:
                return False

        return True

    def _select_next_provider(self, strategy: str = "intelligent") -> Optional[str]:
        """Select next provider using specified strategy"""
        available = [p for p in self.active_providers if self._is_provider_available(p)]

        if not available:
            return None

        if strategy == "priority":
            # Use priority order (already sorted)
            return available[0]

        elif strategy == "round_robin":
            # Round robin through all providers
            provider = available[self.current_index % len(available)]
            self.current_index += 1
            return provider

        elif strategy == "intelligent":
            # Weighted selection based on success rate and response time
            weights = []
            for pid in available:
                config = self.providers[pid]
                success_rate = (
                    config.get_success_rate() / 100.0
                    if config.get_success_rate() > 0
                    else 0.5
                )

                # Faster response time = higher weight
                speed_factor = (
                    1.0 / (config.avg_response_time + 0.1)
                    if config.avg_response_time > 0
                    else 1.0
                )

                # Combined weight
                weight = (success_rate * 0.7) + (speed_factor * 0.3)
                weights.append(weight)

            # Normalize weights
            total_weight = sum(weights)
            if total_weight > 0:
                weights = [w / total_weight for w in weights]
            else:
                weights = [1.0 / len(weights)] * len(weights)

            return random.choices(available, weights=weights)[0]

        elif strategy == "fastest":
            # Select fastest provider
            available_configs = [(p, self.providers[p]) for p in available]
            available_configs.sort(
                key=lambda x: (
                    x[1].avg_response_time if x[1].avg_response_time > 0 else 999
                )
            )
            return available_configs[0][0] if available_configs else None

        else:
            return available[0]

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        strategy: str = "intelligent",
        max_attempts: Optional[int] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Generate AI response with comprehensive fallback

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            strategy: Selection strategy ('priority', 'round_robin', 'intelligent', 'fastest')
            max_attempts: Maximum number of providers to try (None = try all)
            **kwargs: Additional parameters (max_tokens, temperature, etc.)

        Returns:
            Response dictionary with success status and content
        """
        self.global_stats["total_requests"] += 1

        # Prepare messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Determine max attempts
        if max_attempts is None:
            max_attempts = len(self.active_providers)

        # Try providers with fallback
        for attempt in range(min(max_attempts, len(self.active_providers))):
            provider_id = self._select_next_provider(strategy)

            if not provider_id:
                logger.warning(f"No available providers (attempt {attempt + 1})")
                continue

            config = self.providers[provider_id]
            logger.info(
                f"🤖 Attempting with {config.name} (attempt {attempt + 1}/{max_attempts})"
            )

            try:
                result = await self._make_request(provider_id, messages, **kwargs)

                if result["success"]:
                    # Update success stats
                    config.success_count += 1
                    config.consecutive_failures = 0
                    config.last_used = datetime.now()
                    config.status = ProviderStatus.ACTIVE

                    # Update average response time
                    if config.avg_response_time == 0:
                        config.avg_response_time = result["response_time"]
                    else:
                        config.avg_response_time = (
                            config.avg_response_time + result["response_time"]
                        ) / 2

                    # Update global stats
                    self.global_stats["successful_requests"] += 1
                    self.global_stats["total_response_time"] += result["response_time"]
                    self.global_stats["providers_usage"][provider_id] = (
                        self.global_stats["providers_usage"].get(provider_id, 0) + 1
                    )

                    if self.global_stats["successful_requests"] > 0:
                        self.global_stats["average_response_time"] = (
                            self.global_stats["total_response_time"]
                            / self.global_stats["successful_requests"]
                        )

                    if attempt > 0:
                        self.global_stats["total_fallbacks"] += 1

                    logger.info(
                        f"✅ Success with {config.name} in {result['response_time']:.2f}s"
                    )
                    return result

                else:
                    # Update failure stats
                    config.failure_count += 1
                    config.consecutive_failures += 1
                    config.last_error = result.get("error", "Unknown error")
                    config.status = ProviderStatus.FAILED

                    logger.warning(
                        f"❌ {config.name} failed: {result.get('error', 'Unknown error')}"
                    )

            except Exception as e:
                config.failure_count += 1
                config.consecutive_failures += 1
                config.last_error = str(e)
                config.status = ProviderStatus.FAILED
                logger.error(f"❌ Exception with {config.name}: {e}")

        # All providers failed
        self.global_stats["failed_requests"] += 1
        logger.error("❌ ALL AI PROVIDERS FAILED!")

        return {
            "success": False,
            "error": "All AI providers failed",
            "provider": "none",
            "provider_name": "All Providers Failed",
            "attempts": attempt + 1,
            "stats": self.get_stats(),
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics"""
        success_rate = 0
        if self.global_stats["total_requests"] > 0:
            success_rate = (
                self.global_stats["successful_requests"]
                / self.global_stats["total_requests"]
            ) * 100

        uptime = (datetime.now() - self.global_stats["uptime"]).total_seconds()

        return {
            "total_providers": len(self.providers),
            "active_providers": len(self.active_providers),
            "total_requests": self.global_stats["total_requests"],
            "successful_requests": self.global_stats["successful_requests"],
            "failed_requests": self.global_stats["failed_requests"],
            "success_rate": f"{success_rate:.1f}%",
            "total_fallbacks": self.global_stats["total_fallbacks"],
            "average_response_time": f"{self.global_stats['average_response_time']:.2f}s",
            "providers_usage": self.global_stats["providers_usage"],
            "uptime_seconds": uptime,
            "last_reset": self.global_stats["last_reset"].isoformat(),
        }

    def get_provider_health(self) -> Dict[str, Any]:
        """Get detailed health status of all providers"""
        health = {}

        for provider_id, config in self.providers.items():
            is_available = self._is_provider_available(provider_id)

            health[provider_id] = {
                "name": config.name,
                "priority": config.priority,
                "status": config.status.value,
                "available": is_available,
                "success_count": config.success_count,
                "failure_count": config.failure_count,
                "success_rate": f"{config.get_success_rate():.1f}%",
                "avg_response_time": f"{config.avg_response_time:.2f}s",
                "consecutive_failures": config.consecutive_failures,
                "last_used": config.last_used.isoformat() if config.last_used else None,
                "last_error": config.last_error,
                "rate_limited": (
                    config.rate_limit_until.isoformat()
                    if config.rate_limit_until
                    else None
                ),
            }

        return health

    def reset_stats(self):
        """Reset all statistics"""
        self.global_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_fallbacks": 0,
            "providers_usage": {},
            "average_response_time": 0,
            "total_response_time": 0,
            "last_reset": datetime.now(),
            "uptime": self.global_stats["uptime"],
        }

        for config in self.providers.values():
            config.success_count = 0
            config.failure_count = 0
            config.consecutive_failures = 0
            config.avg_response_time = 0
            config.last_error = None

        logger.info("📊 Statistics reset")

    def get_config_summary(self) -> str:
        """Get human-readable configuration summary"""
        lines = [
            "=" * 80,
            "🤖 UNIVERSAL AI MANAGER - CONFIGURATION SUMMARY",
            "=" * 80,
            f"Total Providers: {len(self.providers)}",
            f"Active Providers: {len(self.active_providers)}",
            "",
            "ACTIVE PROVIDERS (in priority order):",
            "",
        ]

        for pid in self.active_providers:
            config = self.providers[pid]
            lines.append(
                f"  [{config.priority:2d}] {config.name:25s} | {config.model:35s} | {config.provider_type.value}"
            )

        lines.extend(["", "INACTIVE PROVIDERS:", ""])

        inactive = [
            pid for pid in self.providers.keys() if pid not in self.active_providers
        ]
        if inactive:
            for pid in inactive:
                config = self.providers[pid]
                lines.append(f"  ❌ {config.name} (API key not configured)")
        else:
            lines.append("  ✅ All providers configured!")

        lines.append("=" * 80)

        return "\n".join(lines)


# Global instance
_universal_ai_manager: Optional[UniversalAIManager] = None


def get_universal_ai_manager() -> UniversalAIManager:
    """Get or create the global Universal AI Manager instance"""
    global _universal_ai_manager
    if _universal_ai_manager is None:
        _universal_ai_manager = UniversalAIManager()
    return _universal_ai_manager


async def generate_ai_response(
    prompt: str,
    system_prompt: Optional[str] = None,
    strategy: str = "intelligent",
    **kwargs,
) -> Dict[str, Any]:
    """
    Convenience function to generate AI response

    Args:
        prompt: User prompt
        system_prompt: Optional system prompt
        strategy: Selection strategy ('priority', 'round_robin', 'intelligent', 'fastest')
        **kwargs: Additional parameters

    Returns:
        Response dictionary
    """
    manager = get_universal_ai_manager()
    return await manager.generate(prompt, system_prompt, strategy, **kwargs)


# Test function
async def test_universal_ai_manager():
    """Test the Universal AI Manager"""
    print("\n" + "=" * 80)
    print("🧪 TESTING UNIVERSAL AI MANAGER")
    print("=" * 80 + "\n")

    manager = get_universal_ai_manager()

    # Show configuration
    print(manager.get_config_summary())
    print()

    # Test 1: Simple generation
    print("📝 Test 1: Simple generation with intelligent strategy...")
    result = await manager.generate(
        "Say 'Hello from Universal AI Manager!' and nothing else.",
        strategy="intelligent",
    )

    if result["success"]:
        print("✅ Success!")
        print(f"   Provider: {result['provider_name']}")
        print(f"   Response: {result['content'][:100]}...")
        print(f"   Time: {result['response_time']:.2f}s")
    else:
        print(f"❌ Failed: {result['error']}")
    print()

    # Test 2: Priority strategy
    print("📝 Test 2: Generation with priority strategy...")
    result = await manager.generate(
        "What is 2+2? Answer with just the number.", strategy="priority"
    )

    if result["success"]:
        print("✅ Success!")
        print(f"   Provider: {result['provider_name']}")
        print(f"   Response: {result['content']}")
    print()

    # Test 3: Fastest strategy
    print("📝 Test 3: Generation with fastest strategy...")
    result = await manager.generate(
        "Say 'Speed test' and nothing else.", strategy="fastest"
    )

    if result["success"]:
        print("✅ Success!")
        print(f"   Provider: {result['provider_name']}")
        print(f"   Time: {result['response_time']:.2f}s")
    print()

    # Show stats
    print("=" * 80)
    print("📊 STATISTICS")
    print("=" * 80)
    stats = manager.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    print()

    # Show provider health
    print("=" * 80)
    print("🏥 PROVIDER HEALTH")
    print("=" * 80)
    health = manager.get_provider_health()
    for provider_id, info in health.items():
        status_emoji = "✅" if info["available"] else "❌"
        print(
            f"{status_emoji} {info['name']:25s} | Success Rate: {info['success_rate']:6s} | Avg Time: {info['avg_response_time']:8s} | Status: {info['status']}"
        )
    print()


if __name__ == "__main__":
    asyncio.run(test_universal_ai_manager())
