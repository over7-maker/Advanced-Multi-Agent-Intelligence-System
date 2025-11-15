"""
AI Performance Analysis and Optimization System

Continuously analyzes agent performance, workflow efficiency, and system
optimization to enable autonomous self-improvement and learning.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import uuid
import json
import numpy as np
import pandas as pd
from pathlib import Path
import sqlite3
from collections import defaultdict, deque
import statistics
from scipy import stats

logger = logging.getLogger(__name__)

class MetricType(str, Enum):
    # Agent performance metrics
    TASK_SUCCESS_RATE = "task_success_rate"
    TASK_COMPLETION_TIME = "task_completion_time"
    QUALITY_SCORE = "quality_score"
    COST_EFFICIENCY = "cost_efficiency"
    # Workflow performance metrics
    WORKFLOW_SUCCESS_RATE = "workflow_success_rate"
    WORKFLOW_DURATION = "workflow_duration"
    AGENT_COORDINATION = "agent_coordination"
    RESOURCE_UTILIZATION = "resource_utilization"
    # System performance metrics
    SYSTEM_THROUGHPUT = "system_throughput"
    SYSTEM_LATENCY = "system_latency"
    ERROR_RATE = "error_rate"
    USER_SATISFACTION = "user_satisfaction"

class TrendDirection(str, Enum):
    IMPROVING = "improving"
    STABLE = "stable"
    DECLINING = "declining"
    CRITICAL = "critical"

@dataclass
class PerformanceMetric:
    """Individual performance metric with historical data."""
    id: str
    metric_type: MetricType
    entity_id: str  # agent_id, workflow_id, or 'system'
    entity_type: str  # 'agent', 'workflow', 'system'
    current_value: float
    target_value: float
    threshold_warning: float
    threshold_critical: float
    historical_values: List[Tuple[datetime, float]] = field(default_factory=list)
    trend_direction: TrendDirection = TrendDirection.STABLE
    trend_strength: float = 0.0  # -1.0 to 1.0
    confidence_interval: Tuple[float, float] = (0.0, 0.0)
    baseline_value: float = 0.0
    improvement_percentage: float = 0.0
    last_improvement_date: Optional[datetime] = None
    tags: Set[str] = field(default_factory=set)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self):
        if self.entity_type not in {"agent", "workflow", "system"}:
            raise ValueError(f"Invalid entity_type: {self.entity_type}")
        if not self.id:
            raise ValueError("Metric id cannot be empty")

    def add_data_point(self, value: float, timestamp: datetime = None):
        timestamp = timestamp or datetime.now(timezone.utc)
        self.historical_values.append((timestamp, value))
        self.current_value = value
        self.updated_at = timestamp
        if len(self.historical_values) > 1000:
            self.historical_values = self.historical_values[-1000:]
        self._analyze_trend()

    def _analyze_trend(self):
        if len(self.historical_values) < 5:
            return
        recent_cutoff = datetime.now(timezone.utc) - timedelta(days=7)
        recent_values = [ (ts, val) for ts, val in self.historical_values[-30:] if ts > recent_cutoff ]
        if len(recent_values) < 3:
            return
        timestamps = [ts.timestamp() for ts, val in recent_values]
        values = [val for ts, val in recent_values]
        try:
            slope, intercept, r_value, p_value, std_err = stats.linregress(timestamps, values)
            self.trend_strength = r_value
            if abs(slope) < 0.001:
                self.trend_direction = TrendDirection.STABLE
            elif slope > 0:
                self.trend_direction = TrendDirection.IMPROVING if self.current_value >= self.threshold_warning else TrendDirection.DECLINING
            else:
                if self.current_value <= self.threshold_critical:
                    self.trend_direction = TrendDirection.CRITICAL
                elif self.current_value <= self.threshold_warning:
                    self.trend_direction = TrendDirection.DECLINING
                else:
                    self.trend_direction = TrendDirection.STABLE
            if len(values) > 2:
                std_dev = statistics.stdev(values)
                self.confidence_interval = (
                    self.current_value - 1.96 * std_dev,
                    self.current_value + 1.96 * std_dev
                )
        except Exception as e:
            logger.warning(f"Error analyzing trend for metric {self.id}: {e}")

    def get_health_status(self) -> str:
        if self.current_value <= self.threshold_critical:
            return "critical"
        elif self.current_value <= self.threshold_warning:
            return "warning"
        elif self.current_value >= self.target_value:
            return "excellent"
        else:
            return "good"

    def calculate_improvement_since_baseline(self) -> float:
        if self.baseline_value == 0:
            return 0.0
        improvement = ((self.current_value - self.baseline_value) / self.baseline_value) * 100
        self.improvement_percentage = improvement
        return improvement
