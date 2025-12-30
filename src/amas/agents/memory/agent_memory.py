"""
Agent Memory System
Stores task history, learns patterns, and improves over time
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)

# Try to use Redis if available, fallback to in-memory
try:
    from src.cache.redis import get_redis_client
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available, using in-memory storage for agent memory")


class AgentMemory:
    """
    Agent Memory System
    
    Features:
    - Task history storage
    - Pattern recognition
    - Error learning
    - Context memory
    - Expertise score tracking
    """
    
    def __init__(self, agent_id: str, use_redis: bool = True):
        self.agent_id = agent_id
        self.use_redis = use_redis and REDIS_AVAILABLE
        self.logger = logging.getLogger(f"{__name__}.{agent_id}")
        
        # In-memory storage (fallback)
        self._task_history: List[Dict[str, Any]] = []
        self._patterns: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self._expertise_scores: Dict[str, float] = {}
        
        # Redis client (if available)
        self.redis_client = None
        if self.use_redis:
            try:
                self.redis_client = get_redis_client()
                if not self.redis_client:
                    self.use_redis = False
                    self.logger.warning("Redis client not available, using in-memory storage")
            except Exception as e:
                self.use_redis = False
                self.logger.warning(f"Failed to initialize Redis: {e}, using in-memory storage")
    
    def _make_key(self, *parts: str) -> str:
        """Generate Redis key"""
        return f"amas:agent:memory:{self.agent_id}:{':'.join(parts)}"
    
    async def store_execution(
        self,
        task_id: str,
        result: Dict[str, Any],
        context: Dict[str, Any]
    ) -> bool:
        """
        Store task execution in memory
        
        Args:
            task_id: Task identifier
            result: Execution result
            context: Task context
        """
        try:
            execution_record = {
                "task_id": task_id,
                "timestamp": datetime.utcnow().isoformat(),
                "result": result,
                "context": context,
                "success": result.get("success", False),
                "quality_score": result.get("quality_score", 0.0),
                "duration": result.get("duration", 0.0)
            }
            
            if self.use_redis and self.redis_client:
                # Store in Redis with TTL (30 days)
                key = self._make_key("executions", task_id)
                await self.redis_client.setex(
                    key,
                    30 * 24 * 60 * 60,  # 30 days
                    json.dumps(execution_record, default=str)
                )
                
                # Add to task history list (keep last 1000)
                history_key = self._make_key("history")
                await self.redis_client.lpush(history_key, json.dumps(execution_record, default=str))
                await self.redis_client.ltrim(history_key, 0, 999)  # Keep last 1000
            else:
                # Store in memory
                self._task_history.append(execution_record)
                # Keep only last 1000
                if len(self._task_history) > 1000:
                    self._task_history = self._task_history[-1000:]
            
            # Update patterns
            await self._update_patterns(execution_record)
            
            # Update expertise score
            await self.update_expertise_score(
                result.get("success", False),
                result.get("quality_score", 0.0)
            )
            
            self.logger.debug(f"Stored execution for task {task_id}")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to store execution for task {task_id}: {e}", exc_info=True)
            return False
    
    async def retrieve_similar_tasks(
        self,
        current_task: Dict[str, Any],
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve similar tasks from history
        
        Args:
            current_task: Current task to find similarities for
            limit: Maximum number of similar tasks to return
            
        Returns:
            List of similar task executions
        """
        try:
            task_type = current_task.get("task_type") or current_task.get("type", "unknown")
            target = current_task.get("target", "")
            
            similar_tasks = []
            
            if self.use_redis and self.redis_client:
                # Get from Redis
                history_key = self._make_key("history")
                history_data = await self.redis_client.lrange(history_key, 0, 999)
                
                for item in history_data:
                    try:
                        task_record = json.loads(item)
                        # Simple similarity: same task type or similar target
                        if (task_record.get("context", {}).get("task_type") == task_type or
                            target in str(task_record.get("context", {}).get("target", ""))):
                            similar_tasks.append(task_record)
                    except Exception:
                        continue
            else:
                # Search in memory
                for task_record in self._task_history:
                    task_context = task_record.get("context", {})
                    if (task_context.get("task_type") == task_type or
                        target in str(task_context.get("target", ""))):
                        similar_tasks.append(task_record)
            
            # Sort by quality score and recency
            similar_tasks.sort(
                key=lambda x: (
                    x.get("quality_score", 0.0),
                    datetime.fromisoformat(x.get("timestamp", "2000-01-01")).timestamp()
                ),
                reverse=True
            )
            
            return similar_tasks[:limit]
        
        except Exception as e:
            self.logger.error(f"Failed to retrieve similar tasks: {e}", exc_info=True)
            return []
    
    async def get_learned_patterns(self, task_type: str) -> Dict[str, Any]:
        """
        Get learned patterns for a task type
        
        Args:
            task_type: Type of task
            
        Returns:
            Learned patterns and insights
        """
        try:
            if self.use_redis and self.redis_client:
                pattern_key = self._make_key("patterns", task_type)
                pattern_data = await self.redis_client.get(pattern_key)
                if pattern_data:
                    return json.loads(pattern_data)
            else:
                if task_type in self._patterns:
                    patterns = self._patterns[task_type]
                    if patterns:
                        # Aggregate patterns
                        return {
                            "task_type": task_type,
                            "success_rate": sum(1 for p in patterns if p.get("success")) / len(patterns),
                            "avg_quality": sum(p.get("quality_score", 0.0) for p in patterns) / len(patterns),
                            "common_approaches": self._extract_common_approaches(patterns),
                            "common_errors": self._extract_common_errors(patterns)
                        }
            
            return {
                "task_type": task_type,
                "success_rate": 0.0,
                "avg_quality": 0.0,
                "common_approaches": [],
                "common_errors": []
            }
        
        except Exception as e:
            self.logger.error(f"Failed to get learned patterns: {e}", exc_info=True)
            return {}
    
    async def update_expertise_score(self, success: bool, quality_score: float):
        """
        Update agent expertise score based on execution results
        
        Args:
            success: Whether execution was successful
            quality_score: Quality score (0-1)
        """
        try:
            # Calculate new expertise score (weighted average)
            current_score = self._expertise_scores.get("overall", 0.90)
            
            # Weight: 70% current, 30% new result
            if success:
                new_score = current_score * 0.7 + quality_score * 0.3
            else:
                # Penalize failures less
                new_score = current_score * 0.8 + quality_score * 0.2
            
            self._expertise_scores["overall"] = new_score
            
            if self.use_redis and self.redis_client:
                score_key = self._make_key("expertise_score")
                await self.redis_client.set(
                    score_key,
                    json.dumps(self._expertise_scores, default=str)
                )
            
            self.logger.debug(f"Updated expertise score: {new_score:.2f}")
        
        except Exception as e:
            self.logger.error(f"Failed to update expertise score: {e}", exc_info=True)
    
    def get_expertise_score(self) -> float:
        """Get current expertise score"""
        return self._expertise_scores.get("overall", 0.90)
    
    async def _update_patterns(self, execution_record: Dict[str, Any]):
        """Update learned patterns from execution"""
        try:
            context = execution_record.get("context", {})
            task_type = context.get("task_type") or context.get("type", "unknown")
            
            pattern_entry = {
                "success": execution_record.get("success", False),
                "quality_score": execution_record.get("quality_score", 0.0),
                "approach": context.get("approach", "default"),
                "tools_used": context.get("tools_used", []),
                "timestamp": execution_record.get("timestamp")
            }
            
            if self.use_redis and self.redis_client:
                pattern_key = self._make_key("patterns", task_type)
                # Get existing patterns
                existing_data = await self.redis_client.get(pattern_key)
                patterns = json.loads(existing_data) if existing_data else []
                patterns.append(pattern_entry)
                # Keep last 100 patterns per task type
                if len(patterns) > 100:
                    patterns = patterns[-100:]
                await self.redis_client.setex(
                    pattern_key,
                    90 * 24 * 60 * 60,  # 90 days
                    json.dumps(patterns, default=str)
                )
            else:
                self._patterns[task_type].append(pattern_entry)
                # Keep last 100 patterns per task type
                if len(self._patterns[task_type]) > 100:
                    self._patterns[task_type] = self._patterns[task_type][-100:]
        
        except Exception as e:
            self.logger.error(f"Failed to update patterns: {e}", exc_info=True)
    
    def _extract_common_approaches(self, patterns: List[Dict[str, Any]]) -> List[str]:
        """Extract common successful approaches from patterns"""
        successful_patterns = [p for p in patterns if p.get("success")]
        approaches = defaultdict(int)
        
        for pattern in successful_patterns:
            approach = pattern.get("approach", "default")
            approaches[approach] += 1
        
        # Return top 3 approaches
        return [approach for approach, _ in sorted(approaches.items(), key=lambda x: x[1], reverse=True)[:3]]
    
    def _extract_common_errors(self, patterns: List[Dict[str, Any]]) -> List[str]:
        """Extract common errors from failed patterns"""
        failed_patterns = [p for p in patterns if not p.get("success")]
        # This would require storing error messages in patterns
        # For now, return empty list
        return []


# Global memory instances
_agent_memories: Dict[str, AgentMemory] = {}


def get_agent_memory(agent_id: str, use_redis: bool = True) -> AgentMemory:
    """Get or create agent memory instance"""
    if agent_id not in _agent_memories:
        _agent_memories[agent_id] = AgentMemory(agent_id, use_redis)
    return _agent_memories[agent_id]

