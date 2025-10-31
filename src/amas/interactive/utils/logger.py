"""
AMAS Interactive Logger - Advanced Logging System
Advanced Multi-Agent Intelligence System - Interactive Mode

This module provides comprehensive logging capabilities for the AMAS
interactive system with structured logging, performance tracking, and
enhanced console output.
"""

import json
import logging
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Rich for enhanced console output
from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table


@dataclass
class LogEntry:
    """Log entry data structure"""

    timestamp: datetime
    level: str
    message: str
    module: str
    function: str
    line_number: int
    session_id: Optional[str] = None
    task_id: Optional[str] = None
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class InteractiveLogger:
    """Advanced Interactive Logging System"""

    def __init__(self, name: str = "amas_interactive", log_level: str = "INFO"):
        self.name = name
        self.console = Console()

        # Setup logging directory
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)

        # Log files
        self.main_log_file = self.log_dir / "interactive.log"
        self.error_log_file = self.log_dir / "errors.log"
        self.performance_log_file = self.log_dir / "performance.log"
        self.audit_log_file = self.log_dir / "audit.log"

        # Initialize logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))

        # Clear existing handlers
        self.logger.handlers.clear()

        # Setup handlers
        self._setup_handlers()

        # Performance tracking
        self.performance_metrics = {
            "total_logs": 0,
            "error_count": 0,
            "warning_count": 0,
            "info_count": 0,
            "debug_count": 0,
            "average_log_size": 0.0,
        }

        # Session tracking
        self.current_session = None
        self.session_logs = []

    def _setup_handlers(self):
        """Setup logging handlers"""
        # Console handler with Rich formatting
        console_handler = RichHandler(
            console=self.console,
            show_time=True,
            show_path=True,
            enable_link_path=True,
            markup=True,
        )
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%H:%M:%S"
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # Main log file handler
        main_handler = logging.FileHandler(self.main_log_file)
        main_handler.setLevel(logging.DEBUG)
        main_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
        )
        main_handler.setFormatter(main_formatter)
        self.logger.addHandler(main_handler)

        # Error log file handler
        error_handler = logging.FileHandler(self.error_log_file)
        error_handler.setLevel(logging.ERROR)
        error_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s\n%(pathname)s:%(lineno)d"
        )
        error_handler.setFormatter(error_formatter)
        self.logger.addHandler(error_handler)

        # Performance log file handler
        performance_handler = logging.FileHandler(self.performance_log_file)
        performance_handler.setLevel(logging.INFO)
        performance_formatter = logging.Formatter("%(asctime)s - %(message)s")
        performance_handler.setFormatter(performance_formatter)
        self.logger.addHandler(performance_handler)

    def set_session(self, session_id: str):
        """Set current session ID"""
        self.current_session = session_id
        self.session_logs = []

    def _create_log_entry(self, level: str, message: str, **kwargs) -> LogEntry:
        """Create a log entry"""
        # Get caller information
        frame = sys._getframe(2)
        module = frame.f_globals.get("__name__", "unknown")
        function = frame.f_code.co_name
        line_number = frame.f_lineno

        return LogEntry(
            timestamp=datetime.now(),
            level=level.upper(),
            message=message,
            module=module,
            function=function,
            line_number=line_number,
            session_id=self.current_session,
            **kwargs,
        )

    def _log_entry(self, level: str, message: str, **kwargs):
        """Internal logging method"""
        log_entry = self._create_log_entry(level, message, **kwargs)

        # Add to session logs
        if self.current_session:
            self.session_logs.append(log_entry)

        # Update performance metrics
        self.performance_metrics["total_logs"] += 1
        self.performance_metrics[f"{level.lower()}_count"] += 1

        # Calculate average log size
        log_size = len(message)
        total_logs = self.performance_metrics["total_logs"]
        current_avg = self.performance_metrics["average_log_size"]
        self.performance_metrics["average_log_size"] = (
            current_avg * (total_logs - 1) + log_size
        ) / total_logs

        # Log to appropriate handler
        if level.upper() == "ERROR":
            self.logger.error(message, extra={"log_entry": log_entry})
        elif level.upper() == "WARNING":
            self.logger.warning(message, extra={"log_entry": log_entry})
        elif level.upper() == "INFO":
            self.logger.info(message, extra={"log_entry": log_entry})
        elif level.upper() == "DEBUG":
            self.logger.debug(message, extra={"log_entry": log_entry})
        else:
            self.logger.info(message, extra={"log_entry": log_entry})

    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self._log_entry("DEBUG", message, **kwargs)

    def info(self, message: str, **kwargs):
        """Log info message"""
        self._log_entry("INFO", message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self._log_entry("WARNING", message, **kwargs)

    def error(self, message: str, **kwargs):
        """Log error message"""
        self._log_entry("ERROR", message, **kwargs)

    def critical(self, message: str, **kwargs):
        """Log critical message"""
        self._log_entry("CRITICAL", message, **kwargs)

    def task_start(self, task_id: str, task_type: str, target: str, **kwargs):
        """Log task start"""
        message = f"Task started: {task_type} on {target}"
        self._log_entry("INFO", message, task_id=task_id, **kwargs)

    def task_complete(self, task_id: str, task_type: str, duration: float, **kwargs):
        """Log task completion"""
        message = f"Task completed: {task_type} in {duration:.2f}s"
        self._log_entry("INFO", message, task_id=task_id, **kwargs)

    def task_failed(self, task_id: str, task_type: str, error: str, **kwargs):
        """Log task failure"""
        message = f"Task failed: {task_type} - {error}"
        self._log_entry("ERROR", message, task_id=task_id, **kwargs)

    def agent_activity(
        self, agent_id: str, action: str, task_id: Optional[str] = None, **kwargs
    ):
        """Log agent activity"""
        message = f"Agent {agent_id}: {action}"
        self._log_entry("INFO", message, task_id=task_id, **kwargs)

    def user_action(self, action: str, user_id: Optional[str] = None, **kwargs):
        """Log user action"""
        message = f"User action: {action}"
        self._log_entry("INFO", message, user_id=user_id, **kwargs)

    def system_event(self, event: str, **kwargs):
        """Log system event"""
        message = f"System event: {event}"
        self._log_entry("INFO", message, **kwargs)

    def performance_metric(
        self, metric_name: str, value: Union[int, float], unit: str = "", **kwargs
    ):
        """Log performance metric"""
        message = f"Performance: {metric_name} = {value}{unit}"
        self._log_entry("INFO", message, **kwargs)

        # Also log to performance file
        perf_logger = logging.getLogger(f"{self.name}.performance")
        perf_logger.info(f"{metric_name}: {value}{unit}")

    def security_event(self, event: str, severity: str = "medium", **kwargs):
        """Log security event"""
        message = f"Security event [{severity}]: {event}"
        level = "WARNING" if severity == "high" else "INFO"
        self._log_entry(level, message, **kwargs)

        # Log to audit file
        audit_logger = logging.getLogger(f"{self.name}.audit")
        audit_logger.info(f"SECURITY: {event} [{severity}]")

    def exception(self, message: str, exception: Exception, **kwargs):
        """Log exception with traceback"""
        error_message = f"{message}: {str(exception)}"
        self._log_entry("ERROR", error_message, **kwargs)

        # Log traceback to error file
        error_logger = logging.getLogger(f"{self.name}.error")
        error_logger.error(f"{message}: {str(exception)}", exc_info=True)

    def command_processed(self, command: str, intent: str, confidence: float, **kwargs):
        """Log command processing"""
        message = f"Command processed: '{command}' -> {intent} ({confidence:.1%})"
        self._log_entry("INFO", message, **kwargs)

    def configuration_change(self, config_type: str, changes: Dict[str, Any], **kwargs):
        """Log configuration changes"""
        changes_str = ", ".join([f"{k}={v}" for k, v in changes.items()])
        message = f"Configuration changed [{config_type}]: {changes_str}"
        self._log_entry("INFO", message, **kwargs)

    def get_session_logs(self) -> List[LogEntry]:
        """Get logs for current session"""
        return self.session_logs.copy()

    def export_session_logs(self, file_path: str):
        """Export session logs to file"""
        try:
            logs_data = []
            for log_entry in self.session_logs:
                log_dict = asdict(log_entry)
                # Convert datetime to string
                log_dict["timestamp"] = log_entry.timestamp.isoformat()
                logs_data.append(log_dict)

            with open(file_path, "w") as f:
                json.dump(logs_data, f, indent=2)

            self.console.print(f"✅ Session logs exported to {file_path}", style="green")

        except Exception as e:
            self.console.print(f"❌ Failed to export session logs: {e}", style="red")

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get logging performance metrics"""
        return self.performance_metrics.copy()

    def display_log_summary(self):
        """Display logging summary"""
        metrics = self.performance_metrics

        # Create summary table
        table = Table(title="📊 Logging Summary")
        table.add_column("Metric", style="cyan", width=20)
        table.add_column("Value", style="green")

        table.add_row("Total Logs", str(metrics["total_logs"]))
        table.add_row("Info Logs", str(metrics["info_count"]))
        table.add_row("Warning Logs", str(metrics["warning_count"]))
        table.add_row("Error Logs", str(metrics["error_count"]))
        table.add_row("Debug Logs", str(metrics["debug_count"]))
        table.add_row("Average Log Size", f"{metrics['average_log_size']:.1f} chars")

        # Session info
        if self.current_session:
            table.add_row("Current Session", self.current_session)
            table.add_row("Session Logs", str(len(self.session_logs)))

        self.console.print(table)

        # Log file info
        log_files = [
            ("Main Log", self.main_log_file),
            ("Error Log", self.error_log_file),
            ("Performance Log", self.performance_log_file),
            ("Audit Log", self.audit_log_file),
        ]

        files_table = Table(title="📁 Log Files")
        files_table.add_column("Type", style="cyan", width=15)
        files_table.add_column("Path", style="green")
        files_table.add_column("Size", style="yellow")
        files_table.add_column("Exists", style="blue")

        for log_type, log_file in log_files:
            exists = "✅" if log_file.exists() else "❌"
            size = (
                f"{log_file.stat().st_size / 1024:.1f} KB"
                if log_file.exists()
                else "N/A"
            )

            files_table.add_row(log_type, str(log_file), size, exists)

        self.console.print(files_table)

    def clear_old_logs(self, days: int = 30):
        """Clear log files older than specified days"""
        try:
            from datetime import timedelta

            cutoff_date = datetime.now() - timedelta(days=days)
            cleared_count = 0

            for log_file in [
                self.main_log_file,
                self.error_log_file,
                self.performance_log_file,
                self.audit_log_file,
            ]:
                if log_file.exists():
                    file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                    if file_time < cutoff_date:
                        log_file.unlink()
                        cleared_count += 1

            self.console.print(
                f"✅ Cleared {cleared_count} old log files", style="green"
            )

        except Exception as e:
            self.console.print(f"❌ Failed to clear old logs: {e}", style="red")

    def set_log_level(self, level: str):
        """Set logging level"""
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }

        if level.upper() in level_map:
            self.logger.setLevel(level_map[level.upper()])
            self.console.print(f"✅ Log level set to {level.upper()}", style="green")
        else:
            self.console.print(f"❌ Invalid log level: {level}", style="red")

    def enable_console_output(self, enabled: bool = True):
        """Enable or disable console output"""
        for handler in self.logger.handlers:
            if isinstance(handler, RichHandler):
                handler.setLevel(logging.INFO if enabled else logging.CRITICAL + 1)

        status = "enabled" if enabled else "disabled"
        self.console.print(f"✅ Console output {status}", style="green")
