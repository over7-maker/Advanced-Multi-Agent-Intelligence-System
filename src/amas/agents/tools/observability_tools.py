"""
Observability Tools
Implementations for monitoring and observability: Prometheus, Grafana, Loki, Jaeger, Pyroscope
"""

import logging
import os
from typing import Any, Dict
import aiohttp

from . import AgentTool

logger = logging.getLogger(__name__)


class PrometheusTool(AgentTool):
    """Prometheus metrics collection and monitoring"""
    
    def __init__(self):
        super().__init__(
            name="prometheus",
            description="Metrics collection and monitoring"
        )
        self.category = "observability"
        self.prometheus_url = os.getenv("PROMETHEUS_URL", "http://localhost:9090")
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "PromQL query"},
                "query_type": {"type": "string", "enum": ["instant", "range"], "default": "instant"}
            },
            "required": ["query"]
        }
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Prometheus query"""
        try:
            query = params.get("query")
            if not query:
                return {"success": False, "error": "Query parameter is required"}
            
            query_type = params.get("query_type", "instant")
            
            endpoint = "/api/v1/query" if query_type == "instant" else "/api/v1/query_range"
            
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(
                        f"{self.prometheus_url}{endpoint}",
                        params={"query": query},
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            return {
                                "success": True,
                                "result": {
                                    "query": query,
                                    "data": data.get("data", {}),
                                    "result_type": data.get("data", {}).get("resultType", "")
                                }
                            }
                        return {"success": False, "error": f"Prometheus returned status {response.status}"}
                except aiohttp.ClientError as e:
                    return {
                        "success": False,
                        "error": f"Prometheus service not available at {self.prometheus_url}. Please start Prometheus service."
                    }
        except Exception as e:
            logger.error(f"Prometheus query failed: {e}")
            return {"success": False, "error": str(e)}


class GrafanaTool(AgentTool):
    """Grafana metrics visualization and dashboards"""
    
    def __init__(self):
        super().__init__(
            name="grafana",
            description="Metrics visualization and dashboards"
        )
        self.category = "observability"
        self.grafana_url = os.getenv("GRAFANA_URL", "http://localhost:3000")
        self.grafana_api_key = os.getenv("GRAFANA_API_KEY")
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "operation": {"type": "string", "enum": ["list_dashboards", "get_dashboard", "query"], "default": "list_dashboards"},
                "dashboard_id": {"type": "integer", "description": "Dashboard ID (for get_dashboard)"},
                "query": {"type": "string", "description": "Query (for query operation)"}
            },
            "required": []
        }
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Grafana operation"""
        try:
            if not self.grafana_api_key:
                return {"success": False, "error": "Grafana API key required"}
            
            operation = params.get("operation", "list_dashboards")
            headers = {"Authorization": f"Bearer {self.grafana_api_key}"}
            
            async with aiohttp.ClientSession() as session:
                if operation == "list_dashboards":
                    async with session.get(
                        f"{self.grafana_url}/api/search",
                        params={"type": "dash-db"},
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            return {
                                "success": True,
                                "result": {
                                    "dashboards": data,
                                    "count": len(data)
                                }
                            }
                
                elif operation == "get_dashboard":
                    dashboard_id = params.get("dashboard_id")
                    if not dashboard_id:
                        return {"success": False, "error": "dashboard_id required"}
                    
                    async with session.get(
                        f"{self.grafana_url}/api/dashboards/uid/{dashboard_id}",
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            return {
                                "success": True,
                                "result": {
                                    "dashboard": data.get("dashboard", {})
                                }
                            }
                
                return {"success": False, "error": f"Grafana returned status {response.status}"}
        except Exception as e:
            logger.error(f"Grafana operation failed: {e}")
            return {"success": False, "error": str(e)}


class LokiTool(AgentTool):
    """Loki log aggregation system"""
    
    def __init__(self):
        super().__init__(
            name="loki",
            description="Log aggregation system"
        )
        self.category = "observability"
        self.loki_url = os.getenv("LOKI_URL", "http://localhost:3100")
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "LogQL query"},
                "limit": {"type": "integer", "default": 100}
            },
            "required": ["query"]
        }
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Loki query"""
        try:
            query = params.get("query")
            limit = params.get("limit", 100)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.loki_url}/loki/api/v1/query_range",
                    params={"query": query, "limit": limit},
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "result": {
                                "query": query,
                                "streams": data.get("data", {}).get("result", []),
                                "count": len(data.get("data", {}).get("result", []))
                            }
                        }
                    return {"success": False, "error": f"Loki returned status {response.status}"}
        except Exception as e:
            logger.error(f"Loki query failed: {e}")
            return {"success": False, "error": str(e)}


class JaegerTool(AgentTool):
    """Jaeger distributed tracing"""
    
    def __init__(self):
        super().__init__(
            name="jaeger",
            description="Distributed tracing"
        )
        self.category = "observability"
        self.jaeger_url = os.getenv("JAEGER_URL", "http://localhost:16686")
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "operation": {"type": "string", "enum": ["search_traces", "get_trace"], "default": "search_traces"},
                "service": {"type": "string", "description": "Service name"},
                "trace_id": {"type": "string", "description": "Trace ID (for get_trace)"}
            },
            "required": []
        }
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Jaeger operation"""
        try:
            operation = params.get("operation", "search_traces")
            
            async with aiohttp.ClientSession() as session:
                if operation == "search_traces":
                    service = params.get("service", "")
                    async with session.get(
                        f"{self.jaeger_url}/api/traces",
                        params={"service": service, "limit": 20},
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            return {
                                "success": True,
                                "result": {
                                    "service": service,
                                    "traces": data.get("data", []),
                                    "count": len(data.get("data", []))
                                }
                            }
                
                elif operation == "get_trace":
                    trace_id = params.get("trace_id")
                    if not trace_id:
                        return {"success": False, "error": "trace_id required"}
                    
                    async with session.get(
                        f"{self.jaeger_url}/api/traces/{trace_id}",
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            return {
                                "success": True,
                                "result": {
                                    "trace_id": trace_id,
                                    "trace": data.get("data", [])
                                }
                            }
                
                return {"success": False, "error": f"Jaeger returned status {response.status}"}
        except Exception as e:
            logger.error(f"Jaeger operation failed: {e}")
            return {"success": False, "error": str(e)}


class PyroscopeTool(AgentTool):
    """Pyroscope continuous profiling"""
    
    def __init__(self):
        super().__init__(
            name="pyroscope",
            description="Continuous profiling"
        )
        self.category = "observability"
        self.pyroscope_url = os.getenv("PYROSCOPE_URL", "http://localhost:4040")
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Pyroscope query"},
                "from_time": {"type": "integer", "description": "Start time (Unix timestamp)"},
                "until_time": {"type": "integer", "description": "End time (Unix timestamp)"}
            },
            "required": ["query"]
        }
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Pyroscope query"""
        try:
            query = params.get("query")
            from_time = params.get("from_time")
            until_time = params.get("until_time")
            
            query_params = {"query": query}
            if from_time:
                query_params["from"] = from_time
            if until_time:
                query_params["until"] = until_time
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.pyroscope_url}/api/query",
                    params=query_params,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "result": {
                                "query": query,
                                "profiles": data
                            }
                        }
                    return {"success": False, "error": f"Pyroscope returned status {response.status}"}
        except Exception as e:
            logger.error(f"Pyroscope query failed: {e}")
            return {"success": False, "error": str(e)}

