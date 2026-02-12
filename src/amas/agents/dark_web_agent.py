"""
Dark Web OSINT Agent with Robin Integration (AMAS v3.0)
AI-powered dark web research and threat intelligence
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

import aiohttp

from src.amas.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class DarkWebAgent(BaseAgent):
    """
    Dark Web OSINT Agent with Robin integration
    
    Features:
    - AI-powered Tor crawler
    - Dark web investigation
    - Threat intelligence
    - Continuous monitoring
    """
    
    def __init__(self):
        super().__init__(
            agent_id="dark_web",
            name="Dark Web OSINT Agent",
            agent_type="dark_web",
            system_prompt="""You are a dark web intelligence specialist. Your role is to:
1. Conduct dark web investigations using Tor network
2. Analyze threat intelligence from dark web sources
3. Monitor for data breaches and leaks
4. Track ransomware and malware activities
5. Provide comprehensive threat reports

You use Robin for AI-powered dark web crawling and Tor network access.
IMPORTANT: All activities must comply with local laws and regulations.""",
            model_preference=None,  # Use local models for privacy
            strategy="quality_first"
        )
        
        # Robin configuration
        self.robin_url = "http://localhost:8002"  # Default Robin URL
        self.tor_socks = "127.0.0.1:9050"  # Tor SOCKS proxy
        self.tor_control = "127.0.0.1:9051"  # Tor control port
        self.ollama_url = "http://localhost:11434"  # Ollama for local AI
        
        # Check if Robin is available
        self.robin_available = False
        asyncio.create_task(self._check_robin_availability())
    
    async def _check_robin_availability(self):
        """Check if Robin service is available"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.robin_url}/health",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        self.robin_available = True
                        logger.info("Robin service is available")
                    else:
                        logger.warning(f"Robin health check returned {response.status}")
        except Exception as e:
            logger.warning(f"Robin not available: {e}")
            self.robin_available = False
    
    async def _prepare_prompt(
        self,
        target: str,
        parameters: Dict[str, Any]
    ) -> str:
        """Prepare dark web investigation prompt"""
        query = parameters.get("query", target)
        search_types = parameters.get("search_types", ["breach", "ransomware", "malware"])
        
        prompt = f"""Conduct dark web investigation for: {query}

Investigation Requirements:
- Search types: {', '.join(search_types)}
- Target: {query}
- Focus areas: {parameters.get('focus_areas', 'threat intelligence')}
- Language: {parameters.get('language', 'English')}

Please provide:
1. Threat level assessment
2. Findings and evidence
3. Sources and references
4. Risk factors
5. Recommendations

Query: {query}
Search Types: {', '.join(search_types)}"""
        
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
                    "threat_level": parsed.get("threat_level", "low"),
                    "findings": parsed.get("findings", []),
                    "sources": parsed.get("sources", []),
                    "risk_factors": parsed.get("risk_factors", []),
                    "recommendations": parsed.get("recommendations", []),
                    "confidence": parsed.get("confidence", 0.7),
                    "quality_score": parsed.get("quality_score", 0.8)
                }
            
            # Fallback: parse as text
            return {
                "success": True,
                "threat_level": "medium",
                "findings": [],
                "sources": [],
                "risk_factors": [],
                "recommendations": [],
                "confidence": 0.6,
                "quality_score": 0.7
            }
        except Exception as e:
            logger.error(f"Failed to parse response: {e}")
            return {
                "success": False,
                "error": str(e),
                "threat_level": "unknown",
                "quality_score": 0.5
            }
    
    async def investigate_target(
        self,
        target: str,
        search_types: List[str] = None
    ) -> Dict[str, Any]:
        """
        Investigate target on dark web
        
        Args:
            target: Target to investigate (company name, domain, etc.)
            search_types: Types of searches (breach, ransomware, malware, etc.)
            
        Returns:
            Investigation results with threat assessment
        """
        if search_types is None:
            search_types = ["breach", "ransomware", "malware"]
        
        try:
            # If Robin is available, use it
            if self.robin_available:
                return await self._investigate_with_robin(target, search_types)
            
            # Fallback to AI-powered investigation
            return await self._investigate_with_ai(target, search_types)
        
        except Exception as e:
            logger.error(f"Dark web investigation failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "target": target,
                "threat_level": "unknown",
                "findings": []
            }
    
    async def _investigate_with_robin(
        self,
        target: str,
        search_types: List[str]
    ) -> Dict[str, Any]:
        """Investigate using Robin dark web crawler"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.robin_url}/investigate",
                    json={
                        "target": target,
                        "search_types": search_types
                    },
                    timeout=aiohttp.ClientTimeout(total=60)  # Longer timeout for dark web
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "target": target,
                            "threat_level": data.get("threat_level", "low"),
                            "findings": data.get("findings", []),
                            "sources": data.get("sources", []),
                            "risk_factors": data.get("risk_factors", []),
                            "recommendations": data.get("recommendations", []),
                            "method": "robin"
                        }
                    else:
                        raise Exception(f"Robin returned status {response.status}")
        except Exception as e:
            logger.warning(f"Robin investigation failed: {e}, falling back to AI")
            return await self._investigate_with_ai(target, search_types)
    
    async def _investigate_with_ai(
        self,
        target: str,
        search_types: List[str]
    ) -> Dict[str, Any]:
        """Investigate using AI (fallback when Robin unavailable)"""
        # Use base agent execute method
        result = await self.execute(
            task_id=f"darkweb_{target[:20]}",
            target=target,
            parameters={
                "query": target,
                "search_types": search_types
            }
        )
        
        return {
            "success": result.get("success", False),
            "target": target,
            "threat_level": result.get("result", {}).get("threat_level", "medium"),
            "findings": result.get("result", {}).get("findings", []),
            "sources": result.get("result", {}).get("sources", []),
            "risk_factors": result.get("result", {}).get("risk_factors", []),
            "recommendations": result.get("result", {}).get("recommendations", []),
            "method": "ai_fallback"
        }
    
    async def monitor_target(
        self,
        target: str,
        interval_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Set up continuous monitoring for target
        
        Args:
            target: Target to monitor
            interval_hours: Monitoring interval in hours
            
        Returns:
            Monitoring setup confirmation
        """
        try:
            if self.robin_available:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.robin_url}/monitor",
                        json={
                            "target": target,
                            "interval_hours": interval_hours
                        },
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            return {
                                "success": True,
                                "target": target,
                                "monitoring_id": data.get("monitoring_id"),
                                "interval_hours": interval_hours,
                                "status": "active"
                            }
            
            return {
                "success": False,
                "error": "Robin service not available",
                "target": target
            }
        except Exception as e:
            logger.error(f"Failed to setup monitoring: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "target": target
            }

