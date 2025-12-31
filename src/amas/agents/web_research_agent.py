"""
Web Research Agent with AgenticSeek Integration (AMAS v3.0)
Autonomous web browsing and research capabilities
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

import aiohttp
from bs4 import BeautifulSoup

from src.amas.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class WebResearchAgent(BaseAgent):
    """
    Web Research Agent with AgenticSeek integration
    
    Features:
    - Autonomous web browsing
    - Local AI agent (Ollama integration)
    - Privacy-first research
    - Screenshot capture
    """
    
    def __init__(self):
        super().__init__(
            agent_id="web_research",
            name="Web Research Agent",
            agent_type="web_research",
            system_prompt="""You are a web research specialist agent. Your role is to:
1. Conduct autonomous web browsing and research
2. Extract and analyze information from web pages
3. Provide comprehensive research reports
4. Maintain privacy-first approach
5. Capture screenshots when needed for documentation

You use AgenticSeek for autonomous browsing and local AI models for privacy.""",
            model_preference=None,  # Use local models first
            strategy="quality_first"
        )
        
        # AgenticSeek configuration
        self.agenticseek_url = "http://localhost:8000"  # Default AgenticSeek URL
        self.ollama_url = "http://localhost:11434"  # Default Ollama URL
        self.browser_headless = True
        self.max_retries = 3
        self.timeout_seconds = 30
        
        # Check if AgenticSeek is available
        self.agenticseek_available = False
        asyncio.create_task(self._check_agenticseek_availability())
    
    async def _check_agenticseek_availability(self):
        """Check if AgenticSeek service is available"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.agenticseek_url}/health",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        self.agenticseek_available = True
                        logger.info("AgenticSeek service is available")
                    else:
                        logger.warning(f"AgenticSeek health check returned {response.status}")
        except Exception as e:
            logger.warning(f"AgenticSeek not available: {e}")
            self.agenticseek_available = False
    
    async def _prepare_prompt(
        self,
        target: str,
        parameters: Dict[str, Any]
    ) -> str:
        """Prepare research prompt"""
        query = parameters.get("query", target)
        depth = parameters.get("depth", "medium")  # shallow, medium, deep
        max_results = parameters.get("max_results", 10)
        
        prompt = f"""Conduct comprehensive web research on: {query}

Research Requirements:
- Research depth: {depth}
- Maximum results: {max_results}
- Focus areas: {parameters.get('focus_areas', 'general information')}
- Language: {parameters.get('language', 'English')}

Please provide:
1. Summary of findings
2. Key information extracted
3. Sources and references
4. Confidence level
5. Recommendations for further research

Query: {query}"""
        
        return prompt
    
    async def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response into structured format"""
        try:
            import json
            
            # Try to parse as JSON first
            if response.strip().startswith("{"):
                parsed = json.loads(response)
                return {
                    "success": True,
                    "analysis": parsed.get("analysis", response),
                    "findings": parsed.get("findings", []),
                    "sources": parsed.get("sources", []),
                    "confidence": parsed.get("confidence", 0.8),
                    "recommendations": parsed.get("recommendations", []),
                    "quality_score": parsed.get("quality_score", 0.85)
                }
            
            # Fallback: parse as text
            return {
                "success": True,
                "analysis": response,
                "findings": [],
                "sources": [],
                "confidence": 0.7,
                "recommendations": [],
                "quality_score": 0.75
            }
        except Exception as e:
            logger.error(f"Failed to parse response: {e}")
            return {
                "success": False,
                "error": str(e),
                "analysis": response,
                "quality_score": 0.5
            }
    
    async def research(
        self,
        query: str,
        depth: str = "medium",
        max_results: int = 10,
        use_agenticseek: bool = True
    ) -> Dict[str, Any]:
        """
        Conduct web research
        
        Args:
            query: Research query
            depth: Research depth (shallow, medium, deep)
            max_results: Maximum number of results
            use_agenticseek: Whether to use AgenticSeek for autonomous browsing
            
        Returns:
            Research results with findings, sources, and analysis
        """
        try:
            # If AgenticSeek is available, use it
            if use_agenticseek and self.agenticseek_available:
                return await self._research_with_agenticseek(query, depth, max_results)
            
            # Fallback to AI-powered research
            return await self._research_with_ai(query, depth, max_results)
        
        except Exception as e:
            logger.error(f"Research failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "findings": []
            }
    
    async def _research_with_agenticseek(
        self,
        query: str,
        depth: str,
        max_results: int
    ) -> Dict[str, Any]:
        """Research using AgenticSeek autonomous browsing"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.agenticseek_url}/research",
                    json={
                        "query": query,
                        "depth": depth,
                        "max_results": max_results
                    },
                    timeout=aiohttp.ClientTimeout(total=self.timeout_seconds)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "query": query,
                            "findings": data.get("findings", []),
                            "sources": data.get("sources", []),
                            "analysis": data.get("analysis", ""),
                            "screenshots": data.get("screenshots", []),
                            "confidence": data.get("confidence", 0.8),
                            "method": "agenticseek"
                        }
                    else:
                        raise Exception(f"AgenticSeek returned status {response.status}")
        except Exception as e:
            logger.warning(f"AgenticSeek research failed: {e}, falling back to AI")
            return await self._research_with_ai(query, depth, max_results)
    
    async def _research_with_ai(
        self,
        query: str,
        depth: str,
        max_results: int
    ) -> Dict[str, Any]:
        """Research using AI (fallback when AgenticSeek unavailable)"""
        # Use base agent execute method with research parameters
        result = await self.execute(
            task_id=f"research_{query[:20]}",
            target=query,
            parameters={
                "query": query,
                "depth": depth,
                "max_results": max_results
            }
        )
        
        return {
            "success": result.get("success", False),
            "query": query,
            "findings": result.get("result", {}).get("findings", []),
            "sources": result.get("result", {}).get("sources", []),
            "analysis": result.get("result", {}).get("analysis", ""),
            "confidence": result.get("result", {}).get("confidence", 0.7),
            "method": "ai_fallback"
        }

