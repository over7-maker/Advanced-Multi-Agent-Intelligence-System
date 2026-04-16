"""
OSINT Tools
Implementations for OSINT tools: FOFA, ZoomEye, Netlas, Criminal IP
"""

import base64
import logging
import os
from typing import Any, Dict
import aiohttp

from . import AgentTool

logger = logging.getLogger(__name__)


class FOFATool(AgentTool):
    """FOFA cyberspace mapping and asset discovery"""
    
    def __init__(self):
        super().__init__(
            name="fofa",
            description="FOFA cyberspace mapping and asset discovery"
        )
        self.category = "osint"
        self.email = os.getenv("FOFA_EMAIL")
        self.api_key = os.getenv("FOFA_API_KEY")
        self.base_url = "https://fofa.info/api/v1"
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "FOFA query"},
                "size": {"type": "integer", "default": 100, "description": "Number of results"}
            },
            "required": ["query"]
        }
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute FOFA search"""
        try:
            if not self.email or not self.api_key:
                return {"success": False, "error": "FOFA email and API key required"}
            
            query = params.get("query")
            size = params.get("size", 100)
            
            # Encode query to base64
            query_bytes = base64.b64encode(query.encode()).decode()
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/search/all",
                    params={
                        "qbase64": query_bytes,
                        "email": self.email,
                        "key": self.api_key,
                        "size": size
                    },
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": data.get("error", False) is False,
                            "result": {
                                "query": query,
                                "results": data.get("results", []),
                                "size": data.get("size", 0)
                            },
                            "error": data.get("errmsg") if data.get("error") else None
                        }
                    return {"success": False, "error": f"HTTP {response.status}"}
        except Exception as e:
            logger.error(f"FOFA search failed: {e}")
            return {"success": False, "error": str(e)}


class ZoomEyeTool(AgentTool):
    """ZoomEye cyberspace fingerprinting"""
    
    def __init__(self):
        super().__init__(
            name="zoomeye",
            description="Cyberspace fingerprinting"
        )
        self.category = "osint"
        self.api_key = os.getenv("ZOOMEYE_API_KEY")
        self.base_url = "https://api.zoomeye.org"
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "ZoomEye query"},
                "page": {"type": "integer", "default": 1}
            },
            "required": ["query"]
        }
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute ZoomEye search"""
        try:
            if not self.api_key:
                return {"success": False, "error": "ZoomEye API key required"}
            
            query = params.get("query")
            page = params.get("page", 1)
            
            headers = {"API-KEY": self.api_key}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/host/search",
                    params={"query": query, "page": page},
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "result": {
                                "query": query,
                                "results": data.get("matches", []),
                                "total": data.get("total", 0)
                            }
                        }
                    return {"success": False, "error": f"HTTP {response.status}"}
        except Exception as e:
            logger.error(f"ZoomEye search failed: {e}")
            return {"success": False, "error": str(e)}


class NetlasTool(AgentTool):
    """Netlas Attack Surface Management"""
    
    def __init__(self):
        super().__init__(
            name="netlas",
            description="Attack Surface Management focused"
        )
        self.category = "osint"
        self.api_key = os.getenv("NETLAS_API_KEY")
        self.base_url = "https://app.netlas.io/api"
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Netlas query"},
                "max_results": {"type": "integer", "default": 10}
            },
            "required": ["query"]
        }
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Netlas search"""
        try:
            if not self.api_key:
                return {"success": False, "error": "Netlas API key required"}
            
            query = params.get("query")
            headers = {"X-API-Key": self.api_key}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/responses",
                    params={"q": query, "start": 0, "fields": "*"},
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = data.get("items", [])[:params.get("max_results", 10)]
                        return {
                            "success": True,
                            "result": {
                                "query": query,
                                "results": results,
                                "count": len(results)
                            }
                        }
                    return {"success": False, "error": f"HTTP {response.status}"}
        except Exception as e:
            logger.error(f"Netlas search failed: {e}")
            return {"success": False, "error": str(e)}


class CriminalIPTool(AgentTool):
    """Criminal IP threat intelligence"""
    
    def __init__(self):
        super().__init__(
            name="criminal_ip",
            description="Threat intelligence and context (100 queries/month free)"
        )
        self.category = "osint"
        self.api_key = os.getenv("CRIMINAL_IP_API_KEY")
        self.base_url = "https://api.criminalip.io/v1"
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "ip": {"type": "string", "description": "IP address to check"},
                "query": {"type": "string", "description": "Search query"}
            },
            "required": []
        }
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Criminal IP lookup"""
        try:
            if not self.api_key:
                return {"success": False, "error": "Criminal IP API key required"}
            
            headers = {"x-api-key": self.api_key}
            
            # IP lookup
            if "ip" in params:
                ip = params["ip"]
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{self.base_url}/ip/data",
                        params={"ip": ip},
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            return {
                                "success": True,
                                "result": {
                                    "ip": ip,
                                    "data": data
                                }
                            }
                        return {"success": False, "error": f"HTTP {response.status}"}
            
            # Search query
            elif "query" in params:
                query = params["query"]
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{self.base_url}/domain/search",
                        params={"query": query},
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            return {
                                "success": True,
                                "result": {
                                    "query": query,
                                    "results": data.get("data", {}).get("result", [])
                                }
                            }
                        return {"success": False, "error": f"HTTP {response.status}"}
            
            return {"success": False, "error": "Either 'ip' or 'query' parameter required"}
        except Exception as e:
            logger.error(f"Criminal IP lookup failed: {e}")
            return {"success": False, "error": str(e)}

