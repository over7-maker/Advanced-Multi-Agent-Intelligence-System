"""
API Fetcher Tool
Tool for making HTTP API requests
"""

import logging
from typing import Any, Dict

import aiohttp

from . import AgentTool

logger = logging.getLogger(__name__)


class APIFetcherTool(AgentTool):
    """Tool for making HTTP API requests"""
    
    def __init__(self):
        super().__init__(
            name="api_fetcher",
            description="Make HTTP API requests (GET, POST, etc.) and retrieve responses"
        )
        self.category = "data_collection"
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "API endpoint URL"
                },
                "method": {
                    "type": "string",
                    "enum": ["GET", "POST", "PUT", "PATCH", "DELETE"],
                    "description": "HTTP method",
                    "default": "GET"
                },
                "headers": {
                    "type": "object",
                    "description": "HTTP headers"
                },
                "params": {
                    "type": "object",
                    "description": "Query parameters (for GET)"
                },
                "data": {
                    "type": "object",
                    "description": "Request body data (for POST/PUT/PATCH)"
                },
                "timeout": {
                    "type": "number",
                    "description": "Request timeout in seconds",
                    "default": 30
                }
            },
            "required": ["url"]
        }
    
    def validate_params(self, params: Dict[str, Any]) -> bool:
        if "url" not in params:
            return False
        url = params["url"]
        if not isinstance(url, str) or not url.startswith(('http://', 'https://')):
            return False
        return True
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute API request"""
        try:
            if not self.validate_params(params):
                return {
                    "success": False,
                    "error": "Invalid parameters: url is required and must be http/https"
                }
            
            url = params["url"]
            method = params.get("method", "GET").upper()
            headers = params.get("headers", {})
            query_params = params.get("params", {})
            data = params.get("data")
            timeout = params.get("timeout", 30)
            
            logger.info(f"APIFetcherTool: Making {method} request to {url}")
            
            timeout_obj = aiohttp.ClientTimeout(total=timeout)
            
            result = {
                "url": url,
                "method": method,
                "status_code": None,
                "headers": {},
                "body": None,
                "error": None
            }
            
            async with aiohttp.ClientSession(timeout=timeout_obj) as session:
                try:
                    # Prepare request kwargs
                    request_kwargs = {
                        "headers": headers,
                        "params": query_params if method == "GET" else None
                    }
                    
                    if method in ["POST", "PUT", "PATCH"] and data:
                        request_kwargs["json"] = data
                    
                    # Make request
                    async with session.request(method, url, **request_kwargs) as response:
                        result["status_code"] = response.status
                        result["headers"] = dict(response.headers)
                        
                        # Try to get JSON, fallback to text
                        try:
                            result["body"] = await response.json()
                        except Exception:
                            result["body"] = await response.text()
                        
                        logger.info(f"APIFetcherTool: {method} {url} returned status {response.status}")
                        
                        return {
                            "success": response.status < 400,
                            "result": result,
                            "metadata": {
                                "url": url,
                                "method": method,
                                "status_code": response.status
                            }
                        }
                
                except aiohttp.ClientError as e:
                    error_msg = f"HTTP client error: {str(e)}"
                    logger.warning(f"APIFetcherTool: {error_msg}")
                    result["error"] = error_msg
                    return {
                        "success": False,
                        "error": error_msg,
                        "result": result
                    }
                except Exception as e:
                    error_msg = f"Request error: {str(e)}"
                    logger.error(f"APIFetcherTool: {error_msg}", exc_info=True)
                    result["error"] = error_msg
                    return {
                        "success": False,
                        "error": error_msg,
                        "result": result
                    }
        
        except Exception as e:
            logger.error(f"APIFetcherTool: Failed to fetch {params.get('url', 'unknown')}: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"API fetch failed: {str(e)}"
            }

