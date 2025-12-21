#!/usr/bin/env python3
"""
Zero-Failure AI Orchestrator
16-provider fallback chain for maximum reliability and zero workflow failures.
"""

import asyncio
import json
import os
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List

import aiohttp

try:
    from tenacity import (
        retry,
        retry_if_exception_type,
        stop_after_attempt,
        wait_exponential,
    )
except ImportError:
    # Fallback if tenacity not available
    def retry(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    stop_after_attempt = None
    wait_exponential = None
    retry_if_exception_type = None

from ai_cache import AICache


class TaskType(str, Enum):
    """AI task categories"""
    CODE_REVIEW = "code_review"
    PR_ANALYSIS = "pr_analysis"
    SECURITY_SCAN = "security_scan"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    DOCUMENTATION = "documentation"
    TEST_GENERATION = "test_generation"
    DEPENDENCY_ANALYSIS = "dependency_analysis"
    GENERAL = "general"


@dataclass
class Provider:
    """AI provider configuration"""
    name: str
    api_key_env: str
    kind: str  # openai_compat, gemini, cohere, chutes, cerebras
    base_url: str
    model: str
    capabilities: List[str] = field(default_factory=list)
    timeout: int = 60
    max_retries: int = 3


class AIOrchestrator:
    """Zero-failure AI orchestrator with 16-provider fallback chain"""
    
    def __init__(self, cache_enabled: bool = True):
        self.cache = AICache() if cache_enabled else None
        self.providers = self._init_providers()
        self.metrics_dir = Path(".github/data/metrics")
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
    
    def _init_providers(self) -> List[Provider]:
        """Initialize 16 AI providers from environment variables"""
        providers = []
        
        # OpenAI-compatible providers (OpenRouter)
        openrouter_providers = [
            ("deepseek", "DEEPSEEK_API_KEY", "deepseek/deepseek-chat-v3.1:free", ["code_review", "pr_analysis", "general"]),
            ("glm", "GLM_API_KEY", "z-ai/glm-4.5-air:free", ["code_review", "general"]),
            ("grok", "GROK_API_KEY", "x-ai/grok-4-fast:free", ["code_review", "general"]),
            ("kimi", "KIMI_API_KEY", "moonshotai/kimi-k2:free", ["code_review", "general"]),
            ("qwen", "QWEN_API_KEY", "qwen/qwen3-coder:free", ["code_review", "pr_analysis", "general"]),
            ("gptoss", "GPTOSS_API_KEY", "openai/gpt-oss-120b:free", ["code_review", "general"]),
        ]
        
        for name, key_env, model, capabilities in openrouter_providers:
            if os.getenv(key_env):
                providers.append(Provider(
                    name=name,
                    api_key_env=key_env,
                    kind="openai_compat",
                    base_url="https://openrouter.ai/api/v1",
                    model=model,
                    capabilities=capabilities
                ))
        
        # NVIDIA API
        if os.getenv("NVIDIA_API_KEY"):
            providers.append(Provider(
                name="nvidia",
                api_key_env="NVIDIA_API_KEY",
                kind="openai_compat",
                base_url="https://integrate.api.nvidia.com/v1",
                model="deepseek-ai/deepseek-r1",
                capabilities=["code_review", "pr_analysis", "general"]
            ))
        
        # Codestral (Mistral)
        if os.getenv("CODESTRAL_API_KEY"):
            providers.append(Provider(
                name="codestral",
                api_key_env="CODESTRAL_API_KEY",
                kind="openai_compat",
                base_url="https://codestral.mistral.ai/v1",
                model="codestral-latest",
                capabilities=["code_review", "pr_analysis", "general"]
            ))
        
        # Chutes
        if os.getenv("CHUTES_API_KEY"):
            providers.append(Provider(
                name="chutes",
                api_key_env="CHUTES_API_KEY",
                kind="chutes",
                base_url="https://llm.chutes.ai/v1",
                model="zai-org/GLM-4.5-Air",
                capabilities=["code_review", "general"]
            ))
        
        # Cerebras
        if os.getenv("CEREBRAS_API_KEY"):
            providers.append(Provider(
                name="cerebras",
                api_key_env="CEREBRAS_API_KEY",
                kind="cerebras",
                base_url="https://api.cerebras.ai/v1",
                model="qwen-3-235b-a22b-instruct-2507",
                capabilities=["code_review", "general"]
            ))
        
        # Gemini (Google)
        if os.getenv("GEMINIAI_API_KEY"):
            providers.append(Provider(
                name="gemini",
                api_key_env="GEMINIAI_API_KEY",
                kind="gemini",
                base_url="https://generativelanguage.googleapis.com/v1beta",
                model="gemini-1.5-pro",
                capabilities=["code_review", "documentation", "general"]
            ))
        
        # Gemini 2
        if os.getenv("GEMINI2_API_KEY"):
            providers.append(Provider(
                name="gemini2",
                api_key_env="GEMINI2_API_KEY",
                kind="gemini",
                base_url="https://generativelanguage.googleapis.com/v1beta",
                model="gemini-2.0-flash",
                capabilities=["code_review", "documentation", "general"]
            ))
        
        # Groq
        if os.getenv("GROQAI_API_KEY"):
            providers.append(Provider(
                name="groq",
                api_key_env="GROQAI_API_KEY",
                kind="openai_compat",
                base_url="https://api.groq.com/openai/v1",
                model="llama-3.1-70b-versatile",
                capabilities=["code_review", "general"]
            ))
        
        # Groq 2
        if os.getenv("GROQ2_API_KEY"):
            providers.append(Provider(
                name="groq2",
                api_key_env="GROQ2_API_KEY",
                kind="openai_compat",
                base_url="https://api.groq.com/openai/v1",
                model="llama-3.1-70b-versatile",
                capabilities=["code_review", "general"]
            ))
        
        # Cohere
        if os.getenv("COHERE_API_KEY"):
            providers.append(Provider(
                name="cohere",
                api_key_env="COHERE_API_KEY",
                kind="cohere",
                base_url="https://api.cohere.ai/v2",
                model="command-a-03-2025",
                capabilities=["code_review", "pr_analysis", "general"]
            ))
        
        return providers
    
    def _provider_chain(self, task_type: str) -> List[Provider]:
        """Select and order providers based on task type and capabilities"""
        task_enum = TaskType(task_type) if task_type in [t.value for t in TaskType] else TaskType.GENERAL
        
        # Prioritize providers with matching capabilities
        matching = [p for p in self.providers if task_type in p.capabilities or "general" in p.capabilities]
        others = [p for p in self.providers if p not in matching]
        
        return matching + others
    
    async def execute(
        self,
        task_type: str,
        system_message: str,
        user_prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """Execute AI task with fallback chain"""
        start_time = time.time()
        
        # Check cache first
        if use_cache and self.cache:
            cached = self.cache.get(task_type, user_prompt, system_message)
            if cached:
                return {
                    "success": True,
                    "provider": "cache",
                    "response": cached.get("response", ""),
                    "duration_ms": int((time.time() - start_time) * 1000),
                    "fallback_count": 0,
                    "cached": True
                }
        
        # Get provider chain
        provider_chain = self._provider_chain(task_type)
        
        if not provider_chain:
            return {
                "success": False,
                "error": "No AI providers available",
                "duration_ms": int((time.time() - start_time) * 1000),
                "fallback_count": 0
            }
        
        # Try each provider in chain
        last_error = None
        fallback_count = 0
        
        for i, provider in enumerate(provider_chain):
            try:
                result = await self._call_provider(
                    provider, system_message, user_prompt, max_tokens, temperature
                )
                
                # Cache successful response
                if use_cache and self.cache and result.get("success"):
                    self.cache.set(task_type, user_prompt, {
                        "response": result.get("response", ""),
                        "provider": provider.name
                    }, system_message)
                
                # Log metrics
                self._log_metrics(provider.name, task_type, True, 
                                 int((time.time() - start_time) * 1000), fallback_count)
                
                return {
                    "success": True,
                    "provider": provider.name,
                    "response": result.get("response", ""),
                    "duration_ms": int((time.time() - start_time) * 1000),
                    "fallback_count": fallback_count,
                    "cached": False
                }
            
            except Exception as e:
                last_error = str(e)
                fallback_count += 1
                continue
        
        # All providers failed
        self._log_metrics("none", task_type, False, 
                         int((time.time() - start_time) * 1000), fallback_count)
        
        return {
            "success": False,
            "error": f"All {len(provider_chain)} providers failed. Last error: {last_error}",
            "duration_ms": int((time.time() - start_time) * 1000),
            "fallback_count": fallback_count,
            "providers_tried": len(provider_chain)
        }
    
    async def _call_provider(
        self,
        provider: Provider,
        system_message: str,
        user_prompt: str,
        max_tokens: int,
        temperature: float
    ) -> Dict[str, Any]:
        """Route to appropriate provider adapter"""
        if provider.kind == "openai_compat":
            return await self._call_openai_compat(provider, system_message, user_prompt, max_tokens, temperature)
        elif provider.kind == "gemini":
            return await self._call_gemini(provider, system_message, user_prompt, max_tokens, temperature)
        elif provider.kind == "cohere":
            return await self._call_cohere(provider, system_message, user_prompt, max_tokens, temperature)
        elif provider.kind == "chutes":
            return await self._call_chutes(provider, system_message, user_prompt, max_tokens, temperature)
        elif provider.kind == "cerebras":
            return await self._call_cerebras(provider, system_message, user_prompt, max_tokens, temperature)
        else:
            raise ValueError(f"Unknown provider kind: {provider.kind}")
    
    async def _call_openai_compat(
        self,
        provider: Provider,
        system_message: str,
        user_prompt: str,
        max_tokens: int,
        temperature: float
    ) -> Dict[str, Any]:
        """Call OpenAI-compatible API"""
        api_key = os.getenv(provider.api_key_env)
        if not api_key:
            raise ValueError(f"API key not found: {provider.api_key_env}")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Add OpenRouter-specific headers
        if "openrouter.ai" in provider.base_url:
            headers.update({
                "HTTP-Referer": "https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System",
                "X-Title": "AMAS AI Orchestrator"
            })
        
        payload = {
            "model": provider.model,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        timeout = aiohttp.ClientTimeout(total=provider.timeout)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                f"{provider.base_url}/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"API error {response.status}: {error_text}")
                
                data = await response.json()
                return {
                    "success": True,
                    "response": data["choices"][0]["message"]["content"]
                }
    
    async def _call_gemini(
        self,
        provider: Provider,
        system_message: str,
        user_prompt: str,
        max_tokens: int,
        temperature: float
    ) -> Dict[str, Any]:
        """Call Google Gemini API"""
        api_key = os.getenv(provider.api_key_env)
        if not api_key:
            raise ValueError(f"API key not found: {provider.api_key_env}")
        
        # Combine system and user messages for Gemini
        full_prompt = f"{system_message}\n\n{user_prompt}"
        
        payload = {
            "contents": [{
                "parts": [{"text": full_prompt}]
            }],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }
        
        timeout = aiohttp.ClientTimeout(total=provider.timeout)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                f"{provider.base_url}/models/{provider.model}:generateContent",
                headers={"X-goog-api-key": api_key},
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"API error {response.status}: {error_text}")
                
                data = await response.json()
                return {
                    "success": True,
                    "response": data["candidates"][0]["content"]["parts"][0]["text"]
                }
    
    async def _call_cohere(
        self,
        provider: Provider,
        system_message: str,
        user_prompt: str,
        max_tokens: int,
        temperature: float
    ) -> Dict[str, Any]:
        """Call Cohere API"""
        api_key = os.getenv(provider.api_key_env)
        if not api_key:
            raise ValueError(f"API key not found: {provider.api_key_env}")
        
        # Combine system and user messages
        full_prompt = f"{system_message}\n\n{user_prompt}"
        
        payload = {
            "model": provider.model,
            "messages": [{"role": "user", "content": full_prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        timeout = aiohttp.ClientTimeout(total=provider.timeout)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                f"{provider.base_url}/chat",
                headers=headers,
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"API error {response.status}: {error_text}")
                
                data = await response.json()
                return {
                    "success": True,
                    "response": data["text"]
                }
    
    async def _call_chutes(
        self,
        provider: Provider,
        system_message: str,
        user_prompt: str,
        max_tokens: int,
        temperature: float
    ) -> Dict[str, Any]:
        """Call Chutes API (similar to OpenAI but different endpoint)"""
        api_key = os.getenv(provider.api_key_env)
        if not api_key:
            raise ValueError(f"API key not found: {provider.api_key_env}")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": provider.model,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        timeout = aiohttp.ClientTimeout(total=provider.timeout)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                f"{provider.base_url}/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"API error {response.status}: {error_text}")
                
                data = await response.json()
                return {
                    "success": True,
                    "response": data["choices"][0]["message"]["content"]
                }
    
    async def _call_cerebras(
        self,
        provider: Provider,
        system_message: str,
        user_prompt: str,
        max_tokens: int,
        temperature: float
    ) -> Dict[str, Any]:
        """Call Cerebras API (uses OpenAI-compatible format)"""
        # For now, use OpenAI-compatible format
        return await self._call_openai_compat(provider, system_message, user_prompt, max_tokens, temperature)
    
    def _log_metrics(
        self,
        provider: str,
        task_type: str,
        success: bool,
        duration_ms: int,
        fallback_count: int
    ) -> None:
        """Log execution metrics"""
        metric = {
            "timestamp": datetime.now().isoformat(),
            "provider": provider,
            "task_type": task_type,
            "success": success,
            "duration_ms": duration_ms,
            "fallback_count": fallback_count
        }
        
        metric_file = self.metrics_dir / f"metrics_{datetime.now().strftime('%Y%m%d')}.jsonl"
        try:
            with open(metric_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(metric) + "\n")
        except Exception:
            pass  # Silently fail if metrics write fails


# CLI interface
async def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Zero-Failure AI Orchestrator")
    parser.add_argument("--task-type", required=True, help="Task type")
    parser.add_argument("--system-message", required=True, help="System message")
    parser.add_argument("--user-prompt", required=True, help="User prompt")
    parser.add_argument("--max-tokens", type=int, default=2000, help="Max tokens")
    parser.add_argument("--temperature", type=float, default=0.7, help="Temperature")
    parser.add_argument("--no-cache", action="store_true", help="Disable cache")
    parser.add_argument("--output", help="Output file (JSON)")
    
    args = parser.parse_args()
    
    orchestrator = AIOrchestrator(cache_enabled=not args.no_cache)
    result = await orchestrator.execute(
        task_type=args.task_type,
        system_message=args.system_message,
        user_prompt=args.user_prompt,
        max_tokens=args.max_tokens,
        temperature=args.temperature
    )
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    asyncio.run(main())
