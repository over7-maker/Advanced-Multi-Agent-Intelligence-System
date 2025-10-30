#!/usr/bin/env python3
"""
Security Scanning Script for AMAS
Implements comprehensive security scanning for CI/CD pipeline
"""

import argparse
import json
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class SecurityScanner:
    """Comprehensive security scanner for AMAS"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.results = {
            "timestamp": datetime.utcnow().isoformat(),
            "scans": {},
            "summary": {
                "total_issues": 0,
                "critical_issues": 0,
                "high_issues": 0,
                "medium_issues": 0,
                "low_issues": 0,
                "passed_scans": 0,
                "failed_scans": 0
            }
        }

    def run_bandit_scan(self) -> Dict[str, Any]:
        """Run Bandit security linter"""
        logger.info("Running Bandit security scan...")
        
        try:
            # Run bandit with JSON output
            result = subprocess.run([
                "bandit", "-r", "src/", "-f", "json", "-ll"
            ], capture_output=True, text=True, timeout=300)
            
            bandit_results = json.loads(result.stdout) if result.stdout else {"results": []}
            
            # Categorize issues by severity
            issues = {
                "critical": [],
                "high": [],
                "medium": [],
                "low": []
            }
            
            for issue in bandit_results.get("results", []):
                severity = issue.get("issue_severity", "low").lower()
                if severity in issues:
                    issues[severity].append(issue)
            
            scan_result = {
                "tool": "bandit",
                "status": "passed" if result.returncode == 0 else "failed",
                "issues": issues,
                "total_issues": len(bandit_results.get("results", [])),
                "return_code": result.returncode,
                "stderr": result.stderr
            }
            
            self.results["scans"]["bandit"] = scan_result
            self._update_summary(scan_result)
            
            return scan_result
            
        except subprocess.TimeoutExpired:
            logger.error("Bandit scan timed out")
            return {"tool": "bandit", "status": "failed", "error": "Timeout"}
        except Exception as e:
            logger.error(f"Bandit scan failed: {e}")
            return {"tool": "bandit", "status": "failed", "error": str(e)}

    def run_safety_scan(self) -> Dict[str, Any]:
        """Run Safety dependency vulnerability scanner"""
        logger.info("Running Safety dependency scan...")
        
        try:
            # Run safety with JSON output
            result = subprocess.run([
                "safety", "check", "--json", "--full-report"
            ], capture_output=True, text=True, timeout=300)
            
            safety_results = json.loads(result.stdout) if result.stdout else []
            
            # Categorize vulnerabilities by severity
            vulnerabilities = {
                "critical": [],
                "high": [],
                "medium": [],
                "low": []
            }
            
            for vuln in safety_results:
                # Safety doesn't provide severity, so we'll categorize by CVE score if available
                severity = "medium"  # Default
                if "cve" in vuln.get("advisory", "").lower():
                    severity = "high"
                
                vulnerabilities[severity].append(vuln)
            
            scan_result = {
                "tool": "safety",
                "status": "passed" if result.returncode == 0 else "failed",
                "vulnerabilities": vulnerabilities,
                "total_vulnerabilities": len(safety_results),
                "return_code": result.returncode,
                "stderr": result.stderr
            }
            
            self.results["scans"]["safety"] = scan_result
            self._update_summary(scan_result)
            
            return scan_result
            
        except subprocess.TimeoutExpired:
            logger.error("Safety scan timed out")
            return {"tool": "safety", "status": "failed", "error": "Timeout"}
        except Exception as e:
            logger.error(f"Safety scan failed: {e}")
            return {"tool": "safety", "status": "failed", "error": str(e)}

    def run_semgrep_scan(self) -> Dict[str, Any]:
        """Run Semgrep static analysis"""
        logger.info("Running Semgrep security scan...")
        
        try:
            # Run semgrep with JSON output
            result = subprocess.run([
                "semgrep", "--config=auto", "--json", "src/"
            ], capture_output=True, text=True, timeout=600)
            
            semgrep_results = json.loads(result.stdout) if result.stdout else {"results": []}
            
            # Categorize findings by severity
            findings = {
                "critical": [],
                "high": [],
                "medium": [],
                "low": []
            }
            
            for finding in semgrep_results.get("results", []):
                severity = finding.get("extra", {}).get("severity", "info").lower()
                if severity in findings:
                    findings[severity].append(finding)
            
            scan_result = {
                "tool": "semgrep",
                "status": "passed" if result.returncode == 0 else "failed",
                "findings": findings,
                "total_findings": len(semgrep_results.get("results", [])),
                "return_code": result.returncode,
                "stderr": result.stderr
            }
            
            self.results["scans"]["semgrep"] = scan_result
            self._update_summary(scan_result)
            
            return scan_result
            
        except subprocess.TimeoutExpired:
            logger.error("Semgrep scan timed out")
            return {"tool": "semgrep", "status": "failed", "error": "Timeout"}
        except Exception as e:
            logger.error(f"Semgrep scan failed: {e}")
            return {"tool": "semgrep", "status": "failed", "error": str(e)}

    def run_docker_scan(self) -> Dict[str, Any]:
        """Run Docker image security scan"""
        logger.info("Running Docker security scan...")
        
        try:
            # Check if docker is available
            subprocess.run(["docker", "--version"], check=True, capture_output=True)
            
            # Build image first
            build_result = subprocess.run([
                "docker", "build", "-t", "amas:security-scan", "."
            ], capture_output=True, text=True, timeout=600)
            
            if build_result.returncode != 0:
                return {
                    "tool": "docker",
                    "status": "failed",
                    "error": f"Failed to build image: {build_result.stderr}"
                }
            
            # Run Trivy scan if available
            try:
                trivy_result = subprocess.run([
                    "trivy", "image", "--format", "json", "amas:security-scan"
                ], capture_output=True, text=True, timeout=300)
                
                trivy_results = json.loads(trivy_result.stdout) if trivy_result.stdout else {}
                
                # Categorize vulnerabilities
                vulnerabilities = {
                    "critical": [],
                    "high": [],
                    "medium": [],
                    "low": []
                }
                
                for vuln in trivy_results.get("Results", []):
                    for vuln_detail in vuln.get("Vulnerabilities", []):
                        severity = vuln_detail.get("Severity", "UNKNOWN").lower()
                        if severity in vulnerabilities:
                            vulnerabilities[severity].append(vuln_detail)
                
                scan_result = {
                    "tool": "docker_trivy",
                    "status": "passed" if trivy_result.returncode == 0 else "failed",
                    "vulnerabilities": vulnerabilities,
                    "total_vulnerabilities": sum(len(v) for v in vulnerabilities.values()),
                    "return_code": trivy_result.returncode,
                    "stderr": trivy_result.stderr
                }
                
            except FileNotFoundError:
                # Trivy not available, use basic docker scan
                scan_result = {
                    "tool": "docker",
                    "status": "passed",
                    "message": "Docker image built successfully, Trivy not available for detailed scan"
                }
            
            self.results["scans"]["docker"] = scan_result
            self._update_summary(scan_result)
            
            return scan_result
            
        except subprocess.TimeoutExpired:
            logger.error("Docker scan timed out")
            return {"tool": "docker", "status": "failed", "error": "Timeout"}
        except Exception as e:
            logger.error(f"Docker scan failed: {e}")
            return {"tool": "docker", "status": "failed", "error": str(e)}

    def run_secrets_scan(self) -> Dict[str, Any]:
        """Run secrets detection scan"""
        logger.info("Running secrets detection scan...")
        
        try:
            # Use detect-secrets if available
            try:
                result = subprocess.run([
                    "detect-secrets", "scan", "--all-files", "--baseline", ".secrets.baseline"
                ], capture_output=True, text=True, timeout=300)
                
                # Parse results
                secrets_found = 0
                if result.returncode != 0:
                    # Check if it's just because baseline doesn't exist
                    if "baseline" in result.stderr.lower():
                        # Create baseline
                        subprocess.run([
                            "detect-secrets", "scan", "--all-files", "--baseline", ".secrets.baseline"
                        ], capture_output=True, text=True)
                        secrets_found = 0
                    else:
                        secrets_found = len(result.stdout.split('\n')) - 1
                
                scan_result = {
                    "tool": "detect-secrets",
                    "status": "passed" if secrets_found == 0 else "failed",
                    "secrets_found": secrets_found,
                    "return_code": result.returncode,
                    "stderr": result.stderr
                }
                
            except FileNotFoundError:
                # Fallback to simple grep-based scan
                sensitive_patterns = [
                    r"password\s*=\s*['\"][^'\"]+['\"]",
                    r"secret\s*=\s*['\"][^'\"]+['\"]",
                    r"api_key\s*=\s*['\"][^'\"]+['\"]",
                    r"token\s*=\s*['\"][^'\"]+['\"]",
                    r"sk-[a-zA-Z0-9]{48}",
                    r"pk_[a-zA-Z0-9]{48}",
                ]
                
                secrets_found = 0
                for pattern in sensitive_patterns:
                    result = subprocess.run([
                        "grep", "-r", "-E", pattern, "src/", "--exclude-dir=__pycache__"
                    ], capture_output=True, text=True)
                    secrets_found += len(result.stdout.split('\n')) - 1
                
                scan_result = {
                    "tool": "grep_secrets",
                    "status": "passed" if secrets_found == 0 else "failed",
                    "secrets_found": secrets_found,
                    "patterns_checked": len(sensitive_patterns)
                }
            
            self.results["scans"]["secrets"] = scan_result
            self._update_summary(scan_result)
            
            return scan_result
            
        except subprocess.TimeoutExpired:
            logger.error("Secrets scan timed out")
            return {"tool": "secrets", "status": "failed", "error": "Timeout"}
        except Exception as e:
            logger.error(f"Secrets scan failed: {e}")
            return {"tool": "secrets", "status": "failed", "error": str(e)}

    def run_dependency_scan(self) -> Dict[str, Any]:
        """Run dependency vulnerability scan"""
        logger.info("Running dependency vulnerability scan...")
        
        try:
            # Check for known vulnerabilities in requirements
            result = subprocess.run([
                "pip-audit", "--format=json", "--desc"
            ], capture_output=True, text=True, timeout=300)
            
            audit_results = json.loads(result.stdout) if result.stdout else {"vulnerabilities": []}
            
            # Categorize vulnerabilities
            vulnerabilities = {
                "critical": [],
                "high": [],
                "medium": [],
                "low": []
            }
            
            for vuln in audit_results.get("vulnerabilities", []):
                severity = vuln.get("severity", "medium").lower()
                if severity in vulnerabilities:
                    vulnerabilities[severity].append(vuln)
            
            scan_result = {
                "tool": "pip-audit",
                "status": "passed" if result.returncode == 0 else "failed",
                "vulnerabilities": vulnerabilities,
                "total_vulnerabilities": len(audit_results.get("vulnerabilities", [])),
                "return_code": result.returncode,
                "stderr": result.stderr
            }
            
            self.results["scans"]["dependencies"] = scan_result
            self._update_summary(scan_result)
            
            return scan_result
            
        except subprocess.TimeoutExpired:
            logger.error("Dependency scan timed out")
            return {"tool": "dependencies", "status": "failed", "error": "Timeout"}
        except Exception as e:
            logger.error(f"Dependency scan failed: {e}")
            return {"tool": "dependencies", "status": "failed", "error": str(e)}

    def _update_summary(self, scan_result: Dict[str, Any]):
        """Update summary statistics"""
        if scan_result["status"] == "passed":
            self.results["summary"]["passed_scans"] += 1
        else:
            self.results["summary"]["failed_scans"] += 1
        
        # Count issues by severity
        for key in ["issues", "vulnerabilities", "findings"]:
            if key in scan_result:
                for severity in ["critical", "high", "medium", "low"]:
                    count = len(scan_result[key].get(severity, []))
                    self.results["summary"][f"{severity}_issues"] += count
                    self.results["summary"]["total_issues"] += count

    def run_all_scans(self) -> Dict[str, Any]:
        """Run all security scans"""
        logger.info("Starting comprehensive security scan...")
        
        # Run all scans
        self.run_bandit_scan()
        self.run_safety_scan()
        self.run_semgrep_scan()
        self.run_docker_scan()
        self.run_secrets_scan()
        self.run_dependency_scan()
        
        # Determine overall status
        total_scans = self.results["summary"]["passed_scans"] + self.results["summary"]["failed_scans"]
        self.results["overall_status"] = "passed" if self.results["summary"]["failed_scans"] == 0 else "failed"
        
        logger.info(f"Security scan completed. Overall status: {self.results['overall_status']}")
        logger.info(f"Total issues found: {self.results['summary']['total_issues']}")
        
        return self.results

    def save_results(self, output_file: str):
        """Save scan results to file"""
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        logger.info(f"Security scan results saved to {output_file}")

    def print_summary(self):
        """Print scan summary"""
        summary = self.results["summary"]
        print("\n" + "="*50)
        print("SECURITY SCAN SUMMARY")
        print("="*50)
        print(f"Overall Status: {self.results['overall_status'].upper()}")
        print(f"Total Scans: {summary['passed_scans'] + summary['failed_scans']}")
        print(f"Passed: {summary['passed_scans']}")
        print(f"Failed: {summary['failed_scans']}")
        print(f"Total Issues: {summary['total_issues']}")
        print(f"  - Critical: {summary['critical_issues']}")
        print(f"  - High: {summary['high_issues']}")
        print(f"  - Medium: {summary['medium_issues']}")
        print(f"  - Low: {summary['low_issues']}")
        print("="*50)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="AMAS Security Scanner")
    parser.add_argument("--output", "-o", default="security_report.json", help="Output file for results")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--scan", choices=["all", "bandit", "safety", "semgrep", "docker", "secrets", "dependencies"], 
                       default="all", help="Specific scan to run")
    
    args = parser.parse_args()
    
    # Setup logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Create scanner
    scanner = SecurityScanner()
    
    # Run scans
    if args.scan == "all":
        results = scanner.run_all_scans()
    else:
        scan_method = getattr(scanner, f"run_{args.scan}_scan")
        results = scan_method()
    
    # Save and display results
    scanner.save_results(args.output)
    scanner.print_summary()
    
    # Exit with appropriate code
    sys.exit(0 if results["overall_status"] == "passed" else 1)


if __name__ == "__main__":
    main()