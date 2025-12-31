"""
AMAS Configuration Management
Production-ready configuration with pydantic-settings
"""

import os
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Database configuration settings"""

    url: str = Field(default="postgresql://postgres:amas_password@localhost:5432/amas")
    host: str = Field(default="localhost")
    port: int = Field(default=5432)
    name: str = Field(default="amas")
    user: str = Field(default="postgres")
    password: str = Field(default="amas_password")
    pool_size: int = Field(default=10, description="Base number of database connections")
    max_overflow: int = Field(default=20, description="Additional connections allowed beyond pool_size")
    pool_timeout: int = Field(default=30, description="Timeout in seconds for getting connection from pool")
    pool_recycle: int = Field(default=3600, description="Recycle connections after this many seconds")
    pool_pre_ping: bool = Field(default=True, description="Verify connections before using them")
    echo: bool = Field(default=False)

    model_config = SettingsConfigDict(
        env_prefix="DB_", 
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"  # Ignore extra environment variables
    )
    
    @model_validator(mode="after")
    def check_database_url(self):
        """Override URL if DATABASE_URL env var is set"""
        if os.getenv("DATABASE_URL"):
            db_url = os.getenv("DATABASE_URL").strip()
            # Strip trailing spaces from database name in URL
            # Format: postgresql://user:password@host:port/database
            if "/" in db_url:
                parts = db_url.rsplit("/", 1)
                if len(parts) == 2:
                    base_url = parts[0]
                    db_name = parts[1].strip()  # Remove trailing spaces from database name
                    self.url = f"{base_url}/{db_name}"
                else:
                    self.url = db_url
            else:
                self.url = db_url
        return self


class RedisSettings(BaseSettings):
    """Redis configuration settings"""

    url: str = Field(default="redis://localhost:6379/0")
    host: str = Field(default="localhost")
    port: int = Field(default=6379)
    password: Optional[str] = Field(default=None)
    db: int = Field(default=0)
    max_connections: int = Field(default=20)

    model_config = SettingsConfigDict(
        env_prefix="REDIS_", 
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"  # Ignore extra environment variables
    )
    
    @model_validator(mode="after")
    def check_redis_url(self):
        """Override URL if REDIS_URL env var is set, and add password if needed"""
        import logging
        logger = logging.getLogger(__name__)
        
        env_redis_url = os.getenv("REDIS_URL")
        env_redis_password = os.getenv("REDIS_PASSWORD")
        
        logger.debug(f"check_redis_url: REDIS_URL env var: {env_redis_url[:50] if env_redis_url else 'None'}...")
        logger.debug(f"check_redis_url: REDIS_PASSWORD env var: {'***' if env_redis_password else 'None'}")
        logger.debug(f"check_redis_url: Current self.url: {self.url}")
        logger.debug(f"check_redis_url: Current self.password: {'***' if self.password else 'None'}")
        
        # Override URL if env var is set
        if env_redis_url:
            self.url = env_redis_url
            logger.info(f"Redis URL set from env var: {self.url[:30]}...")
        
        # Use password from env var if available, otherwise use self.password
        password_to_use = env_redis_password or self.password
        
        # Check if password is set but not in URL
        if password_to_use and self.url and self.url.startswith("redis://"):
            # Check if URL already has password (format: redis://:password@host:port/db)
            # URL has password if it contains @ and : after redis://
            url_parts = self.url.split("://", 1)
            if len(url_parts) == 2:
                after_protocol = url_parts[1]
                url_has_password = "@" in after_protocol and ":" in after_protocol.split("@")[0]
            else:
                url_has_password = False
            
            logger.debug(f"check_redis_url: URL has password: {url_has_password}")
            
            if not url_has_password:
                # Add password to URL
                try:
                    # Parse URL to extract host:port/db
                    # Format: redis://host:port/db or redis://host:port
                    url_without_protocol = self.url.replace("redis://", "")
                    
                    # Split by / to get host:port and db
                    if "/" in url_without_protocol:
                        parts = url_without_protocol.split("/", 1)
                        host_port = parts[0]  # host:port
                        db_part = parts[1] if len(parts) > 1 else "0"
                    else:
                        host_port = url_without_protocol
                        db_part = "0"
                    
                    # Construct new URL with password
                    self.url = f"redis://:{password_to_use}@{host_port}/{db_part}"
                    # Also update self.password for consistency
                    if not self.password:
                        self.password = password_to_use
                    logger.info(f"Added password to Redis URL: redis://:***@{host_port}/{db_part}")
                except Exception as e:
                    logger.warning(f"Failed to add password to Redis URL: {e}")
        
        logger.debug(f"check_redis_url: Final self.url: {self.url}")
        return self


class Neo4jSettings(BaseSettings):
    """Neo4j configuration settings"""

    uri: str = Field(default="bolt://localhost:7687")
    user: str = Field(default="neo4j")
    password: str = Field(default="amas_password")
    max_connections: int = Field(default=50)

    model_config = SettingsConfigDict(
        env_prefix="NEO4J_",
        extra="ignore"  # Ignore extra environment variables
    )
    
    @model_validator(mode="after")
    def strip_neo4j_settings(self):
        """Strip whitespace from Neo4j settings"""
        self.uri = self.uri.strip() if self.uri else self.uri
        self.user = self.user.strip() if self.user else self.user
        self.password = self.password.strip() if self.password else self.password
        return self


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

    model_config = SettingsConfigDict(
        env_prefix="SECURITY_",
        extra="ignore"  # Ignore extra environment variables
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

    model_config = SettingsConfigDict(
        env_prefix="AI_",
        extra="ignore"  # Ignore extra environment variables
    )


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

    model_config = SettingsConfigDict(
        env_prefix="INTEGRATION_",
        extra="ignore"  # Ignore extra environment variables
    )


class MonitoringSettings(BaseSettings):
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

    model_config = SettingsConfigDict(
        env_prefix="MONITORING_",
        extra="ignore"  # Ignore extra environment variables
    )


class PerformanceSettings(BaseSettings):
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

    model_config = SettingsConfigDict(
        env_prefix="PERFORMANCE_",
        extra="ignore"  # Ignore extra environment variables
    )


class FeatureFlags(BaseSettings):
    """Feature flags for enabling/disabling functionality"""

    enable_voice_commands: bool = Field(default=True)
    enable_web_dashboard: bool = Field(default=True)
    enable_api_documentation: bool = Field(default=True)
    enable_metrics_collection: bool = Field(default=True)
    enable_health_checks: bool = Field(default=True)

    model_config = SettingsConfigDict(
        env_prefix="FEATURE_",
        extra="ignore"  # Ignore extra environment variables
    )


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
    integration: IntegrationSettings = IntegrationSettings()
    monitoring: MonitoringSettings = MonitoringSettings()
    performance: PerformanceSettings = PerformanceSettings()
    features: FeatureFlags = FeatureFlags()

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v):
        # Strip whitespace to handle trailing spaces from environment variables
        v = v.strip() if isinstance(v, str) else v
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

    model_config = SettingsConfigDict(
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
