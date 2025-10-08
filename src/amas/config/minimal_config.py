"""
Minimal Configuration System for AMAS
Supports graceful degradation with 3-4 essential API keys
"""

import logging
import os
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

class ConfigLevel(Enum):
    """Configuration levels based on available API keys"""

    MINIMAL = "minimal"  # 1-2 API keys
    BASIC = "basic"  # 3-4 API keys
    STANDARD = "standard"  # 5-8 API keys
    FULL = "full"  # 9+ API keys


@dataclass
class ProviderConfig:
    """Configuration for an AI provider"""

    name: str
    api_key: str
    base_url: str
    model: str
    priority: int
    required: bool = False
    fallback_available: bool = True

@dataclass
class MinimalConfig:
    """Minimal configuration with graceful degradation"""

    # Core configuration
    config_level: ConfigLevel
    available_providers: List[ProviderConfig]
    required_providers: List[str]
    optional_providers: List[str]

    # Service URLs (with defaults)
    llm_service_url: str = "http://localhost:11434"
    vector_service_url: str = "http://localhost:8001"
    graph_service_url: str = "bolt://localhost:7687"

    # Database configuration
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "amas"
    postgres_password: str = "amas123"
    postgres_db: str = "amas"

    # Redis configuration
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    # Security configuration
    jwt_secret: str = "your-secret-key-change-this"
    encryption_key: str = "your-encryption-key-change-this"

    # Feature flags based on configuration level
    features: Dict[str, bool] = None

    def __post_init__(self):
        if self.features is None:
            self.features = self._determine_features()

    def _determine_features(self) -> Dict[str, bool]:
        """Determine available features based on configuration level"""
        features = {
            "osint_collection": True,
            "forensics_analysis": True,
            "real_web_scraping": self.config_level
            in [ConfigLevel.BASIC, ConfigLevel.STANDARD, ConfigLevel.FULL],
            "advanced_ai_models": self.config_level
            in [ConfigLevel.STANDARD, ConfigLevel.FULL],
            "multi_provider_fallback": self.config_level
            in [ConfigLevel.BASIC, ConfigLevel.STANDARD, ConfigLevel.FULL],
            "circuit_breaker": self.config_level
            in [ConfigLevel.STANDARD, ConfigLevel.FULL],
            "rate_limiting": self.config_level
            in [ConfigLevel.STANDARD, ConfigLevel.FULL],
            "advanced_analytics": self.config_level == ConfigLevel.FULL,
            "real_time_monitoring": self.config_level == ConfigLevel.FULL,
        }
        return features

class MinimalConfigManager:
    """Manages minimal configuration with graceful degradation"""

    def __init__(self):
        self.config: Optional[MinimalConfig] = None
        self._initialize_config()

    def _initialize_config(self):
        """Initialize configuration based on available API keys"""
        logger.info("🔧 Initializing minimal configuration...")

        # Check for API keys
        available_providers = self._detect_available_providers()
        config_level = self._determine_config_level(available_providers)

        # Define required and optional providers
        required_providers = ["deepseek"]  # Only one required for minimal setup
        optional_providers = ["glm", "grok", "nvidia", "codestral"]

        self.config = MinimalConfig(
            config_level=config_level,
            available_providers=available_providers,
            required_providers=required_providers,
            optional_providers=optional_providers,
        )

        logger.info(f"✅ Configuration initialized: {config_level.value} level")
        logger.info(f"📊 Available providers: {len(available_providers)}")

    def _detect_available_providers(self) -> List[ProviderConfig]:
        """Detect available AI providers based on environment variables"""
        providers = []

        # Essential providers (minimal setup)
        if os.getenv("DEEPSEEK_API_KEY"):
            providers.append(
                ProviderConfig(
                    name="DeepSeek",
                    api_key=os.getenv("DEEPSEEK_API_KEY"),
                    base_url="https://api.deepseek.com/v1",
                    model="deepseek-chat",
                    priority=1,
                    required=True,
                )
            )

        # Optional providers for enhanced functionality
        if os.getenv("GLM_API_KEY"):
            providers.append(
                ProviderConfig(
                    name="GLM",
                    api_key=os.getenv("GLM_API_KEY"),
                    base_url="https://open.bigmodel.cn/api/paas/v4",
                    model="glm-4-flash",
                    priority=2,
                    required=False,
                )
            )

        if os.getenv("GROK_API_KEY"):
            providers.append(
                ProviderConfig(
                    name="Grok",
                    api_key=os.getenv("GROK_API_KEY"),
                    base_url="https://api.openrouter.ai/v1",
                    model="x-ai/grok-beta",
                    priority=3,
                    required=False,
                )
            )

        if os.getenv("NVIDIA_API_KEY"):
            providers.append(
                ProviderConfig(
                    name="NVIDIA",
                    api_key=os.getenv("NVIDIA_API_KEY"),
                    base_url="https://integrate.api.nvidia.com/v1",
                    model="deepseek-ai/deepseek-r1",
                    priority=4,
                    required=False,
                )
            )

        if os.getenv("CODESTRAL_API_KEY"):
            providers.append(
                ProviderConfig(
                    name="Codestral",
                    api_key=os.getenv("CODESTRAL_API_KEY"),
                    base_url="https://codestral.mistral.ai/v1",
                    model="codestral-latest",
                    priority=5,
                    required=False,
                )
            )

        return providers

    def _determine_config_level(self, providers: List[ProviderConfig]) -> ConfigLevel:
        """Determine configuration level based on available providers"""
        provider_count = len(providers)

        if provider_count >= 9:
            return ConfigLevel.FULL
        elif provider_count >= 5:
            return ConfigLevel.STANDARD
        elif provider_count >= 3:
            return ConfigLevel.BASIC
        else:
            return ConfigLevel.MINIMAL

    def get_config(self) -> MinimalConfig:
        """Get current configuration"""
        if self.config is None:
            self._initialize_config()
        return self.config

    def validate_config(self) -> Dict[str, Any]:
        """Validate current configuration"""
        config = self.get_config()

        validation_result = {
            "valid": True,
            "level": config.config_level.value,
            "providers_available": len(config.available_providers),
            "required_providers_met": True,
            "warnings": [],
            "errors": [],
        }

        # Check required providers
        for provider in minimal_config.required_providers:
            config = ai_config.get_provider_config(provider)
            if config and config.enabled and config.api_key:
                validation_result["available_providers"].append(provider.value)
            else:
                validation_result["missing_required"].append(provider.value)
                validation_result["valid"] = False

        # Check optional providers
        for provider in minimal_config.optional_providers:
            config = ai_config.get_provider_config(provider)
            if config and config.enabled and config.api_key:
                validation_result["available_providers"].append(provider.value)
            else:
                validation_result["missing_optional"].append(provider.value)

        # Add warnings and recommendations
        if not validation_result["valid"]:
            validation_result["warnings"].append(
                f"Missing required providers: {', '.join(validation_result['missing_required'])}"
            )
            validation_result["recommendations"].append(
                f"Set environment variables for: {', '.join(validation_result['missing_required'])}"
            )

        if validation_result["missing_optional"]:
            validation_result["warnings"].append(
                f"Optional providers not configured: {', '.join(validation_result['missing_optional'])}"
            )
            validation_result["recommendations"].append(
                "Consider adding optional providers for better redundancy"
            )

        # Check if required providers are available
        required_available = all(
            any(p.name.lower() == req.lower() for p in config.available_providers)
            for req in config.required_providers
        )

        if not required_available:
            validation_result["valid"] = False
            validation_result["required_providers_met"] = False
            validation_result["errors"].append("Required providers not available")

        # Check for warnings
        if config.config_level == ConfigLevel.MINIMAL:
            validation_result["warnings"].append(
                "Minimal configuration - limited functionality available"
            )

        return validation_result

        # Disable all providers first
        for provider in AIProvider:
            ai_config.disable_provider(provider)

        # Enable only available required and optional providers
        for provider in minimal_config.required_providers + minimal_config.optional_providers:
            config = ai_config.get_provider_config(provider)
            if config and config.api_key:
                ai_config.enable_provider(provider)

        return ai_config

    def get_environment_setup_guide(self, mode: MinimalMode = MinimalMode.BASIC) -> str:
        """Get environment setup guide for minimal mode"""
        minimal_config = self.get_minimal_config(mode)

        if len(config.available_providers) < 3:
            validation_result["warnings"].append(
                "Consider adding more API keys for better reliability"
            )

        return validation_result

    def get_setup_instructions(self) -> str:
        """Get setup instructions based on current configuration"""
        config = self.get_config()
        instructions = [
            "=" * 60,
            "🔧 AMAS MINIMAL CONFIGURATION SETUP",
            "=" * 60,
            "",
            f"Current Level: {config.config_level.value.upper()}",
            f"Available Providers: {len(config.available_providers)}",
            "",
            "MINIMAL SETUP (1-2 API keys):",
            "  Required: DEEPSEEK_API_KEY",
            "  Optional: GLM_API_KEY",
            "",
            "BASIC SETUP (3-4 API keys):",
            "  Required: DEEPSEEK_API_KEY",
            "  Recommended: GLM_API_KEY, GROK_API_KEY, NVIDIA_API_KEY",
            "",
            "STANDARD SETUP (5-8 API keys):",
            "  Add: CODESTRAL_API_KEY, GEMINI_API_KEY, etc.",
            "",
            "FULL SETUP (9+ API keys):",
            "  All available providers configured",
            "",
            "SETUP STEPS:",
            "1. Set environment variables:",
        ]

        for provider in config.available_providers:
            instructions.append(
                f"   export {provider.name.upper()}_API_KEY='your-key-here'"
            )

        instructions.extend(
            [
                "",
                "2. Run configuration validation:",
                '   python -c "from amas.config.minimal_config import get_config_manager; print(get_config_manager().validate_config())"',
                "",
                "3. Start AMAS:",
                "   python -m amas.main",
                "",
                "=" * 60,
            ]
        )

        return "\n".join(instructions)

    def get_feature_status(self) -> Dict[str, Any]:
        """Get status of available features"""
        config = self.get_config()

    def get_minimal_docker_compose(self, mode: MinimalMode = MinimalMode.BASIC) -> str:
        """Get minimal docker-compose configuration"""
        minimal_config = self.get_minimal_config(mode)

        compose = """version: '3.8'

services:
  amas:
    build: .
    environment:
      # Database
      AMAS_DB_HOST: postgres
      AMAS_DB_USER: amas
      AMAS_DB_PASSWORD: amas123
      AMAS_DB_NAME: amas

      # Redis
      AMAS_REDIS_HOST: redis

      # Neo4j
      AMAS_NEO4J_HOST: neo4j
      AMAS_NEO4J_USER: neo4j
      AMAS_NEO4J_PASSWORD: amas123

      # AI Providers (Minimal Mode)
"""

        for provider in minimal_config.required_providers:
            env_var = f"{provider.value.upper()}_API_KEY"
            compose += f"      {env_var}: ${{{env_var}}}\n"

        for provider in minimal_config.optional_providers:
            env_var = f"{provider.value.upper()}_API_KEY"
            compose += f"      {env_var}: ${{{env_var}}}  # Optional\n"

        compose += """
    depends_on:
      - postgres
      - redis
      - neo4j
    ports:
      - "8000:8000"
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
        """

        return compose

    def get_feature_status(self) -> Dict[str, Any]:
        """Get status of available features"""
        config = self.get_config()
        return {
            "configuration_level": config.config_level.value,
            "features": config.features,
            "providers": [
                {
                    "name": p.name,
                    "priority": p.priority,
                    "required": p.required,
                    "available": True,
                }
                for p in config.available_providers
            ],
            "recommendations": self._get_recommendations(),
        }

    def _get_recommendations(self) -> List[str]:
        """Get configuration recommendations"""
        config = self.get_config()
        recommendations = []

        if config.config_level == ConfigLevel.MINIMAL:
            recommendations.extend(
                [
                    "Add GLM_API_KEY for better reliability",
                    "Add GROK_API_KEY for enhanced capabilities",
                    "Consider NVIDIA_API_KEY for specialized tasks",
                ]
            )
        elif config.config_level == ConfigLevel.BASIC:
            recommendations.extend(
                [
                    "Add CODESTRAL_API_KEY for code analysis",
                    "Consider GEMINI_API_KEY for additional fallback",
                ]
            )
        elif config.config_level == ConfigLevel.STANDARD:
            recommendations.extend(
                [
                    "Configuration is well-balanced",
                    "Consider adding more specialized providers if needed",
                ]
            )
        else:  # FULL
            recommendations.append("Configuration is optimal - all features available")

        return recommendations

# Global configuration manager
_config_manager: Optional[MinimalConfigManager] = None

def get_config_manager() -> MinimalConfigManager:
    """Get or create the global configuration manager"""
    global _config_manager
    if _config_manager is None:
        _config_manager = MinimalConfigManager()
    return _config_manager


def get_minimal_config() -> MinimalConfig:
    """Get the current minimal configuration"""
    return get_config_manager().get_config()


def validate_setup() -> Dict[str, Any]:
    """Validate the current setup"""
    return get_config_manager().validate_config()


def print_setup_instructions():
    """Print setup instructions"""
    print(get_config_manager().get_setup_instructions())


# Example usage
if __name__ == "__main__":
    print("🔧 AMAS Minimal Configuration System")
    print("=" * 50)

    # Get configuration manager
    config_manager = get_config_manager()

    # Show current configuration
    config = config_manager.get_config()
    print(f"Configuration Level: {config.config_level.value}")
    print(f"Available Providers: {len(config.available_providers)}")

    # Show validation results
    validation = config_manager.validate_config()
    print(f"\nValidation: {'✅ Valid' if validation['valid'] else '❌ Invalid'}")

    if validation["warnings"]:
        print("Warnings:")
        for warning in validation["warnings"]:
            print(f"  ⚠️  {warning}")

    if validation["errors"]:
        print("Errors:")
        for error in validation["errors"]:
            print(f"  ❌ {error}")

    # Show feature status
    print("\nFeature Status:")
    features = config_manager.get_feature_status()
    for feature, available in features["features"].items():
        status = "✅" if available else "❌"
        print(f"  {status} {feature}")

    # Show recommendations
    print("\nRecommendations:")
    for rec in features["recommendations"]:
        print(f"  💡 {rec}")

    # Show setup instructions
    print("\n" + config_manager.get_setup_instructions())
>>>>>>> origin/main
