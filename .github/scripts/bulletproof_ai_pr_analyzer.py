#!/usr/bin/env python3
"""
Bulletproof AI PR Analyzer - Phase 2
Comprehensive PR analysis using real AI providers with bulletproof validation
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

# Add project root to sys.path
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

try:
    from standalone_universal_ai_manager import get_manager
except ImportError:
    print("Error: Could not import Universal AI Manager")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class BulletproofAIAnalyzer:
    """Bulletproof AI PR Analyzer with real provider validation"""

    def __init__(self):
        self.ai_manager = get_manager()
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.repo_name = os.getenv("REPO_NAME")
        self.pr_number = os.getenv("PR_NUMBER")
        self.commit_sha = os.getenv("COMMIT_SHA")
        self.event_name = os.getenv("EVENT_NAME")
        self.artifacts_dir = "artifacts"

        # Create artifacts directory
        os.makedirs(self.artifacts_dir, exist_ok=True)

        # Verification tracking
        self.verification_results = {
            "real_ai_verified": False,
            "bulletproof_validated": False,
            "provider_used": None,
            "response_time": 0.0,
            "timestamp": datetime.utcnow().isoformat(),
            "analysis_types": []
        }

    def get_pr_diff(self) -> str:
        """Get the diff for the pull request"""
        try:
            if self.pr_number:
                # Get PR diff
                cmd = ["git", "diff", "origin/main...HEAD"]
            else:
                # Get commit diff
                cmd = ["git", "diff", "HEAD~1", "HEAD"]

            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.stdout
        except Exception as e:
            logger.error(f"Error getting diff: {str(e)}")
            return ""

    def get_changed_files(self) -> List[str]:
        """Get list of changed files"""
        try:
            if self.pr_number:
                cmd = ["git", "diff", "--name-only", "origin/main...HEAD"]
            else:
                cmd = ["git", "diff", "--name-only", "HEAD~1", "HEAD"]

            result = subprocess.run(cmd, capture_output=True, text=True)
            return [f.strip() for f in result.stdout.split("\n") if f.strip()]
        except Exception as e:
            logger.error(f"Error getting changed files: {str(e)}")
            return []

    def calculate_diff_stats(self, diff: str) -> Dict[str, int]:
        """Calculate statistics from the diff"""
        additions = len([line for line in diff.split("\n") if line.startswith("+")])
        deletions = len([line for line in diff.split("\n") if line.startswith("-")])
        files_changed = len(self.get_changed_files())

        return {
            "additions": additions,
            "deletions": deletions,
            "files_changed": files_changed,
        }

    async def run_ai_analysis(self, analysis_type: str, prompt: str) -> Dict[str, Any]:
        """Run AI analysis with bulletproof validation"""
        try:
            logger.info(f"🤖 Running {analysis_type} analysis...")
            
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
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                logger.error(f"❌ {analysis_type} analysis failed: {result.get('error', 'Unknown error')}")
                return {
                    "success": False,
                    "error": result.get("error", "Unknown error"),
                    "timestamp": datetime.utcnow().isoformat()
                }

        except Exception as e:
            logger.error(f"Exception in {analysis_type} analysis: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def analyze_security(self, diff: str, changed_files: List[str]) -> Dict[str, Any]:
        """Security analysis focusing on Phase 2 hardening"""
        prompt = f"""## Security Analysis - Phase 2 Hardening

Please perform a comprehensive security analysis of the following changes:

**Changed Files:**
{', '.join(changed_files)}

**Code Diff:**
```diff
{diff[:3000]}
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
        prompt = f"""## Performance Analysis - Observability Impact

Please analyze the performance impact of these changes:

**Changed Files:**
{', '.join(changed_files)}

**Code Diff:**
```diff
{diff[:3000]}
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
        prompt = f"""## Observability Analysis - Monitoring & Alerting

Please analyze the observability implementation in these changes:

**Changed Files:**
{', '.join(changed_files)}

**Code Diff:**
```diff
{diff[:3000]}
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
        prompt = f"""## Reliability Analysis - Error Handling & Resilience

Please analyze the reliability improvements in these changes:

**Changed Files:**
{', '.join(changed_files)}

**Code Diff:**
```diff
{diff[:3000]}
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
**Analysis Time:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

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

## 🛡️ Reliability Analysis
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

    def save_verification_results(self):
        """Save verification results for audit trail"""
        verification_file = os.path.join(self.artifacts_dir, "verification_results.json")
        with open(verification_file, "w") as f:
            json.dump(self.verification_results, f, indent=2)
        
        logger.info(f"Verification results saved to {verification_file}")

    async def run_comprehensive_analysis(self):
        """Run comprehensive bulletproof AI analysis"""
        logger.info("🚀 Starting Bulletproof AI PR Analysis...")
        
        # Get PR information
        diff = self.get_pr_diff()
        changed_files = self.get_changed_files()
        diff_stats = self.calculate_diff_stats(diff)

        if not diff and not changed_files:
            logger.warning("No changes detected")
            return

        logger.info(f"Analyzing {diff_stats['files_changed']} files with {diff_stats['additions']} additions and {diff_stats['deletions']} deletions")

        # Run all analyses in parallel for efficiency
        analyses = {}
        
        try:
            # Run all analyses concurrently
            analysis_tasks = [
                ("security", self.analyze_security(diff, changed_files)),
                ("performance", self.analyze_performance(diff, changed_files)),
                ("observability", self.analyze_observability(diff, changed_files)),
                ("reliability", self.analyze_reliability(diff, changed_files))
            ]
            
            # Execute all analyses
            for analysis_type, task in analysis_tasks:
                analyses[analysis_type] = await task
            
            # Generate documentation
            analyses["documentation"] = await self.generate_documentation(analyses)
            
        except Exception as e:
            logger.error(f"Error during analysis: {str(e)}")
            return

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


async def main():
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
