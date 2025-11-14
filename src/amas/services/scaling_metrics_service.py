"""
Scaling Metrics Service for AMAS

Tracks autoscaling decisions, scaling events, and scaling effectiveness.
Provides metrics for monitoring scaling behavior.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    from prometheus_client import Counter, Gauge, Histogram
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    # Dummy classes
    class Counter:
        def __init__(self, *args, **kwargs):
            pass
        def inc(self, *args, **kwargs):
            pass
        def labels(self, *args, **kwargs):
            return self
    class Gauge:
        def __init__(self, *args, **kwargs):
            pass
        def set(self, *args, **kwargs):
            pass
        def labels(self, *args, **kwargs):
            return self
    class Histogram:
        def __init__(self, *args, **kwargs):
            pass
        def observe(self, *args, **kwargs):
            pass

logger = logging.getLogger(__name__)

# Prometheus metrics for scaling
if PROMETHEUS_AVAILABLE:
    SCALING_EVENTS = Counter(
        "amas_scaling_events_total",
        "Total scaling events",
        ["component", "direction", "reason"]
    )
    CURRENT_REPLICAS = Gauge(
        "amas_current_replicas",
        "Current number of replicas",
        ["component"]
    )
    SCALING_DURATION = Histogram(
        "amas_scaling_duration_seconds",
        "Time taken for scaling operations",
        ["component", "direction"],
        buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 120.0]
    )
    SCALING_EFFECTIVENESS = Gauge(
        "amas_scaling_effectiveness",
        "Scaling effectiveness (requests per replica)",
        ["component"]
    )


@dataclass
class ScalingEvent:
    """Scaling event data"""
    timestamp: datetime
    component: str
    direction: str  # "up" or "down"
    from_replicas: int
    to_replicas: int
    reason: str
    trigger_metric: Optional[str] = None
    trigger_value: Optional[float] = None
    duration_seconds: Optional[float] = None


class ScalingMetricsService:
    """
    Service for tracking scaling events and metrics.
    
    Features:
    - Track scaling events (scale up/down)
    - Monitor scaling effectiveness
    - Record scaling reasons and triggers
    - Provide scaling analytics
    """
    
    def __init__(self):
        """Initialize scaling metrics service"""
        self.events: List[ScalingEvent] = []
        self.max_events = 1000  # Keep last 1000 events
        
        # Current state
        self.current_replicas: Dict[str, int] = {}
        self.scaling_history: Dict[str, List[ScalingEvent]] = {}
    
    def record_scaling_event(
        self,
        component: str,
        direction: str,
        from_replicas: int,
        to_replicas: int,
        reason: str,
        trigger_metric: Optional[str] = None,
        trigger_value: Optional[float] = None,
        duration_seconds: Optional[float] = None
    ):
        """
        Record a scaling event.
        
        Args:
            component: Component name (e.g., "orchestrator", "worker")
            direction: "up" or "down"
            from_replicas: Number of replicas before scaling
            to_replicas: Number of replicas after scaling
            reason: Reason for scaling
            trigger_metric: Metric that triggered scaling
            trigger_value: Value of trigger metric
            duration_seconds: Time taken for scaling
        """
        event = ScalingEvent(
            timestamp=datetime.utcnow(),
            component=component,
            direction=direction,
            from_replicas=from_replicas,
            to_replicas=to_replicas,
            reason=reason,
            trigger_metric=trigger_metric,
            trigger_value=trigger_value,
            duration_seconds=duration_seconds
        )
        
        self.events.append(event)
        
        # Keep only last N events
        if len(self.events) > self.max_events:
            self.events = self.events[-self.max_events:]
        
        # Track per component
        if component not in self.scaling_history:
            self.scaling_history[component] = []
        self.scaling_history[component].append(event)
        
        # Update current replicas
        self.current_replicas[component] = to_replicas
        
        # Update Prometheus metrics
        if PROMETHEUS_AVAILABLE:
            SCALING_EVENTS.labels(
                component=component,
                direction=direction,
                reason=reason
            ).inc()
            
            CURRENT_REPLICAS.labels(component=component).set(to_replicas)
            
            if duration_seconds:
                SCALING_DURATION.labels(
                    component=component,
                    direction=direction
                ).observe(duration_seconds)
        
        logger.info(
            f"Scaling event: {component} {direction} "
            f"{from_replicas} -> {to_replicas} ({reason})"
        )
    
    def update_scaling_effectiveness(
        self,
        component: str,
        requests_per_second: float
    ):
        """
        Update scaling effectiveness metric.
        
        Args:
            component: Component name
            requests_per_second: Current requests per second
        """
        current_replicas = self.current_replicas.get(component, 1)
        if current_replicas > 0:
            effectiveness = requests_per_second / current_replicas
        else:
            effectiveness = 0.0
        
        if PROMETHEUS_AVAILABLE:
            SCALING_EFFECTIVENESS.labels(component=component).set(effectiveness)
    
    def get_scaling_stats(
        self,
        component: Optional[str] = None,
        hours: int = 24
    ) -> Dict[str, Any]:
        """
        Get scaling statistics.
        
        Args:
            component: Optional component filter
            hours: Number of hours to look back
            
        Returns:
            Dictionary with scaling statistics
        """
        from datetime import timedelta
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        if component:
            events = [
                e for e in self.scaling_history.get(component, [])
                if e.timestamp >= cutoff_time
            ]
        else:
            events = [e for e in self.events if e.timestamp >= cutoff_time]
        
        scale_ups = [e for e in events if e.direction == "up"]
        scale_downs = [e for e in events if e.direction == "down"]
        
        total_scale_ups = len(scale_ups)
        total_scale_downs = len(scale_downs)
        
        avg_scale_up_duration = (
            sum(e.duration_seconds for e in scale_ups if e.duration_seconds) / total_scale_ups
            if total_scale_ups > 0 else 0.0
        )
        
        avg_scale_down_duration = (
            sum(e.duration_seconds for e in scale_downs if e.duration_seconds) / total_scale_downs
            if total_scale_downs > 0 else 0.0
        )
        
        # Most common scaling reasons
        reasons = {}
        for event in events:
            reasons[event.reason] = reasons.get(event.reason, 0) + 1
        
        return {
            "total_events": len(events),
            "scale_ups": total_scale_ups,
            "scale_downs": total_scale_downs,
            "avg_scale_up_duration_seconds": avg_scale_up_duration,
            "avg_scale_down_duration_seconds": avg_scale_down_duration,
            "most_common_reasons": dict(sorted(reasons.items(), key=lambda x: x[1], reverse=True)[:5]),
            "current_replicas": self.current_replicas.copy(),
            "period_hours": hours
        }
    
    def get_recent_events(
        self,
        component: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get recent scaling events.
        
        Args:
            component: Optional component filter
            limit: Maximum number of events to return
            
        Returns:
            List of recent scaling events
        """
        if component:
            events = self.scaling_history.get(component, [])
        else:
            events = self.events
        
        recent = sorted(events, key=lambda e: e.timestamp, reverse=True)[:limit]
        
        return [
            {
                "timestamp": e.timestamp.isoformat(),
                "component": e.component,
                "direction": e.direction,
                "from_replicas": e.from_replicas,
                "to_replicas": e.to_replicas,
                "reason": e.reason,
                "trigger_metric": e.trigger_metric,
                "trigger_value": e.trigger_value,
                "duration_seconds": e.duration_seconds
            }
            for e in recent
        ]


# Global instance
_scaling_metrics_service: Optional[ScalingMetricsService] = None


def get_scaling_metrics_service() -> ScalingMetricsService:
    """Get global scaling metrics service instance"""
    global _scaling_metrics_service
    
    if _scaling_metrics_service is None:
        _scaling_metrics_service = ScalingMetricsService()
    
    return _scaling_metrics_service
