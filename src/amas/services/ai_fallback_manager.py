from standalone_universal_ai_manager import get_api_key
#!/usr/bin/env python3
"""
AI Fallback Manager - Intelligent fallback system for all 6 AI providers
"""

import asyncio
import logging
import os
from typing import Any, Dict, List, Optional

import aiohttp

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AIFallbackManager:
    """Intelligent fallback manager for all 6 AI providers"""

    def __init__(self):
        self.providers = {
            "deepseek": {
                "name": "DeepSeek",
                "api_key": get_api_key("DEEPSEEK_API_KEY"),
                "base_url": "https://api.deepseek.com/v1",
                "model": "deepseek-chat",
                "priority": 1,
                "timeout": 30,
                "max_retries": 3,
            },
            "glm": {
                "name": "GLM 4.5 Air",
                "api_key": get_api_key("GLM_API_KEY"),
                "base_url": "https://open.bigmodel.cn/api/paas/v4",
                "model": "glm-4-flash",
                "priority": 2,
                "timeout": 30,
                "max_retries": 3,
            },
            "grok": {
                "name": "xAI Grok 4 Fast",
                "api_key": get_api_key("GROK_API_KEY"),
                "base_url": "https://api.openrouter.ai/v1",
                "model": "x-ai/grok-beta",
                "priority": 3,
                "timeout": 30,
                "max_retries": 3,
            },
            "kimi": {
                "name": "MoonshotAI Kimi K2",
                "api_key": get_api_key("KIMI_API_KEY"),
                "base_url": "https://api.moonshot.cn/v1",
                "model": "moonshot-v1-8k",
                "priority": 4,
                "timeout": 30,
                "max_retries": 3,
            },
            "qwen": {
                "name": "Qwen3 Coder",
                "api_key": get_api_key("QWEN_API_KEY"),
                "base_url": "https://dashscope.aliyuncs.com/api/v1",
                "model": "qwen-plus",
                "priority": 5,
                "timeout": 30,
                "max_retries": 3,
            },
            "gptoss": {
                "name": "OpenAI GPT-OSS 120B",
                "api_key": get_api_key("GPTOSS_API_KEY"),
                "base_url": "https://api.openrouter.ai/v1",
                "model": "openai/gpt-4o",
                "priority": 6,
                "timeout": 30,
                "max_retries": 3,
            },
        }

        self.fallback_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "fallback_usage": {},
            "provider_performance": {},
        }

        self.active_providers = self._get_active_providers()
        self.current_provider_index = 0

    def _get_active_providers(self) -> List[str]:
        """Get list of active providers with valid API keys"""
        active = []
        for provider_id, config in self.providers.items():
            if config["api_key"] and config["api_key"].strip():
                active.append(provider_id)
                logger.info(f"✅ {config['name']} is active")
            else:
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

                async with session.post(
                    f"{config['base_url']}/chat/completions",
                    headers=headers,
                    json=test_payload,
                    timeout=aiohttp.ClientTimeout(total=config["timeout"]),
                ) as response:
                    return response.status == 200

        except Exception as e:
            logger.warning(f"Provider {provider_id} test failed: {e}")
            return False

    async def _get_next_provider(self) -> Optional[str]:
        """Get next available provider in fallback order"""
        for i in range(len(self.active_providers)):
            provider_id = self.active_providers[self.current_provider_index]

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

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{config['base_url']}/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=config["timeout"]),
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        "success": True,
                        "provider": provider_id,
                        "response": result,
                        "content": result["choices"][0]["message"]["content"],
                    }
                else:
                    error_text = await response.text()
                    return {
                        "success": False,
                        "provider": provider_id,
                        "error": f"HTTP {response.status}: {error_text}",
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

                    logger.info(
                        f"✅ Success with {self.providers[provider_id]['name']}"
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
            "error": "All AI providers failed",
            "fallback_stats": self.fallback_stats,
        }

    def get_fallback_stats(self) -> Dict[str, Any]:
        """Get fallback statistics"""
        total = self.fallback_stats["total_requests"]
        success_rate = (
            (self.fallback_stats["successful_requests"] / total * 100)
            if total > 0
            else 0
        )

        return {
            "total_requests": total,
            "successful_requests": self.fallback_stats["successful_requests"],
            "failed_requests": self.fallback_stats["failed_requests"],
            "success_rate": f"{success_rate:.1f}%",
            "fallback_usage": self.fallback_stats["fallback_usage"],
            "active_providers": len(self.active_providers),
            "provider_names": [
                self.providers[p]["name"] for p in self.active_providers
            ],
        }

    def reset_fallback_order(self):
        """Reset fallback order to priority order"""
        self.current_provider_index = 0
        logger.info("Fallback order reset to priority order")


# Global fallback manager instance
fallback_manager = AIFallbackManager()


async def generate_ai_response(prompt: str, **kwargs) -> Dict[str, Any]:
    """Generate AI response with intelligent fallback"""
    return await fallback_manager.generate_response(prompt, **kwargs)


def get_fallback_stats() -> Dict[str, Any]:
    """Get fallback statistics"""
    return fallback_manager.get_fallback_stats()


def reset_fallback_order():
    """Reset fallback order"""
    fallback_manager.reset_fallback_order()


# Test function
async def test_fallback_system():
    """Test the fallback system"""
    print("🧪 Testing AI Fallback System...")
    print("=" * 50)

    # Test with a simple prompt
    result = await generate_ai_response(
        "Hello, this is a test. Please respond with 'AI Fallback Test Successful'"
    )

    if result["success"]:
        print(
            f"✅ Test successful with {fallback_manager.providers[result['provider']]['name']}"
        )
        print(f"Response: {result['content'][:100]}...")
    else:
        print(f"❌ Test failed: {result['error']}")

    # Show stats
    stats = get_fallback_stats()
    print("\n📊 Fallback Statistics:")
    print(f"Total Requests: {stats['total_requests']}")
    print(f"Success Rate: {stats['success_rate']}")
    print(f"Active Providers: {stats['active_providers']}")
    print(f"Provider Names: {', '.join(stats['provider_names'])}")


if __name__ == "__main__":
    asyncio.run(test_fallback_system())
