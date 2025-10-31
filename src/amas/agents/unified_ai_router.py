from standalone_universal_ai_manager import get_api_key

"""
Unified AI Router with Intelligent Fallback Mechanism
Handles multiple AI providers with automatic failover and load balancing
"""

import asyncio

# import json
import logging
import os

# import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import aiohttp
import anthropic
from openai import AsyncOpenAI, OpenAI

logger = logging.getLogger(__name__)


class ModelProvider(Enum):
    """Available AI model providers"""

    OPENROUTER = "openrouter"
    DEEPSEEK_DIRECT = "deepseek_direct"
    OPENAI_DIRECT = "openai_direct"
    CLAUDE_DIRECT = "claude_direct"
    GLM_DIRECT = "glm_direct"
    LOCAL_LLAMA = "local_llama"
    LOCAL_CODELLAMA = "local_codellama"


@dataclass
class ModelConfig:
    """Configuration for an AI model"""

    provider: ModelProvider
    model_name: str
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    max_tokens: int = 4096
    temperature: float = 0.7
    priority: int = 1  # Lower is higher priority
    rate_limit_per_minute: int = 60
    cost_per_1k_tokens: float = 0.001
    supports_streaming: bool = True
    timeout_seconds: int = 30


@dataclass
class ModelUsageStats:
    """Track usage statistics for rate limiting and load balancing"""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_tokens: int = 0
    last_request_time: Optional[datetime] = None
    last_failure_time: Optional[datetime] = None
    consecutive_failures: int = 0
    is_available: bool = True


class UnifiedAIRouter:
    """
    Unified router for multiple AI providers with intelligent fallback
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the AI router with configuration"""
        self.models: Dict[str, ModelConfig] = {}
        self.usage_stats: Dict[str, ModelUsageStats] = {}
        self.clients: Dict[str, Any] = {}

        # Load configuration
        self._load_configuration(config_path)

        # Initialize clients
        self._initialize_clients()

        # Start background monitoring
        self._start_monitoring()

    def _load_configuration(self, config_path: Optional[str] = None):
        """Load model configurations from environment and config file"""

        # OpenRouter configuration (if available)
        openrouter_key = get_api_key("OPENROUTER_API_KEY") or os.getenv(
            "DEEPSEEK_API_KEY"
        )
        if openrouter_key and openrouter_key.startswith("sk-or-"):
            # These are OpenRouter keys
            self.models["openrouter_deepseek"] = ModelConfig(
                provider=ModelProvider.OPENROUTER,
                model_name="deepseek/deepseek-chat",
                base_url="https://openrouter.ai/api/v1",
                api_key=openrouter_key,
                priority=1,
                cost_per_1k_tokens=0.0001,
            )

            self.models["openrouter_claude"] = ModelConfig(
                provider=ModelProvider.OPENROUTER,
                model_name="anthropic/claude-3-opus-20240229",
                base_url="https://openrouter.ai/api/v1",
                api_key=openrouter_key,
                priority=2,
                cost_per_1k_tokens=0.015,
            )

            self.models["openrouter_gpt4"] = ModelConfig(
                provider=ModelProvider.OPENROUTER,
                model_name="openai/gpt-4-turbo-preview",
                base_url="https://openrouter.ai/api/v1",
                api_key=openrouter_key,
                priority=3,
                cost_per_1k_tokens=0.01,
            )

        # Direct API configurations
        if get_api_key("OPENAI_API_KEY"):
            self.models["openai_direct"] = ModelConfig(
                provider=ModelProvider.OPENAI_DIRECT,
                model_name="gpt-4-turbo-preview",
                api_key=get_api_key("OPENAI_API_KEY"),
                priority=2,
            )

        if get_api_key("CLAUDE_API_KEY"):
            self.models["claude_direct"] = ModelConfig(
                provider=ModelProvider.CLAUDE_DIRECT,
                model_name="claude-3-opus-20240229",
                api_key=get_api_key("CLAUDE_API_KEY"),
                priority=2,
            )

        # Local LLM configurations (always available as fallback)
        self.models["local_llama"] = ModelConfig(
            provider=ModelProvider.LOCAL_LLAMA,
            model_name="llama3.1:70b",
            base_url="http://localhost:11434/v1",
            priority=10,  # Lower priority fallback
            cost_per_1k_tokens=0.0,
        )

        self.models["local_codellama"] = ModelConfig(
            provider=ModelProvider.LOCAL_CODELLAMA,
            model_name="codellama:34b",
            base_url="http://localhost:11434/v1",
            priority=11,
            cost_per_1k_tokens=0.0,
        )

        # Initialize usage stats
        for model_id in self.models:
            self.usage_stats[model_id] = ModelUsageStats()

    def _initialize_clients(self):
        """Initialize API clients for each provider"""
        for model_id, config in self.models.items():
            try:
                if config.provider in [
                    ModelProvider.OPENROUTER,
                    ModelProvider.DEEPSEEK_DIRECT,
                    ModelProvider.OPENAI_DIRECT,
                    ModelProvider.GLM_DIRECT,
                ]:
                    # OpenAI-compatible clients
                    self.clients[model_id] = AsyncOpenAI(
                        api_key=config.api_key, base_url=config.base_url
                    )
                elif config.provider == ModelProvider.CLAUDE_DIRECT:
                    # Anthropic client
                    self.clients[model_id] = anthropic.AsyncAnthropic(
                        api_key=config.api_key
                    )
                elif config.provider in [
                    ModelProvider.LOCAL_LLAMA,
                    ModelProvider.LOCAL_CODELLAMA,
                ]:
                    # Local Ollama client (OpenAI-compatible)
                    self.clients[model_id] = AsyncOpenAI(
                        api_key="ollama",  # Dummy key for Ollama
                        base_url=config.base_url,
                    )

                logger.info(f"Initialized client for {model_id}")

            except Exception as e:
                logger.error(f"Failed to initialize client for {model_id}: {e}")
                self.usage_stats[model_id].is_available = False

    def _start_monitoring(self):
        """Start background monitoring tasks"""
        # This would start async tasks for monitoring model health
        # For now, we'll keep it simple
        pass

    async def complete(
        self,
        messages: List[Dict[str, str]],
        model_preference: Optional[str] = None,
        max_retries: int = 3,
        **kwargs,
    ) -> Tuple[str, str, Dict[str, Any]]:
        """
        Complete a chat request with automatic fallback

        Returns: (response_text, model_used, metadata)
        """
        # Sort models by priority and availability
        available_models = [
            (model_id, config)
            for model_id, config in self.models.items()
            if self.usage_stats[model_id].is_available
        ]
        available_models.sort(key=lambda x: x[1].priority)

        # If model preference is specified, try it first
        if model_preference and model_preference in self.models:
            available_models.insert(
                0, (model_preference, self.models[model_preference])
            )

        last_error = None

        for model_id, config in available_models:
            try:
                # Check rate limits
                if not self._check_rate_limit(model_id):
                    logger.warning(f"Rate limit exceeded for {model_id}")
                    continue

                # Attempt completion
                logger.info(f"Attempting completion with {model_id}")

                response = await self._complete_with_model(
                    model_id, config, messages, **kwargs
                )

                # Update stats
                self.usage_stats[model_id].successful_requests += 1
                self.usage_stats[model_id].total_requests += 1
                self.usage_stats[model_id].last_request_time = datetime.now()
                self.usage_stats[model_id].consecutive_failures = 0

                # Extract response text based on provider
                if config.provider == ModelProvider.CLAUDE_DIRECT:
                    response_text = response.content[0].text
                else:
                    response_text = response.choices[0].message.content

                metadata = {
                    "model_used": model_id,
                    "provider": config.provider.value,
                    "actual_model": config.model_name,
                    "usage": getattr(response, "usage", None),
                    "cost_estimate": self._estimate_cost(model_id, response),
                }

                return response_text, model_id, metadata

            except Exception as e:
                logger.error(f"Failed with {model_id}: {e}")
                last_error = e

                # Update failure stats
                self.usage_stats[model_id].failed_requests += 1
                self.usage_stats[model_id].total_requests += 1
                self.usage_stats[model_id].last_failure_time = datetime.now()
                self.usage_stats[model_id].consecutive_failures += 1

                # Disable model after consecutive failures
                if self.usage_stats[model_id].consecutive_failures >= 3:
                    self.usage_stats[model_id].is_available = False
                    logger.warning(f"Disabled {model_id} after consecutive failures")

        # All models failed
        raise Exception(f"All models failed. Last error: {last_error}")

    async def _complete_with_model(
        self,
        model_id: str,
        config: ModelConfig,
        messages: List[Dict[str, str]],
        **kwargs,
    ) -> Any:
        """Complete request with specific model"""
        client = self.clients.get(model_id)
        if not client:
            raise Exception(f"No client initialized for {model_id}")

        # Merge kwargs with config defaults
        request_params = {
            "model": config.model_name,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", config.max_tokens),
            "temperature": kwargs.get("temperature", config.temperature),
        }

        # Add OpenRouter specific headers if needed
        if config.provider == ModelProvider.OPENROUTER:
            request_params["extra_headers"] = {
                "HTTP-Referer": "https://github.com/over7-maker/AMAS",
                "X-Title": "AMAS Multi-Agent System",
            }

        # Handle provider-specific APIs
        if config.provider == ModelProvider.CLAUDE_DIRECT:
            # Anthropic has different API
            return await client.messages.create(**request_params)
        else:
            # OpenAI-compatible API
            return await client.chat.completions.create(**request_params)

    def _check_rate_limit(self, model_id: str) -> bool:
        """Check if model is within rate limits"""
        stats = self.usage_stats[model_id]
        config = self.models[model_id]

        if not stats.last_request_time:
            return True

        # Simple rate limiting - could be enhanced
        time_since_last = datetime.now() - stats.last_request_time
        if time_since_last.total_seconds() < (60 / config.rate_limit_per_minute):
            return False

        return True

    def _estimate_cost(self, model_id: str, response: Any) -> float:
        """Estimate cost of the request"""
        config = self.models[model_id]

        # Extract token count
        usage = getattr(response, "usage", None)
        if not usage:
            return 0.0

        total_tokens = getattr(usage, "total_tokens", 0)
        return (total_tokens / 1000) * config.cost_per_1k_tokens

    def get_status(self) -> Dict[str, Any]:
        """Get current status of all models"""
        status = {
            "models": {},
            "total_requests": 0,
            "total_failures": 0,
            "available_models": 0,
        }

        for model_id, config in self.models.items():
            stats = self.usage_stats[model_id]
            status["models"][model_id] = {
                "provider": config.provider.value,
                "model": config.model_name,
                "available": stats.is_available,
                "total_requests": stats.total_requests,
                "success_rate": (
                    stats.successful_requests / stats.total_requests
                    if stats.total_requests > 0
                    else 0
                ),
                "consecutive_failures": stats.consecutive_failures,
                "last_request": (
                    stats.last_request_time.isoformat()
                    if stats.last_request_time
                    else None
                ),
            }

            status["total_requests"] += stats.total_requests
            status["total_failures"] += stats.failed_requests
            if stats.is_available:
                status["available_models"] += 1

        return status

    async def test_all_models(self) -> Dict[str, bool]:
        """Test all configured models"""
        results = {}
        test_message = [{"role": "user", "content": "Say 'OK' if you can hear me."}]

        for model_id in self.models:
            try:
                response, _, _ = await self.complete(
                    test_message, model_preference=model_id, max_tokens=10
                )
                results[model_id] = True
                logger.info(f"✓ {model_id} is working")
            except Exception as e:
                results[model_id] = False
                logger.error(f"✗ {model_id} failed: {e}")

        return results


# Singleton instance
_router_instance: Optional[UnifiedAIRouter] = None


def get_ai_router() -> UnifiedAIRouter:
    """Get or create the singleton AI router instance"""
    global _router_instance
    if _router_instance is None:
        _router_instance = UnifiedAIRouter()
    return _router_instance


# Example usage for agents
async def agent_complete(
    agent_name: str,
    messages: List[Dict[str, str]],
    preferred_models: Optional[List[str]] = None,
    **kwargs,
) -> Tuple[str, Dict[str, Any]]:
    """
    Helper function for agents to complete requests

    Args:
        agent_name: Name of the agent making the request
        messages: Chat messages
        preferred_models: List of preferred models in order
        **kwargs: Additional parameters

    Returns:
        (response_text, metadata)
    """
    router = get_ai_router()

    # Try preferred models first
    if preferred_models:
        for model in preferred_models:
            try:
                response, model_used, metadata = await router.complete(
                    messages, model_preference=model, **kwargs
                )
                logger.info(f"{agent_name} completed with {model_used}")
                return response, metadata
            except Exception:
                continue

    # Fallback to any available model
    response, model_used, metadata = await router.complete(messages, **kwargs)
    logger.info(f"{agent_name} completed with {model_used} (fallback)")
    return response, metadata
