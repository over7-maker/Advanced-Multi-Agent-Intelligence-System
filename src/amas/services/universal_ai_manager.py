#!/usr/bin/env python3
"""
Universal AI Manager - Comprehensive fallback system for all 16+ AI providers
Ensures maximum reliability and zero workflow failures due to API issues
"""

import asyncio
import json
import logging
import os
import random
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

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
    ANTHROPIC = "anthropic"
    MISTRAL = "mistral"
    PERPLEXITY = "perplexity"
    OPENAI = "openai"
    AZURE_OPENAI = "azure_openai"
    AWS_BEDROCK = "aws_bedrock"
    GOOGLE_CLOUD = "google_cloud"
    HUGGINGFACE = "huggingface"


@dataclass
class ProviderConfig:
    """Configuration for AI provider"""

    name: str
    api_key: str
    base_url: str
    model: str
    provider_type: ProviderType
    priority: int = 10  # Lower number means higher priority
    timeout: int = 30
    max_retries: int = 3
    max_tokens: int = 4096
    temperature: float = 0.7
    model_capabilities: List[str] = field(default_factory=list) # e.g., ['text_generation', 'code_completion']
    cost_per_token_input: float = 0.0 # Placeholder for cost management
    cost_per_token_output: float = 0.0 # Placeholder for cost management
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
            "model_capabilities": self.model_capabilities,
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
        """Initialize all 16+ AI providers from environment variables"""
        logger.info("🚀 Initializing Universal AI Manager with available providers...")

        # Helper to add provider if API key is present
        def _add_provider(provider_id: str, config: ProviderConfig):
            if config.api_key and config.api_key.strip():
                self.providers[provider_id] = config
                logger.info(f"  ✅ Loaded provider: {config.name}")
            else:
                logger.info(f"  ❌ Skipped provider {config.name}: API key not set.")

        # 1. DeepSeek
        _add_provider(
            "deepseek",
            ProviderConfig(
                name="DeepSeek V3.1",
                api_key=os.getenv("DEEPSEEK_API_KEY", ""),
                base_url="https://api.deepseek.com/v1",
                model="deepseek-chat",
                provider_type=ProviderType.OPENAI_COMPATIBLE,
                priority=1,
                max_tokens=8192,
                model_capabilities=['text_generation', 'code_generation', 'reasoning'],
            ),
        )

        # 2. GLM
        _add_provider(
            "glm",
            ProviderConfig(
                name="GLM 4.5 Air",
                api_key=os.getenv("GLM_API_KEY", ""),
                base_url="https://open.bigmodel.cn/api/paas/v4",
                model="glm-4-flash",
                provider_type=ProviderType.OPENAI_COMPATIBLE,
                priority=2,
                max_tokens=8192,
                model_capabilities=['text_generation', 'multilingual', 'summarization'],
            ),
        )

        # 3. Grok
        _add_provider(
            "grok",
            ProviderConfig(
                name="xAI Grok Beta",
                api_key=os.getenv("GROK_API_KEY", ""),
                base_url="https://api.openrouter.ai/v1",
                model="x-ai/grok-beta",
                provider_type=ProviderType.OPENAI_COMPATIBLE,
                priority=3,
                max_tokens=4096,
                model_capabilities=['text_generation', 'creative_writing', 'humor'],
            ),
        )

        # 4. Kimi
        _add_provider(
            "kimi",
            ProviderConfig(
                name="MoonshotAI Kimi",
                api_key=os.getenv("KIMI_API_KEY", ""),
                base_url="https://api.moonshot.cn/v1",
                model="moonshot-v1-8k",
                provider_type=ProviderType.OPENAI_COMPATIBLE,
                priority=4,
                max_tokens=8192,
                model_capabilities=['long_context', 'summarization', 'qa'],
            ),
        )

        # 5. Qwen
        _add_provider(
            "qwen",
            ProviderConfig(
                name="Qwen Plus",
                api_key=os.getenv("QWEN_API_KEY", ""),
                base_url="https://dashscope.aliyuncs.com/api/v1",
                model="qwen-plus",
                provider_type=ProviderType.OPENAI_COMPATIBLE,
                priority=5,
                max_tokens=8192,
                model_capabilities=['text_generation', 'multilingual', 'code_generation'],
            ),
        )

        # 6. GPT OSS (OpenRouter - GPT-4o)
        _add_provider(
            "gptoss",
            ProviderConfig(
                name="GPT OSS (OpenRouter)",
                api_key=os.getenv("GPTOSS_API_KEY", ""),
                base_url="https://api.openrouter.ai/v1",
                model="openai/gpt-4o",
                provider_type=ProviderType.OPENAI_COMPATIBLE,
                priority=6,
                max_tokens=4096,
                model_capabilities=['text_generation', 'reasoning', 'multimodal'],
            ),
        )

        # 7. Groq AI (primary)
        _add_provider(
            "groq_primary",
            ProviderConfig(
                name="Groq AI (Primary)",
                api_key=os.getenv("GROQAI_API_KEY", ""),
                base_url="https://api.groq.com/openai/v1",
                model="llama-3.3-70b-versatile",
                provider_type=ProviderType.GROQ,
                priority=7,
                max_tokens=8192,
                model_capabilities=['fast_inference', 'text_generation', 'code_generation'],
            ),
        )

        # 8. Cerebras
        _add_provider(
            "cerebras",
            ProviderConfig(
                name="Cerebras AI",
                api_key=os.getenv("CEREBRAS_API_KEY", ""),
                base_url="https://api.cerebras.ai/v1",
                model="llama3.1-8b",
                provider_type=ProviderType.CEREBRAS,
                priority=8,
                max_tokens=8192,
                model_capabilities=['text_generation', 'research'],
            ),
        )

        # 9. Gemini AI (primary)
        _add_provider(
            "gemini_primary",
            ProviderConfig(
                name="Gemini AI (Primary)",
                api_key=os.getenv("GEMINIAI_API_KEY", ""),
                base_url="https://generativelanguage.googleapis.com/v1beta",
                model="gemini-2.0-flash",
                provider_type=ProviderType.GEMINI,
                priority=9,
                max_tokens=8192,
                model_capabilities=['multimodal', 'text_generation', 'reasoning'],
            ),
        )

        # 10. Codestral
        _add_provider(
            "codestral",
            ProviderConfig(
                name="Codestral",
                api_key=os.getenv("CODESTRAL_API_KEY", ""),
                base_url="https://codestral.mistral.ai/v1",
                model="codestral-latest",
                provider_type=ProviderType.CODESTRAL,
                priority=10,
                max_tokens=4096,
                model_capabilities=['code_generation', 'code_completion', 'debugging'],
            ),
        )

        # 11. NVIDIA
        _add_provider(
            "nvidia",
            ProviderConfig(
                name="NVIDIA AI",
                api_key=os.getenv("NVIDIA_API_KEY", ""),
                base_url="https://integrate.api.nvidia.com/v1",
                model="deepseek-ai/deepseek-r1", # Example model
                provider_type=ProviderType.NVIDIA,
                priority=11,
                max_tokens=4096,
                model_capabilities=['text_generation', 'gpu_optimized', 'high_performance'],
            ),
        )

        # 12. Gemini 2 (secondary)
        _add_provider(
            "gemini_secondary",
            ProviderConfig(
                name="Gemini 2 (Secondary)",
                api_key=os.getenv("GEMINI2_API_KEY", ""),
                base_url="https://generativelanguage.googleapis.com/v1beta",
                model="gemini-2.0-flash",
                provider_type=ProviderType.GEMINI,
                priority=12,
                max_tokens=8192,
                model_capabilities=['multimodal', 'text_generation'],
            ),
        )

        # 13. Groq 2 (secondary)
        _add_provider(
            "groq_secondary",
            ProviderConfig(
                name="Groq 2 (Secondary)",
                api_key=os.getenv("GROQ2_API_KEY", ""),
                base_url="https://api.groq.com/openai/v1",
                model="llama-3.3-70b-versatile",
                provider_type=ProviderType.GROQ,
                priority=13,
                max_tokens=8192,
                model_capabilities=['fast_inference', 'text_generation'],
            ),
        )

        # 14. Cohere
        _add_provider(
            "cohere",
            ProviderConfig(
                name="Cohere",
                api_key=os.getenv("COHERE_API_KEY", ""),
                base_url="https://api.cohere.ai/v1",
                model="command-r-plus",
                provider_type=ProviderType.COHERE,
                priority=14,
                max_tokens=4096,
                model_capabilities=['text_generation', 'summarization', 'enterprise_grade'],
            ),
        )

        # 15. Chutes AI
        _add_provider(
            "chutes",
            ProviderConfig(
                name="Chutes AI",
                api_key=os.getenv("CHUTES_API_KEY", ""),
                base_url="https://llm.chutes.ai/v1",
                model="zai-org/GLM-4.5-Air",
                provider_type=ProviderType.CHUTES,
                priority=15,
                max_tokens=1024,
                model_capabilities=['text_generation', 'specialized_tasks'],
            ),
        )

        # 16. Anthropic
        _add_provider(
            "anthropic",
            ProviderConfig(
                name="Anthropic Claude",
                api_key=os.getenv("ANTHROPIC_API_KEY", ""),
                base_url="https://api.anthropic.com/v1",
                model="claude-3-opus-20240229",
                provider_type=ProviderType.ANTHROPIC,
                priority=16,
                max_tokens=4096,
                model_capabilities=['text_generation', 'reasoning', 'safety'],
            ),
        )

        # 17. Mistral
        _add_provider(
            "mistral",
            ProviderConfig(
                name="Mistral AI",
                api_key=os.getenv("MISTRAL_API_KEY", ""),
                base_url="https://api.mistral.ai/v1",
                model="mistral-large-latest",
                provider_type=ProviderType.MISTRAL,
                priority=17,
                max_tokens=8192,
                model_capabilities=['text_generation', 'code_generation', 'multilingual'],
            ),
        )

        # 18. Perplexity AI
        _add_provider(
            "perplexity",
            ProviderConfig(
                name="Perplexity AI",
                api_key=os.getenv("PERPLEXITY_API_KEY", ""),
                base_url="https://api.perplexity.ai",
                model="llama-3-sonar-large-32k-online",
                provider_type=ProviderType.PERPLEXITY,
                priority=18,
                max_tokens=8192,
                model_capabilities=['realtime_search', 'qa', 'summarization'],
            ),
        )

        # 19. OpenAI
        _add_provider(
            "openai",
            ProviderConfig(
                name="OpenAI",
                api_key=os.getenv("OPENAI_API_KEY", ""),
                base_url="https://api.openai.com/v1",
                model="gpt-4o",
                provider_type=ProviderType.OPENAI,
                priority=19,
                max_tokens=4096,
                model_capabilities=['text_generation', 'reasoning', 'multimodal'],
            ),
        )

        # 20. Azure OpenAI
        _add_provider(
            "azure_openai",
            ProviderConfig(
                name="Azure OpenAI",
                api_key=os.getenv("AZURE_OPENAI_API_KEY", ""),
                base_url=os.getenv("AZURE_OPENAI_BASE_URL", ""), # Azure requires full endpoint URL
                model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o-deployment"), # Deployment name is the model
                provider_type=ProviderType.AZURE_OPENAI,
                priority=20,
                max_tokens=4096,
                model_capabilities=['text_generation', 'enterprise_grade', 'security'],
            ),
        )

        # 21. AWS Bedrock (Example for a specific model)
        _add_provider(
            "aws_bedrock",
            ProviderConfig(
                name="AWS Bedrock (Claude)",
                api_key=os.getenv("AWS_ACCESS_KEY_ID", ""), # AWS keys are different
                base_url=os.getenv("AWS_REGION_NAME", "us-east-1"), # Region is base_url here
                model="anthropic.claude-3-sonnet-v1:0",
                provider_type=ProviderType.AWS_BEDROCK,
                priority=21,
                max_tokens=4096,
                model_capabilities=['text_generation', 'enterprise_grade', 'scalability'],
            ),
        )

        # 22. Google Cloud Vertex AI (Example for a specific model)
        _add_provider(
            "google_cloud",
            ProviderConfig(
                name="Google Cloud Vertex AI (Gemini)",
                api_key=os.getenv("GOOGLE_APPLICATION_CREDENTIALS", ""), # Path to service account key file
                base_url=os.getenv("GOOGLE_CLOUD_PROJECT_ID", ""), # Project ID
                model="gemini-1.5-flash-001",
                provider_type=ProviderType.GOOGLE_CLOUD,
                priority=22,
                max_tokens=8192,
                model_capabilities=['text_generation', 'multimodal', 'enterprise_grade'],
            ),
        )

        # 23. HuggingFace Inference API
        _add_provider(
            "huggingface",
            ProviderConfig(
                name="HuggingFace Inference API",
                api_key=os.getenv("HUGGINGFACE_API_KEY", ""),
                base_url="https://api-inference.huggingface.co/models",
                model="mistralai/Mistral-7B-Instruct-v0.2", # Example model
                provider_type=ProviderType.HUGGINGFACE,
                priority=23,
                max_tokens=4096,
                model_capabilities=['text_generation', 'open_source'],
            ),
        )

        if not self.providers:
            logger.error("🚨 No AI providers were loaded. Please check your environment variables.")
            return

        # Start health check loop
        asyncio.create_task(self._health_check_loop())

        logger.info(f"🎉 Universal AI Manager initialized with {len(self.providers)} providers.")

    async def _health_check_loop(self, interval: int = 300):
        """Periodically check the health of all providers."""
        while True:
            logger.info("🩺 Starting periodic health check of all providers...")
            await self.update_all_provider_statuses()
            await asyncio.sleep(interval)

    async def update_all_provider_statuses(self):
        """Update the status of all configured providers."""
        tasks = [self.check_provider_health(p) for p in self.providers.keys()]
        await asyncio.gather(*tasks)
        self._update_active_providers()

    async def check_provider_health(self, provider_id: str):
        """Check the health of a specific provider."""
        config = self.providers.get(provider_id)
        if not config:
            return

        # If provider is rate-limited, check if the timeout has passed
        if config.rate_limit_until and datetime.now() < config.rate_limit_until:
            config.status = ProviderStatus.RATE_LIMITED
            return

        config.status = ProviderStatus.TESTING
        try:
            # Use a simple, non-intrusive prompt for health check
            response = await self._make_request(
                provider_id, messages=[{"role": "user", "content": "Health check"}], max_tokens=10
            )
            if response["success"]:
                config.status = ProviderStatus.ACTIVE
                config.consecutive_failures = 0
                logger.info(f"💚 {config.name} is ACTIVE.")
            else:
                config.status = ProviderStatus.FAILED
                config.last_error = response.get("error", "Health check failed")
                logger.warning(f"💛 {config.name} is FAILED: {config.last_error}")
        except Exception as e:
            config.status = ProviderStatus.FAILED
            config.last_error = str(e)
            logger.error(f"❤️ {config.name} is FAILED with exception: {e}")

    def _update_active_providers(self):
        """Update the list of active providers based on status and priority."""
        active = [
            p
            for p, config in self.providers.items()
            if config.status == ProviderStatus.ACTIVE
        ]
        # Sort by priority (lower is better)
        self.active_providers = sorted(active, key=lambda p: self.providers[p].priority)
        logger.info(f"Active providers updated: {self.active_providers}")

    def get_active_providers(self) -> List[Dict[str, Any]]:
        """Get a list of currently active providers."""
        return [self.providers[p].to_dict() for p in self.active_providers]

    async def generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Generate a response from the best available AI provider.

        Args:
            prompt: The user prompt.
            system_prompt: An optional system prompt.
            **kwargs: Additional parameters for the request, including:
                - `strategy`: `priority`, `random`, `least_used`, `fastest`
                - `preferred_apis`: List of provider IDs to try first.
                - `allowed_apis`: List of provider IDs to restrict to.
                - `max_attempts`: Maximum number of providers to try.
                - `task_type`: e.g., 'code_generation', 'summarization' for capability-based routing.

        Returns:
            A dictionary with the response and metadata.
        """
        self.global_stats["total_requests"] += 1
        start_time = time.time()

        # Extract routing parameters from kwargs
        strategy = kwargs.pop("strategy", "priority")
        preferred_apis = kwargs.pop("preferred_apis", [])
        allowed_apis = kwargs.pop("allowed_apis", [])
        max_attempts = kwargs.pop("max_attempts", None)
        task_type = kwargs.pop("task_type", None)

        # Prepare messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Determine max attempts
        if max_attempts is None:
            max_attempts = len(self.active_providers)

        # Create a shuffled list of providers to try, based on strategy and filters
        providers_to_try = []
        if preferred_apis:
            # Add preferred APIs first, maintaining their order if strategy is priority
            for pref_api in preferred_apis:
                # Find provider_id by name or alias
                found_pid = None
                for pid, config in self.providers.items():
                    if pid == pref_api or config.name.lower() == pref_api.lower() or config.model.lower() == pref_api.lower():
                        found_pid = pid
                        break
                if found_pid and found_pid in self.active_providers:
                    providers_to_try.append(found_pid)

        # Filter providers based on allowed_apis and task_type
        candidate_providers = self.active_providers
        if allowed_apis:
            candidate_providers = [p for p in candidate_providers if p in allowed_apis]
        if task_type:
            candidate_providers = [
                p for p in candidate_providers if task_type in self.providers[p].model_capabilities
            ]

        # Apply strategy to the remaining candidates
        if strategy == "random":
            random.shuffle(candidate_providers)
        elif strategy == "least_used":
            candidate_providers.sort(key=lambda p: self.providers[p].success_count)
        elif strategy == "fastest":
            candidate_providers.sort(key=lambda p: self.providers[p].avg_response_time)
        # 'priority' is the default and is already sorted

        # Combine preferred and candidate providers, avoiding duplicates
        final_providers_to_try = []
        seen = set()
        for p in providers_to_try + candidate_providers:
            if p not in seen:
                final_providers_to_try.append(p)
                seen.add(p)

        if not final_providers_to_try:
            self.global_stats["failed_requests"] += 1
            logger.error("❌ ALL AI PROVIDERS FAILED! No providers available after filtering.")
            return {
                "success": False,
                "error": "All AI providers failed or no suitable providers found",
                "provider": "none",
                "provider_name": "All Providers Failed",
                "attempts": 0,
                "stats": self.get_stats(),
            }

        # Try providers with fallback
        for attempt, provider_id in enumerate(final_providers_to_try):
            if attempt >= max_attempts: # Respect max_attempts
                break
            config = self.providers[provider_id]
            logger.info(
                f'🤖 Attempting with {config.name} (attempt {attempt + 1}/{len(final_providers_to_try)}) for task type "{task_type or "general"}".'
            )
            try:
                result = await self._make_request(provider_id, messages, **kwargs)
                if result["success"]:
                    # Update success stats
                    config.success_count += 1
                    config.consecutive_failures = 0
                    config.last_used = datetime.now()
                    config.status = ProviderStatus.ACTIVE

                    # Update average response time (exponential moving average for smoother updates)
                    alpha = 0.1 # Smoothing factor
                    if config.avg_response_time == 0:
                        config.avg_response_time = result["response_time"]
                    else:
                        config.avg_response_time = (alpha * result["response_time"]) + ((1 - alpha) * config.avg_response_time)

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
                        f'✅ Success with {config.name} in {result["response_time"]:.2f}s'
                    )
                    return result
                else:
                    # Update failure stats
                    config.failure_count += 1
                    config.consecutive_failures += 1
                    config.last_error = result.get("error", "Unknown error")
                    config.status = ProviderStatus.FAILED
                    logger.warning(
                        f'❌ {config.name} failed: {result.get("error", "Unknown error")}'
                    )
            except Exception as e:
                config.failure_count += 1
                config.consecutive_failures += 1
                config.last_error = str(e)
                config.status = ProviderStatus.FAILED
                logger.error(f"❌ Exception with {config.name}: {e}")

        # All providers failed
        self.global_stats["failed_requests"] += 1
        logger.error("❌ ALL AI PROVIDERS FAILED after all attempts!")
        return {
            "success": False,
            "error": "All AI providers failed after all attempts",
            "provider": "none",
            "provider_name": "All Providers Failed",
            "attempts": len(final_providers_to_try),
            "stats": self.get_stats(),
        }

    async def get_status(self) -> Dict[str, Any]:
        """
        Get overall status of the Universal AI Manager.
        """
        return {
            "status": "active" if self.active_providers else "inactive",
            "active_providers_count": len(self.active_providers),
            "total_providers_configured": len(self.providers),
            "global_stats": self.get_stats(),
            "active_providers": self.get_active_providers(),
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get detailed global statistics."""
        total_reqs = self.global_stats["total_requests"]
        success_rate = (
            (self.global_stats["successful_requests"] / total_reqs) * 100
            if total_reqs > 0
            else 0
        )
        uptime = (datetime.now() - self.global_stats["uptime"]).total_seconds()

        return {
            "total_requests": total_reqs,
            "successful_requests": self.global_stats["successful_requests"],
            "failed_requests": self.global_stats["failed_requests"],
            "success_rate": f"{success_rate:.1f}%",
            "total_fallbacks": self.global_stats["total_fallbacks"],
            "average_response_time": f'{self.global_stats["average_response_time"]:.2f}s',
            "providers_usage": self.global_stats["providers_usage"],
            "uptime_seconds": uptime,
            "last_reset": self.global_stats["last_reset"].isoformat(),
        }

    def reset_stats(self):
        """Reset all statistics."""
        self.global_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_fallbacks": 0,
            "providers_usage": {},
            "average_response_time": 0,
            "total_response_time": 0,
            "last_reset": datetime.now(),
            "uptime": self.global_stats["uptime"], # Keep original uptime
        }
        for provider in self.providers.values():
            provider.success_count = 0
            provider.failure_count = 0
            provider.avg_response_time = 0
        logger.info("📊 Statistics have been reset.")

    async def _make_request(
        self, provider_id: str, messages: List[Dict[str, str]], **kwargs
    ) -> Dict[str, Any]:
        """Make a request to a specific provider."""
        config = self.providers[provider_id]
        start_time = time.time()

        try:
            handler = self._get_provider_handler(config.provider_type)
            response = await handler(config, messages, **kwargs)
            response_time = time.time() - start_time
            response["response_time"] = response_time
            return response
        except Exception as e:
            response_time = time.time() - start_time
            return {
                "success": False,
                "error": str(e),
                "provider": provider_id,
                "provider_name": config.name,
                "response_time": response_time,
            }

    def _get_provider_handler(self, provider_type: ProviderType):
        """Get the appropriate handler for a provider type."""
        if provider_type == ProviderType.OPENAI_COMPATIBLE:
            return self._handle_openai_compatible
        elif provider_type == ProviderType.GROQ:
            return self._handle_groq
        elif provider_type == ProviderType.CEREBRAS:
            return self._handle_cerebras
        elif provider_type == ProviderType.GEMINI:
            return self._handle_gemini
        elif provider_type == ProviderType.NVIDIA:
            return self._handle_nvidia
        elif provider_type == ProviderType.COHERE:
            return self._handle_cohere
        elif provider_type == ProviderType.CHUTES:
            return self._handle_chutes
        elif provider_type == ProviderType.CODESTRAL:
            return self._handle_codestral
        elif provider_type == ProviderType.ANTHROPIC:
            return self._handle_anthropic
        elif provider_type == ProviderType.MISTRAL:
            return self._handle_mistral
        elif provider_type == ProviderType.PERPLEXITY:
            return self._handle_perplexity
        elif provider_type == ProviderType.OPENAI:
            return self._handle_openai
        elif provider_type == ProviderType.AZURE_OPENAI:
            return self._handle_azure_openai
        elif provider_type == ProviderType.AWS_BEDROCK:
            return self._handle_aws_bedrock
        elif provider_type == ProviderType.GOOGLE_CLOUD:
            return self._handle_google_cloud
        elif provider_type == ProviderType.HUGGINGFACE:
            return self._handle_huggingface
        else:
            raise ValueError(f"Unsupported provider type: {provider_type}")

    # --- Provider-specific handlers ---

    async def _handle_openai_compatible(
        self, config: ProviderConfig, messages: List[Dict[str, str]], **kwargs
    ) -> Dict[str, Any]:
        """Handler for OpenAI-compatible APIs."""
        headers = {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": config.model,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", config.max_tokens),
            "temperature": kwargs.get("temperature", config.temperature),
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{config.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=config.timeout,
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {
                        "success": True,
                        "content": data["choices"][0]["message"]["content"],
                        "provider": config.name,
                        "tokens_used": data.get("usage", {}).get("total_tokens", 0),
                    }
                else:
                    error_text = await resp.text()
                    return {
                        "success": False,
                        "error": f"HTTP {resp.status}: {error_text}",
                    }

    async def _handle_groq(
        self, config: ProviderConfig, messages: List[Dict[str, str]], **kwargs
    ) -> Dict[str, Any]:
        """Handler for Groq API."""
        # Groq is OpenAI compatible, so we can reuse the handler
        return await self._handle_openai_compatible(config, messages, **kwargs)

    async def _handle_cerebras(
        self, config: ProviderConfig, messages: List[Dict[str, str]], **kwargs
    ) -> Dict[str, Any]:
        """Handler for Cerebras API."""
        # Cerebras is also OpenAI compatible
        return await self._handle_openai_compatible(config, messages, **kwargs)

    async def _handle_gemini(
        self, config: ProviderConfig, messages: List[Dict[str, str]], **kwargs
    ) -> Dict[str, Any]:
        """Handler for Gemini API."""
        headers = {
            "Content-Type": "application/json",
        }
        # Gemini has a different message format
        contents = []
        for msg in messages:
            contents.append({"role": msg["role"], "parts": [{"text": msg["content"]}]})

        payload = {
            "contents": contents,
            "generationConfig": {
                "maxOutputTokens": kwargs.get("max_tokens", config.max_tokens),
                "temperature": kwargs.get("temperature", config.temperature),
            },
        }

        url = f"{config.base_url}/models/{config.model}:generateContent?key={config.api_key}"

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=config.timeout) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {
                        "success": True,
                        "content": data["candidates"][0]["content"]["parts"][0]["text"],
                        "provider": config.name,
                        "tokens_used": data.get("usageMetadata", {}).get("totalTokenCount", 0),
                    }
                else:
                    error_text = await resp.text()
                    return {
                        "success": False,
                        "error": f"HTTP {resp.status}: {error_text}",
                    }

    async def _handle_nvidia(
        self, config: ProviderConfig, messages: List[Dict[str, str]], **kwargs
    ) -> Dict[str, Any]:
        """Handler for NVIDIA API."""
        # NVIDIA is OpenAI compatible
        return await self._handle_openai_compatible(config, messages, **kwargs)

    async def _handle_cohere(
        self, config: ProviderConfig, messages: List[Dict[str, str]], **kwargs
    ) -> Dict[str, Any]:
        """Handler for Cohere API."""
        headers = {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
        }
        # Cohere has a different message format
        chat_history = []
        prompt = ""
        for i, msg in enumerate(messages):
            if i == len(messages) - 1:
                prompt = msg["content"]
            else:
                chat_history.append({"role": msg["role"].upper(), "message": msg["content"]})

        payload = {
            "model": config.model,
            "message": prompt,
            "chat_history": chat_history,
            "max_tokens": kwargs.get("max_tokens", config.max_tokens),
            "temperature": kwargs.get("temperature", config.temperature),
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{config.base_url}/chat", headers=headers, json=payload, timeout=config.timeout
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {
                        "success": True,
                        "content": data["text"],
                        "provider": config.name,
                        "tokens_used": data.get("meta", {}).get("tokens", {}).get("output_tokens", 0),
                    }
                else:
                    error_text = await resp.text()
                    return {
                        "success": False,
                        "error": f"HTTP {resp.status}: {error_text}",
                    }

    async def _handle_chutes(
        self, config: ProviderConfig, messages: List[Dict[str, str]], **kwargs
    ) -> Dict[str, Any]:
        """Handler for Chutes AI API."""
        # Chutes is OpenAI compatible
        return await self._handle_openai_compatible(config, messages, **kwargs)

    async def _handle_codestral(
        self, config: ProviderConfig, messages: List[Dict[str, str]], **kwargs
    ) -> Dict[str, Any]:
        """Handler for Codestral API."""
        # Codestral is OpenAI compatible
        return await self._handle_openai_compatible(config, messages, **kwargs)

    async def _handle_anthropic(
        self, config: ProviderConfig, messages: List[Dict[str, str]], **kwargs
    ) -> Dict[str, Any]:
        """Handler for Anthropic API."""
        headers = {
            "x-api-key": config.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        payload = {
            "model": config.model,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", config.max_tokens),
            "temperature": kwargs.get("temperature", config.temperature),
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{config.base_url}/messages", headers=headers, json=payload, timeout=config.timeout
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {
                        "success": True,
                        "content": data["content"][0]["text"],
                        "provider": config.name,
                        "tokens_used": data.get("usage", {}).get("input_tokens", 0)
                        + data.get("usage", {}).get("output_tokens", 0),
                    }
                else:
                    error_text = await resp.text()
                    return {
                        "success": False,
                        "error": f"HTTP {resp.status}: {error_text}",
                    }

    async def _handle_mistral(
        self, config: ProviderConfig, messages: List[Dict[str, str]], **kwargs
    ) -> Dict[str, Any]:
        """Handler for Mistral API."""
        # Mistral is OpenAI compatible
        return await self._handle_openai_compatible(config, messages, **kwargs)

    async def _handle_perplexity(
        self, config: ProviderConfig, messages: List[Dict[str, str]], **kwargs
    ) -> Dict[str, Any]:
        """Handler for Perplexity API."""
        # Perplexity is OpenAI compatible
        return await self._handle_openai_compatible(config, messages, **kwargs)

    async def _handle_openai(
        self, config: ProviderConfig, messages: List[Dict[str, str]], **kwargs
    ) -> Dict[str, Any]:
        """Handler for OpenAI API."""
        return await self._handle_openai_compatible(config, messages, **kwargs)

    async def _handle_azure_openai(
        self, config: ProviderConfig, messages: List[Dict[str, str]], **kwargs
    ) -> Dict[str, Any]:
        """Handler for Azure OpenAI API."""
        headers = {
            "api-key": config.api_key,
            "Content-Type": "application/json",
        }
        # Azure URL already includes the deployment name (model)
        url = f"{config.base_url}/openai/deployments/{config.model}/chat/completions?api-version=2023-05-15"
        payload = {
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", config.max_tokens),
            "temperature": kwargs.get("temperature", config.temperature),
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=config.timeout) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {
                        "success": True,
                        "content": data["choices"][0]["message"]["content"],
                        "provider": config.name,
                        "tokens_used": data.get("usage", {}).get("total_tokens", 0),
                    }
                else:
                    error_text = await resp.text()
                    return {
                        "success": False,
                        "error": f"HTTP {resp.status}: {error_text}",
                    }

    async def _handle_aws_bedrock(
        self, config: ProviderConfig, messages: List[Dict[str, str]], **kwargs
    ) -> Dict[str, Any]:
        """Handler for AWS Bedrock API (using aiobotocore)."""
        # This is a simplified example. A full implementation would require
        # setting up aiobotocore with credentials.
        # For now, we will raise a NotImplementedError.
        raise NotImplementedError("AWS Bedrock handler is not fully implemented yet.")

    async def _handle_google_cloud(
        self, config: ProviderConfig, messages: List[Dict[str, str]], **kwargs
    ) -> Dict[str, Any]:
        """Handler for Google Cloud Vertex AI API."""
        # This is a simplified example. A full implementation would require
        # google-cloud-aiplatform library and authentication.
        # For now, we will raise a NotImplementedError.
        raise NotImplementedError("Google Cloud Vertex AI handler is not fully implemented yet.")

    async def _handle_huggingface(
        self, config: ProviderConfig, messages: List[Dict[str, str]], **kwargs
    ) -> Dict[str, Any]:
        """Handler for HuggingFace Inference API."""
        headers = {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
        }

        # HuggingFace Inference API often expects a simple string input or specific chat formats
        # This example assumes a simple text generation task.
        # For chat models, you might need to format messages into a single prompt string.
        formatted_prompt = "\n".join([f'{msg["role"]}: {msg["content"]}' for msg in messages])

        payload = {
            "inputs": formatted_prompt,
            "parameters": {
                "max_new_tokens": kwargs.get("max_tokens", config.max_tokens),
                "temperature": kwargs.get("temperature", config.temperature),
            },
        }

        url = f"{config.base_url}/{config.model}"

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=config.timeout) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    # The response format can vary greatly between models on HuggingFace
                    # This is a common format for text generation models
                    generated_text = data[0].get("generated_text", "")
                    # The API might return the original prompt in the response, so we remove it.
                    if generated_text.startswith(formatted_prompt):
                        generated_text = generated_text[len(formatted_prompt):].strip()

                    return {
                        "success": True,
                        "content": generated_text,
                        "provider": config.name,
                        "tokens_used": 0,  # HF API doesn't typically provide token usage
                    }
                else:
                    error_text = await resp.text()
                    return {
                        "success": False,
                        "error": f"HTTP {resp.status}: {error_text}",
                    }

# --- Singleton instance ---

_universal_ai_manager_instance: Optional[UniversalAIManager] = None


def get_universal_ai_manager() -> UniversalAIManager:
    """
    Returns a singleton instance of the UniversalAIManager.
    """
    global _universal_ai_manager_instance
    if _universal_ai_manager_instance is None:
        _universal_ai_manager_instance = UniversalAIManager()
    return _universal_ai_manager_instance


async def main():
    """Main function to demonstrate the UniversalAIManager."""
    ai_manager = get_universal_ai_manager()

    # Wait for initial health checks to complete
    await asyncio.sleep(5)

    print("--- System Status ---")
    status = await ai_manager.get_status()
    print(json.dumps(status, indent=2))

    print("\n--- Generating a response ---")
    prompt = "Write a short story about a robot who discovers music."
    response = await ai_manager.generate_response(prompt, system_prompt="You are a creative writer.")

    if response["success"]:
        print(f"Provider: {response['provider_name']}")
        print(f"Response Time: {response['response_time']:.2f}s")
        print(f"Content:\n{response['content']}")
    else:
        print(f"Failed to get a response: {response['error']}")

    print("\n--- System Stats ---")
    stats = ai_manager.get_stats()
    print(json.dumps(stats, indent=2))

if __name__ == "__main__":
    asyncio.run(main())

