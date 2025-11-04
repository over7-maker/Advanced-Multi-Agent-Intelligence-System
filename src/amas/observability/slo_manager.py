"""
SLO Manager for AMAS Observability Framework

Implements Service Level Objective (SLO) monitoring with error budget tracking,
burn rate alerts, and performance regression detection.
"""

import logging
import os
import yaml
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field

from prometheus_client import Gauge, Counter, Histogram, start_http_server
import requests

logger = logging.getLogger(__name__)


@dataclass
class SLODefinition:
    """Service Level Objective definition"""
    name: str
    description: str
    metric_query: str
    threshold: float
    comparison: str  # ">=", "<=", "=="
    window_minutes: int
    error_budget_percent: float
    severity: str
    
    def __post_init__(self):
        """Validate SLO definition"""
        if self.comparison not in [">=", "<=", "==", ">", "<"]:
            raise ValueError(f"Invalid comparison operator: {self.comparison}")
        if not 0 < self.error_budget_percent <= 100:
            raise ValueError(f"Error budget must be between 0 and 100: {self.error_budget_percent}")


@dataclass
class SLOStatus:
    """Current status of an SLO"""
    slo_name: str
    current_value: float
    target_value: float
    compliance_percent: float
    error_budget_total: float
    error_budget_remaining: float
    error_budget_remaining_percent: float
    burn_rate: float
    status: str  # "compliant", "warning", "critical", "violated"
    last_evaluated: datetime
    violations_count: int = 0


class SLOManager:
    """
    Manages Service Level Objectives with error budget tracking.
    
    Features:
    - Periodic SLO evaluation against Prometheus metrics
    - Error budget calculation and tracking
    - Multi-window burn rate detection
    - Performance baseline establishment
    - Automatic alert generation
    """
    
    def __init__(self, 
                 prometheus_url: str = None,
                 slo_config_path: str = None,
                 evaluation_interval_seconds: int = 60):
        """
        Initialize SLO Manager
        
        Args:
            prometheus_url: URL to Prometheus query API (default: from env or http://localhost:9090)
            slo_config_path: Path to SLO definitions YAML (default: config/observability/slo_definitions.yaml)
            evaluation_interval_seconds: How often to evaluate SLOs
        """
        self.prometheus_url = prometheus_url or os.getenv(
            "PROMETHEUS_URL", 
            "http://localhost:9090"
        )
        
        if slo_config_path:
            self.slo_config_path = slo_config_path
        else:
            # Resolve relative to workspace root
            current_dir = os.path.dirname(os.path.abspath(__file__))
            workspace_root = os.path.abspath(os.path.join(current_dir, "..", "..", "..", ".."))
            self.slo_config_path = os.path.join(workspace_root, "config", "observability", "slo_definitions.yaml")
        
        self.evaluation_interval = evaluation_interval_seconds
        self.slo_definitions: Dict[str, SLODefinition] = {}
        self.slo_statuses: Dict[str, SLOStatus] = {}
        self.performance_baselines: Dict[str, float] = {}
        
        # Prometheus metrics for SLO tracking
        self._setup_prometheus_metrics()
        
        # Load SLO definitions
        self._load_slo_definitions()
        
        logger.info(f"SLO Manager initialized with {len(self.slo_definitions)} SLOs")
    
    def _setup_prometheus_metrics(self):
        """Setup Prometheus metrics for SLO tracking"""
        # SLO compliance status (0 = violated, 1 = compliant)
        self.slo_compliance_gauge = Gauge(
            "amas_slo_compliance",
            "SLO compliance status (1 = compliant, 0 = violated)",
            ["slo_name"]
        )
        
        # Error budget remaining percentage
        self.error_budget_gauge = Gauge(
            "amas_slo_error_budget_remaining_percent",
            "Remaining error budget as percentage",
            ["slo_name"]
        )
        
        # Error budget burn rate
        self.burn_rate_gauge = Gauge(
            "amas_slo_error_budget_burn_rate",
            "Error budget burn rate (fraction per hour)",
            ["slo_name"]
        )
        
        # SLO current value
        self.slo_value_gauge = Gauge(
            "amas_slo_current_value",
            "Current SLO metric value",
            ["slo_name"]
        )
        
        # SLO violations counter
        self.slo_violations_counter = Counter(
            "amas_slo_violations_total",
            "Total number of SLO violations",
            ["slo_name", "severity"]
        )
        
        # Error budget consumed counter
        self.error_budget_consumed_counter = Counter(
            "amas_slo_error_budget_consumed_total",
            "Total error budget consumed",
            ["slo_name"]
        )
    
    def _load_slo_definitions(self):
        """Load SLO definitions from YAML configuration"""
        try:
            # Ensure absolute path
            if not os.path.isabs(self.slo_config_path):
                current_dir = os.path.dirname(os.path.abspath(__file__))
                workspace_root = os.path.abspath(os.path.join(current_dir, "..", "..", "..", ".."))
                self.slo_config_path = os.path.join(workspace_root, self.slo_config_path.lstrip("./"))
            
            with open(self.slo_config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            slos = config.get('slos', [])
            
            for slo_config in slos:
                slo = SLODefinition(
                    name=slo_config['name'],
                    description=slo_config['description'],
                    metric_query=slo_config['metric_query'],
                    threshold=slo_config['threshold'],
                    comparison=slo_config['comparison'],
                    window_minutes=slo_config['window_minutes'],
                    error_budget_percent=slo_config['error_budget_percent'],
                    severity=slo_config.get('severity', 'medium')
                )
                self.slo_definitions[slo.name] = slo
                
                # Initialize status
                self.slo_statuses[slo.name] = SLOStatus(
                    slo_name=slo.name,
                    current_value=0.0,
                    target_value=slo.threshold,
                    compliance_percent=100.0,
                    error_budget_total=slo.error_budget_percent,
                    error_budget_remaining=slo.error_budget_percent,
                    error_budget_remaining_percent=100.0,
                    burn_rate=0.0,
                    status="compliant",
                    last_evaluated=datetime.now(timezone.utc),
                    violations_count=0
                )
            
            logger.info(f"Loaded {len(self.slo_definitions)} SLO definitions")
            
        except FileNotFoundError:
            logger.error(f"SLO configuration file not found: {self.slo_config_path}")
            raise
        except Exception as e:
            logger.error(f"Failed to load SLO definitions: {e}")
            raise
    
    def query_prometheus(self, query: str) -> Optional[float]:
        """
        Query Prometheus for a metric value
        
        Args:
            query: PromQL query string
            
        Returns:
            Metric value as float, or None if query fails
        """
        try:
            response = requests.get(
                f"{self.prometheus_url}/api/v1/query",
                params={"query": query},
                timeout=5
            )
            response.raise_for_status()
            
            data = response.json()
            
            if data['status'] == 'success' and data['data']['result']:
                # Extract the first result value
                result = data['data']['result'][0]
                value = float(result['value'][1])
                return value
            else:
                logger.warning(f"Prometheus query returned no results: {query}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to query Prometheus: {e}")
            return None
        except (KeyError, ValueError, IndexError) as e:
            logger.error(f"Failed to parse Prometheus response: {e}")
            return None
    
    def evaluate_slo(self, slo_name: str) -> Optional[SLOStatus]:
        """
        Evaluate a single SLO against current metrics
        
        Args:
            slo_name: Name of the SLO to evaluate
            
        Returns:
            Updated SLOStatus, or None if evaluation failed
        """
        if slo_name not in self.slo_definitions:
            logger.error(f"SLO not found: {slo_name}")
            return None
        
        slo_def = self.slo_definitions[slo_name]
        status = self.slo_statuses[slo_name]
        
        # Query current metric value
        current_value = self.query_prometheus(slo_def.metric_query)
        
        if current_value is None:
            logger.warning(f"Could not get metric value for SLO: {slo_name}")
            return status
        
        # Update current value
        status.current_value = current_value
        
        # Check compliance
        is_compliant = self._check_compliance(
            current_value, 
            slo_def.threshold, 
            slo_def.comparison
        )
        
        # Calculate compliance percentage
        if slo_def.comparison in [">=", ">"]:
            # Higher is better (e.g., availability)
            if current_value >= slo_def.threshold:
                status.compliance_percent = 100.0
            else:
                status.compliance_percent = (current_value / slo_def.threshold) * 100.0
        else:
            # Lower is better (e.g., latency)
            if current_value <= slo_def.threshold:
                status.compliance_percent = 100.0
            else:
                status.compliance_percent = (slo_def.threshold / current_value) * 100.0
        
        # Calculate error budget consumption
        if not is_compliant:
            # Calculate how much error budget was consumed
            violation_percent = 100.0 - status.compliance_percent
            budget_consumed = (violation_percent / 100.0) * (self.evaluation_interval / 60.0)  # per minute
            
            status.error_budget_remaining = max(0.0, status.error_budget_remaining - budget_consumed)
            status.violations_count += 1
            
            # Record violation metric
            self.slo_violations_counter.labels(
                slo_name=slo_name,
                severity=slo_def.severity
            ).inc()
            
            # Record error budget consumption
            self.error_budget_consumed_counter.labels(
                slo_name=slo_name
            ).inc(budget_consumed)
        else:
            # Gradually recover error budget (if not at 100%)
            if status.error_budget_remaining < slo_def.error_budget_percent:
                recovery_rate = (slo_def.error_budget_percent / (30 * 24 * 60))  # Recover over 30 days
                status.error_budget_remaining = min(
                    slo_def.error_budget_percent,
                    status.error_budget_remaining + recovery_rate * (self.evaluation_interval / 60.0)
                )
        
        # Calculate remaining budget percentage
        status.error_budget_remaining_percent = (
            status.error_budget_remaining / slo_def.error_budget_percent
        ) * 100.0
        
        # Calculate burn rate (fraction of budget consumed per hour)
        time_since_last = (datetime.now(timezone.utc) - status.last_evaluated).total_seconds() / 3600.0
        if time_since_last > 0:
            budget_consumed = slo_def.error_budget_percent - status.error_budget_remaining
            status.burn_rate = budget_consumed / time_since_last if time_since_last > 0 else 0.0
        
        # Determine status
        if status.error_budget_remaining_percent <= 5:
            status.status = "critical"
        elif status.error_budget_remaining_percent <= 15:
            status.status = "warning"
        elif not is_compliant:
            status.status = "violated"
        else:
            status.status = "compliant"
        
        status.last_evaluated = datetime.now(timezone.utc)
        
        # Update Prometheus metrics
        self.slo_compliance_gauge.labels(slo_name=slo_name).set(1.0 if is_compliant else 0.0)
        self.error_budget_gauge.labels(slo_name=slo_name).set(status.error_budget_remaining_percent)
        self.burn_rate_gauge.labels(slo_name=slo_name).set(status.burn_rate)
        self.slo_value_gauge.labels(slo_name=slo_name).set(current_value)
        
        return status
    
    def _check_compliance(self, value: float, threshold: float, comparison: str) -> bool:
        """Check if value meets SLO threshold"""
        if comparison == ">=":
            return value >= threshold
        elif comparison == "<=":
            return value <= threshold
        elif comparison == ">":
            return value > threshold
        elif comparison == "<":
            return value < threshold
        elif comparison == "==":
            return abs(value - threshold) < 0.001  # Float comparison with epsilon
        else:
            raise ValueError(f"Unknown comparison operator: {comparison}")
    
    def evaluate_all_slos(self) -> Dict[str, SLOStatus]:
        """Evaluate all SLOs"""
        results = {}
        for slo_name in self.slo_definitions:
            status = self.evaluate_slo(slo_name)
            if status:
                results[slo_name] = status
        return results
    
    def get_slo_status(self, slo_name: str) -> Optional[SLOStatus]:
        """Get current status of an SLO"""
        return self.slo_statuses.get(slo_name)
    
    def get_all_slo_statuses(self) -> Dict[str, SLOStatus]:
        """Get status of all SLOs"""
        return self.slo_statuses.copy()
    
    def get_violations(self, severity: Optional[str] = None) -> List[SLOStatus]:
        """Get SLOs that are currently violating or warning"""
        violations = []
        for status in self.slo_statuses.values():
            if status.status in ["violated", "warning", "critical"]:
                if severity is None or status.status == severity:
                    violations.append(status)
        return violations
    
    def check_burn_rate_alerts(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Check for burn rate alerts based on multi-window, multi-burn-rate strategy
        
        Args:
            config: Burn rate alert configuration from YAML
            
        Returns:
            List of active burn rate alerts
        """
        alerts = []
        
        burn_rate_configs = config.get('burn_rate_alerts', [])
        
        for alert_config in burn_rate_configs:
            # Check each SLO for burn rate violations
            for slo_name, status in self.slo_statuses.items():
                # Calculate burn rate for short and long windows
                short_window_minutes = self._parse_time_window(alert_config['short_window'])
                long_window_minutes = self._parse_time_window(alert_config['long_window'])
                
                # Query burn rate metrics
                short_burn_rate = self._calculate_burn_rate(slo_name, short_window_minutes)
                long_burn_rate = self._calculate_burn_rate(slo_name, long_window_minutes)
                
                threshold = alert_config['burn_rate_threshold']
                
                # Check if burn rate exceeds threshold
                if short_burn_rate and short_burn_rate > threshold:
                    alerts.append({
                        'alert_name': alert_config['name'],
                        'slo_name': slo_name,
                        'burn_rate': short_burn_rate,
                        'threshold': threshold,
                        'window': alert_config['short_window'],
                        'severity': alert_config['severity'],
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    })
                elif long_burn_rate and long_burn_rate > threshold:
                    alerts.append({
                        'alert_name': alert_config['name'],
                        'slo_name': slo_name,
                        'burn_rate': long_burn_rate,
                        'threshold': threshold,
                        'window': alert_config['long_window'],
                        'severity': alert_config['severity'],
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    })
        
        return alerts
    
    def _parse_time_window(self, window_str: str) -> int:
        """Parse time window string (e.g., '5m', '1h') to minutes"""
        if window_str.endswith('m'):
            return int(window_str[:-1])
        elif window_str.endswith('h'):
            return int(window_str[:-1]) * 60
        elif window_str.endswith('d'):
            return int(window_str[:-1]) * 24 * 60
        else:
            raise ValueError(f"Invalid time window format: {window_str}")
    
    def _calculate_burn_rate(self, slo_name: str, window_minutes: int) -> Optional[float]:
        """Calculate error budget burn rate for a time window"""
        # Query error budget consumption over the window
        query = f"increase(amas_slo_error_budget_consumed_total{{slo_name=\"{slo_name}\"}}[{window_minutes}m])"
        consumed = self.query_prometheus(query)
        
        if consumed is None:
            return None
        
        slo_def = self.slo_definitions.get(slo_name)
        if not slo_def:
            return None
        
        # Calculate burn rate as fraction of budget per hour
        budget_per_hour = slo_def.error_budget_percent / (30 * 24)  # Monthly budget / hours in month
        burn_rate = consumed / (budget_per_hour * (window_minutes / 60.0))
        
        return burn_rate
    
    def update_performance_baseline(self, operation: str, p95_duration: float):
        """Update performance baseline for an operation"""
        baseline_key = f"{operation}_p95_seconds"
        old_baseline = self.performance_baselines.get(baseline_key, 0.0)
        
        # Only update if significantly different (>20% change)
        if old_baseline == 0 or abs(p95_duration - old_baseline) / old_baseline > 0.2:
            self.performance_baselines[baseline_key] = p95_duration
            logger.info(f"Updated performance baseline for {operation}: {p95_duration:.3f}s")
    
    def detect_performance_regression(self, operation: str, current_duration: float) -> Optional[Dict[str, Any]]:
        """
        Detect if current performance represents a regression
        
        Args:
            operation: Operation name
            current_duration: Current duration in seconds
            
        Returns:
            Regression detection result or None
        """
        baseline_key = f"{operation}_p95_seconds"
        baseline = self.performance_baselines.get(baseline_key)
        
        if baseline is None:
            # Establish initial baseline
            self.update_performance_baseline(operation, current_duration)
            return None
        
        # Check for regression (>50% slower than baseline)
        if current_duration > baseline * 1.5:
            regression_percent = ((current_duration - baseline) / baseline) * 100.0
            severity = "high" if current_duration > baseline * 2.0 else "medium"
            
            return {
                "type": "latency_regression",
                "operation": operation,
                "current_duration": current_duration,
                "baseline_duration": baseline,
                "regression_percent": regression_percent,
                "severity": severity,
                "detected_at": datetime.now(timezone.utc).isoformat()
            }
        
        return None


# Global SLO Manager instance
_global_slo_manager: Optional[SLOManager] = None


def initialize_slo_manager(prometheus_url: str = None, 
                          slo_config_path: str = None) -> SLOManager:
    """Initialize global SLO Manager"""
    global _global_slo_manager
    _global_slo_manager = SLOManager(
        prometheus_url=prometheus_url,
        slo_config_path=slo_config_path
    )
    return _global_slo_manager


def get_slo_manager() -> SLOManager:
    """Get global SLO Manager instance"""
    global _global_slo_manager
    if _global_slo_manager is None:
        return initialize_slo_manager()
    return _global_slo_manager
