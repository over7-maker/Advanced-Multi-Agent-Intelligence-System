"""
Task Cache Service
Task-specific caching with read-through, write-through patterns, and intelligent invalidation
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.cache.redis import get_redis_client

logger = logging.getLogger(__name__)

# Global service instance
_task_cache_service: Optional["TaskCacheService"] = None


class TaskCacheService:
    """
    Task-specific caching strategies
    
    Features:
    - Cache task details (read-through)
    - Cache task lists with pagination
    - Cache task statistics
    - Write-through caching
    - Pattern-based invalidation
    - Recent tasks feed (Redis list)
    """
    
    def __init__(self):
        self.cache = get_redis_client()
        self.ttl_short = 60  # 1 minute
        self.ttl_medium = 300  # 5 minutes
        self.ttl_long = 3600  # 1 hour
        self.key_prefix = "amas:task:"
    
    def _make_key(self, *parts: str) -> str:
        """Generate cache key"""
        return f"{self.key_prefix}{':'.join(parts)}"
    
    def _serialize(self, data: Any) -> str:
        """Serialize data to JSON string"""
        if isinstance(data, dict):
            # Convert datetime objects to ISO format strings
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
    # TASK DETAIL CACHING
    # ========================================================================
    
    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get task with caching (read-through pattern)
        
        Strategy: Check cache first, fetch from DB if miss, cache result
        """
        if not self.cache:
            logger.warning("Redis cache not available, fetching from database")
            return await self._fetch_task_from_db(task_id)
        
        cache_key = self._make_key("detail", task_id)
        
        try:
            # Try cache first
            cached = await self.cache.get(cache_key)
            if cached:
                logger.debug(f"Task cache HIT: {task_id}")
                return self._deserialize(cached)
            
            logger.debug(f"Task cache MISS: {task_id}")
            
            # Fetch from database
            task = await self._fetch_task_from_db(task_id)
            
            if task:
                # Cache for 5 minutes
                try:
                    await self.cache.setex(
                        cache_key,
                        self.ttl_medium,
                        self._serialize(task)
                    )
                except Exception as cache_error:
                    # Non-critical: cache write failed, but we still return the task
                    logger.debug(f"Cache write failed (non-critical): {cache_error}")
                return task
            
            return None
        except Exception as e:
            # Log as debug for expected errors (Redis auth, connection issues)
            logger.debug(f"Error in get_task for {task_id} (non-critical): {e}")
            # Try to fetch from DB as fallback
            try:
                return await self._fetch_task_from_db(task_id)
            except Exception:
                return None
    
    async def _fetch_task_from_db(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Fetch task from database"""
        try:
            from src.database.connection import async_session
            from sqlalchemy import text
            
            if not async_session:
                return None
            
            async with async_session() as session:
                result = await session.execute(
                    text("SELECT * FROM tasks WHERE task_id = :task_id"),
                    {"task_id": task_id}
                )
                row = result.fetchone()
                
                if row:
                    task_dict = dict(row._mapping)
                    # Convert datetime objects to ISO format
                    for key, value in task_dict.items():
                        if isinstance(value, datetime):
                            task_dict[key] = value.isoformat()
                    return task_dict
        except Exception as e:
            logger.error(f"Database fetch failed for task {task_id}: {e}")
        return None
    
    async def update_task(
        self,
        task_id: str,
        update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update task with write-through caching
        
        Strategy: Update DB, update cache immediately, invalidate related caches
        """
        try:
            from src.database.connection import async_session
            from sqlalchemy import text
            
            if not async_session:
                logger.warning("Database not available for task update")
                return None
            
            # Build update query - use id instead of task_id
            # Since task_id is stored in description as JSON, we need to find the task by searching description
            # OR we can update by id if we have it, but for now, let's search in description
            set_clauses = []
            values = {}
            
            # Only update columns that exist in the schema: title, description, status, priority, updated_at
            allowed_columns = {"title", "description", "status", "priority"}
            for key, value in update_data.items():
                if key in allowed_columns:
                    set_clauses.append(f"{key} = :{key}")
                    values[key] = value
            
            if not set_clauses:
                logger.warning(f"No valid columns to update for task {task_id}")
                return None
            
            # Search for task by task_id in description (where we store metadata)
            # Format: [METADATA:{"task_id": "...", ...}]
            query = f"""
            UPDATE tasks 
            SET {', '.join(set_clauses)}, updated_at = CURRENT_TIMESTAMP
            WHERE description LIKE :task_id_pattern
            RETURNING *
            """
            values["task_id_pattern"] = f"%task_id\":\"{task_id}\"%"
            
            async with async_session() as session:
                result = await session.execute(text(query), values)
                await session.commit()
                row = result.fetchone()
                
                if row:
                    task_dict = dict(row._mapping)
                    
                    # Serialize datetimes
                    for key, value in task_dict.items():
                        if isinstance(value, datetime):
                            task_dict[key] = value.isoformat()
                    
                    # Update cache (write-through)
                    if self.cache:
                        cache_key = self._make_key("detail", task_id)
                        await self.cache.setex(
                            cache_key,
                            self.ttl_medium,
                            self._serialize(task_dict)
                        )
                    
                    # Invalidate related caches
                    await self._invalidate_task_lists()
                    
                    logger.info(f"Updated task {task_id} (cache updated)")
                    return task_dict
            
            return None
        except Exception as e:
            logger.error(f"Failed to update task {task_id}: {e}")
            return None
    
    async def invalidate_task(self, task_id: str):
        """Invalidate task cache"""
        if not self.cache:
            return
        
        try:
            cache_key = self._make_key("detail", task_id)
            await self.cache.delete(cache_key)
            
            # Also invalidate lists
            await self._invalidate_task_lists()
            
            logger.debug(f"Invalidated cache for task: {task_id}")
        except Exception as e:
            logger.error(f"Failed to invalidate task cache {task_id}: {e}")
    
    # ========================================================================
    # TASK LIST CACHING
    # ========================================================================
    
    async def get_tasks_by_status(
        self,
        status: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get tasks by status with caching
        
        Strategy: Cache entire result set for common queries
        TTL: 60 seconds (short, as lists change frequently)
        """
        if not self.cache:
            return await self._fetch_tasks_by_status_from_db(status, limit, offset)
        
        cache_key = self._make_key("list", "status", status, str(limit), str(offset))
        
        try:
            # Try cache
            cached = await self.cache.get(cache_key)
            if cached:
                logger.debug(f"Task list cache HIT: {status}")
                return self._deserialize(cached)
            
            logger.debug(f"Task list cache MISS: {status}")
            
            # Fetch from database
            tasks = await self._fetch_tasks_by_status_from_db(status, limit, offset)
            
            if tasks:
                # Cache for 60 seconds
                await self.cache.setex(
                    cache_key,
                    self.ttl_short,
                    self._serialize(tasks)
                )
            
            return tasks
        except Exception as e:
            logger.error(f"Error in get_tasks_by_status: {e}")
            return await self._fetch_tasks_by_status_from_db(status, limit, offset)
    
    async def _fetch_tasks_by_status_from_db(
        self,
        status: str,
        limit: int,
        offset: int
    ) -> List[Dict[str, Any]]:
        """Fetch tasks by status from database"""
        try:
            from src.database.connection import async_session
            from sqlalchemy import text
            
            if not async_session:
                return []
            
            async with async_session() as session:
                result = await session.execute(
                    text("""
                        SELECT * FROM tasks 
                        WHERE status = :status 
                        ORDER BY created_at DESC 
                        LIMIT :limit OFFSET :offset
                    """),
                    {"status": status, "limit": limit, "offset": offset}
                )
                rows = result.fetchall()
                
                tasks_list = []
                for row in rows:
                    task_dict = dict(row._mapping)
                    # Convert datetime objects
                    for key, value in task_dict.items():
                        if isinstance(value, datetime):
                            task_dict[key] = value.isoformat()
                    tasks_list.append(task_dict)
                
                return tasks_list
        except Exception as e:
            logger.error(f"Database fetch failed for tasks by status: {e}")
            return []
    
    # ========================================================================
    # TASK STATISTICS CACHING
    # ========================================================================
    
    async def get_task_statistics(self) -> Dict[str, Any]:
        """
        Get global task statistics (cached)
        
        TTL: 300 seconds (medium, stats change slowly)
        """
        if not self.cache:
            return await self._fetch_statistics_from_db()
        
        cache_key = self._make_key("stats", "global")
        
        try:
            # Try cache
            cached = await self.cache.get(cache_key)
            if cached:
                logger.debug("Task statistics cache HIT")
                return self._deserialize(cached)
            
            logger.debug("Task statistics cache MISS")
            
            # Fetch from database
            stats = await self._fetch_statistics_from_db()
            
            if stats:
                # Cache for 5 minutes
                await self.cache.setex(
                    cache_key,
                    self.ttl_medium,
                    self._serialize(stats)
                )
            
            return stats
        except Exception as e:
            logger.error(f"Error in get_task_statistics: {e}")
            return await self._fetch_statistics_from_db()
    
    async def _fetch_statistics_from_db(self) -> Dict[str, Any]:
        """Fetch statistics from database"""
        try:
            from src.database.connection import async_session
            from sqlalchemy import text
            
            if not async_session:
                return {
                    "total_tasks": 0,
                    "pending": 0,
                    "executing": 0,
                    "completed": 0,
                    "failed": 0
                }
            
            async with async_session() as session:
                # Get counts by status
                result = await session.execute(
                    text("""
                        SELECT 
                            status,
                            COUNT(*) as count
                        FROM tasks
                        GROUP BY status
                    """)
                )
                rows = result.fetchall()
                
                stats = {
                    "total_tasks": 0,
                    "pending": 0,
                    "executing": 0,
                    "completed": 0,
                    "failed": 0
                }
                
                for row in rows:
                    status = row.status
                    count = row.count
                    stats["total_tasks"] += count
                    if status in stats:
                        stats[status] = count
                
                return stats
        except Exception as e:
            logger.error(f"Database fetch failed for statistics: {e}")
            return {
                "total_tasks": 0,
                "pending": 0,
                "executing": 0,
                "completed": 0,
                "failed": 0
            }
    
    # ========================================================================
    # RECENT TASKS FEED
    # ========================================================================
    
    async def add_to_recent_feed(self, task_data: Dict[str, Any]):
        """Add task to recent feed (Redis list)"""
        if not self.cache:
            return
        
        try:
            feed_key = self._make_key("feed", "recent")
            # Add to list (left push)
            await self.cache.lpush(feed_key, self._serialize(task_data))
            # Keep only last 100 items
            await self.cache.ltrim(feed_key, 0, 99)
            # Set expiration on the list
            await self.cache.expire(feed_key, self.ttl_long)
        except Exception as e:
            logger.error(f"Failed to add to recent feed: {e}")
    
    async def get_recent_tasks(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent tasks from feed"""
        if not self.cache:
            return []
        
        try:
            feed_key = self._make_key("feed", "recent")
            # Get recent items (rightmost = newest)
            items = await self.cache.lrange(feed_key, 0, limit - 1)
            
            tasks = []
            for item in items:
                try:
                    task = self._deserialize(item)
                    if task:
                        tasks.append(task)
                except Exception as e:
                    logger.warning(f"Failed to deserialize recent task: {e}")
            
            return tasks
        except Exception as e:
            logger.error(f"Failed to get recent tasks: {e}")
            return []
    
    # ========================================================================
    # CACHE INVALIDATION
    # ========================================================================
    
    async def _invalidate_task_lists(self):
        """Invalidate all task list caches"""
        if not self.cache:
            return
        
        try:
            # Invalidate all status lists
            pattern = self._make_key("list", "status", "*")
            # Note: Redis doesn't support wildcard delete directly
            # We'll need to scan and delete
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
            
            # Invalidate statistics
            stats_key = self._make_key("stats", "*")
            cursor = 0
            while True:
                cursor, keys = await self.cache.scan(
                    cursor,
                    match=stats_key,
                    count=100
                )
                if keys:
                    await self.cache.delete(*keys)
                if cursor == 0:
                    break
            
            logger.debug("Invalidated task list caches")
        except Exception as e:
            logger.error(f"Failed to invalidate task lists: {e}")


def get_task_cache_service() -> TaskCacheService:
    """Get global TaskCacheService instance (singleton pattern)"""
    global _task_cache_service
    
    if _task_cache_service is None:
        _task_cache_service = TaskCacheService()
    
    return _task_cache_service

