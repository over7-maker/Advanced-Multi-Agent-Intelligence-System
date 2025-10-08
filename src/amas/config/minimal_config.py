"""
Minimal Configuration Mode for AMAS

Provides a simplified configuration requiring only 3-4 API keys
with graceful fallback for missing providers.
"""

import logging
import os
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from .ai_config import AIProvider, AIProviderConfig, AIConfigManager

logger = logging.getLogger(__name__)

class MinimalMode(Enum):
    """Minimal configuration modes"""
    BASIC = "basic"  # 3 providers minimum
    STANDARD = "standard"  # 4 providers recommended
    FULL = "full"  # All providers

@dataclass
class MinimalConfig:
    """Minimal configuration settings"""
    mode: MinimalMode
    required_providers: List[AIProvider]
    optional_providers: List[AIProvider]
    fallback_enabled: bool = True
    graceful_degradation: bool = True

class MinimalConfigManager:
    """Manages minimal configuration mode"""

    def __init__(self):
        self.minimal_configs = {
            MinimalMode.BASIC: MinimalConfig(
                mode=MinimalMode.BASIC,
                required_providers=[
                    AIProvider.DEEPSEEK,  # Primary
                    AIProvider.GLM,       # Secondary
                    AIProvider.GROK,      # Tertiary
                ],
                optional_providers=[
                    AIProvider.KIMI,
                    AIProvider.QWEN,
                    AIProvider.GPTOSS,
                ],
                fallback_enabled=True,
                graceful_degradation=True,
            ),
            MinimalMode.STANDARD: MinimalConfig(
                mode=MinimalMode.STANDARD,
                required_providers=[
                    AIProvider.DEEPSEEK,  # Primary
                    AIProvider.GLM,       # Secondary
                    AIProvider.GROK,      # Tertiary
                    AIProvider.KIMI,      # Quaternary
                ],
                optional_providers=[
                    AIProvider.QWEN,
                    AIProvider.GPTOSS,
                ],
                fallback_enabled=True,
                graceful_degradation=True,
            ),
            MinimalMode.FULL: MinimalConfig(
                mode=MinimalMode.FULL,
                required_providers=list(AIProvider),
                optional_providers=[],
                fallback_enabled=False,
                graceful_degradation=False,
            ),
        }

    def get_minimal_config(self, mode: MinimalMode = MinimalMode.BASIC) -> MinimalConfig:
        """Get minimal configuration for specified mode"""
        return self.minimal_configs[mode]

    def validate_minimal_setup(self, mode: MinimalMode = MinimalMode.BASIC) -> Dict[str, Any]:
        """Validate if current environment meets minimal requirements"""
        ai_config = AIConfigManager()
        minimal_config = self.get_minimal_config(mode)

        validation_result = {
            "mode": mode.value,
            "valid": True,
            "available_providers": [],
            "missing_required": [],
            "missing_optional": [],
            "warnings": [],
            "recommendations": [],
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

        # Check if we have at least one provider
        if not validation_result["available_providers"]:
            validation_result["valid"] = False
            validation_result["warnings"].append("No AI providers are configured")
            validation_result["recommendations"].append(
                "Configure at least one AI provider to use the system"
            )

        return validation_result

    def create_minimal_ai_config(self, mode: MinimalMode = MinimalMode.BASIC) -> AIConfigManager:
        """Create AI configuration with only minimal providers enabled"""
        minimal_config = self.get_minimal_config(mode)
        ai_config = AIConfigManager()

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

        guide = f"""
# AMAS Minimal Configuration Setup Guide - {mode.value.upper()} Mode

## Required Environment Variables

### Primary Providers (Required)
"""

        for provider in minimal_config.required_providers:
            env_var = f"{provider.value.upper()}_API_KEY"
            guide += f"export {env_var}=your_api_key_here\n"

        if minimal_config.optional_providers:
            guide += "\n### Optional Providers (Recommended)\n"
            for provider in minimal_config.optional_providers:
                env_var = f"{provider.value.upper()}_API_KEY"
                guide += f"export {env_var}=your_api_key_here  # Optional\n"

        guide += f"""
## Quick Start

1. Set the required environment variables above
2. Run: python scripts/validate_env.py --mode {mode.value}
3. Start the system: python main.py

## Fallback Behavior

- System will gracefully degrade if optional providers are missing
- Circuit breakers will handle provider failures automatically
- Tasks will be routed to available providers only

## Validation

Run the validation script to check your setup:
```bash
python scripts/validate_env.py --mode {mode.value} --verbose
```
"""

        return guide

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

  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: amas
      POSTGRES_PASSWORD: amas123
      POSTGRES_DB: amas
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  neo4j:
    image: neo4j:5
    environment:
      NEO4J_AUTH: neo4j/amas123
    ports:
      - "7474:7474"
      - "7687:7687"
    volumes:
      - neo4j_data:/data

volumes:
  postgres_data:
  neo4j_data:
"""

        return compose

# Global minimal config manager
minimal_config_manager = MinimalConfigManager()

def get_minimal_config_manager() -> MinimalConfigManager:
    """Get the global minimal configuration manager"""
    return minimal_config_manager

def validate_environment(mode: MinimalMode = MinimalMode.BASIC) -> Dict[str, Any]:
    """Quick validation of environment for minimal mode"""
    return minimal_config_manager.validate_minimal_setup(mode)
