"""
AgenticSeek Tool
Autonomous web browsing and research tool
"""

import logging
import os
from typing import Any, Dict
import aiohttp

from . import AgentTool

logger = logging.getLogger(__name__)


class AgenticSeekTool(AgentTool):
    """AgenticSeek autonomous web browsing and research"""
    
    def __init__(self):
        super().__init__(
            name="agenticseek",
            description="Autonomous web browsing and research with local AI"
        )
        self.category = "web_research"
        self.base_url = os.getenv("AGENTICSEEK_URL", "http://localhost:8000")
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Research query"},
                "depth": {"type": "string", "enum": ["shallow", "medium", "deep"], "default": "medium"},
                "max_results": {"type": "integer", "default": 10}
            },
            "required": ["query"]
        }
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute AgenticSeek research"""
        try:
            query = params.get("query")
            depth = params.get("depth", "medium")
            max_results = params.get("max_results", 10)
            
            # Check if AgenticSeek service is available
            async with aiohttp.ClientSession() as session:
                try:
                    # Try health check first
                    async with session.get(
                        f"{self.base_url}/health",
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as health_response:
                        if health_response.status != 200:
                            return {"success": False, "error": "AgenticSeek service not available"}
                except Exception:
                    return {"success": False, "error": "AgenticSeek service not reachable"}
                
                # Execute research
                async with session.post(
                    f"{self.base_url}/research",
                    json={
                        "query": query,
                        "depth": depth,
                        "max_results": max_results
                    },
                    timeout=aiohttp.ClientTimeout(total=300)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "result": {
                                "query": query,
                                "findings": data.get("findings", []),
                                "sources": data.get("sources", []),
                                "analysis": data.get("analysis", ""),
                                "screenshots": data.get("screenshots", []),
                                "confidence": data.get("confidence", 0.8)
                            }
                        }
                    return {"success": False, "error": f"AgenticSeek returned status {response.status}"}
        except aiohttp.ClientError as e:
            logger.error(f"AgenticSeek request failed: {e}")
            return {"success": False, "error": f"Network error: {str(e)}"}
        except Exception as e:
            logger.error(f"AgenticSeek research failed: {e}")
            return {"success": False, "error": str(e)}

