# src/utils/logging_config.py (STRUCTURED LOGGING CONFIGURATION)
import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict
import os

class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging
    
    Outputs logs in JSON format for log aggregation systems (Loki, ELK, etc.)
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON
        
        Args:
            record: Log record to format
            
        Returns:
            JSON string
        """
        
        # Generate correlation ID if not present
        correlation_id = getattr(record, "correlation_id", None)
        if not correlation_id:
            import uuid
            correlation_id = str(uuid.uuid4())[:8]
        
        # Base log data
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "correlation_id": correlation_id,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields from record
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        
        if hasattr(record, "task_id"):
            log_data["task_id"] = record.task_id
        
        if hasattr(record, "agent_id"):
            log_data["agent_id"] = record.agent_id
        
        # Add any extra fields
        for key, value in record.__dict__.items():
            if key not in [
                "name", "msg", "args", "created", "filename", "funcName",
                "levelname", "levelno", "lineno", "module", "msecs",
                "message", "pathname", "process", "processName", "relativeCreated",
                "thread", "threadName", "exc_info", "exc_text", "stack_info"
            ]:
                if not key.startswith("_"):
                    log_data[key] = value
        
        return json.dumps(log_data, default=str)


def configure_logging(
    level: str = None,
    json_format: bool = None,
    log_file: str = None
):
    """
    Configure application logging
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: Use JSON formatting (default: True in production)
        log_file: Optional log file path
    """
    
    # Get log level from env or parameter
    if level is None:
        level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    log_level = getattr(logging, level, logging.INFO)
    
    # Determine JSON format
    if json_format is None:
        json_format = os.getenv("LOG_JSON", "true").lower() == "true"
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Create formatter
    if json_format:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (if specified or if LOG_FILE env var is set)
    log_file_path = log_file or os.getenv("LOG_FILE", None)
    if log_file_path:
        from logging.handlers import RotatingFileHandler
        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(log_file_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_file_path,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    elif os.getenv("LOG_TO_FILE", "false").lower() == "true":
        # Default log file if LOG_TO_FILE is enabled
        log_dir = os.getenv("LOG_DIR", "logs")
        os.makedirs(log_dir, exist_ok=True)
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, "amas.log"),
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Set levels for noisy libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    
    logging.info(f"Logging configured: level={level}, json={json_format}")


def setup_logging(environment: str = None):
    """
    Setup logging for the application (alias for configure_logging)
    
    Args:
        environment: Environment name (production, development, testing)
    """
    # Determine JSON format based on environment
    json_format = True
    if environment:
        json_format = environment.lower() in ("production", "prod")
    
    configure_logging(json_format=json_format)


# Alias for backward compatibility
JsonFormatter = JSONFormatter


def get_logger(name: str) -> logging.Logger:
    """
    Get logger with context enrichment support
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# Context manager for adding context to logs
class LogContext:
    """
    Context manager to add context to all logs within scope
    """
    
    def __init__(self, **context):
        self.context = context
        self.old_factory = logging.getLogRecordFactory()
    
    def __enter__(self):
        def record_factory(*args, **kwargs):
            record = self.old_factory(*args, **kwargs)
            for key, value in self.context.items():
                setattr(record, key, value)
            return record
        
        logging.setLogRecordFactory(record_factory)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.setLogRecordFactory(self.old_factory)

