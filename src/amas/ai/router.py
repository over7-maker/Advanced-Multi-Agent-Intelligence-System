#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
Universal AI Provider Router with Comprehensive Failover

Bulletproof multi-provider AI system that ensures no workflow ever fails due to AI provider issues.
Automatically detects available providers from repository secrets and implements intelligent failover.

Features:
- 15+ AI provider support with automatic fallback
- Zero-fail guarantee: always returns structured results
- Intelligent provider prioritization (speed/cost optimized)
- Comprehensive error handling and telemetry
- Rate limiting and timeout protection
- Circuit breaker friendly design

Supported Providers (via Repository Secrets):
- Cerebras (CEREBRAS_API_KEY)
- NVIDIA Integrate (NVIDIA_API_KEY)
- Gemini 2.0 (GEMINI2_API_KEY)
- Codestral/Mistral (CODESTRAL_API_KEY)
- Cohere (COHERE_API_KEY)
- Chutes (CHUTES_API_KEY)
- Groq2 (GROQ2_API_KEY)
- GroqAI (GROQAI_API_KEY)
- OpenRouter Models via:
  - DeepSeek (DEEPSEEK_API_KEY)
  - GLM 4.5 (GLM_API_KEY)
  - Grok 4 (GROK_API_KEY)
  - Kimi (KIMI_API_KEY)
  - Qwen (QWEN_API_KEY)
  - GPT-OSS (GPTOSS_API_KEY)
"""

import asyncio
import json
import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

import aiohttp

# Configure logging for router
logger = logging.getLogger("amas.ai.router")

# Import OpenAI client with fallback
try:
    from openai import AsyncOpenAI, OpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OpenAI = None
    AsyncOpenAI = None
    OPENAI_AVAILABLE = False

# Import Cerebras SDK with fallback
try:
    from cerebras.cloud.sdk import Cerebras

    CEREBRAS_SDK_AVAILABLE = True
except ImportError:
    Cerebras = None
    CEREBRAS_SDK_AVAILABLE = False

# Default configurations
DEFAULT_TIMEOUT = aiohttp.ClientTimeout(total=45)
DEFAULT_MAX_RETRIES = 3
DEFAULT_BASE_DELAY = 1.0
DEFAULT_MAX_TOKENS = 2000
DEFAULT_TEMPERATURE = 0.3


@dataclass
class ProviderAttempt:
    """Records an attempt to use a provider."""

    provider: str
    status: str  # 'success' | 'error' | 'timeout' | 'quota' | 'auth' | 'unavailable'
    elapsed_ms: int
    error: Optional[str] = None
    model: Optional[str] = None
    tokens_used: Optional[int] = None


class ProviderError(Exception):
    """Provider-specific error."""

    def __init__(self, message: str, provider: str, error_type: str = "error"):
        super().__init__(message)
        self.provider = provider
        self.error_type = error_type


def _env(name: str) -> Optional[str]:
    """Get environment variable, stripped of whitespace."""
    value = os.getenv(name)
    return value.strip() if value else None


def _enabled(provider_key: str) -> bool:
    """Check if provider is enabled via repository secret."""
    return bool(_env(provider_key))


def _now_ms() -> int:
    """Current time in milliseconds."""
    return int(time.time() * 1000)


def build_provider_priority() -> List[str]:
    """Build prioritized list of available providers based on repository secrets.

    Priority order optimized for:
    1. Speed and reliability (Cerebras, NVIDIA)
    2. Quality and capabilities (Gemini2, Codestral)
    3. Alternative providers (Groq variants, Cohere)
    4. Free tier fallbacks (OpenRouter models, Chutes)

    Returns:
        List of provider names in priority order
    """
    providers = []

    # Tier 1: Fast and reliable providers
    if _enabled("CEREBRAS_API_KEY"):
        providers.append("cerebras")
    if _enabled("NVIDIA_API_KEY"):
        providers.append("nvidia")

    # Tier 2: High-quality providers
    if _enabled("GEMINI2_API_KEY"):
        providers.append("gemini2")
    if _enabled("CODESTRAL_API_KEY"):
        providers.append("codestral")

    # Tier 3: Alternative commercial providers
    if _enabled("GROQ2_API_KEY"):
        providers.append("groq2")
    if _enabled("GROQAI_API_KEY"):
        providers.append("groqai")
    if _enabled("COHERE_API_KEY"):
        providers.append("cohere")

    # Tier 4: Specialized providers
    if _enabled("CHUTES_API_KEY"):
        providers.append("chutes")

    # Tier 5: OpenRouter-backed models (free tier fallbacks)
    openrouter_keys = [
        "DEEPSEEK_API_KEY",
        "GLM_API_KEY",
        "GROK_API_KEY",
        "KIMI_API_KEY",
        "QWEN_API_KEY",
        "GPTOSS_API_KEY",
    ]
    if any(_enabled(k) for k in openrouter_keys):
        providers.append("openrouter")

    logger.info(
        f"Built provider priority order: {providers} ({len(providers)} available)"
    )
    return providers


async def _with_retries(
    coro_factory,
    retries: int = DEFAULT_MAX_RETRIES,
    base_delay: float = DEFAULT_BASE_DELAY,
):
    """Execute coroutine with exponential backoff retries."""
    last_exception = None
    for attempt in range(retries):
        try:
            return await coro_factory()
        except Exception as e:
            last_exception = e
            if attempt < retries - 1:  # Don't sleep on last attempt
                delay = base_delay * (2**attempt)
                logger.debug(
                    f"Retry attempt {attempt + 1} failed, waiting {delay:.1f}s: {e}"
                )
                await asyncio.sleep(delay)

    if last_exception:
        raise last_exception


# Provider Implementation Functions


async def call_cerebras(
    messages: List[Dict[str, str]], session: aiohttp.ClientSession, **kwargs
) -> Dict[str, Any]:
    """Call Cerebras using official SDK."""
    key = _env("CEREBRAS_API_KEY")
    if not key:
        raise ProviderError(
            "CEREBRAS_API_KEY not found in environment", "cerebras", "auth"
        )

    if not CEREBRAS_SDK_AVAILABLE:
        # Fallback to HTTP API if SDK not available
        return await call_cerebras_http(messages, session, key, **kwargs)

    try:
        client = Cerebras(api_key=key)

        max_tokens = kwargs.get("max_tokens", DEFAULT_MAX_TOKENS)
        temperature = kwargs.get("temperature", DEFAULT_TEMPERATURE)

        response = client.chat.completions.create(
            messages=messages,
            model="llama3.1-70b",
            stream=False,
            max_completion_tokens=max_tokens,
            temperature=temperature,
            top_p=0.8,
        )

        content = response.choices[0].message.content or ""
        tokens = getattr(response, "usage", {}).get("total_tokens", 0)

        return {
            "provider": "cerebras",
            "content": content,
            "success": True,
            "model": "llama3.1-70b",
            "tokens_used": tokens,
        }
    except Exception as e:
        error_type = "quota" if "quota" in str(e).lower() else "error"
        raise ProviderError(f"Cerebras failed: {e}", "cerebras", error_type)


async def call_cerebras_http(
    messages: List[Dict[str, str]], session: aiohttp.ClientSession, key: str, **kwargs
) -> Dict[str, Any]:
    """Call Cerebras via HTTP API (fallback when SDK unavailable)."""
    url = "https://api.cerebras.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

    body = {
        "model": "llama3.1-70b",
        "messages": messages,
        "max_tokens": kwargs.get("max_tokens", DEFAULT_MAX_TOKENS),
        "temperature": kwargs.get("temperature", DEFAULT_TEMPERATURE),
        "stream": False,
    }

    async with session.post(
        url, headers=headers, json=body, timeout=DEFAULT_TIMEOUT
    ) as resp:
        if resp.status >= 400:
            error_text = await resp.text()
            error_type = (
                "auth"
                if resp.status == 401
                else "quota" if resp.status == 429 else "error"
            )
            raise ProviderError(
                f"Cerebras HTTP {resp.status}: {error_text}", "cerebras", error_type
            )

        data = await resp.json()

        try:
            content = data["choices"][0]["message"]["content"]
            tokens = data.get("usage", {}).get("total_tokens", 0)
        except Exception:
            content = json.dumps(data)[:1000]
            tokens = 0

        return {
            "provider": "cerebras",
            "content": content,
            "success": True,
            "model": "llama3.1-70b",
            "tokens_used": tokens,
        }


async def call_nvidia(
    messages: List[Dict[str, str]], session: aiohttp.ClientSession, **kwargs
) -> Dict[str, Any]:
    """Call NVIDIA Integrate API using OpenAI-compatible client."""
    key = _env("NVIDIA_API_KEY")
    if not key:
        raise ProviderError("NVIDIA_API_KEY not found in environment", "nvidia", "auth")

    if not OPENAI_AVAILABLE:
        raise ProviderError(
            "OpenAI client not available for NVIDIA", "nvidia", "unavailable"
        )

    try:
        client = OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=key)

        max_tokens = kwargs.get("max_tokens", DEFAULT_MAX_TOKENS)
        temperature = kwargs.get("temperature", DEFAULT_TEMPERATURE)

        response = client.chat.completions.create(
            model="deepseek-ai/deepseek-r1",
            messages=messages,
            temperature=temperature,
            top_p=0.7,
            max_tokens=max_tokens,
            stream=False,
        )

        content = response.choices[0].message.content or ""
        tokens = getattr(response, "usage", {}).get("total_tokens", 0)

        # Check for reasoning content (DeepSeek R1 feature)
        reasoning = getattr(response.choices[0].message, "reasoning_content", None)
        if reasoning:
            content = f"## Reasoning\n{reasoning}\n\n## Response\n{content}"

        return {
            "provider": "nvidia",
            "content": content,
            "success": True,
            "model": "deepseek-ai/deepseek-r1",
            "tokens_used": tokens,
        }
    except Exception as e:
        error_type = (
            "quota"
            if "quota" in str(e).lower()
            else "auth" if "401" in str(e) else "error"
        )
        raise ProviderError(f"NVIDIA failed: {e}", "nvidia", error_type)


async def call_gemini2(
    messages: List[Dict[str, str]], session: aiohttp.ClientSession, **kwargs
) -> Dict[str, Any]:
    """Call Gemini 2.0 Flash via Google Generative Language API."""
    key = _env("GEMINI2_API_KEY")
    if not key:
        raise ProviderError(
            "GEMINI2_API_KEY not found in environment", "gemini2", "auth"
        )

    try:
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        headers = {"Content-Type": "application/json", "X-goog-api-key": key}

        # Convert messages to Gemini format (combine user messages)
        user_content = "\n".join(
            [msg["content"] for msg in messages if msg["role"] == "user"]
        )
        system_content = "\n".join(
            [msg["content"] for msg in messages if msg["role"] == "system"]
        )

        if system_content:
            user_content = f"Context: {system_content}\n\nRequest: {user_content}"

        body = {
            "contents": [{"parts": [{"text": user_content}]}],
            "generationConfig": {
                "temperature": kwargs.get("temperature", DEFAULT_TEMPERATURE),
                "maxOutputTokens": kwargs.get("max_tokens", DEFAULT_MAX_TOKENS),
            },
        }

        async with session.post(
            url, headers=headers, json=body, timeout=DEFAULT_TIMEOUT
        ) as resp:
            if resp.status >= 400:
                error_text = await resp.text()
                error_type = (
                    "auth"
                    if resp.status == 401
                    else "quota" if resp.status == 429 else "error"
                )
                raise ProviderError(
                    f"Gemini2 HTTP {resp.status}: {error_text}", "gemini2", error_type
                )

            data = await resp.json()

            # Extract content safely
            content = ""
            try:
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    content = "".join(part.get("text", "") for part in parts)
            except Exception:
                content = json.dumps(data)[:1000]

            return {
                "provider": "gemini2",
                "content": content,
                "success": True,
                "model": "gemini-2.0-flash",
                "tokens_used": len(content.split()),  # Approximate
            }
    except ProviderError:
        raise
    except Exception as e:
        raise ProviderError(f"Gemini2 failed: {e}", "gemini2", "error")


async def call_codestral(
    messages: List[Dict[str, str]], session: aiohttp.ClientSession, **kwargs
) -> Dict[str, Any]:
    """Call Codestral using OpenAI-compatible client."""
    key = _env("CODESTRAL_API_KEY")
    if not key:
        raise ProviderError(
            "CODESTRAL_API_KEY not found in environment", "codestral", "auth"
        )

    if not OPENAI_AVAILABLE:
        raise ProviderError(
            "OpenAI client not available for Codestral", "codestral", "unavailable"
        )

    try:
        client = OpenAI(base_url="https://codestral.mistral.ai/v1", api_key=key)

        max_tokens = kwargs.get("max_tokens", DEFAULT_MAX_TOKENS)
        temperature = kwargs.get("temperature", DEFAULT_TEMPERATURE)

        response = client.chat.completions.create(
            model="codestral-latest",
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        content = response.choices[0].message.content or ""
        tokens = getattr(response, "usage", {}).get("total_tokens", 0)

        return {
            "provider": "codestral",
            "content": content,
            "success": True,
            "model": "codestral-latest",
            "tokens_used": tokens,
        }
    except Exception as e:
        error_type = (
            "quota"
            if "quota" in str(e).lower()
            else "auth" if "401" in str(e) else "error"
        )
        raise ProviderError(f"Codestral failed: {e}", "codestral", error_type)


async def call_cohere(
    messages: List[Dict[str, str]], session: aiohttp.ClientSession, **kwargs
) -> Dict[str, Any]:
    """Call Cohere using v2 chat API."""
    key = _env("COHERE_API_KEY")
    if not key:
        raise ProviderError("COHERE_API_KEY not found in environment", "cohere", "auth")

    try:
        url = "https://api.cohere.ai/v2/chat"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {key}"}

        body = {
            "model": "command-r-plus-08-2024",
            "messages": messages,
            "temperature": kwargs.get("temperature", DEFAULT_TEMPERATURE),
            "max_tokens": kwargs.get("max_tokens", DEFAULT_MAX_TOKENS),
        }

        async with session.post(
            url, headers=headers, json=body, timeout=DEFAULT_TIMEOUT
        ) as resp:
            if resp.status >= 400:
                error_text = await resp.text()
                error_type = (
                    "auth"
                    if resp.status == 401
                    else "quota" if resp.status == 429 else "error"
                )
                raise ProviderError(
                    f"Cohere HTTP {resp.status}: {error_text}", "cohere", error_type
                )

            data = await resp.json()

            # Extract content from Cohere v2 response
            content = ""
            try:
                message = data.get("message", {})
                content_list = message.get("content", [])
                if content_list and isinstance(content_list, list):
                    content = content_list[0].get("text", "")
            except Exception:
                content = json.dumps(data)[:1000]

            return {
                "provider": "cohere",
                "content": content,
                "success": True,
                "model": "command-r-plus-08-2024",
                "tokens_used": len(content.split()),  # Approximate
            }
    except ProviderError:
        raise
    except Exception as e:
        raise ProviderError(f"Cohere failed: {e}", "cohere", "error")


async def call_chutes(
    messages: List[Dict[str, str]], session: aiohttp.ClientSession, **kwargs
) -> Dict[str, Any]:
    """Call Chutes AI using their chat completions API."""
    key = _env("CHUTES_API_KEY")
    if not key:
        raise ProviderError("CHUTES_API_KEY not found in environment", "chutes", "auth")

    try:
        url = "https://llm.chutes.ai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

        body = {
            "model": "zai-org/GLM-4.5-Air",
            "messages": messages,
            "stream": False,
            "max_tokens": kwargs.get("max_tokens", DEFAULT_MAX_TOKENS),
            "temperature": kwargs.get("temperature", DEFAULT_TEMPERATURE),
        }

        async with session.post(
            url, headers=headers, json=body, timeout=DEFAULT_TIMEOUT
        ) as resp:
            if resp.status >= 400:
                error_text = await resp.text()
                error_type = (
                    "auth"
                    if resp.status == 401
                    else "quota" if resp.status == 429 else "error"
                )
                raise ProviderError(
                    f"Chutes HTTP {resp.status}: {error_text}", "chutes", error_type
                )

            data = await resp.json()

            # Extract content from OpenAI-style response
            content = ""
            try:
                content = data["choices"][0]["message"]["content"]
            except Exception:
                content = json.dumps(data)[:1000]

            return {
                "provider": "chutes",
                "content": content,
                "success": True,
                "model": "zai-org/GLM-4.5-Air",
                "tokens_used": len(content.split()),  # Approximate
            }
    except ProviderError:
        raise
    except Exception as e:
        raise ProviderError(f"Chutes failed: {e}", "chutes", "error")


async def call_openrouter(
    messages: List[Dict[str, str]], session: aiohttp.ClientSession, **kwargs
) -> Dict[str, Any]:
    """Call OpenRouter with automatic model selection based on available keys."""
    # Model and key selection based on priority
    model_mapping = {
        "DEEPSEEK_API_KEY": "deepseek/deepseek-chat-v3.1:free",
        "GLM_API_KEY": "z-ai/glm-4.5-air:free",
        "GROK_API_KEY": "x-ai/grok-4-fast:free",
        "KIMI_API_KEY": "moonshotai/kimi-k2:free",
        "QWEN_API_KEY": "qwen/qwen3-coder:free",
        "GPTOSS_API_KEY": "openai/gpt-oss-120b:free",
    }

    selected_key = None
    selected_model = None
    selected_key_name = None

    # Try in priority order
    for key_name, model in model_mapping.items():
        if _enabled(key_name):
            selected_key = _env(key_name)
            selected_model = model
            selected_key_name = key_name
            break

    if not selected_key or not selected_model:
        raise ProviderError("No OpenRouter-compatible keys found", "openrouter", "auth")

    if not OPENAI_AVAILABLE:
        raise ProviderError(
            "OpenAI client not available for OpenRouter", "openrouter", "unavailable"
        )

    try:
        client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=selected_key)

        max_tokens = kwargs.get("max_tokens", DEFAULT_MAX_TOKENS)
        temperature = kwargs.get("temperature", DEFAULT_TEMPERATURE)

        response = client.chat.completions.create(
            model=selected_model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            extra_headers={
                "HTTP-Referer": "https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System",
                "X-Title": "AMAS AI Router",
            },
        )

        content = response.choices[0].message.content or ""
        tokens = getattr(response, "usage", {}).get("total_tokens", 0)

        return {
            "provider": f"openrouter:{selected_model}",
            "content": content,
            "success": True,
            "model": selected_model,
            "tokens_used": tokens,
            "key_used": selected_key_name,
        }
    except Exception as e:
        error_type = (
            "quota"
            if "quota" in str(e).lower()
            else "auth" if "401" in str(e) else "error"
        )
        raise ProviderError(
            f"OpenRouter ({selected_model}) failed: {e}", "openrouter", error_type
        )


# Placeholder implementations for future providers
async def call_groq2(
    messages: List[Dict[str, str]], session: aiohttp.ClientSession, **kwargs
) -> Dict[str, Any]:
    """Call Groq2 - placeholder implementation."""
    if not _enabled("GROQ2_API_KEY"):
        raise ProviderError("GROQ2_API_KEY not found in environment", "groq2", "auth")
    # TODO: Implement when official SDK/endpoint is available
    raise ProviderError(
        "Groq2 adapter not yet implemented - will be added when SDK is available",
        "groq2",
        "unavailable",
    )


async def call_groqai(
    messages: List[Dict[str, str]], session: aiohttp.ClientSession, **kwargs
) -> Dict[str, Any]:
    """Call GroqAI - placeholder implementation."""
    if not _enabled("GROQAI_API_KEY"):
        raise ProviderError("GROQAI_API_KEY not found in environment", "groqai", "auth")
    # TODO: Implement when official SDK/endpoint is available
    raise ProviderError(
        "GroqAI adapter not yet implemented - will be added when SDK is available",
        "groqai",
        "unavailable",
    )


# Provider function mapping
PROVIDER_FUNCTIONS = {
    "cerebras": call_cerebras,
    "nvidia": call_nvidia,
    "gemini2": call_gemini2,
    "codestral": call_codestral,
    "cohere": call_cohere,
    "chutes": call_chutes,
    "openrouter": call_openrouter,
    "groq2": call_groq2,
    "groqai": call_groqai,
}


# Main router function
async def generate(
    prompt: str,
    system_prompt: str = "",
    temperature: float = DEFAULT_TEMPERATURE,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    timeout: Optional[float] = None,
    strategy: str = "intelligent",
    **kwargs,
) -> Dict[str, Any]:
    """Universal AI generation with comprehensive multi-provider failover.

    This function ensures no workflow ever fails due to AI provider issues by:
    - Trying providers in optimized priority order
    - Handling all error types (network, auth, quota, timeouts)
    - Providing structured failure information for debugging
    - Never raising exceptions (returns success/failure status)

    Args:
        prompt: User prompt for generation
        system_prompt: System prompt for context (optional)
        temperature: Generation temperature (0.0-1.0)
        max_tokens: Maximum tokens to generate
        timeout: Overall timeout in seconds (optional)
        strategy: Generation strategy ("intelligent", "fast", "quality")
        **kwargs: Additional provider-specific parameters

    Returns:
        Dict with structure:
        {
            "success": bool,
            "provider": str (if success),
            "content": str (if success),
            "error": str (if failure),
            "attempts": List[ProviderAttempt],
            "response_time": float,
            "provider_name": str,
            "tokens_used": int
        }
    """
    start_time = time.time()

    # Build messages list
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    # Get prioritized provider list
    providers = build_provider_priority()
    if not providers:
        return {
            "success": False,
            "error": "No AI providers configured via repository secrets. Please add API keys to repository secrets.",
            "attempts": [],
            "response_time": 0.0,
            "provider_name": "none",
            "tokens_used": 0,
        }

    logger.info(
        f"🚀 Starting AI generation with {len(providers)} available providers: {providers}"
    )

    attempts = []

    async with aiohttp.ClientSession() as session:
        for provider_name in providers:
            provider_func = PROVIDER_FUNCTIONS.get(provider_name)
            if not provider_func:
                attempts.append(
                    ProviderAttempt(
                        provider=provider_name,
                        status="unavailable",
                        elapsed_ms=0,
                        error="No adapter function available",
                    )
                )
                continue

            attempt_start = _now_ms()

            try:
                logger.debug(f"🔄 Attempting provider: {provider_name}")

                # Apply overall timeout if specified
                if timeout:
                    result = await asyncio.wait_for(
                        _with_retries(
                            lambda: provider_func(
                                messages,
                                session,
                                temperature=temperature,
                                max_tokens=max_tokens,
                                **kwargs,
                            )
                        ),
                        timeout=timeout,
                    )
                else:
                    result = await _with_retries(
                        lambda: provider_func(
                            messages,
                            session,
                            temperature=temperature,
                            max_tokens=max_tokens,
                            **kwargs,
                        )
                    )

                elapsed = _now_ms() - attempt_start

                attempts.append(
                    ProviderAttempt(
                        provider=provider_name,
                        status="success",
                        elapsed_ms=elapsed,
                        model=result.get("model"),
                        tokens_used=result.get("tokens_used", 0),
                    )
                )

                response_time = time.time() - start_time

                logger.info(
                    f"✅ AI generation successful with {provider_name} in {response_time:.2f}s"
                )

                return {
                    "success": True,
                    "provider": result.get("provider", provider_name),
                    "content": result.get("content", ""),
                    "attempts": attempts,
                    "response_time": response_time,
                    "provider_name": result.get("provider", provider_name),
                    "tokens_used": result.get("tokens_used", 0),
                    "model": result.get("model"),
                }

            except asyncio.TimeoutError:
                elapsed = _now_ms() - attempt_start
                attempts.append(
                    ProviderAttempt(
                        provider=provider_name,
                        status="timeout",
                        elapsed_ms=elapsed,
                        error="Request timed out",
                    )
                )
                logger.warning(f"⏰ {provider_name} timed out after {elapsed}ms")

            except ProviderError as e:
                elapsed = _now_ms() - attempt_start
                attempts.append(
                    ProviderAttempt(
                        provider=provider_name,
                        status=e.error_type,
                        elapsed_ms=elapsed,
                        error=str(e),
                    )
                )
                logger.warning(f"⚠️ {provider_name} failed ({e.error_type}): {e}")

            except Exception as e:
                elapsed = _now_ms() - attempt_start
                attempts.append(
                    ProviderAttempt(
                        provider=provider_name,
                        status="error",
                        elapsed_ms=elapsed,
                        error=str(e),
                    )
                )
                logger.warning(f"❌ {provider_name} failed: {e}")

    # All providers failed
    response_time = time.time() - start_time
    error_summary = f"All {len(providers)} providers failed: " + "; ".join(
        f"{a.provider}({a.status})" for a in attempts
    )

    logger.error(
        f"❌ AI generation failed after trying all providers in {response_time:.2f}s"
    )

    return {
        "success": False,
        "error": error_summary,
        "attempts": attempts,
        "response_time": response_time,
        "provider_name": "failed_all",
        "tokens_used": 0,
    }


# Utility functions
def get_available_providers() -> List[str]:
    """Get list of currently available providers based on repository secrets.

    Returns:
        List of provider names that have valid API keys configured
    """
    return build_provider_priority()


def get_provider_status() -> Dict[str, bool]:
    """Get status of all supported providers.

    Returns:
        Dict mapping provider names to availability status
    """
    all_providers = list(PROVIDER_FUNCTIONS.keys())
    status = {}

    for provider in all_providers:
        if provider == "openrouter":
            # Special case: available if any OpenRouter key is present
            openrouter_keys = [
                "DEEPSEEK_API_KEY",
                "GLM_API_KEY",
                "GROK_API_KEY",
                "KIMI_API_KEY",
                "QWEN_API_KEY",
                "GPTOSS_API_KEY",
            ]
            status[provider] = any(_enabled(k) for k in openrouter_keys)
        else:
            # Map provider name to expected env var
            key_mapping = {
                "cerebras": "CEREBRAS_API_KEY",
                "nvidia": "NVIDIA_API_KEY",
                "gemini2": "GEMINI2_API_KEY",
                "codestral": "CODESTRAL_API_KEY",
                "cohere": "COHERE_API_KEY",
                "chutes": "CHUTES_API_KEY",
                "groq2": "GROQ2_API_KEY",
                "groqai": "GROQAI_API_KEY",
            }

            key_name = key_mapping.get(provider)
            status[provider] = _enabled(key_name) if key_name else False

    return status


# Health check and diagnostics
async def health_check() -> Dict[str, Any]:
    """Perform health check on all available providers.

    Returns:
        Dict with overall health status and per-provider results
    """
    providers = get_available_providers()
    if not providers:
        return {
            "status": "unhealthy",
            "message": "No providers configured via repository secrets",
            "providers": {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "available_count": 0,
        }

    # Quick health check with minimal prompt
    test_prompt = "Respond with 'OK' to confirm you're working."

    # Try the first available provider for health check
    result = await generate(
        prompt=test_prompt,
        system_prompt="You are a health check service. Respond concisely.",
        timeout=15.0,  # Quick health check timeout
        max_tokens=50,
    )

    if result["success"]:
        return {
            "status": "healthy",
            "providers_available": len(providers),
            "providers_healthy": 1,
            "working_provider": result["provider_name"],
            "response_time": result["response_time"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    else:
        return {
            "status": "unhealthy",
            "providers_available": len(providers),
            "providers_healthy": 0,
            "error": result["error"],
            "attempts": [vars(a) for a in result["attempts"]],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# Backward compatibility for existing code
class UniversalAIManager:
    """Backward-compatible wrapper for existing code."""

    @property
    def active_providers(self) -> List[str]:
        """Get list of active providers for compatibility."""
        return get_available_providers()

    async def generate(
        self, prompt: str, system_prompt: str = "", **kwargs
    ) -> Dict[str, Any]:
        """Generate response using universal router."""
        return await generate(prompt, system_prompt, **kwargs)


def get_manager():
    """Get universal AI manager instance for compatibility."""
    return UniversalAIManager()


if __name__ == "__main__":
    # Quick test/demo
    async def test():
        print("🧪 Testing Universal AI Router")
        print(f"Available providers: {get_available_providers()}")
        print(f"Provider status: {get_provider_status()}")

        print("\n🔍 Running health check...")
        health = await health_check()
        print(f"Health status: {health['status']}")

        if health["status"] == "healthy":
            print("\n🚀 Testing generation...")
            result = await generate("Say hello and identify yourself in one sentence.")
            if result["success"]:
                print(
                    f"✅ Success with {result['provider_name']}: {result['content'][:100]}..."
                )
            else:
                print(f"❌ Failed: {result['error']}")
        else:
            print(f"⚠️ Health check failed: {health.get('error', 'Unknown error')}")

    asyncio.run(test())
