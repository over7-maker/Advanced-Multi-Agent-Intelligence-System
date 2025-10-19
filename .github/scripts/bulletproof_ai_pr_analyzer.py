#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
Bulletproof AI PR Analyzer - Phase 2
Comprehensive PR analysis using real AI providers with bulletproof validation

Security hardened with input validation, secure subprocess calls, and sanitized logging.
Enhanced with improved project root finding and structured logging.
"""

# Standard library imports
import asyncio
import json
import logging
import logging.config
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Dict, List, Optional

# Third-party imports
import tenacity

# Constants
MAX_ENV_LENGTH = 64
VALID_LOG_LEVELS = frozenset({'CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'})


def safe_getenv(key: str, default: str, max_len: int = 64, allowed: frozenset = None) -> str:
    """Safely get environment variable with validation and sanitization."""
    value = os.getenv(key, default).strip()
    if len(value) > max_len or (allowed and value not in allowed):
        return default
    # Sanitize input to prevent injection
    value = re.sub(r'[^A-Z]', '', value.upper())
    return value if value in (allowed or {}) else default


def _find_project_root(start_path: Path = None) -> Path:
    """Find project root by walking up until .git directory is found."""
    current = start_path or Path(__file__).resolve()
    for _ in range(10):
        if (current / ".git").exists():
            return current
        if current.parent == current:
            break
        current = current.parent
    raise RuntimeError("Project root with .git not found within 10 levels")


def configure_logging() -> logging.Logger:
    """Configure logging once and return a module-specific logger.
    - Validates LOG_LEVEL via whitelist
    - Configures rotating file + console handlers
    - Uses structured formatter
    - Idempotent: won't duplicate handlers if already configured
    """
    # Check if already configured to prevent duplicate handlers
    logger = logging.getLogger('bulletproof_ai_pr_analyzer')
    if logger.handlers:
        return logger
    
    # Read, normalize, validate
    input_log_level = safe_getenv('LOG_LEVEL', 'INFO', MAX_ENV_LENGTH, VALID_LOG_LEVELS)
    
    # Safe level resolution
    try:
        level = getattr(logging, input_log_level)
    except AttributeError:
        level = logging.INFO

    # Create logs directory
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / 'bulletproof_ai_pr_analyzer.log'

    # Use dictConfig for structured logging configuration
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'structured': {
                'format': '%(asctime)s.%(msecs)03d | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': input_log_level,
                'formatter': 'structured',
                'stream': 'ext://sys.stderr'
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': str(log_file),
                'maxBytes': 10485760,  # 10 MB
                'backupCount': 5,
                'level': input_log_level,
                'formatter': 'structured',
                'encoding': 'utf-8'
            }
        },
        'loggers': {
            'bulletproof_ai_pr_analyzer': {
                'level': input_log_level,
                'handlers': ['console', 'file'],
                'propagate': False
            }
        },
        'root': {
            'level': input_log_level,
            'handlers': ['console', 'file']
        }
    }

    # Apply configuration
    logging.config.dictConfig(logging_config)
    
    return logging.getLogger('bulletproof_ai_pr_analyzer')


logger = configure_logging()

# Setup project root and paths
try:
    PROJECT_ROOT = _find_project_root()
    logger.info(f"Project root found: {PROJECT_ROOT}")
    
    # Add project root to sys.path if not already present
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
        logger.debug(f"Added project root to sys.path: {PROJECT_ROOT}")
except RuntimeError as e:
    logger.warning(f"Could not find project root: {e}")
    PROJECT_ROOT = Path(__file__).parent.parent
    logger.info(f"Using fallback project root: {PROJECT_ROOT}")

# Import enhanced services with graceful fallback
try:
    from src.amas.services.circuit_breaker_service import (
        get_circuit_breaker_service, CircuitBreakerConfig,
        CircuitBreakerOpenException, CircuitBreakerTimeoutException,
    )
    from src.amas.services.error_recovery_service import (
        get_error_recovery_service, ErrorContext, ErrorSeverity,
    )
    from src.amas.errors.error_handling import (
        AMASException, ValidationError, InternalError, ExternalServiceError,
        TimeoutError as AMASTimeoutError, SecurityError,
    )
    ENHANCED_ERROR_HANDLING = True
    logger.info("Enhanced error handling services loaded successfully")
except ImportError as e:
    ENHANCED_ERROR_HANDLING = False
    class AMASException(Exception):
        def __init__(self, message: str, safe_message: str = None, details: str = None):
            super().__init__(safe_message or message)
            self.details = details
            self.original_message = message
    class ValidationError(AMASException):
        def __init__(self, message: str, safe_message: str = "Invalid input provided"): super().__init__(message, safe_message)
    class InternalError(AMASException):
        def __init__(self, message: str, safe_message: str = "Internal system error occurred"): super().__init__(message, safe_message)
    class ExternalServiceError(AMASException):
        def __init__(self, message: str, safe_message: str = "External service temporarily unavailable"): super().__init__(message, safe_message)
    class SecurityError(AMASException):
        def __init__(self, message: str, safe_message: str = "Security violation detected"): super().__init__(message, safe_message)
    class AMASTimeoutError(AMASException):
        def __init__(self, message: str, safe_message: str = "Operation timed out"): super().__init__(message, safe_message)
    logger.warning("Enhanced error handling not available, using basic error handling: %s", e)

# Project root resolution using pathlib
SCRIPT_DIR = str(Path(__file__).resolve().parent)

def _find_project_root(start: Path = None) -> Path:
    """Locate project root via .git/pyproject with depth limit; return safe fallback."""
    current = (start or Path(__file__).parent).resolve()
    for _ in range(10):
        if (current / '.git').exists() or (current / 'pyproject.toml').exists():
            logger.info("Found project root: %s", current)
            return current
        if current.parent == current:
            break
        current = current.parent
    fallback = Path(__file__).resolve().parent.parent.parent
    if (fallback / '.git').exists() or (fallback / 'pyproject.toml').exists():
        logger.info("Using fallback project root: %s", fallback)
        return fallback
    final_fallback = Path(__file__).resolve().parent.parent
    logger.warning("Using final fallback project root: %s", final_fallback)
    return final_fallback

def _setup_project_paths() -> str:
    try:
        from src.amas.utils.project_root import find_project_root, add_project_root_to_path
        project_root: str = find_project_root(SCRIPT_DIR)
        add_project_root_to_path(project_root)
        logger.info("Using enhanced project root finding: %s", project_root)
        return project_root
    except ImportError:
        project_root = str(_find_project_root())
        if SCRIPT_DIR not in sys.path:
            sys.path.insert(0, SCRIPT_DIR)
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        logger.info("Using legacy project root finding: %s", project_root)
        return project_root

PROJECT_ROOT = _setup_project_paths()

try:
    from standalone_universal_ai_manager import get_manager
except ImportError as e:
    logger.critical("Could not import Universal AI Manager: %s", e)
    logger.critical("Current sys.path: %s", sys.path)
    logger.critical("Looking for module in: %s", PROJECT_ROOT)
    sys.exit(1)

# Prefer enhanced logging service, fallback to basic already configured
try:
    from src.amas.services.enhanced_logging_service import (
        configure_logging as enhanced_configure_logging,
        get_logger as enhanced_get_logger,
        LoggingConfig, LogLevel, LogFormat, SecurityLevel,
    )
    env_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    env_fmt = os.getenv('LOG_FORMAT', 'json').lower()
    env_sec = os.getenv('LOG_SECURITY_LEVEL', 'medium').lower()
    cfg = LoggingConfig(
        level=LogLevel(env_level if env_level in VALID_LOG_LEVELS else 'INFO'),
        format=LogFormat(env_fmt if env_fmt in {'json','text','structured'} else 'json'),
        security_level=SecurityLevel(env_sec if env_sec in {'low','medium','high','maximum'} else 'medium'),
        enable_console=True, enable_correlation=True, enable_metrics=True,
        enable_audit=True, enable_performance=True, include_stack_traces=True,
    )
    enhanced_configure_logging(cfg)
    logger = enhanced_get_logger(__name__, 'bulletproof_ai_analyzer')
    logger.info("Enhanced logging service configured successfully")
except ImportError:
    logger.debug("Enhanced logging not available; using basic logging")

SENSITIVE_VARS = {"GITHUB_TOKEN", "API_KEY", "SECRET", "PASSWORD", "TOKEN"}

def sanitize_env(env: Dict[str, str]) -> Dict[str, str]:
    return {k: "<redacted>" if any(s in k.upper() for s in SENSITIVE_VARS) else v for k, v in env.items()}

class BulletproofAIAnalyzer:
    def __init__(self) -> None:
        self.ai_manager = self._get_ai_manager_with_retry()
        self._load_and_validate_environment()
        self.verification_results = {
            "real_ai_verified": False,
            "bulletproof_validated": False,
            "provider_used": None,
            "response_time": 0.0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "analysis_types": [],
        }
        if ENHANCED_ERROR_HANDLING:
            self.circuit_breaker_service = get_circuit_breaker_service()
            self.error_recovery_service = get_error_recovery_service()
            self._setup_circuit_breakers()
        else:
            self.circuit_breaker_service = None
            self.error_recovery_service = None

    def _get_ai_manager_with_retry(self) -> Any:
        @tenacity.retry(stop=tenacity.stop_after_attempt(3),
                        wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
                        retry=tenacity.retry_if_exception_type(Exception))
        def _retry_get_manager():
            return get_manager()
        try:
            return _retry_get_manager()
        except Exception as e:
            logger.critical("Failed to initialize AI manager after retries: %s", e)
            sys.exit(1)

    def _load_and_validate_environment(self) -> None:
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.repo_name = os.getenv("REPO_NAME")
        self.pr_number = os.getenv("PR_NUMBER")
        self.commit_sha = os.getenv("COMMIT_SHA")
        self.event_name = os.getenv("EVENT_NAME")
        self.artifacts_dir = os.getenv("ARTIFACTS_DIR", "artifacts")
        required = {"GITHUB_TOKEN": self.github_token, "REPO_NAME": self.repo_name}
        missing = [k for k, v in required.items() if not v]
        if missing:
            logger.error("Missing required environment variables: %s", ", ".join(missing))
            sys.exit(1)
        if self.pr_number:
            try:
                self.pr_number = int(self.pr_number)
            except (TypeError, ValueError):
                logger.error("PR_NUMBER must be an integer")
                sys.exit(1)
        if self.commit_sha and not re.match(r'^[a-f0-9]{40}$', self.commit_sha):
            logger.error("COMMIT_SHA must be a valid 40-character Git SHA")
            sys.exit(1)
        os.makedirs(self.artifacts_dir, exist_ok=True)
        logger.debug("Environment loaded: REPO_NAME=%s, PR_NUMBER=%s", self.repo_name, self.pr_number)

    def _setup_circuit_breakers(self):
        if not ENHANCED_ERROR_HANDLING:
            return
        ai_cfg = CircuitBreakerConfig(failure_threshold=5, recovery_timeout=60.0, success_threshold=3, timeout=30.0, expected_exceptions=[Exception])
        git_cfg = CircuitBreakerConfig(failure_threshold=3, recovery_timeout=30.0, success_threshold=2, timeout=10.0, expected_exceptions=[Exception])
        file_cfg = CircuitBreakerConfig(failure_threshold=5, recovery_timeout=30.0, success_threshold=3, timeout=5.0, expected_exceptions=[Exception])
        self.circuit_breaker_service.create_breaker("ai_api", ai_cfg)
        self.circuit_breaker_service.create_breaker("git_operations", git_cfg)
        self.circuit_breaker_service.create_breaker("file_operations", file_cfg)

    @tenacity.retry(stop=tenacity.stop_after_attempt(3),
                    wait=tenacity.wait_exponential(multiplier=1, min=2, max=8),
                    retry=tenacity.retry_if_exception_type((subprocess.CalledProcessError, OSError)))
    async def get_pr_diff(self) -> str:
        try:
            if ENHANCED_ERROR_HANDLING:
                breaker = self.circuit_breaker_service.get_breaker("git_operations")
                if breaker:
                    return await breaker.call(self._get_pr_diff_impl)
            return await self._get_pr_diff_impl()
        except (CircuitBreakerOpenException, CircuitBreakerTimeoutException) as e:
            logger.error("Circuit breaker prevented git diff operation: %s", e)
            return ""
        except Exception as e:
            logger.error("Error getting diff: %s", e)
            if ENHANCED_ERROR_HANDLING:
                await self._handle_git_error(e, "get_pr_diff")
            return ""

    async def _get_pr_diff_impl(self) -> str:
        cmd = ["git", "diff", "origin/main...HEAD"] if self.pr_number else ["git", "diff", "HEAD~1", "HEAD"]
        process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            raise Exception(f"Git diff failed: {stderr.decode()}")
        return stdout.decode()

    async def get_changed_files(self) -> List[str]:
        try:
            if ENHANCED_ERROR_HANDLING:
                breaker = self.circuit_breaker_service.get_breaker("git_operations")
                if breaker:
                    return await breaker.call(self._get_changed_files_impl)
            return await self._get_changed_files_impl()
        except (CircuitBreakerOpenException, CircuitBreakerTimeoutException) as e:
            logger.error("Circuit breaker prevented git operations: %s", e)
            return []
        except Exception as e:
            logger.error("Error getting changed files: %s", e)
            if ENHANCED_ERROR_HANDLING:
                await self._handle_git_error(e, "get_changed_files")
            return []

    async def _get_changed_files_impl(self) -> List[str]:
        cmd = ["git", "diff", "--name-only", "origin/main...HEAD"] if self.pr_number else ["git", "diff", "--name-only", "HEAD~1", "HEAD"]
        process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            raise Exception(f"Git diff --name-only failed: {stderr.decode()}")
        return [f.strip() for f in stdout.decode().split("\n") if f.strip()]

    async def calculate_diff_stats(self, diff: str) -> Dict[str, int]:
        additions = len([line for line in diff.split("\n") if line.startswith("+")])
        deletions = len([line for line in diff.split("\n") if line.startswith("-")])
        files_changed = len(await self.get_changed_files())
        return {"additions": additions, "deletions": deletions, "files_changed": files_changed}

    @tenacity.retry(stop=tenacity.stop_after_attempt(3),
                    wait=tenacity.wait_exponential(multiplier=1, min=2, max=10),
                    retry=tenacity.retry_if_exception_type((Exception,)))
    async def run_ai_analysis(self, analysis_type: str, prompt: str) -> Dict[str, Any]:
        try:
            if ENHANCED_ERROR_HANDLING:
                breaker = self.circuit_breaker_service.get_breaker("ai_api")
                if breaker:
                    return await breaker.call(self._run_ai_analysis_impl, analysis_type, prompt)
            return await self._run_ai_analysis_impl(analysis_type, prompt)
        except (CircuitBreakerOpenException, CircuitBreakerTimeoutException) as e:
            logger.error("Circuit breaker prevented AI analysis: %s", e)
            return {"success": False, "error": f"AI service unavailable: {e}", "timestamp": datetime.now(timezone.utc).isoformat()}
        except Exception as e:
            logger.error("Error in AI analysis: %s", e)
            if ENHANCED_ERROR_HANDLING:
                await self._handle_ai_error(e, analysis_type)
            return {"success": False, "error": str(e), "timestamp": datetime.now(timezone.utc).isoformat()}

    async def _run_ai_analysis_impl(self, analysis_type: str, prompt: str) -> Dict[str, Any]:
        max_retries, retry_delay = 3, 1.0
        for attempt in range(max_retries):
            try:
                logger.info("Running %s analysis (attempt %d/%d)", analysis_type, attempt + 1, max_retries)
                result = await self.ai_manager.generate(
                    prompt=prompt,
                    system_prompt="You are an expert code reviewer and security analyst. Provide detailed, actionable feedback in professional markdown format.",
                    strategy="intelligent",
                    max_tokens=4000,
                    temperature=0.3,
                )
                if result and result.get("success", False):
                    self.verification_results.update({
                        "real_ai_verified": True,
                        "bulletproof_validated": True,
                        "provider_used": result.get("provider_name", "Unknown"),
                        "response_time": result.get("response_time", 0.0),
                    })
                    self.verification_results["analysis_types"].append(analysis_type)
                    return {
                        "success": True,
                        "analysis": result.get("content", ""),
                        "provider": result.get("provider_name", "Unknown"),
                        "response_time": result.get("response_time", 0.0),
                        "tokens_used": result.get("tokens_used", 0),
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                err = result.get('error', 'Unknown error') if result else 'No result returned'
                logger.warning("%s analysis attempt %d failed: %s", analysis_type, attempt + 1, err)
            except Exception as e:
                logger.warning("Exception in %s analysis attempt %d: %s", analysis_type, attempt + 1, e)
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay * (2 ** attempt))
        return {"success": False, "error": "Analysis failed after retries", "timestamp": datetime.now(timezone.utc).isoformat()}

    async def _handle_git_error(self, error: Exception, operation: str):
        if not ENHANCED_ERROR_HANDLING: return
        try:
            context = ErrorContext(error_type="git_error", error_message=str(error), severity=ErrorSeverity.MEDIUM,
                                   component="bulletproof_ai_analyzer", operation=operation, metadata={"error_type": type(error).__name__})
            success = await self.error_recovery_service.handle_error(context)
            logger.info("Recovered from git error in %s" if success else "Failed to recover from git error in %s", operation)
        except Exception as recovery_error:
            logger.error("Error during git error recovery: %s", recovery_error)

    async def _handle_ai_error(self, error: Exception, analysis_type: str):
        if not ENHANCED_ERROR_HANDLING: return
        try:
            context = ErrorContext(error_type="ai_analysis_error", error_message=str(error), severity=ErrorSeverity.HIGH,
                                   component="bulletproof_ai_analyzer", operation=f"ai_analysis_{analysis_type}", metadata={"error_type": type(error).__name__, "analysis_type": analysis_type})
            success = await self.error_recovery_service.handle_error(context)
            logger.info("Recovered from AI error in %s" if success else "Failed to recover from AI error in %s", analysis_type)
        except Exception as recovery_error:
            logger.error("Error during AI error recovery: %s", recovery_error)

    async def run_comprehensive_analysis(self) -> str:
        logger.info("Starting Bulletproof AI PR Analysis...")
        diff = await self.get_pr_diff()
        changed_files = await self.get_changed_files()
        diff_stats = await self.calculate_diff_stats(diff)
        if not diff and not changed_files:
            logger.warning("No changes detected")
            return ""
        analyses: Dict[str, Any] = {}
        tasks = [
            ("security", self._analysis_wrapper(self.analyze_security, diff, changed_files)),
            ("performance", self._analysis_wrapper(self.analyze_performance, diff, changed_files)),
            ("observability", self._analysis_wrapper(self.analyze_observability, diff, changed_files)),
            ("reliability", self._analysis_wrapper(self.analyze_reliability, diff, changed_files)),
        ]
        for name, coro in tasks:
            try:
                analyses[name] = await asyncio.wait_for(coro, timeout=300.0)
            except asyncio.TimeoutError:
                analyses[name] = {"success": False, "error": f"{name} analysis timed out after 5 minutes", "timestamp": datetime.now(timezone.utc).isoformat()}
        try:
            analyses["documentation"] = await asyncio.wait_for(self.generate_documentation(analyses), timeout=300.0)
        except asyncio.TimeoutError:
            analyses["documentation"] = {"success": False, "error": "Documentation generation timed out after 5 minutes", "timestamp": datetime.now(timezone.utc).isoformat()}
        report = self.generate_bulletproof_report(analyses, diff_stats)
        os.makedirs(self.artifacts_dir, exist_ok=True)
        with open(os.path.join(self.artifacts_dir, "bulletproof_analysis_report.md"), "w") as f:
            f.write(report)
        self.save_verification_results()
        logger.info("Bulletproof analysis report saved to %s", os.path.join(self.artifacts_dir, "bulletproof_analysis_report.md"))
        return report

    async def _analysis_wrapper(self, func, diff, changed_files):
        return await func(diff, changed_files)

async def main() -> None:
    try:
        analyzer = BulletproofAIAnalyzer()
        await analyzer.run_comprehensive_analysis()
    except Exception as e:
        logger.error("Bulletproof AI analysis failed: %s", e)
        os.makedirs("artifacts", exist_ok=True)
        with open("artifacts/bulletproof_analysis_report.md", "w") as f:
            f.write(f"# ❌ Bulletproof AI Analysis Error\n\n``""\n{e}\n``""\n")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
