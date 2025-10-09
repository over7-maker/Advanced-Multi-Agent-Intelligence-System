"""
Advanced ML-Powered Monitoring Service for AMAS Intelligence System
Provides predictive analytics, anomaly detection, and intelligent alerting
"""

import asyncio
import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

import joblib
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AnomalyType(Enum):
    """Types of anomalies detected"""

    PERFORMANCE_DEGRADATION = "performance_degradation"
    RESOURCE_SPIKE = "resource_spike"
    UNUSUAL_PATTERN = "unusual_pattern"
    SECURITY_THREAT = "security_threat"
    SYSTEM_FAILURE = "system_failure"


@dataclass
class MLModel:
    """ML model data structure"""

    name: str
    model: Any
    accuracy: float
    last_trained: datetime
    features: List[str]
    threshold: float = 0.5


@dataclass
class AnomalyDetection:
    """Anomaly detection result"""

    id: str
    type: AnomalyType
    severity: AlertSeverity
    confidence: float
    description: str
    timestamp: datetime
    features: Dict[str, float]
    recommendations: List[str] = field(default_factory=list)


@dataclass
class PredictiveAlert:
    """Predictive alert data structure"""

    id: str
    metric: str
    predicted_value: float
    actual_value: float
    confidence: float
    time_horizon: int  # minutes
    timestamp: datetime
    recommendations: List[str] = field(default_factory=list)


class AdvancedMonitoringService:
    """
    Advanced ML-Powered Monitoring Service for AMAS Intelligence System

    Provides:
    - Predictive analytics and forecasting
    - Anomaly detection using ML algorithms
    - Intelligent alerting and recommendations
    - Performance trend analysis
    - Resource optimization suggestions
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize the advanced monitoring service"""
        self.config = config
        self.ml_models = {}
        self.anomaly_detector = None
        self.predictive_models = {}
        self.scaler = StandardScaler()

        # Data storage
        self.metrics_history = []
        self.anomalies = []
        self.predictive_alerts = []

        # ML configuration
        self.ml_config = {
            "anomaly_detection": {"contamination": 0.1, "min_samples": 5, "eps": 0.5},
            "prediction": {
                "lookback_window": 60,  # minutes
                "prediction_horizon": 15,  # minutes
                "min_data_points": 30,
            },
            "training": {
                "retrain_interval": 3600,  # seconds
                "min_accuracy_threshold": 0.7,
            },
        }

        # Performance baselines
        self.baselines = {
            "response_time": 1.0,
            "cpu_usage": 50.0,
            "memory_usage": 60.0,
            "error_rate": 0.01,
            "throughput": 1000,
        }

        logger.info("Advanced monitoring service initialized")

    async def initialize(self):
        """Initialize the advanced monitoring service"""
        try:
            logger.info("Initializing advanced monitoring service...")

            # Initialize ML models
            await self._initialize_ml_models()

            # Start monitoring tasks
            await self._start_monitoring_tasks()

            # Initialize data collection
            await self._initialize_data_collection()

            logger.info("Advanced monitoring service initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize advanced monitoring service: {e}")
            raise

    async def _initialize_ml_models(self):
        """Initialize ML models for monitoring"""
        try:
            logger.info("Initializing ML models...")

            # Anomaly detection model
            self.anomaly_detector = IsolationForest(
                contamination=self.ml_config["anomaly_detection"]["contamination"],
                random_state=42,
            )

            # Predictive models for different metrics
            metrics = [
                "response_time",
                "cpu_usage",
                "memory_usage",
                "error_rate",
                "throughput",
            ]

            for metric in metrics:
                self.predictive_models[metric] = LinearRegression()

            # Initialize model storage
            self.ml_models = {
                "anomaly_detector": MLModel(
                    name="anomaly_detector",
                    model=self.anomaly_detector,
                    accuracy=0.0,
                    last_trained=datetime.utcnow(),
                    features=[
                        "response_time",
                        "cpu_usage",
                        "memory_usage",
                        "error_rate",
                    ],
                )
            }

            for metric, model in self.predictive_models.items():
                self.ml_models[f"predict_{metric}"] = MLModel(
                    name=f"predict_{metric}",
                    model=model,
                    accuracy=0.0,
                    last_trained=datetime.utcnow(),
                    features=[metric],
                )

            logger.info("ML models initialized")

        except Exception as e:
            logger.error(f"Failed to initialize ML models: {e}")
            raise

    async def _start_monitoring_tasks(self):
        """Start advanced monitoring tasks"""
        try:
            self.monitoring_tasks = [
                asyncio.create_task(self._collect_advanced_metrics()),
                asyncio.create_task(self._detect_anomalies()),
                asyncio.create_task(self._generate_predictions()),
                asyncio.create_task(self._train_models()),
                asyncio.create_task(self._analyze_trends()),
                asyncio.create_task(self._optimize_recommendations()),
            ]

            logger.info("Advanced monitoring tasks started")

        except Exception as e:
            logger.error(f"Failed to start monitoring tasks: {e}")
            raise

    async def _initialize_data_collection(self):
        """Initialize data collection for ML models"""
        try:
            # Initialize metrics history with sample data
            current_time = datetime.utcnow()

            for i in range(100):  # Generate 100 sample data points
                timestamp = current_time - timedelta(minutes=i)

                # Generate realistic metrics data
                metrics = {
                    "timestamp": timestamp,
                    "response_time": max(0.1, 1.0 + np.random.normal(0, 0.2)),
                    "cpu_usage": max(0, min(100, 50 + np.random.normal(0, 15))),
                    "memory_usage": max(0, min(100, 60 + np.random.normal(0, 10))),
                    "error_rate": max(0, min(1, 0.01 + np.random.normal(0, 0.005))),
                    "throughput": max(0, 1000 + np.random.normal(0, 100)),
                    "active_connections": max(0, 50 + int(np.random.normal(0, 10))),
                    "queue_size": max(0, 10 + int(np.random.normal(0, 5))),
                }

                self.metrics_history.append(metrics)

            # Sort by timestamp
            self.metrics_history.sort(key=lambda x: x["timestamp"])

            logger.info("Data collection initialized with sample data")

        except Exception as e:
            logger.error(f"Failed to initialize data collection: {e}")
            raise

    async def _collect_advanced_metrics(self):
        """Collect advanced metrics for ML analysis"""
        while True:
            try:
                # Collect real-time metrics
                current_metrics = await self._gather_current_metrics()

                # Add to history
                self.metrics_history.append(current_metrics)

                # Keep only last 24 hours of data
                cutoff_time = datetime.utcnow() - timedelta(hours=24)
                self.metrics_history = [
                    m for m in self.metrics_history if m["timestamp"] > cutoff_time
                ]

                # Update baselines
                await self._update_baselines()

                await asyncio.sleep(30)  # Collect every 30 seconds

            except Exception as e:
                logger.error(f"Advanced metrics collection error: {e}")
                await asyncio.sleep(60)

    async def _gather_current_metrics(self) -> Dict[str, Any]:
        """Gather current system metrics"""
        try:
            # Simulate gathering real metrics
            # In production, this would collect actual system metrics

            current_time = datetime.utcnow()

            # Generate realistic metrics with some variation
            base_response_time = 1.0
            base_cpu = 50.0
            base_memory = 60.0
            base_error_rate = 0.01
            base_throughput = 1000

            # Add some realistic patterns
            time_factor = np.sin(current_time.hour * np.pi / 12) * 0.1  # Daily pattern
            random_factor = np.random.normal(0, 0.05)

            metrics = {
                "timestamp": current_time,
                "response_time": max(
                    0.1, base_response_time * (1 + time_factor + random_factor)
                ),
                "cpu_usage": max(
                    0, min(100, base_cpu * (1 + time_factor + random_factor))
                ),
                "memory_usage": max(
                    0, min(100, base_memory * (1 + time_factor + random_factor))
                ),
                "error_rate": max(
                    0,
                    min(
                        1, base_error_rate * (1 + abs(time_factor) + abs(random_factor))
                    ),
                ),
                "throughput": max(
                    0, base_throughput * (1 + time_factor + random_factor)
                ),
                "active_connections": max(0, 50 + int(np.random.normal(0, 10))),
                "queue_size": max(0, 10 + int(np.random.normal(0, 5))),
                "cache_hit_rate": max(0, min(1, 0.95 + np.random.normal(0, 0.02))),
                "disk_io": max(0, 1000 + int(np.random.normal(0, 200))),
                "network_io": max(0, 5000 + int(np.random.normal(0, 1000))),
            }

            return metrics

        except Exception as e:
            logger.error(f"Failed to gather current metrics: {e}")
            return {
                "timestamp": datetime.utcnow(),
                "response_time": 1.0,
                "cpu_usage": 50.0,
                "memory_usage": 60.0,
                "error_rate": 0.01,
                "throughput": 1000,
                "active_connections": 50,
                "queue_size": 10,
                "cache_hit_rate": 0.95,
                "disk_io": 1000,
                "network_io": 5000,
            }

    async def _update_baselines(self):
        """Update performance baselines based on recent data"""
        try:
            if len(self.metrics_history) < 10:
                return

            # Calculate baselines from recent data (last hour)
            recent_data = [
                m
                for m in self.metrics_history
                if m["timestamp"] > datetime.utcnow() - timedelta(hours=1)
            ]

            if not recent_data:
                return

            # Update baselines with moving average
            for metric in [
                "response_time",
                "cpu_usage",
                "memory_usage",
                "error_rate",
                "throughput",
            ]:
                values = [m[metric] for m in recent_data]
                if values:
                    self.baselines[metric] = np.mean(values)

        except Exception as e:
            logger.error(f"Failed to update baselines: {e}")

    async def _detect_anomalies(self):
        """Detect anomalies using ML models"""
        while True:
            try:
                if len(self.metrics_history) < 30:
                    await asyncio.sleep(60)
                    continue

                # Prepare data for anomaly detection
                features = await self._prepare_anomaly_features()

                if features is None or len(features) < 10:
                    await asyncio.sleep(60)
                    continue

                # Detect anomalies
                anomaly_scores = self.anomaly_detector.decision_function(features)
                predictions = self.anomaly_detector.predict(features)

                # Process anomalies
                for i, (score, prediction) in enumerate(
                    zip(anomaly_scores, predictions)
                ):
                    if prediction == -1:  # Anomaly detected
                        await self._process_anomaly(features[i], score, i)

                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                logger.error(f"Anomaly detection error: {e}")
                await asyncio.sleep(60)

    async def _prepare_anomaly_features(self) -> Optional[np.ndarray]:
        """Prepare features for anomaly detection"""
        try:
            if len(self.metrics_history) < 10:
                return None

            # Get recent data
            recent_data = self.metrics_history[-30:]  # Last 30 data points

            # Extract features
            features = []
            for metric in recent_data:
                feature_vector = [
                    metric["response_time"],
                    metric["cpu_usage"],
                    metric["memory_usage"],
                    metric["error_rate"],
                ]
                features.append(feature_vector)

            return np.array(features)

        except Exception as e:
            logger.error(f"Failed to prepare anomaly features: {e}")
            return None

    async def _process_anomaly(self, features: np.ndarray, score: float, index: int):
        """Process detected anomaly"""
        try:
            # Determine anomaly type and severity
            anomaly_type = await self._classify_anomaly(features)
            severity = await self._determine_severity(score, features)

            # Create anomaly record
            anomaly = AnomalyDetection(
                id=f"anomaly_{int(time.time())}_{index}",
                type=anomaly_type,
                severity=severity,
                confidence=abs(score),
                description=await self._generate_anomaly_description(
                    anomaly_type, features
                ),
                timestamp=datetime.utcnow(),
                features={
                    "response_time": features[0],
                    "cpu_usage": features[1],
                    "memory_usage": features[2],
                    "error_rate": features[3],
                },
                recommendations=await self._generate_anomaly_recommendations(
                    anomaly_type, features
                ),
            )

            # Store anomaly
            self.anomalies.append(anomaly)

            # Trigger alert
            await self._trigger_anomaly_alert(anomaly)

            logger.warning(f"Anomaly detected: {anomaly.description}")

        except Exception as e:
            logger.error(f"Failed to process anomaly: {e}")

    async def _classify_anomaly(self, features: np.ndarray) -> AnomalyType:
        """Classify the type of anomaly"""
        try:
            response_time, cpu_usage, memory_usage, error_rate = features

            # Classification logic
            if response_time > self.baselines["response_time"] * 2:
                return AnomalyType.PERFORMANCE_DEGRADATION
            elif (
                cpu_usage > self.baselines["cpu_usage"] * 1.5
                or memory_usage > self.baselines["memory_usage"] * 1.5
            ):
                return AnomalyType.RESOURCE_SPIKE
            elif error_rate > self.baselines["error_rate"] * 5:
                return AnomalyType.SYSTEM_FAILURE
            else:
                return AnomalyType.UNUSUAL_PATTERN

        except Exception as e:
            logger.error(f"Failed to classify anomaly: {e}")
            return AnomalyType.UNUSUAL_PATTERN

    async def _determine_severity(
        self, score: float, features: np.ndarray
    ) -> AlertSeverity:
        """Determine anomaly severity"""
        try:
            # Severity based on score and feature values
            if score < -0.5:
                return AlertSeverity.CRITICAL
            elif score < -0.3:
                return AlertSeverity.HIGH
            elif score < -0.1:
                return AlertSeverity.MEDIUM
            else:
                return AlertSeverity.LOW

        except Exception as e:
            logger.error(f"Failed to determine severity: {e}")
            return AlertSeverity.MEDIUM

    async def _generate_anomaly_description(
        self, anomaly_type: AnomalyType, features: np.ndarray
    ) -> str:
        """Generate human-readable anomaly description"""
        try:
            response_time, cpu_usage, memory_usage, error_rate = features

            descriptions = {
                AnomalyType.PERFORMANCE_DEGRADATION: f"Performance degradation detected: response time {response_time:.2f}s (baseline: {self.baselines['response_time']:.2f}s)",
                AnomalyType.RESOURCE_SPIKE: f"Resource spike detected: CPU {cpu_usage:.1f}%, Memory {memory_usage:.1f}%",
                AnomalyType.SYSTEM_FAILURE: f"System failure indicators: error rate {error_rate:.3f} (baseline: {self.baselines['error_rate']:.3f})",
                AnomalyType.UNUSUAL_PATTERN: "Unusual system pattern detected in metrics",
            }

            return descriptions.get(anomaly_type, "Unknown anomaly detected")

        except Exception as e:
            logger.error(f"Failed to generate anomaly description: {e}")
            return "Anomaly detected in system metrics"

    async def _generate_anomaly_recommendations(
        self, anomaly_type: AnomalyType, features: np.ndarray
    ) -> List[str]:
        """Generate recommendations for anomaly"""
        try:
            recommendations = []

            if anomaly_type == AnomalyType.PERFORMANCE_DEGRADATION:
                recommendations.extend(
                    [
                        "Check for resource bottlenecks",
                        "Review recent deployments",
                        "Scale up resources if needed",
                        "Investigate slow queries or operations",
                    ]
                )
            elif anomaly_type == AnomalyType.RESOURCE_SPIKE:
                recommendations.extend(
                    [
                        "Monitor resource usage trends",
                        "Check for memory leaks",
                        "Consider load balancing",
                        "Review resource allocation",
                    ]
                )
            elif anomaly_type == AnomalyType.SYSTEM_FAILURE:
                recommendations.extend(
                    [
                        "Check system logs for errors",
                        "Verify service health",
                        "Review recent changes",
                        "Consider failover procedures",
                    ]
                )
            else:
                recommendations.extend(
                    [
                        "Monitor system closely",
                        "Review metrics trends",
                        "Check for external factors",
                    ]
                )

            return recommendations

        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            return ["Monitor system closely"]

    async def _trigger_anomaly_alert(self, anomaly: AnomalyDetection):
        """Trigger alert for anomaly"""
        try:
            # In production, this would integrate with alerting system
            logger.warning(
                f"ANOMALY ALERT [{anomaly.severity.value.upper()}] {anomaly.description}"
            )

            # Store in alert history
            # Could integrate with external alerting systems here

        except Exception as e:
            logger.error(f"Failed to trigger anomaly alert: {e}")

    async def _generate_predictions(self):
        """Generate predictive alerts"""
        while True:
            try:
                if (
                    len(self.metrics_history)
                    < self.ml_config["prediction"]["min_data_points"]
                ):
                    await asyncio.sleep(60)
                    continue

                # Generate predictions for each metric
                for metric in [
                    "response_time",
                    "cpu_usage",
                    "memory_usage",
                    "error_rate",
                    "throughput",
                ]:
                    await self._predict_metric(metric)

                await asyncio.sleep(300)  # Predict every 5 minutes

            except Exception as e:
                logger.error(f"Prediction generation error: {e}")
                await asyncio.sleep(60)

    async def _predict_metric(self, metric: str):
        """Predict future values for a metric"""
        try:
            # Get historical data
            lookback_window = self.ml_config["prediction"]["lookback_window"]
            cutoff_time = datetime.utcnow() - timedelta(minutes=lookback_window)

            historical_data = [
                m for m in self.metrics_history if m["timestamp"] > cutoff_time
            ]

            if len(historical_data) < 10:
                return

            # Prepare data for prediction
            values = [m[metric] for m in historical_data]
            X = np.array(values[:-1]).reshape(-1, 1)
            y = np.array(values[1:])

            # Train model
            model = self.predictive_models[metric]
            model.fit(X, y)

            # Make prediction
            last_value = values[-1]
            prediction = model.predict([[last_value]])[0]

            # Calculate confidence based on recent accuracy
            recent_actual = values[-5:] if len(values) >= 5 else values
            recent_predicted = [
                model.predict([[values[i - 1]]])[0]
                for i in range(1, len(recent_actual))
            ]

            if len(recent_predicted) > 0:
                mse = mean_squared_error(recent_actual[1:], recent_predicted)
                confidence = max(0, 1 - mse / np.var(recent_actual))
            else:
                confidence = 0.5

            # Check if prediction indicates potential issues
            baseline = self.baselines[metric]
            threshold_factor = 1.5  # 50% above baseline

            if prediction > baseline * threshold_factor:
                # Create predictive alert
                alert = PredictiveAlert(
                    id=f"predict_{metric}_{int(time.time())}",
                    metric=metric,
                    predicted_value=prediction,
                    actual_value=last_value,
                    confidence=confidence,
                    time_horizon=self.ml_config["prediction"]["prediction_horizon"],
                    timestamp=datetime.utcnow(),
                    recommendations=await self._generate_predictive_recommendations(
                        metric, prediction, baseline
                    ),
                )

                self.predictive_alerts.append(alert)
                await self._trigger_predictive_alert(alert)

        except Exception as e:
            logger.error(f"Failed to predict metric {metric}: {e}")

    async def _generate_predictive_recommendations(
        self, metric: str, prediction: float, baseline: float
    ) -> List[str]:
        """Generate recommendations based on predictions"""
        try:
            recommendations = []

            if metric == "response_time":
                recommendations.extend(
                    [
                        "Consider scaling up resources",
                        "Review database query performance",
                        "Check for network latency issues",
                        "Implement caching strategies",
                    ]
                )
            elif metric == "cpu_usage":
                recommendations.extend(
                    [
                        "Monitor CPU-intensive processes",
                        "Consider horizontal scaling",
                        "Review resource allocation",
                        "Check for infinite loops or inefficient code",
                    ]
                )
            elif metric == "memory_usage":
                recommendations.extend(
                    [
                        "Check for memory leaks",
                        "Review memory allocation patterns",
                        "Consider garbage collection tuning",
                        "Monitor memory-intensive operations",
                    ]
                )
            elif metric == "error_rate":
                recommendations.extend(
                    [
                        "Review error logs",
                        "Check service dependencies",
                        "Verify configuration settings",
                        "Implement better error handling",
                    ]
                )
            elif metric == "throughput":
                recommendations.extend(
                    [
                        "Optimize data processing",
                        "Review bottleneck operations",
                        "Consider parallel processing",
                        "Check I/O performance",
                    ]
                )

            return recommendations

        except Exception as e:
            logger.error(f"Failed to generate predictive recommendations: {e}")
            return ["Monitor system closely"]

    async def _trigger_predictive_alert(self, alert: PredictiveAlert):
        """Trigger predictive alert"""
        try:
            logger.warning(
                f"PREDICTIVE ALERT: {alert.metric} predicted to reach {alert.predicted_value:.2f} in {alert.time_horizon} minutes"
            )

        except Exception as e:
            logger.error(f"Failed to trigger predictive alert: {e}")

    async def _train_models(self):
        """Retrain ML models periodically"""
        while True:
            try:
                if len(self.metrics_history) < 50:
                    await asyncio.sleep(3600)
                    continue

                # Retrain anomaly detector
                await self._retrain_anomaly_detector()

                # Retrain predictive models
                for metric in self.predictive_models.keys():
                    await self._retrain_predictive_model(metric)

                await asyncio.sleep(self.ml_config["training"]["retrain_interval"])

            except Exception as e:
                logger.error(f"Model training error: {e}")
                await asyncio.sleep(3600)

    async def _retrain_anomaly_detector(self):
        """Retrain anomaly detection model"""
        try:
            # Prepare training data
            features = await self._prepare_anomaly_features()

            if features is None or len(features) < 20:
                return

            # Fit the model
            self.anomaly_detector.fit(features)

            # Update model info
            self.ml_models["anomaly_detector"].last_trained = datetime.utcnow()

            logger.info("Anomaly detector retrained")

        except Exception as e:
            logger.error(f"Failed to retrain anomaly detector: {e}")

    async def _retrain_predictive_model(self, metric: str):
        """Retrain predictive model for a metric"""
        try:
            # Get historical data
            lookback_window = self.ml_config["prediction"]["lookback_window"]
            cutoff_time = datetime.utcnow() - timedelta(minutes=lookback_window)

            historical_data = [
                m for m in self.metrics_history if m["timestamp"] > cutoff_time
            ]

            if len(historical_data) < 20:
                return

            # Prepare training data
            values = [m[metric] for m in historical_data]
            X = np.array(values[:-1]).reshape(-1, 1)
            y = np.array(values[1:])

            # Train model
            model = self.predictive_models[metric]
            model.fit(X, y)

            # Calculate accuracy
            predictions = model.predict(X)
            mse = mean_squared_error(y, predictions)
            accuracy = max(0, 1 - mse / np.var(y))

            # Update model info
            model_key = f"predict_{metric}"
            if model_key in self.ml_models:
                self.ml_models[model_key].accuracy = accuracy
                self.ml_models[model_key].last_trained = datetime.utcnow()

            logger.info(
                f"Predictive model for {metric} retrained (accuracy: {accuracy:.3f})"
            )

        except Exception as e:
            logger.error(f"Failed to retrain predictive model for {metric}: {e}")

    async def _analyze_trends(self):
        """Analyze performance trends"""
        while True:
            try:
                if len(self.metrics_history) < 20:
                    await asyncio.sleep(300)
                    continue

                # Analyze trends for each metric
                for metric in [
                    "response_time",
                    "cpu_usage",
                    "memory_usage",
                    "error_rate",
                    "throughput",
                ]:
                    await self._analyze_metric_trend(metric)

                await asyncio.sleep(300)  # Analyze every 5 minutes

            except Exception as e:
                logger.error(f"Trend analysis error: {e}")
                await asyncio.sleep(300)

    async def _analyze_metric_trend(self, metric: str):
        """Analyze trend for a specific metric"""
        try:
            # Get recent data
            recent_data = self.metrics_history[-20:]  # Last 20 data points
            values = [m[metric] for m in recent_data]

            if len(values) < 10:
                return

            # Calculate trend
            x = np.arange(len(values))
            slope, intercept = np.polyfit(x, values, 1)

            # Determine trend direction
            if slope > 0.01:
                trend = "increasing"
            elif slope < -0.01:
                trend = "decreasing"
            else:
                trend = "stable"

            # Log significant trends
            if abs(slope) > 0.05:  # Significant trend
                logger.info(
                    f"Trend detected for {metric}: {trend} (slope: {slope:.4f})"
                )

        except Exception as e:
            logger.error(f"Failed to analyze trend for {metric}: {e}")

    async def _optimize_recommendations(self):
        """Generate optimization recommendations"""
        while True:
            try:
                if len(self.metrics_history) < 50:
                    await asyncio.sleep(600)
                    continue

                # Generate optimization recommendations
                recommendations = await self._generate_optimization_recommendations()

                if recommendations:
                    logger.info(f"Optimization recommendations: {recommendations}")

                await asyncio.sleep(600)  # Generate every 10 minutes

            except Exception as e:
                logger.error(f"Optimization recommendations error: {e}")
                await asyncio.sleep(600)

    async def _generate_optimization_recommendations(self) -> List[str]:
        """Generate system optimization recommendations"""
        try:
            recommendations = []

            # Analyze recent performance
            recent_data = self.metrics_history[-20:]

            # Check response time trends
            response_times = [m["response_time"] for m in recent_data]
            avg_response_time = np.mean(response_times)

            if avg_response_time > self.baselines["response_time"] * 1.2:
                recommendations.append(
                    "Consider implementing response time optimizations"
                )

            # Check resource usage
            cpu_usage = [m["cpu_usage"] for m in recent_data]
            avg_cpu = np.mean(cpu_usage)

            if avg_cpu > self.baselines["cpu_usage"] * 1.3:
                recommendations.append(
                    "High CPU usage detected - consider scaling or optimization"
                )

            # Check error rates
            error_rates = [m["error_rate"] for m in recent_data]
            avg_error_rate = np.mean(error_rates)

            if avg_error_rate > self.baselines["error_rate"] * 2:
                recommendations.append(
                    "Elevated error rate - investigate and fix issues"
                )

            return recommendations

        except Exception as e:
            logger.error(f"Failed to generate optimization recommendations: {e}")
            return []

    async def get_monitoring_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive monitoring dashboard data"""
        try:
            # Get recent metrics
            recent_metrics = self.metrics_history[-50:] if self.metrics_history else []

            # Get recent anomalies
            recent_anomalies = [
                {
                    "id": a.id,
                    "type": a.type.value,
                    "severity": a.severity.value,
                    "description": a.description,
                    "timestamp": a.timestamp.isoformat(),
                    "confidence": a.confidence,
                }
                for a in self.anomalies[-10:]  # Last 10 anomalies
            ]

            # Get recent predictive alerts
            recent_predictions = [
                {
                    "id": p.id,
                    "metric": p.metric,
                    "predicted_value": p.predicted_value,
                    "confidence": p.confidence,
                    "time_horizon": p.time_horizon,
                    "timestamp": p.timestamp.isoformat(),
                }
                for p in self.predictive_alerts[-10:]  # Last 10 predictions
            ]

            # Calculate system health score
            health_score = await self._calculate_health_score()

            return {
                "timestamp": datetime.utcnow().isoformat(),
                "health_score": health_score,
                "baselines": self.baselines,
                "recent_metrics": recent_metrics,
                "anomalies": recent_anomalies,
                "predictions": recent_predictions,
                "ml_models": {
                    name: {
                        "accuracy": model.accuracy,
                        "last_trained": model.last_trained.isoformat(),
                        "features": model.features,
                    }
                    for name, model in self.ml_models.items()
                },
                "recommendations": await self._generate_optimization_recommendations(),
            }

        except Exception as e:
            logger.error(f"Failed to get monitoring dashboard data: {e}")
            return {"timestamp": datetime.utcnow().isoformat(), "error": str(e)}

    async def _calculate_health_score(self) -> float:
        """Calculate overall system health score"""
        try:
            if not self.metrics_history:
                return 0.5

            # Get recent metrics
            recent_data = (
                self.metrics_history[-10:]
                if len(self.metrics_history) >= 10
                else self.metrics_history
            )

            # Calculate health factors
            factors = []

            # Response time factor
            response_times = [m["response_time"] for m in recent_data]
            avg_response_time = np.mean(response_times)
            response_factor = max(
                0,
                1
                - (avg_response_time - self.baselines["response_time"])
                / self.baselines["response_time"],
            )
            factors.append(response_factor)

            # CPU usage factor
            cpu_usage = [m["cpu_usage"] for m in recent_data]
            avg_cpu = np.mean(cpu_usage)
            cpu_factor = max(0, 1 - (avg_cpu - self.baselines["cpu_usage"]) / 100)
            factors.append(cpu_factor)

            # Error rate factor
            error_rates = [m["error_rate"] for m in recent_data]
            avg_error_rate = np.mean(error_rates)
            error_factor = max(
                0, 1 - (avg_error_rate - self.baselines["error_rate"]) / 0.1
            )
            factors.append(error_factor)

            # Calculate overall health score
            health_score = np.mean(factors)
            return min(1.0, max(0.0, health_score))

        except Exception as e:
            logger.error(f"Failed to calculate health score: {e}")
            return 0.5

    async def get_anomaly_report(self, hours: int = 24) -> Dict[str, Any]:
        """Get anomaly report for specified time period"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)

            # Filter anomalies by time
            recent_anomalies = [a for a in self.anomalies if a.timestamp > cutoff_time]

            # Group by type and severity
            by_type = {}
            by_severity = {}

            for anomaly in recent_anomalies:
                # By type
                if anomaly.type not in by_type:
                    by_type[anomaly.type] = []
                by_type[anomaly.type].append(anomaly)

                # By severity
                if anomaly.severity not in by_severity:
                    by_severity[anomaly.severity] = []
                by_severity[anomaly.severity].append(anomaly)

            return {
                "time_period_hours": hours,
                "total_anomalies": len(recent_anomalies),
                "by_type": {
                    type_name.value: len(anomalies)
                    for type_name, anomalies in by_type.items()
                },
                "by_severity": {
                    severity.value: len(anomalies)
                    for severity, anomalies in by_severity.items()
                },
                "anomalies": [
                    {
                        "id": a.id,
                        "type": a.type.value,
                        "severity": a.severity.value,
                        "description": a.description,
                        "timestamp": a.timestamp.isoformat(),
                        "confidence": a.confidence,
                        "recommendations": a.recommendations,
                    }
                    for a in recent_anomalies
                ],
            }

        except Exception as e:
            logger.error(f"Failed to get anomaly report: {e}")
            return {"error": str(e)}

    async def shutdown(self):
        """Shutdown advanced monitoring service"""
        try:
            logger.info("Shutting down advanced monitoring service...")

            # Cancel monitoring tasks
            for task in self.monitoring_tasks:
                task.cancel()

            # Wait for tasks to complete
            await asyncio.gather(*self.monitoring_tasks, return_exceptions=True)

            # Save models
            await self._save_models()

            logger.info("Advanced monitoring service shutdown complete")

        except Exception as e:
            logger.error(f"Error during advanced monitoring service shutdown: {e}")

    async def _save_models(self):
        """Save trained models to disk"""
        try:
            models_dir = "/app/models"
            os.makedirs(models_dir, exist_ok=True)

            for name, model_info in self.ml_models.items():
                model_path = os.path.join(models_dir, f"{name}.joblib")
                joblib.dump(model_info.model, model_path)

            logger.info("Models saved to disk")

        except Exception as e:
            logger.error(f"Failed to save models: {e}")
