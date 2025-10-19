#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
Bulletproof AI PR Analyzer - Phase 2
Comprehensive PR analysis using real AI providers with bulletproof validation

Security hardened with input validation, secure subprocess calls, and sanitized logging.
Enhanced with improved project root finding and structured logging.
"""

import asyncio
import json
import logging
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import tenacity

# Set up basic logging first
def _setup_logging():
    """Setup logging configuration safely and idempotently"""
    logging_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    try:
        level = getattr(logging, logging_level)
    except AttributeError:
        level = logging.INFO
    
    # Configure logging with force=True to ensure consistent setup
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        force=True  # Ensures consistent setup even if already configured
    )
    return logging.getLogger(__name__)

logger = _setup_logging()

# Import enhanced error handling and circuit breaker services
try:
    from src.amas.services.circuit_breaker_service import (
        get_circuit_breaker_service, CircuitBreakerConfig, 
        CircuitBreakerOpenException, CircuitBreakerTimeoutException
    )
    from src.amas.services.error_recovery_service import (
        get_error_recovery_service, ErrorContext, ErrorSeverity
    )
    from src.amas.errors.error_handling import (
        AMASException, ValidationError, InternalError, ExternalServiceError,
        TimeoutError as AMASTimeoutError, SecurityError
    )
    ENHANCED_ERROR_HANDLING = True
except ImportError:
    ENHANCED_ERROR_HANDLING = False
    # Define fallback exception classes for basic error handling
    class AMASException(Exception):
        """Base exception for AMAS system"""
        def __init__(self, message: str, safe_message: str = None, details: str = None):
            super().__init__(safe_message or message)
            self.details = details  # For internal logging, not user-facing
            self.original_message = message
    
    class ValidationError(AMASException):
        """Raised when input/data validation fails"""
        def __init__(self, message: str, safe_message: str = "Invalid input provided"):
            super().__init__(message, safe_message)
    
    class InternalError(AMASException):
        """Raised for internal system errors"""
        def __init__(self, message: str, safe_message: str = "Internal system error occurred"):
            super().__init__(message, safe_message)
    
    class ExternalServiceError(AMASException):
        """Raised when external services fail"""
        def __init__(self, message: str, safe_message: str = "External service temporarily unavailable"):
            super().__init__(message, safe_message)
    
    class SecurityError(AMASException):
        """Raised for security-related violations"""
        def __init__(self, message: str, safe_message: str = "Security violation detected"):
            super().__init__(message, safe_message)
    
    class AMASTimeoutError(AMASException):
        """Raised when operations timeout"""
        def __init__(self, message: str, safe_message: str = "Operation timed out"):
            super().__init__(message, safe_message)
    
    logger.warning("Enhanced error handling not available, using basic error handling")
    
    # For CI environments, we can be more lenient with fallbacks
    # But log a warning about potential behavior differences
    logger.warning("Running in fallback mode - some advanced features may not be available")

# Add project root to sys.path securely
SCRIPT_DIR = str(Path(__file__).resolve().parent)

def _setup_project_paths():
    """Setup project paths for imports using secure pathlib operations"""
    try:
        from src.amas.utils.project_root import find_project_root, get_project_root, add_project_root_to_path
        PROJECT_ROOT: str = find_project_root(SCRIPT_DIR)
        add_project_root_to_path(PROJECT_ROOT)
        logger.info(f"Using enhanced project root finding: {PROJECT_ROOT}")
        return PROJECT_ROOT
    except ImportError:
        # Fallback to legacy method if enhanced module not available
        def _find_project_root() -> str:
            """Find project root by looking for .git directory with depth limit using pathlib"""
            MAX_TRAVERSAL_DEPTH = 10
            current = Path(__file__).resolve().parent
            
            for depth in range(MAX_TRAVERSAL_DEPTH):
                if (current / '.git').exists():
                    logger.info(f"Found project root: {current}")
                    return str(current)
                
                if current.parent == current:  # Reached filesystem root
                    break
                current = current.parent
            
            # Fallback to two directories up from script
            fallback = Path(__file__).resolve().parent.parent.parent
            
            # Validate fallback contains expected project files
            if (fallback / '.git').exists() or (fallback / 'pyproject.toml').exists():
                logger.info(f"Using fallback project root: {fallback}")
                return str(fallback)
            
            # Final fallback to script's parent directory
            final_fallback = Path(__file__).resolve().parent.parent
            logger.warning(f"Could not find project root within {MAX_TRAVERSAL_DEPTH} levels, using final fallback: {final_fallback}")
            return str(final_fallback)
        
        PROJECT_ROOT: str = _find_project_root()
        
        # Add paths safely
        if SCRIPT_DIR not in sys.path:
            sys.path.insert(0, SCRIPT_DIR)
        if PROJECT_ROOT not in sys.path:
            sys.path.insert(0, PROJECT_ROOT)
        
        logger.info(f"Using legacy project root finding: {PROJECT_ROOT}")
        return PROJECT_ROOT

# Setup project paths
PROJECT_ROOT = _setup_project_paths()

try:
    from standalone_universal_ai_manager import get_manager
except ImportError as e:
    print(f"Error: Could not import Universal AI Manager: {e}", file=sys.stderr)
    print(f"Current sys.path: {sys.path}", file=sys.stderr)
    print(f"Looking for module in: {PROJECT_ROOT}", file=sys.stderr)
    sys.exit(1)

# Configure enhanced logging with security considerations
try:
    from src.amas.services.enhanced_logging_service import (
        configure_logging, get_logger, LoggingConfig, LogLevel, LogFormat, SecurityLevel
    )
    
    # Configure enhanced logging
    config = LoggingConfig(
        level=LogLevel.INFO,
        format=LogFormat.JSON,
        security_level=SecurityLevel.MEDIUM,
        enable_console=True,
        enable_correlation=True,
        enable_metrics=True,
        enable_audit=True,
        enable_performance=True,
        include_stack_traces=True
    )
    
    # Override with environment variables
    log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
    if log_level_str in {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}:
        config.level = LogLevel(log_level_str)
    
    log_format_str = os.getenv("LOG_FORMAT", "json").lower()
    if log_format_str in {'json', 'text', 'structured'}:
        config.format = LogFormat(log_format_str)
    
    security_level_str = os.getenv("LOG_SECURITY_LEVEL", "medium").lower()
    if security_level_str in {'low', 'medium', 'high', 'maximum'}:
        config.security_level = SecurityLevel(security_level_str)
    
    configure_logging(config)
    logger = get_logger(__name__, "bulletproof_ai_analyzer")
    
except ImportError:
    # Fallback to basic logging if enhanced module not available
    VALID_LOG_LEVELS = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
    log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()

    if log_level_str not in VALID_LOG_LEVELS:
        print(f"Warning: Invalid LOG_LEVEL='{log_level_str}', defaulting to INFO", file=sys.stderr)
        log_level_str = "INFO"

    logging.basicConfig(
        level=getattr(logging, log_level_str, logging.INFO), 
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stderr)
        ]
    )
    logger = logging.getLogger(__name__)

# Security: Never log sensitive environment variables
SENSITIVE_VARS = {"GITHUB_TOKEN", "API_KEY", "SECRET", "PASSWORD", "TOKEN"}

def sanitize_env(env: Dict[str, str]) -> Dict[str, str]:
    """Sanitize environment variables to prevent secret leakage"""
    return {
        k: "<redacted>" if any(sens in k.upper() for sens in SENSITIVE_VARS) else v
        for k, v in env.items()
    }

class BulletproofAIAnalyzer:
    """Bulletproof AI PR Analyzer with real provider validation and security hardening"""

    def __init__(self) -> None:
        """Initialize the analyzer with security hardening"""
        # Initialize AI manager with retry logic
        self.ai_manager = self._get_ai_manager_with_retry()
        
        # Load and validate environment variables
        self._load_and_validate_environment()
        
        # Initialize verification tracking
        self.verification_results = {
            "real_ai_verified": False,
            "bulletproof_validated": False,
            "provider_used": None,
            "response_time": 0.0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "analysis_types": []
        }
        
        # Initialize enhanced error handling if available
        if ENHANCED_ERROR_HANDLING:
            self.circuit_breaker_service = get_circuit_breaker_service()
            self.error_recovery_service = get_error_recovery_service()
            
            # Create circuit breakers for different operations
            self._setup_circuit_breakers()
        else:
            self.circuit_breaker_service = None
            self.error_recovery_service = None

    def _get_ai_manager_with_retry(self) -> Any:
        """Get AI manager with retry logic and proper error handling"""
        @tenacity.retry(
            stop=tenacity.stop_after_attempt(3),
            wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
            retry=tenacity.retry_if_exception_type(Exception)
        )
        def _retry_get_manager():
            return get_manager()
        
        try:
            return _retry_get_manager()
        except Exception as e:
            logger.critical(f"Failed to initialize AI manager after retries: {e}")
            sys.exit(1)

    def _load_and_validate_environment(self) -> None:
        """Load and validate environment variables with security checks"""
        # Load environment variables
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.repo_name = os.getenv("REPO_NAME")
        self.pr_number = os.getenv("PR_NUMBER")
        self.commit_sha = os.getenv("COMMIT_SHA")
        self.event_name = os.getenv("EVENT_NAME")
        self.artifacts_dir = os.getenv("ARTIFACTS_DIR", "artifacts")

        # Validate required environment variables
        required_env = {
            "GITHUB_TOKEN": self.github_token,
            "REPO_NAME": self.repo_name,
        }
        missing = [k for k, v in required_env.items() if not v]
        if missing:
            logger.error(f"Missing required environment variables: {', '.join(missing)}")
            sys.exit(1)

        # Validate input data for security
        self._validate_inputs()

        # Create artifacts directory
        os.makedirs(self.artifacts_dir, exist_ok=True)

        # Log environment info safely (never log tokens)
        safe_env = sanitize_env(dict(os.environ))
        logger.debug(f"Environment loaded: REPO_NAME={self.repo_name}, PR_NUMBER={self.pr_number}")
        # NEVER log self.github_token
    
    def _setup_circuit_breakers(self):
        """Setup circuit breakers for different operations"""
        if not ENHANCED_ERROR_HANDLING:
            return
        
        # AI API circuit breaker
        ai_config = CircuitBreakerConfig(
            failure_threshold=5,
            recovery_timeout=60.0,
            success_threshold=3,
            timeout=30.0,
            expected_exceptions=[Exception]
        )
        self.circuit_breaker_service.create_breaker("ai_api", ai_config)
        
        # Git operations circuit breaker
        git_config = CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=30.0,
            success_threshold=2,
            timeout=10.0,
            expected_exceptions=[Exception]
        )
        self.circuit_breaker_service.create_breaker("git_operations", git_config)
        
        # File operations circuit breaker
        file_config = CircuitBreakerConfig(
            failure_threshold=5,
            recovery_timeout=30.0,
            success_threshold=3,
            timeout=5.0,
            expected_exceptions=[Exception]
        )
        self.circuit_breaker_service.create_breaker("file_operations", file_config)

    def _validate_inputs(self) -> None:
        """Validate input data for security"""
        # Validate PR number if provided
        if self.pr_number:
            try:
                self.pr_number = int(self.pr_number)
            except (TypeError, ValueError):
                logger.error("PR_NUMBER must be an integer")
                sys.exit(1)
        
        # Validate commit SHA if provided
        if self.commit_sha and not re.match(r'^[a-f0-9]{40}$', self.commit_sha):
            logger.error("COMMIT_SHA must be a valid 40-character Git SHA")
            sys.exit(1)

    async def get_pr_diff(self) -> str:
        """Get the diff for the pull request using async subprocess with circuit breaker"""
        try:
            if ENHANCED_ERROR_HANDLING:
                # Use circuit breaker for git operations
                breaker = self.circuit_breaker_service.get_breaker("git_operations")
                if breaker:
                    return await breaker.call(self._get_pr_diff_impl)
                else:
                    return await self._get_pr_diff_impl()
            else:
                return await self._get_pr_diff_impl()
        except (CircuitBreakerOpenException, CircuitBreakerTimeoutException) as e:
            logger.error(f"Circuit breaker prevented git diff operation: {e}")
            return ""
        except Exception as e:
            logger.error(f"Error getting diff: {str(e)}")
            if ENHANCED_ERROR_HANDLING:
                # Try to recover from error
                await self._handle_git_error(e, "get_pr_diff")
            return ""
    
    async def _get_pr_diff_impl(self) -> str:
        """Implementation of getting PR diff"""
        if self.pr_number:
            # Get PR diff
            cmd = ["git", "diff", "origin/main...HEAD"]
        else:
            # Get commit diff
            cmd = ["git", "diff", "HEAD~1", "HEAD"]

        # Use async subprocess to avoid blocking the event loop
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise Exception(f"Git diff failed: {stderr.decode()}")
        
        return stdout.decode()

    async def get_changed_files(self) -> List[str]:
        """Get list of changed files using async subprocess with circuit breaker"""
        try:
            if ENHANCED_ERROR_HANDLING:
                # Use circuit breaker for git operations
                breaker = self.circuit_breaker_service.get_breaker("git_operations")
                if breaker:
                    return await breaker.call(self._get_changed_files_impl)
                else:
                    return await self._get_changed_files_impl()
            else:
                return await self._get_changed_files_impl()
        except (CircuitBreakerOpenException, CircuitBreakerTimeoutException) as e:
            logger.error(f"Circuit breaker prevented git operations: {e}")
            return []
        except Exception as e:
            logger.error(f"Error getting changed files: {str(e)}")
            if ENHANCED_ERROR_HANDLING:
                # Try to recover from error
                await self._handle_git_error(e, "get_changed_files")
            return []
    
    async def _get_changed_files_impl(self) -> List[str]:
        """Implementation of getting changed files"""
        if self.pr_number:
            cmd = ["git", "diff", "--name-only", "origin/main...HEAD"]
        else:
            cmd = ["git", "diff", "--name-only", "HEAD~1", "HEAD"]

        # Use async subprocess to avoid blocking the event loop
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise Exception(f"Git diff --name-only failed: {stderr.decode()}")
        
        return [f.strip() for f in stdout.decode().split("\n") if f.strip()]

    async def calculate_diff_stats(self, diff: str) -> Dict[str, int]:
        """Calculate statistics from the diff"""
        additions = len([line for line in diff.split("\n") if line.startswith("+")])
        deletions = len([line for line in diff.split("\n") if line.startswith("-")])
        changed_files = await self.get_changed_files()
        files_changed = len(changed_files)

        return {
            "additions": additions,
            "deletions": deletions,
            "files_changed": files_changed,
        }

    async def run_ai_analysis(self, analysis_type: str, prompt: str) -> Dict[str, Any]:
        """Run AI analysis with bulletproof validation and retry logic"""
        try:
            if ENHANCED_ERROR_HANDLING:
                # Use circuit breaker for AI API calls
                breaker = self.circuit_breaker_service.get_breaker("ai_api")
                if breaker:
                    return await breaker.call(self._run_ai_analysis_impl, analysis_type, prompt)
                else:
                    return await self._run_ai_analysis_impl(analysis_type, prompt)
            else:
                return await self._run_ai_analysis_impl(analysis_type, prompt)
        except (CircuitBreakerOpenException, CircuitBreakerTimeoutException) as e:
            logger.error(f"Circuit breaker prevented AI analysis: {e}")
            return {
                "success": False,
                "error": f"AI service unavailable: {str(e)}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Error in AI analysis: {str(e)}")
            if ENHANCED_ERROR_HANDLING:
                # Try to recover from error
                await self._handle_ai_error(e, analysis_type)
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def _run_ai_analysis_impl(self, analysis_type: str, prompt: str) -> Dict[str, Any]:
        """Implementation of AI analysis with retry logic"""
        max_retries = 3
        retry_delay = 1.0
        
        for attempt in range(max_retries):
            try:
                logger.info(f"🤖 Running {analysis_type} analysis... (attempt {attempt + 1}/{max_retries})")
                
                # Use the universal AI manager with intelligent strategy
                result = await self.ai_manager.generate(
                    prompt=prompt,
                    system_prompt="You are an expert code reviewer and security analyst. Provide detailed, actionable feedback in professional markdown format.",
                    strategy="intelligent",
                    max_tokens=4000,
                    temperature=0.3
                )
                
                if result and result.get("success", False):
                    # Update verification results
                    self.verification_results["real_ai_verified"] = True
                    self.verification_results["bulletproof_validated"] = True
                    self.verification_results["provider_used"] = result.get("provider_name", "Unknown")
                    self.verification_results["response_time"] = result.get("response_time", 0.0)
                    self.verification_results["analysis_types"].append(analysis_type)

                    logger.info(f"✅ {analysis_type} analysis completed with {result.get('provider_name')} in {result.get('response_time', 0):.2f}s")
                    
                    return {
                        "success": True,
                        "analysis": result.get("content", ""),
                        "provider": result.get("provider_name", "Unknown"),
                        "response_time": result.get("response_time", 0.0),
                        "tokens_used": result.get("tokens_used", 0),
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                else:
                    error_msg = result.get('error', 'Unknown error') if result else 'No result returned'
                    logger.warning(f"⚠️ {analysis_type} analysis attempt {attempt + 1} failed: {error_msg}")
                    
                    if attempt < max_retries - 1:
                        await asyncio.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                        continue
                    else:
                        return {
                            "success": False,
                            "error": error_msg,
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        }

            except Exception as e:
                logger.warning(f"Exception in {analysis_type} analysis attempt {attempt + 1}: {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                    continue
                else:
                    return {
                        "success": False,
                        "error": str(e),
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }

    async def analyze_security(self, diff: str, changed_files: List[str]) -> Dict[str, Any]:
        """Security analysis focusing on Phase 2 hardening"""
        # Sanitize inputs to prevent injection
        safe_changed_files = [f.replace('\n', '').replace('\r', '') for f in changed_files[:50]]  # Limit and sanitize
        safe_diff = diff[:3000].replace('\0', '')  # Remove null bytes
        
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
        """Performance analysis focusing on observability overhead"""
        # Sanitize inputs to prevent injection
        safe_changed_files = [f.replace('\n', '').replace('\r', '') for f in changed_files[:50]]  # Limit and sanitize
        safe_diff = diff[:3000].replace('\0', '')  # Remove null bytes
        
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
        """Observability analysis for monitoring and alerting"""
        # Sanitize inputs to prevent injection
        safe_changed_files = [f.replace('\n', '').replace('\r', '') for f in changed_files[:50]]  # Limit and sanitize
        safe_diff = diff[:3000].replace('\0', '')  # Remove null bytes
        
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
        """Reliability analysis for error handling and resilience"""
        # Sanitize inputs to prevent injection
        safe_changed_files = [f.replace('\n', '').replace('\r', '') for f in changed_files[:50]]  # Limit and sanitize
        safe_diff = diff[:3000].replace('\0', '')  # Remove null bytes
        
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
        """Generate comprehensive documentation summary"""
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
        """Generate the final bulletproof analysis report"""

        # Check if we have real AI verification
        verification_status = "✅ REAL AI Verified" if self.verification_results["real_ai_verified"] else "❌ AI Verification Failed"
        bulletproof_status = "✅ Bulletproof Validated" if self.verification_results["bulletproof_validated"] else "❌ Validation Failed"

        report = f"""# 🤖 Bulletproof AI Analysis Report - Phase 2

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

1. **Review Security Findings**: Address any security vulnerabilities identified
2. **Optimize Performance**: Implement performance recommendations
3. **Complete Observability**: Ensure all monitoring components are properly configured
4. **Test Reliability**: Verify error handling and recovery mechanisms
5. **Update Documentation**: Keep technical documentation current

---

*Generated by Bulletproof AI Analysis System v2.0*
*Real AI Provider: {self.verification_results.get('provider_used', 'Unknown')}*
*Analysis Types: {', '.join(self.verification_results.get('analysis_types', []))}*
"""

        return report

    def _format_analysis_section(self, analysis: Dict[str, Any]) -> str:
        """Format an analysis section for the report"""
        if not analysis.get("success", False):
            return f"❌ **Analysis Failed:** {analysis.get('error', 'Unknown error')}"

        content = analysis.get("analysis", "No analysis content available")
        provider = analysis.get("provider", "Unknown")
        response_time = analysis.get("response_time", 0)

        return f"""**Provider:** {provider} | **Response Time:** {response_time:.2f}s

{content}"""

    def save_verification_results(self) -> None:
        """Save verification results for audit trail"""
        verification_file = os.path.join(self.artifacts_dir, "verification_results.json")
        with open(verification_file, "w") as f:
            json.dump(self.verification_results, f, indent=2)

        logger.info(f"Verification results saved to {verification_file}")
    
    async def _handle_git_error(self, error: Exception, operation: str):
        """Handle git operation errors with recovery"""
        if not ENHANCED_ERROR_HANDLING:
            return
        
        try:
            context = ErrorContext(
                error_type="git_error",
                error_message=str(error),
                severity=ErrorSeverity.MEDIUM,
                component="bulletproof_ai_analyzer",
                operation=operation,
                metadata={"error_type": type(error).__name__}
            )
            
            success = await self.error_recovery_service.handle_error(context)
            if success:
                logger.info(f"Successfully recovered from git error in {operation}")
            else:
                logger.warning(f"Failed to recover from git error in {operation}")
        except Exception as recovery_error:
            logger.error(f"Error during git error recovery: {recovery_error}")
    
    async def _handle_ai_error(self, error: Exception, analysis_type: str):
        """Handle AI analysis errors with recovery"""
        if not ENHANCED_ERROR_HANDLING:
            return
        
        try:
            context = ErrorContext(
                error_type="ai_analysis_error",
                error_message=str(error),
                severity=ErrorSeverity.HIGH,
                component="bulletproof_ai_analyzer",
                operation=f"ai_analysis_{analysis_type}",
                metadata={
                    "error_type": type(error).__name__,
                    "analysis_type": analysis_type
                }
            )
            
            success = await self.error_recovery_service.handle_error(context)
            if success:
                logger.info(f"Successfully recovered from AI error in {analysis_type}")
            else:
                logger.warning(f"Failed to recover from AI error in {analysis_type}")
        except Exception as recovery_error:
            logger.error(f"Error during AI error recovery: {recovery_error}")
    
    async def _handle_file_error(self, error: Exception, operation: str):
        """Handle file operation errors with recovery"""
        if not ENHANCED_ERROR_HANDLING:
            return
        
        try:
            context = ErrorContext(
                error_type="file_error",
                error_message=str(error),
                severity=ErrorSeverity.MEDIUM,
                component="bulletproof_ai_analyzer",
                operation=operation,
                metadata={"error_type": type(error).__name__}
            )
            
            success = await self.error_recovery_service.handle_error(context)
            if success:
                logger.info(f"Successfully recovered from file error in {operation}")
            else:
                logger.warning(f"Failed to recover from file error in {operation}")
        except Exception as recovery_error:
            logger.error(f"Error during file error recovery: {recovery_error}")

    async def run_comprehensive_analysis(self) -> str:
        """Run comprehensive bulletproof AI analysis"""
        logger.info("🚀 Starting Bulletproof AI PR Analysis...")
        
        # Get PR information
        diff = await self.get_pr_diff()
        changed_files = await self.get_changed_files()
        diff_stats = await self.calculate_diff_stats(diff)

        if not diff and not changed_files:
            logger.warning("No changes detected")
            return ""

        logger.info(f"Analyzing {diff_stats['files_changed']} files with {diff_stats['additions']} additions and {diff_stats['deletions']} deletions")

        # Run all analyses in parallel for efficiency
        analyses = {}

        try:
            # Run all analyses concurrently with timeout
            analysis_tasks = [
                ("security", self.analyze_security(diff, changed_files)),
                ("performance", self.analyze_performance(diff, changed_files)),
                ("observability", self.analyze_observability(diff, changed_files)),
                ("reliability", self.analyze_reliability(diff, changed_files))
            ]
            
            # Execute all analyses with timeout (5 minutes per analysis)
            for analysis_type, task in analysis_tasks:
                try:
                    analyses[analysis_type] = await asyncio.wait_for(task, timeout=300.0)
                except asyncio.TimeoutError:
                    logger.error(f"❌ {analysis_type} analysis timed out after 5 minutes")
                    analyses[analysis_type] = {
                        "success": False,
                        "error": "Analysis timed out after 5 minutes",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
            
            # Generate documentation with timeout
            try:
                analyses["documentation"] = await asyncio.wait_for(
                    self.generate_documentation(analyses), 
                    timeout=300.0
                )
            except asyncio.TimeoutError:
                logger.error("❌ Documentation generation timed out after 5 minutes")
                analyses["documentation"] = {
                    "success": False,
                    "error": "Documentation generation timed out after 5 minutes",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }

        except Exception as e:
            logger.error(f"Error during analysis: {str(e)}")
            return ""

        # Generate final report
        report = self.generate_bulletproof_report(analyses, diff_stats)

        # Save report
        report_path = os.path.join(self.artifacts_dir, "bulletproof_analysis_report.md")
        with open(report_path, "w") as f:
            f.write(report)

        # Save verification results
        self.save_verification_results()

        logger.info(f"Bulletproof analysis report saved to {report_path}")

        # Print summary
        print("\n" + "=" * 80)
        print("🤖 BULLETPROOF AI ANALYSIS COMPLETE")
        print("=" * 80)
        print(f"✅ Real AI Verified: {self.verification_results['real_ai_verified']}")
        print(f"✅ Bulletproof Validated: {self.verification_results['bulletproof_validated']}")
        print(f"✅ Provider Used: {self.verification_results.get('provider_used', 'Unknown')}")
        print(f"✅ Response Time: {self.verification_results.get('response_time', 0):.2f}s")
        print(f"✅ Analysis Types: {', '.join(self.verification_results.get('analysis_types', []))}")
        print("=" * 80 + "\n")

        return report


async def main() -> None:
    """Main function"""
    try:
        analyzer = BulletproofAIAnalyzer()
        await analyzer.run_comprehensive_analysis()
    except Exception as e:
        logger.error(f"Bulletproof AI analysis failed: {str(e)}")

        # Create error report
        error_report = f"""# ❌ Bulletproof AI Analysis Error

An error occurred during the bulletproof AI analysis process:

```
{str(e)}
```

Please check the workflow logs for more details.

*Bulletproof AI Analysis System v2.0*
"""

        # Save error report
        os.makedirs("artifacts", exist_ok=True)
        with open("artifacts/bulletproof_analysis_report.md", "w") as f:
            f.write(error_report)

        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())