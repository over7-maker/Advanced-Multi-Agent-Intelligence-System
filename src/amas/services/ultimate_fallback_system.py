#!/usr/bin/env python3
"""
Ultimate Fallback System - Comprehensive fallback for all 9 AI providers
"""

import os
import sys
import asyncio
import aiohttp
import json
import logging
import time
import random
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from enum import Enum
import openai
from groq import Groq
from google import genai
from cerebras.cloud.sdk import Cerebras

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
    RATE_LIMITED = "rate_limited"


class UltimateFallbackSystem:
    """Ultimate fallback system for all 9 AI providers"""

    def __init__(self):
        self.providers = {
            "deepseek": {
                "name": "DeepSeek V3.1",
                "api_key": os.getenv("DEEPSEEK_API_KEY"),
                "base_url": "https://openrouter.ai/api/v1",
                "model": "deepseek/deepseek-chat-v3.1:free",
                "priority": 1,
                "timeout": 30,
                "max_retries": 3,
                "status": ProviderStatus.UNKNOWN,
                "last_used": None,
                "success_count": 0,
                "failure_count": 0,
                "response_time": 0,
                "rate_limit_until": None,
            },
            "glm": {
                "name": "GLM 4.5 Air",
                "api_key": os.getenv("GLM_API_KEY"),
                "base_url": "https://openrouter.ai/api/v1",
                "model": "z-ai/glm-4.5-air:free",
                "priority": 2,
                "timeout": 30,
                "max_retries": 3,
                "status": ProviderStatus.UNKNOWN,
                "last_used": None,
                "success_count": 0,
                "failure_count": 0,
                "response_time": 0,
                "rate_limit_until": None,
            },
            "grok": {
                "name": "xAI Grok 4 Fast",
                "api_key": os.getenv("GROK_API_KEY"),
                "base_url": "https://openrouter.ai/api/v1",
                "model": "x-ai/grok-4-fast:free",
                "priority": 3,
                "timeout": 30,
                "max_retries": 3,
                "status": ProviderStatus.UNKNOWN,
                "last_used": None,
                "success_count": 0,
                "failure_count": 0,
                "response_time": 0,
                "rate_limit_until": None,
            },
            "kimi": {
                "name": "MoonshotAI Kimi K2",
                "api_key": os.getenv("KIMI_API_KEY"),
                "base_url": "https://openrouter.ai/api/v1",
                "model": "moonshotai/kimi-k2:free",
                "priority": 4,
                "timeout": 30,
                "max_retries": 3,
                "status": ProviderStatus.UNKNOWN,
                "last_used": None,
                "success_count": 0,
                "failure_count": 0,
                "response_time": 0,
                "rate_limit_until": None,
            },
            "qwen": {
                "name": "Qwen3 Coder",
                "api_key": os.getenv("QWEN_API_KEY"),
                "base_url": "https://openrouter.ai/api/v1",
                "model": "qwen/qwen3-coder:free",
                "priority": 5,
                "timeout": 30,
                "max_retries": 3,
                "status": ProviderStatus.UNKNOWN,
                "last_used": None,
                "success_count": 0,
                "failure_count": 0,
                "response_time": 0,
                "rate_limit_until": None,
            },
            "gptoss": {
                "name": "OpenAI GPT-OSS 120B",
                "api_key": os.getenv("GPTOSS_API_KEY"),
                "base_url": "https://openrouter.ai/api/v1",
                "model": "openai/gpt-oss-120b:free",
                "priority": 6,
                "timeout": 30,
                "max_retries": 3,
                "status": ProviderStatus.UNKNOWN,
                "last_used": None,
                "success_count": 0,
                "failure_count": 0,
                "response_time": 0,
                "rate_limit_until": None,
            },
            "groq": {
                "name": "Groq AI",
                "api_key": os.getenv("GROQAI_API_KEY"),
                "base_url": "https://api.groq.com/openai/v1",
                "model": "llama-3.3-70b-versatile",
                "priority": 7,
                "timeout": 30,
                "max_retries": 3,
                "status": ProviderStatus.UNKNOWN,
                "last_used": None,
                "success_count": 0,
                "failure_count": 0,
                "response_time": 0,
                "rate_limit_until": None,
            },
            "cerebras": {
                "name": "Cerebras AI",
                "api_key": os.getenv("CEREBRAS_API_KEY"),
                "base_url": "https://api.cerebras.ai",
                "model": "qwen-3-235b-a22b-instruct-2507",
                "priority": 8,
                "timeout": 30,
                "max_retries": 3,
                "status": ProviderStatus.UNKNOWN,
                "last_used": None,
                "success_count": 0,
                "failure_count": 0,
                "response_time": 0,
                "rate_limit_until": None,
            },
            "gemini": {
                "name": "Gemini AI",
                "api_key": os.getenv("GEMINIAI_API_KEY"),
                "base_url": "https://generativelanguage.googleapis.com/v1beta",
                "model": "gemini-2.5-flash",
                "priority": 9,
                "timeout": 30,
                "max_retries": 3,
                "status": ProviderStatus.UNKNOWN,
                "last_used": None,
                "success_count": 0,
                "failure_count": 0,
                "response_time": 0,
                "rate_limit_until": None,
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
            "random_selection_count": 0,
            "priority_selection_count": 0,
        }

        self.active_providers = self._get_active_providers()
        self.current_provider_index = 0
        self.random_mode = True  # Start with random selection

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

        # Sort by priority for fallback order
        active.sort(key=lambda x: self.providers[x]["priority"])
        logger.info(f"Active providers: {[self.providers[p]['name'] for p in active]}")
        return active

    async def _test_provider(self, provider_id: str) -> bool:
        """Test if a provider is working"""
        try:
            config = self.providers[provider_id]
            config["status"] = ProviderStatus.TESTING

            # Check if rate limited
            if (
                config["rate_limit_until"]
                and datetime.now() < config["rate_limit_until"]
            ):
                config["status"] = ProviderStatus.RATE_LIMITED
                return False

            # Test based on provider type
            if provider_id == "groq":
                return await self._test_groq_provider(provider_id)
            elif provider_id == "cerebras":
                return await self._test_cerebras_provider(provider_id)
            elif provider_id == "gemini":
                return await self._test_gemini_provider(provider_id)
            else:
                return await self._test_openrouter_provider(provider_id)

        except Exception as e:
            logger.warning(f"Provider {provider_id} test failed: {e}")
            config["status"] = ProviderStatus.FAILED
            return False

    async def _test_openrouter_provider(self, provider_id: str) -> bool:
        """Test OpenRouter-based providers"""
        config = self.providers[provider_id]

        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {config['api_key']}",
                "Content-Type": "application/json",
            }

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
                elif response.status == 429:  # Rate limited
                    config["status"] = ProviderStatus.RATE_LIMITED
                    config["rate_limit_until"] = (
                        datetime.now().timestamp() + 3600
                    )  # 1 hour
                    return False
                else:
                    config["status"] = ProviderStatus.FAILED
                    return False

    async def _test_groq_provider(self, provider_id: str) -> bool:
        """Test Groq provider"""
        try:
            config = self.providers[provider_id]
            client = Groq(api_key=config["api_key"])

            start_time = time.time()
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": "Test"}],
                model=config["model"],
                max_tokens=10,
            )
            response_time = time.time() - start_time
            config["response_time"] = response_time
            config["status"] = ProviderStatus.ACTIVE
            return True
        except Exception as e:
            logger.warning(f"Groq test failed: {e}")
            config["status"] = ProviderStatus.FAILED
            return False

    async def _test_cerebras_provider(self, provider_id: str) -> bool:
        """Test Cerebras provider"""
        try:
            config = self.providers[provider_id]
            client = Cerebras(api_key=config["api_key"])

            start_time = time.time()
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": "Test"}],
                model=config["model"],
                max_tokens=10,
            )
            response_time = time.time() - start_time
            config["response_time"] = response_time
            config["status"] = ProviderStatus.ACTIVE
            return True
        except Exception as e:
            logger.warning(f"Cerebras test failed: {e}")
            config["status"] = ProviderStatus.FAILED
            return False

    async def _test_gemini_provider(self, provider_id: str) -> bool:
        """Test Gemini provider"""
        try:
            config = self.providers[provider_id]
            client = genai.Client(api_key=config["api_key"])

            start_time = time.time()
            response = client.models.generate_content(
                model=config["model"], contents="Test"
            )
            response_time = time.time() - start_time
            config["response_time"] = response_time
            config["status"] = ProviderStatus.ACTIVE
            return True
        except Exception as e:
            logger.warning(f"Gemini test failed: {e}")
            config["status"] = ProviderStatus.FAILED
            return False

    def _get_next_provider_random(self) -> Optional[str]:
        """Get next provider using random selection"""
        available_providers = [
            p
            for p in self.active_providers
            if self.providers[p]["status"]
            in [ProviderStatus.ACTIVE, ProviderStatus.UNKNOWN]
        ]

        if not available_providers:
            return None

        # Random selection with weighted probability based on success rate
        weights = []
        for provider in available_providers:
            config = self.providers[provider]
            total_requests = config["success_count"] + config["failure_count"]
            success_rate = (
                config["success_count"] / total_requests if total_requests > 0 else 0.5
            )
            weights.append(success_rate + 0.1)  # Add small base weight

        return random.choices(available_providers, weights=weights)[0]

    def _get_next_provider_priority(self) -> Optional[str]:
        """Get next provider using priority order"""
        for i in range(len(self.active_providers)):
            provider_id = self.active_providers[self.current_provider_index]
            config = self.providers[provider_id]

            if config["status"] in [ProviderStatus.ACTIVE, ProviderStatus.UNKNOWN]:
                return provider_id

            self.current_provider_index = (self.current_provider_index + 1) % len(
                self.active_providers
            )

        return None

    async def _get_next_provider(self) -> Optional[str]:
        """Get next available provider using intelligent selection"""
        # Toggle between random and priority selection
        if self.random_mode:
            provider = self._get_next_provider_random()
            if provider:
                self.fallback_stats["random_selection_count"] += 1
                return provider

        # Fallback to priority selection
        provider = self._get_next_provider_priority()
        if provider:
            self.fallback_stats["priority_selection_count"] += 1
            return provider

        return None

    async def _make_request_openrouter(
        self, provider_id: str, messages: List[Dict], **kwargs
    ) -> Dict[str, Any]:
        """Make request to OpenRouter-based providers"""
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
                    elif response.status == 429:  # Rate limited
                        config["failure_count"] += 1
                        config["status"] = ProviderStatus.RATE_LIMITED
                        config["rate_limit_until"] = datetime.now().timestamp() + 3600
                        return {
                            "success": False,
                            "provider": provider_id,
                            "provider_name": config["name"],
                            "error": "Rate limited",
                            "response_time": response_time,
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

    async def _make_request_groq(
        self, provider_id: str, messages: List[Dict], **kwargs
    ) -> Dict[str, Any]:
        """Make request to Groq provider"""
        config = self.providers[provider_id]

        start_time = time.time()

        try:
            client = Groq(api_key=config["api_key"])
            response = client.chat.completions.create(
                messages=messages,
                model=config["model"],
                max_tokens=kwargs.get("max_tokens", 2000),
                temperature=kwargs.get("temperature", 0.7),
            )

            response_time = time.time() - start_time
            config["response_time"] = response_time
            config["last_used"] = datetime.now().isoformat()
            config["success_count"] += 1
            config["status"] = ProviderStatus.ACTIVE

            return {
                "success": True,
                "provider": provider_id,
                "provider_name": config["name"],
                "response": response,
                "content": response.choices[0].message.content,
                "response_time": response_time,
                "tokens_used": response.usage.total_tokens if response.usage else 0,
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

    async def _make_request_cerebras(
        self, provider_id: str, messages: List[Dict], **kwargs
    ) -> Dict[str, Any]:
        """Make request to Cerebras provider"""
        config = self.providers[provider_id]

        start_time = time.time()

        try:
            client = Cerebras(api_key=config["api_key"])
            response = client.chat.completions.create(
                messages=messages,
                model=config["model"],
                max_tokens=kwargs.get("max_tokens", 2000),
                temperature=kwargs.get("temperature", 0.7),
            )

            response_time = time.time() - start_time
            config["response_time"] = response_time
            config["last_used"] = datetime.now().isoformat()
            config["success_count"] += 1
            config["status"] = ProviderStatus.ACTIVE

            return {
                "success": True,
                "provider": provider_id,
                "provider_name": config["name"],
                "response": response,
                "content": response.choices[0].message.content,
                "response_time": response_time,
                "tokens_used": response.usage.total_tokens if response.usage else 0,
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

    async def _make_request_gemini(
        self, provider_id: str, messages: List[Dict], **kwargs
    ) -> Dict[str, Any]:
        """Make request to Gemini provider"""
        config = self.providers[provider_id]

        start_time = time.time()

        try:
            client = genai.Client(api_key=config["api_key"])

            # Convert messages to Gemini format
            content = messages[-1]["content"] if messages else "Hello"

            response = client.models.generate_content(
                model=config["model"], contents=content
            )

            response_time = time.time() - start_time
            config["response_time"] = response_time
            config["last_used"] = datetime.now().isoformat()
            config["success_count"] += 1
            config["status"] = ProviderStatus.ACTIVE

            return {
                "success": True,
                "provider": provider_id,
                "provider_name": config["name"],
                "response": response,
                "content": response.text,
                "response_time": response_time,
                "tokens_used": 0,  # Gemini doesn't provide token count
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

    async def _make_request(
        self, provider_id: str, messages: List[Dict], **kwargs
    ) -> Dict[str, Any]:
        """Make request to specific provider"""
        if provider_id == "groq":
            return await self._make_request_groq(provider_id, messages, **kwargs)
        elif provider_id == "cerebras":
            return await self._make_request_cerebras(provider_id, messages, **kwargs)
        elif provider_id == "gemini":
            return await self._make_request_gemini(provider_id, messages, **kwargs)
        else:
            return await self._make_request_openrouter(provider_id, messages, **kwargs)

    async def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate response with intelligent fallback"""
        self.fallback_stats["total_requests"] += 1

        messages = [{"role": "user", "content": prompt}]

        # Try each provider in intelligent order
        for attempt in range(len(self.active_providers)):
            provider_id = await self._get_next_provider()

            if not provider_id:
                break

            # Test provider if needed
            if not await self._test_provider(provider_id):
                continue

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
            "random_selection_count": self.fallback_stats["random_selection_count"],
            "priority_selection_count": self.fallback_stats["priority_selection_count"],
            "last_reset": self.fallback_stats["last_reset"],
        }

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
                "rate_limited_until": config["rate_limit_until"],
            }

        return health

    def reset_fallback_order(self):
        """Reset fallback order and toggle selection mode"""
        self.current_provider_index = 0
        self.random_mode = not self.random_mode  # Toggle between random and priority
        self.fallback_stats["last_reset"] = datetime.now().isoformat()
        logger.info(
            f"Fallback order reset - Mode: {'Random' if self.random_mode else 'Priority'}"
        )


# Global fallback system instance
ultimate_fallback_system = UltimateFallbackSystem()


# Convenience functions
async def generate_ai_response(prompt: str, **kwargs) -> Dict[str, Any]:
    """Generate AI response with intelligent fallback"""
    return await ultimate_fallback_system.generate_response(prompt, **kwargs)


def get_fallback_stats() -> Dict[str, Any]:
    """Get fallback statistics"""
    return ultimate_fallback_system.get_fallback_stats()


def get_provider_health() -> Dict[str, Any]:
    """Get provider health information"""
    return ultimate_fallback_system.get_provider_health()


def reset_fallback_order():
    """Reset fallback order"""
    ultimate_fallback_system.reset_fallback_order()


# Test function
async def test_ultimate_fallback():
    """Test the ultimate fallback system"""
    print("🧪 Testing Ultimate Fallback System...")
    print("=" * 60)

    # Test with a simple prompt
    result = await generate_ai_response(
        "Hello, this is a test. Please respond with 'Ultimate Fallback Test Successful'"
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
    print(f"\n📊 Fallback Statistics:")
    print(f"Total Requests: {stats['total_requests']}")
    print(f"Success Rate: {stats['success_rate']}")
    print(f"Average Response Time: {stats['average_response_time']}")
    print(f"Active Providers: {stats['active_providers']}")
    print(f"Random Selections: {stats['random_selection_count']}")
    print(f"Priority Selections: {stats['priority_selection_count']}")

    # Show provider health
    health = get_provider_health()
    print(f"\n🏥 Provider Health:")
    for provider_id, info in health.items():
        print(f"  {info['name']}: {info['status']} ({info['success_rate']})")


if __name__ == "__main__":
    asyncio.run(test_ultimate_fallback())
