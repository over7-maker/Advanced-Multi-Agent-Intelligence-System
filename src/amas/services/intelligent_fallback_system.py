#!/usr/bin/env python3
"""
Intelligent Fallback System - Comprehensive fallback for all 6 AI providers
"""

import asyncio
import logging
import os
import time
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import aiohttp

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ProviderStatus(Enum):
    ACTIVE = "active"
    FAILED = "failed"
    TESTING = "testing"
    UNKNOWN = "unknown"


class IntelligentFallbackSystem:
    """Intelligent fallback system for all 6 AI providers"""

    def __init__(self):
        self.providers = {
            "deepseek": {
                "name": "DeepSeek",
                "api_key": os.getenv("DEEPSEEK_API_KEY"),
                "base_url": "https://api.deepseek.com/v1",
                "model": "deepseek-chat",
                "priority": 1,
                "timeout": 30,
                "max_retries": 3,
                "status": ProviderStatus.UNKNOWN,
                "last_used": None,
                "success_count": 0,
                "failure_count": 0,
                "response_time": 0,
            },
            "glm": {
                "name": "GLM 4.5 Air",
                "api_key": os.getenv("GLM_API_KEY"),
                "base_url": "https://open.bigmodel.cn/api/paas/v4",
                "model": "glm-4-flash",
                "priority": 2,
                "timeout": 30,
                "max_retries": 3,
                "status": ProviderStatus.UNKNOWN,
                "last_used": None,
                "success_count": 0,
                "failure_count": 0,
                "response_time": 0,
            },
            "grok": {
                "name": "xAI Grok 4 Fast",
                "api_key": os.getenv("GROK_API_KEY"),
                "base_url": "https://api.openrouter.ai/v1",
                "model": "x-ai/grok-beta",
                "priority": 3,
                "timeout": 30,
                "max_retries": 3,
                "status": ProviderStatus.UNKNOWN,
                "last_used": None,
                "success_count": 0,
                "failure_count": 0,
                "response_time": 0,
            },
            "kimi": {
                "name": "MoonshotAI Kimi K2",
                "api_key": os.getenv("KIMI_API_KEY"),
                "base_url": "https://api.moonshot.cn/v1",
                "model": "moonshot-v1-8k",
                "priority": 4,
                "timeout": 30,
                "max_retries": 3,
                "status": ProviderStatus.UNKNOWN,
                "last_used": None,
                "success_count": 0,
                "failure_count": 0,
                "response_time": 0,
            },
            "qwen": {
                "name": "Qwen3 Coder",
                "api_key": os.getenv("QWEN_API_KEY"),
                "base_url": "https://dashscope.aliyuncs.com/api/v1",
                "model": "qwen-plus",
                "priority": 5,
                "timeout": 30,
                "max_retries": 3,
                "status": ProviderStatus.UNKNOWN,
                "last_used": None,
                "success_count": 0,
                "failure_count": 0,
                "response_time": 0,
            },
            "gptoss": {
                "name": "OpenAI GPT-OSS 120B",
                "api_key": os.getenv("GPTOSS_API_KEY"),
                "base_url": "https://api.openrouter.ai/v1",
                "model": "openai/gpt-4o",
                "priority": 6,
                "timeout": 30,
                "max_retries": 3,
                "status": ProviderStatus.UNKNOWN,
                "last_used": None,
                "success_count": 0,
                "failure_count": 0,
                "response_time": 0,
            },
        }

        self.fallback_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "fallback_usage": {},
            "provider_performance": {},
            "average_response_time": 0,
            "last_reset": datetime.now().isoformat(),
        }

        self.active_providers = self._get_active_providers()
        self.current_provider_index = 0

    def _get_active_providers(self) -> List[str]:
        """Get list of active providers with valid API keys"""
        active = []
        for provider_id, config in self.providers.items():
            if config["api_key"] and config["api_key"].strip():
                active.append(provider_id)
                config["status"] = ProviderStatus.ACTIVE
                logger.info(f"✅ {config['name']} is active")
            else:
                config["status"] = ProviderStatus.FAILED
                logger.warning(f"⚠️ {config['name']} is inactive (no API key)")

        if not active:
            raise Exception(
                "No active AI providers found! Please set at least one API key."
            )

        # Sort by priority
        active.sort(key=lambda x: self.providers[x]["priority"])
        logger.info(
            f"Active providers (in priority order): {[self.providers[p]['name'] for p in active]}"
        )
        return active

    async def _test_provider(self, provider_id: str) -> bool:
        """Test if a provider is working"""
        try:
            config = self.providers[provider_id]
            config["status"] = ProviderStatus.TESTING

            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {config['api_key']}",
                    "Content-Type": "application/json",
                }

                # Simple test request
                test_payload = {
                    "model": config["model"],
                    "messages": [{"role": "user", "content": "Test"}],
                    "max_tokens": 10,
                }

                start_time = time.time()
                async with session.post(
                    f"{config['base_url']}/chat/completions",
                    headers=headers,
                    json=test_payload,
                    timeout=aiohttp.ClientTimeout(total=config["timeout"]),
                ) as response:
                    response_time = time.time() - start_time
                    config["response_time"] = response_time

                    if response.status == 200:
                        config["status"] = ProviderStatus.ACTIVE
                        return True
                    else:
                        config["status"] = ProviderStatus.FAILED
                        return False

        except Exception as e:
            logger.warning(f"Provider {provider_id} test failed: {e}")
            config["status"] = ProviderStatus.FAILED
            return False

    async def _get_next_provider(self) -> Optional[str]:
        """Get next available provider in fallback order"""
        for i in range(len(self.active_providers)):
            provider_id = self.active_providers[self.current_provider_index]
            config = self.providers[provider_id]

            # Skip if provider is known to be failed
            if config["status"] == ProviderStatus.FAILED:
                self.current_provider_index = (self.current_provider_index + 1) % len(
                    self.active_providers
                )
                continue

            # Test if provider is working
            if await self._test_provider(provider_id):
                return provider_id

            # Move to next provider
            self.current_provider_index = (self.current_provider_index + 1) % len(
                self.active_providers
            )

        return None

    async def _make_request(
        self, provider_id: str, messages: List[Dict], **kwargs
    ) -> Dict[str, Any]:
        """Make request to specific provider"""
        config = self.providers[provider_id]

        payload = {
            "model": config["model"],
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", 2000),
            "temperature": kwargs.get("temperature", 0.7),
        }

        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json",
        }

        start_time = time.time()

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{config['base_url']}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=config["timeout"]),
                ) as response:
                    response_time = time.time() - start_time
                    config["response_time"] = response_time
                    config["last_used"] = datetime.now().isoformat()

                    if response.status == 200:
                        result = await response.json()
                        config["success_count"] += 1
                        config["status"] = ProviderStatus.ACTIVE

                        return {
                            "success": True,
                            "provider": provider_id,
                            "provider_name": config["name"],
                            "response": result,
                            "content": result["choices"][0]["message"]["content"],
                            "response_time": response_time,
                            "tokens_used": result.get("usage", {}).get(
                                "total_tokens", 0
                            ),
                        }
                    else:
                        error_text = await response.text()
                        config["failure_count"] += 1
                        config["status"] = ProviderStatus.FAILED

                        return {
                            "success": False,
                            "provider": provider_id,
                            "provider_name": config["name"],
                            "error": f"HTTP {response.status}: {error_text}",
                            "response_time": response_time,
                        }
        except Exception as e:
            response_time = time.time() - start_time
            config["failure_count"] += 1
            config["status"] = ProviderStatus.FAILED

            return {
                "success": False,
                "provider": provider_id,
                "provider_name": config["name"],
                "error": str(e),
                "response_time": response_time,
            }

    async def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate response with intelligent fallback"""
        self.fallback_stats["total_requests"] += 1

        messages = [{"role": "user", "content": prompt}]

        # Try each provider in order
        for attempt in range(len(self.active_providers)):
            provider_id = await self._get_next_provider()

            if not provider_id:
                break

            logger.info(
                f"Attempting request with {self.providers[provider_id]['name']} (attempt {attempt + 1})"
            )

            try:
                result = await self._make_request(provider_id, messages, **kwargs)

                if result["success"]:
                    self.fallback_stats["successful_requests"] += 1
                    self.fallback_stats["fallback_usage"][provider_id] = (
                        self.fallback_stats["fallback_usage"].get(provider_id, 0) + 1
                    )

                    # Update performance stats
                    if provider_id not in self.fallback_stats["provider_performance"]:
                        self.fallback_stats["provider_performance"][provider_id] = {
                            "success_count": 0,
                            "failure_count": 0,
                            "total_response_time": 0,
                            "average_response_time": 0,
                        }

                    perf = self.fallback_stats["provider_performance"][provider_id]
                    perf["success_count"] += 1
                    perf["total_response_time"] += result["response_time"]
                    perf["average_response_time"] = (
                        perf["total_response_time"] / perf["success_count"]
                    )

                    logger.info(
                        f"✅ Success with {self.providers[provider_id]['name']} in {result['response_time']:.2f}s"
                    )
                    return result
                else:
                    logger.warning(
                        f"❌ {self.providers[provider_id]['name']} failed: {result['error']}"
                    )

            except Exception as e:
                logger.warning(
                    f"❌ {self.providers[provider_id]['name']} exception: {e}"
                )

            # Move to next provider
            self.current_provider_index = (self.current_provider_index + 1) % len(
                self.active_providers
            )

        # All providers failed
        self.fallback_stats["failed_requests"] += 1
        logger.error("❌ All AI providers failed!")

        return {
            "success": False,
            "provider": "none",
            "provider_name": "All Providers Failed",
            "error": "All AI providers failed",
            "fallback_stats": self.fallback_stats,
        }

    def get_fallback_stats(self) -> Dict[str, Any]:
        """Get comprehensive fallback statistics"""
        total = self.fallback_stats["total_requests"]
        success_rate = (
            (self.fallback_stats["successful_requests"] / total * 100)
            if total > 0
            else 0
        )

        # Calculate average response time
        total_time = sum(
            perf["total_response_time"]
            for perf in self.fallback_stats["provider_performance"].values()
        )
        total_success = sum(
            perf["success_count"]
            for perf in self.fallback_stats["provider_performance"].values()
        )
        avg_response_time = total_time / total_success if total_success > 0 else 0

        return {
            "total_requests": total,
            "successful_requests": self.fallback_stats["successful_requests"],
            "failed_requests": self.fallback_stats["failed_requests"],
            "success_rate": f"{success_rate:.1f}%",
            "average_response_time": f"{avg_response_time:.2f}s",
            "fallback_usage": self.fallback_stats["fallback_usage"],
            "provider_performance": self.fallback_stats["provider_performance"],
            "active_providers": len(self.active_providers),
            "provider_names": [
                self.providers[p]["name"] for p in self.active_providers
            ],
            "provider_status": {
                p: self.providers[p]["status"].value for p in self.providers
            },
            "last_reset": self.fallback_stats["last_reset"],
        }

    def reset_fallback_order(self):
        """Reset fallback order to priority order"""
        self.current_provider_index = 0
        self.fallback_stats["last_reset"] = datetime.now().isoformat()
        logger.info("Fallback order reset to priority order")

    def get_provider_health(self) -> Dict[str, Any]:
        """Get detailed provider health information"""
        health = {}
        for provider_id, config in self.providers.items():
            total_requests = config["success_count"] + config["failure_count"]
            success_rate = (
                (config["success_count"] / total_requests * 100)
                if total_requests > 0
                else 0
            )

            health[provider_id] = {
                "name": config["name"],
                "status": config["status"].value,
                "success_count": config["success_count"],
                "failure_count": config["failure_count"],
                "success_rate": f"{success_rate:.1f}%",
                "average_response_time": f"{config['response_time']:.2f}s",
                "last_used": config["last_used"],
                "priority": config["priority"],
            }

        return health


# Global fallback system instance
fallback_system = IntelligentFallbackSystem()


# Convenience functions
async def generate_ai_response(prompt: str, **kwargs) -> Dict[str, Any]:
    """Generate AI response with intelligent fallback"""
    return await fallback_system.generate_response(prompt, **kwargs)


def get_fallback_stats() -> Dict[str, Any]:
    """Get fallback statistics"""
    return fallback_system.get_fallback_stats()


def get_provider_health() -> Dict[str, Any]:
    """Get provider health information"""
    return fallback_system.get_provider_health()


def reset_fallback_order():
    """Reset fallback order"""
    fallback_system.reset_fallback_order()


# Test function
async def test_intelligent_fallback():
    """Test the intelligent fallback system"""
    print("🧪 Testing Intelligent Fallback System...")
    print("=" * 60)

    # Test with a simple prompt
    result = await generate_ai_response(
        "Hello, this is a test. Please respond with 'AI Fallback Test Successful'"
    )

    if result["success"]:
        print(f"✅ Test successful with {result['provider_name']}")
        print(f"Response: {result['content'][:100]}...")
        print(f"Response Time: {result['response_time']:.2f}s")
        if "tokens_used" in result:
            print(f"Tokens Used: {result['tokens_used']}")
    else:
        print(f"❌ Test failed: {result['error']}")

    # Show comprehensive stats
    stats = get_fallback_stats()
    print("\n📊 Fallback Statistics:")
    print(f"Total Requests: {stats['total_requests']}")
    print(f"Success Rate: {stats['success_rate']}")
    print(f"Average Response Time: {stats['average_response_time']}")
    print(f"Active Providers: {stats['active_providers']}")
    print(f"Provider Names: {', '.join(stats['provider_names'])}")

    # Show provider health
    health = get_provider_health()
    print("\n🏥 Provider Health:")
    for provider_id, info in health.items():
        print(f"  {info['name']}: {info['status']} ({info['success_rate']})")


if __name__ == "__main__":
    asyncio.run(test_intelligent_fallback())
