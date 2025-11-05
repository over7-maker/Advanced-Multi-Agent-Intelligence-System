"""
AI Performance Analysis and Optimization System

Continuously analyzes agent performance, workflow efficiency, and system
optimization to enable autonomous self-improvement and learning.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
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
import pickle

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
    """Individual performance metric with historical data"""
    id: str
    metric_type: MetricType
    entity_id: str  # agent_id, workflow_id, or 'system'
    entity_type: str  # 'agent', 'workflow', 'system'
    
    # Current values
    current_value: float
    target_value: float
    threshold_warning: float
    threshold_critical: float
    
    # Historical data
    historical_values: List[Tuple[datetime, float]] = field(default_factory=list)
    
    # Analysis results
    trend_direction: TrendDirection = TrendDirection.STABLE
    trend_strength: float = 0.0  # -1.0 to 1.0
    confidence_interval: Tuple[float, float] = (0.0, 0.0)
    
    # Improvement tracking
    baseline_value: float = 0.0
    improvement_percentage: float = 0.0
    last_improvement_date: Optional[datetime] = None
    
    # Context
    tags: Set[str] = field(default_factory=set)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def add_data_point(self, value: float, timestamp: datetime = None):
        """Add new data point and update analysis"""
        timestamp = timestamp or datetime.now(timezone.utc)
        
        self.historical_values.append((timestamp, value))
        self.current_value = value
        self.updated_at = timestamp
        
        # Keep only last 1000 data points
        if len(self.historical_values) > 1000:
            self.historical_values = self.historical_values[-1000:]
        
        # Update analysis
        self._analyze_trend()
    
    def _analyze_trend(self):
        """Analyze trend from historical data"""
        if len(self.historical_values) < 5:
            return
        
        # Get recent values (last 30 data points or 7 days)
        recent_cutoff = datetime.now(timezone.utc) - timedelta(days=7)
        recent_values = [
            (ts, val) for ts, val in self.historical_values[-30:]
            if ts > recent_cutoff
        ]
        
        if len(recent_values) < 3:
            return
        
        # Calculate trend using linear regression
        timestamps = [ts.timestamp() for ts, val in recent_values]
        values = [val for ts, val in recent_values]
        
        try:
            slope, intercept, r_value, p_value, std_err = stats.linregress(timestamps, values)
            
            # Determine trend direction and strength
            self.trend_strength = r_value  # Correlation coefficient
            
            if abs(slope) < 0.001:  # Nearly flat
                self.trend_direction = TrendDirection.STABLE
            elif slope > 0:
                if self.current_value >= self.threshold_warning:
                    self.trend_direction = TrendDirection.IMPROVING
                else:
                    self.trend_direction = TrendDirection.DECLINING if self.current_value < self.threshold_critical else TrendDirection.STABLE
            else:  # slope < 0
                if self.current_value <= self.threshold_critical:
                    self.trend_direction = TrendDirection.CRITICAL
                elif self.current_value <= self.threshold_warning:
                    self.trend_direction = TrendDirection.DECLINING
                else:
                    self.trend_direction = TrendDirection.STABLE
            
            # Calculate confidence interval
            if len(values) > 2:
                std_dev = statistics.stdev(values)
                self.confidence_interval = (
                    self.current_value - 1.96 * std_dev,
                    self.current_value + 1.96 * std_dev
                )
            
        except Exception as e:
            logger.warning(f"Error analyzing trend for metric {self.id}: {e}")
    
    def get_health_status(self) -> str:
        """Get current health status based on thresholds"""
        if self.current_value <= self.threshold_critical:
            return "critical"
        elif self.current_value <= self.threshold_warning:
            return "warning"
        elif self.current_value >= self.target_value:
            return "excellent"
        else:
            return "good"
    
    def calculate_improvement_since_baseline(self) -> float:
        """Calculate improvement percentage since baseline"""
        if self.baseline_value == 0:
            return 0.0
        
        improvement = ((self.current_value - self.baseline_value) / self.baseline_value) * 100
        self.improvement_percentage = improvement
        return improvement

@dataclass
class OptimizationRecommendation:
    """AI-generated recommendation for system optimization"""
    id: str
    recommendation_type: str
    priority: str  # 'low', 'medium', 'high', 'critical'
    
    # Recommendation details
    title: str
    description: str
    expected_impact: str
    implementation_effort: str  # 'low', 'medium', 'high'
    
    # Affected entities
    affected_agents: List[str] = field(default_factory=list)
    affected_workflows: List[str] = field(default_factory=list)
    affected_metrics: List[str] = field(default_factory=list)
    
    # Implementation details
    action_steps: List[str] = field(default_factory=list)
    configuration_changes: Dict[str, Any] = field(default_factory=dict)
    
    # Validation and tracking
    confidence_score: float = 0.0
    expected_improvement: Dict[str, float] = field(default_factory=dict)
    implementation_status: str = "pending"  # pending, implementing, completed, failed
    
    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str = "performance_analyzer"
    category: str = "performance"
    tags: Set[str] = field(default_factory=set)

@dataclass
class LearningInsight:
    """Insight learned from performance analysis"""
    id: str
    insight_type: str
    category: str
    
    # Insight content
    title: str
    description: str
    evidence: List[str] = field(default_factory=list)
    
    # Applicability
    applies_to_agents: List[str] = field(default_factory=list)
    applies_to_workflows: List[str] = field(default_factory=list)
    applies_globally: bool = False
    
    # Impact assessment
    impact_score: float = 0.0  # 0.0 to 1.0
    confidence_level: float = 0.0  # 0.0 to 1.0
    
    # Implementation
    actionable: bool = True
    action_recommendations: List[str] = field(default_factory=list)
    
    # Learning metadata
    discovered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    validation_count: int = 0
    applied_count: int = 0
    success_rate: float = 0.0

class PerformanceAnalyzer:
    """AI-powered performance analysis and optimization system"""
    
    def __init__(self, db_path: str = "data/performance_analytics.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Performance tracking
        self.metrics: Dict[str, PerformanceMetric] = {}
        self.recommendations: Dict[str, OptimizationRecommendation] = {}
        self.learning_insights: Dict[str, LearningInsight] = {}
        
        # Analysis configuration
        self.analysis_interval_minutes = 30
        self.learning_window_days = 30
        self.min_data_points_for_analysis = 10
        
        # Background processing
        self.running = False
        self.analysis_tasks: List[asyncio.Task] = []
        
        # Machine learning models (simplified)
        self.performance_models: Dict[str, Any] = {}
        self.pattern_cache: Dict[str, Any] = {}
        
        # Performance baselines
        self.baseline_metrics: Dict[str, float] = {
            MetricType.TASK_SUCCESS_RATE.value: 0.90,
            MetricType.QUALITY_SCORE.value: 0.85,
            MetricType.COST_EFFICIENCY.value: 0.80,
            MetricType.WORKFLOW_SUCCESS_RATE.value: 0.92,
            MetricType.USER_SATISFACTION.value: 0.88
        }
        
        # Initialize database
        self._init_database()
        
        logger.info(f"Performance Analyzer initialized with database: {self.db_path}")
    
    def _init_database(self):
        """Initialize performance analytics database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id TEXT PRIMARY KEY,
                    metric_type TEXT NOT NULL,
                    entity_id TEXT NOT NULL,
                    entity_type TEXT NOT NULL,
                    current_value REAL NOT NULL,
                    target_value REAL NOT NULL,
                    threshold_warning REAL NOT NULL,
                    threshold_critical REAL NOT NULL,
                    trend_direction TEXT NOT NULL,
                    trend_strength REAL NOT NULL,
                    baseline_value REAL DEFAULT 0.0,
                    improvement_percentage REAL DEFAULT 0.0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    tags TEXT  -- JSON set
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS metric_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    value REAL NOT NULL,
                    context TEXT,  -- JSON
                    FOREIGN KEY (metric_id) REFERENCES performance_metrics (id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS optimization_recommendations (
                    id TEXT PRIMARY KEY,
                    recommendation_type TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    expected_impact TEXT NOT NULL,
                    implementation_effort TEXT NOT NULL,
                    affected_agents TEXT,  -- JSON list
                    affected_workflows TEXT,  -- JSON list
                    action_steps TEXT,  -- JSON list
                    configuration_changes TEXT,  -- JSON
                    confidence_score REAL NOT NULL,
                    implementation_status TEXT DEFAULT 'pending',
                    created_at TEXT NOT NULL,
                    category TEXT NOT NULL,
                    tags TEXT  -- JSON set
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS learning_insights (
                    id TEXT PRIMARY KEY,
                    insight_type TEXT NOT NULL,
                    category TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    evidence TEXT,  -- JSON list
                    applies_to_agents TEXT,  -- JSON list
                    applies_to_workflows TEXT,  -- JSON list
                    applies_globally BOOLEAN DEFAULT 0,
                    impact_score REAL NOT NULL,
                    confidence_level REAL NOT NULL,
                    actionable BOOLEAN DEFAULT 1,
                    action_recommendations TEXT,  -- JSON list
                    discovered_at TEXT NOT NULL,
                    validation_count INTEGER DEFAULT 0,
                    applied_count INTEGER DEFAULT 0,
                    success_rate REAL DEFAULT 0.0
                )
            """)
            
            conn.commit()
    
    async def start_performance_analysis(self):
        """Start background performance analysis"""
        if self.running:
            return
        
        self.running = True
        
        # Start analysis tasks
        self.analysis_tasks = [
            asyncio.create_task(self._performance_monitoring_loop()),
            asyncio.create_task(self._optimization_analysis_loop()),
            asyncio.create_task(self._learning_discovery_loop())
        ]
        
        logger.info("Performance analysis started")
    
    async def stop_performance_analysis(self):
        """Stop background performance analysis"""
        self.running = False
        
        # Cancel analysis tasks
        for task in self.analysis_tasks:
            task.cancel()
        
        if self.analysis_tasks:
            await asyncio.gather(*self.analysis_tasks, return_exceptions=True)
        
        self.analysis_tasks.clear()
        
        logger.info("Performance analysis stopped")
    
    async def record_agent_performance(self,
                                     agent_id: str,
                                     task_id: str,
                                     success: bool,
                                     completion_time_seconds: float,
                                     quality_score: float,
                                     cost_usd: float,
                                     context: Dict[str, Any] = None):
        """Record individual agent performance data"""
        
        timestamp = datetime.now(timezone.utc)
        context = context or {}
        
        # Update success rate metric
        success_metric_id = f"agent_{agent_id}_success_rate"
        if success_metric_id not in self.metrics:
            self.metrics[success_metric_id] = PerformanceMetric(
                id=success_metric_id,
                metric_type=MetricType.TASK_SUCCESS_RATE,
                entity_id=agent_id,
                entity_type="agent",
                current_value=0.0,
                target_value=0.95,
                threshold_warning=0.85,
                threshold_critical=0.75,
                baseline_value=self.baseline_metrics.get(MetricType.TASK_SUCCESS_RATE.value, 0.90)
            )
        
        # Update success rate (moving average)
        current_metric = self.metrics[success_metric_id]
        success_value = 1.0 if success else 0.0
        
        # Calculate moving average success rate
        recent_successes = [val for ts, val in current_metric.historical_values[-20:]]  # Last 20 tasks
        recent_successes.append(success_value)
        new_success_rate = sum(recent_successes) / len(recent_successes)
        
        current_metric.add_data_point(new_success_rate, timestamp)
        
        # Update completion time metric
        time_metric_id = f"agent_{agent_id}_completion_time"
        if time_metric_id not in self.metrics:
            self.metrics[time_metric_id] = PerformanceMetric(
                id=time_metric_id,
                metric_type=MetricType.TASK_COMPLETION_TIME,
                entity_id=agent_id,
                entity_type="agent",
                current_value=completion_time_seconds,
                target_value=3600.0,  # 1 hour target
                threshold_warning=7200.0,  # 2 hours warning
                threshold_critical=14400.0,  # 4 hours critical
                baseline_value=3600.0
            )
        
        self.metrics[time_metric_id].add_data_point(completion_time_seconds, timestamp)
        
        # Update quality score metric
        quality_metric_id = f"agent_{agent_id}_quality"
        if quality_metric_id not in self.metrics:
            self.metrics[quality_metric_id] = PerformanceMetric(
                id=quality_metric_id,
                metric_type=MetricType.QUALITY_SCORE,
                entity_id=agent_id,
                entity_type="agent",
                current_value=quality_score,
                target_value=0.95,
                threshold_warning=0.80,
                threshold_critical=0.70,
                baseline_value=self.baseline_metrics.get(MetricType.QUALITY_SCORE.value, 0.85)
            )
        
        self.metrics[quality_metric_id].add_data_point(quality_score, timestamp)
        
        # Update cost efficiency metric
        cost_metric_id = f"agent_{agent_id}_cost_efficiency"
        if cost_metric_id not in self.metrics:
            self.metrics[cost_metric_id] = PerformanceMetric(
                id=cost_metric_id,
                metric_type=MetricType.COST_EFFICIENCY,
                entity_id=agent_id,
                entity_type="agent",
                current_value=0.0,
                target_value=0.90,
                threshold_warning=0.70,
                threshold_critical=0.50,
                baseline_value=self.baseline_metrics.get(MetricType.COST_EFFICIENCY.value, 0.80)
            )
        
        # Calculate cost efficiency (quality per dollar)
        cost_efficiency = quality_score / max(cost_usd, 0.001)  # Prevent division by zero
        self.metrics[cost_metric_id].add_data_point(cost_efficiency, timestamp)
        
        # Store historical data
        await self._persist_metric_history(success_metric_id, success_value, timestamp, context)
        await self._persist_metric_history(time_metric_id, completion_time_seconds, timestamp, context)
        await self._persist_metric_history(quality_metric_id, quality_score, timestamp, context)
        await self._persist_metric_history(cost_metric_id, cost_efficiency, timestamp, context)
        
        logger.debug(f"Recorded agent performance: {agent_id} - Success: {success}, Quality: {quality_score:.2f}")
    
    async def record_workflow_performance(self,
                                        workflow_id: str,
                                        success: bool,
                                        duration_seconds: float,
                                        agent_coordination_score: float,
                                        resource_utilization: float,
                                        context: Dict[str, Any] = None):
        """Record workflow-level performance metrics"""
        
        timestamp = datetime.now(timezone.utc)
        context = context or {}
        
        # Workflow success rate
        success_metric_id = f"workflow_{workflow_id}_success_rate"
        if success_metric_id not in self.metrics:
            self.metrics[success_metric_id] = PerformanceMetric(
                id=success_metric_id,
                metric_type=MetricType.WORKFLOW_SUCCESS_RATE,
                entity_id=workflow_id,
                entity_type="workflow",
                current_value=0.0,
                target_value=0.95,
                threshold_warning=0.88,
                threshold_critical=0.80,
                baseline_value=self.baseline_metrics.get(MetricType.WORKFLOW_SUCCESS_RATE.value, 0.92)
            )
        
        success_value = 1.0 if success else 0.0
        current_metric = self.metrics[success_metric_id]
        
        # Calculate moving average
        recent_successes = [val for ts, val in current_metric.historical_values[-10:]]
        recent_successes.append(success_value)
        new_success_rate = sum(recent_successes) / len(recent_successes)
        
        current_metric.add_data_point(new_success_rate, timestamp)
        
        # Workflow duration
        duration_metric_id = f"workflow_{workflow_id}_duration"
        if duration_metric_id not in self.metrics:
            self.metrics[duration_metric_id] = PerformanceMetric(
                id=duration_metric_id,
                metric_type=MetricType.WORKFLOW_DURATION,
                entity_id=workflow_id,
                entity_type="workflow",
                current_value=duration_seconds,
                target_value=7200.0,  # 2 hours target
                threshold_warning=14400.0,  # 4 hours warning
                threshold_critical=28800.0,  # 8 hours critical
                baseline_value=7200.0
            )
        
        self.metrics[duration_metric_id].add_data_point(duration_seconds, timestamp)
        
        # Agent coordination score
        coordination_metric_id = f"workflow_{workflow_id}_coordination"
        if coordination_metric_id not in self.metrics:
            self.metrics[coordination_metric_id] = PerformanceMetric(
                id=coordination_metric_id,
                metric_type=MetricType.AGENT_COORDINATION,
                entity_id=workflow_id,
                entity_type="workflow",
                current_value=agent_coordination_score,
                target_value=0.90,
                threshold_warning=0.75,
                threshold_critical=0.60,
                baseline_value=0.80
            )
        
        self.metrics[coordination_metric_id].add_data_point(agent_coordination_score, timestamp)
        
        # Resource utilization
        resource_metric_id = f"workflow_{workflow_id}_resource_util"
        if resource_metric_id not in self.metrics:
            self.metrics[resource_metric_id] = PerformanceMetric(
                id=resource_metric_id,
                metric_type=MetricType.RESOURCE_UTILIZATION,
                entity_id=workflow_id,
                entity_type="workflow",
                current_value=resource_utilization,
                target_value=0.80,
                threshold_warning=0.90,
                threshold_critical=0.95,
                baseline_value=0.75
            )
        
        self.metrics[resource_metric_id].add_data_point(resource_utilization, timestamp)
        
        # Persist history
        await self._persist_metric_history(success_metric_id, success_value, timestamp, context)
        await self._persist_metric_history(duration_metric_id, duration_seconds, timestamp, context)
        await self._persist_metric_history(coordination_metric_id, agent_coordination_score, timestamp, context)
        await self._persist_metric_history(resource_metric_id, resource_utilization, timestamp, context)
        
        logger.debug(f"Recorded workflow performance: {workflow_id} - Success: {success}, Duration: {duration_seconds:.1f}s")
    
    async def _performance_monitoring_loop(self):
        """Background loop for continuous performance monitoring"""
        while self.running:
            try:
                # Analyze all metrics for anomalies and trends
                await self._analyze_performance_trends()
                
                # Generate alerts for critical issues
                await self._generate_performance_alerts()
                
                # Update performance models
                await self._update_performance_models()
                
                await asyncio.sleep(self.analysis_interval_minutes * 60)
                
            except Exception as e:
                logger.error(f"Error in performance monitoring loop: {e}")
                await asyncio.sleep(300)  # 5 minute recovery delay
    
    async def _analyze_performance_trends(self):
        """Analyze trends across all performance metrics"""
        
        critical_metrics = []
        declining_metrics = []
        improving_metrics = []
        
        for metric in self.metrics.values():
            if len(metric.historical_values) >= self.min_data_points_for_analysis:
                
                if metric.trend_direction == TrendDirection.CRITICAL:
                    critical_metrics.append(metric)
                elif metric.trend_direction == TrendDirection.DECLINING:
                    declining_metrics.append(metric)
                elif metric.trend_direction == TrendDirection.IMPROVING:
                    improving_metrics.append(metric)
        
        # Log trend summary
        if critical_metrics or declining_metrics:
            logger.warning(f"Performance trends - Critical: {len(critical_metrics)}, "
                         f"Declining: {len(declining_metrics)}, Improving: {len(improving_metrics)}")
        
        # Generate recommendations for declining performance
        for metric in critical_metrics + declining_metrics:
            await self._generate_performance_recommendation(metric)
    
    async def _generate_performance_recommendation(self, metric: PerformanceMetric):
        """Generate AI-powered recommendation for performance improvement"""
        
        recommendation_id = f"rec_{uuid.uuid4().hex[:8]}"
        
        # Analyze the specific performance issue
        issue_analysis = await self._analyze_performance_issue(metric)
        
        # Generate contextual recommendation
        recommendation = OptimizationRecommendation(
            id=recommendation_id,
            recommendation_type="performance_improvement",
            priority="high" if metric.trend_direction == TrendDirection.CRITICAL else "medium",
            title=issue_analysis['title'],
            description=issue_analysis['description'],
            expected_impact=issue_analysis['expected_impact'],
            implementation_effort=issue_analysis['effort'],
            affected_agents=issue_analysis.get('affected_agents', []),
            affected_workflows=issue_analysis.get('affected_workflows', []),
            affected_metrics=[metric.id],
            action_steps=issue_analysis['action_steps'],
            configuration_changes=issue_analysis.get('config_changes', {}),
            confidence_score=issue_analysis['confidence'],
            category="performance",
            tags={"auto_generated", "performance", metric.metric_type.value}
        )
        
        self.recommendations[recommendation_id] = recommendation
        await self._persist_recommendation(recommendation)
        
        logger.info(f"Generated performance recommendation: {recommendation.title} (ID: {recommendation_id})")
    
    async def _analyze_performance_issue(self, metric: PerformanceMetric) -> Dict[str, Any]:
        """Analyze specific performance issue and generate contextual recommendations"""
        
        if metric.metric_type == MetricType.TASK_SUCCESS_RATE:
            return await self._analyze_success_rate_issue(metric)
        elif metric.metric_type == MetricType.TASK_COMPLETION_TIME:
            return await self._analyze_completion_time_issue(metric)
        elif metric.metric_type == MetricType.QUALITY_SCORE:
            return await self._analyze_quality_score_issue(metric)
        elif metric.metric_type == MetricType.COST_EFFICIENCY:
            return await self._analyze_cost_efficiency_issue(metric)
        else:
            return await self._analyze_generic_performance_issue(metric)
    
    async def _analyze_success_rate_issue(self, metric: PerformanceMetric) -> Dict[str, Any]:
        """Analyze task success rate issues"""
        
        current_rate = metric.current_value * 100
        target_rate = metric.target_value * 100
        
        # Determine root cause analysis
        recent_failures = len([val for ts, val in metric.historical_values[-20:] if val < 0.5])
        
        if recent_failures > 5:
            # Multiple recent failures - likely systemic issue
            return {
                'title': f"High Task Failure Rate Detected - Agent {metric.entity_id}",
                'description': f"Agent success rate dropped to {current_rate:.1f}% (target: {target_rate:.1f}%). "
                              f"{recent_failures} failures in last 20 tasks suggests systemic issues.",
                'expected_impact': "15-25% improvement in success rate",
                'effort': "medium",
                'confidence': 0.85,
                'action_steps': [
                    "Analyze recent task failure patterns",
                    "Review agent tool configuration and availability",
                    "Check for resource constraints or timeout issues",
                    "Implement additional error handling and retry logic",
                    "Consider agent specialization refinement"
                ],
                'affected_agents': [metric.entity_id],
                'config_changes': {
                    'agent_timeout_seconds': 1800,  # Increase timeout
                    'retry_attempts': 3,
                    'enable_detailed_logging': True
                }
            }
        else:
            # Sporadic failures - likely resource or complexity issues
            return {
                'title': f"Task Success Rate Below Target - Agent {metric.entity_id}",
                'description': f"Agent success rate at {current_rate:.1f}% (target: {target_rate:.1f}%). "
                              "Sporadic failures suggest resource or complexity issues.",
                'expected_impact': "8-15% improvement in success rate",
                'effort': "low",
                'confidence': 0.75,
                'action_steps': [
                    "Monitor agent resource allocation during task execution",
                    "Review task complexity vs agent capabilities",
                    "Implement adaptive timeout based on task complexity",
                    "Add resource availability checks before task assignment"
                ],
                'affected_agents': [metric.entity_id]
            }
    
    async def _analyze_completion_time_issue(self, metric: PerformanceMetric) -> Dict[str, Any]:
        """Analyze task completion time issues"""
        
        current_time = metric.current_value
        target_time = metric.target_value
        
        if current_time > target_time * 2:
            # Significantly slow performance
            return {
                'title': f"Slow Task Completion - Agent {metric.entity_id}",
                'description': f"Average task completion time is {current_time/3600:.1f} hours "
                              f"(target: {target_time/3600:.1f} hours). Performance optimization needed.",
                'expected_impact': "30-50% reduction in completion time",
                'effort': "high",
                'confidence': 0.80,
                'action_steps': [
                    "Profile agent task execution to identify bottlenecks",
                    "Optimize tool selection for better performance",
                    "Implement parallel processing where possible",
                    "Review and optimize agent prompts and instructions",
                    "Consider task decomposition improvements"
                ],
                'affected_agents': [metric.entity_id],
                'config_changes': {
                    'enable_parallel_processing': True,
                    'optimize_tool_selection': True,
                    'task_timeout_multiplier': 1.5
                }
            }
        else:
            # Moderate performance issues
            return {
                'title': f"Task Completion Time Above Target - Agent {metric.entity_id}",
                'description': f"Tasks taking {current_time/3600:.1f} hours on average "
                              f"(target: {target_time/3600:.1f} hours). Minor optimization opportunity.",
                'expected_impact': "10-20% reduction in completion time",
                'effort': "medium",
                'confidence': 0.70,
                'action_steps': [
                    "Analyze task complexity distribution",
                    "Optimize agent tool usage patterns",
                    "Implement smarter task prioritization",
                    "Review agent resource allocation"
                ],
                'affected_agents': [metric.entity_id]
            }
    
    async def _generate_performance_alerts(self):
        """Generate alerts for critical performance issues"""
        
        alerts = []
        
        for metric in self.metrics.values():
            health_status = metric.get_health_status()
            
            if health_status == "critical":
                alerts.append({
                    'severity': 'critical',
                    'type': 'performance_degradation',
                    'entity_type': metric.entity_type,
                    'entity_id': metric.entity_id,
                    'metric_type': metric.metric_type.value,
                    'current_value': metric.current_value,
                    'threshold': metric.threshold_critical,
                    'trend': metric.trend_direction.value,
                    'message': f"{metric.entity_type.title()} {metric.entity_id} {metric.metric_type.value} "
                              f"is critically low: {metric.current_value:.3f} (threshold: {metric.threshold_critical:.3f})"
                })
        
        if alerts:
            # Send alerts through notification system
            from ..automation.notification_engine import get_notification_engine
            notification_engine = get_notification_engine()
            
            for alert in alerts:
                await notification_engine.send_notification(
                    notification_type="performance_alert",
                    data=alert,
                    channels=["admin_alerts"],
                    priority="high" if alert['severity'] == 'critical' else "normal"
                )
            
            logger.warning(f"Generated {len(alerts)} performance alerts")
    
    async def _optimization_analysis_loop(self):
        """Background loop for generating optimization recommendations"""
        while self.running:
            try:
                # Analyze system-wide optimization opportunities
                await self._analyze_cross_agent_patterns()
                await self._analyze_workflow_optimization_opportunities()
                await self._analyze_resource_allocation_efficiency()
                
                # Implement approved recommendations
                await self._implement_approved_optimizations()
                
                await asyncio.sleep(3600)  # Analyze every hour
                
            except Exception as e:
                logger.error(f"Error in optimization analysis loop: {e}")
                await asyncio.sleep(1800)  # 30 minute recovery delay
    
    async def _analyze_cross_agent_patterns(self):
        """Analyze patterns across multiple agents for optimization opportunities"""
        
        # Group metrics by agent
        agent_metrics = defaultdict(list)
        for metric in self.metrics.values():
            if metric.entity_type == "agent":
                agent_metrics[metric.entity_id].append(metric)
        
        # Analyze agent performance distribution
        if len(agent_metrics) >= 3:  # Need multiple agents for comparison
            
            # Find high-performing vs low-performing agents
            agent_scores = {}
            for agent_id, metrics in agent_metrics.items():
                # Calculate composite performance score
                success_metric = next((m for m in metrics if m.metric_type == MetricType.TASK_SUCCESS_RATE), None)
                quality_metric = next((m for m in metrics if m.metric_type == MetricType.QUALITY_SCORE), None)
                
                if success_metric and quality_metric:
                    composite_score = (success_metric.current_value * 0.6 + quality_metric.current_value * 0.4)
                    agent_scores[agent_id] = composite_score
            
            if len(agent_scores) >= 3:
                # Find top and bottom performers
                sorted_agents = sorted(agent_scores.items(), key=lambda x: x[1], reverse=True)
                top_performers = sorted_agents[:len(sorted_agents)//3]  # Top third
                bottom_performers = sorted_agents[-len(sorted_agents)//3:]  # Bottom third
                
                if top_performers and bottom_performers:
                    # Generate cross-agent learning recommendation
                    recommendation = await self._generate_cross_agent_learning_recommendation(
                        top_performers, bottom_performers
                    )
                    
                    if recommendation:
                        self.recommendations[recommendation.id] = recommendation
                        await self._persist_recommendation(recommendation)
    
    async def _generate_cross_agent_learning_recommendation(self,
                                                          top_performers: List[Tuple[str, float]],
                                                          bottom_performers: List[Tuple[str, float]]) -> OptimizationRecommendation:
        """Generate recommendation for cross-agent learning"""
        
        recommendation_id = f"rec_{uuid.uuid4().hex[:8]}"
        
        top_agent_ids = [agent_id for agent_id, score in top_performers]
        bottom_agent_ids = [agent_id for agent_id, score in bottom_performers]
        
        avg_top_score = statistics.mean([score for agent_id, score in top_performers])
        avg_bottom_score = statistics.mean([score for agent_id, score in bottom_performers])
        
        potential_improvement = ((avg_top_score - avg_bottom_score) / avg_bottom_score) * 100
        
        return OptimizationRecommendation(
            id=recommendation_id,
            recommendation_type="cross_agent_learning",
            priority="medium",
            title=f"Cross-Agent Performance Transfer Opportunity",
            description=f"Analysis shows {potential_improvement:.1f}% performance gap between "
                       f"top performers (avg: {avg_top_score:.2f}) and bottom performers (avg: {avg_bottom_score:.2f}). "
                       "Implementing best practices from top performers could significantly improve overall system performance.",
            expected_impact=f"Up to {potential_improvement:.1f}% improvement for {len(bottom_performers)} agents",
            implementation_effort="medium",
            affected_agents=bottom_agent_ids,
            action_steps=[
                f"Analyze task execution patterns of top-performing agents: {', '.join(top_agent_ids[:3])}",
                "Identify key differences in tool usage, prompting, and workflow approaches",
                f"Implement best practices for underperforming agents: {', '.join(bottom_agent_ids[:3])}",
                "Monitor performance improvement over 2-week period",
                "Standardize successful patterns across all similar agents"
            ],
            configuration_changes={
                'enable_cross_agent_learning': True,
                'performance_benchmarking': True,
                'best_practice_sharing': True
            },
            confidence_score=0.78,
            expected_improvement={
                MetricType.TASK_SUCCESS_RATE.value: potential_improvement / 200,  # Conservative estimate
                MetricType.QUALITY_SCORE.value: potential_improvement / 300
            },
            category="agent_optimization",
            tags={"cross_learning", "performance", "agent_improvement"}
        )
    
    async def _learning_discovery_loop(self):
        """Background loop for discovering learning insights"""
        while self.running:
            try:
                # Discover patterns and insights from historical data
                await self._discover_performance_patterns()
                await self._discover_optimization_insights()
                await self._validate_existing_insights()
                
                await asyncio.sleep(7200)  # Analyze every 2 hours
                
            except Exception as e:
                logger.error(f"Error in learning discovery loop: {e}")
                await asyncio.sleep(3600)  # 1 hour recovery delay
    
    async def _discover_performance_patterns(self):
        """Discover patterns in performance data using statistical analysis"""
        
        # Analyze time-of-day performance patterns
        await self._analyze_temporal_patterns()
        
        # Analyze task complexity vs performance patterns
        await self._analyze_complexity_performance_patterns()
        
        # Analyze tool usage vs success patterns
        await self._analyze_tool_success_patterns()
        
        # Analyze agent collaboration patterns
        await self._analyze_collaboration_patterns()
    
    async def _analyze_temporal_patterns(self):
        """Analyze performance patterns by time of day, week, etc."""
        
        # Collect performance data with timestamps
        temporal_data = []
        for metric in self.metrics.values():
            if metric.metric_type == MetricType.TASK_SUCCESS_RATE:
                for timestamp, value in metric.historical_values:
                    temporal_data.append({
                        'hour': timestamp.hour,
                        'day_of_week': timestamp.weekday(),
                        'value': value,
                        'agent_id': metric.entity_id
                    })
        
        if len(temporal_data) < 50:  # Need sufficient data
            return
        
        # Analyze hourly patterns
        df = pd.DataFrame(temporal_data)
        hourly_avg = df.groupby('hour')['value'].mean()
        
        # Find best and worst performing hours
        best_hour = hourly_avg.idxmax()
        worst_hour = hourly_avg.idxmin()
        performance_difference = hourly_avg[best_hour] - hourly_avg[worst_hour]
        
        if performance_difference > 0.1:  # 10% difference
            # Generate temporal pattern insight
            insight = LearningInsight(
                id=f"insight_{uuid.uuid4().hex[:8]}",
                insight_type="temporal_pattern",
                category="performance_optimization",
                title="Time-of-Day Performance Pattern Identified",
                description=f"Analysis shows {performance_difference*100:.1f}% better performance at "
                           f"{best_hour:02d}:00 vs {worst_hour:02d}:00. Scheduling critical tasks during "
                           "optimal hours could improve overall success rates.",
                evidence=[
                    f"Best performing hour: {best_hour:02d}:00 (avg success: {hourly_avg[best_hour]*100:.1f}%)",
                    f"Worst performing hour: {worst_hour:02d}:00 (avg success: {hourly_avg[worst_hour]*100:.1f}%)",
                    f"Performance difference: {performance_difference*100:.1f}%",
                    f"Analysis based on {len(temporal_data)} data points"
                ],
                applies_globally=True,
                impact_score=performance_difference,
                confidence_level=0.82,
                action_recommendations=[
                    f"Schedule high-priority tasks during optimal hours ({best_hour-1:02d}:00-{best_hour+2:02d}:00)",
                    f"Avoid scheduling critical tasks during low-performance hours ({worst_hour-1:02d}:00-{worst_hour+2:02d}:00)",
                    "Implement time-aware task scheduling in automation system",
                    "Monitor and validate performance improvements from temporal optimization"
                ]
            )
            
            self.learning_insights[insight.id] = insight
            await self._persist_learning_insight(insight)
            
            logger.info(f"Discovered temporal performance pattern: {performance_difference*100:.1f}% difference")
    
    async def get_performance_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive performance dashboard data"""
        
        # System-wide metrics
        total_metrics = len(self.metrics)
        critical_metrics = sum(1 for m in self.metrics.values() 
                              if m.get_health_status() == "critical")
        warning_metrics = sum(1 for m in self.metrics.values() 
                             if m.get_health_status() == "warning")
        
        # Agent performance summary
        agent_metrics = {}
        for metric in self.metrics.values():
            if metric.entity_type == "agent":
                agent_id = metric.entity_id
                if agent_id not in agent_metrics:
                    agent_metrics[agent_id] = {}
                
                agent_metrics[agent_id][metric.metric_type.value] = {
                    'current_value': metric.current_value,
                    'trend': metric.trend_direction.value,
                    'health': metric.get_health_status()
                }
        
        # Recent insights
        recent_insights = sorted(
            self.learning_insights.values(),
            key=lambda i: i.discovered_at,
            reverse=True
        )[:10]
        
        # Active recommendations
        active_recommendations = [r for r in self.recommendations.values() 
                                 if r.implementation_status == "pending"]
        active_recommendations.sort(key=lambda r: {
            'critical': 4, 'high': 3, 'medium': 2, 'low': 1
        }.get(r.priority, 0), reverse=True)
        
        return {
            'system_health': {
                'total_metrics': total_metrics,
                'critical_issues': critical_metrics,
                'warning_issues': warning_metrics,
                'health_score': 1.0 - (critical_metrics * 0.2 + warning_metrics * 0.1) / max(1, total_metrics)
            },
            'agent_performance': agent_metrics,
            'recent_insights': [{
                'id': insight.id,
                'title': insight.title,
                'category': insight.category,
                'impact_score': insight.impact_score,
                'confidence': insight.confidence_level,
                'discovered_at': insight.discovered_at.isoformat(),
                'actionable': insight.actionable
            } for insight in recent_insights],
            'active_recommendations': [{
                'id': rec.id,
                'title': rec.title,
                'priority': rec.priority,
                'expected_impact': rec.expected_impact,
                'implementation_effort': rec.implementation_effort,
                'confidence_score': rec.confidence_score,
                'affected_agents_count': len(rec.affected_agents)
            } for rec in active_recommendations[:10]],
            'learning_summary': {
                'total_insights': len(self.learning_insights),
                'actionable_insights': sum(1 for i in self.learning_insights.values() if i.actionable),
                'applied_optimizations': sum(1 for r in self.recommendations.values() 
                                           if r.implementation_status == "completed"),
                'avg_improvement_rate': self._calculate_average_improvement_rate()
            }
        }
    
    def _calculate_average_improvement_rate(self) -> float:
        """Calculate average improvement rate across all metrics"""
        improvements = []
        
        for metric in self.metrics.values():
            if metric.baseline_value > 0:
                improvement = metric.calculate_improvement_since_baseline()
                if abs(improvement) < 500:  # Filter out outliers
                    improvements.append(improvement)
        
        return statistics.mean(improvements) if improvements else 0.0
    
    async def _persist_metric_history(self, 
                                    metric_id: str, 
                                    value: float, 
                                    timestamp: datetime,
                                    context: Dict[str, Any]):
        """Persist metric data point to database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO metric_history (metric_id, timestamp, value, context)
                VALUES (?, ?, ?, ?)
            """, (
                metric_id, timestamp.isoformat(), value, json.dumps(context)
            ))
            conn.commit()
    
    async def _persist_recommendation(self, recommendation: OptimizationRecommendation):
        """Persist optimization recommendation to database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO optimization_recommendations (
                    id, recommendation_type, priority, title, description, expected_impact,
                    implementation_effort, affected_agents, affected_workflows, action_steps,
                    configuration_changes, confidence_score, implementation_status,
                    created_at, category, tags
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                recommendation.id, recommendation.recommendation_type, recommendation.priority,
                recommendation.title, recommendation.description, recommendation.expected_impact,
                recommendation.implementation_effort, json.dumps(recommendation.affected_agents),
                json.dumps(recommendation.affected_workflows), json.dumps(recommendation.action_steps),
                json.dumps(recommendation.configuration_changes), recommendation.confidence_score,
                recommendation.implementation_status, recommendation.created_at.isoformat(),
                recommendation.category, json.dumps(list(recommendation.tags))
            ))
            conn.commit()
    
    async def _persist_learning_insight(self, insight: LearningInsight):
        """Persist learning insight to database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO learning_insights (
                    id, insight_type, category, title, description, evidence,
                    applies_to_agents, applies_to_workflows, applies_globally,
                    impact_score, confidence_level, actionable, action_recommendations,
                    discovered_at, validation_count, applied_count, success_rate
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                insight.id, insight.insight_type, insight.category, insight.title,
                insight.description, json.dumps(insight.evidence),
                json.dumps(insight.applies_to_agents), json.dumps(insight.applies_to_workflows),
                insight.applies_globally, insight.impact_score, insight.confidence_level,
                insight.actionable, json.dumps(insight.action_recommendations),
                insight.discovered_at.isoformat(), insight.validation_count,
                insight.applied_count, insight.success_rate
            ))
            conn.commit()
    
    def get_performance_analytics(self) -> Dict[str, Any]:
        """Get comprehensive performance analytics"""
        
        # Calculate system-wide performance scores
        system_metrics = {
            'total_metrics_tracked': len(self.metrics),
            'metrics_above_target': sum(1 for m in self.metrics.values() 
                                       if m.current_value >= m.target_value),
            'metrics_critical': sum(1 for m in self.metrics.values() 
                                   if m.get_health_status() == "critical"),
            'avg_improvement_rate': self._calculate_average_improvement_rate(),
            'learning_insights_discovered': len(self.learning_insights),
            'optimization_recommendations': len(self.recommendations),
            'recommendations_implemented': sum(1 for r in self.recommendations.values() 
                                             if r.implementation_status == "completed")
        }
        
        return {
            'system_performance': system_metrics,
            'analysis_running': self.running,
            'last_analysis': datetime.now(timezone.utc).isoformat(),
            'performance_score': min(1.0, system_metrics['metrics_above_target'] / max(1, system_metrics['total_metrics_tracked']))
        }

# Global performance analyzer instance
_global_performance_analyzer: Optional[PerformanceAnalyzer] = None

def get_performance_analyzer() -> PerformanceAnalyzer:
    """Get global performance analyzer instance"""
    global _global_performance_analyzer
    if _global_performance_analyzer is None:
        _global_performance_analyzer = PerformanceAnalyzer()
    return _global_performance_analyzer
