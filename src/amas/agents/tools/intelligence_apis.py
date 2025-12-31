"""
Intelligence API Tools
Integrations with intelligence APIs: GitHub, GitLab, NPM/PyPI, OSINT sources
"""

import logging
import os
from typing import Any, Dict

import aiohttp

from . import AgentTool

logger = logging.getLogger(__name__)


class GitHubAPITool(AgentTool):
    """Tool for GitHub API integration"""
    
    def __init__(self):
        super().__init__(
            name="github_api",
            description="Query GitHub API for repositories, code, issues, and more"
        )
        self.category = "intelligence_api"
        self.api_token = os.getenv("GITHUB_TOKEN")
        self.base_url = "https://api.github.com"
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "endpoint": {
                    "type": "string",
                    "description": "GitHub API endpoint (e.g., 'repos/owner/repo', 'search/repositories')"
                },
                "method": {
                    "type": "string",
                    "enum": ["GET", "POST"],
                    "description": "HTTP method",
                    "default": "GET"
                },
                "params": {
                    "type": "object",
                    "description": "Query parameters"
                }
            },
            "required": ["endpoint"]
        }
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute GitHub API request"""
        endpoint = params.get("endpoint")
        method = params.get("method", "GET").upper()
        query_params = params.get("params", {})
        
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            headers = {
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "AMAS-Agent"
            }
            
            if self.api_token:
                headers["Authorization"] = f"token {self.api_token}"
            
            async with aiohttp.ClientSession() as session:
                if method == "GET":
                    async with session.get(url, headers=headers, params=query_params) as response:
                        return await self._handle_response(response, endpoint)
                else:
                    async with session.post(url, headers=headers, json=query_params) as response:
                        return await self._handle_response(response, endpoint)
        
        except Exception as e:
            logger.error(f"GitHub API error: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"GitHub API error: {str(e)}"
            }
    
    async def _handle_response(self, response: aiohttp.ClientResponse, endpoint: str) -> Dict[str, Any]:
        """Handle GitHub API response"""
        if response.status == 200:
            data = await response.json()
            return {
                "success": True,
                "result": data,
                "metadata": {"endpoint": endpoint, "status": response.status}
            }
        else:
            error_text = await response.text()
            return {
                "success": False,
                "error": f"GitHub API returned status {response.status}",
                "result": error_text
            }


class GitLabAPITool(AgentTool):
    """Tool for GitLab API integration"""
    
    def __init__(self):
        super().__init__(
            name="gitlab_api",
            description="Query GitLab API for projects, repositories, and more"
        )
        self.category = "intelligence_api"
        self.api_token = os.getenv("GITLAB_TOKEN")
        self.base_url = os.getenv("GITLAB_URL", "https://gitlab.com/api/v4")
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "endpoint": {
                    "type": "string",
                    "description": "GitLab API endpoint"
                },
                "params": {
                    "type": "object",
                    "description": "Query parameters"
                }
            },
            "required": ["endpoint"]
        }
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute GitLab API request"""
        endpoint = params.get("endpoint")
        query_params = params.get("params", {})
        
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            headers = {
                "Content-Type": "application/json"
            }
            
            if self.api_token:
                headers["PRIVATE-TOKEN"] = self.api_token
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=query_params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "result": data,
                            "metadata": {"endpoint": endpoint}
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"GitLab API returned status {response.status}",
                            "result": await response.text()
                        }
        
        except Exception as e:
            logger.error(f"GitLab API error: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"GitLab API error: {str(e)}"
            }


class NPMPackageTool(AgentTool):
    """Tool for NPM package information"""
    
    def __init__(self):
        super().__init__(
            name="npm_package",
            description="Get NPM package information and vulnerability data"
        )
        self.category = "intelligence_api"
        self.base_url = "https://registry.npmjs.org"
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "package_name": {
                    "type": "string",
                    "description": "NPM package name"
                },
                "version": {
                    "type": "string",
                    "description": "Package version (optional, defaults to latest)"
                }
            },
            "required": ["package_name"]
        }
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get NPM package information"""
        package_name = params.get("package_name")
        version = params.get("version")
        
        try:
            if version:
                url = f"{self.base_url}/{package_name}/{version}"
            else:
                url = f"{self.base_url}/{package_name}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "result": {
                                "name": data.get("name"),
                                "version": data.get("version") or (data.get("dist-tags", {}).get("latest") if not version else version),
                                "description": data.get("description"),
                                "dependencies": data.get("dependencies", {}),
                                "maintainers": data.get("maintainers", []),
                                "repository": data.get("repository"),
                                "homepage": data.get("homepage")
                            },
                            "metadata": {"package": package_name, "version": version}
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"NPM API returned status {response.status}"
                        }
        
        except Exception as e:
            logger.error(f"NPM API error: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"NPM API error: {str(e)}"
            }


class PyPIPackageTool(AgentTool):
    """Tool for PyPI package information"""
    
    def __init__(self):
        super().__init__(
            name="pypi_package",
            description="Get PyPI package information"
        )
        self.category = "intelligence_api"
        self.base_url = "https://pypi.org/pypi"
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "package_name": {
                    "type": "string",
                    "description": "PyPI package name"
                },
                "version": {
                    "type": "string",
                    "description": "Package version (optional, defaults to latest)"
                }
            },
            "required": ["package_name"]
        }
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get PyPI package information"""
        package_name = params.get("package_name")
        version = params.get("version")
        
        try:
            if version:
                url = f"{self.base_url}/{package_name}/{version}/json"
            else:
                url = f"{self.base_url}/{package_name}/json"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        info = data.get("info", {})
                        return {
                            "success": True,
                            "result": {
                                "name": info.get("name"),
                                "version": info.get("version"),
                                "summary": info.get("summary"),
                                "description": info.get("description"),
                                "requires_dist": info.get("requires_dist", []),
                                "author": info.get("author"),
                                "home_page": info.get("home_page"),
                                "project_urls": info.get("project_urls", {})
                            },
                            "metadata": {"package": package_name, "version": version}
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"PyPI API returned status {response.status}"
                        }
        
        except Exception as e:
            logger.error(f"PyPI API error: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"PyPI API error: {str(e)}"
            }

