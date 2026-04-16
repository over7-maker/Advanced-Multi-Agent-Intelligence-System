"""
Advanced Security Tools
SonarQube and OWASP ZAP implementations
"""

import logging
import os
import subprocess
from typing import Any, Dict
import aiohttp

from . import AgentTool

logger = logging.getLogger(__name__)


class SonarQubeTool(AgentTool):
    """SonarQube code quality and security analysis"""
    
    def __init__(self):
        super().__init__(
            name="sonarqube",
            description="Code quality and security analysis (40+ languages)"
        )
        self.category = "security_analysis"
        self.sonar_url = os.getenv("SONARQUBE_URL", "http://localhost:9000")
        self.sonar_token = os.getenv("SONARQUBE_TOKEN")
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "project_key": {"type": "string", "description": "SonarQube project key"},
                "target": {"type": "string", "description": "Code directory to analyze"}
            },
            "required": ["target"]
        }
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute SonarQube analysis"""
        try:
            target = params.get("target")
            project_key = params.get("project_key", "default-project")
            
            # Check if sonar-scanner is installed
            try:
                subprocess.run(["sonar-scanner", "--version"], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                return {"success": False, "error": "SonarQube scanner not installed. See: https://docs.sonarqube.org"}
            
            # Create sonar-project.properties if needed
            props_file = os.path.join(target, "sonar-project.properties")
            if not os.path.exists(props_file):
                with open(props_file, 'w') as f:
                    f.write(f"sonar.projectKey={project_key}\n")
                    f.write(f"sonar.sources=.\n")
                    if self.sonar_url:
                        f.write(f"sonar.host.url={self.sonar_url}\n")
                    if self.sonar_token:
                        f.write(f"sonar.login={self.sonar_token}\n")
            
            # Run sonar-scanner
            result = subprocess.run(
                ["sonar-scanner", f"-Dproject.settings={props_file}"],
                cwd=target,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode == 0:
                # Try to get results from SonarQube API
                if self.sonar_url and self.sonar_token:
                    try:
                        async with aiohttp.ClientSession() as session:
                            async with session.get(
                                f"{self.sonar_url}/api/issues/search",
                                params={"componentKeys": project_key},
                                auth=aiohttp.BasicAuth(self.sonar_token, ""),
                                timeout=aiohttp.ClientTimeout(total=30)
                            ) as response:
                                if response.status == 200:
                                    data = await response.json()
                                    return {
                                        "success": True,
                                        "result": {
                                            "project_key": project_key,
                                            "issues": data.get("issues", []),
                                            "count": data.get("total", 0)
                                        }
                                    }
                    except Exception as e:
                        logger.warning(f"Failed to fetch SonarQube API results: {e}")
                
                return {
                    "success": True,
                    "result": {
                        "project_key": project_key,
                        "message": "Analysis completed. Check SonarQube dashboard for results.",
                        "output": result.stdout
                    }
                }
            
            return {"success": False, "error": f"SonarQube scan failed: {result.stderr}"}
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "SonarQube scan timed out"}
        except Exception as e:
            logger.error(f"SonarQube scan failed: {e}")
            return {"success": False, "error": str(e)}


class OWASPZAPTool(AgentTool):
    """OWASP ZAP web application security testing"""
    
    def __init__(self):
        super().__init__(
            name="owasp_zap",
            description="Web application security testing"
        )
        self.category = "security_analysis"
        self.zap_url = os.getenv("ZAP_URL", "http://localhost:8080")
        self.zap_api_key = os.getenv("ZAP_API_KEY")
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "target_url": {"type": "string", "description": "URL to scan"},
                "scan_type": {"type": "string", "enum": ["spider", "active", "passive"], "default": "spider"}
            },
            "required": ["target_url"]
        }
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute OWASP ZAP scan"""
        try:
            target_url = params.get("target_url")
            scan_type = params.get("scan_type", "spider")
            
            # Check if ZAP is available via API
            api_url = f"{self.zap_url}/JSON"
            headers = {}
            if self.zap_api_key:
                headers["X-ZAP-API-Key"] = self.zap_api_key
            
            async with aiohttp.ClientSession() as session:
                # Start spider scan
                if scan_type == "spider":
                    async with session.get(
                        f"{api_url}/spider/action/scan",
                        params={"url": target_url},
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            scan_id = data.get("scan")
                            
                            # Wait for scan to complete
                            import asyncio
                            for _ in range(60):  # Wait up to 5 minutes
                                await asyncio.sleep(5)
                                async with session.get(
                                    f"{api_url}/spider/view/status",
                                    params={"scanId": scan_id},
                                    headers=headers
                                ) as status_response:
                                    if status_response.status == 200:
                                        status_data = await status_response.json()
                                        if int(status_data.get("status", 100)) >= 100:
                                            break
                            
                            # Get results
                            async with session.get(
                                f"{api_url}/spider/view/results",
                                params={"scanId": scan_id},
                                headers=headers
                            ) as results_response:
                                if results_response.status == 200:
                                    results_data = await results_response.json()
                                    return {
                                        "success": True,
                                        "result": {
                                            "target_url": target_url,
                                            "urls_found": results_data.get("results", []),
                                            "count": len(results_data.get("results", []))
                                        }
                                    }
                
                # Get alerts (vulnerabilities)
                async with session.get(
                    f"{api_url}/core/view/alerts",
                    params={"baseurl": target_url},
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as alerts_response:
                    if alerts_response.status == 200:
                        alerts_data = await alerts_response.json()
                        return {
                            "success": True,
                            "result": {
                                "target_url": target_url,
                                "alerts": alerts_data.get("alerts", []),
                                "count": len(alerts_data.get("alerts", []))
                            }
                        }
                
                return {"success": False, "error": "ZAP API not accessible or scan failed"}
        except Exception as e:
            logger.error(f"OWASP ZAP scan failed: {e}")
            return {"success": False, "error": str(e)}

