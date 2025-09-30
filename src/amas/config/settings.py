"""
AMAS Configuration Settings

Centralized configuration management using Pydantic settings.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseSettings, Field, validator


class DatabaseConfig(BaseSettings):
    """Database configuration"""

    host: str = Field(default="localhost", env="AMAS_DB_HOST")
    port: int = Field(default=5432, env="AMAS_DB_PORT")
    user: str = Field(default="amas", env="AMAS_DB_USER")
    password: str = Field(default="amas123", env="AMAS_DB_PASSWORD")
    database: str = Field(default="amas", env="AMAS_DB_NAME")

    @property
    def url(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


class RedisConfig(BaseSettings):
    """Redis configuration"""

    host: str = Field(default="localhost", env="AMAS_REDIS_HOST")
    port: int = Field(default=6379, env="AMAS_REDIS_PORT")
    db: int = Field(default=0, env="AMAS_REDIS_DB")
    password: Optional[str] = Field(default=None, env="AMAS_REDIS_PASSWORD")

    @property
    def url(self) -> str:
        auth = f":{self.password}@" if self.password else ""
        return f"redis://{auth}{self.host}:{self.port}/{self.db}"


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
    """Main AMAS configuration"""

    # Application settings
    app_name: str = Field(default="AMAS", env="AMAS_APP_NAME")
    version: str = Field(default="1.0.0", env="AMAS_VERSION")
    environment: str = Field(default="development", env="AMAS_ENVIRONMENT")
    debug: bool = Field(default=False, env="AMAS_DEBUG")
    offline_mode: bool = Field(default=True, env="AMAS_OFFLINE_MODE")
    gpu_enabled: bool = Field(default=True, env="AMAS_GPU_ENABLED")

    # Logging
    log_level: str = Field(default="INFO", env="AMAS_LOG_LEVEL")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="AMAS_LOG_FORMAT",
    )

    # Directories
    data_dir: Path = Field(default=Path("data"), env="AMAS_DATA_DIR")
    logs_dir: Path = Field(default=Path("logs"), env="AMAS_LOGS_DIR")
    models_dir: Path = Field(default=Path("models"), env="AMAS_MODELS_DIR")

    # Component configurations
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    neo4j: Neo4jConfig = Field(default_factory=Neo4jConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    api: APIConfig = Field(default_factory=APIConfig)

    # External API keys (loaded from environment)
    deepseek_api_key: Optional[str] = Field(default=None, env="DEEPSEEK_API_KEY")
    glm_api_key: Optional[str] = Field(default=None, env="GLM_API_KEY")
    grok_api_key: Optional[str] = Field(default=None, env="GROK_API_KEY")
    kimi_api_key: Optional[str] = Field(default=None, env="KIMI_API_KEY")
    qwen_api_key: Optional[str] = Field(default=None, env="QWEN_API_KEY")
    gptoss_api_key: Optional[str] = Field(default=None, env="GPTOSS_API_KEY")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @validator("log_level")
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()

    @validator("environment")
    def validate_environment(cls, v):
        valid_envs = ["development", "staging", "production"]
        if v.lower() not in valid_envs:
            raise ValueError(f"Environment must be one of {valid_envs}")
        return v.lower()

    def create_directories(self):
        """Create necessary directories"""
        for directory in [self.data_dir, self.logs_dir, self.models_dir]:
            directory.mkdir(parents=True, exist_ok=True)


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
