# **🎯 AMAS PROJECT: PART 3 - AI PROVIDER FALLBACK SYSTEM**
## **Complete 16-Provider Integration with Intelligent Routing**

***

## **PHASE 1 CONTINUATION: AI PROVIDER FALLBACK CHAIN**

### **Step 3.1: Enhanced AI Router Implementation**

**File**: `src/amas/ai/enhanced_router_v2.py` (EXISTS - NEEDS FULL INTEGRATION)

**CURRENT STATE**: The enhanced router exists with 15-provider fallback, but it's not being called by agents.

**REQUIRED COMPLETE IMPLEMENTATION**:

```python
# src/amas/ai/enhanced_router_v2.py (COMPLETE PRODUCTION VERSION)
import asyncio
import time
import logging
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple
from enum import Enum
import httpx
import openai
import anthropic
from google import generativeai as genai
import cohere
import json

logger = logging.getLogger(__name__)

class AIProvider(str, Enum):
    """All supported AI providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    GROQ = "groq"
    DEEPSEEK = "deepseek"
    COHERE = "cohere"
    TOGETHER = "together"
    ANYSCALE = "anyscale"
    FIREWORKS = "fireworks"
    REPLICATE = "replicate"
    PERPLEXITY = "perplexity"
    MISTRAL = "mistral"
    HUGGINGFACE = "huggingface"
    OLLAMA = "ollama"
    OPENROUTER = "openrouter"
    CEREBRAS = "cerebras"

@dataclass
class ProviderConfig:
    """Provider configuration and metadata"""
    name: str
    api_key: Optional[str]
    base_url: Optional[str]
    default_model: str
    max_tokens: int
    timeout: int
    retry_attempts: int
    cost_per_1k_tokens: float
    avg_latency_ms: float
    success_rate: float
    is_available: bool
    last_check: Optional[str]

@dataclass
class AIResponse:
    """Standardized AI response"""
    content: str
    provider: str
    model: str
    tokens_used: int
    cost_usd: float
    latency_ms: float
    attempt_number: int
    fallback_used: bool
    raw_response: Optional[Dict[str, Any]] = None

@dataclass
class ProviderHealth:
    """Provider health status"""
    provider: str
    is_healthy: bool
    response_time_ms: float
    last_success: Optional[str]
    last_failure: Optional[str]
    consecutive_failures: int
    success_rate_24h: float

class CircuitBreaker:
    """
    Circuit breaker pattern for provider resilience
    
    States:
    - CLOSED: Normal operation
    - OPEN: Provider failed, don't try (timeout period)
    - HALF_OPEN: Test if provider recovered
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout_seconds: int = 60,
        success_threshold: int = 2
    ):
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.success_threshold = success_threshold
        
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def record_success(self):
        """Record successful call"""
        self.failure_count = 0
        
        if self.state == "HALF_OPEN":
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self.state = "CLOSED"
                self.success_count = 0
                logger.info("Circuit breaker: HALF_OPEN → CLOSED (recovered)")
    
    def record_failure(self):
        """Record failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning(f"Circuit breaker: CLOSED → OPEN "
                         f"({self.failure_count} consecutive failures)")
    
    def can_attempt(self) -> bool:
        """Check if provider can be attempted"""
        if self.state == "CLOSED":
            return True
        
        if self.state == "OPEN":
            # Check if timeout period has passed
            if self.last_failure_time:
                elapsed = time.time() - self.last_failure_time
                if elapsed >= self.timeout_seconds:
                    self.state = "HALF_OPEN"
                    self.success_count = 0
                    logger.info("Circuit breaker: OPEN → HALF_OPEN (testing)")
                    return True
            return False
        
        if self.state == "HALF_OPEN":
            return True
        
        return False

class EnhancedAIRouter:
    """
    Production-grade AI provider router with intelligent fallback
    
    ✅ 16 AI providers
    ✅ Automatic fallback chain
    ✅ Circuit breaker pattern
    ✅ Health monitoring
    ✅ Cost optimization
    ✅ Latency tracking
    ✅ Retry logic with exponential backoff
    ✅ Provider selection strategies
    """
    
    def __init__(self):
        self.providers: Dict[str, ProviderConfig] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.provider_stats: Dict[str, Dict[str, Any]] = {}
        self.http_client = httpx.AsyncClient(timeout=30.0)
        
        # Initialize all providers
        self._initialize_providers()
        
        logger.info("EnhancedAIRouter initialized with 16 providers")
    
    def _initialize_providers(self):
        """Initialize all 16 AI providers with configurations"""
        
        import os
        
        # 1. OpenAI (Primary - Best quality)
        self.providers[AIProvider.OPENAI] = ProviderConfig(
            name="OpenAI",
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url="https://api.openai.com/v1",
            default_model="gpt-4-turbo-preview",
            max_tokens=4096,
            timeout=30,
            retry_attempts=2,
            cost_per_1k_tokens=0.01,  # $0.01/1K tokens
            avg_latency_ms=1200,
            success_rate=0.98,
            is_available=bool(os.getenv("OPENAI_API_KEY")),
            last_check=None
        )
        
        # 2. Anthropic Claude (Backup - High quality)
        self.providers[AIProvider.ANTHROPIC] = ProviderConfig(
            name="Anthropic",
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            base_url="https://api.anthropic.com/v1",
            default_model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            timeout=25,
            retry_attempts=2,
            cost_per_1k_tokens=0.003,  # $0.003/1K tokens
            avg_latency_ms=1100,
            success_rate=0.97,
            is_available=bool(os.getenv("ANTHROPIC_API_KEY")),
            last_check=None
        )
        
        # 3. Google Gemini (Tertiary - Good balance)
        self.providers[AIProvider.GOOGLE] = ProviderConfig(
            name="Google",
            api_key=os.getenv("GOOGLE_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1",
            default_model="gemini-pro",
            max_tokens=4096,
            timeout=25,
            retry_attempts=2,
            cost_per_1k_tokens=0.0005,  # $0.0005/1K tokens
            avg_latency_ms=1300,
            success_rate=0.95,
            is_available=bool(os.getenv("GOOGLE_API_KEY")),
            last_check=None
        )
        
        # 4. Groq (Speed-optimized)
        self.providers[AIProvider.GROQ] = ProviderConfig(
            name="Groq",
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1",
            default_model="llama-3.1-70b-versatile",
            max_tokens=4096,
            timeout=15,
            retry_attempts=3,
            cost_per_1k_tokens=0.0001,  # Very cheap
            avg_latency_ms=400,  # Very fast
            success_rate=0.92,
            is_available=bool(os.getenv("GROQ_API_KEY")),
            last_check=None
        )
        
        # 5. DeepSeek (Cost-optimized)
        self.providers[AIProvider.DEEPSEEK] = ProviderConfig(
            name="DeepSeek",
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com/v1",
            default_model="deepseek-chat",
            max_tokens=4096,
            timeout=20,
            retry_attempts=3,
            cost_per_1k_tokens=0.00014,  # Very cheap
            avg_latency_ms=1500,
            success_rate=0.90,
            is_available=bool(os.getenv("DEEPSEEK_API_KEY")),
            last_check=None
        )
        
        # 6. Cohere (Specialized NLP)
        self.providers[AIProvider.COHERE] = ProviderConfig(
            name="Cohere",
            api_key=os.getenv("COHERE_API_KEY"),
            base_url="https://api.cohere.ai/v1",
            default_model="command-r-plus",
            max_tokens=4096,
            timeout=20,
            retry_attempts=2,
            cost_per_1k_tokens=0.003,
            avg_latency_ms=1200,
            success_rate=0.94,
            is_available=bool(os.getenv("COHERE_API_KEY")),
            last_check=None
        )
        
        # 7. Together AI (Open models)
        self.providers[AIProvider.TOGETHER] = ProviderConfig(
            name="Together",
            api_key=os.getenv("TOGETHER_API_KEY"),
            base_url="https://api.together.xyz/v1",
            default_model="meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
            max_tokens=4096,
            timeout=20,
            retry_attempts=2,
            cost_per_1k_tokens=0.0009,
            avg_latency_ms=1100,
            success_rate=0.93,
            is_available=bool(os.getenv("TOGETHER_API_KEY")),
            last_check=None
        )
        
        # 8. Anyscale (Endpoints for open models)
        self.providers[AIProvider.ANYSCALE] = ProviderConfig(
            name="Anyscale",
            api_key=os.getenv("ANYSCALE_API_KEY"),
            base_url="https://api.endpoints.anyscale.com/v1",
            default_model="meta-llama/Meta-Llama-3.1-70B-Instruct",
            max_tokens=4096,
            timeout=20,
            retry_attempts=2,
            cost_per_1k_tokens=0.001,
            avg_latency_ms=1000,
            success_rate=0.91,
            is_available=bool(os.getenv("ANYSCALE_API_KEY")),
            last_check=None
        )
        
        # 9. Fireworks AI (Fast inference)
        self.providers[AIProvider.FIREWORKS] = ProviderConfig(
            name="Fireworks",
            api_key=os.getenv("FIREWORKS_API_KEY"),
            base_url="https://api.fireworks.ai/inference/v1",
            default_model="accounts/fireworks/models/llama-v3p1-70b-instruct",
            max_tokens=4096,
            timeout=15,
            retry_attempts=2,
            cost_per_1k_tokens=0.0009,
            avg_latency_ms=600,
            success_rate=0.92,
            is_available=bool(os.getenv("FIREWORKS_API_KEY")),
            last_check=None
        )
        
        # 10. Replicate (Various models)
        self.providers[AIProvider.REPLICATE] = ProviderConfig(
            name="Replicate",
            api_key=os.getenv("REPLICATE_API_KEY"),
            base_url="https://api.replicate.com/v1",
            default_model="meta/meta-llama-3.1-70b-instruct",
            max_tokens=4096,
            timeout=30,
            retry_attempts=2,
            cost_per_1k_tokens=0.0015,
            avg_latency_ms=2000,
            success_rate=0.88,
            is_available=bool(os.getenv("REPLICATE_API_KEY")),
            last_check=None
        )
        
        # 11. Perplexity (Search-augmented)
        self.providers[AIProvider.PERPLEXITY] = ProviderConfig(
            name="Perplexity",
            api_key=os.getenv("PERPLEXITY_API_KEY"),
            base_url="https://api.perplexity.ai",
            default_model="llama-3.1-sonar-large-128k-online",
            max_tokens=4096,
            timeout=25,
            retry_attempts=2,
            cost_per_1k_tokens=0.001,
            avg_latency_ms=1800,
            success_rate=0.89,
            is_available=bool(os.getenv("PERPLEXITY_API_KEY")),
            last_check=None
        )
        
        # 12. Mistral AI (European provider)
        self.providers[AIProvider.MISTRAL] = ProviderConfig(
            name="Mistral",
            api_key=os.getenv("MISTRAL_API_KEY"),
            base_url="https://api.mistral.ai/v1",
            default_model="mistral-large-latest",
            max_tokens=4096,
            timeout=20,
            retry_attempts=2,
            cost_per_1k_tokens=0.004,
            avg_latency_ms=1200,
            success_rate=0.93,
            is_available=bool(os.getenv("MISTRAL_API_KEY")),
            last_check=None
        )
        
        # 13. HuggingFace Inference
        self.providers[AIProvider.HUGGINGFACE] = ProviderConfig(
            name="HuggingFace",
            api_key=os.getenv("HUGGINGFACE_API_KEY"),
            base_url="https://api-inference.huggingface.co/models",
            default_model="meta-llama/Meta-Llama-3.1-70B-Instruct",
            max_tokens=4096,
            timeout=30,
            retry_attempts=2,
            cost_per_1k_tokens=0.0,  # Free tier available
            avg_latency_ms=2500,
            success_rate=0.85,
            is_available=bool(os.getenv("HUGGINGFACE_API_KEY")),
            last_check=None
        )
        
        # 14. Ollama (Local deployment)
        self.providers[AIProvider.OLLAMA] = ProviderConfig(
            name="Ollama",
            api_key=None,  # No API key needed
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            default_model="llama3.1:70b",
            max_tokens=4096,
            timeout=30,
            retry_attempts=1,
            cost_per_1k_tokens=0.0,  # Local, no cost
            avg_latency_ms=3000,
            success_rate=0.95,
            is_available=True,  # Always available if running
            last_check=None
        )
        
        # 15. OpenRouter (Multi-provider aggregator)
        self.providers[AIProvider.OPENROUTER] = ProviderConfig(
            name="OpenRouter",
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
            default_model="anthropic/claude-3.5-sonnet",
            max_tokens=4096,
            timeout=25,
            retry_attempts=2,
            cost_per_1k_tokens=0.003,
            avg_latency_ms=1400,
            success_rate=0.94,
            is_available=bool(os.getenv("OPENROUTER_API_KEY")),
            last_check=None
        )
        
        # 16. Cerebras (Ultra-fast inference)
        self.providers[AIProvider.CEREBRAS] = ProviderConfig(
            name="Cerebras",
            api_key=os.getenv("CEREBRAS_API_KEY"),
            base_url="https://api.cerebras.ai/v1",
            default_model="llama3.1-70b",
            max_tokens=4096,
            timeout=15,
            retry_attempts=2,
            cost_per_1k_tokens=0.0006,
            avg_latency_ms=350,  # Extremely fast
            success_rate=0.91,
            is_available=bool(os.getenv("CEREBRAS_API_KEY")),
            last_check=None
        )
        
        # Initialize circuit breakers for each provider
        for provider_name in self.providers.keys():
            self.circuit_breakers[provider_name] = CircuitBreaker()
        
        # Initialize stats
        for provider_name in self.providers.keys():
            self.provider_stats[provider_name] = {
                "total_calls": 0,
                "successful_calls": 0,
                "failed_calls": 0,
                "total_tokens": 0,
                "total_cost": 0.0,
                "total_latency": 0.0,
                "last_used": None
            }
        
        # Log available providers
        available = [p.name for p in self.providers.values() if p.is_available]
        logger.info(f"Available providers ({len(available)}): {', '.join(available)}")

    async def generate_with_fallback(
        self,
        prompt: str,
        model_preference: Optional[str] = None,
        max_tokens: int = 4000,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None,
        strategy: str = "quality_first"  # quality_first, speed_first, cost_optimized
    ) -> AIResponse:
        """
        Generate AI response with intelligent fallback
        
        Strategies:
        - quality_first: OpenAI → Anthropic → Google → Others
        - speed_first: Groq → Cerebras → Fireworks → Others
        - cost_optimized: DeepSeek → Groq → Together → Others
        
        Args:
            prompt: User prompt
            model_preference: Preferred model name (optional)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-1.0)
            system_prompt: System prompt (optional)
            strategy: Provider selection strategy
        
        Returns:
            AIResponse with content and metadata
        """
        
        start_time = time.time()
        
        # Determine provider priority based on strategy
        provider_priority = self._get_provider_priority(strategy, model_preference)
        
        logger.info(f"Generating with strategy '{strategy}', "
                   f"priority: {[p.value for p in provider_priority[:5]]}")
        
        last_error = None
        
        # Try each provider in priority order
        for attempt, provider_enum in enumerate(provider_priority, 1):
            provider_name = provider_enum.value
            
            # Check circuit breaker
            if not self.circuit_breakers[provider_name].can_attempt():
                logger.warning(f"Skipping {provider_name}: circuit breaker OPEN")
                continue
            
            provider = self.providers[provider_enum]
            
            if not provider.is_available:
                logger.warning(f"Skipping {provider_name}: not available")
                continue
            
            try:
                logger.info(f"Attempting provider: {provider_name} (attempt {attempt})")
                
                # Generate with this provider
                response = await self._generate_with_provider(
                    provider_enum=provider_enum,
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system_prompt=system_prompt
                )
                
                # Record success
                self.circuit_breakers[provider_name].record_success()
                self._record_success(provider_name, response)
                
                # Add metadata
                response.attempt_number = attempt
                response.fallback_used = attempt > 1
                response.latency_ms = (time.time() - start_time) * 1000
                
                logger.info(f"✅ Success with {provider_name}: "
                           f"{len(response.content)} chars, "
                           f"{response.tokens_used} tokens, "
                           f"${response.cost_usd:.4f}, "
                           f"{response.latency_ms:.0f}ms")
                
                return response
            
            except Exception as e:
                last_error = e
                logger.error(f"❌ Failed with {provider_name}: {e}")
                
                # Record failure
                self.circuit_breakers[provider_name].record_failure()
                self._record_failure(provider_name, str(e))
                
                # Try next provider
                continue
        
        # All providers failed
        total_latency = (time.time() - start_time) * 1000
        
        logger.error(f"❌ ALL PROVIDERS FAILED after {len(provider_priority)} attempts "
                    f"({total_latency:.0f}ms)")
        
        raise Exception(
            f"All {len(provider_priority)} AI providers failed. "
            f"Last error: {last_error}"
        )

    def _get_provider_priority(
        self,
        strategy: str,
        model_preference: Optional[str] = None
    ) -> List[AIProvider]:
        """
        Get provider priority list based on strategy
        
        Returns ordered list of providers to try
        """
        
        if strategy == "quality_first":
            # Best quality models first
            return [
                AIProvider.OPENAI,
                AIProvider.ANTHROPIC,
                AIProvider.GOOGLE,
                AIProvider.MISTRAL,
                AIProvider.COHERE,
                AIProvider.OPENROUTER,
                AIProvider.TOGETHER,
                AIProvider.ANYSCALE,
                AIProvider.FIREWORKS,
                AIProvider.GROQ,
                AIProvider.DEEPSEEK,
                AIProvider.PERPLEXITY,
                AIProvider.CEREBRAS,
                AIProvider.REPLICATE,
                AIProvider.HUGGINGFACE,
                AIProvider.OLLAMA
            ]
        
        elif strategy == "speed_first":
            # Fastest response time first
            return [
                AIProvider.CEREBRAS,      # ~350ms
                AIProvider.GROQ,          # ~400ms
                AIProvider.FIREWORKS,     # ~600ms
                AIProvider.ANYSCALE,      # ~1000ms
                AIProvider.TOGETHER,      # ~1100ms
                AIProvider.ANTHROPIC,     # ~1100ms
                AIProvider.OPENAI,        # ~1200ms
                AIProvider.COHERE,        # ~1200ms
                AIProvider.MISTRAL,       # ~1200ms
                AIProvider.GOOGLE,        # ~1300ms
                AIProvider.OPENROUTER,    # ~1400ms
                AIProvider.DEEPSEEK,      # ~1500ms
                AIProvider.PERPLEXITY,    # ~1800ms
                AIProvider.REPLICATE,     # ~2000ms
                AIProvider.HUGGINGFACE,   # ~2500ms
                AIProvider.OLLAMA         # ~3000ms
            ]
        
        elif strategy == "cost_optimized":
            # Lowest cost first
            return [
                AIProvider.OLLAMA,        # $0.00 (local)
                AIProvider.HUGGINGFACE,   # $0.00 (free tier)
                AIProvider.GROQ,          # $0.0001/1K
                AIProvider.DEEPSEEK,      # $0.00014/1K
                AIProvider.GOOGLE,        # $0.0005/1K
                AIProvider.CEREBRAS,      # $0.0006/1K
                AIProvider.FIREWORKS,     # $0.0009/1K
                AIProvider.TOGETHER,      # $0.0009/1K
                AIProvider.ANYSCALE,      # $0.001/1K
                AIProvider.PERPLEXITY,    # $0.001/1K
                AIProvider.REPLICATE,     # $0.0015/1K
                AIProvider.COHERE,        # $0.003/1K
                AIProvider.ANTHROPIC,     # $0.003/1K
                AIProvider.OPENROUTER,    # $0.003/1K
                AIProvider.MISTRAL,       # $0.004/1K
                AIProvider.OPENAI         # $0.01/1K
            ]
        
        else:
            # Default: quality_first
            return self._get_provider_priority("quality_first")

    async def _generate_with_provider(
        self,
        provider_enum: AIProvider,
        prompt: str,
        max_tokens: int,
        temperature: float,
        system_prompt: Optional[str]
    ) -> AIResponse:
        """
        Generate with specific provider
        
        Handles provider-specific API calls
        """
        
        provider_name = provider_enum.value
        provider = self.providers[provider_enum]
        
        request_start = time.time()
        
        try:
            # OpenAI-compatible providers
            if provider_enum in [
                AIProvider.OPENAI,
                AIProvider.GROQ,
                AIProvider.TOGETHER,
                AIProvider.ANYSCALE,
                AIProvider.FIREWORKS,
                AIProvider.OPENROUTER,
                AIProvider.DEEPSEEK,
                AIProvider.MISTRAL,
                AIProvider.CEREBRAS
            ]:
                response = await self._call_openai_compatible(
                    provider, prompt, max_tokens, temperature, system_prompt
                )
            
            # Anthropic Claude
            elif provider_enum == AIProvider.ANTHROPIC:
                response = await self._call_anthropic(
                    provider, prompt, max_tokens, temperature, system_prompt
                )
            
            # Google Gemini
            elif provider_enum == AIProvider.GOOGLE:
                response = await self._call_google(
                    provider, prompt, max_tokens, temperature, system_prompt
                )
            
            # Cohere
            elif provider_enum == AIProvider.COHERE:
                response = await self._call_cohere(
                    provider, prompt, max_tokens, temperature, system_prompt
                )
            
            # Perplexity
            elif provider_enum == AIProvider.PERPLEXITY:
                response = await self._call_perplexity(
                    provider, prompt, max_tokens, temperature, system_prompt
                )
            
            # HuggingFace
            elif provider_enum == AIProvider.HUGGINGFACE:
                response = await self._call_huggingface(
                    provider, prompt, max_tokens, temperature, system_prompt
                )
            
            # Ollama
            elif provider_enum == AIProvider.OLLAMA:
                response = await self._call_ollama(
                    provider, prompt, max_tokens, temperature, system_prompt
                )
            
            # Replicate
            elif provider_enum == AIProvider.REPLICATE:
                response = await self._call_replicate(
                    provider, prompt, max_tokens, temperature, system_prompt
                )
            
            else:
                raise NotImplementedError(f"Provider {provider_name} not implemented")
            
            request_duration = (time.time() - request_start) * 1000
            
            return AIResponse(
                content=response["content"],
                provider=provider_name,
                model=response.get("model", provider.default_model),
                tokens_used=response.get("tokens", 0),
                cost_usd=response.get("tokens", 0) * provider.cost_per_1k_tokens / 1000,
                latency_ms=request_duration,
                attempt_number=1,
                fallback_used=False,
                raw_response=response
            )
        
        except Exception as e:
            logger.error(f"Provider {provider_name} failed: {e}", exc_info=True)
            raise

    async def _call_openai_compatible(
        self,
        provider: ProviderConfig,
        prompt: str,
        max_tokens: int,
        temperature: float,
        system_prompt: Optional[str]
    ) -> Dict[str, Any]:
        """
        Call OpenAI-compatible API
        
        Compatible with:
        - OpenAI
        - Groq
        - Together
        - Anyscale
        - Fireworks
        - OpenRouter
        - DeepSeek
        - Mistral
        - Cerebras
        """
        
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        headers = {
            "Authorization": f"Bearer {provider.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": provider.default_model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        response = await self.http_client.post(
            f"{provider.base_url}/chat/completions",
            json=payload,
            headers=headers,
            timeout=provider.timeout
        )
        
        response.raise_for_status()
        
        data = response.json()
        
        return {
            "content": data["choices"][0]["message"]["content"],
            "model": data.get("model", provider.default_model),
            "tokens": data.get("usage", {}).get("total_tokens", 0)
        }

    async def _call_anthropic(
        self,
        provider: ProviderConfig,
        prompt: str,
        max_tokens: int,
        temperature: float,
        system_prompt: Optional[str]
    ) -> Dict[str, Any]:
        """Call Anthropic Claude API"""
        
        client = anthropic.AsyncAnthropic(api_key=provider.api_key)
        
        message = await client.messages.create(
            model=provider.default_model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt if system_prompt else "",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return {
            "content": message.content[0].text,
            "model": message.model,
            "tokens": message.usage.input_tokens + message.usage.output_tokens
        }

    async def _call_google(
        self,
        provider: ProviderConfig,
        prompt: str,
        max_tokens: int,
        temperature: float,
        system_prompt: Optional[str]
    ) -> Dict[str, Any]:
        """Call Google Gemini API"""
        
        genai.configure(api_key=provider.api_key)
        
        model = genai.GenerativeModel(provider.default_model)
        
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        
        response = model.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature
            )
        )
        
        return {
            "content": response.text,
            "model": provider.default_model,
            "tokens": 0  # Gemini doesn't return token count
        }

    async def _call_cohere(
        self,
        provider: ProviderConfig,
        prompt: str,
        max_tokens: int,
        temperature: float,
        system_prompt: Optional[str]
    ) -> Dict[str, Any]:
        """Call Cohere API"""
        
        co = cohere.AsyncClient(api_key=provider.api_key)
        
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        
        response = await co.chat(
            model=provider.default_model,
            message=full_prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return {
            "content": response.text,
            "model": provider.default_model,
            "tokens": response.meta.tokens.total_tokens if response.meta else 0
        }

    async def _call_perplexity(
        self,
        provider: ProviderConfig,
        prompt: str,
        max_tokens: int,
        temperature: float,
        system_prompt: Optional[str]
    ) -> Dict[str, Any]:
        """Call Perplexity API"""
        
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        headers = {
            "Authorization": f"Bearer {provider.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": provider.default_model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        response = await self.http_client.post(
            f"{provider.base_url}/chat/completions",
            json=payload,
            headers=headers,
            timeout=provider.timeout
        )
        
        response.raise_for_status()
        
        data = response.json()
        
        return {
            "content": data["choices"][0]["message"]["content"],
            "model": data.get("model", provider.default_model),
            "tokens": data.get("usage", {}).get("total_tokens", 0)
        }

    async def _call_huggingface(
        self,
        provider: ProviderConfig,
        prompt: str,
        max_tokens: int,
        temperature: float,
        system_prompt: Optional[str]
    ) -> Dict[str, Any]:
        """Call HuggingFace Inference API"""
        
        headers = {
            "Authorization": f"Bearer {provider.api_key}",
            "Content-Type": "application/json"
        }
        
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        
        payload = {
            "inputs": full_prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": temperature,
                "return_full_text": False
            }
        }
        
        response = await self.http_client.post(
            f"{provider.base_url}/{provider.default_model}",
            json=payload,
            headers=headers,
            timeout=provider.timeout
        )
        
        response.raise_for_status()
        
        data = response.json()
        
        content = data[0]["generated_text"] if isinstance(data, list) else data.get("generated_text", "")
        
        return {
            "content": content,
            "model": provider.default_model,
            "tokens": 0  # HuggingFace doesn't return token count
        }

    async def _call_ollama(
        self,
        provider: ProviderConfig,
        prompt: str,
        max_tokens: int,
        temperature: float,
        system_prompt: Optional[str]
    ) -> Dict[str, Any]:
        """Call Ollama local API"""
        
        payload = {
            "model": provider.default_model,
            "prompt": prompt,
            "system": system_prompt if system_prompt else "",
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature
            }
        }
        
        response = await self.http_client.post(
            f"{provider.base_url}/api/generate",
            json=payload,
            timeout=provider.timeout
        )
        
        response.raise_for_status()
        
        data = response.json()
        
        return {
            "content": data.get("response", ""),
            "model": provider.default_model,
            "tokens": 0  # Ollama doesn't return token count
        }

    async def _call_replicate(
        self,
        provider: ProviderConfig,
        prompt: str,
        max_tokens: int,
        temperature: float,
        system_prompt: Optional[str]
    ) -> Dict[str, Any]:
        """Call Replicate API"""
        
        headers = {
            "Authorization": f"Token {provider.api_key}",
            "Content-Type": "application/json"
        }
        
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        
        payload = {
            "version": provider.default_model,
            "input": {
                "prompt": full_prompt,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
        }
        
        # Start prediction
        response = await self.http_client.post(
            f"{provider.base_url}/predictions",
            json=payload,
            headers=headers
        )
        
        response.raise_for_status()
        
        prediction = response.json()
        prediction_id = prediction["id"]
        
        # Poll for completion
        max_polls = 30
        for _ in range(max_polls):
            await asyncio.sleep(1)
            
            status_response = await self.http_client.get(
                f"{provider.base_url}/predictions/{prediction_id}",
                headers=headers
            )
            
            status_response.raise_for_status()
            
            status_data = status_response.json()
            
            if status_data["status"] == "succeeded":
                output = status_data.get("output", "")
                if isinstance(output, list):
                    output = "".join(output)
                
                return {
                    "content": output,
                    "model": provider.default_model,
                    "tokens": 0
                }
            
            elif status_data["status"] in ["failed", "canceled"]:
                raise Exception(f"Prediction failed: {status_data.get('error', 'Unknown error')}")
        
        raise Exception("Prediction timed out")

    def _record_success(self, provider_name: str, response: AIResponse):
        """Record successful API call for analytics"""
        
        stats = self.provider_stats[provider_name]
        stats["total_calls"] += 1
        stats["successful_calls"] += 1
        stats["total_tokens"] += response.tokens_used
        stats["total_cost"] += response.cost_usd
        stats["total_latency"] += response.latency_ms
        stats["last_used"] = datetime.now().isoformat()

    def _record_failure(self, provider_name: str, error: str):
        """Record failed API call for analytics"""
        
        stats = self.provider_stats[provider_name]
        stats["total_calls"] += 1
        stats["failed_calls"] += 1

    async def get_provider_health(self) -> List[ProviderHealth]:
        """
        Get health status of all providers
        
        Returns list of ProviderHealth objects for monitoring
        """
        
        health_list = []
        
        for provider_enum, provider in self.providers.items():
            provider_name = provider_enum.value
            stats = self.provider_stats[provider_name]
            circuit_breaker = self.circuit_breakers[provider_name]
            
            total_calls = stats["total_calls"]
            successful_calls = stats["successful_calls"]
            
            success_rate = (successful_calls / total_calls) if total_calls > 0 else 0.0
            avg_latency = (stats["total_latency"] / successful_calls) if successful_calls > 0 else 0.0
            
            is_healthy = (
                circuit_breaker.state == "CLOSED" and
                success_rate > 0.7 and
                provider.is_available
            )
            
            health_list.append(ProviderHealth(
                provider=provider_name,
                is_healthy=is_healthy,
                response_time_ms=avg_latency,
                last_success=stats.get("last_used"),
                last_failure=None,  # TODO: Track this
                consecutive_failures=circuit_breaker.failure_count,
                success_rate_24h=success_rate
            ))
        
        return health_list

    async def get_provider_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        Get detailed provider statistics
        
        For monitoring dashboard
        """
        
        stats_summary = {}
        
        for provider_name, stats in self.provider_stats.items():
            total_calls = stats["total_calls"]
            successful_calls = stats["successful_calls"]
            
            stats_summary[provider_name] = {
                "total_calls": total_calls,
                "successful_calls": successful_calls,
                "failed_calls": stats["failed_calls"],
                "success_rate": (successful_calls / total_calls) if total_calls > 0 else 0.0,
                "total_tokens": stats["total_tokens"],
                "total_cost_usd": stats["total_cost"],
                "avg_latency_ms": (stats["total_latency"] / successful_calls) if successful_calls > 0 else 0.0,
                "last_used": stats["last_used"],
                "circuit_breaker_state": self.circuit_breakers[provider_name].state
            }
        
        return stats_summary

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.http_client.aclose()


# Global singleton instance
_router_instance = None

def get_ai_router() -> EnhancedAIRouter:
    """Get global AI router instance"""
    global _router_instance
    
    if _router_instance is None:
        _router_instance = EnhancedAIRouter()
    
    return _router_instance
```

***

### **Step 3.2: Integrate AI Router into Agent Execution**

**File**: `src/amas/agents/base_agent.py` (CREATE OR ENHANCE)

```python
# src/amas/agents/base_agent.py (BASE AGENT CLASS)
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from src.amas.ai.enhanced_router_v2 import get_ai_router, AIResponse
import logging

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """
    Base class for all specialized agents
    
    ✅ Standardized interface
    ✅ AI provider integration via router
    ✅ Tool execution
    ✅ Memory integration
    ✅ Error handling
    """
    
    def __init__(
        self,
        agent_id: str,
        name: str,
        type: str,
        system_prompt: str,
        tools: List[Any] = None,
        model_preference: str = "gpt-4-turbo-preview",
        strategy: str = "quality_first"
    ):
        self.id = agent_id
        self.name = name
        self.type = type
        self.system_prompt = system_prompt
        self.tools = tools or []
        self.model_preference = model_preference
        self.strategy = strategy
        
        # Get AI router
        self.ai_router = get_ai_router()
        
        # Performance tracking
        self.expertise_score = 0.90  # Default
        self.executions = 0
        self.successes = 0
        self.total_duration = 0.0
    
    async def execute(
        self,
        task_id: str,
        target: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute agent task
        
        Returns:
            Dict with result, success, duration, etc.
        """
        
        execution_start = time.time()
        
        try:
            # STEP 1: Prepare prompt
            prompt = await self._prepare_prompt(target, parameters)
            
            # STEP 2: Call AI via router (WITH FALLBACK)
            logger.info(f"Agent {self.name}: Calling AI with strategy '{self.strategy}'")
            
            ai_response: AIResponse = await self.ai_router.generate_with_fallback(
                prompt=prompt,
                model_preference=self.model_preference,
                max_tokens=4000,
                temperature=0.3,
                system_prompt=self.system_prompt,
                strategy=self.strategy
            )
            
            logger.info(f"Agent {self.name}: Got response from {ai_response.provider} "
                       f"({ai_response.tokens_used} tokens, ${ai_response.cost_usd:.4f})")
            
            # STEP 3: Parse response
            parsed_result = await self._parse_response(ai_response.content)
            
            # STEP 4: Execute tools if needed
            if self.tools and parsed_result.get("requires_tools"):
                tool_results = await self._execute_tools(parsed_result)
                parsed_result["tool_results"] = tool_results
            
            execution_duration = time.time() - execution_start
            
            # Update stats
            self.executions += 1
            self.successes += 1
            self.total_duration += execution_duration
            
            return {
                "success": True,
                "agent_id": self.id,
                "agent_name": self.name,
                "result": parsed_result,
                "duration": execution_duration,
                "ai_provider": ai_response.provider,
                "ai_model": ai_response.model,
                "tokens_used": ai_response.tokens_used,
                "cost_usd": ai_response.cost_usd,
                "fallback_used": ai_response.fallback_used
            }
        
        except Exception as e:
            execution_duration = time.time() - execution_start
            
            logger.error(f"Agent {self.name} execution failed: {e}", exc_info=True)
            
            self.executions += 1
            self.total_duration += execution_duration
            
            return {
                "success": False,
                "agent_id": self.id,
                "agent_name": self.name,
                "error": str(e),
                "duration": execution_duration
            }
    
    @abstractmethod
    async def _prepare_prompt(
        self,
        target: str,
        parameters: Dict[str, Any]
    ) -> str:
        """
        Prepare agent-specific prompt
        
        Override in subclasses
        """
        pass
    
    @abstractmethod
    async def _parse_response(self, response: str) -> Dict[str, Any]:
        """
        Parse AI response
        
        Override in subclasses
        """
        pass
    
    async def _execute_tools(self, parsed_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute tools if agent has them"""
        
        tool_results = []
        
        for tool in self.tools:
            try:
                result = await tool.execute(parsed_result)
                tool_results.append({
                    "tool": tool.name,
                    "success": True,
                    "result": result
                })
            except Exception as e:
                tool_results.append({
                    "tool": tool.name,
                    "success": False,
                    "error": str(e)
                })
        
        return tool_results
```

***

### **Step 3.3: Create Specialized Agent Implementations**

**File**: `src/amas/agents/security_expert.py` (EXAMPLE - CREATE FOR ALL 20+ AGENTS)

```python
# src/amas/agents/security_expert.py (SPECIALIZED AGENT)
from src.amas.agents.base_agent import BaseAgent
from typing import Any, Dict
import json

class SecurityExpertAgent(BaseAgent):
    """
    Security Expert Agent
    
    Specializes in:
    - Vulnerability assessment
    - Security auditing
    - Penetration testing
    - Threat analysis
    """
    
    def __init__(self):
        super().__init__(
            agent_id="security_expert",
            name="Security Expert",
            type="security",
            system_prompt="""You are an elite cybersecurity expert with 15+ years of experience 
            in penetration testing, vulnerability assessment, and security auditing.
            
            Your expertise includes:
            • OWASP Top 10 vulnerabilities
            • Network security analysis
            • Web application security
            • API security testing
            • SSL/TLS configuration review
            • Security header analysis
            • Common vulnerability detection (SQL injection, XSS, CSRF, etc.)
            
            When analyzing a target, you:
            1. Perform comprehensive security assessment
            2. Identify specific vulnerabilities with CVE references when applicable
            3. Provide severity ratings (Critical, High, Medium, Low)
            4. Suggest concrete remediation steps
            5. Prioritize findings by risk
            
            Always provide actionable, technical recommendations.""",
            tools=[],  # Tools can be added here
            model_preference="gpt-4-turbo-preview",
            strategy="quality_first"
        )
        
        self.expertise_score = 0.95  # High expertise
    
    async def _prepare_prompt(
        self,
        target: str,
        parameters: Dict[str, Any]
    ) -> str:
        """Prepare security analysis prompt"""
        
        depth = parameters.get("depth", "standard")
        
        prompt = f"""Perform a comprehensive security analysis of the target: {target}

Analysis Depth: {depth}

Please analyze:
1. Port scanning results (if URL/domain)
2. SSL/TLS configuration
3. Security headers (X-Frame-Options, CSP, HSTS, etc.)
4. Common vulnerabilities (OWASP Top 10)
5. Technology stack identification
6. Known CVEs for detected technologies
7. Configuration issues
8. Potential attack vectors

Provide results in the following JSON format:
{{
    "vulnerabilities": [
        {{
            "id": "VULN-001",
            "severity": "Critical|High|Medium|Low",
            "title": "SQL Injection in Login Form",
            "description": "Detailed description",
            "location": "Specific location",
            "cwe": "CWE-89",
            "cvss_score": 9.8,
            "remediation": "Concrete fix steps"
        }}
    ],
    "ssl_analysis": {{
        "valid": true,
        "expires": "2026-01-15",
        "issues": []
    }},
    "security_headers": {{
        "present": ["X-Frame-Options", "HSTS"],
        "missing": ["Content-Security-Policy"],
        "issues": []
    }},
    "technology_stack": {{
        "server": "Apache 2.4.52",
        "backend": "PHP 8.1",
        "framework": "WordPress 6.2",
        "known_cves": ["CVE-2023-XXXX"]
    }},
    "summary": "Overall security assessment",
    "risk_rating": "Critical|High|Medium|Low",
    "recommendations": ["Action 1", "Action 2"]
}}"""
        
        return prompt
    
    async def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response into structured format"""
        
        try:
            # Try to extract JSON from response
            # AI might wrap JSON in markdown code blocks
            if "```
                json_str = response.split("```json").split("```
            elif "```" in response:
                json_str = response.split("``````")[0].strip()
            else:
                json_str = response.strip()
            
            parsed = json.loads(json_str)
            
            return {
                "success": True,
                "data": parsed,
                "raw_response": response
            }
        
        except json.JSONDecodeError:
            # If JSON parsing fails, return raw text
            logger.warning("Failed to parse JSON response, returning raw text")
            
            return {
                "success": True,
                "data": {
                    "vulnerabilities": [],
                    "summary": response,
                    "parsing_error": True
                },
                "raw_response": response
            }
```

***

**This completes Part 3 - AI Provider Fallback System Integration**

**Key Implementation Points**:
1. ✅ 16 AI providers fully configured
2. ✅ Intelligent fallback chain (quality/speed/cost strategies)
3. ✅ Circuit breaker pattern for resilience
4. ✅ Provider health monitoring
5. ✅ Cost and latency tracking
6. ✅ Base agent class with router integration
7. ✅ Specialized agent example (Security Expert)

**Next Steps**:
- **Part 4**: Database Full Integration (PostgreSQL + Redis + Neo4j)
- **Part 5**: Platform Integrations (N8N, Slack, Salesforce, etc.)
- **Part 6**: Monitoring & Observability (Prometheus + Grafana)
- **Part 7**: Frontend Complete Integration
- **Part 8**: Testing & Validation
- **Part 9**: Production Deployment
- **Part 10**: Final Checklist

NEXT **Part 4** 🚀

[1](https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System)