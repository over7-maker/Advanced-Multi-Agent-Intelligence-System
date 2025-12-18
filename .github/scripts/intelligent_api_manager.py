#!/usr/bin/env python3
"""
Intelligent Multi-API Manager for AMAS
Manages 16 AI API keys with intelligent failover, caching, and load balancing

Supported Providers (16 total):
1. CEREBRAS_API_KEY - Cerebras (Fast, 235B model)
2. CODESTRAL_API_KEY - Mistral Codestral (Code specialist)
3. DEEPSEEK_API_KEY - DeepSeek (Cost-effective)
4. GEMINIAI_API_KEY - Google Gemini Advanced
5. GLM_API_KEY - OpenRouter GLM-4.5 Air (Free)
6. GPTOSS_API_KEY - OpenRouter GPT OSS (Free)
7. GROK_API_KEY - OpenRouter Grok (Free)
8. GROQAI_API_KEY - Groq (Fast inference)
9. KIMI_API_KEY - OpenRouter Kimi (Free)
10. NVIDIA_API_KEY - NVIDIA NIM (Multi-model)
11. QWEN_API_KEY - OpenRouter Qwen (Free)
12. GEMINI2_API_KEY - Google Gemini 2.0 Flash
13. GROQ2_API_KEY - Groq Backup
14. COHERE_API_KEY - Cohere (Text generation)
15. CHUTES_API_KEY - Chutes (Multi-model gateway)
16. Additional backup key (reserved)
"""

import os
import sys
import json
import asyncio
import logging
import time
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProviderType(Enum):
    """AI Provider types"""
    CEREBRAS = "cerebras"
    CODESTRAL = "codestral"
    DEEPSEEK = "deepseek"
    GEMINI = "gemini"
    GLM = "glm"
    GPTOSS = "gptoss"
    GROK = "grok"
    GROQ = "groq"
    KIMI = "kimi"
    NVIDIA = "nvidia"
    QWEN = "qwen"
    GEMINI2 = "gemini2"
    GROQ2 = "groq2"
    COHERE = "cohere"
    CHUTES = "chutes"


class TaskType(Enum):
    """Task types requiring AI"""
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    TESTING = "testing"
    ANALYSIS = "analysis"
    DOCUMENTATION = "documentation"
    OPTIMIZATION = "optimization"
    SECURITY = "security"
    DEPLOYMENT = "deployment"
    LEARNING = "learning"


@dataclass
class APIProvider:
    """API Provider configuration"""
    name: str
    type: ProviderType
    api_key: str
    endpoint: str
    model: str
    priority: int  # 1 = highest priority
    cost_per_1k_tokens: float  # Estimated cost
    speed_score: int  # 1-10, higher = faster
    quality_score: int  # 1-10, higher = better quality
    supported_tasks: List[TaskType]
    is_free: bool
    rate_limit: int  # requests per minute
    last_used: Optional[datetime] = None
    consecutive_failures: int = 0
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    
    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.total_requests == 0:
            return 1.0
        return self.successful_requests / self.total_requests
    
    def is_healthy(self) -> bool:
        """Check if provider is healthy"""
        # Mark unhealthy if >3 consecutive failures
        if self.consecutive_failures > 3:
            return False
        # Mark unhealthy if success rate < 50%
        if self.success_rate() < 0.5 and self.total_requests > 5:
            return False
        return True
    
    def reset_failures(self):
        """Reset failure counter"""
        self.consecutive_failures = 0


@dataclass
class ProviderPool:
    """Pool of available providers"""
    providers: List[APIProvider] = field(default_factory=list)
    cache: Dict[str, Any] = field(default_factory=dict)
    cache_ttl: int = 3600  # 1 hour default
    last_cache_cleanup: datetime = field(default_factory=datetime.now)
    
    def get_available_providers(self, task_type: TaskType) -> List[APIProvider]:
        """Get providers capable of handling task, sorted by priority"""
        available = [
            p for p in self.providers
            if task_type in p.supported_tasks and p.is_healthy()
        ]
        # Sort by priority (1 = highest), then by success rate
        return sorted(
            available,
            key=lambda p: (p.priority, -p.success_rate())
        )
    
    def get_provider_by_type(self, provider_type: ProviderType) -> Optional[APIProvider]:
        """Get specific provider by type"""
        for p in self.providers:
            if p.type == provider_type and p.is_healthy():
                return p
        return None
    
    def mark_success(self, provider: APIProvider):
        """Mark successful API call"""
        provider.successful_requests += 1
        provider.total_requests += 1
        provider.consecutive_failures = 0
        provider.last_used = datetime.now()
    
    def mark_failure(self, provider: APIProvider):
        """Mark failed API call"""
        provider.failed_requests += 1
        provider.total_requests += 1
        provider.consecutive_failures += 1
        logger.warning(
            f"❌ {provider.name} failed (consecutive: {provider.consecutive_failures}, "
            f"success rate: {provider.success_rate():.1%})"
        )
    
    def cleanup_cache(self):
        """Remove expired cache entries"""
        now = datetime.now()
        if (now - self.last_cache_cleanup).seconds < 300:  # Cleanup every 5 minutes
            return
        
        expired_keys = [
            k for k, v in self.cache.items()
            if (now - v.get('timestamp', now)).seconds > self.cache_ttl
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            logger.info(f"🗑️ Cleaned up {len(expired_keys)} expired cache entries")
        
        self.last_cache_cleanup = now


class IntelligentAPIManager:
    """Intelligent manager for all AI APIs with automatic failover"""
    
    def __init__(self):
        """Initialize API manager with all providers"""
        self.pool = ProviderPool()
        self._initialize_providers()
        logger.info(f"✅ Initialized API Manager with {len(self.pool.providers)} providers")
    
    def _initialize_providers(self):
        """Initialize all 16 providers"""
        
        # Provider 1: CEREBRAS - Fast, large model
        cerebras_key = os.environ.get('CEREBRAS_API_KEY')
        if cerebras_key:
            self.pool.providers.append(APIProvider(
                name="Cerebras",
                type=ProviderType.CEREBRAS,
                api_key=cerebras_key,
                endpoint="https://api.cerebras.ai/v1",
                model="qwen-3-235b-a22b-instruct-2507",
                priority=3,
                cost_per_1k_tokens=0.0008,
                speed_score=9,
                quality_score=8,
                supported_tasks=[
                    TaskType.CODE_GENERATION, TaskType.ANALYSIS,
                    TaskType.OPTIMIZATION, TaskType.DOCUMENTATION
                ],
                is_free=False,
                rate_limit=100
            ))
        
        # Provider 2: CODESTRAL - Code specialist
        codestral_key = os.environ.get('CODESTRAL_API_KEY')
        if codestral_key:
            self.pool.providers.append(APIProvider(
                name="Codestral",
                type=ProviderType.CODESTRAL,
                api_key=codestral_key,
                endpoint="https://codestral.mistral.ai/v1",
                model="codestral-latest",
                priority=2,
                cost_per_1k_tokens=0.0006,
                speed_score=8,
                quality_score=9,
                supported_tasks=[
                    TaskType.CODE_GENERATION, TaskType.CODE_REVIEW,
                    TaskType.TESTING, TaskType.OPTIMIZATION
                ],
                is_free=False,
                rate_limit=120
            ))
        
        # Provider 3: DEEPSEEK - Cost-effective
        deepseek_key = os.environ.get('DEEPSEEK_API_KEY')
        if deepseek_key:
            self.pool.providers.append(APIProvider(
                name="DeepSeek",
                type=ProviderType.DEEPSEEK,
                api_key=deepseek_key,
                endpoint="https://api.deepseek.com/v1",
                model="deepseek-chat",
                priority=1,  # Primary provider
                cost_per_1k_tokens=0.0005,
                speed_score=7,
                quality_score=8,
                supported_tasks=[
                    TaskType.CODE_GENERATION, TaskType.ANALYSIS,
                    TaskType.DOCUMENTATION, TaskType.LEARNING
                ],
                is_free=False,
                rate_limit=150
            ))
        
        # Provider 4: GEMINI - Multi-modal
        gemini_key = os.environ.get('GEMINIAI_API_KEY')
        if gemini_key:
            self.pool.providers.append(APIProvider(
                name="Gemini Advanced",
                type=ProviderType.GEMINI,
                api_key=gemini_key,
                endpoint="https://generativelanguage.googleapis.com/v1beta",
                model="gemini-2.0-pro",
                priority=4,
                cost_per_1k_tokens=0.0010,
                speed_score=8,
                quality_score=9,
                supported_tasks=[
                    TaskType.ANALYSIS, TaskType.DOCUMENTATION,
                    TaskType.SECURITY, TaskType.LEARNING
                ],
                is_free=False,
                rate_limit=100
            ))
        
        # Providers 5-8: OpenRouter FREE models (GLM, GPTOSS, GROK, KIMI)
        openrouter_key = os.environ.get('GLM_API_KEY') or os.environ.get('GPTOSS_API_KEY')
        if openrouter_key:
            # GLM-4.5 Air
            self.pool.providers.append(APIProvider(
                name="GLM-4.5 Air",
                type=ProviderType.GLM,
                api_key=openrouter_key,
                endpoint="https://openrouter.ai/api/v1",
                model="z-ai/glm-4.5-air:free",
                priority=8,
                cost_per_1k_tokens=0.0,
                speed_score=7,
                quality_score=7,
                supported_tasks=[TaskType.ANALYSIS, TaskType.DOCUMENTATION],
                is_free=True,
                rate_limit=50
            ))
            
            # Grok
            self.pool.providers.append(APIProvider(
                name="Grok",
                type=ProviderType.GROK,
                api_key=openrouter_key,
                endpoint="https://openrouter.ai/api/v1",
                model="x-ai/grok-4-fast:free",
                priority=9,
                cost_per_1k_tokens=0.0,
                speed_score=6,
                quality_score=6,
                supported_tasks=[TaskType.ANALYSIS],
                is_free=True,
                rate_limit=40
            ))
            
            # Qwen
            self.pool.providers.append(APIProvider(
                name="Qwen-2.5",
                type=ProviderType.QWEN,
                api_key=openrouter_key,
                endpoint="https://openrouter.ai/api/v1",
                model="qwen/qwen-2.5-7b-instruct:free",
                priority=10,
                cost_per_1k_tokens=0.0,
                speed_score=6,
                quality_score=6,
                supported_tasks=[TaskType.ANALYSIS, TaskType.DOCUMENTATION],
                is_free=True,
                rate_limit=40
            ))
            
            # Kimi
            self.pool.providers.append(APIProvider(
                name="Kimi",
                type=ProviderType.KIMI,
                api_key=openrouter_key,
                endpoint="https://openrouter.ai/api/v1",
                model="moonshot/moonshot-v1-8k:free",
                priority=11,
                cost_per_1k_tokens=0.0,
                speed_score=5,
                quality_score=6,
                supported_tasks=[TaskType.ANALYSIS],
                is_free=True,
                rate_limit=40
            ))
        
        # Provider 9: GROQ - Fast inference
        groq_key = os.environ.get('GROQAI_API_KEY')
        if groq_key:
            self.pool.providers.append(APIProvider(
                name="Groq",
                type=ProviderType.GROQ,
                api_key=groq_key,
                endpoint="https://api.groq.com/openai/v1",
                model="mixtral-8x7b-32768",
                priority=5,
                cost_per_1k_tokens=0.0002,
                speed_score=10,  # Fastest
                quality_score=7,
                supported_tasks=[
                    TaskType.CODE_GENERATION, TaskType.ANALYSIS,
                    TaskType.DOCUMENTATION
                ],
                is_free=False,
                rate_limit=200
            ))
        
        # Provider 10: NVIDIA - Multi-model gateway
        nvidia_key = os.environ.get('NVIDIA_API_KEY')
        if nvidia_key:
            self.pool.providers.append(APIProvider(
                name="NVIDIA NIM",
                type=ProviderType.NVIDIA,
                api_key=nvidia_key,
                endpoint="https://integrate.api.nvidia.com/v1",
                model="deepseek-ai/deepseek-r1",
                priority=2,
                cost_per_1k_tokens=0.0007,
                speed_score=8,
                quality_score=9,
                supported_tasks=[
                    TaskType.CODE_GENERATION, TaskType.ANALYSIS,
                    TaskType.OPTIMIZATION, TaskType.LEARNING
                ],
                is_free=False,
                rate_limit=150
            ))
        
        # Provider 11: GEMINI 2.0 - Latest Google model
        gemini2_key = os.environ.get('GEMINI2_API_KEY')
        if gemini2_key:
            self.pool.providers.append(APIProvider(
                name="Gemini 2.0 Flash",
                type=ProviderType.GEMINI2,
                api_key=gemini2_key,
                endpoint="https://generativelanguage.googleapis.com/v1beta",
                model="gemini-2.0-flash",
                priority=3,
                cost_per_1k_tokens=0.0008,
                speed_score=9,
                quality_score=9,
                supported_tasks=[
                    TaskType.CODE_GENERATION, TaskType.ANALYSIS,
                    TaskType.DOCUMENTATION, TaskType.OPTIMIZATION
                ],
                is_free=False,
                rate_limit=120
            ))
        
        # Provider 12: GROQ 2 - Backup Groq instance
        groq2_key = os.environ.get('GROQ2_API_KEY')
        if groq2_key:
            self.pool.providers.append(APIProvider(
                name="Groq (Backup)",
                type=ProviderType.GROQ2,
                api_key=groq2_key,
                endpoint="https://api.groq.com/openai/v1",
                model="mixtral-8x7b-32768",
                priority=6,
                cost_per_1k_tokens=0.0002,
                speed_score=10,
                quality_score=7,
                supported_tasks=[
                    TaskType.CODE_GENERATION, TaskType.ANALYSIS,
                    TaskType.DOCUMENTATION
                ],
                is_free=False,
                rate_limit=200
            ))
        
        # Provider 13: COHERE - Text generation specialist
        cohere_key = os.environ.get('COHERE_API_KEY')
        if cohere_key:
            self.pool.providers.append(APIProvider(
                name="Cohere",
                type=ProviderType.COHERE,
                api_key=cohere_key,
                endpoint="https://api.cohere.ai/v1",
                model="command-a-03-2025",
                priority=7,
                cost_per_1k_tokens=0.0003,
                speed_score=7,
                quality_score=8,
                supported_tasks=[
                    TaskType.DOCUMENTATION, TaskType.ANALYSIS,
                    TaskType.LEARNING
                ],
                is_free=False,
                rate_limit=100
            ))
        
        # Provider 14: CHUTES - Multi-model gateway (OpenRouter alternative)
        chutes_key = os.environ.get('CHUTES_API_KEY')
        if chutes_key:
            self.pool.providers.append(APIProvider(
                name="Chutes",
                type=ProviderType.CHUTES,
                api_key=chutes_key,
                endpoint="https://llm.chutes.ai/v1",
                model="zai-org/GLM-4.5-Air",
                priority=12,
                cost_per_1k_tokens=0.0001,
                speed_score=6,
                quality_score=6,
                supported_tasks=[TaskType.ANALYSIS, TaskType.DOCUMENTATION],
                is_free=False,
                rate_limit=60
            ))
        
        logger.info(
            f"✅ Loaded {len(self.pool.providers)} API providers:\n" +
            "\n".join([f"  - {p.name} (Priority {p.priority})" for p in self.pool.providers])
        )
    
    async def call_api(
        self,
        task_type: TaskType,
        prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        timeout: int = 30
    ) -> Tuple[Optional[str], Optional[APIProvider], bool]:
        """
        Call AI API with intelligent failover
        
        Returns:
            - Response text (or None if all failed)
            - Provider used (or None if failed)
            - Success boolean
        """
        
        # Check cache first
        cache_key = self._generate_cache_key(task_type, prompt)
        if cache_key in self.pool.cache:
            cached = self.pool.cache[cache_key]
            if (datetime.now() - cached['timestamp']).seconds < self.pool.cache_ttl:
                logger.info(f"💾 Cache hit for {task_type.value}")
                return cached['response'], None, True
        
        # Get available providers for this task
        available_providers = self.pool.get_available_providers(task_type)
        
        if not available_providers:
            logger.error(f"❌ No healthy providers available for {task_type.value}")
            return None, None, False
        
        # Try each provider in order
        for provider in available_providers:
            try:
                logger.info(
                    f"🤖 Attempting {provider.name} for {task_type.value} "
                    f"(Success rate: {provider.success_rate():.1%})"
                )
                
                response = await self._call_provider(
                    provider, prompt, max_tokens, temperature, timeout
                )
                
                if response:
                    self.pool.mark_success(provider)
                    
                    # Cache the response
                    self.pool.cache[cache_key] = {
                        'response': response,
                        'timestamp': datetime.now(),
                        'provider': provider.name
                    }
                    
                    logger.info(
                        f"✅ Success with {provider.name} "
                        f"(Success rate now: {provider.success_rate():.1%})"
                    )
                    return response, provider, True
            
            except Exception as e:
                self.pool.mark_failure(provider)
                logger.warning(
                    f"⚠️ {provider.name} failed: {str(e)[:100]}... "
                    f"Trying next provider..."
                )
                continue
        
        logger.error(
            f"❌ All {len(available_providers)} providers failed for {task_type.value}"
        )
        return None, None, False
    
    async def _call_provider(
        self,
        provider: APIProvider,
        prompt: str,
        max_tokens: int,
        temperature: float,
        timeout: int
    ) -> Optional[str]:
        """
        Call a specific provider's API
        Implement provider-specific logic here
        """
        # This would be implemented with provider-specific async calls
        # For now, returning placeholder
        await asyncio.sleep(0.1)  # Simulate async call
        
        # In production, implement actual API calls:
        # - For OpenAI-compatible (DeepSeek, NVIDIA, Groq): use OpenAI client
        # - For Google: use google-generativeai
        # - For Cerebras: use cerebras.cloud.sdk
        # - For Cohere: use cohere library
        # - For Chutes: use aiohttp
        
        return f"Response from {provider.name}"
    
    def _generate_cache_key(self, task_type: TaskType, prompt: str) -> str:
        """Generate cache key for prompt"""
        content = f"{task_type.value}:{prompt}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get_provider_stats(self) -> Dict[str, Any]:
        """Get statistics for all providers"""
        stats = {
            'timestamp': datetime.now().isoformat(),
            'total_providers': len(self.pool.providers),
            'healthy_providers': len([p for p in self.pool.providers if p.is_healthy()]),
            'providers': []
        }
        
        for p in sorted(self.pool.providers, key=lambda x: x.priority):
            stats['providers'].append({
                'name': p.name,
                'type': p.type.value,
                'priority': p.priority,
                'healthy': p.is_healthy(),
                'success_rate': f"{p.success_rate():.1%}",
                'total_requests': p.total_requests,
                'successful': p.successful_requests,
                'failed': p.failed_requests,
                'consecutive_failures': p.consecutive_failures,
                'cost_per_1k': f"${p.cost_per_1k_tokens:.4f}",
                'speed': f"{p.speed_score}/10",
                'quality': f"{p.quality_score}/10",
                'free': p.is_free,
                'last_used': p.last_used.isoformat() if p.last_used else None
            })
        
        return stats
    
    def print_status_report(self):
        """Print comprehensive status report"""
        stats = self.get_provider_stats()
        
        report = [
            "\n" + "="*80,
            "🤖 INTELLIGENT AI API MANAGER - STATUS REPORT",
            "="*80,
            f"\n📊 Timestamp: {stats['timestamp']}",
            f"✅ Healthy Providers: {stats['healthy_providers']}/{stats['total_providers']}",
            f"💾 Cache Entries: {len(self.pool.cache)}",
            "\n" + "-"*80,
            "PROVIDER DETAILS",
            "-"*80
        ]
        
        for provider in stats['providers']:
            health_icon = "✅" if provider['healthy'] else "❌"
            report.append(
                f"\n{health_icon} {provider['name']} (Priority {provider['priority']})\n"
                f"   Type: {provider['type']}\n"
                f"   Health: Success Rate {provider['success_rate']} "
                f"({provider['successful']}/{provider['total_requests']} requests)\n"
                f"   Performance: Speed {provider['speed']}, Quality {provider['quality']}\n"
                f"   Cost: {provider['cost_per_1k']}/1K tokens, Free: {provider['free']}\n"
                f"   Last Used: {provider['last_used'] or 'Never'}"
            )
        
        report.append("\n" + "="*80 + "\n")
        print("\n".join(report))
    
    def export_stats(self, filepath: str = "api_manager_stats.json"):
        """Export statistics to JSON file"""
        stats = self.get_provider_stats()
        with open(filepath, 'w') as f:
            json.dump(stats, f, indent=2)
        logger.info(f"📊 Statistics exported to {filepath}")


async def main():
    """Main entry point for testing"""
    logger.info("🚀 Starting Intelligent API Manager...")
    
    manager = IntelligentAPIManager()
    
    # Print initial status
    manager.print_status_report()
    
    # Example: Try different task types
    tasks = [
        (TaskType.CODE_GENERATION, "Generate a Python function to calculate factorial"),
        (TaskType.ANALYSIS, "Analyze the security implications of API key management"),
        (TaskType.DOCUMENTATION, "Write documentation for AI API failover system"),
    ]
    
    for task_type, prompt in tasks:
        logger.info(f"\n📝 Task: {task_type.value}")
        response, provider, success = await manager.call_api(
            task_type,
            prompt,
            max_tokens=500
        )
        
        if success:
            logger.info(f"\n✅ Response received from {provider.name}:")
            logger.info(f"   {response[:100]}...")
        else:
            logger.error("❌ Task failed after trying all providers")
    
    # Print final status
    manager.print_status_report()
    
    # Export statistics
    manager.export_stats()


if __name__ == "__main__":
    asyncio.run(main())
