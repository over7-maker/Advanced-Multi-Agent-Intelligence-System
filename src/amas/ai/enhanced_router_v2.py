#!/usr/bin/env python3
"""
Enhanced AI Router v2.0 - Complete Integration with All 9 API Keys
Intelligent fallback system with OpenRouter support for all providers
"""

import asyncio
import logging
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import aiohttp

logger = logging.getLogger("amas.ai.enhanced_router")

# OpenAI client for OpenRouter compatibility
try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    AsyncOpenAI = None
    OPENAI_AVAILABLE = False

# Cerebras SDK
try:
    from cerebras.cloud.sdk import Cerebras
    CEREBRAS_AVAILABLE = True
except ImportError:
    Cerebras = None
    CEREBRAS_AVAILABLE = False

# Groq SDK
try:
    from groq import AsyncGroq
    GROQ_AVAILABLE = True
except ImportError:
    AsyncGroq = None
    GROQ_AVAILABLE = False

# Google Generative AI
# Note: Python 3.13 has OpenSSL compatibility issues with google.generativeai
# We catch both ImportError and OSError to handle this gracefully
try:
    import google.generativeai as genai

    # Test if the module actually works (Python 3.13 compatibility check)
    try:
        # This will fail on Python 3.13 if OpenSSL is incompatible
        _ = genai.__version__
        GEMINI_AVAILABLE = True
    except (AttributeError, ImportError, OSError) as e:
        if "X509_V_FLAG_NOTIFY_POLICY" in str(e) or "OpenSSL" in str(e):
            logger.warning(
                "Google Generative AI unavailable due to Python 3.13 OpenSSL compatibility issue. "
                "Continuing with other 15 providers."
            )
            genai = None
            GEMINI_AVAILABLE = False
        else:
            raise
except (ImportError, OSError, AttributeError) as e:
    if "X509_V_FLAG_NOTIFY_POLICY" in str(e) or "OpenSSL" in str(e):
        logger.warning(
            "Google Generative AI unavailable due to Python 3.13 OpenSSL compatibility issue. "
            "Continuing with other 15 providers."
        )
    genai = None
    GEMINI_AVAILABLE = False


@dataclass
class ProviderConfig:
    """Provider configuration"""
    name: str
    api_key_env: str
    model: str
    base_url: Optional[str] = None
    provider_type: str = "openrouter"  # openrouter, direct, cerebras, groq, gemini
    priority: int = 5  # Lower = higher priority
    enabled: bool = False


# Provider configurations - All 16+ providers with proper setup
# Optimized priority order for maximum reliability and speed
# Supports both standard providers and user's actual API keys
PROVIDER_CONFIGS = {
    # Tier 0 - Standard Premium Providers (Highest Priority)
    "openai": ProviderConfig(
        name="OpenAI",
        api_key_env="OPENAI_API_KEY",
        model="gpt-4-turbo-preview",
        base_url="https://api.openai.com/v1",
        provider_type="openai_compatible",
        priority=0,  # Highest priority - Standard provider
    ),
    "anthropic": ProviderConfig(
        name="Anthropic Claude",
        api_key_env="ANTHROPIC_API_KEY",
        model="claude-3-5-sonnet-20241022",
        base_url="https://api.anthropic.com/v1",
        provider_type="anthropic",
        priority=0,  # Highest priority - Standard provider
    ),
    
    # Tier 1 - Premium Speed & Quality (Direct APIs - Fastest, Most Reliable)
    "cerebras": ProviderConfig(
        name="Cerebras AI",
        api_key_env="CEREBRAS_API_KEY",
        model="qwen-3-235b-a22b-instruct-2507",
        provider_type="cerebras",
        priority=1,  # Highest priority - Ultra-fast
    ),
    "nvidia": ProviderConfig(
        name="NVIDIA AI",
        api_key_env="NVIDIA_API_KEY",
        model="deepseek-ai/deepseek-r1",
        base_url="https://integrate.api.nvidia.com/v1",
        provider_type="openai_compatible",
        priority=1,  # Highest priority - GPU-accelerated
    ),
    "groq2": ProviderConfig(
        name="Groq 2",
        api_key_env="GROQ2_API_KEY",
        model="llama-3.3-70b-versatile",
        provider_type="groq",
        priority=2,  # High priority - Fast inference
    ),
    "groqai": ProviderConfig(
        name="Groq AI",
        api_key_env="GROQAI_API_KEY",
        model="llama-3.3-70b-versatile",
        provider_type="groq",
        priority=2,  # High priority - Fast inference
    ),
    
    # Tier 2 - High Quality (OpenRouter Primary & Direct APIs)
    "deepseek": ProviderConfig(
        name="DeepSeek V3.1",
        api_key_env="DEEPSEEK_API_KEY",
        model="deepseek/deepseek-chat-v3.1:free",
        base_url="https://openrouter.ai/api/v1",
        provider_type="openrouter",
        priority=3,  # High quality, free tier
    ),
    "codestral": ProviderConfig(
        name="Codestral",
        api_key_env="CODESTRAL_API_KEY",
        model="codestral-latest",
        base_url="https://codestral.mistral.ai/v1",
        provider_type="openai_compatible",
        priority=3,  # Code-specialized, high quality
    ),
    "glm": ProviderConfig(
        name="GLM 4.5 Air",
        api_key_env="GLM_API_KEY",
        model="z-ai/glm-4.5-air:free",
        base_url="https://openrouter.ai/api/v1",
        provider_type="openrouter",
        priority=4,  # Good quality, free tier
    ),
    "gemini2": ProviderConfig(
        name="Gemini 2.0",
        api_key_env="GEMINI2_API_KEY",
        model="gemini-2.0-flash",
        provider_type="gemini",
        priority=4,  # High quality, multimodal
    ),
    "grok": ProviderConfig(
        name="Grok 4 Fast",
        api_key_env="GROK_API_KEY",
        model="x-ai/grok-4-fast:free",
        base_url="https://openrouter.ai/api/v1",
        provider_type="openrouter",
        priority=5,  # Good quality, free tier
    ),
    
    # Tier 3 - Commercial & Specialized (Enterprise Quality)
    "cohere": ProviderConfig(
        name="Cohere",
        api_key_env="COHERE_API_KEY",
        model="command-a-03-2025",  # Updated to latest model
        base_url="https://api.cohere.ai/v1",
        provider_type="cohere",
        priority=6,  # Enterprise features
    ),
    
    # Tier 4 - OpenRouter Free Tier (Secondary - Reliable Fallbacks)
    "kimi": ProviderConfig(
        name="Kimi K2",
        api_key_env="KIMI_API_KEY",
        model="moonshotai/kimi-k2:free",
        base_url="https://openrouter.ai/api/v1",
        provider_type="openrouter",
        priority=7,  # Long context support
    ),
    "qwen": ProviderConfig(
        name="Qwen 3 Coder",
        api_key_env="QWEN_API_KEY",
        model="qwen/qwen3-coder:free",
        base_url="https://openrouter.ai/api/v1",
        provider_type="openrouter",
        priority=8,  # Code-specialized
    ),
    "gptoss": ProviderConfig(
        name="GPT OSS 120B",
        api_key_env="GPTOSS_API_KEY",
        model="openai/gpt-oss-120b:free",
        base_url="https://openrouter.ai/api/v1",
        provider_type="openrouter",
        priority=9,  # Large model
    ),
    "chutes": ProviderConfig(
        name="Chutes AI",
        api_key_env="CHUTES_API_KEY",
        model="zai-org/GLM-4.5-Air",  # Updated model name
        base_url="https://llm.chutes.ai/v1",  # Updated base URL
        provider_type="openai_compatible",
        priority=10,  # Final fallback
    ),
    
    # Additional Standard Providers (Architecture Requirement - 16 providers)
    "together": ProviderConfig(
        name="Together AI",
        api_key_env="TOGETHER_API_KEY",
        model="meta-llama/Llama-3-70b-chat-hf",
        base_url="https://api.together.xyz/v1",
        provider_type="openai_compatible",
        priority=5,
    ),
    "perplexity": ProviderConfig(
        name="Perplexity",
        api_key_env="PERPLEXITY_API_KEY",
        model="llama-3.1-sonar-large-128k-online",
        base_url="https://api.perplexity.ai",
        provider_type="openai_compatible",
        priority=6,
    ),
    "fireworks": ProviderConfig(
        name="Fireworks AI",
        api_key_env="FIREWORKS_API_KEY",
        model="accounts/fireworks/models/llama-v3-70b-instruct",
        base_url="https://api.fireworks.ai/inference/v1",
        provider_type="openai_compatible",
        priority=5,
    ),
    "replicate": ProviderConfig(
        name="Replicate",
        api_key_env="REPLICATE_API_KEY",
        model="meta/llama-2-70b-chat",
        base_url="https://api.replicate.com/v1",
        provider_type="openai_compatible",
        priority=7,
    ),
    "huggingface": ProviderConfig(
        name="HuggingFace",
        api_key_env="HUGGINGFACE_API_KEY",
        model="meta-llama/Llama-2-70b-chat-hf",
        base_url="https://api-inference.huggingface.co",
        provider_type="openai_compatible",
        priority=7,
    ),
    "ai21": ProviderConfig(
        name="AI21 Labs",
        api_key_env="AI21_API_KEY",
        model="j2-ultra",
        base_url="https://api.ai21.com/studio/v1",
        provider_type="openai_compatible",
        priority=6,
    ),
    "aleph_alpha": ProviderConfig(
        name="Aleph Alpha",
        api_key_env="ALEPH_ALPHA_API_KEY",
        model="luminous-extended",
        base_url="https://api.aleph-alpha.com",
        provider_type="openai_compatible",
        priority=7,
    ),
    "writer": ProviderConfig(
        name="Writer",
        api_key_env="WRITER_API_KEY",
        model="palmyra-x",
        base_url="https://api.writer.com/v1",
        provider_type="openai_compatible",
        priority=8,
    ),
    "moonshot": ProviderConfig(
        name="Moonshot AI",
        api_key_env="MOONSHOT_API_KEY",
        model="moonshot-v1-8k",
        base_url="https://api.moonshot.cn/v1",
        provider_type="openai_compatible",
        priority=7,
    ),
    "mistral": ProviderConfig(
        name="Mistral AI",
        api_key_env="MISTRAL_API_KEY",
        model="mistral-large-latest",
        base_url="https://api.mistral.ai/v1",
        provider_type="openai_compatible",
        priority=4,
    ),
    # Ollama - Local fallback provider (no API key required)
    "ollama": ProviderConfig(
        name="Ollama",
        api_key_env="OLLAMA_API_KEY",  # Not required, but checked
        # Use a commonly available local model - try llama3.2 first, fallback to llama3.1:8b
        # These are the most commonly installed Ollama models
        model=os.getenv("OLLAMA_MODEL", "llama3.2"),  # Default to llama3.2, can be overridden
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
        provider_type="ollama",
        priority=100,  # Lowest priority - fallback only
    ),
}


def get_api_key(env_name: str) -> Optional[str]:
    """
    Get API key from environment or settings, stripping whitespace.
    
    Priority:
    1. Environment variable (highest priority)
    2. Settings configuration (from .env file)
    3. None (if not found)
    """
    # First try environment variable (highest priority)
    value = os.getenv(env_name)
    if value:
        return value.strip()
    
    # Fallback to settings if available
    try:
        from src.config.settings import get_settings
        settings = get_settings()
        
        # Map env names to settings attributes
        env_to_attr = {
            "OPENAI_API_KEY": "openai_api_key",
            "ANTHROPIC_API_KEY": "anthropic_api_key",
            "GOOGLE_AI_API_KEY": "google_ai_api_key",
            "GROQ_API_KEY": "groq_api_key",
            "COHERE_API_KEY": "cohere_api_key",
            "HUGGINGFACE_API_KEY": "huggingface_api_key",
            "CEREBRAS_API_KEY": "cerebras_api_key",
            "NVIDIA_API_KEY": "nvidia_api_key",
            "GROQ2_API_KEY": "groq2_api_key",
            "GROQAI_API_KEY": "groqai_api_key",
            "DEEPSEEK_API_KEY": "deepseek_api_key",
            "CODESTRAL_API_KEY": "codestral_api_key",
            "GLM_API_KEY": "glm_api_key",
            "GEMINI2_API_KEY": "gemini2_api_key",
            "GROK_API_KEY": "grok_api_key",
            "KIMI_API_KEY": "kimi_api_key",
            "QWEN_API_KEY": "qwen_api_key",
            "GPTOSS_API_KEY": "gptoss_api_key",
            "CHUTES_API_KEY": "chutes_api_key",
            "TOGETHER_API_KEY": "together_api_key",
            "PERPLEXITY_API_KEY": "perplexity_api_key",
            "FIREWORKS_API_KEY": "fireworks_api_key",
            "REPLICATE_API_KEY": "replicate_api_key",
            "AI21_API_KEY": "ai21_api_key",
            "ALEPH_ALPHA_API_KEY": "aleph_alpha_api_key",
            "WRITER_API_KEY": "writer_api_key",
            "MOONSHOT_API_KEY": "moonshot_api_key",
            "MISTRAL_API_KEY": "mistral_api_key",
        }
        
        attr_name = env_to_attr.get(env_name)
        if attr_name:
            value = getattr(settings.ai, attr_name, None)
            if value:
                return value.strip()
    except Exception as e:
        logger.debug(f"Could not load API key from settings for {env_name}: {e}")
    
    return None


def get_available_providers() -> List[str]:
    """Get list of available providers based on API keys."""
    available = []
    for provider_id, config in PROVIDER_CONFIGS.items():
        # Skip Ollama in initial loop - handle separately
        if provider_id == "ollama":
            continue
            
        if get_api_key(config.api_key_env):
            config.enabled = True
            available.append(provider_id)
        else:
            config.enabled = False
    
    # Always check Ollama as local fallback (even if other providers are available)
    try:
        import httpx
        response = httpx.get("http://localhost:11434/api/tags", timeout=2.0)
        if response.status_code == 200:
            data = response.json()
            models = [model.get("name", "") for model in data.get("models", [])]
            if models:
                ollama_config = PROVIDER_CONFIGS["ollama"]
                ollama_config.enabled = True
                if "ollama" not in available:
                    available.append("ollama")
                logger.info(f"✅ Ollama detected with {len(models)} models: {', '.join(models[:3])}")
    except Exception as e:
        logger.debug(f"Ollama not available: {e}")
    
    return sorted(available, key=lambda p: PROVIDER_CONFIGS.get(p, ProviderConfig(name=p, api_key_env="", model="", priority=999)).priority)


async def call_openrouter_provider(
    provider_id: str,
    messages: List[Dict[str, str]],
    config: ProviderConfig,
    session: aiohttp.ClientSession,
    **kwargs
) -> Dict[str, Any]:
    """Call OpenRouter-based provider with proper headers."""
    api_key = get_api_key(config.api_key_env)
    if not api_key:
        raise ValueError(f"{config.api_key_env} not found")

    # OpenRouter requires specific headers
    referer = "https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System"
    title = "AMAS Project"

    if not OPENAI_AVAILABLE:
        # Fallback to HTTP
        url = f"{config.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": referer,
            "X-Title": title,
        }
        
        body = {
            "model": config.model,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", 2000),
            "temperature": kwargs.get("temperature", 0.7),
        }
        
        async with session.post(url, headers=headers, json=body, timeout=aiohttp.ClientTimeout(total=45)) as resp:
            if resp.status >= 400:
                error_text = await resp.text()
                raise Exception(f"OpenRouter {provider_id} {resp.status}: {error_text}")
            
            data = await resp.json()
            content = data["choices"][0]["message"]["content"]
            tokens = data.get("usage", {}).get("total_tokens", 0)
            
            return {
                "provider": provider_id,
                "content": content,
                "success": True,
                "model": config.model,
                "tokens_used": tokens,
            }
    else:
        # Use OpenAI-compatible client
        client = AsyncOpenAI(
            base_url=config.base_url,
            api_key=api_key,
        )
        
        response = await client.chat.completions.create(
            model=config.model,
            messages=messages,
            max_tokens=kwargs.get("max_tokens", 2000),
            temperature=kwargs.get("temperature", 0.7),
            extra_headers={
                "HTTP-Referer": referer,
                "X-Title": title,
            },
        )
        
        return {
            "provider": provider_id,
            "content": response.choices[0].message.content,
            "success": True,
            "model": config.model,
            "tokens_used": response.usage.total_tokens if response.usage else 0,
        }


async def call_groq_provider(
    provider_id: str,
    messages: List[Dict[str, str]],
    config: ProviderConfig,
    **kwargs
) -> Dict[str, Any]:
    """Call Groq provider."""
    api_key = get_api_key(config.api_key_env)
    if not api_key:
        raise ValueError(f"{config.api_key_env} not found")
    
    if not GROQ_AVAILABLE:
        raise Exception("Groq SDK not installed")
    
    client = AsyncGroq(api_key=api_key)
    
    response = await client.chat.completions.create(
        model=config.model,
        messages=messages,
        max_tokens=kwargs.get("max_tokens", 2000),
        temperature=kwargs.get("temperature", 0.7),
    )
    
    return {
        "provider": provider_id,
        "content": response.choices[0].message.content,
        "success": True,
        "model": config.model,
        "tokens_used": response.usage.total_tokens if response.usage else 0,
    }


async def call_cerebras_provider(
    provider_id: str,
    messages: List[Dict[str, str]],
    config: ProviderConfig,
    **kwargs
) -> Dict[str, Any]:
    """Call Cerebras provider."""
    api_key = get_api_key(config.api_key_env)
    if not api_key:
        raise ValueError(f"{config.api_key_env} not found")
    
    if not CEREBRAS_AVAILABLE:
        raise Exception("Cerebras SDK not installed")
    
    client = Cerebras(api_key=api_key)
    
    response = client.chat.completions.create(
        model=config.model,
        messages=messages,
        stream=False,
        max_completion_tokens=kwargs.get("max_tokens", 2000),
        temperature=kwargs.get("temperature", 0.7),
    )
    
    return {
        "provider": provider_id,
        "content": response.choices[0].message.content,
        "success": True,
        "model": config.model,
        "tokens_used": 0,  # Cerebras doesn't always return usage
    }


async def call_gemini_provider(
    provider_id: str,
    messages: List[Dict[str, str]],
    config: ProviderConfig,
    **kwargs
) -> Dict[str, Any]:
    """Call Gemini provider."""
    api_key = get_api_key(config.api_key_env)
    if not api_key:
        raise ValueError(f"{config.api_key_env} not found")
    
    if not GEMINI_AVAILABLE:
        raise Exception("Google Generative AI SDK not installed")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(config.model)
    
    # Convert messages to Gemini format
    user_content = "\n".join([msg["content"] for msg in messages if msg["role"] == "user"])
    system_content = "\n".join([msg["content"] for msg in messages if msg["role"] == "system"])
    
    prompt = f"{system_content}\n\n{user_content}" if system_content else user_content
    
    response = await model.generate_content_async(
        prompt,
        generation_config={
            "temperature": kwargs.get("temperature", 0.7),
            "max_output_tokens": kwargs.get("max_tokens", 2000),
        },
    )
    
    return {
        "provider": provider_id,
        "content": response.text,
        "success": True,
        "model": config.model,
        "tokens_used": 0,
    }


async def call_openai_compatible_provider(
    provider_id: str,
    messages: List[Dict[str, str]],
    config: ProviderConfig,
    session: aiohttp.ClientSession,
    **kwargs
) -> Dict[str, Any]:
    """Call OpenAI-compatible provider (NVIDIA, Codestral, Chutes)."""
    api_key = get_api_key(config.api_key_env)
    if not api_key:
        raise ValueError(f"{config.api_key_env} not found")
    
    # Special handling for NVIDIA (reasoning content)
    is_nvidia = provider_id == "nvidia"
    
    if not OPENAI_AVAILABLE:
        # Fallback to HTTP
        url = f"{config.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        
        body = {
            "model": config.model,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", 2000),
            "temperature": kwargs.get("temperature", 0.7),
        }
        
        # NVIDIA-specific parameters
        if is_nvidia:
            body["temperature"] = kwargs.get("temperature", 0.6)
            body["top_p"] = 0.7
        
        async with session.post(url, headers=headers, json=body, timeout=aiohttp.ClientTimeout(total=45)) as resp:
            if resp.status >= 400:
                error_text = await resp.text()
                raise Exception(f"{provider_id} {resp.status}: {error_text}")
            
            data = await resp.json()
            content = data["choices"][0]["message"]["content"]
            
            # NVIDIA reasoning content
            if is_nvidia:
                reasoning = data["choices"][0].get("message", {}).get("reasoning_content")
                if reasoning:
                    content = f"## Reasoning\n{reasoning}\n\n## Response\n{content}"
            
            tokens = data.get("usage", {}).get("total_tokens", 0)
            
            return {
                "provider": provider_id,
                "content": content,
                "success": True,
                "model": config.model,
                "tokens_used": tokens,
            }
    else:
        client = AsyncOpenAI(
            base_url=config.base_url,
            api_key=api_key,
        )
        
        # NVIDIA-specific parameters
        extra_params = {}
        if is_nvidia:
            extra_params["temperature"] = kwargs.get("temperature", 0.6)
            extra_params["top_p"] = 0.7
        
        response = await client.chat.completions.create(
            model=config.model,
            messages=messages,
            max_tokens=kwargs.get("max_tokens", 2000),
            temperature=kwargs.get("temperature", 0.7),
            **extra_params
        )
        
        content = response.choices[0].message.content
        
        # NVIDIA reasoning content
        if is_nvidia:
            reasoning = getattr(response.choices[0].message, "reasoning_content", None)
            if reasoning:
                content = f"## Reasoning\n{reasoning}\n\n## Response\n{content}"
        
        return {
            "provider": provider_id,
            "content": content,
            "success": True,
            "model": config.model,
            "tokens_used": response.usage.total_tokens if response.usage else 0,
        }


async def call_anthropic_provider(
    provider_id: str,
    messages: List[Dict[str, str]],
    config: ProviderConfig,
    session: aiohttp.ClientSession,
    **kwargs
) -> Dict[str, Any]:
    """Call Anthropic Claude provider."""
    api_key = get_api_key(config.api_key_env)
    if not api_key:
        raise ValueError(f"{config.api_key_env} not found")
    
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
    }
    
    # Convert messages to Claude format
    system_msg = next((msg["content"] for msg in messages if msg["role"] == "system"), None)
    user_msgs = [{"role": msg["role"], "content": msg["content"]} for msg in messages if msg["role"] != "system"]
    
    body = {
        "model": config.model,
        "messages": user_msgs,
        "max_tokens": kwargs.get("max_tokens", 2000),
        "temperature": kwargs.get("temperature", 0.7),
    }
    if system_msg:
        body["system"] = system_msg
    
    async with session.post(url, headers=headers, json=body, timeout=aiohttp.ClientTimeout(total=45)) as resp:
        if resp.status >= 400:
            error_text = await resp.text()
            raise Exception(f"Claude {resp.status}: {error_text}")
        
        data = await resp.json()
        content = data["content"][0]["text"] if data.get("content") else ""
        tokens = data.get("usage", {}).get("output_tokens", 0)
        
        return {
            "provider": provider_id,
            "content": content,
            "success": True,
            "model": config.model,
            "tokens_used": tokens,
        }


async def call_cohere_provider(
    provider_id: str,
    messages: List[Dict[str, str]],
    config: ProviderConfig,
    session: aiohttp.ClientSession,
    **kwargs
) -> Dict[str, Any]:
    """Call Cohere provider using v2 API."""
    api_key = get_api_key(config.api_key_env)
    if not api_key:
        raise ValueError(f"{config.api_key_env} not found")
    
    # Cohere v2 API format
    url = f"{config.base_url}/chat"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    # Convert to Cohere v2 format
    cohere_messages = []
    for msg in messages:
        if msg["role"] == "system":
            # Cohere v2 doesn't have system role, prepend to first user message
            continue
        cohere_messages.append({
            "role": "USER" if msg["role"] == "user" else "CHATBOT",
            "content": msg["content"]
        })
    
    # Get system message if exists
    system_msg = next((msg["content"] for msg in messages if msg["role"] == "system"), None)
    if system_msg and cohere_messages:
        cohere_messages[0]["content"] = f"{system_msg}\n\n{cohere_messages[0]['content']}"
    
    body = {
        "model": config.model,
        "messages": cohere_messages,
        "max_tokens": kwargs.get("max_tokens", 2000),
        "temperature": kwargs.get("temperature", 0.7),
    }
    
    async with session.post(url, headers=headers, json=body, timeout=aiohttp.ClientTimeout(total=45)) as resp:
        if resp.status >= 400:
            error_text = await resp.text()
            raise Exception(f"Cohere {resp.status}: {error_text}")
        
        data = await resp.json()
        # Cohere v2 returns text directly in response
        content = data.get("text", "") or (data.get("message", {}).get("content", "") if isinstance(data.get("message"), dict) else "")
        tokens = data.get("usage", {}).get("total_tokens", 0) if data.get("usage") else 0
        
        return {
            "provider": provider_id,
            "content": content,
            "success": True,
            "model": config.model,
            "tokens_used": tokens,
        }


async def generate_with_fallback(
    prompt: str,
    system_prompt: Optional[str] = None,
    max_tokens: int = 2000,
    temperature: float = 0.7,
    timeout: float = 45.0,
    session: Optional[aiohttp.ClientSession] = None,
) -> Dict[str, Any]:
    """
    Generate AI response with intelligent fallback across all providers.
    
    Returns:
        Dict with:
        - success: bool
        - content: str (if success)
        - provider: str
        - attempts: List[Dict] (all attempts made)
        - error: str (if all failed)
    """
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    available_providers = get_available_providers()
    if not available_providers:
        return {
            "success": False,
            "error": "No API keys configured. Please add at least one API key to GitHub Secrets.",
            "attempts": [],
        }
    
    attempts = []
    last_error = None
    
    if session is None:
        async with aiohttp.ClientSession() as temp_session:
            return await _try_providers(
                available_providers, messages, max_tokens, temperature, timeout, temp_session, attempts
            )
    else:
        return await _try_providers(
            available_providers, messages, max_tokens, temperature, timeout, session, attempts
        )


async def call_ollama_provider(
    provider_id: str,
    messages: List[Dict[str, str]],
    config: ProviderConfig,
    session: aiohttp.ClientSession,
    **kwargs
) -> Dict[str, Any]:
    """
    Call Ollama provider with automatic model fallback.
    
    Tries models in order:
    1. Config model (from OLLAMA_MODEL env or default)
    2. llama3.2 (most common)
    3. llama3.1:8b
    4. mistral
    5. qwen2.5:7b
    """
    base_url = config.base_url or "http://localhost:11434"
    base_url_clean = base_url.replace('/v1', '').rstrip('/')
    if not base_url_clean.startswith('http'):
        base_url_clean = f"http://{base_url_clean}"
    
    # First, try to get list of available models from Ollama
    available_models = []
    try:
        import httpx
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(f"{base_url_clean}/api/tags")
            if response.status_code == 200:
                data = response.json()
                available_models = [model.get("name", "") for model in data.get("models", [])]
                if available_models:
                    logger.info(f"✅ Found {len(available_models)} Ollama models: {', '.join(available_models[:5])}")
    except Exception as e:
        logger.debug(f"Could not fetch Ollama models list: {e}")
    
    # If we have available models, use ONLY those models (don't try non-existent models)
    if available_models:
        # Prioritize configured model if it's available
        models_to_try = []
        if config.model in available_models:
            models_to_try.append(config.model)
        
        # Add remaining available models
        for model in available_models:
            if model not in models_to_try:
                models_to_try.append(model)
        
        models_to_try = models_to_try[:10]  # Limit to first 10
        logger.info(f"✅ Using {len(models_to_try)} available Ollama models: {', '.join(models_to_try)}")
    else:
        # No available models list, use fallback order (but these will likely fail)
        fallback_models = [
            config.model,  # Try configured model first
            "llama3.2",
            "llama3.1:8b",
            "mistral",
            "qwen2.5:7b",
            "llama3.1",
            "llama3",
        ]
        seen = set()
        models_to_try = []
        for model in fallback_models:
            if model not in seen:
                seen.add(model)
                models_to_try.append(model)
        logger.warning(f"⚠️ No Ollama models list available, trying fallback models: {', '.join(models_to_try)}")
    
    # Ollama uses /api/chat endpoint (native API is more reliable)
    # Try native API first, then OpenAI-compatible endpoint as fallback
    native_url = f"{base_url_clean}/api/chat"
    openai_url = f"{base_url}/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
    }
    
    # Convert messages format for Ollama
    ollama_messages = []
    for msg in messages:
        if msg["role"] in ["user", "assistant", "system"]:
            ollama_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
    
    last_error = None
    
    # Try each model in order - use native API first (more reliable)
    for model_name in models_to_try:
        try:
            # Native Ollama API format
            native_body = {
                "model": model_name,
                "messages": ollama_messages,
                "stream": False,
            }
            
            logger.debug(f"Trying Ollama model '{model_name}' via native API")
            
            # Try native Ollama /api/chat endpoint first (most reliable)
            async with session.post(native_url, headers=headers, json=native_body, timeout=aiohttp.ClientTimeout(total=60)) as native_resp:
                if native_resp.status == 200:
                    data = await native_resp.json()
                    # Handle different response formats
                    if isinstance(data.get("message"), dict):
                        content = data["message"].get("content", "")
                    elif isinstance(data.get("response"), str):
                        content = data["response"]
                    else:
                        content = str(data)
                    
                    tokens_used = data.get("eval_count", 0) + data.get("prompt_eval_count", 0)
                    
                    logger.info(f"✅ Ollama model '{model_name}' succeeded (native API)")
                    return {
                        "provider": provider_id,
                        "content": content,
                        "success": True,
                        "model": model_name,
                        "tokens_used": tokens_used,
                    }
                
                if native_resp.status == 404:
                    error_text = await native_resp.text()
                    logger.debug(f"Model '{model_name}' not found (native API): {error_text}")
                    last_error = f"Model '{model_name}' not found"
                    continue
                
                # If native API fails, try OpenAI-compatible endpoint
                error_text = await native_resp.text()
                logger.debug(f"Ollama native API failed for '{model_name}': {error_text}, trying OpenAI-compatible endpoint")
                
                # Try OpenAI-compatible endpoint as fallback
                openai_body = {
                    "model": model_name,
                    "messages": ollama_messages,
                    "max_tokens": kwargs.get("max_tokens", 2000),
                    "temperature": kwargs.get("temperature", 0.7),
                }
                
                async with session.post(openai_url, headers=headers, json=openai_body, timeout=aiohttp.ClientTimeout(total=60)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        content = data["choices"][0]["message"]["content"]
                        usage = data.get("usage", {})
                        
                        logger.info(f"✅ Ollama model '{model_name}' succeeded (OpenAI-compatible)")
                        return {
                            "provider": provider_id,
                            "content": content,
                            "success": True,
                            "model": model_name,
                            "tokens_used": usage.get("total_tokens", 0),
                        }
                    
                    if resp.status == 404:
                        error_text = await resp.text()
                        logger.debug(f"Model '{model_name}' not found (OpenAI-compatible): {error_text}")
                        last_error = f"Model '{model_name}' not found"
                        continue
                    
                    # Other error - try next model
                    error_text = await resp.text()
                    logger.debug(f"Ollama OpenAI-compatible endpoint failed for '{model_name}': {error_text}")
                    last_error = f"Ollama {resp.status}: {error_text}"
                    continue
                    
        except Exception as e:
            logger.debug(f"Exception trying model '{model_name}': {e}")
            last_error = str(e)
            continue
    
    # All models failed
    if available_models:
        error_msg = f"Ollama: All {len(models_to_try)} models failed. Available models: {', '.join(available_models[:5])}. Last error: {last_error or 'Unknown error'}"
    else:
        error_msg = f"Ollama: All {len(models_to_try)} models failed. No models found in Ollama. Please install a model using 'ollama pull llama3.2' or similar. Last error: {last_error or 'No models available'}"
    
    raise Exception(error_msg)


async def _try_providers(
    providers: List[str],
    messages: List[Dict[str, str]],
    max_tokens: int,
    temperature: float,
    timeout: float,
    session: aiohttp.ClientSession,
    attempts: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Try each provider in priority order."""
    for provider_id in providers:
        # Handle Ollama specially (may not be in PROVIDER_CONFIGS if not initialized)
        if provider_id == "ollama":
            if provider_id not in PROVIDER_CONFIGS:
                # Create temporary config for Ollama
                config = ProviderConfig(
                    name="Ollama",
                    api_key_env="",
                    model=os.getenv("OLLAMA_MODEL", "llama3.2"),
                    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
                    provider_type="ollama",
                    priority=100,
                )
            else:
                config = PROVIDER_CONFIGS[provider_id]
        else:
            if provider_id not in PROVIDER_CONFIGS:
                logger.warning(f"Provider {provider_id} not found in PROVIDER_CONFIGS, skipping")
                continue
            config = PROVIDER_CONFIGS[provider_id]
        start_time = time.time()
        
        try:
            if config.provider_type == "ollama":
                result = await asyncio.wait_for(
                    call_ollama_provider(provider_id, messages, config, session, max_tokens=max_tokens, temperature=temperature),
                    timeout=timeout,
                )
            elif config.provider_type == "openrouter":
                result = await asyncio.wait_for(
                    call_openrouter_provider(provider_id, messages, config, session, max_tokens=max_tokens, temperature=temperature),
                    timeout=timeout,
                )
            elif config.provider_type == "groq":
                result = await asyncio.wait_for(
                    call_groq_provider(provider_id, messages, config, max_tokens=max_tokens, temperature=temperature),
                    timeout=timeout,
                )
            elif config.provider_type == "cerebras":
                result = await asyncio.wait_for(
                    call_cerebras_provider(provider_id, messages, config, max_tokens=max_tokens, temperature=temperature),
                    timeout=timeout,
                )
            elif config.provider_type == "gemini":
                if not GEMINI_AVAILABLE:
                    raise ImportError("Google Generative AI not available (Python 3.13 OpenSSL compatibility issue). Skipping Gemini provider.")
                result = await asyncio.wait_for(
                    call_gemini_provider(provider_id, messages, config, max_tokens=max_tokens, temperature=temperature),
                    timeout=timeout,
                )
            elif config.provider_type == "openai_compatible":
                result = await asyncio.wait_for(
                    call_openai_compatible_provider(provider_id, messages, config, session, max_tokens=max_tokens, temperature=temperature),
                    timeout=timeout,
                )
            elif config.provider_type == "anthropic":
                result = await asyncio.wait_for(
                    call_anthropic_provider(provider_id, messages, config, session, max_tokens=max_tokens, temperature=temperature),
                    timeout=timeout,
                )
            elif config.provider_type == "cohere":
                result = await asyncio.wait_for(
                    call_cohere_provider(provider_id, messages, config, session, max_tokens=max_tokens, temperature=temperature),
                    timeout=timeout,
                )
            else:
                raise ValueError(f"Unknown provider type: {config.provider_type}")
            
            elapsed = time.time() - start_time
            attempts.append({
                "provider": provider_id,
                "status": "success",
                "elapsed_ms": int(elapsed * 1000),
            })
            
            result["attempts"] = attempts
            return result
            
        except asyncio.TimeoutError:
            elapsed = time.time() - start_time
            attempts.append({
                "provider": provider_id,
                "status": "timeout",
                "elapsed_ms": int(elapsed * 1000),
                "error": "Request timeout",
            })
            last_error = f"{provider_id} timeout"
            
        except Exception as e:
            elapsed = time.time() - start_time
            error_msg = str(e)
            attempts.append({
                "provider": provider_id,
                "status": "error",
                "elapsed_ms": int(elapsed * 1000),
                "error": error_msg,
            })
            last_error = f"{provider_id}: {error_msg}"
            logger.warning(f"Provider {provider_id} failed: {e}")
    
    # All providers failed
    return {
        "success": False,
        "error": f"All providers failed. Last error: {last_error}",
        "attempts": attempts,
    }


# Main function for backward compatibility
async def generate(
    prompt: str,
    system_prompt: Optional[str] = None,
    max_tokens: int = 2000,
    temperature: float = 0.7,
    timeout: float = 45.0,
) -> Dict[str, Any]:
    """Main generate function with fallback."""
    async with aiohttp.ClientSession() as session:
        return await generate_with_fallback(
            prompt, system_prompt, max_tokens, temperature, timeout, session
        )


