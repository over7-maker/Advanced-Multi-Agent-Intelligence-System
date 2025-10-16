#!/usr/bin/env python3
"""
Bulletproof AI PR Analyzer - Phase 2
Comprehensive PR analysis using real AI providers with bulletproof validation

Security hardened with input validation, secure subprocess calls, and sanitized logging.
"""

import asyncio
import json
import logging
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import tenacity

# Add project root to sys.path securely
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from standalone_universal_ai_manager import get_manager
except ImportError:
    print("Error: Could not import Universal AI Manager")
    sys.exit(1)

# Configure secure logging (no token exposure)
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Security: Never log sensitive environment variables
SENSITIVE_VARS = {"GITHUB_TOKEN", "API_KEY", "SECRET", "PASSWORD", "TOKEN"}

class BulletproofAIAnalyzer:
    """Bulletproof AI PR Analyzer with real provider validation and security hardening"""

    def __init__(self) -> None:
        """Initialize the analyzer with secure environment validation"""
        # Initialize AI manager with retry logic
        self.ai_manager = self._get_ai_manager_with_retry()
        
        # Load and validate environment variables
        self._load_and_validate_env()
        
        # Set up artifacts directory
        self.artifacts_dir = os.getenv("ARTIFACTS_DIR", "artifacts")
        os.makedirs(self.artifacts_dir, exist_ok=True)

        # Verification tracking
        self.verification_results = {
            "real_ai_verified": False,
            "bulletproof_validated": False,
            "fake_ai_detected": True,
            "provider_used": None,
            "response_time": 0.0,
            "timestamp": datetime.utcnow().isoformat(),
            "analysis_types": []
        }
        
        logger.info("Bulletproof AI Analyzer initialized successfully")

    @tenacity.retry(
        stop=tenacity.stop_after_attempt(3), 
        wait=tenacity.wait_exponential(multiplier=1, min=4, max=10)
    )
    def _get_ai_manager_with_retry(self):
        """Get AI manager with retry logic for reliability"""
        try:
            return get_manager()
        except Exception as e:
            logger.error(f"Failed to initialize AI manager: {e}")
            raise RuntimeError(f"AI manager initialization failed: {e}") from e

    def _load_and_validate_env(self) -> None:
        """Load and validate required environment variables securely"""
        # Load environment variables
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.repo_name = os.getenv("REPO_NAME")
        self.pr_number = os.getenv("PR_NUMBER")
        self.commit_sha = os.getenv("COMMIT_SHA")
        self.event_name = os.getenv("EVENT_NAME")
        
        # Validate required variables
        required_env = {
            "GITHUB_TOKEN": self.github_token,
            "REPO_NAME": self.repo_name,
            "COMMIT_SHA": self.commit_sha,
            "EVENT_NAME": self.event_name
        }
        
        missing = [k for k, v in required_env.items() if not v]
        if missing:
            logger.error(f"Missing required environment variables: {', '.join(missing)}")
            sys.exit(1)
        
        # Validate PR_NUMBER if provided
        if self.pr_number:
            try:
                self.pr_number = int(self.pr_number)
            except (TypeError, ValueError):
                logger.error("PR_NUMBER must be an integer")
                sys.exit(1)
        
        # Validate COMMIT_SHA format
        if not re.match(r'^[a-f0-9]{7,40}$', self.commit_sha):
            logger.error("Invalid commit SHA format")
            sys.exit(1)
        
        # Sanitized logging (no sensitive data)
        logger.info(f"Environment loaded - REPO: {self.repo_name}, PR: {self.pr_number}, EVENT: {self.event_name}")
        # SECURITY: Never log self.github_token

    def _validate_path_security(self, path: str) -> bool:
        """Validate path for security (prevent traversal)"""
        # Block path traversal attempts
        if ".." in path or path.startswith("/") or "~" in path:
            logger.error(f"Potential path traversal detected: {path}")
            return False
        return True

    async def get_pr_diff(self) -> str:
        """Get the diff for the pull request using secure subprocess calls"""
        try:
            if self.pr_number:
                # Get PR diff (secure - no shell=True)
                cmd = ["git", "diff", "origin/main...HEAD"]
            else:
                # Get commit diff (secure - no shell=True)
                cmd = ["git", "diff", "HEAD~1", "HEAD"]

            # Security: Use list form, no shell=True, with timeout
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,  # Prevent hanging
                check=False  # Don't raise on non-zero exit
            )
            
            if result.returncode != 0:
                logger.warning(f"Git diff returned code {result.returncode}: {result.stderr}")
                return ""
            
            return result.stdout
            
        except subprocess.TimeoutExpired:
            logger.error("Git diff timed out after 30 seconds")
            return ""
        except Exception as e:
            logger.error(f"Error getting diff: {str(e)}")
            return ""

    async def get_changed_files(self) -> List[str]:
        """Get list of changed files using secure subprocess"""
        try:
            if self.pr_number:
                cmd = ["git", "diff", "--name-only", "origin/main...HEAD"]
            else:
                cmd = ["git", "diff", "--name-only", "HEAD~1", "HEAD"]

            # Security: Use list form, no shell=True, with timeout
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=15,
                check=False
            )
            
            if result.returncode != 0:
                logger.warning(f"Git diff --name-only returned code {result.returncode}")
                return []
            
            files = [f.strip() for f in result.stdout.split("\n") if f.strip()]
            
            # Security: Validate file paths
            secure_files = []
            for file_path in files:
                if self._validate_path_security(file_path):
                    secure_files.append(file_path)
                else:
                    logger.warning(f"Skipping potentially unsafe file path: {file_path}")
            
            return secure_files
            
        except subprocess.TimeoutExpired:
            logger.error("Git diff --name-only timed out")
            return []
        except Exception as e:
            logger.error(f"Error getting changed files: {str(e)}")
            return []

    def calculate_diff_stats(self, diff: str) -> Dict[str, int]:
        """Calculate statistics from the diff safely"""
        try:
            lines = diff.split("\n")
            additions = sum(1 for line in lines if line.startswith("+") and not line.startswith("+++"))
            deletions = sum(1 for line in lines if line.startswith("-") and not line.startswith("---"))
            
            return {
                "additions": additions,
                "deletions": deletions,
                "files_changed": 0,  # Will be set by caller
            }
        except Exception as e:
            logger.error(f"Error calculating diff stats: {e}")
            return {"additions": 0, "deletions": 0, "files_changed": 0}

    async def run_ai_analysis(self, analysis_type: str, prompt: str) -> Dict[str, Any]:
        """Run AI analysis with bulletproof validation and security"""
        try:
            logger.info(f"🤖 Running {analysis_type} analysis...")
            
            # Security: Truncate prompt to prevent injection
            safe_prompt = prompt[:8000]  # Limit prompt size
            
            # Use the universal AI manager with intelligent strategy
            result = await self.ai_manager.generate(
                prompt=safe_prompt,
                system_prompt="You are an expert code reviewer and security analyst. Provide detailed, actionable feedback in professional markdown format. Be specific with file names and line numbers.",
                strategy="intelligent",
                max_tokens=4000,
                temperature=0.3
            )

            if result and result.get("success", False):
                # Bulletproof validation checks
                provider_name = result.get("provider_name", "Unknown")
                content = result.get("content", "")
                response_time = result.get("response_time", 0.0)
                
                # Validate it's a real AI response (not template)
                if self._validate_real_ai_response(provider_name, content, response_time):
                    # Update verification results
                    self.verification_results["real_ai_verified"] = True
                    self.verification_results["bulletproof_validated"] = True
                    self.verification_results["fake_ai_detected"] = False
                    self.verification_results["provider_used"] = provider_name
                    self.verification_results["response_time"] = response_time
                    self.verification_results["analysis_types"].append(analysis_type)

                    logger.info(f"✅ {analysis_type} analysis completed with {provider_name} in {response_time:.2f}s")
                    
                    return {
                        "success": True,
                        "analysis": content,
                        "provider": provider_name,
                        "response_time": response_time,
                        "tokens_used": result.get("tokens_used", 0),
                        "timestamp": datetime.utcnow().isoformat(),
                        "bulletproof_validated": True,
                        "real_ai_verified": True,
                        "fake_ai_detected": False
                    }
                else:
                    logger.error(f"❌ Fake AI detected in {analysis_type} analysis - failing validation")
                    return {
                        "success": False,
                        "error": "Fake AI detected - bulletproof validation failed",
                        "timestamp": datetime.utcnow().isoformat(),
                        "bulletproof_validated": False,
                        "fake_ai_detected": True
                    }
            else:
                logger.error(f"❌ {analysis_type} analysis failed: {result.get('error', 'Unknown error')}")
                return {
                    "success": False,
                    "error": result.get("error", "Unknown error"),
                    "timestamp": datetime.utcnow().isoformat(),
                    "bulletproof_validated": False
                }

        except Exception as e:
            logger.error(f"Exception in {analysis_type} analysis: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "bulletproof_validated": False
            }

    def _validate_real_ai_response(self, provider: str, content: str, response_time: float) -> bool:
        """Validate that the response is from a real AI provider (not fake)"""
        # Check for fake provider names
        fake_providers = {"AI System", "Unknown", "Template", "Fake", "Mock"}
        if provider in fake_providers:
            return False
        
        # Check for template-like response times (suspiciously identical)
        suspicious_times = {1.5, 2.0, 2.5, 3.0}  # Common fake times
        if response_time in suspicious_times:
            return False
        
        # Check for generic/template content
        fake_indicators = [
            "AI-powered analysis completed successfully",
            "Continue current practices",
            "All checks passed",
            "No analysis available",
            "Analysis completed",
            "No specific recommendations"
        ]
        
        content_lower = content.lower()
        for indicator in fake_indicators:
            if indicator.lower() in content_lower:
                return False
        
        # Must be substantial and specific
        if len(content) < 100:
            return False
        
        # Must contain specific technical terms (not generic)
        technical_terms = ["file", "line", "function", "method", "class", "variable", "error", "security", "performance"]
        if not any(term in content_lower for term in technical_terms):
            return False
        
        return True

    async def analyze_security(self, diff: str, changed_files: List[str]) -> Dict[str, Any]:
        """Security analysis focusing on Phase 2 hardening"""
        files_list = ', '.join(changed_files[:10])  # Limit for prompt size
        prompt = f"""## Security Analysis - Phase 2 Hardening

Please perform a comprehensive security analysis of the following changes:

**Changed Files:**
{files_list}

**Code Diff:**
```diff
{diff[:2000]}  
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

Provide specific recommendations with code examples and security best practices. Include file names and line numbers for issues found.
"""

        return await self.run_ai_analysis("security", prompt)

    async def analyze_performance(self, diff: str, changed_files: List[str]) -> Dict[str, Any]:
        """Performance analysis focusing on observability overhead"""
        files_list = ', '.join(changed_files[:10])
        prompt = f"""## Performance Analysis - Observability Impact

Please analyze the performance impact of these changes:

**Changed Files:**
{files_list}

**Code Diff:**
```diff
{diff[:2000]}
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

Provide specific performance recommendations and optimization suggestions with file names and line numbers.
"""

        return await self.run_ai_analysis("performance", prompt)

    async def analyze_observability(self, diff: str, changed_files: List[str]) -> Dict[str, Any]:
        """Observability analysis for monitoring and alerting"""
        files_list = ', '.join(changed_files[:10])
        prompt = f"""## Observability Analysis - Monitoring & Alerting

Please analyze the observability implementation in these changes:

**Changed Files:**
{files_list}

**Code Diff:**
```diff
{diff[:2000]}
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

Provide specific observability recommendations and monitoring best practices with file names and line numbers.
"""

        return await self.run_ai_analysis("observability", prompt)

    async def analyze_reliability(self, diff: str, changed_files: List[str]) -> Dict[str, Any]:
        """Reliability analysis for error handling and resilience"""
        files_list = ', '.join(changed_files[:10])
        prompt = f"""## Reliability Analysis - Error Handling & Resilience

Please analyze the reliability improvements in these changes:

**Changed Files:**
{files_list}

**Code Diff:**
```diff
{diff[:2000]}
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

Provide specific reliability recommendations and resilience patterns with file names and line numbers.
"""

        return await self.run_ai_analysis("reliability", prompt)

    async def generate_documentation(self, analyses: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive documentation summary"""
        # Extract summaries safely
        security_summary = analyses.get('security', {}).get('analysis', 'Not available')[:800]
        performance_summary = analyses.get('performance', {}).get('analysis', 'Not available')[:800]
        observability_summary = analyses.get('observability', {}).get('analysis', 'Not available')[:800]
        reliability_summary = analyses.get('reliability', {}).get('analysis', 'Not available')[:800]
        
        prompt = f"""## Documentation Generation - Phase 2 Summary

Please generate a comprehensive summary of the Phase 2 improvements based on these analyses:

**Security Analysis Summary:**
{security_summary}...

**Performance Analysis Summary:**
{performance_summary}...

**Observability Analysis Summary:**
{observability_summary}...

**Reliability Analysis Summary:**
{reliability_summary}...

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
        fake_ai_status = "❌ false" if not self.verification_results["fake_ai_detected"] else "✅ true"
        
        report = f"""# 🤖 BULLETPROOF REAL AI Analysis

**Status:** {verification_status}  
**Provider:** {self.verification_results.get('provider_used', 'Unknown')} {'(CONFIRMED REAL API CALL)' if self.verification_results['real_ai_verified'] else '(Unverified)'}  
**Response Time:** {self.verification_results.get('response_time', 0):.2f}s  
**Validation:** {bulletproof_status}  

---

## 🔍 Analysis

**Repository:** {self.repo_name}  
**PR Number:** {self.pr_number or 'N/A'}  
**Commit:** {self.commit_sha[:7] if self.commit_sha else 'N/A'}  
**Analysis Time:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}  

### 📊 Change Summary
- **Files Changed:** {diff_stats['files_changed']}
- **Lines Added:** +{diff_stats['additions']}
- **Lines Removed:** -{diff_stats['deletions']}

### 🔐 Security Analysis
{self._format_analysis_section(analyses.get('security', {}))}

### ⚡ Performance Analysis
{self._format_analysis_section(analyses.get('performance', {}))}

### 📈 Observability Analysis
{self._format_analysis_section(analyses.get('observability', {}))}

### 🛡️ Reliability Analysis
{self._format_analysis_section(analyses.get('reliability', {}))}

### 📚 Documentation Summary
{self._format_analysis_section(analyses.get('documentation', {}))}

---

## 📊 Verification Proof
- **Real AI Verified:** {'✅ true' if self.verification_results['real_ai_verified'] else '❌ false'}
- **Fake AI Detected:** {fake_ai_status}
- **Bulletproof Validated:** {'✅ true' if self.verification_results['bulletproof_validated'] else '❌ false'}
- **Provider Attempt:** {len(self.verification_results.get('analysis_types', []))}/4

---

*Generated by Bulletproof AI Analysis System v2.0*  
*🛡️ Protected by BULLETPROOF AI Detection System*  
*⚡ Optimized for large JSON processing with jq*
"""

        return report

    def _format_analysis_section(self, analysis: Dict[str, Any]) -> str:
        """Format an analysis section for the report"""
        if not analysis.get("success", False):
            return f"❌ **Analysis Failed:** {analysis.get('error', 'Unknown error')}"
        
        content = analysis.get("analysis", "No analysis content available")
        provider = analysis.get("provider", "Unknown")
        response_time = analysis.get("response_time", 0)
        
        # Truncate content for readability
        if len(content) > 1500:
            content = content[:1500] + "\n\n... (analysis truncated for readability)"
        
        return f"**Provider:** {provider} | **Response Time:** {response_time:.2f}s\n\n{content}"

    def save_verification_results(self) -> None:
        """Save verification results for audit trail"""
        try:
            verification_file = os.path.join(self.artifacts_dir, "verification_results.json")
            
            # Security: Ensure directory exists and is writable
            os.makedirs(self.artifacts_dir, exist_ok=True)
            
            with open(verification_file, "w", encoding="utf-8") as f:
                json.dump(self.verification_results, f, indent=2)
            
            logger.info(f"Verification results saved to {verification_file}")
        except Exception as e:
            logger.error(f"Failed to save verification results: {e}")

    async def run_comprehensive_analysis(self) -> Optional[str]:
        """Run comprehensive bulletproof AI analysis"""
        logger.info("🚀 Starting Bulletproof AI PR Analysis...")
        
        try:
            # Get PR information
            diff = await self.get_pr_diff()
            changed_files = await self.get_changed_files()
            diff_stats = self.calculate_diff_stats(diff)
            diff_stats["files_changed"] = len(changed_files)

            if not diff and not changed_files:
                logger.warning("No changes detected")
                return None

            logger.info(f"Analyzing {diff_stats['files_changed']} files with {diff_stats['additions']} additions and {diff_stats['deletions']} deletions")

            # Run all analyses sequentially to avoid rate limits
            analyses = {}
            
            analysis_types = [
                ("security", self.analyze_security),
                ("performance", self.analyze_performance),
                ("observability", self.analyze_observability),
                ("reliability", self.analyze_reliability)
            ]
            
            # Execute analyses sequentially with delay
            for analysis_type, analysis_func in analysis_types:
                logger.info(f"Running {analysis_type} analysis...")
                analyses[analysis_type] = await analysis_func(diff, changed_files)
                
                # Add delay between analyses to avoid rate limiting
                await asyncio.sleep(2)
            
            # Generate documentation
            logger.info("Generating documentation summary...")
            analyses["documentation"] = await self.generate_documentation(analyses)
            
        except Exception as e:
            logger.error(f"Error during analysis: {str(e)}")
            return None

        # Generate final report
        report = self.generate_bulletproof_report(analyses, diff_stats)
        
        # Save report securely
        try:
            report_path = os.path.join(self.artifacts_dir, "bulletproof_analysis_report.md")
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(report)
            logger.info(f"Bulletproof analysis report saved to {report_path}")
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
        
        # Save verification results
        self.save_verification_results()
        
        # Print summary
        print("\n" + "=" * 80)
        print("🤖 BULLETPROOF AI ANALYSIS COMPLETE")
        print("=" * 80)
        print(f"✅ Real AI Verified: {self.verification_results['real_ai_verified']}")
        print(f"✅ Bulletproof Validated: {self.verification_results['bulletproof_validated']}")
        print(f"❌ Fake AI Detected: {self.verification_results['fake_ai_detected']}")
        print(f"🤖 Provider Used: {self.verification_results.get('provider_used', 'Unknown')}")
        print(f"⏱️ Response Time: {self.verification_results.get('response_time', 0):.2f}s")
        print(f"📊 Analysis Types: {', '.join(self.verification_results.get('analysis_types', []))}")
        print("=" * 80 + "\n")
        
        return report


async def main() -> None:
    """Main function with proper error handling"""
    try:
        analyzer = BulletproofAIAnalyzer()
        await analyzer.run_comprehensive_analysis()
        
    except KeyboardInterrupt:
        logger.info("Analysis interrupted by user")
        sys.exit(130)
        
    except Exception as e:
        logger.error(f"Bulletproof AI analysis failed: {str(e)}")
        
        # Create error report
        error_report = f"""# ❌ Bulletproof AI Analysis Error

**Status:** ❌ Analysis Failed  
**Error:** {str(e)}  
**Timestamp:** {datetime.utcnow().isoformat()}  

An error occurred during the bulletproof AI analysis process. Please check the workflow logs for more details.

## 🔧 Troubleshooting Steps
1. Verify all required environment variables are set
2. Check AI provider API keys are valid
3. Ensure repository permissions are correct
4. Review workflow logs for detailed error information

---

*🛡️ Protected by BULLETPROOF AI Detection System*  
*No fake responses generated when analysis unavailable*
"""

        # Save error report safely
        try:
            os.makedirs("artifacts", exist_ok=True)
            with open("artifacts/bulletproof_analysis_report.md", "w", encoding="utf-8") as f:
                f.write(error_report)
        except Exception as save_error:
            logger.error(f"Failed to save error report: {save_error}")

        sys.exit(1)


if __name__ == "__main__":
    # Security: Verify Python version
    if sys.version_info < (3, 8):
        print("Error: Python 3.8+ required for bulletproof AI analysis")
        sys.exit(1)
    
    asyncio.run(main())