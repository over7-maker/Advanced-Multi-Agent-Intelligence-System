"""
AMAS Configuration Management
Production-ready configuration with pydantic-settings
"""

import os
from typing import List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseModel):
    """Database configuration settings"""

    url: str = Field(default="postgresql://postgres:amas_password@localhost:5432/amas")
    host: str = Field(default="localhost")
    port: int = Field(default=5432)
    name: str = Field(default="amas")
    user: str = Field(default="postgres")
    password: str = Field(default="amas_password")
    pool_size: int = Field(default=10)
    max_overflow: int = Field(default=20)
    echo: bool = Field(default=False)

    model_config = ConfigDict(env_prefix="DB_")


class RedisSettings(BaseModel):
    """Redis configuration settings"""

    url: str = Field(default="redis://localhost:6379/0")
    host: str = Field(default="localhost")
    port: int = Field(default=6379)
    password: Optional[str] = Field(default=None)
    db: int = Field(default=0)
    max_connections: int = Field(default=20)

    model_config = ConfigDict(env_prefix="REDIS_")


class Neo4jSettings(BaseModel):
    """Neo4j configuration settings"""

    uri: str = Field(default="bolt://localhost:7687")
    user: str = Field(default="neo4j")
    password: str = Field(default="amas_password")
    max_connections: int = Field(default=50)

    model_config = ConfigDict(env_prefix="NEO4J_")


class SecuritySettings(BaseModel):
    """Security configuration settings"""

    secret_key: str = Field(default="default_secret_key_change_in_production")
    jwt_secret_key: str = Field(default="default_jwt_secret_key_change_in_production")
    jwt_algorithm: str = Field(default="HS256")
    jwt_access_token_expire_minutes: int = Field(default=30)
    jwt_refresh_token_expire_days: int = Field(default=7)
    bcrypt_rounds: int = Field(default=12)

    # CORS settings - allow localhost on any port for development
    cors_origins: List[str] = Field(default=["http://localhost:3000", "http://localhost:8000", "http://localhost:8001", "http://127.0.0.1:8000", "http://127.0.0.1:8001"])
    cors_allow_credentials: bool = Field(default=True)
    cors_allow_methods: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )
    cors_allow_headers: List[str] = Field(default=["*"])

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    model_config = ConfigDict(env_prefix="SECURITY_")


class AISettings(BaseModel):
    """AI provider configuration settings"""

    # OpenAI
    openai_api_key: Optional[str] = Field(default=None)
    openai_org_id: Optional[str] = Field(default=None)

    # Anthropic
    anthropic_api_key: Optional[str] = Field(default=None)

    # Google AI
    google_ai_api_key: Optional[str] = Field(default=None)

    # Groq
    groq_api_key: Optional[str] = Field(default=None)

    # Cohere
    cohere_api_key: Optional[str] = Field(default=None)

    # Hugging Face
    huggingface_api_key: Optional[str] = Field(default=None)

    # Model settings
    default_model: str = Field(default="gpt-4")
    fallback_model: str = Field(default="gpt-3.5-turbo")
    max_tokens: int = Field(default=4000)
    temperature: float = Field(default=0.7)

    model_config = ConfigDict(env_prefix="AI_")


class MonitoringSettings(BaseModel):
    """Monitoring and observability settings"""

    prometheus_enabled: bool = Field(default=True)
    prometheus_port: int = Field(default=9090)

    grafana_enabled: bool = Field(default=True)
    grafana_port: int = Field(default=3001)
    grafana_admin_password: str = Field(default="amas_grafana_password")

    # Logging
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="json")
    log_file_path: str = Field(default="/app/logs/amas.log")
    log_max_size: str = Field(default="100MB")
    log_backup_count: int = Field(default=5)

    model_config = ConfigDict(env_prefix="MONITORING_")


class PerformanceSettings(BaseModel):
    """Performance and scaling settings"""

    worker_processes: int = Field(default=4)
    worker_connections: int = Field(default=1000)
    max_requests: int = Field(default=1000)
    max_requests_jitter: int = Field(default=100)

    # Cache settings
    cache_ttl: int = Field(default=3600)
    cache_max_size: int = Field(default=1000)

    # Rate limiting
    rate_limit_requests: int = Field(default=100)
    rate_limit_window: int = Field(default=60)

    # Agent settings
    max_agents: int = Field(default=10)
    agent_timeout: int = Field(default=300)
    agent_memory_limit: int = Field(default=1000)

    model_config = ConfigDict(env_prefix="PERFORMANCE_")


class FeatureFlags(BaseModel):
    """Feature flags for enabling/disabling functionality"""

    enable_voice_commands: bool = Field(default=True)
    enable_web_dashboard: bool = Field(default=True)
    enable_api_documentation: bool = Field(default=True)
    enable_metrics_collection: bool = Field(default=True)
    enable_health_checks: bool = Field(default=True)

    model_config = ConfigDict(env_prefix="FEATURE_")


class Settings(BaseSettings):
    """Main application settings"""

    # Application
    app_name: str = Field(default="AMAS")
    environment: str = Field(default="development")
    debug: bool = Field(default=False)
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)

    # Sub-settings
    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    neo4j: Neo4jSettings = Neo4jSettings()
    security: SecuritySettings = SecuritySettings()
    ai: AISettings = AISettings()
    monitoring: MonitoringSettings = MonitoringSettings()
    performance: PerformanceSettings = PerformanceSettings()
    features: FeatureFlags = FeatureFlags()

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v):
        allowed = ["development", "testing", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    @property
    def is_testing(self) -> bool:
        return self.environment == "testing"

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        validate_assignment=True,
        extra="ignore",  # Ignore extra environment variables
    )


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance"""
    return settings


def validate_configuration() -> bool:
    """Validate the current configuration"""
    try:
        # Check required settings
        if not settings.security.secret_key:
            raise ValueError("SECRET_KEY is required")

        if not settings.security.jwt_secret_key:
            raise ValueError("JWT_SECRET_KEY is required")

        # Check database connection
        if not settings.database.url:
            raise ValueError("DATABASE_URL is required")

        # Check Redis connection
        if not settings.redis.url:
            raise ValueError("REDIS_URL is required")

        # Check Neo4j connection
        if not settings.neo4j.uri:
            raise ValueError("NEO4J_URI is required")

        return True

    except Exception as e:
        print(f"Configuration validation failed: {e}")
        return False


if __name__ == "__main__":
    # Test configuration loading
    print("Loading AMAS configuration...")
    print(f"Environment: {settings.environment}")
    print(f"Debug mode: {settings.debug}")
    print(f"Database URL: {settings.database.url}")
    print(f"Redis URL: {settings.redis.url}")
    print(f"Neo4j URI: {settings.neo4j.uri}")

    if validate_configuration():
        print("✅ Configuration is valid")
    else:
        print("❌ Configuration validation failed")
