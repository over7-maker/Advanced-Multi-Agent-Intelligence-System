"""
FOFA Integration for Cyberspace Mapping (AMAS v3.0)
Asset discovery and cyberspace reconnaissance
"""

import base64
import logging
from typing import Any, Dict, List, Optional

import aiohttp

logger = logging.getLogger(__name__)


class FOFAClient:
    """
    FOFA API Client for cyberspace asset discovery
    
    Features:
    - Asset discovery queries
    - Certificate-based search
    - Port scanning
    - Framework detection
    """
    
    def __init__(self, email: str, api_key: str):
        """
        Initialize FOFA client
        
        Args:
            email: FOFA account email
            api_key: FOFA API key
        """
        self.email = email
        self.api_key = api_key
        self.base_url = "https://fofa.info/api/v1"
        self.timeout = 30
    
    async def search_assets(
        self,
        query: str,
        size: int = 100,
        page: int = 1,
        fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Search for assets using FOFA query syntax
        
        Args:
            query: FOFA query (e.g., 'domain="example.com"')
            size: Number of results (max 10000)
            page: Page number
            fields: Fields to return (default: host,ip,port,protocol,domain)
            
        Returns:
            Search results with assets
        """
        try:
            # Encode query to base64
            query_bytes = base64.b64encode(query.encode()).decode()
            
            # Default fields
            if fields is None:
                fields = ["host", "ip", "port", "protocol", "domain"]
            
            params = {
                "qbase64": query_bytes,
                "email": self.email,
                "key": self.api_key,
                "size": min(size, 10000),  # FOFA max is 10000
                "page": page,
                "fields": ",".join(fields)
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/search/all",
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get("error"):
                            raise Exception(f"FOFA API error: {data.get('errmsg', 'Unknown error')}")
                        
                        return {
                            "success": True,
                            "query": query,
                            "size": data.get("size", 0),
                            "page": page,
                            "results": data.get("results", []),
                            "total": len(data.get("results", []))
                        }
                    else:
                        error_text = await response.text()
                        raise Exception(f"FOFA API returned status {response.status}: {error_text}")
        
        except Exception as e:
            logger.error(f"FOFA search failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "results": []
            }
    
    async def get_user_info(self) -> Dict[str, Any]:
        """Get FOFA user information and quota"""
        try:
            params = {
                "email": self.email,
                "key": self.api_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/info/my",
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "email": data.get("email", ""),
                            "username": data.get("username", ""),
                            "fcoin": data.get("fcoin", 0),
                            "vip_level": data.get("vip_level", 0),
                            "is_vip": data.get("is_vip", False)
                        }
                    else:
                        error_text = await response.text()
                        raise Exception(f"FOFA API returned status {response.status}: {error_text}")
        
        except Exception as e:
            logger.error(f"Failed to get FOFA user info: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def search_by_domain(self, domain: str, size: int = 100) -> Dict[str, Any]:
        """Search for all assets under a domain"""
        query = f'domain="{domain}"'
        return await self.search_assets(query, size=size)
    
    async def search_by_port(self, port: int, country: Optional[str] = None) -> Dict[str, Any]:
        """Search for assets with specific port"""
        query = f'port="{port}"'
        if country:
            query += f' && country="{country}"'
        return await self.search_assets(query)
    
    async def search_by_certificate(
        self,
        issuer: Optional[str] = None,
        is_valid: bool = True
    ) -> Dict[str, Any]:
        """Search by SSL certificate"""
        query = "cert.is_valid=true" if is_valid else "cert.is_valid=false"
        if issuer:
            query = f'cert.issuer="{issuer}" && {query}'
        return await self.search_assets(query)
    
    async def search_by_framework(self, framework: str) -> Dict[str, Any]:
        """Search for specific framework"""
        # Common framework queries
        framework_queries = {
            "wordpress": 'body="wp-content"',
            "joomla": 'body="joomla"',
            "drupal": 'body="drupal"',
            "laravel": 'header="X-Powered-By: Laravel"',
            "django": 'header="X-Powered-By: Django"',
            "rails": 'header="X-Powered-By: Phusion Passenger"',
            "spring": 'body="spring" && header="X-Application-Context"'
        }
        
        query = framework_queries.get(framework.lower(), f'body="{framework}"')
        return await self.search_assets(query)


def get_fofa_client() -> Optional[FOFAClient]:
    """Get FOFA client instance from environment variables"""
    import os
    
    email = os.getenv("FOFA_EMAIL")
    api_key = os.getenv("FOFA_API_KEY")
    
    if email and api_key:
        return FOFAClient(email, api_key)
    
    logger.warning("FOFA credentials not found in environment variables")
    return None

