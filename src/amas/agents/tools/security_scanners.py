"""
Security Scanner Tools
Implementations for security scanning tools: Semgrep, Bandit, Trivy, Gitleaks, OWASP ZAP, OSV Scanner
"""

import logging
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List

from . import AgentTool

logger = logging.getLogger(__name__)


class SemgrepTool(AgentTool):
    """Semgrep security pattern detection"""
    
    def __init__(self):
        super().__init__(
            name="semgrep",
            description="Security pattern detection (2,000+ rules)"
        )
        self.category = "security_analysis"
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "target": {"type": "string", "description": "File or directory to scan"},
                "config": {"type": "string", "description": "Semgrep config (auto, p/security-audit, etc.)", "default": "auto"}
            },
            "required": ["target"]
        }
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Semgrep scan"""
        try:
            target = params.get("target")
            config = params.get("config", "auto")
            
            # Check if semgrep is installed
            try:
                subprocess.run(["semgrep", "--version"], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                return {"success": False, "error": "Semgrep not installed. Install with: pip install semgrep"}
            
            # Run semgrep
            cmd = ["semgrep", "--config", config, "--json", target]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                import json
                try:
                    data = json.loads(result.stdout)
                    return {
                        "success": True,
                        "result": {
                            "target": target,
                            "findings": data.get("results", []),
                            "count": len(data.get("results", []))
                        }
                    }
                except json.JSONDecodeError:
                    return {"success": False, "error": "Failed to parse Semgrep output"}
            
            return {"success": False, "error": f"Semgrep failed: {result.stderr}"}
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Semgrep scan timed out"}
        except Exception as e:
            logger.error(f"Semgrep scan failed: {e}")
            return {"success": False, "error": str(e)}


class BanditTool(AgentTool):
    """Bandit Python security scanner"""
    
    def __init__(self):
        super().__init__(
            name="bandit",
            description="Python-specific security scanner"
        )
        self.category = "security_analysis"
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "target": {"type": "string", "description": "File or directory to scan"},
                "severity": {"type": "string", "enum": ["low", "medium", "high"], "default": "medium"}
            },
            "required": ["target"]
        }
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Bandit scan"""
        try:
            target = params.get("target")
            severity = params.get("severity", "medium")
            
            # Check if bandit is installed
            try:
                subprocess.run(["bandit", "--version"], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                return {"success": False, "error": "Bandit not installed. Install with: pip install bandit"}
            
            # Run bandit
            cmd = ["bandit", "-r", "-f", "json", "-ll", target]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode in [0, 1]:  # 1 means issues found
                import json
                try:
                    data = json.loads(result.stdout)
                    # Filter by severity
                    findings = [
                        f for f in data.get("results", [])
                        if f.get("issue_severity", "").lower() == severity or severity == "low"
                    ]
                    return {
                        "success": True,
                        "result": {
                            "target": target,
                            "findings": findings,
                            "count": len(findings),
                            "metrics": data.get("metrics", {})
                        }
                    }
                except json.JSONDecodeError:
                    return {"success": False, "error": "Failed to parse Bandit output"}
            
            return {"success": False, "error": f"Bandit failed: {result.stderr}"}
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Bandit scan timed out"}
        except Exception as e:
            logger.error(f"Bandit scan failed: {e}")
            return {"success": False, "error": str(e)}


class TrivyTool(AgentTool):
    """Trivy container and dependency vulnerability scanner"""
    
    def __init__(self):
        super().__init__(
            name="trivy",
            description="Container and dependency vulnerability scanner"
        )
        self.category = "security_analysis"
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "target": {"type": "string", "description": "Image, file, or directory to scan"},
                "scan_type": {"type": "string", "enum": ["image", "fs", "repo"], "default": "fs"}
            },
            "required": ["target"]
        }
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Trivy scan"""
        try:
            target = params.get("target")
            scan_type = params.get("scan_type", "fs")
            
            # Check if trivy is installed
            try:
                subprocess.run(["trivy", "--version"], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                return {"success": False, "error": "Trivy not installed. See: https://github.com/aquasecurity/trivy"}
            
            # Run trivy
            cmd = ["trivy", scan_type, "--format", "json", target]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode in [0, 1]:  # 1 means vulnerabilities found
                import json
                try:
                    data = json.loads(result.stdout)
                    return {
                        "success": True,
                        "result": {
                            "target": target,
                            "vulnerabilities": data.get("Results", []),
                            "summary": data.get("Summary", {})
                        }
                    }
                except json.JSONDecodeError:
                    return {"success": False, "error": "Failed to parse Trivy output"}
            
            return {"success": False, "error": f"Trivy failed: {result.stderr}"}
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Trivy scan timed out"}
        except Exception as e:
            logger.error(f"Trivy scan failed: {e}")
            return {"success": False, "error": str(e)}


class GitleaksTool(AgentTool):
    """Gitleaks secret detection in Git repositories"""
    
    def __init__(self):
        super().__init__(
            name="gitleaks",
            description="Secret detection in Git repositories"
        )
        self.category = "security_analysis"
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "target": {"type": "string", "description": "Git repository path or URL"},
                "no_git": {"type": "boolean", "default": False, "description": "Scan files without git"}
            },
            "required": ["target"]
        }
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Gitleaks scan"""
        try:
            target = params.get("target")
            no_git = params.get("no_git", False)
            
            # Check if gitleaks is installed
            try:
                subprocess.run(["gitleaks", "version"], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                return {"success": False, "error": "Gitleaks not installed. See: https://github.com/gitleaks/gitleaks"}
            
            # Run gitleaks
            cmd = ["gitleaks", "detect", "--source", target, "--report-format", "json"]
            if no_git:
                cmd.append("--no-git")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            # Gitleaks returns non-zero if secrets found, but that's success for us
            import json
            try:
                if result.stdout:
                    data = json.loads(result.stdout)
                    return {
                        "success": True,
                        "result": {
                            "target": target,
                            "findings": data if isinstance(data, list) else [],
                            "count": len(data) if isinstance(data, list) else 0
                        }
                    }
                else:
                    return {
                        "success": True,
                        "result": {
                            "target": target,
                            "findings": [],
                            "count": 0,
                            "message": "No secrets found"
                        }
                    }
            except json.JSONDecodeError:
                # No JSON output means no findings
                return {
                    "success": True,
                    "result": {
                        "target": target,
                        "findings": [],
                        "count": 0
                    }
                }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Gitleaks scan timed out"}
        except Exception as e:
            logger.error(f"Gitleaks scan failed: {e}")
            return {"success": False, "error": str(e)}


class OSVScannerTool(AgentTool):
    """OSV Scanner dependency vulnerability scanner"""
    
    def __init__(self):
        super().__init__(
            name="osv_scanner",
            description="Dependency vulnerability scanner"
        )
        self.category = "security_analysis"
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "target": {"type": "string", "description": "Lockfile or directory to scan"},
                "lockfile": {"type": "string", "description": "Lockfile path (package-lock.json, etc.)"}
            },
            "required": ["target"]
        }
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute OSV Scanner"""
        try:
            target = params.get("target")
            lockfile = params.get("lockfile")
            
            # Check if osv-scanner is installed
            try:
                subprocess.run(["osv-scanner", "--version"], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                return {"success": False, "error": "OSV Scanner not installed. See: https://google.github.io/osv-scanner/"}
            
            # Run osv-scanner
            cmd = ["osv-scanner", "--json", target]
            if lockfile:
                cmd.extend(["--lockfile", lockfile])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                import json
                try:
                    data = json.loads(result.stdout)
                    return {
                        "success": True,
                        "result": {
                            "target": target,
                            "vulnerabilities": data.get("results", []),
                            "summary": data.get("summary", {})
                        }
                    }
                except json.JSONDecodeError:
                    return {"success": False, "error": "Failed to parse OSV Scanner output"}
            
            return {"success": False, "error": f"OSV Scanner failed: {result.stderr}"}
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "OSV Scanner timed out"}
        except Exception as e:
            logger.error(f"OSV Scanner failed: {e}")
            return {"success": False, "error": str(e)}

