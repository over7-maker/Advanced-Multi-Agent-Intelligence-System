"""
Dark Web Pipeline (AMAS v3.0)
Complete dark web research stack with TorBot, OnionScan, and VigilantOnion
"""

import asyncio
import logging
import subprocess
from typing import Any, Dict, List, Optional

import aiohttp

logger = logging.getLogger(__name__)


class TorBotClient:
    """TorBot client for .onion crawling"""
    
    def __init__(self):
        self.torbot_path = "torbot"  # Assume TorBot is in PATH
        self.available = False
        asyncio.create_task(self._check_availability())
    
    async def _check_availability(self):
        """Check if TorBot is available"""
        try:
            result = subprocess.run(
                ["which", "torbot"],
                capture_output=True,
                timeout=5
            )
            self.available = result.returncode == 0
            if self.available:
                logger.info("TorBot is available")
        except Exception as e:
            logger.warning(f"TorBot not available: {e}")
            self.available = False
    
    async def search_mirrors(self, domain: str) -> List[str]:
        """Search for .onion mirrors of a domain"""
        if not self.available:
            return []
        
        try:
            # Run TorBot to find mirrors
            process = await asyncio.create_subprocess_exec(
                self.torbot_path,
                "--domain", domain,
                "--output", "json",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                import json
                data = json.loads(stdout.decode())
                return data.get("mirrors", [])
            
            return []
        except Exception as e:
            logger.error(f"TorBot search failed: {e}")
            return []


class OnionScanClient:
    """OnionScan client for vulnerability scanning"""
    
    def __init__(self):
        self.onionscan_path = "onionscan"  # Assume OnionScan is in PATH
        self.available = False
        asyncio.create_task(self._check_availability())
    
    async def _check_availability(self):
        """Check if OnionScan is available"""
        try:
            result = subprocess.run(
                ["which", "onionscan"],
                capture_output=True,
                timeout=5
            )
            self.available = result.returncode == 0
            if self.available:
                logger.info("OnionScan is available")
        except Exception as e:
            logger.warning(f"OnionScan not available: {e}")
            self.available = False
    
    async def scan(self, onion_url: str) -> Dict[str, Any]:
        """Scan .onion site for vulnerabilities"""
        if not self.available:
            return {
                "success": False,
                "error": "OnionScan not available",
                "onion_url": onion_url
            }
        
        try:
            # Run OnionScan
            process = await asyncio.create_subprocess_exec(
                self.onionscan_path,
                "-json",
                onion_url,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                import json
                data = json.loads(stdout.decode())
                return {
                    "success": True,
                    "onion_url": onion_url,
                    "vulnerabilities": data.get("vulnerabilities", []),
                    "services": data.get("services", []),
                    "metadata": data.get("metadata", {})
                }
            
            return {
                "success": False,
                "error": stderr.decode(),
                "onion_url": onion_url
            }
        except Exception as e:
            logger.error(f"OnionScan failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "onion_url": onion_url
            }


class VigilantOnionClient:
    """VigilantOnion client for continuous monitoring"""
    
    def __init__(self):
        self.vigilant_url = "http://localhost:8080"  # Default VigilantOnion URL
        self.available = False
        asyncio.create_task(self._check_availability())
    
    async def _check_availability(self):
        """Check if VigilantOnion is available"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.vigilant_url}/health",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        self.available = True
                        logger.info("VigilantOnion is available")
        except Exception as e:
            logger.warning(f"VigilantOnion not available: {e}")
            self.available = False
    
    async def analyze(self, onion_url: str) -> Dict[str, Any]:
        """Analyze .onion site using VigilantOnion"""
        if not self.available:
            return {
                "success": False,
                "error": "VigilantOnion not available",
                "onion_url": onion_url
            }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.vigilant_url}/analyze",
                    json={"onion_url": onion_url},
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "onion_url": onion_url,
                            "analysis": data.get("analysis", {}),
                            "metadata": data.get("metadata", {})
                        }
                    else:
                        raise Exception(f"VigilantOnion returned status {response.status}")
        except Exception as e:
            logger.error(f"VigilantOnion analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "onion_url": onion_url
            }
    
    async def setup_monitoring(self, onion_urls: List[str]) -> Dict[str, Any]:
        """Setup continuous monitoring for .onion sites"""
        if not self.available:
            return {
                "success": False,
                "error": "VigilantOnion not available",
                "monitors": []
            }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.vigilant_url}/monitor",
                    json={"onion_urls": onion_urls},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "monitors": data.get("monitors", []),
                            "count": len(data.get("monitors", []))
                        }
                    else:
                        raise Exception(f"VigilantOnion returned status {response.status}")
        except Exception as e:
            logger.error(f"Failed to setup monitoring: {e}")
            return {
                "success": False,
                "error": str(e),
                "monitors": []
            }


class DarkWebPipeline:
    """
    Complete dark web research pipeline
    
    Integrates:
    - TorBot: .onion crawler
    - OnionScan: Vulnerability scanner
    - VigilantOnion: Continuous monitoring
    """
    
    def __init__(self):
        self.torbot = TorBotClient()
        self.onionscan = OnionScanClient()
        self.vigilant = VigilantOnionClient()
    
    async def full_investigation(
        self,
        target_domain: str
    ) -> Dict[str, Any]:
        """
        Conduct full dark web investigation
        
        Args:
            target_domain: Target domain to investigate
            
        Returns:
            Complete investigation results
        """
        results = {
            "target": target_domain,
            "success": False,
            "mirrors": [],
            "vulnerabilities": {},
            "monitoring_active": 0
        }
        
        try:
            # Stage 1: Find .onion mirrors
            logger.info(f"Stage 1: Finding .onion mirrors for {target_domain}")
            onion_mirrors = await self.torbot.search_mirrors(target_domain)
            results["mirrors"] = onion_mirrors
            logger.info(f"Found {len(onion_mirrors)} .onion mirrors")
            
            # Stage 2: Scan each mirror
            logger.info(f"Stage 2: Scanning {len(onion_mirrors)} mirrors")
            vulnerabilities = {}
            for mirror in onion_mirrors:
                try:
                    # Try OnionScan first
                    if self.onionscan.available:
                        vuln_result = await self.onionscan.scan(mirror)
                        if vuln_result.get("success"):
                            vulnerabilities[mirror] = vuln_result
                        else:
                            # Fallback to VigilantOnion
                            if self.vigilant.available:
                                vuln_result = await self.vigilant.analyze(mirror)
                                vulnerabilities[mirror] = vuln_result
                    else:
                        # Use VigilantOnion if OnionScan not available
                        if self.vigilant.available:
                            vuln_result = await self.vigilant.analyze(mirror)
                            vulnerabilities[mirror] = vuln_result
                except Exception as e:
                    logger.error(f"Failed to scan mirror {mirror}: {e}")
                    vulnerabilities[mirror] = {
                        "success": False,
                        "error": str(e)
                    }
            
            results["vulnerabilities"] = vulnerabilities
            
            # Stage 3: Setup monitoring
            if self.vigilant.available and onion_mirrors:
                logger.info(f"Stage 3: Setting up monitoring for {len(onion_mirrors)} mirrors")
                monitoring_result = await self.vigilant.setup_monitoring(onion_mirrors)
                if monitoring_result.get("success"):
                    results["monitoring_active"] = monitoring_result.get("count", 0)
            
            results["success"] = True
            return results
        
        except Exception as e:
            logger.error(f"Full investigation failed: {e}", exc_info=True)
            results["error"] = str(e)
            return results

