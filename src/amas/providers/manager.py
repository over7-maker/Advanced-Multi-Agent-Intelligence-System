#!/usr/bin/env python3
"""
AMAS Provider Manager
Centralized management of AI provider API keys and dynamic discovery
"""

import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class ProviderConfig:
    name: str
    env_key: str
    required: bool = False
    priority: int = 0
    max_retries: int = 3
    timeout: int = 30


class ProviderStatus(Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"
    ERROR = "error"
    QUOTA_EXCEEDED = "quota_exceeded"


class AIProvider(ABC):
    """Abstract base class for AI providers"""

    def __init__(self, api_key: str, config: ProviderConfig):
        self.api_key = api_key
        self.config = config
        self.status = ProviderStatus.ENABLED
        self.error_count = 0
        self.last_error = None

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available"""
        pass

    @abstractmethod
    def infer(self, prompt: str, **kwargs) -> str:
        """Generate inference from prompt"""
        pass

    @abstractmethod
    def get_provider_info(self) -> Dict[str, Any]:
        """Get provider information"""
        pass

    def handle_error(self, error: Exception):
        """Handle provider errors"""
        self.error_count += 1
        self.last_error = str(error)

        if self.error_count >= self.config.max_retries:
            self.status = ProviderStatus.ERROR
        elif "quota" in str(error).lower():
            self.status = ProviderStatus.QUOTA_EXCEEDED


class ProviderManager:
    """Centralized provider management with dynamic discovery"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.providers: Dict[str, AIProvider] = {}
        self.provider_configs = self._get_provider_configs()
        self._discover_providers()

    def _get_provider_configs(self) -> List[ProviderConfig]:
        """Get all provider configurations"""
        return [
            # Core providers (required for minimal setup)
            ProviderConfig("OpenAI", "OPENAI_API_KEY", required=True, priority=1),
            ProviderConfig("GeminiAI", "GEMINIAI_API_KEY", required=True, priority=2),
            ProviderConfig("GroqAI", "GROQAI_API_KEY", required=True, priority=3),
            # Extended providers (optional for redundancy)
            ProviderConfig("Cohere", "COHERE_API_KEY", required=False, priority=4),
            ProviderConfig(
                "Anthropic", "ANTHROPIC_API_KEY", required=False, priority=5
            ),
            ProviderConfig(
                "HuggingFace", "HUGGINGFACE_API_KEY", required=False, priority=6
            ),
            ProviderConfig("NVIDIAAI", "NVIDIAAI_API_KEY", required=False, priority=7),
            ProviderConfig(
                "Replicate", "REPLICATE_API_KEY", required=False, priority=8
            ),
            ProviderConfig(
                "TogetherAI", "TOGETHERAI_API_KEY", required=False, priority=9
            ),
            ProviderConfig(
                "Perplexity", "PERPLEXITY_API_KEY", required=False, priority=10
            ),
            ProviderConfig("DeepSeek", "DEEPSEEK_API_KEY", required=False, priority=11),
            ProviderConfig(
                "MistralAI", "MISTRALAI_API_KEY", required=False, priority=12
            ),
            ProviderConfig("Ollama", "OLLAMA_API_KEY", required=False, priority=13),
            ProviderConfig("LocalAI", "LOCALAI_API_KEY", required=False, priority=14),
            ProviderConfig("Custom", "CUSTOM_API_KEY", required=False, priority=15),
        ]

    def _discover_providers(self):
        """Discover and initialize available providers"""
        self.logger.info("🔍 Discovering AI providers...")

        enabled_count = 0
        required_missing = []

        for config in self.provider_configs:
            api_key = os.getenv(config.env_key)

            if api_key:
                try:
                    # Create provider instance (simplified for now)
                    provider = self._create_provider(config, api_key)
                    if provider and provider.is_available():
                        self.providers[config.name] = provider
                        enabled_count += 1
                        self.logger.info(f"✅ {config.name} (enabled)")
                    else:
                        self.logger.warning(
                            f"⚠️ {config.name} (API key present but unavailable)"
                        )
                except Exception as e:
                    self.logger.error(f"❌ {config.name} (error: {e})")
            else:
                if config.required:
                    required_missing.append(config.name)
                self.logger.info(f"✖️ {config.name} (missing API key)")

        # Check if we have minimum required providers
        if required_missing:
            self.logger.warning(
                f"⚠️ Missing required providers: {', '.join(required_missing)}"
            )

        if enabled_count == 0:
            raise RuntimeError(
                "No AI provider API keys found. Please add at least one key to .env or secrets.\n"
                "Required: OPENAI_API_KEY, GEMINIAI_API_KEY, or GROQAI_API_KEY"
            )

        self.logger.info(
            f"🎯 {enabled_count} providers enabled out of {len(self.provider_configs)} configured"
        )

    def _create_provider(
        self, config: ProviderConfig, api_key: str
    ) -> Optional[AIProvider]:
        """Create provider instance (simplified implementation)"""
        # This would be expanded with actual provider implementations
        return MockProvider(api_key, config)

    def get_available_providers(self) -> List[str]:
        """Get list of available provider names"""
        return [
            name
            for name, provider in self.providers.items()
            if provider.status == ProviderStatus.ENABLED
        ]

    def get_provider(self, name: str) -> Optional[AIProvider]:
        """Get specific provider by name"""
        return self.providers.get(name)

    def get_best_provider(self) -> Optional[AIProvider]:
        """Get the best available provider based on priority and status"""
        available = [
            (provider, config.priority)
            for name, provider in self.providers.items()
            for config in self.provider_configs
            if config.name == name and provider.status == ProviderStatus.ENABLED
        ]

        if not available:
            return None

        # Sort by priority (lower number = higher priority)
        available.sort(key=lambda x: x[1])
        return available[0][0]

    def get_provider_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all providers"""
        status = {}

        for config in self.provider_configs:
            if config.name in self.providers:
                provider = self.providers[config.name]
                status[config.name] = {
                    "status": provider.status.value,
                    "available": provider.is_available(),
                    "error_count": provider.error_count,
                    "last_error": provider.last_error,
                    "priority": config.priority,
                }
            else:
                status[config.name] = {
                    "status": "missing_key",
                    "available": False,
                    "error_count": 0,
                    "last_error": None,
                    "priority": config.priority,
                }

        return status

    def validate_environment(self) -> Dict[str, Any]:
        """Validate current environment configuration"""
        validation_result = {
            "valid": True,
            "enabled_providers": len(self.get_available_providers()),
            "total_configured": len(self.provider_configs),
            "missing_required": [],
            "warnings": [],
            "recommendations": [],
        }

        # Check required providers
        for config in self.provider_configs:
            if config.required and config.name not in self.providers:
                validation_result["missing_required"].append(config.name)
                validation_result["valid"] = False

        # Check if we have minimum providers
        if validation_result["enabled_providers"] < 2:
            validation_result["warnings"].append(
                "Only 1 provider enabled - consider adding more for redundancy"
            )

        if validation_result["enabled_providers"] >= 5:
            validation_result["recommendations"].append(
                "Excellent redundancy! You have 5+ providers enabled"
            )

        return validation_result


class MockProvider(AIProvider):
    """Mock provider for testing and development"""

    def is_available(self) -> bool:
        return True

    def infer(self, prompt: str, **kwargs) -> str:
        return f"Mock response to: {prompt[:50]}..."

    def get_provider_info(self) -> Dict[str, Any]:
        return {
            "name": self.config.name,
            "type": "mock",
            "status": self.status.value,
            "priority": self.config.priority,
        }


# Global provider manager instance
provider_manager = ProviderManager()


def get_provider_manager() -> ProviderManager:
    """Get the global provider manager instance"""
    return provider_manager


def validate_environment() -> Dict[str, Any]:
    """Validate the current environment configuration"""
    return provider_manager.validate_environment()


# CLI interface for environment validation
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AMAS Provider Manager")
    parser.add_argument("--validate", action="store_true", help="Validate environment")
    parser.add_argument("--status", action="store_true", help="Show provider status")

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    if args.validate:
        result = validate_environment()
        print("\n🔍 Environment Validation Results:")
        print(f"Valid: {result['valid']}")
        print(f"Enabled Providers: {result['enabled_providers']}")
        print(f"Missing Required: {result['missing_required']}")
        if result["warnings"]:
            print(f"Warnings: {result['warnings']}")
        if result["recommendations"]:
            print(f"Recommendations: {result['recommendations']}")

    if args.status:
        status = provider_manager.get_provider_status()
        print("\n📊 Provider Status:")
        for name, info in status.items():
            status_icon = "✅" if info["available"] else "❌"
            print(
                f"{status_icon} {name}: {info['status']} (Priority: {info['priority']})"
            )
