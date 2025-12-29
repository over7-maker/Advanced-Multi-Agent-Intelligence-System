"""
Shared Context for Agent Communication
Provides Redis-backed shared context for agents to share data
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set

logger = logging.getLogger(__name__)

# Global shared context instances
_shared_contexts: Dict[str, "SharedContext"] = {}


class ContextVersion:
    """Version information for context value"""
    
    def __init__(self, value: Any, version: int, timestamp: datetime, updated_by: str):
        self.value = value
        self.version = version
        self.timestamp = timestamp
        self.updated_by = updated_by
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "value": self.value,
            "version": self.version,
            "timestamp": self.timestamp.isoformat(),
            "updated_by": self.updated_by,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ContextVersion":
        """Create from dictionary"""
        return cls(
            value=data["value"],
            version=data["version"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            updated_by=data["updated_by"],
        )


class SharedContext:
    """
    Shared context for agents with Redis persistence
    
    Features:
    - Redis-backed storage
    - Context versioning
    - TTL support
    - Watch/notify on changes
    - Namespace isolation
    - Conflict resolution (last-write-wins)
    """
    
    def __init__(self, namespace: str = "default"):
        """
        Initialize shared context
        
        Args:
            namespace: Namespace for context isolation (e.g., task_id, agent_id)
        """
        self.namespace = namespace
        self._redis_client = None
        self._local_cache: Dict[str, Any] = {}
        self._versions: Dict[str, int] = {}
        self._watchers: Dict[str, Set[Callable]] = {}
        self._initialized = False
        
        logger.debug(f"SharedContext created for namespace: {namespace}")
    
    async def initialize(self):
        """Initialize Redis connection"""
        if self._initialized:
            return
        
        try:
            from src.cache.redis import get_redis_client
            self._redis_client = get_redis_client()
            self._initialized = True
            logger.info(f"SharedContext initialized for namespace: {self.namespace}")
        except Exception as e:
            logger.warning(f"SharedContext could not connect to Redis: {e}")
    
    def _get_key(self, key: str) -> str:
        """Get Redis key with namespace"""
        return f"shared_context:{self.namespace}:{key}"
    
    def _get_version_key(self, key: str) -> str:
        """Get Redis key for version tracking"""
        return f"shared_context:{self.namespace}:{key}:version"
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        updated_by: Optional[str] = None,
    ) -> bool:
        """
        Set a value in shared context
        
        Args:
            key: Context key
            value: Value to store
            ttl: Time-to-live in seconds (None for no expiration)
            updated_by: ID of agent updating the value
            
        Returns:
            True if successful
        """
        try:
            # Update local cache
            self._local_cache[key] = value
            
            # Increment version
            current_version = self._versions.get(key, 0)
            new_version = current_version + 1
            self._versions[key] = new_version
            
            # Store in Redis if available
            if self._redis_client:
                redis_key = self._get_key(key)
                version_key = self._get_version_key(key)
                
                # Create versioned value
                versioned_value = ContextVersion(
                    value=value,
                    version=new_version,
                    timestamp=datetime.utcnow(),
                    updated_by=updated_by or "unknown",
                )
                
                # Store value and version
                value_json = json.dumps(versioned_value.to_dict())
                await self._redis_client.set(redis_key, value_json)
                
                # Set TTL if specified
                if ttl:
                    await self._redis_client.expire(redis_key, ttl)
                
                logger.debug(f"Set {key}={value} in namespace {self.namespace} (v{new_version})")
            
            # Notify watchers
            await self._notify_watchers(key, value, new_version)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to set context value {key}: {e}", exc_info=True)
            return False
    
    async def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from shared context
        
        Args:
            key: Context key
            default: Default value if key not found
            
        Returns:
            Value or default
        """
        try:
            # Try local cache first
            if key in self._local_cache:
                return self._local_cache[key]
            
            # Try Redis if available
            if self._redis_client:
                redis_key = self._get_key(key)
                value_json = await self._redis_client.get(redis_key)
                
                if value_json:
                    versioned_value = ContextVersion.from_dict(json.loads(value_json))
                    
                    # Update local cache and version
                    self._local_cache[key] = versioned_value.value
                    self._versions[key] = versioned_value.version
                    
                    return versioned_value.value
            
            return default
            
        except Exception as e:
            logger.error(f"Failed to get context value {key}: {e}", exc_info=True)
            return default
    
    async def update(
        self,
        key: str,
        value: Any,
        updated_by: Optional[str] = None,
    ) -> bool:
        """
        Update a value (alias for set without TTL)
        
        Args:
            key: Context key
            value: New value
            updated_by: ID of agent updating
            
        Returns:
            True if successful
        """
        return await self.set(key, value, ttl=None, updated_by=updated_by)
    
    async def delete(self, key: str) -> bool:
        """
        Delete a value from shared context
        
        Args:
            key: Context key to delete
            
        Returns:
            True if successful
        """
        try:
            # Remove from local cache
            self._local_cache.pop(key, None)
            self._versions.pop(key, None)
            
            # Remove from Redis
            if self._redis_client:
                redis_key = self._get_key(key)
                version_key = self._get_version_key(key)
                
                await self._redis_client.delete(redis_key)
                await self._redis_client.delete(version_key)
            
            # Notify watchers
            await self._notify_watchers(key, None, 0)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete context value {key}: {e}", exc_info=True)
            return False
    
    async def exists(self, key: str) -> bool:
        """
        Check if key exists in context
        
        Args:
            key: Context key
            
        Returns:
            True if key exists
        """
        # Check local cache
        if key in self._local_cache:
            return True
        
        # Check Redis
        if self._redis_client:
            redis_key = self._get_key(key)
            return bool(await self._redis_client.exists(redis_key))
        
        return False
    
    async def get_version(self, key: str) -> int:
        """
        Get version number for a key
        
        Args:
            key: Context key
            
        Returns:
            Version number (0 if not found)
        """
        return self._versions.get(key, 0)
    
    async def get_all(self) -> Dict[str, Any]:
        """
        Get all values in this namespace
        
        Returns:
            Dictionary of all key-value pairs
        """
        all_values = {}
        
        # Get from Redis if available
        if self._redis_client:
            try:
                pattern = f"shared_context:{self.namespace}:*"
                keys = []
                
                # Scan for keys (async iteration)
                async for key in self._redis_client.scan_iter(match=pattern):
                    if b":version" not in key:  # Skip version keys
                        keys.append(key)
                
                # Get all values
                for redis_key in keys:
                    value_json = await self._redis_client.get(redis_key)
                    if value_json:
                        versioned_value = ContextVersion.from_dict(json.loads(value_json))
                        # Extract original key (remove namespace prefix)
                        original_key = redis_key.decode().split(":", 2)[2]
                        all_values[original_key] = versioned_value.value
                
            except Exception as e:
                logger.error(f"Failed to get all context values: {e}", exc_info=True)
        
        # Merge with local cache
        all_values.update(self._local_cache)
        
        return all_values
    
    def watch(self, key: str, callback: Callable) -> None:
        """
        Watch a key for changes
        
        Args:
            key: Context key to watch
            callback: Async function to call on change
        """
        if key not in self._watchers:
            self._watchers[key] = set()
        
        self._watchers[key].add(callback)
        logger.debug(f"Watcher added for key: {key}")
    
    def unwatch(self, key: str, callback: Callable) -> None:
        """
        Stop watching a key
        
        Args:
            key: Context key
            callback: Callback to remove
        """
        if key in self._watchers:
            self._watchers[key].discard(callback)
            logger.debug(f"Watcher removed for key: {key}")
    
    async def _notify_watchers(self, key: str, value: Any, version: int) -> None:
        """
        Notify watchers of a change
        
        Args:
            key: Changed key
            value: New value
            version: New version
        """
        watchers = self._watchers.get(key, set()).copy()
        
        if not watchers:
            return
        
        # Call all watchers
        tasks = []
        for watcher in watchers:
            try:
                if asyncio.iscoroutinefunction(watcher):
                    tasks.append(watcher(key, value, version))
                else:
                    tasks.append(asyncio.to_thread(watcher, key, value, version))
            except Exception as e:
                logger.error(f"Error creating watcher task: {e}")
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Log errors
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Watcher error for key {key}: {result}")
    
    async def clear(self) -> bool:
        """
        Clear all values in this namespace
        
        Returns:
            True if successful
        """
        try:
            # Clear local cache
            self._local_cache.clear()
            self._versions.clear()
            
            # Clear Redis if available
            if self._redis_client:
                pattern = f"shared_context:{self.namespace}:*"
                keys = []
                
                async for key in self._redis_client.scan_iter(match=pattern):
                    keys.append(key)
                
                if keys:
                    await self._redis_client.delete(*keys)
            
            logger.info(f"Cleared all context values for namespace: {self.namespace}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear context: {e}", exc_info=True)
            return False


def get_shared_context(namespace: str = "default") -> SharedContext:
    """
    Get or create a shared context for a namespace
    
    Args:
        namespace: Namespace for context isolation
        
    Returns:
        SharedContext instance
    """
    if namespace not in _shared_contexts:
        _shared_contexts[namespace] = SharedContext(namespace)
    
    return _shared_contexts[namespace]

