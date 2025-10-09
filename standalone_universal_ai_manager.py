#!/usr/bin/env python3
"""
Standalone Universal AI Manager - No dependencies on AMAS package
Can be used independently in any project
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
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ProviderStatus(Enum):
    """Provider status states"""

    ACTIVE = "active"
    FAILED = "failed"
    TESTING = "testing"
    UNKNOWN = "unknown"
    RATE_LIMITED = "rate_limited"


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

    def get_success_rate(self) -> float:
        """Calculate success rate"""
        total = self.success_count + self.failure_count
        if total == 0:
            return 0.0
        return (self.success_count / total) * 100


class StandaloneUniversalAIManager:
    """
    Standalone Universal AI Manager - No AMAS dependencies
    Supports 16 AI providers with comprehensive fallback
    """

    def __init__(self):
        """Initialize the manager"""
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

        self._initialize_providers()

    def _initialize_providers(self):
        """Initialize all providers"""
        logger.info("🚀 Initializing Standalone Universal AI Manager...")

        # Initialize all 16 providers (same as before)
        if os.getenv("DEEPSEEK_API_KEY"):
            self.providers["deepseek"] = ProviderConfig(
                name="DeepSeek V3.1",
                api_key=os.getenv("DEEPSEEK_API_KEY"),
                base_url="https://api.deepseek.com/v1",
                model="deepseek-chat",
                provider_type=ProviderType.OPENAI_COMPATIBLE,
                priority=1,
                max_tokens=8192,
            )

        if os.getenv("GLM_API_KEY"):
            self.providers["glm"] = ProviderConfig(
                name="GLM 4.5 Air",
                api_key=os.getenv("GLM_API_KEY"),
                base_url="https://open.bigmodel.cn/api/paas/v4",
                model="glm-4-flash",
                provider_type=ProviderType.OPENAI_COMPATIBLE,
                priority=2,
                max_tokens=8192,
            )

        if os.getenv("GROK_API_KEY"):
            self.providers["grok"] = ProviderConfig(
                name="xAI Grok Beta",
                api_key=os.getenv("GROK_API_KEY"),
                base_url="https://api.openrouter.ai/v1",
                model="x-ai/grok-beta",
                provider_type=ProviderType.OPENAI_COMPATIBLE,
                priority=3,
                max_tokens=4096,
            )

        if os.getenv("KIMI_API_KEY"):
            self.providers["kimi"] = ProviderConfig(
                name="MoonshotAI Kimi",
                api_key=os.getenv("KIMI_API_KEY"),
                base_url="https://api.moonshot.cn/v1",
                model="moonshot-v1-8k",
                provider_type=ProviderType.OPENAI_COMPATIBLE,
                priority=4,
                max_tokens=8192,
            )

        if os.getenv("QWEN_API_KEY"):
            self.providers["qwen"] = ProviderConfig(
                name="Qwen Plus",
                api_key=os.getenv("QWEN_API_KEY"),
                base_url="https://dashscope.aliyuncs.com/api/v1",
                model="qwen-plus",
                provider_type=ProviderType.OPENAI_COMPATIBLE,
                priority=5,
                max_tokens=8192,
            )

        if os.getenv("GPTOSS_API_KEY"):
            self.providers["gptoss"] = ProviderConfig(
                name="GPT OSS",
                api_key=os.getenv("GPTOSS_API_KEY"),
                base_url="https://api.openrouter.ai/v1",
                model="openai/gpt-4o",
                provider_type=ProviderType.OPENAI_COMPATIBLE,
                priority=6,
                max_tokens=4096,
            )

        if os.getenv("GROQAI_API_KEY"):
            self.providers["groq"] = ProviderConfig(
                name="Groq AI",
                api_key=os.getenv("GROQAI_API_KEY"),
                base_url="https://api.groq.com/openai/v1",
                model="llama-3.3-70b-versatile",
                provider_type=ProviderType.OPENAI_COMPATIBLE,
                priority=7,
                max_tokens=8192,
            )

        if os.getenv("CEREBRAS_API_KEY"):
            self.providers["cerebras"] = ProviderConfig(
                name="Cerebras AI",
                api_key=os.getenv("CEREBRAS_API_KEY"),
                base_url="https://api.cerebras.ai/v1",
                model="llama3.1-8b",
                provider_type=ProviderType.OPENAI_COMPATIBLE,
                priority=8,
                max_tokens=8192,
            )

        if os.getenv("GEMINIAI_API_KEY"):
            self.providers["gemini"] = ProviderConfig(
                name="Gemini AI",
                api_key=os.getenv("GEMINIAI_API_KEY"),
                base_url="https://generativelanguage.googleapis.com/v1beta",
                model="gemini-2.0-flash",
                provider_type=ProviderType.GEMINI,
                priority=9,
                max_tokens=8192,
            )

        if os.getenv("CODESTRAL_API_KEY"):
            self.providers["codestral"] = ProviderConfig(
                name="Codestral",
                api_key=os.getenv("CODESTRAL_API_KEY"),
                base_url="https://codestral.mistral.ai/v1",
                model="codestral-latest",
                provider_type=ProviderType.OPENAI_COMPATIBLE,
                priority=10,
                max_tokens=4096,
            )

        if os.getenv("NVIDIA_API_KEY"):
            self.providers["nvidia"] = ProviderConfig(
                name="NVIDIA AI",
                api_key=os.getenv("NVIDIA_API_KEY"),
                base_url="https://integrate.api.nvidia.com/v1",
                model="deepseek-ai/deepseek-r1",
                provider_type=ProviderType.OPENAI_COMPATIBLE,
                priority=11,
                max_tokens=4096,
            )

        if os.getenv("GEMINI2_API_KEY"):
            self.providers["gemini2"] = ProviderConfig(
                name="Gemini 2",
                api_key=os.getenv("GEMINI2_API_KEY"),
                base_url="https://generativelanguage.googleapis.com/v1beta",
                model="gemini-2.0-flash",
                provider_type=ProviderType.GEMINI,
                priority=12,
                max_tokens=8192,
            )

        if os.getenv("GROQ2_API_KEY"):
            self.providers["groq2"] = ProviderConfig(
                name="Groq 2",
                api_key=os.getenv("GROQ2_API_KEY"),
                base_url="https://api.groq.com/openai/v1",
                model="llama-3.3-70b-versatile",
                provider_type=ProviderType.OPENAI_COMPATIBLE,
                priority=13,
                max_tokens=8192,
            )

        if os.getenv("COHERE_API_KEY"):
            self.providers["cohere"] = ProviderConfig(
                name="Cohere",
                api_key=os.getenv("COHERE_API_KEY"),
                base_url="https://api.cohere.ai/v2",
                model="command-r-plus",
                provider_type=ProviderType.OPENAI_COMPATIBLE,
                priority=14,
                max_tokens=4096,
            )

        if os.getenv("CHUTES_API_KEY"):
            self.providers["chutes"] = ProviderConfig(
                name="Chutes AI",
                api_key=os.getenv("CHUTES_API_KEY"),
                base_url="https://llm.chutes.ai/v1",
                model="zai-org/GLM-4.5-Air",
                provider_type=ProviderType.OPENAI_COMPATIBLE,
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

        logger.info(f"✅ Initialized {len(self.active_providers)}/15 providers")
        for pid in self.active_providers:
            config = self.providers[pid]
            logger.info(f"  [{config.priority}] {config.name}")

        if not self.active_providers:
            logger.warning("⚠️  No active AI providers found (no API keys configured)")

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

            if "openrouter.ai" in config.base_url:
                headers["HTTP-Referer"] = "https://github.com"
                headers["X-Title"] = "Universal AI Manager"

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
                        }
                    elif response.status == 429:
                        config.rate_limit_until = datetime.now() + timedelta(minutes=5)
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"Rate limited: {error_text[:100]}",
                            "response_time": response_time,
                            "provider": provider_id,
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text[:100]}",
                            "response_time": response_time,
                            "provider": provider_id,
                        }

        except Exception as e:
            response_time = time.time() - start_time
            return {
                "success": False,
                "error": str(e)[:100],
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
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text[:100]}",
                            "response_time": response_time,
                            "provider": provider_id,
                        }

        except Exception as e:
            response_time = time.time() - start_time
            return {
                "success": False,
                "error": str(e)[:100],
                "response_time": response_time,
                "provider": provider_id,
            }

    async def _make_request(
        self, provider_id: str, messages: List[Dict[str, str]], **kwargs
    ) -> Dict[str, Any]:
        """Make request to any provider"""
        config = self.providers[provider_id]

        try:
            if config.provider_type == ProviderType.GEMINI:
                result = await self._make_gemini_request(
                    provider_id, messages, **kwargs
                )
            else:
                result = await self._make_openai_request(
                    provider_id, messages, **kwargs
                )

            # Ensure we always return a valid dictionary
            if not result or not isinstance(result, dict):
                return {
                    "success": False,
                    "error": "Provider returned invalid response",
                    "provider": provider_id,
                    "response_time": 0.0,
                }

            return result
        except Exception as e:
            return {
                "success": False,
                "error": f"Request failed: {str(e)}",
                "provider": provider_id,
                "response_time": 0.0,
            }

    def _is_provider_available(self, provider_id: str) -> bool:
        """Check if provider is available"""
        config = self.providers[provider_id]

        if config.rate_limit_until and datetime.now() < config.rate_limit_until:
            return False

        if config.consecutive_failures >= 5:
            if config.last_used and (datetime.now() - config.last_used).seconds > 600:
                config.consecutive_failures = 0
            else:
                return False

        return True

    def _select_next_provider(self, strategy: str = "intelligent") -> Optional[str]:
        """Select next provider"""
        available = [p for p in self.active_providers if self._is_provider_available(p)]

        if not available:
            return None

        if strategy == "priority":
            return available[0]
        elif strategy == "round_robin":
            provider = available[self.current_index % len(available)]
            self.current_index += 1
            return provider
        elif strategy == "intelligent":
            weights = []
            for pid in available:
                config = self.providers[pid]
                success_rate = (
                    config.get_success_rate() / 100.0
                    if config.get_success_rate() > 0
                    else 0.5
                )
                speed_factor = (
                    1.0 / (config.avg_response_time + 0.1)
                    if config.avg_response_time > 0
                    else 1.0
                )
                weight = (success_rate * 0.7) + (speed_factor * 0.3)
                weights.append(weight)

            total_weight = sum(weights)
            if total_weight > 0:
                weights = [w / total_weight for w in weights]
            else:
                weights = [1.0 / len(weights)] * len(weights)

            return random.choices(available, weights=weights)[0]
        elif strategy == "fastest":
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
        """Generate AI response with comprehensive fallback"""
        self.global_stats["total_requests"] += 1

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        if max_attempts is None:
            max_attempts = len(self.active_providers)

        for attempt in range(min(max_attempts, len(self.active_providers))):
            provider_id = self._select_next_provider(strategy)

            if not provider_id:
                logger.warning(f"No available providers (attempt {attempt + 1})")
                continue

            if provider_id not in self.providers:
                logger.error(f"Selected invalid provider: {provider_id}")
                continue

            config = self.providers[provider_id]
            logger.info(
                f"🤖 Attempting with {config.name} "
                f"(attempt {attempt + 1}/{max_attempts})"
            )

            try:
                result = await self._make_request(provider_id, messages, **kwargs)

                if not result or not isinstance(result, dict):
                    logger.error(f"❌ {config.name} returned invalid result: {result}")
                    config.failure_count += 1
                    config.consecutive_failures += 1
                    config.last_error = "Provider returned invalid result"
                    config.status = ProviderStatus.FAILED
                    continue

                if result.get("success", False):
                    config.success_count += 1
                    config.consecutive_failures = 0
                    config.last_used = datetime.now()
                    config.status = ProviderStatus.ACTIVE

                    if config.avg_response_time == 0:
                        config.avg_response_time = result["response_time"]
                    else:
                        config.avg_response_time = (
                            config.avg_response_time + result["response_time"]
                        ) / 2

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
                        f"✅ Success with {config.name} "
                        f"in {result['response_time']:.2f}s"
                    )
                    return result

                else:
                    config.failure_count += 1
                    config.consecutive_failures += 1
                    config.last_error = result.get("error", "Unknown error")
                    config.status = ProviderStatus.FAILED

                    logger.warning(
                        f"❌ {config.name} failed: "
                        f"{result.get('error', 'Unknown error')}"
                    )

            except Exception as e:
                config.failure_count += 1
                config.consecutive_failures += 1
                config.last_error = str(e)
                config.status = ProviderStatus.FAILED
                logger.error(f"❌ Exception with {config.name}: {e}")

        self.global_stats["failed_requests"] += 1
        logger.error("❌ ALL AI PROVIDERS FAILED!")

        return {
            "success": False,
            "error": "All AI providers failed",
            "provider": "none",
            "provider_name": "All Providers Failed",
            "attempts": min(max_attempts, len(self.active_providers)),
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
        }

    def get_provider_health(self) -> Dict[str, Any]:
        """Get provider health status"""
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
                "last_error": config.last_error,
            }

        return health

    def get_config_summary(self) -> str:
        """Get configuration summary"""
        lines = [
            "=" * 80,
            "🤖 STANDALONE UNIVERSAL AI MANAGER - CONFIGURATION",
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
                f"  [{config.priority:2d}] {config.name:25s} | {config.model:35s}"
            )

        lines.extend(["", "=" * 80])

        return "\n".join(lines)


# Global instance
_manager: Optional[StandaloneUniversalAIManager] = None


def get_manager() -> StandaloneUniversalAIManager:
    """Get or create the global manager instance"""
    global _manager
    if _manager is None:
        _manager = StandaloneUniversalAIManager()
    return _manager


async def generate_ai_response(
    prompt: str,
    system_prompt: Optional[str] = None,
    strategy: str = "intelligent",
    **kwargs,
) -> Dict[str, Any]:
    """Convenience function to generate AI response"""
    manager = get_manager()
    return await manager.generate(prompt, system_prompt, strategy, **kwargs)


# Test function
async def test_manager():
    """Test the Standalone Universal AI Manager"""
    print("\n" + "=" * 80)
    print("🧪 TESTING STANDALONE UNIVERSAL AI MANAGER")
    print("=" * 80 + "\n")

    manager = get_manager()

    print(manager.get_config_summary())
    print()

    if len(manager.active_providers) == 0:
        print("⚠️  No API keys configured - cannot test live generation")
        print("   Set environment variables to test with real providers")
        print()
        print("✅ Test PASSED - Manager initialized successfully")
        print("   (Ready to use once API keys are configured)")
        return

    print("📝 Test 1: Simple generation...")
    result = await manager.generate(
        "Say 'Standalone Universal AI Manager test successful!' and nothing else.",
        strategy="intelligent",
    )

    if result["success"]:
        print(f"✅ Success!")
        print(f"   Provider: {result['provider_name']}")
        print(f"   Response: {result['content'][:100]}...")
        print(f"   Time: {result['response_time']:.2f}s")
    else:
        print(f"❌ Failed: {result['error']}")
    print()

    print("=" * 80)
    print("📊 STATISTICS")
    print("=" * 80)
    stats = manager.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    print()

    print("=" * 80)
    print("🏥 PROVIDER HEALTH")
    print("=" * 80)
    health = manager.get_provider_health()
    for provider_id, info in health.items():
        status_emoji = "✅" if info["available"] else "❌"
        print(
            f"{status_emoji} {info['name']:25s} | Status: {info['status']:12s} | Success: {info['success_rate']:6s}"
        )
    print()


if __name__ == "__main__":
    asyncio.run(test_manager())
