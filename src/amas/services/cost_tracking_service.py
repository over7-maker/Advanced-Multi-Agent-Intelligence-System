"""
Cost Tracking and Optimization Service for AMAS

Tracks token usage, API costs, and infrastructure costs per request.
Provides optimization recommendations.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

logger = logging.getLogger(__name__)


@dataclass
class CostEntry:
    """Cost entry for a single request"""
    request_id: str
    timestamp: datetime
    provider: str
    model: str
    tokens_input: int
    tokens_output: int
    tokens_total: int
    cost_usd: float
    latency_ms: float
    success: bool


@dataclass
class CostSummary:
    """Cost summary for a time period"""
    period_start: datetime
    period_end: datetime
    total_requests: int
    total_tokens: int
    total_cost_usd: float
    avg_cost_per_request: float
    avg_tokens_per_request: float
    cost_by_provider: Dict[str, float] = field(default_factory=dict)
    cost_by_model: Dict[str, float] = field(default_factory=dict)
    requests_by_provider: Dict[str, int] = field(default_factory=dict)


# Provider cost per 1M tokens (input/output)
PROVIDER_COSTS = {
    "openai": {"gpt-4": {"input": 30.0, "output": 60.0}, "gpt-3.5-turbo": {"input": 0.5, "output": 1.5}},
    "anthropic": {"claude-3-opus": {"input": 15.0, "output": 75.0}, "claude-3-sonnet": {"input": 3.0, "output": 15.0}},
    "deepseek": {"deepseek-chat": {"input": 0.14, "output": 0.28}},
    "glm": {"glm-4": {"input": 0.1, "output": 0.1}},
    "grok": {"grok-beta": {"input": 0.1, "output": 0.1}},
    "ollama": {"llama2": {"input": 0.0, "output": 0.0}},  # Self-hosted
}


class CostTrackingService:
    """
    Service for tracking and optimizing costs.
    
    Features:
    - Token usage tracking
    - Cost calculation per request
    - Cost aggregation by provider/model
    - Optimization recommendations
    - Cost alerts
    """
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379/0",
        daily_budget_usd: float = 100.0
    ):
        """
        Initialize cost tracking service.
        
        Args:
            redis_url: Redis connection URL for cost storage
            daily_budget_usd: Daily budget limit in USD
        """
        self.redis_url = redis_url
        self.daily_budget_usd = daily_budget_usd
        self.redis_client: Optional[redis.Redis] = None
        
        # Cost statistics
        self.stats = {
            "total_requests": 0,
            "total_tokens": 0,
            "total_cost_usd": 0.0,
            "daily_cost_usd": 0.0
        }
    
    async def initialize(self):
        """Initialize Redis connection"""
        if not REDIS_AVAILABLE:
            logger.warning("Redis not available. Cost tracking will use in-memory storage.")
            self._memory_entries = []
            return
        
        try:
            self.redis_client = await redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("Cost tracking: Redis connection established")
        except Exception as e:
            logger.warning(f"Failed to connect to Redis for cost tracking: {e}. Using in-memory.")
            self.redis_client = None
            self._memory_entries = []
    
    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
    
    def calculate_cost(
        self,
        provider: str,
        model: str,
        tokens_input: int,
        tokens_output: int
    ) -> float:
        """
        Calculate cost for a request.
        
        Args:
            provider: Provider name
            model: Model name
            tokens_input: Input tokens
            tokens_output: Output tokens
            
        Returns:
            Cost in USD
        """
        provider_costs = PROVIDER_COSTS.get(provider.lower(), {})
        model_costs = provider_costs.get(model.lower(), {"input": 0.0, "output": 0.0})
        
        cost_input = (tokens_input / 1_000_000) * model_costs.get("input", 0.0)
        cost_output = (tokens_output / 1_000_000) * model_costs.get("output", 0.0)
        
        return cost_input + cost_output
    
    async def record_request(
        self,
        request_id: str,
        provider: str,
        model: str,
        tokens_input: int,
        tokens_output: int,
        latency_ms: float,
        success: bool = True
    ):
        """
        Record a request's cost.
        
        Args:
            request_id: Unique request identifier
            provider: Provider name
            model: Model name
            tokens_input: Input tokens
            tokens_output: Output tokens
            latency_ms: Request latency in milliseconds
            success: Whether request was successful
        """
        tokens_total = tokens_input + tokens_output
        cost_usd = self.calculate_cost(provider, model, tokens_input, tokens_output)
        
        entry = CostEntry(
            request_id=request_id,
            timestamp=datetime.utcnow(),
            provider=provider,
            model=model,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            tokens_total=tokens_total,
            cost_usd=cost_usd,
            latency_ms=latency_ms,
            success=success
        )
        
        # Store in Redis or memory
        if self.redis_client:
            key = f"cost:entry:{request_id}"
            await self.redis_client.setex(
                key,
                86400 * 30,  # Keep for 30 days
                entry.__dict__.__str__()  # Simple serialization
            )
            
            # Update daily cost
            today_key = f"cost:daily:{datetime.utcnow().date().isoformat()}"
            await self.redis_client.incrbyfloat(today_key, cost_usd)
            await self.redis_client.expire(today_key, 86400 * 7)  # Keep for 7 days
        else:
            self._memory_entries.append(entry)
            # Keep only last 10000 entries in memory
            if len(self._memory_entries) > 10000:
                self._memory_entries = self._memory_entries[-10000:]
        
        # Update stats
        self.stats["total_requests"] += 1
        self.stats["total_tokens"] += tokens_total
        self.stats["total_cost_usd"] += cost_usd
        self.stats["daily_cost_usd"] += cost_usd
        
        # Check budget
        if self.stats["daily_cost_usd"] > self.daily_budget_usd:
            logger.warning(
                f"Daily budget exceeded: ${self.stats['daily_cost_usd']:.2f} > ${self.daily_budget_usd:.2f}"
            )
    
    async def get_cost_summary(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> CostSummary:
        """
        Get cost summary for a time period.
        
        Args:
            start_time: Start of period
            end_time: End of period
            
        Returns:
            CostSummary with aggregated data
        """
        # This would query Redis or memory for entries in the time range
        # For now, return summary from stats
        
        return CostSummary(
            period_start=start_time,
            period_end=end_time,
            total_requests=self.stats["total_requests"],
            total_tokens=self.stats["total_tokens"],
            total_cost_usd=self.stats["total_cost_usd"],
            avg_cost_per_request=(
                self.stats["total_cost_usd"] / self.stats["total_requests"]
                if self.stats["total_requests"] > 0 else 0.0
            ),
            avg_tokens_per_request=(
                self.stats["total_tokens"] / self.stats["total_requests"]
                if self.stats["total_requests"] > 0 else 0
            )
        )
    
    async def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """
        Get cost optimization recommendations.
        
        Returns:
            List of optimization recommendations
        """
        recommendations = []
        
        # Check if using expensive models
        if self.stats["total_cost_usd"] > 50.0:
            recommendations.append({
                "type": "model_optimization",
                "priority": "high",
                "message": "Consider using cheaper models for non-critical requests",
                "potential_savings": "30-50%"
            })
        
        # Check token usage
        if self.stats["avg_tokens_per_request"] > 2000:
            recommendations.append({
                "type": "token_optimization",
                "priority": "medium",
                "message": "High token usage detected. Consider optimizing prompts.",
                "potential_savings": "20-40%"
            })
        
        # Check daily budget
        if self.stats["daily_cost_usd"] > self.daily_budget_usd * 0.8:
            recommendations.append({
                "type": "budget_alert",
                "priority": "high",
                "message": f"Approaching daily budget: ${self.stats['daily_cost_usd']:.2f} / ${self.daily_budget_usd:.2f}",
                "potential_savings": "Enable rate limiting or caching"
            })
        
        return recommendations
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cost tracking statistics"""
        return {
            **self.stats,
            "daily_budget_usd": self.daily_budget_usd,
            "budget_utilization": (
                self.stats["daily_cost_usd"] / self.daily_budget_usd * 100
                if self.daily_budget_usd > 0 else 0.0
            )
        }


# Global instance
_cost_tracking_service: Optional[CostTrackingService] = None


async def get_cost_tracking_service(
    redis_url: str = "redis://localhost:6379/0",
    **kwargs
) -> CostTrackingService:
    """Get or create global cost tracking service instance"""
    global _cost_tracking_service
    
    if _cost_tracking_service is None:
        _cost_tracking_service = CostTrackingService(redis_url=redis_url, **kwargs)
        await _cost_tracking_service.initialize()
    
    return _cost_tracking_service
