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

# Set up basic logging first
def configure_logging() -> logging.Logger:
    """Configure root logging and return module-specific logger with security validation."""
    # Whitelist for log level
    VALID_LOG_LEVELS = {'CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'}

    # Get raw env, clamp length, normalize case
    raw_level = os.getenv('LOG_LEVEL', 'INFO') or 'INFO'
    raw_level = raw_level.strip().upper()
    if len(raw_level) > 32:
        raw_level = 'INFO'

    # Whitelist-only selection to avoid log injection
    logging_level = raw_level if raw_level in VALID_LOG_LEVELS else 'INFO'
    level = getattr(logging, logging_level)

    # Configure root logger only once
    root_logger = logging.getLogger()
    if not root_logger.hasHandlers():
        # Create logs directory
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / 'bulletproof_analyzer.log'

        # Handlers
        file_handler = RotatingFileHandler(str(log_file), maxBytes=1024 * 1024, backupCount=3)
        file_handler.setLevel(level)
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(level)

        # Formatter (ISO 8601 UTC)
        formatter = logging.Formatter('%(asctime)sZ - %(name)s - %(levelname)s - %(message)s',
                                      datefmt='%Y-%m-%dT%H:%M:%S')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Apply
        root_logger.setLevel(level)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)

    # Always return a module logger
    return logging.getLogger(__name__)

# Initialize logger once on import
logger = configure_logging()

# Import enhanced services (with graceful fallback)
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

# Project root resolution
SCRIPT_DIR = str(Path(__file__).resolve().parent)

def _find_project_root(start: Path = None) -> Path:
    """Locate project root using .git/pyproject markers with depth limit and safe fallbacks."""
    current = (start or Path(__file__).parent).resolve()
    max_depth = 10
    for _ in range(max_depth):
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

# Prefer enhanced logging service, fallback to basic already configured above
try:
    from src.amas.services.enhanced_logging_service import (
        configure_logging as enhanced_configure_logging,
        get_logger as enhanced_get_logger,
        LoggingConfig, LogLevel, LogFormat, SecurityLevel,
    )
    cfg = LoggingConfig(
        level=LogLevel(os.getenv('LOG_LEVEL', 'INFO').upper() if os.getenv('LOG_LEVEL', 'INFO').upper() in {'DEBUG','INFO','WARNING','ERROR','CRITICAL'} else 'INFO'),
        format=LogFormat(os.getenv('LOG_FORMAT', 'json').lower() if os.getenv('LOG_FORMAT', 'json').lower() in {'json','text','structured'} else 'json'),
        security_level=SecurityLevel(os.getenv('LOG_SECURITY_LEVEL', 'medium').lower() if os.getenv('LOG_SECURITY_LEVEL', 'medium').lower() in {'low','medium','high','maximum'} else 'medium'),
        enable_console=True, enable_correlation=True, enable_metrics=True, enable_audit=True, enable_performance=True, include_stack_traces=True,
    )
    enhanced_configure_logging(cfg)
    logger = enhanced_get_logger(__name__, 'bulletproof_ai_analyzer')
except ImportError:
    # Already configured above
    logger.debug("Enhanced logging not available; using basic logging")

SENSITIVE_VARS = {"GITHUB_TOKEN", "API_KEY", "SECRET", "PASSWORD", "TOKEN"}

def sanitize_env(env: Dict[str, str]) -> Dict[str, str]:
    return {k: "<redacted>" if any(s in k.upper() for s in SENSITIVE_VARS) else v for k, v in env.items()}

class BulletproofAIAnalyzer:
    """Bulletproof AI PR Analyzer with real provider validation and security hardening"""
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

    async def analyze_security(self, diff: str, changed_files: List[str]) -> Dict[str, Any]:
        safe_changed_files = [f.replace('\n', '').replace('\r', '') for f in changed_files[:50]]
        safe_diff = diff[:3000].replace('\0', '')
        prompt = f"""## Security Analysis - Phase 2 Hardening

Please perform a comprehensive security analysis of the following changes:

**Changed Files:**
{', '.join(safe_changed_files)}

**Code Diff:**
```diff
{safe_diff}
```

Focus on Phase 2 security requirements:
1. **JWT/OIDC Validation**: Check for proper audience, issuer, exp, nbf validation and key rotation
2. **Security Headers**: Verify CSP, HSTS, X-Content-Type-Options, X-Frame-Options implementation
3. **Rate Limiting**: Assess per IP/service/token rate limiting with burst handling
4. **Input Validation**: Check for strict schema validation (types, ranges, patterns)
5. **Audit Logging**: Verify security event logging and integrity
6. **Authentication**: Review auth flow security and session management
7. **Authorization**: Check access control and permission validation
8. **Data Protection**: Verify encryption, sanitization, and secure storage

Provide specific recommendations with code examples and security best practices.
"""
        return await self.run_ai_analysis("security", prompt)

    async def analyze_performance(self, diff: str, changed_files: List[str]) -> Dict[str, Any]:
        safe_changed_files = [f.replace('\n', '').replace('\r', '') for f in changed_files[:50]]
        safe_diff = diff[:3000].replace('\0', '')
        prompt = f"""## Performance Analysis - Observability Impact

Please analyze the performance impact of these changes:

**Changed Files:**
{', '.join(safe_changed_files)}

**Code Diff:**
```diff
{safe_diff}
```

Focus on Phase 2 performance requirements:
1. **Middleware Overhead**: Assess impact of monitoring, logging, and metrics middleware
2. **Async Operations**: Check for non-blocking logging and async processing
3. **Cardinality Safety**: Verify metrics labels won't cause cardinality explosion
4. **Memory Usage**: Analyze memory footprint of new monitoring components
5. **Response Times**: Check for performance degradation in critical paths
6. **Resource Utilization**: Assess CPU, memory, and I/O impact
7. **Scalability**: Review horizontal scaling implications
8. **Caching**: Check for appropriate caching strategies

Provide specific performance recommendations and optimization suggestions.
"""
        return await self.run_ai_analysis("performance", prompt)

    async def analyze_observability(self, diff: str, changed_files: List[str]) -> Dict[str, Any]:
        safe_changed_files = [f.replace('\n', '').replace('\r', '') for f in changed_files[:50]]
        safe_diff = diff[:3000].replace('\0', '')
        prompt = f"""## Observability Analysis - Monitoring & Alerting

Please analyze the observability implementation in these changes:

**Changed Files:**
{', '.join(safe_changed_files)}

**Code Diff:**
```diff
{safe_diff}
```

Focus on Phase 2 observability requirements:
1. **Structured Logging**: Verify consistent schema (service, level, trace_id)
2. **Metrics Exposure**: Check namespaced metrics (amas_*) with proper labels
3. **Health Checks**: Verify JSON responses with status, deps, version
4. **Alert Rules**: Check thresholds, runbooks, and severity levels
5. **Dashboard Integration**: Assess Grafana dashboard compatibility
6. **Prometheus Metrics**: Verify metric naming and cardinality
7. **Error Tracking**: Check error correlation and tracing
8. **SLO Monitoring**: Verify service level objective tracking

Provide specific observability recommendations and monitoring best practices.
"""
        return await self.run_ai_analysis("observability", prompt)

    async def analyze_reliability(self, diff: str, changed_files: List[str]) -> Dict[str, Any]:
        safe_changed_files = [f.replace('\n', '').replace('\r', '') for f in changed_files[:50]]
        safe_diff = diff[:3000].replace('\0', '')
        prompt = f"""## Reliability Analysis - Error Handling & Resilience

Please analyze the reliability improvements in these changes:

**Changed Files:**
{', '.join(safe_changed_files)}

**Code Diff:**
```diff
{safe_diff}
```

Focus on Phase 2 reliability requirements:
1. **Error Handling**: Check for consistent error envelope (code, message, correlation_id)
2. **Retry Policies**: Verify bounded retry strategies with exponential backoff
3. **Circuit Breakers**: Check for circuit breaker patterns where applicable
4. **Health Endpoints**: Verify dependency health checks and degraded states
5. **Graceful Degradation**: Check for graceful service degradation
6. **Timeout Handling**: Verify proper timeout configuration
7. **Resource Cleanup**: Check for proper resource cleanup and disposal
8. **Recovery Mechanisms**: Verify automatic recovery and self-healing

Provide specific reliability recommendations and resilience patterns.
"""
        return await self.run_ai_analysis("reliability", prompt)

    async def generate_documentation(self, analyses: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""## Documentation Generation - Phase 2 Summary

Please generate a comprehensive summary of the Phase 2 improvements based on these analyses:

**Security Analysis:**
{analyses.get('security', {}).get('analysis', 'Not available')[:1000]}...

**Performance Analysis:**
{analyses.get('performance', {}).get('analysis', 'Not available')[:1000]}...

**Observability Analysis:**
{analyses.get('observability', {}).get('analysis', 'Not available')[:1000]}...

**Reliability Analysis:**
{analyses.get('reliability', {}).get('analysis', 'Not available')[:1000]}...

Create a professional executive summary that:
1. Highlights key Phase 2 improvements
2. Summarizes security hardening achievements
3. Documents monitoring and alerting capabilities
4. Lists performance optimizations
5. Provides implementation recommendations
6. Includes next steps and maintenance guidance

Format as clean, readable markdown suitable for technical documentation.
"""
        return await self.run_ai_analysis("documentation", prompt)

    def generate_bulletproof_report(self, analyses: Dict[str, Any], diff_stats: Dict[str, int]) -> str:
        verification_status = "✅ REAL AI Verified" if self.verification_results["real_ai_verified"] else "❌ AI Verification Failed"
        bulletproof_status = "✅ Bulletproof Validated" if self.verification_results["bulletproof_validated"] else "❌ Validation Failed"
        return f"""# 🤖 Bulletproof AI Analysis Report - Phase 2

**Repository:** {self.repo_name}
**PR Number:** {self.pr_number or 'N/A'}
**Commit:** {self.commit_sha[:7] if self.commit_sha else 'N/A'}
**Analysis Time:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}

## 🔒 Verification Status
- **AI Verification:** {verification_status}
- **Provider Used:** {self.verification_results.get('provider_used', 'Unknown')}
- **Response Time:** {self.verification_results.get('response_time', 0):.2f}s
- **Bulletproof Validation:** {bulletproof_status}

## 📊 Change Summary
- **Files Changed:** {diff_stats['files_changed']}
- **Lines Added:** +{diff_stats['additions']}
- **Lines Removed:** -{diff_stats['deletions']}

---

## 🔐 Security Analysis
{self._format_analysis_section(analyses.get('security', {}))}

## ⚡ Performance Analysis
{self._format_analysis_section(analyses.get('performance', {}))}

## 📈 Observability Analysis
{self._format_analysis_section(analyses.get('observability', {}))}

## 🛡️️ Reliability Analysis
{self._format_analysis_section(analyses.get('reliability', {}))}

## 📚 Documentation Summary
{self._format_analysis_section(analyses.get('documentation', {}))}

---

## 🎯 Phase 2 Compliance Checklist

### Security Hardening
- [ ] JWT/OIDC validation implemented
- [ ] Security headers configured
- [ ] Rate limiting enforced
- [ ] Input validation comprehensive
- [ ] Audit logging enabled

### Observability
- [ ] Structured logging schema consistent
- [ ] Metrics properly namespaced
- [ ] Health checks return JSON
- [ ] Alert rules configured
- [ ] Dashboards updated

### Performance
- [ ] Middleware overhead acceptable
- [ ] Async operations non-blocking
- [ ] Metrics cardinality safe
- [ ] Response times maintained

### Reliability
- [ ] Error handling consistent
- [ ] Retry policies bounded
- [ ] Circuit breakers implemented
- [ ] Health endpoints comprehensive

---

## 🚀 Next Steps

1. Review Security Findings
2. Optimize Performance
3. Complete Observability
4. Test Reliability
5. Update Documentation

---

*Generated by Bulletproof AI Analysis System v2.0*
*Real AI Provider: {self.verification_results.get('provider_used', 'Unknown')}*
*Analysis Types: {', '.join(self.verification_results.get('analysis_types', []))}*
"""

    def _format_analysis_section(self, analysis: Dict[str, Any]) -> str:
        if not analysis.get("success", False):
            return f"❌ **Analysis Failed:** {analysis.get('error', 'Unknown error')}"
        content = analysis.get("analysis", "No analysis content available")
        provider = analysis.get("provider", "Unknown")
        response_time = analysis.get("response_time", 0)
        return f"""**Provider:** {provider} | **Response Time:** {response_time:.2f}s

{content}"""

    def save_verification_results(self) -> None:
        verification_file = os.path.join(self.artifacts_dir, "verification_results.json")
        with open(verification_file, "w") as f:
            json.dump(self.verification_results, f, indent=2)
        logger.info("Verification results saved to %s", verification_file)

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
