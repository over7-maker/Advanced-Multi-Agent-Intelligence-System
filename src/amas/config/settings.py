"""
AMAS Configuration Settings

Centralized configuration management using Pydantic settings.
This module provides type-safe configuration with validation and environment variable support.
"""

# import os
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfig(BaseSettings):
    """Database configuration"""

    host: str = Field(default="localhost", validation_alias="AMAS_DB_HOST")
    port: int = Field(default=5432, validation_alias="AMAS_DB_PORT")
    user: str = Field(default="amas", validation_alias="AMAS_DB_USER")
    password: str = Field(default="amas123", validation_alias="AMAS_DB_PASSWORD")
    database: str = Field(default="amas", validation_alias="AMAS_DB_NAME")

    @property
    def url(self) -> str:
        """Get database connection URL."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

    @field_validator("port")
    @classmethod
    def validate_port(cls, v):
        """Validate port number."""
        if not 1 <= v <= 65535:
            raise ValueError("Port must be between 1 and 65535")
        return v


class RedisConfig(BaseSettings):
    """Redis configuration"""

    host: str = Field(default="localhost", validation_alias="AMAS_REDIS_HOST")
    port: int = Field(default=6379, validation_alias="AMAS_REDIS_PORT")
    db: int = Field(default=0, validation_alias="AMAS_REDIS_DB")
    password: Optional[str] = Field(default=None, validation_alias="AMAS_REDIS_PASSWORD")

    @property
    def url(self) -> str:
        """Get Redis connection URL."""
        auth = f":{self.password}@" if self.password else ""
        return f"redis://{auth}{self.host}:{self.port}/{self.db}"

    @field_validator("port")
    @classmethod
    def validate_port(cls, v):
        """Validate port number."""
        if not 1 <= v <= 65535:
            raise ValueError("Port must be between 1 and 65535")
        return v

    @field_validator("db")
    @classmethod
    def validate_db(cls, v):
        """Validate database number."""
        if not 0 <= v <= 15:
            raise ValueError("Redis database must be between 0 and 15")
        return v


class Neo4jConfig(BaseSettings):
    """Neo4j configuration"""

    host: str = Field(default="localhost", validation_alias="AMAS_NEO4J_HOST")
    port: int = Field(default=7687, validation_alias="AMAS_NEO4J_PORT")
    user: str = Field(default="neo4j", validation_alias="AMAS_NEO4J_USER")
    password: str = Field(default="amas123", validation_alias="AMAS_NEO4J_PASSWORD")
    database: str = Field(default="neo4j", validation_alias="AMAS_NEO4J_DATABASE")

    @property
    def uri(self) -> str:
        return f"bolt://{self.host}:{self.port}"


class LLMConfig(BaseSettings):
    """LLM service configuration"""

    host: str = Field(default="localhost", validation_alias="AMAS_LLM_HOST")
    port: int = Field(default=11434, validation_alias="AMAS_LLM_PORT")
    model: str = Field(default="llama3.1:70b", validation_alias="AMAS_LLM_MODEL")
    timeout: int = Field(default=300, validation_alias="AMAS_LLM_TIMEOUT")

    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}"


class SecurityConfig(BaseSettings):
    """Security configuration"""

    jwt_secret: str = Field(
        default="amas_jwt_secret_key_2024_secure", validation_alias="AMAS_JWT_SECRET"
    )
    encryption_key: str = Field(
        default="amas_encryption_key_2024_secure_32_chars", validation_alias="AMAS_ENCRYPTION_KEY"
    )
    audit_enabled: bool = Field(default=True, validation_alias="AMAS_AUDIT_ENABLED")
    rate_limit_requests: int = Field(default=1000, validation_alias="AMAS_RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=3600, validation_alias="AMAS_RATE_LIMIT_WINDOW")


class APIConfig(BaseSettings):
    """API configuration"""

    host: str = Field(default="0.0.0.0", validation_alias="AMAS_API_HOST")
    port: int = Field(default=8000, validation_alias="AMAS_API_PORT")
    workers: int = Field(default=4, validation_alias="AMAS_API_WORKERS")
    reload: bool = Field(default=False, validation_alias="AMAS_API_RELOAD")
    cors_origins: List[str] = Field(
        default=["http://localhost:3000"], validation_alias="AMAS_CORS_ORIGINS"
    )


class AISettings(BaseSettings):
    """AI provider configuration settings"""

    # Standard Providers (Tier 0)
    openai_api_key: Optional[str] = Field(default=None)
    openai_org_id: Optional[str] = Field(default=None)
    anthropic_api_key: Optional[str] = Field(default=None)
    google_ai_api_key: Optional[str] = Field(default=None)
    groq_api_key: Optional[str] = Field(default=None)
    cohere_api_key: Optional[str] = Field(default=None)
    huggingface_api_key: Optional[str] = Field(default=None)

    # Premium Speed & Quality (Tier 1)
    cerebras_api_key: Optional[str] = Field(default=None)
    nvidia_api_key: Optional[str] = Field(default=None)
    groq2_api_key: Optional[str] = Field(default=None)
    groqai_api_key: Optional[str] = Field(default=None)

    # High Quality (Tier 2)
    deepseek_api_key: Optional[str] = Field(default=None)
    codestral_api_key: Optional[str] = Field(default=None)
    glm_api_key: Optional[str] = Field(default=None)
    gemini2_api_key: Optional[str] = Field(default=None)
    grok_api_key: Optional[str] = Field(default=None)

    # OpenRouter Free Tier (Tier 4)
    kimi_api_key: Optional[str] = Field(default=None)
    qwen_api_key: Optional[str] = Field(default=None)
    gptoss_api_key: Optional[str] = Field(default=None)
    chutes_api_key: Optional[str] = Field(default=None)

    # Additional Providers (Architecture Requirement - 16+ providers)
    together_api_key: Optional[str] = Field(default=None)
    perplexity_api_key: Optional[str] = Field(default=None)
    fireworks_api_key: Optional[str] = Field(default=None)
    replicate_api_key: Optional[str] = Field(default=None)
    ai21_api_key: Optional[str] = Field(default=None)
    aleph_alpha_api_key: Optional[str] = Field(default=None)
    writer_api_key: Optional[str] = Field(default=None)
    moonshot_api_key: Optional[str] = Field(default=None)
    mistral_api_key: Optional[str] = Field(default=None)

    # Model settings
    default_model: str = Field(default="gpt-4")
    fallback_model: str = Field(default="gpt-3.5-turbo")
    max_tokens: int = Field(default=4000)
    temperature: float = Field(default=0.7)

    model_config = SettingsConfigDict(env_prefix="AI_")


class IntegrationSettings(BaseSettings):
    """Integration platform credentials settings"""

    # N8N
    n8n_base_url: Optional[str] = Field(default="http://localhost:5678")
    n8n_api_key: Optional[str] = Field(default=None)
    n8n_username: Optional[str] = Field(default=None)
    n8n_password: Optional[str] = Field(default=None)

    # Slack
    slack_bot_token: Optional[str] = Field(default=None)
    slack_signing_secret: Optional[str] = Field(default=None)
    slack_app_token: Optional[str] = Field(default=None)

    # GitHub
    github_access_token: Optional[str] = Field(default=None)
    github_webhook_secret: Optional[str] = Field(default=None)

    # Notion
    notion_api_key: Optional[str] = Field(default=None)

    # Jira
    jira_server: Optional[str] = Field(default=None)
    jira_email: Optional[str] = Field(default=None)
    jira_api_token: Optional[str] = Field(default=None)

    # Salesforce
    salesforce_username: Optional[str] = Field(default=None)
    salesforce_password: Optional[str] = Field(default=None)
    salesforce_security_token: Optional[str] = Field(default=None)
    salesforce_access_token: Optional[str] = Field(default=None)
    salesforce_instance_url: Optional[str] = Field(default=None)
    salesforce_client_id: Optional[str] = Field(default=None)
    salesforce_client_secret: Optional[str] = Field(default=None)

    model_config = SettingsConfigDict(env_prefix="INTEGRATION_")


class AMASConfig(BaseSettings):
    """
    Main AMAS configuration class.

    This class manages all configuration settings for the AMAS system,
    including validation, environment variable loading, and directory management.
    """

    # Application settings
    app_name: str = Field(
        default="AMAS", validation_alias="AMAS_APP_NAME", description="Application name"
    )
    version: str = Field(
        default="1.0.0", validation_alias="AMAS_VERSION", description="Application version"
    )
    environment: str = Field(
        default="development",
        validation_alias="AMAS_ENVIRONMENT",
        description="Deployment environment",
    )
    debug: bool = Field(
        default=False, validation_alias="AMAS_DEBUG", description="Enable debug mode"
    )
    offline_mode: bool = Field(
        default=True, validation_alias="AMAS_OFFLINE_MODE", description="Enable offline mode"
    )
    gpu_enabled: bool = Field(
        default=True, validation_alias="AMAS_GPU_ENABLED", description="Enable GPU acceleration"
    )

    # Logging
    log_level: str = Field(default="INFO", validation_alias="AMAS_LOG_LEVEL")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        validation_alias="AMAS_LOG_FORMAT",
    )

    # Directory configuration
    data_dir: Path = Field(
        default=Path("data"), validation_alias="AMAS_DATA_DIR", description="Data directory path"
    )
    logs_dir: Path = Field(
        default=Path("logs"), validation_alias="AMAS_LOGS_DIR", description="Logs directory path"
    )
    models_dir: Path = Field(
        default=Path("models"),
        validation_alias="AMAS_MODELS_DIR",
        description="Models directory path",
    )

    # Component configurations
    database: DatabaseConfig = Field(
        default_factory=DatabaseConfig, description="Database configuration"
    )
    redis: RedisConfig = Field(
        default_factory=RedisConfig, description="Redis configuration"
    )
    neo4j: Neo4jConfig = Field(
        default_factory=Neo4jConfig, description="Neo4j configuration"
    )
    llm: LLMConfig = Field(
        default_factory=LLMConfig, description="LLM service configuration"
    )
    security: SecurityConfig = Field(
        default_factory=SecurityConfig, description="Security configuration"
    )
    api: APIConfig = Field(default_factory=APIConfig, description="API configuration")
    ai: "AISettings" = Field(default_factory=lambda: AISettings(), description="AI provider settings")
    integration: "IntegrationSettings" = Field(default_factory=lambda: IntegrationSettings(), description="Integration platform settings")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        validate_assignment=True,
        extra="ignore",  # Ignore extra fields
    )

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v):
        valid_envs = ["development", "staging", "production"]
        if v.lower() not in valid_envs:
            raise ValueError(f"Environment must be one of {valid_envs}")
        return v.lower()

    @field_validator("data_dir", "logs_dir", "models_dir")
    @classmethod
    def validate_directories(cls, v: Path) -> Path:
        """Validate and convert directory paths."""
        if isinstance(v, str):
            return Path(v)
        return v

    @model_validator(mode="after")
    def validate_configuration(self) -> "AMASConfig":
        """Validate overall configuration."""
        # Check if we're in production mode
        if self.environment == "production":
            if self.debug:
                raise ValueError("Debug mode cannot be enabled in production")
            if (
                not self.security.jwt_secret
                or self.security.jwt_secret == "amas_jwt_secret_key_2024_secure"
            ):
                raise ValueError("Production requires secure JWT secret")

        return self

    def create_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        for directory in [self.data_dir, self.logs_dir, self.models_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment.lower() == "production"

    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment.lower() == "development"

    def get_api_keys(self) -> Dict[str, Optional[str]]:
        """Get all configured API keys."""
        # Get from ai settings if available
        if hasattr(self, 'ai') and self.ai:
            return {
                "openai": self.ai.openai_api_key,
                "anthropic": self.ai.anthropic_api_key,
                "google_ai": self.ai.google_ai_api_key,
                "groq": self.ai.groq_api_key,
                "cohere": self.ai.cohere_api_key,
                "huggingface": self.ai.huggingface_api_key,
                "cerebras": self.ai.cerebras_api_key,
                "nvidia": self.ai.nvidia_api_key,
                "groq2": self.ai.groq2_api_key,
                "groqai": self.ai.groqai_api_key,
                "deepseek": self.ai.deepseek_api_key,
                "codestral": self.ai.codestral_api_key,
                "glm": self.ai.glm_api_key,
                "gemini2": self.ai.gemini2_api_key,
                "grok": self.ai.grok_api_key,
                "kimi": self.ai.kimi_api_key,
                "qwen": self.ai.qwen_api_key,
                "gptoss": self.ai.gptoss_api_key,
                "chutes": self.ai.chutes_api_key,
                "together": self.ai.together_api_key,
                "perplexity": self.ai.perplexity_api_key,
                "fireworks": self.ai.fireworks_api_key,
                "replicate": self.ai.replicate_api_key,
                "ai21": self.ai.ai21_api_key,
                "aleph_alpha": self.ai.aleph_alpha_api_key,
                "writer": self.ai.writer_api_key,
                "moonshot": self.ai.moonshot_api_key,
                "mistral": self.ai.mistral_api_key,
            }
        return {}


# Global configuration instance
_config: Optional[AMASConfig] = None


def get_settings() -> AMASConfig:
    """Get the global configuration instance"""
    global _config
    if _config is None:
        _config = AMASConfig()
        _config.create_directories()
    return _config


def reload_settings() -> AMASConfig:
    """Reload configuration from environment"""
    global _config
    _config = AMASConfig()
    _config.create_directories()
    return _config
