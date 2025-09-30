"""
AI Configuration Manager - Handles all AI provider configurations
"""

import os
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class AIProvider(Enum):
    """AI Provider enumeration"""
    DEEPSEEK = "deepseek"
    GLM = "glm"
    GROK = "grok"
    KIMI = "kimi"
    QWEN = "qwen"
    GPTOSS = "gptoss"

@dataclass
class AIProviderConfig:
    """Configuration for AI provider"""
    name: str
    api_key: str
    base_url: str
    model: str
    max_tokens: int = 4000
    temperature: float = 0.7
    timeout: int = 30
    rate_limit: int = 60  # requests per minute
    priority: int = 1  # 1 = highest priority
    enabled: bool = True

class AIConfigManager:
    """AI Configuration Manager"""

    def __init__(self):
        self.providers: Dict[AIProvider, AIProviderConfig] = {}
        self._load_configurations()

    def _load_configurations(self):
        """Load AI provider configurations from environment variables"""
        try:
            # DeepSeek V3.1
            self.providers[AIProvider.DEEPSEEK] = AIProviderConfig(
                name="DeepSeek V3.1",
                api_key=os.getenv('DEEPSEEK_API_KEY', ''),
                base_url="https://openrouter.ai/api/v1",
                model="deepseek/deepseek-chat-v3.1:free",
                max_tokens=4000,
                temperature=0.7,
                timeout=30,
                rate_limit=60,
                priority=1,
                enabled=bool(os.getenv('DEEPSEEK_API_KEY'))
            )

            # GLM 4.5 Air
            self.providers[AIProvider.GLM] = AIProviderConfig(
                name="GLM 4.5 Air",
                api_key=os.getenv('GLM_API_KEY', ''),
                base_url="https://openrouter.ai/api/v1",
                model="z-ai/glm-4.5-air:free",
                max_tokens=4000,
                temperature=0.7,
                timeout=30,
                rate_limit=60,
                priority=2,
                enabled=bool(os.getenv('GLM_API_KEY'))
            )

            # Grok 4 Fast
            self.providers[AIProvider.GROK] = AIProviderConfig(
                name="Grok 4 Fast",
                api_key=os.getenv('GROK_API_KEY', ''),
                base_url="https://openrouter.ai/api/v1",
                model="x-ai/grok-4-fast:free",
                max_tokens=4000,
                temperature=0.7,
                timeout=30,
                rate_limit=60,
                priority=3,
                enabled=bool(os.getenv('GROK_API_KEY'))
            )

            # Kimi K2
            self.providers[AIProvider.KIMI] = AIProviderConfig(
                name="Kimi K2",
                api_key=os.getenv('KIMI_API_KEY', ''),
                base_url="https://openrouter.ai/api/v1",
                model="moonshotai/kimi-k2:free",
                max_tokens=4000,
                temperature=0.7,
                timeout=30,
                rate_limit=60,
                priority=4,
                enabled=bool(os.getenv('KIMI_API_KEY'))
            )

            # Qwen3 Coder
            self.providers[AIProvider.QWEN] = AIProviderConfig(
                name="Qwen3 Coder",
                api_key=os.getenv('QWEN_API_KEY', ''),
                base_url="https://openrouter.ai/api/v1",
                model="qwen/qwen3-coder:free",
                max_tokens=4000,
                temperature=0.7,
                timeout=30,
                rate_limit=60,
                priority=5,
                enabled=bool(os.getenv('QWEN_API_KEY'))
            )

            # GPT OSS 120B
            self.providers[AIProvider.GPTOSS] = AIProviderConfig(
                name="GPT OSS 120B",
                api_key=os.getenv('GPTOSS_API_KEY', ''),
                base_url="https://openrouter.ai/api/v1",
                model="openai/gpt-oss-120b:free",
                max_tokens=4000,
                temperature=0.7,
                timeout=30,
                rate_limit=60,
                priority=6,
                enabled=bool(os.getenv('GPTOSS_API_KEY'))
            )

            enabled_count = sum(1 for p in self.providers.values() if p.enabled)
            logger.info(f"Loaded {enabled_count} AI provider configurations")

        except Exception as e:
            logger.error(f"Error loading AI configurations: {e}")
            raise

    def get_provider_config(self, provider: AIProvider) -> Optional[AIProviderConfig]:
        """Get configuration for a specific provider"""
        return self.providers.get(provider)

    def get_enabled_providers(self) -> Dict[AIProvider, AIProviderConfig]:
        """Get all enabled providers"""
        return {k: v for k, v in self.providers.items() if v.enabled}

    def get_provider_by_priority(self) -> list:
        """Get providers sorted by priority"""
        enabled = self.get_enabled_providers()
        return sorted(enabled.items(), key=lambda x: x[1].priority)

    def validate_configurations(self) -> Dict[str, Any]:
        """Validate all provider configurations"""
        validation_results = {
            'valid_providers': [],
            'invalid_providers': [],
            'total_providers': len(self.providers),
            'enabled_providers': 0
        }

        for provider, config in self.providers.items():
            if config.enabled:
                validation_results['enabled_providers'] += 1

                if config.api_key and config.api_key.strip():
                    validation_results['valid_providers'].append({
                        'provider': provider.value,
                        'name': config.name,
                        'priority': config.priority
                    })
                else:
                    validation_results['invalid_providers'].append({
                        'provider': provider.value,
                        'name': config.name,
                        'issue': 'Missing API key'
                    })
            else:
                validation_results['invalid_providers'].append({
                    'provider': provider.value,
                    'name': config.name,
                    'issue': 'Disabled'
                })

        return validation_results

    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get configuration summary"""
        validation = self.validate_configurations()

        return {
            'total_providers': validation['total_providers'],
            'enabled_providers': validation['enabled_providers'],
            'valid_providers': len(validation['valid_providers']),
            'invalid_providers': len(validation['invalid_providers']),
            'provider_details': validation['valid_providers'],
            'issues': validation['invalid_providers']
        }

    def update_provider_config(self, provider: AIProvider, **kwargs):
        """Update provider configuration"""
        if provider in self.providers:
            config = self.providers[provider]
            for key, value in kwargs.items():
                if hasattr(config, key):
                    setattr(config, key, value)
                    logger.info(f"Updated {provider.value} {key}: {value}")

    def disable_provider(self, provider: AIProvider):
        """Disable a provider"""
        if provider in self.providers:
            self.providers[provider].enabled = False
            logger.info(f"Disabled provider: {provider.value}")

    def enable_provider(self, provider: AIProvider):
        """Enable a provider"""
        if provider in self.providers:
            self.providers[provider].enabled = True
            logger.info(f"Enabled provider: {provider.value}")

    def get_health_check_config(self) -> Dict[str, Any]:
        """Get configuration for health checks"""
        return {
            'providers': {
                provider.value: {
                    'enabled': config.enabled,
                    'api_key_present': bool(config.api_key),
                    'base_url': config.base_url,
                    'model': config.model,
                    'priority': config.priority
                }
                for provider, config in self.providers.items()
            },
            'health_check_timeout': 30,
            'health_check_retries': 3
        }

# Global configuration instance
ai_config = AIConfigManager()

def get_ai_config() -> AIConfigManager:
    """Get the global AI configuration instance"""
    return ai_config

def reload_ai_config():
    """Reload AI configuration from environment"""
    global ai_config
    ai_config = AIConfigManager()
    return ai_config
