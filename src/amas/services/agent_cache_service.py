"""
Agent Cache Service
Agent performance caching with intelligent invalidation
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.cache.redis import get_redis_client

logger = logging.getLogger(__name__)

# Global service instance
_agent_cache_service: Optional["AgentCacheService"] = None


class AgentCacheService:
    """
    Agent performance caching service
    
    Features:
    - Cache agent performance metrics
    - Cache top agents rankings
    - Invalidate on execution completion
    - Pattern-based invalidation
    """
    
    def __init__(self):
        self.cache = get_redis_client()
        self.ttl_medium = 300  # 5 minutes
        self.key_prefix = "amas:agent:"
    
    def _make_key(self, *parts: str) -> str:
        """Generate cache key"""
        return f"{self.key_prefix}{':'.join(parts)}"
    
    def _serialize(self, data: Any) -> str:
        """Serialize data to JSON string"""
        if isinstance(data, dict):
            serialized = {}
            for key, value in data.items():
                if isinstance(value, datetime):
                    serialized[key] = value.isoformat()
                else:
                    serialized[key] = value
            return json.dumps(serialized)
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
    # AGENT PERFORMANCE CACHING
    # ========================================================================
    
    async def get_agent_performance(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get agent performance metrics (cached)
        
        TTL: 300 seconds (5 minutes)
        """
        if not self.cache:
            return await self._fetch_agent_performance_from_db(agent_id)
        
        cache_key = self._make_key("performance", agent_id)
        
        try:
            # Try cache
            cached = await self.cache.get(cache_key)
            if cached:
                logger.debug(f"Agent performance cache HIT: {agent_id}")
                return self._deserialize(cached)
            
            logger.debug(f"Agent performance cache MISS: {agent_id}")
            
            # Fetch from database
            performance = await self._fetch_agent_performance_from_db(agent_id)
            
            if performance:
                # Cache for 5 minutes
                await self.cache.setex(
                    cache_key,
                    self.ttl_medium,
                    self._serialize(performance)
                )
            
            return performance
        except Exception as e:
            logger.error(f"Error in get_agent_performance for {agent_id}: {e}")
            return await self._fetch_agent_performance_from_db(agent_id)
    
    async def _fetch_agent_performance_from_db(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Fetch agent performance from database"""
        try:
            from src.database.connection import async_session
            from sqlalchemy import text
            
            if not async_session:
                return {
                    "agent_id": agent_id,
                    "total_executions": 0,
                    "successful_executions": 0,
                    "failed_executions": 0,
                    "success_rate": 0.0,
                    "average_duration": 0.0,
                    "average_quality_score": 0.0,
                    "total_tokens_used": 0,
                    "total_cost_usd": 0.0
                }
            
            async with async_session() as session:
                # Aggregate performance metrics
                result = await session.execute(
                    text("""
                        SELECT 
                            COUNT(*) as total_executions,
                            COUNT(CASE WHEN success = true THEN 1 END) as successful_executions,
                            COUNT(CASE WHEN success = false THEN 1 END) as failed_executions,
                            AVG(duration_seconds) as average_duration,
                            AVG(quality_score) as average_quality_score,
                            SUM(tokens_used) as total_tokens_used,
                            SUM(cost_usd) as total_cost_usd
                        FROM task_executions
                        WHERE agent_id = :agent_id
                    """),
                    {"agent_id": agent_id}
                )
                row = result.fetchone()
                
                if row and row.total_executions > 0:
                    total = row.total_executions
                    successful = row.successful_executions or 0
                    
                    return {
                        "agent_id": agent_id,
                        "total_executions": total,
                        "successful_executions": successful,
                        "failed_executions": row.failed_executions or 0,
                        "success_rate": successful / total if total > 0 else 0.0,
                        "average_duration": float(row.average_duration or 0.0),
                        "average_quality_score": float(row.average_quality_score or 0.0),
                        "total_tokens_used": int(row.total_tokens_used or 0),
                        "total_cost_usd": float(row.total_cost_usd or 0.0)
                    }
                
                # Return default if no executions
                return {
                    "agent_id": agent_id,
                    "total_executions": 0,
                    "successful_executions": 0,
                    "failed_executions": 0,
                    "success_rate": 0.0,
                    "average_duration": 0.0,
                    "average_quality_score": 0.0,
                    "total_tokens_used": 0,
                    "total_cost_usd": 0.0
                }
        except Exception as e:
            logger.error(f"Database fetch failed for agent performance {agent_id}: {e}")
            return {
                "agent_id": agent_id,
                "total_executions": 0,
                "successful_executions": 0,
                "failed_executions": 0,
                "success_rate": 0.0,
                "average_duration": 0.0,
                "average_quality_score": 0.0,
                "total_tokens_used": 0,
                "total_cost_usd": 0.0
            }
    
    # ========================================================================
    # TOP AGENTS CACHING
    # ========================================================================
    
    async def get_top_agents(
        self,
        task_type: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get top performing agents (cached)
        
        Cache rankings (expensive query)
        TTL: 300 seconds
        """
        if not self.cache:
            return await self._fetch_top_agents_from_db(task_type, limit)
        
        cache_key = self._make_key(
            "top",
            task_type or "all",
            str(limit)
        )
        
        try:
            # Try cache
            cached = await self.cache.get(cache_key)
            if cached:
                logger.debug(f"Top agents cache HIT: {task_type or 'all'}")
                return self._deserialize(cached)
            
            logger.debug(f"Top agents cache MISS: {task_type or 'all'}")
            
            # Fetch from database
            top_agents = await self._fetch_top_agents_from_db(task_type, limit)
            
            if top_agents:
                # Cache for 5 minutes
                await self.cache.setex(
                    cache_key,
                    self.ttl_medium,
                    self._serialize(top_agents)
                )
            
            return top_agents
        except Exception as e:
            logger.error(f"Error in get_top_agents: {e}")
            return await self._fetch_top_agents_from_db(task_type, limit)
    
    async def _fetch_top_agents_from_db(
        self,
        task_type: Optional[str],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Fetch top agents from database"""
        try:
            from src.database.connection import async_session
            from sqlalchemy import text
            
            if not async_session:
                return []
            
            async with async_session() as session:
                if task_type:
                    # Filter by task type
                    result = await session.execute(
                        text("""
                            SELECT 
                                agent_id,
                                COUNT(*) as total_executions,
                                COUNT(CASE WHEN success = true THEN 1 END) as successful_executions,
                                AVG(duration_seconds) as average_duration,
                                AVG(quality_score) as average_quality_score,
                                AVG(CASE WHEN success = true THEN 1.0 ELSE 0.0 END) as success_rate
                            FROM task_executions
                            WHERE task_type = :task_type
                            GROUP BY agent_id
                            ORDER BY 
                                success_rate DESC,
                                average_quality_score DESC,
                                total_executions DESC
                            LIMIT :limit
                        """),
                        {"task_type": task_type, "limit": limit}
                    )
                else:
                    # All task types
                    result = await session.execute(
                        text("""
                            SELECT 
                                agent_id,
                                COUNT(*) as total_executions,
                                COUNT(CASE WHEN success = true THEN 1 END) as successful_executions,
                                AVG(duration_seconds) as average_duration,
                                AVG(quality_score) as average_quality_score,
                                AVG(CASE WHEN success = true THEN 1.0 ELSE 0.0 END) as success_rate
                            FROM task_executions
                            GROUP BY agent_id
                            ORDER BY 
                                success_rate DESC,
                                average_quality_score DESC,
                                total_executions DESC
                            LIMIT :limit
                        """),
                        {"limit": limit}
                    )
                
                rows = result.fetchall()
                
                top_agents = []
                for row in rows:
                    agent_data = {
                        "agent_id": row.agent_id,
                        "total_executions": row.total_executions,
                        "successful_executions": row.successful_executions or 0,
                        "success_rate": float(row.success_rate or 0.0),
                        "average_duration": float(row.average_duration or 0.0),
                        "average_quality_score": float(row.average_quality_score or 0.0)
                    }
                    top_agents.append(agent_data)
                
                return top_agents
        except Exception as e:
            logger.error(f"Database fetch failed for top agents: {e}")
            return []
    
    # ========================================================================
    # CACHE INVALIDATION
    # ========================================================================
    
    async def invalidate_agent_caches(self, agent_id: str):
        """
        Invalidate all caches for an agent
        
        Called on execution completion or agent update
        """
        if not self.cache:
            return
        
        try:
            # Invalidate performance cache
            performance_key = self._make_key("performance", agent_id)
            await self.cache.delete(performance_key)
            
            # Invalidate top agents caches (all task types)
            pattern = self._make_key("top", "*")
            cursor = 0
            while True:
                cursor, keys = await self.cache.scan(
                    cursor,
                    match=pattern,
                    count=100
                )
                if keys:
                    await self.cache.delete(*keys)
                if cursor == 0:
                    break
            
            logger.debug(f"Invalidated caches for agent: {agent_id}")
        except Exception as e:
            logger.error(f"Failed to invalidate agent caches for {agent_id}: {e}")


def get_agent_cache_service() -> AgentCacheService:
    """Get global AgentCacheService instance (singleton pattern)"""
    global _agent_cache_service
    
    if _agent_cache_service is None:
        _agent_cache_service = AgentCacheService()
    
    return _agent_cache_service

