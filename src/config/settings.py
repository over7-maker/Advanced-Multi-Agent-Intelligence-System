"""
AMAS Configuration Management
Production-ready configuration with pydantic-settings
"""

import os
from typing import List, Optional, Union

from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseModel):
    """Database configuration settings"""

    url: str = Field(
        default="postgresql://postgres:amas_password@localhost:5432/amas",
        env="DATABASE_URL",
    )
    host: str = Field(default="localhost", env="POSTGRES_HOST")
    port: int = Field(default=5432, env="POSTGRES_PORT")
    name: str = Field(default="amas", env="POSTGRES_DB")
    user: str = Field(default="postgres", env="POSTGRES_USER")
    password: str = Field(default="amas_password", env="POSTGRES_PASSWORD")
    pool_size: int = Field(default=10, env="DB_POOL_SIZE")
    max_overflow: int = Field(default=20, env="DB_MAX_OVERFLOW")
    echo: bool = Field(default=False, env="DB_ECHO")

    class Config:
        env_prefix = "DB_"


class RedisSettings(BaseModel):
    """Redis configuration settings"""

    url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    host: str = Field(default="localhost", env="REDIS_HOST")
    port: int = Field(default=6379, env="REDIS_PORT")
    password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    db: int = Field(default=0, env="REDIS_DB")
    max_connections: int = Field(default=20, env="REDIS_MAX_CONNECTIONS")

    class Config:
        env_prefix = "REDIS_"


class Neo4jSettings(BaseModel):
    """Neo4j configuration settings"""

    uri: str = Field(default="bolt://localhost:7687", env="NEO4J_URI")
    user: str = Field(default="neo4j", env="NEO4J_USER")
    password: str = Field(default="amas_password", env="NEO4J_PASSWORD")
    max_connections: int = Field(default=50, env="NEO4J_MAX_CONNECTIONS")

    class Config:
        env_prefix = "NEO4J_"


class SecuritySettings(BaseModel):
    """Security configuration settings"""

    secret_key: str = Field(
        default="default_secret_key_change_in_production", env="SECRET_KEY"
    )
    jwt_secret_key: str = Field(
        default="default_jwt_secret_key_change_in_production", env="JWT_SECRET_KEY"
    )
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(
        default=30, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    jwt_refresh_token_expire_days: int = Field(
        default=7, env="JWT_REFRESH_TOKEN_EXPIRE_DAYS"
    )
    bcrypt_rounds: int = Field(default=12, env="BCRYPT_ROUNDS")

    # CORS settings
    cors_origins: List[str] = Field(
        default=["http://localhost:3000"], env="CORS_ORIGINS"
    )
    cors_allow_credentials: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    cors_allow_methods: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "OPTIONS"], env="CORS_ALLOW_METHODS"
    )
    cors_allow_headers: List[str] = Field(default=["*"], env="CORS_ALLOW_HEADERS")

    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    class Config:
        env_prefix = "SECURITY_"


class AISettings(BaseModel):
    """AI provider configuration settings"""

    # OpenAI
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_org_id: Optional[str] = Field(default=None, env="OPENAI_ORG_ID")

    # Anthropic
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")

    # Google AI
    google_ai_api_key: Optional[str] = Field(default=None, env="GOOGLE_AI_API_KEY")

    # Groq
    groq_api_key: Optional[str] = Field(default=None, env="GROQ_API_KEY")

    # Cohere
    cohere_api_key: Optional[str] = Field(default=None, env="COHERE_API_KEY")

    # Hugging Face
    huggingface_api_key: Optional[str] = Field(default=None, env="HUGGINGFACE_API_KEY")

    # Model settings
    default_model: str = Field(default="gpt-4", env="DEFAULT_MODEL")
    fallback_model: str = Field(default="gpt-3.5-turbo", env="FALLBACK_MODEL")
    max_tokens: int = Field(default=4000, env="MAX_TOKENS")
    temperature: float = Field(default=0.7, env="TEMPERATURE")

    class Config:
        env_prefix = "AI_"


class MonitoringSettings(BaseModel):
    """Monitoring and observability settings"""

    prometheus_enabled: bool = Field(default=True, env="PROMETHEUS_ENABLED")
    prometheus_port: int = Field(default=9090, env="PROMETHEUS_PORT")

    grafana_enabled: bool = Field(default=True, env="GRAFANA_ENABLED")
    grafana_port: int = Field(default=3001, env="GRAFANA_PORT")
    grafana_admin_password: str = Field(
        default="amas_grafana_password", env="GRAFANA_ADMIN_PASSWORD"
    )

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    log_file_path: str = Field(default="/app/logs/amas.log", env="LOG_FILE_PATH")
    log_max_size: str = Field(default="100MB", env="LOG_MAX_SIZE")
    log_backup_count: int = Field(default=5, env="LOG_BACKUP_COUNT")

    class Config:
        env_prefix = "MONITORING_"


class PerformanceSettings(BaseModel):
    """Performance and scaling settings"""

    worker_processes: int = Field(default=4, env="WORKER_PROCESSES")
    worker_connections: int = Field(default=1000, env="WORKER_CONNECTIONS")
    max_requests: int = Field(default=1000, env="MAX_REQUESTS")
    max_requests_jitter: int = Field(default=100, env="MAX_REQUESTS_JITTER")

    # Cache settings
    cache_ttl: int = Field(default=3600, env="CACHE_TTL")
    cache_max_size: int = Field(default=1000, env="CACHE_MAX_SIZE")

    # Rate limiting
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=60, env="RATE_LIMIT_WINDOW")

    # Agent settings
    max_agents: int = Field(default=10, env="MAX_AGENTS")
    agent_timeout: int = Field(default=300, env="AGENT_TIMEOUT")
    agent_memory_limit: int = Field(default=1000, env="AGENT_MEMORY_LIMIT")

    class Config:
        env_prefix = "PERFORMANCE_"


class FeatureFlags(BaseModel):
    """Feature flags for enabling/disabling functionality"""

    enable_voice_commands: bool = Field(default=True, env="ENABLE_VOICE_COMMANDS")
    enable_web_dashboard: bool = Field(default=True, env="ENABLE_WEB_DASHBOARD")
    enable_api_documentation: bool = Field(default=True, env="ENABLE_API_DOCUMENTATION")
    enable_metrics_collection: bool = Field(
        default=True, env="ENABLE_METRICS_COLLECTION"
    )
    enable_health_checks: bool = Field(default=True, env="ENABLE_HEALTH_CHECKS")

    class Config:
        env_prefix = "FEATURE_"


class Settings(BaseSettings):
    """Main application settings"""

    # Application
    app_name: str = Field(default="AMAS", env="APP_NAME")
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")

    # Sub-settings
    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    neo4j: Neo4jSettings = Neo4jSettings()
    security: SecuritySettings = SecuritySettings()
    ai: AISettings = AISettings()
    monitoring: MonitoringSettings = MonitoringSettings()
    performance: PerformanceSettings = PerformanceSettings()
    features: FeatureFlags = FeatureFlags()

    @validator("environment")
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

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        validate_assignment = True
        extra = "ignore"  # Ignore extra environment variables


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
