"""
Security API Tools
Integrations with security APIs: VirusTotal, Shodan, Censys, HaveIBeenPwned, AbuseIPDB
"""

import logging
import os
from typing import Any, Dict

import aiohttp

from . import AgentTool

logger = logging.getLogger(__name__)


class VirusTotalTool(AgentTool):
    """Tool for VirusTotal API integration"""
    
    def __init__(self):
        super().__init__(
            name="virustotal",
            description="Check URLs, domains, IPs, and files with VirusTotal"
        )
        self.category = "security_api"
        self.api_key = os.getenv("VIRUSTOTAL_API_KEY")
        self.base_url = "https://www.virustotal.com/vtapi/v2"
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "resource": {
                    "type": "string",
                    "description": "URL, domain, IP, or file hash to check"
                },
                "resource_type": {
                    "type": "string",
                    "enum": ["url", "domain", "ip", "hash"],
                    "description": "Type of resource",
                    "default": "url"
                }
            },
            "required": ["resource"]
        }
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute VirusTotal check"""
        if not self.api_key:
            return {
                "success": False,
                "error": "VIRUSTOTAL_API_KEY not configured"
            }
        
        resource = params.get("resource")
        resource_type = params.get("resource_type", "url")
        
        try:
            if resource_type == "url":
                endpoint = f"{self.base_url}/url/report"
                payload = {"apikey": self.api_key, "resource": resource}
            elif resource_type == "domain":
                endpoint = f"{self.base_url}/domain/report"
                payload = {"apikey": self.api_key, "domain": resource}
            elif resource_type == "ip":
                endpoint = f"{self.base_url}/ip-address/report"
                payload = {"apikey": self.api_key, "ip": resource}
            else:  # hash
                endpoint = f"{self.base_url}/file/report"
                payload = {"apikey": self.api_key, "resource": resource}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(endpoint, data=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "result": data,
                            "metadata": {"resource": resource, "resource_type": resource_type}
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"VirusTotal API returned status {response.status}",
                            "result": await response.text()
                        }
        
        except Exception as e:
            logger.error(f"VirusTotal API error: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"VirusTotal API error: {str(e)}"
            }


class ShodanTool(AgentTool):
    """Tool for Shodan API integration"""
    
    def __init__(self):
        super().__init__(
            name="shodan",
            description="Search Shodan for internet-connected devices and services"
        )
        self.category = "security_api"
        self.api_key = os.getenv("SHODAN_API_KEY")
        self.base_url = "https://api.shodan.io"
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Shodan search query or IP address"
                },
                "query_type": {
                    "type": "string",
                    "enum": ["search", "host", "info"],
                    "description": "Type of query",
                    "default": "search"
                }
            },
            "required": ["query"]
        }
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Shodan query"""
        if not self.api_key:
            return {
                "success": False,
                "error": "SHODAN_API_KEY not configured"
            }
        
        query = params.get("query")
        query_type = params.get("query_type", "search")
        
        try:
            if query_type == "host":
                endpoint = f"{self.base_url}/shodan/host/{query}"
                params_dict = {"key": self.api_key}
            elif query_type == "info":
                endpoint = f"{self.base_url}/api-info"
                params_dict = {"key": self.api_key}
            else:  # search
                endpoint = f"{self.base_url}/shodan/host/search"
                params_dict = {"key": self.api_key, "query": query}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint, params=params_dict) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "result": data,
                            "metadata": {"query": query, "query_type": query_type}
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"Shodan API returned status {response.status}",
                            "result": await response.text()
                        }
        
        except Exception as e:
            logger.error(f"Shodan API error: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Shodan API error: {str(e)}"
            }


class HaveIBeenPwnedTool(AgentTool):
    """Tool for HaveIBeenPwned API integration"""
    
    def __init__(self):
        super().__init__(
            name="haveibeenpwned",
            description="Check if email addresses or passwords have been breached"
        )
        self.category = "security_api"
        self.base_url = "https://haveibeenpwned.com/api/v3"
        self.api_key = os.getenv("HIBP_API_KEY")  # Optional, for authenticated requests
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "email": {
                    "type": "string",
                    "description": "Email address to check"
                },
                "password": {
                    "type": "string",
                    "description": "Password to check (will be hashed)"
                },
                "check_type": {
                    "type": "string",
                    "enum": ["email", "password"],
                    "description": "Type of check",
                    "default": "email"
                }
            },
            "required": []
        }
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute HaveIBeenPwned check"""
        check_type = params.get("check_type", "email")
        email = params.get("email")
        password = params.get("password")
        
        try:
            if check_type == "email" and email:
                endpoint = f"{self.base_url}/breachedaccount/{email}"
                headers = {}
                if self.api_key:
                    headers["hibp-api-key"] = self.api_key
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(endpoint, headers=headers) as response:
                        if response.status == 200:
                            data = await response.json()
                            return {
                                "success": True,
                                "result": {
                                    "breached": True,
                                    "breaches": data
                                },
                                "metadata": {"email": email}
                            }
                        elif response.status == 404:
                            return {
                                "success": True,
                                "result": {
                                    "breached": False,
                                    "breaches": []
                                },
                                "metadata": {"email": email}
                            }
                        else:
                            return {
                                "success": False,
                                "error": f"HIBP API returned status {response.status}"
                            }
            
            elif check_type == "password" and password:
                # Password check uses k-anonymity (first 5 chars of SHA-1 hash)
                import hashlib
                password_hash = hashlib.sha1(password.encode()).hexdigest().upper()
                prefix = password_hash[:5]
                suffix = password_hash[5:]
                
                endpoint = f"https://api.pwnedpasswords.com/range/{prefix}"
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(endpoint) as response:
                        if response.status == 200:
                            data = await response.text()
                            # Check if suffix is in results
                            breached = suffix in data
                            return {
                                "success": True,
                                "result": {
                                    "breached": breached,
                                    "count": data.count(suffix) if breached else 0
                                },
                                "metadata": {"password_checked": True}
                            }
                        else:
                            return {
                                "success": False,
                                "error": f"Password API returned status {response.status}"
                            }
            
            else:
                return {
                    "success": False,
                    "error": "Email or password required"
                }
        
        except Exception as e:
            logger.error(f"HaveIBeenPwned API error: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"HIBP API error: {str(e)}"
            }


class AbuseIPDBTool(AgentTool):
    """Tool for AbuseIPDB API integration"""
    
    def __init__(self):
        super().__init__(
            name="abuseipdb",
            description="Check IP reputation with AbuseIPDB"
        )
        self.category = "security_api"
        self.api_key = os.getenv("ABUSEIPDB_API_KEY")
        self.base_url = "https://api.abuseipdb.com/api/v2"
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "ip": {
                    "type": "string",
                    "description": "IP address to check"
                },
                "max_age_in_days": {
                    "type": "integer",
                    "description": "Maximum age of reports in days",
                    "default": 90
                }
            },
            "required": ["ip"]
        }
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute AbuseIPDB check"""
        if not self.api_key:
            return {
                "success": False,
                "error": "ABUSEIPDB_API_KEY not configured"
            }
        
        ip = params.get("ip")
        max_age = params.get("max_age_in_days", 90)
        
        try:
            endpoint = f"{self.base_url}/check"
            headers = {
                "Key": self.api_key,
                "Accept": "application/json"
            }
            query_params = {
                "ipAddress": ip,
                "maxAgeInDays": max_age,
                "verbose": ""
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint, headers=headers, params=query_params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "result": data,
                            "metadata": {"ip": ip}
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"AbuseIPDB API returned status {response.status}",
                            "result": await response.text()
                        }
        
        except Exception as e:
            logger.error(f"AbuseIPDB API error: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"AbuseIPDB API error: {str(e)}"
            }


# Note: Censys API requires more complex authentication, implementing basic version
class CensysTool(AgentTool):
    """Tool for Censys API integration"""
    
    def __init__(self):
        super().__init__(
            name="censys",
            description="Search Censys for internet-wide scanning data"
        )
        self.category = "security_api"
        self.api_id = os.getenv("CENSYS_API_ID")
        self.api_secret = os.getenv("CENSYS_API_SECRET")
        self.base_url = "https://search.censys.io/api/v1"
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Censys search query"
                },
                "index": {
                    "type": "string",
                    "enum": ["ipv4", "websites", "certificates"],
                    "description": "Index to search",
                    "default": "ipv4"
                }
            },
            "required": ["query"]
        }
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Censys search"""
        if not self.api_id or not self.api_secret:
            return {
                "success": False,
                "error": "CENSYS_API_ID and CENSYS_API_SECRET not configured"
            }
        
        query = params.get("query")
        index = params.get("index", "ipv4")
        
        try:
            import base64
            auth_string = f"{self.api_id}:{self.api_secret}"
            auth_bytes = base64.b64encode(auth_string.encode()).decode()
            
            endpoint = f"{self.base_url}/view/{index}/{query}"
            headers = {
                "Authorization": f"Basic {auth_bytes}",
                "Accept": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "result": data,
                            "metadata": {"query": query, "index": index}
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"Censys API returned status {response.status}",
                            "result": await response.text()
                        }
        
        except Exception as e:
            logger.error(f"Censys API error: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Censys API error: {str(e)}"
            }

