"""
Orchestration Configuration Management

Centralized configuration for orchestration system with environment-based settings.
"""

import os
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class OrchestrationConfig:
    """Configuration for orchestration system"""
    
    # Agent Management
    max_specialist_agents_per_pool: int = 5
    max_concurrent_tasks_per_agent: int = 3
    agent_heartbeat_interval_seconds: int = 60
    agent_failure_threshold: int = 3
    agent_recovery_timeout_seconds: float = 300.0
    
    # Task Decomposition
    task_decomposition_timeout_seconds: float = 120.0
    max_sub_tasks_per_workflow: int = 50
    default_task_priority: int = 5
    
    # Communication
    message_delivery_timeout_seconds: float = 300.0
    max_message_retry_attempts: int = 3
    message_queue_max_size: int = 10000
    broadcast_subscription_limit: int = 1000
    
    # Workflow Execution
    workflow_execution_timeout_hours: float = 24.0
    max_workflow_retries: int = 3
    quality_gate_threshold: float = 0.85
    parallel_task_max_concurrency: int = 10
    
    # Performance
    enable_caching: bool = True
    cache_ttl_seconds: int = 3600
    enable_metrics_collection: bool = True
    metrics_retention_hours: int = 24
    
    # Observability
    enable_detailed_logging: bool = True
    log_level: str = "INFO"
    enable_tracing: bool = True
    trace_sample_rate: float = 1.0
    
    # Error Handling
    enable_circuit_breaker: bool = True
    circuit_breaker_failure_threshold: int = 5
    circuit_breaker_recovery_timeout: float = 60.0
    retry_max_attempts: int = 3
    retry_initial_delay: float = 1.0
    retry_max_delay: float = 60.0
    
    # Resource Limits
    max_active_workflows: int = 100
    max_total_agents: int = 500
    memory_limit_mb: int = 2048
    
    # Integration
    enable_api_endpoints: bool = True
    api_port: int = 8080
    enable_health_checks: bool = True
    health_check_interval_seconds: int = 30
    
    @classmethod
    def from_env(cls) -> "OrchestrationConfig":
        """Load configuration from environment variables"""
        config = cls()
        
        # Agent Management
        config.max_specialist_agents_per_pool = int(
            os.getenv("ORCHESTRATION_MAX_AGENTS_PER_POOL", config.max_specialist_agents_per_pool)
        )
        config.max_concurrent_tasks_per_agent = int(
            os.getenv("ORCHESTRATION_MAX_TASKS_PER_AGENT", config.max_concurrent_tasks_per_agent)
        )
        config.agent_heartbeat_interval_seconds = int(
            os.getenv("ORCHESTRATION_HEARTBEAT_INTERVAL", config.agent_heartbeat_interval_seconds)
        )
        
        # Task Decomposition
        config.task_decomposition_timeout_seconds = float(
            os.getenv("ORCHESTRATION_DECOMPOSITION_TIMEOUT", config.task_decomposition_timeout_seconds)
        )
        config.max_sub_tasks_per_workflow = int(
            os.getenv("ORCHESTRATION_MAX_SUBTASKS", config.max_sub_tasks_per_workflow)
        )
        
        # Communication
        config.message_delivery_timeout_seconds = float(
            os.getenv("ORCHESTRATION_MESSAGE_TIMEOUT", config.message_delivery_timeout_seconds)
        )
        config.max_message_retry_attempts = int(
            os.getenv("ORCHESTRATION_MESSAGE_RETRIES", config.max_message_retry_attempts)
        )
        
        # Workflow Execution
        config.workflow_execution_timeout_hours = float(
            os.getenv("ORCHESTRATION_WORKFLOW_TIMEOUT", config.workflow_execution_timeout_hours)
        )
        config.quality_gate_threshold = float(
            os.getenv("ORCHESTRATION_QUALITY_THRESHOLD", config.quality_gate_threshold)
        )
        
        # Performance
        config.enable_caching = os.getenv("ORCHESTRATION_ENABLE_CACHE", "true").lower() == "true"
        config.enable_metrics_collection = os.getenv("ORCHESTRATION_ENABLE_METRICS", "true").lower() == "true"
        
        # Observability
        config.log_level = os.getenv("ORCHESTRATION_LOG_LEVEL", config.log_level).upper()
        config.enable_tracing = os.getenv("ORCHESTRATION_ENABLE_TRACING", "true").lower() == "true"
        config.trace_sample_rate = float(
            os.getenv("ORCHESTRATION_TRACE_SAMPLE_RATE", config.trace_sample_rate)
        )
        
        # Error Handling
        config.enable_circuit_breaker = os.getenv("ORCHESTRATION_ENABLE_CIRCUIT_BREAKER", "true").lower() == "true"
        config.retry_max_attempts = int(
            os.getenv("ORCHESTRATION_RETRY_ATTEMPTS", config.retry_max_attempts)
        )
        
        # Resource Limits
        config.max_active_workflows = int(
            os.getenv("ORCHESTRATION_MAX_WORKFLOWS", config.max_active_workflows)
        )
        config.max_total_agents = int(
            os.getenv("ORCHESTRATION_MAX_TOTAL_AGENTS", config.max_total_agents)
        )
        
        logger.info(f"Orchestration configuration loaded from environment")
        return config
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "OrchestrationConfig":
        """Load configuration from dictionary"""
        config = cls()
        for key, value in config_dict.items():
            if hasattr(config, key):
                setattr(config, key, value)
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            field.name: getattr(self, field.name)
            for field in self.__dataclass_fields__.values()
        }
    
    def validate(self) -> bool:
        """Validate configuration values"""
        errors = []
        
        if self.max_specialist_agents_per_pool < 1:
            errors.append("max_specialist_agents_per_pool must be >= 1")
        
        if self.max_concurrent_tasks_per_agent < 1:
            errors.append("max_concurrent_tasks_per_agent must be >= 1")
        
        if self.quality_gate_threshold < 0 or self.quality_gate_threshold > 1:
            errors.append("quality_gate_threshold must be between 0 and 1")
        
        if self.max_active_workflows < 1:
            errors.append("max_active_workflows must be >= 1")
        
        if errors:
            logger.error(f"Configuration validation failed: {errors}")
            return False
        
        return True

# Global configuration instance
_global_config: Optional[OrchestrationConfig] = None

def get_config() -> OrchestrationConfig:
    """Get global orchestration configuration"""
    global _global_config
    if _global_config is None:
        _global_config = OrchestrationConfig.from_env()
        if not _global_config.validate():
            logger.warning("Configuration validation failed, using defaults")
    return _global_config

def set_config(config: OrchestrationConfig):
    """Set global orchestration configuration"""
    global _global_config
    if config.validate():
        _global_config = config
        logger.info("Orchestration configuration updated")
    else:
        logger.error("Failed to set configuration: validation failed")
