"""
Connection Pooling Service for AMAS

Optimizes HTTP client configurations with connection pooling,
timeout management, and retry strategies.
"""

import asyncio
import logging
from typing import Dict, Optional

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    httpx = None

logger = logging.getLogger(__name__)


class ConnectionPoolService:
    """
    Service for managing optimized HTTP client connection pools.
    
    Features:
    - Connection pooling with configurable limits
    - Timeout management
    - Retry strategies
    - Keep-alive connections
    - Per-domain connection limits
    """
    
    def __init__(
        self,
        max_connections: int = 100,
        max_keepalive_connections: int = 20,
        keepalive_expiry: float = 5.0,
        timeout: float = 30.0,
        connect_timeout: float = 10.0,
        read_timeout: float = 30.0,
        write_timeout: float = 30.0,
        pool_timeout: float = 5.0
    ):
        """
        Initialize connection pool service.
        
        Args:
            max_connections: Maximum number of connections
            max_keepalive_connections: Maximum keepalive connections
            keepalive_expiry: Keepalive expiry in seconds
            timeout: Default timeout in seconds
            connect_timeout: Connection timeout in seconds
            read_timeout: Read timeout in seconds
            write_timeout: Write timeout in seconds
            pool_timeout: Pool timeout in seconds
        """
        if not HTTPX_AVAILABLE:
            logger.warning("httpx not available. Connection pooling disabled.")
            self._clients: Dict[str, httpx.AsyncClient] = {}
            return
        
        self.config = {
            "max_connections": max_connections,
            "max_keepalive_connections": max_keepalive_connections,
            "keepalive_expiry": keepalive_expiry,
            "timeout": timeout,
            "connect_timeout": connect_timeout,
            "read_timeout": read_timeout,
            "write_timeout": write_timeout,
            "pool_timeout": pool_timeout
        }
        
        # Per-domain clients for connection reuse
        self._clients: Dict[str, httpx.AsyncClient] = {}
        self._default_client: Optional[httpx.AsyncClient] = None
    
    def get_client(
        self,
        base_url: Optional[str] = None,
        **overrides
    ) -> Optional[httpx.AsyncClient]:
        """
        Get optimized HTTP client for a base URL.
        
        Args:
            base_url: Base URL for the client (creates domain-specific client)
            **overrides: Override default configuration
            
        Returns:
            httpx.AsyncClient instance
        """
        if not HTTPX_AVAILABLE:
            return None
        
        # Use default client if no base_url
        if not base_url:
            if not self._default_client:
                self._default_client = self._create_client(**overrides)
            return self._default_client
        
        # Create domain-specific client
        domain = self._extract_domain(base_url)
        if domain not in self._clients:
            self._clients[domain] = self._create_client(base_url=base_url, **overrides)
        
        return self._clients[domain]
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc or parsed.path
        except Exception:
            return url
    
    def _create_client(self, base_url: Optional[str] = None, **overrides) -> httpx.AsyncClient:
        """Create optimized HTTP client"""
        config = {**self.config, **overrides}
        
        limits = httpx.Limits(
            max_connections=config["max_connections"],
            max_keepalive_connections=config["max_keepalive_connections"],
            keepalive_expiry=config["keepalive_expiry"]
        )
        
        timeout = httpx.Timeout(
            connect=config["connect_timeout"],
            read=config["read_timeout"],
            write=config["write_timeout"],
            pool=config["pool_timeout"]
        )
        
        return httpx.AsyncClient(
            base_url=base_url,
            limits=limits,
            timeout=timeout,
            http2=True,  # Enable HTTP/2 for better performance
            follow_redirects=True
        )
    
    async def close_all(self):
        """Close all HTTP clients"""
        for client in self._clients.values():
            await client.aclose()
        self._clients.clear()
        
        if self._default_client:
            await self._default_client.aclose()
            self._default_client = None
    
    def get_stats(self) -> Dict[str, any]:
        """Get connection pool statistics"""
        return {
            "active_clients": len(self._clients) + (1 if self._default_client else 0),
            "config": self.config,
            "httpx_available": HTTPX_AVAILABLE
        }


# Global instance
_connection_pool_service: Optional[ConnectionPoolService] = None


def get_connection_pool_service(**kwargs) -> ConnectionPoolService:
    """Get or create global connection pool service instance"""
    global _connection_pool_service
    
    if _connection_pool_service is None:
        _connection_pool_service = ConnectionPoolService(**kwargs)
    
    return _connection_pool_service
