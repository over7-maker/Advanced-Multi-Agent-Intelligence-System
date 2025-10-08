#!/usr/bin/env python3
"""
Advanced Performance Monitoring System for AMAS
Real-time metrics, predictive alerts, and optimization recommendations
"""

import asyncio
import json
import logging
import time
from collections import deque
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import aioredis
import psutil

@dataclass
class SystemMetrics:
    timestamp: str
    cpu_percent: float
    memory_percent: float
    disk_usage: float
    network_io: Dict[str, int]
    active_agents: int
    task_queue_length: int
    response_times: Dict[str, float]
    error_count: int
    throughput_per_second: float

@dataclass
class AlertThreshold:
    metric_name: str
    warning_threshold: float
    critical_threshold: float
    duration_minutes: int

class AMASPerformanceMonitor:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_client = None
        self.metrics_history = deque(maxlen=1000)  # Keep last 1000 metrics
        self.alert_thresholds = self._setup_default_thresholds()
        self.active_alerts = {}
        self.logger = logging.getLogger(__name__)

        # Initialize Redis for real-time data sharing
        asyncio.create_task(self._init_redis(redis_url))

    def _setup_default_thresholds(self) -> List[AlertThreshold]:
        return [
            AlertThreshold("cpu_percent", 70.0, 90.0, 5),
            AlertThreshold("memory_percent", 80.0, 95.0, 3),
            AlertThreshold("response_time_avg", 3.0, 8.0, 2),
            AlertThreshold("error_rate", 0.05, 0.15, 1),
            AlertThreshold("task_queue_length", 50, 100, 5),
        ]

    async def _init_redis(self, redis_url: str):
        try:
            self.redis_client = await aioredis.from_url(redis_url)
            self.logger.info("✅ Redis connection established for metrics")
        except Exception as e:
            self.logger.warning(f"⚠️ Redis not available: {e}")

    async def collect_system_metrics(self) -> SystemMetrics:
        """Collect comprehensive system metrics"""

        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        network = psutil.net_io_counters()

        # AMAS-specific metrics (mock data for now)
        active_agents = await self._count_active_agents()
        task_queue_length = await self._get_task_queue_length()
        response_times = await self._get_response_times()
        error_count = await self._get_error_count()
        throughput = await self._calculate_throughput()

        metrics = SystemMetrics(
            timestamp=datetime.now().isoformat(),
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            disk_usage=disk.percent,
            network_io={
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
            },
            active_agents=active_agents,
            task_queue_length=task_queue_length,
            response_times=response_times,
            error_count=error_count,
            throughput_per_second=throughput,
        )

        # Store in history
        self.metrics_history.append(metrics)

        # Store in Redis for real-time access
        if self.redis_client:
            await self.redis_client.set(
                "amas:metrics:current",
                json.dumps(asdict(metrics)),
                ex=60,  # Expire in 60 seconds
            )

        return metrics

    async def _count_active_agents(self) -> int:
        """Count currently active agents"""
        # This would connect to your actual agent manager
        # For now, return a realistic simulation
        return 7  # All agents active

    async def _get_task_queue_length(self) -> int:
        """Get current task queue length"""
        # This would connect to your task queue system
        return 3  # Mock data

    async def _get_response_times(self) -> Dict[str, float]:
        """Get average response times by agent type"""
        return {
            "security_agent": 2.3,
            "code_analysis_agent": 1.8,
            "intelligence_agent": 3.1,
            "performance_agent": 1.2,
        }

    async def _get_error_count(self) -> int:
        """Get error count in last minute"""
        return 0  # No errors - system is stable!

    async def _calculate_throughput(self) -> float:
        """Calculate tasks completed per second"""
        return 2.5  # Mock throughput

    async def check_alerts(self, current_metrics: SystemMetrics):
        """Check for alert conditions and trigger notifications"""

        for threshold in self.alert_thresholds:
            metric_value = getattr(current_metrics, threshold.metric_name, None)

            if metric_value is None:
                continue

            alert_key = f"{threshold.metric_name}_{threshold.warning_threshold}"

            # Check warning threshold
            if metric_value >= threshold.warning_threshold:
                if alert_key not in self.active_alerts:
                    await self._trigger_alert(
                        "warning", threshold, metric_value, current_metrics
                    )
                    self.active_alerts[alert_key] = time.time()

            # Check critical threshold
            if metric_value >= threshold.critical_threshold:
                critical_key = f"{threshold.metric_name}_critical"
                if critical_key not in self.active_alerts:
                    await self._trigger_alert(
                        "critical", threshold, metric_value, current_metrics
                    )
                    self.active_alerts[critical_key] = time.time()

            # Clear alert if metric is back to normal
            if (
                metric_value < threshold.warning_threshold
                and alert_key in self.active_alerts
            ):
                await self._clear_alert(threshold, metric_value)
                del self.active_alerts[alert_key]

    async def _trigger_alert(
        self,
        severity: str,
        threshold: AlertThreshold,
        current_value: float,
        metrics: SystemMetrics,
    ):
        """Trigger alert notification"""

        alert_message = f"""
🚨 AMAS {severity.upper()} ALERT 🚨

Metric: {threshold.metric_name}
Current Value: {current_value}
Threshold: {threshold.warning_threshold if severity == 'warning' else threshold.critical_threshold}
Time: {metrics.timestamp}

System Status:
- CPU: {metrics.cpu_percent}%
- Memory: {metrics.memory_percent}%
- Active Agents: {metrics.active_agents}
- Task Queue: {metrics.task_queue_length}
        """

        self.logger.warning(alert_message)

        # Store alert in Redis
        if self.redis_client:
            alert_data = {
                "severity": severity,
                "metric": threshold.metric_name,
                "value": current_value,
                "threshold": threshold.warning_threshold,
                "timestamp": metrics.timestamp,
                "full_metrics": asdict(metrics),
            }

            await self.redis_client.lpush("amas:alerts", json.dumps(alert_data))
            await self.redis_client.ltrim("amas:alerts", 0, 99)  # Keep last 100 alerts

    async def _clear_alert(self, threshold: AlertThreshold, current_value: float):
        """Clear resolved alert"""
        self.logger.info(f"✅ Alert cleared: {threshold.metric_name} = {current_value}")

    async def get_performance_trends(self, hours: int = 24) -> Dict[str, Any]:
        """Analyze performance trends over time"""

        if len(self.metrics_history) < 10:
            return {"message": "Insufficient data for trend analysis"}

        recent_metrics = list(self.metrics_history)[
            -hours * 60 :
        ]  # Assuming 1 metric per minute

        # Calculate trends
        cpu_trend = self._calculate_trend([m.cpu_percent for m in recent_metrics])
        memory_trend = self._calculate_trend([m.memory_percent for m in recent_metrics])
        response_time_trend = self._calculate_avg_response_time_trend(recent_metrics)

        return {
            "period_hours": hours,
            "trends": {
                "cpu_usage": cpu_trend,
                "memory_usage": memory_trend,
                "response_time": response_time_trend,
            },
            "recommendations": await self._generate_recommendations(recent_metrics),
        }

    def _calculate_trend(self, values: List[float]) -> Dict[str, Any]:
        """Calculate trend direction and magnitude"""
        if len(values) < 2:
            return {"direction": "insufficient_data"}

        recent_avg = sum(values[-10:]) / min(10, len(values))
        older_avg = sum(values[:10]) / min(10, len(values))

        change_percent = ((recent_avg - older_avg) / older_avg) * 100

        if abs(change_percent) < 5:
            direction = "stable"
        elif change_percent > 0:
            direction = "increasing"
        else:
            direction = "decreasing"

        return {
            "direction": direction,
            "change_percent": round(change_percent, 2),
            "recent_average": round(recent_avg, 2),
            "baseline_average": round(older_avg, 2),
        }

    def _calculate_avg_response_time_trend(
        self, metrics: List[SystemMetrics]
    ) -> Dict[str, Any]:
        """Calculate average response time trends"""
        avg_response_times = []

        for metric in metrics:
            if metric.response_times:
                avg_rt = sum(metric.response_times.values()) / len(
                    metric.response_times
                )
                avg_response_times.append(avg_rt)

        return self._calculate_trend(avg_response_times)

    async def _generate_recommendations(
        self, metrics: List[SystemMetrics]
    ) -> List[str]:
        """Generate optimization recommendations based on metrics"""
        recommendations = []

        # Analyze recent metrics
        recent_cpu = [m.cpu_percent for m in metrics[-10:]]
        recent_memory = [m.memory_percent for m in metrics[-10:]]
        recent_queue = [m.task_queue_length for m in metrics[-10:]]

        avg_cpu = sum(recent_cpu) / len(recent_cpu)
        avg_memory = sum(recent_memory) / len(recent_memory)
        avg_queue = sum(recent_queue) / len(recent_queue)

        if avg_cpu > 80:
            recommendations.append(
                "🔧 High CPU usage detected. Consider scaling horizontally or optimizing agent algorithms."
            )

        if avg_memory > 85:
            recommendations.append(
                "💾 High memory usage. Consider implementing memory pooling or garbage collection optimization."
            )

        if avg_queue > 20:
            recommendations.append(
                "⚡ Task queue backlog detected. Consider adding more worker processes or improving task prioritization."
            )

        if avg_cpu < 30 and avg_memory < 50:
            recommendations.append(
                "✅ System resources are underutilized. Consider increasing concurrent task limits for better throughput."
            )

        return recommendations

    async def start_monitoring(self, interval_seconds: int = 60):
        """Start continuous performance monitoring"""
        self.logger.info(
            f"🔍 Starting AMAS performance monitoring (interval: {interval_seconds}s)"
        )

        while True:
            try:
                # Collect metrics
                metrics = await self.collect_system_metrics()

                # Check for alerts
                await self.check_alerts(metrics)

                # Log current status
                self.logger.info(
                    f"📊 CPU: {metrics.cpu_percent}% | Memory: {metrics.memory_percent}% | "
                    f"Agents: {metrics.active_agents} | Queue: {metrics.task_queue_length}"
                )

            except Exception as e:
                self.logger.error(f"❌ Error in monitoring loop: {e}")

            await asyncio.sleep(interval_seconds)

    async def get_real_time_dashboard_data(self) -> Dict[str, Any]:
        """Get formatted data for real-time dashboard"""

        if not self.metrics_history:
            return {"status": "initializing"}

        latest_metrics = self.metrics_history[-1]
        trends = await self.get_performance_trends(1)  # Last 1 hour

        # Get recent alerts
        recent_alerts = []
        if self.redis_client:
            alert_data = await self.redis_client.lrange("amas:alerts", 0, 4)
            recent_alerts = [json.loads(alert) for alert in alert_data]

        return {
            "current_metrics": asdict(latest_metrics),
            "trends": trends,
            "recent_alerts": recent_alerts,
            "system_health": self._calculate_system_health_score(latest_metrics),
            "uptime": self._get_system_uptime(),
            "agent_status": await self._get_detailed_agent_status(),
        }

    def _calculate_system_health_score(self, metrics: SystemMetrics) -> Dict[str, Any]:
        """Calculate overall system health score"""

        # Health factors (0-100 scale)
        cpu_health = max(0, 100 - metrics.cpu_percent)
        memory_health = max(0, 100 - metrics.memory_percent)
        queue_health = max(0, 100 - min(metrics.task_queue_length, 100))
        error_health = (
            100 if metrics.error_count == 0 else max(0, 100 - metrics.error_count * 10)
        )

        # Weighted average
        overall_health = (
            cpu_health * 0.3
            + memory_health * 0.3
            + queue_health * 0.2
            + error_health * 0.2
        )

        # Determine health status
        if overall_health >= 90:
            status = "excellent"
            color = "green"
        elif overall_health >= 75:
            status = "good"
            color = "blue"
        elif overall_health >= 60:
            status = "fair"
            color = "yellow"
        else:
            status = "poor"
            color = "red"

        return {
            "score": round(overall_health, 1),
            "status": status,
            "color": color,
            "components": {
                "cpu": round(cpu_health, 1),
                "memory": round(memory_health, 1),
                "queue": round(queue_health, 1),
                "errors": round(error_health, 1),
            },
        }

    def _get_system_uptime(self) -> str:
        """Get system uptime in human readable format"""
        uptime_seconds = time.time() - psutil.boot_time()
        uptime_delta = timedelta(seconds=int(uptime_seconds))
        return str(uptime_delta)

    async def _get_detailed_agent_status(self) -> List[Dict[str, Any]]:
        """Get detailed status for each agent"""

        # This would connect to your actual agent manager
        # For now, return realistic mock data
        agents = [
            {
                "name": "Security Expert",
                "status": "active",
                "tasks_completed": 142,
                "avg_response_time": 2.3,
            },
            {
                "name": "Code Analysis",
                "status": "active",
                "tasks_completed": 89,
                "avg_response_time": 1.8,
            },
            {
                "name": "Intelligence Gathering",
                "status": "active",
                "tasks_completed": 67,
                "avg_response_time": 3.1,
            },
            {
                "name": "Performance Monitor",
                "status": "active",
                "tasks_completed": 156,
                "avg_response_time": 1.2,
            },
            {
                "name": "Documentation",
                "status": "idle",
                "tasks_completed": 23,
                "avg_response_time": 2.7,
            },
            {
                "name": "Testing Coordinator",
                "status": "active",
                "tasks_completed": 45,
                "avg_response_time": 3.5,
            },
            {
                "name": "Integration Manager",
                "status": "active",
                "tasks_completed": 78,
                "avg_response_time": 2.1,
            },
        ]

        return agents

# CLI for testing the monitoring system
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AMAS Performance Monitor")
    parser.add_argument(
        "--interval", type=int, default=30, help="Monitoring interval in seconds"
    )
    parser.add_argument(
        "--redis-url", default="redis://localhost:6379", help="Redis connection URL"
    )

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    monitor = AMASPerformanceMonitor(args.redis_url)

    try:
        asyncio.run(monitor.start_monitoring(args.interval))
    except KeyboardInterrupt:
        print("👋 Performance monitoring stopped")
