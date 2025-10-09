"""
AMAS Configuration Settings

Centralized configuration management using Pydantic settings.
This module provides type-safe configuration with validation and environment variable support.
"""

# import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings


class DatabaseConfig(BaseSettings):
    """Database configuration"""

    host: str = Field(default="localhost", env="AMAS_DB_HOST")
    port: int = Field(default=5432, env="AMAS_DB_PORT")
    user: str = Field(default="amas", env="AMAS_DB_USER")
    password: str = Field(default="amas123", env="AMAS_DB_PASSWORD")
    database: str = Field(default="amas", env="AMAS_DB_NAME")

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

    host: str = Field(default="localhost", env="AMAS_REDIS_HOST")
    port: int = Field(default=6379, env="AMAS_REDIS_PORT")
    db: int = Field(default=0, env="AMAS_REDIS_DB")
    password: Optional[str] = Field(default=None, env="AMAS_REDIS_PASSWORD")

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

    host: str = Field(default="localhost", env="AMAS_NEO4J_HOST")
    port: int = Field(default=7687, env="AMAS_NEO4J_PORT")
    user: str = Field(default="neo4j", env="AMAS_NEO4J_USER")
    password: str = Field(default="amas123", env="AMAS_NEO4J_PASSWORD")
    database: str = Field(default="neo4j", env="AMAS_NEO4J_DATABASE")

    @property
    def uri(self) -> str:
        return f"bolt://{self.host}:{self.port}"


class LLMConfig(BaseSettings):
    """LLM service configuration"""

    host: str = Field(default="localhost", env="AMAS_LLM_HOST")
    port: int = Field(default=11434, env="AMAS_LLM_PORT")
    model: str = Field(default="llama3.1:70b", env="AMAS_LLM_MODEL")
    timeout: int = Field(default=300, env="AMAS_LLM_TIMEOUT")

    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}"


class SecurityConfig(BaseSettings):
    """Security configuration"""

    jwt_secret: str = Field(
        default="amas_jwt_secret_key_2024_secure", env="AMAS_JWT_SECRET"
    )
    encryption_key: str = Field(
        default="amas_encryption_key_2024_secure_32_chars", env="AMAS_ENCRYPTION_KEY"
    )
    audit_enabled: bool = Field(default=True, env="AMAS_AUDIT_ENABLED")
    rate_limit_requests: int = Field(default=1000, env="AMAS_RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=3600, env="AMAS_RATE_LIMIT_WINDOW")


class APIConfig(BaseSettings):
    """API configuration"""

    host: str = Field(default="0.0.0.0", env="AMAS_API_HOST")
    port: int = Field(default=8000, env="AMAS_API_PORT")
    workers: int = Field(default=4, env="AMAS_API_WORKERS")
    reload: bool = Field(default=False, env="AMAS_API_RELOAD")
    cors_origins: List[str] = Field(
        default=["http://localhost:3000"], env="AMAS_CORS_ORIGINS"
    )


class AMASConfig(BaseSettings):
    """
    Main AMAS configuration class.

    This class manages all configuration settings for the AMAS system,
    including validation, environment variable loading, and directory management.
    """

    # Application settings
    app_name: str = Field(
        default="AMAS", env="AMAS_APP_NAME", description="Application name"
    )
    version: str = Field(
        default="1.0.0", env="AMAS_VERSION", description="Application version"
    )
    environment: str = Field(
        default="development",
        env="AMAS_ENVIRONMENT",
        description="Deployment environment",
    )
    debug: bool = Field(
        default=False, env="AMAS_DEBUG", description="Enable debug mode"
    )
    offline_mode: bool = Field(
        default=True, env="AMAS_OFFLINE_MODE", description="Enable offline mode"
    )
    gpu_enabled: bool = Field(
        default=True, env="AMAS_GPU_ENABLED", description="Enable GPU acceleration"
    )

    # Logging
    log_level: str = Field(default="INFO", env="AMAS_LOG_LEVEL")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="AMAS_LOG_FORMAT",
    )

    # Directory configuration
    data_dir: Path = Field(
        default=Path("data"), env="AMAS_DATA_DIR", description="Data directory path"
    )
    logs_dir: Path = Field(
        default=Path("logs"), env="AMAS_LOGS_DIR", description="Logs directory path"
    )
    models_dir: Path = Field(
        default=Path("models"),
        env="AMAS_MODELS_DIR",
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

    # External API keys (loaded from environment)
    deepseek_api_key: Optional[str] = Field(
        default=None, env="DEEPSEEK_API_KEY", description="DeepSeek API key"
    )
    glm_api_key: Optional[str] = Field(
        default=None, env="GLM_API_KEY", description="GLM API key"
    )
    grok_api_key: Optional[str] = Field(
        default=None, env="GROK_API_KEY", description="Grok API key"
    )
    kimi_api_key: Optional[str] = Field(
        default=None, env="KIMI_API_KEY", description="Kimi API key"
    )
    qwen_api_key: Optional[str] = Field(
        default=None, env="QWEN_API_KEY", description="Qwen API key"
    )
    gptoss_api_key: Optional[str] = Field(
        default=None, env="GPTOSS_API_KEY", description="GPToss API key"
    )

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        validate_assignment = True
        extra = "ignore"  # Ignore extra fields

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
        return {
            "deepseek": self.deepseek_api_key,
            "glm": self.glm_api_key,
            "grok": self.grok_api_key,
            "kimi": self.kimi_api_key,
            "qwen": self.qwen_api_key,
            "gptoss": self.gptoss_api_key,
        }


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
