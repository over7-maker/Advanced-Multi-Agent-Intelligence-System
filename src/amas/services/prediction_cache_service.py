"""
Prediction Cache Service
ML prediction caching with intelligent invalidation and version awareness
"""

import hashlib
import json
import logging
from typing import Any, Dict, Optional

from src.cache.redis import get_redis_client

logger = logging.getLogger(__name__)

# Global service instance
_prediction_cache_service: Optional["PredictionCacheService"] = None


class PredictionCacheService:
    """
    ML prediction caching with intelligent invalidation
    
    Features:
    - Cache predictions by input hash
    - Version-aware caching (include model version in key)
    - Invalidate on model retraining
    - TTL: 3600 seconds (1 hour)
    """
    
    def __init__(self, model_version: str = "v1.0"):
        self.cache = get_redis_client()
        self.model_version = model_version
        self.ttl = 3600  # 1 hour
        self.key_prefix = "amas:prediction:"
    
    def _generate_cache_key(self, task_data: Dict[str, Any]) -> str:
        """
        Generate deterministic cache key from task data
        
        Uses hash of canonical JSON representation
        Includes model version in key
        """
        # Create canonical representation (sorted keys)
        canonical = json.dumps(task_data, sort_keys=True)
        hash_value = hashlib.md5(canonical.encode()).hexdigest()
        
        # Include model version in key
        return f"{self.key_prefix}{self.model_version}:{hash_value}"
    
    def _serialize(self, data: Any) -> str:
        """Serialize data to JSON string"""
        return json.dumps(data)
    
    def _deserialize(self, data: str) -> Any:
        """Deserialize JSON string to Python object"""
        if not data:
            return None
        try:
            return json.loads(data)
        except (json.JSONDecodeError, TypeError):
            return data
    
    # ========================================================================
    # PREDICTION CACHING
    # ========================================================================
    
    async def get_prediction(
        self,
        task_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached prediction or None
        
        Key includes model version, so old predictions are automatically
        invalidated when model version changes
        """
        if not self.cache:
            return None
        
        try:
            cache_key = self._generate_cache_key(task_data)
            cached = await self.cache.get(cache_key)
            
            if cached:
                logger.debug(f"Prediction cache HIT: {cache_key[:50]}...")
                return self._deserialize(cached)
            
            logger.debug(f"Prediction cache MISS: {cache_key[:50]}...")
            return None
        except Exception as e:
            logger.error(f"Error in get_prediction: {e}")
            return None
    
    async def cache_prediction(
        self,
        task_data: Dict[str, Any],
        prediction: Dict[str, Any]
    ):
        """
        Cache prediction result
        
        TTL: 3600 seconds (1 hour)
        """
        if not self.cache:
            return
        
        try:
            cache_key = self._generate_cache_key(task_data)
            await self.cache.setex(
                cache_key,
                self.ttl,
                self._serialize(prediction)
            )
            logger.debug(f"Cached prediction: {cache_key[:50]}...")
        except Exception as e:
            logger.error(f"Failed to cache prediction: {e}")
    
    # ========================================================================
    # VERSION MANAGEMENT
    # ========================================================================
    
    async def invalidate_all_predictions(self):
        """
        Invalidate all predictions for current model version
        
        Called when model is retrained
        """
        if not self.cache:
            return
        
        try:
            # Invalidate all predictions for current version
            pattern = f"{self.key_prefix}{self.model_version}:*"
            cursor = 0
            deleted_count = 0
            
            while True:
                cursor, keys = await self.cache.scan(
                    cursor,
                    match=pattern,
                    count=100
                )
                if keys:
                    await self.cache.delete(*keys)
                    deleted_count += len(keys)
                if cursor == 0:
                    break
            
            logger.info(
                f"Invalidated {deleted_count} predictions for version {self.model_version}"
            )
        except Exception as e:
            logger.error(f"Failed to invalidate predictions: {e}")
    
    async def update_model_version(self, new_version: str):
        """
        Update model version (invalidates old predictions)
        
        This should be called when a model is retrained with a new version
        """
        old_version = self.model_version
        self.model_version = new_version
        
        # Invalidate old predictions
        if self.cache:
            try:
                pattern = f"{self.key_prefix}{old_version}:*"
                cursor = 0
                deleted_count = 0
                
                while True:
                    cursor, keys = await self.cache.scan(
                        cursor,
                        match=pattern,
                        count=100
                    )
                    if keys:
                        await self.cache.delete(*keys)
                        deleted_count += len(keys)
                    if cursor == 0:
                        break
                
                logger.info(
                    f"Updated model version from {old_version} to {new_version}, "
                    f"invalidated {deleted_count} old predictions"
                )
            except Exception as e:
                logger.error(f"Failed to invalidate old predictions: {e}")
    
    def get_model_version(self) -> str:
        """Get current model version"""
        return self.model_version


def get_prediction_cache_service(
    model_version: str = "v1.0"
) -> PredictionCacheService:
    """
    Get global PredictionCacheService instance (singleton pattern)
    
    Args:
        model_version: Model version to use (default: v1.0)
    """
    global _prediction_cache_service
    
    if _prediction_cache_service is None:
        _prediction_cache_service = PredictionCacheService(model_version=model_version)
    elif _prediction_cache_service.model_version != model_version:
        # Update version if changed
        _prediction_cache_service.model_version = model_version
    
    return _prediction_cache_service

