#!/usr/bin/env python3
"""
Predictive Intelligence Engine for AMAS
Advanced prediction and forecasting for task outcomes and system optimization
"""

import asyncio
import pickle
import warnings
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import accuracy_score, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

warnings.filterwarnings("ignore")
import logging

@dataclass
class PredictionResult:
    prediction_type: str
    predicted_value: float
    confidence_level: float
    contributing_factors: List[Dict[str, Any]]
    recommendations: List[str]
    prediction_timestamp: str
    model_accuracy: float

@dataclass
class TaskOutcomePrediction:
    task_id: str
    success_probability: float
    estimated_duration: float
    quality_score_prediction: float
    risk_factors: List[str]
    optimization_suggestions: List[str]
    confidence: float

@dataclass
class SystemResourcePrediction:
    time_horizon_minutes: int
    predicted_cpu_usage: float
    predicted_memory_usage: float
    predicted_task_load: int
    bottleneck_predictions: List[str]
    scaling_recommendations: List[str]

class PredictiveIntelligenceEngine:
    """Advanced predictive analytics for AMAS system optimization"""

    def __init__(self, model_path: str = "data/models/"):
        self.model_path = model_path
        self.models: Dict[str, Any] = {}
        self.scalers: Dict[str, StandardScaler] = {}
        self.feature_importance: Dict[str, Dict[str, float]] = {}
        self.prediction_history: List[Dict[str, Any]] = []
        self.training_data: Dict[str, pd.DataFrame] = {}
        self.logger = logging.getLogger(__name__)

        # Initialize models
        self._initialize_models()
        self._load_trained_models()

    def _initialize_models(self):
        """Initialize machine learning models"""

        # Task success prediction model
        self.models["task_success"] = GradientBoostingClassifier(
            n_estimators=100, learning_rate=0.1, max_depth=6, random_state=42
        )

        # Task duration prediction model
        self.models["task_duration"] = RandomForestRegressor(
            n_estimators=100, max_depth=10, random_state=42
        )

        # Quality score prediction model
        self.models["quality_score"] = RandomForestRegressor(
            n_estimators=80, max_depth=8, random_state=42
        )

        # Resource usage prediction models
        self.models["cpu_usage"] = LinearRegression()
        self.models["memory_usage"] = LinearRegression()
        self.models["task_load"] = LinearRegression()

        # Initialize scalers
        for model_name in self.models.keys():
            self.scalers[model_name] = StandardScaler()

    def _load_trained_models(self):
        """Load pre-trained models if available"""
        try:
            import os

            os.makedirs(self.model_path, exist_ok=True)

            for model_name in self.models.keys():
                model_file = f"{self.model_path}{model_name}_model.pkl"
                scaler_file = f"{self.model_path}{model_name}_scaler.pkl"

                if os.path.exists(model_file) and os.path.exists(scaler_file):
                    self.models[model_name] = joblib.load(model_file)
                    self.scalers[model_name] = joblib.load(scaler_file)
                    self.logger.info(f"✅ Loaded trained model: {model_name}")

        except Exception as e:
            self.logger.warning(f"⚠️ Could not load trained models: {e}")

    def _save_trained_models(self):
        """Save trained models to disk"""
        try:
            import os

            os.makedirs(self.model_path, exist_ok=True)

            for model_name, model in self.models.items():
                model_file = f"{self.model_path}{model_name}_model.pkl"
                scaler_file = f"{self.model_path}{model_name}_scaler.pkl"

                joblib.dump(model, model_file)
                joblib.dump(self.scalers[model_name], scaler_file)

            self.logger.info("💾 Saved all trained models")

        except Exception as e:
            self.logger.error(f"❌ Error saving models: {e}")

    async def add_training_data(self, data_type: str, data: Dict[str, Any]):
        """Add training data for model improvement"""

        if data_type not in self.training_data:
            self.training_data[data_type] = pd.DataFrame()

        # Convert data to DataFrame row
        df_row = pd.DataFrame([data])
        self.training_data[data_type] = pd.concat(
            [self.training_data[data_type], df_row], ignore_index=True
        )

        # Retrain model if we have enough data
        if (
            len(self.training_data[data_type]) >= 50
            and len(self.training_data[data_type]) % 20 == 0
        ):
            await self._retrain_model(data_type)

    async def _retrain_model(self, data_type: str):
        """Retrain a specific model with accumulated data"""

        try:
            df = self.training_data[data_type]

            if data_type == "task_outcome":
                await self._retrain_task_prediction_models(df)
            elif data_type == "resource_usage":
                await self._retrain_resource_prediction_models(df)

            self.logger.info(f"🔄 Retrained {data_type} models with {len(df)} samples")

        except Exception as e:
            self.logger.error(f"❌ Error retraining {data_type} model: {e}")

    async def _retrain_task_prediction_models(self, df: pd.DataFrame):
        """Retrain task-related prediction models"""

        # Prepare features
        features = self._extract_task_features(df)

        # Task success model
        if "success_rate" in df.columns:
            y_success = (df["success_rate"] > 0.8).astype(int)
            if len(np.unique(y_success)) > 1:  # Need both success and failure examples
                X_scaled = self.scalers["task_success"].fit_transform(features)
                self.models["task_success"].fit(X_scaled, y_success)

        # Task duration model
        if "execution_time" in df.columns:
            y_duration = df["execution_time"].values
            X_scaled = self.scalers["task_duration"].fit_transform(features)
            self.models["task_duration"].fit(X_scaled, y_duration)

        # Quality score model
        if "quality_score" in df.columns:
            y_quality = df["quality_score"].values
            X_scaled = self.scalers["quality_score"].fit_transform(features)
            self.models["quality_score"].fit(X_scaled, y_quality)

        # Extract feature importance
        for model_name in ["task_success", "task_duration", "quality_score"]:
            if hasattr(self.models[model_name], "feature_importances_"):
                importance = self.models[model_name].feature_importances_
                self.feature_importance[model_name] = {
                    f"feature_{i}": float(importance[i]) for i in range(len(importance))
                }

    async def _retrain_resource_prediction_models(self, df: pd.DataFrame):
        """Retrain resource usage prediction models"""

        # Prepare time-series features
        features = self._extract_resource_features(df)

        # CPU usage model
        if "cpu_usage" in df.columns:
            y_cpu = df["cpu_usage"].values
            X_scaled = self.scalers["cpu_usage"].fit_transform(features)
            self.models["cpu_usage"].fit(X_scaled, y_cpu)

        # Memory usage model
        if "memory_usage" in df.columns:
            y_memory = df["memory_usage"].values
            X_scaled = self.scalers["memory_usage"].fit_transform(features)
            self.models["memory_usage"].fit(X_scaled, y_memory)

        # Task load model
        if "task_load" in df.columns:
            y_load = df["task_load"].values
            X_scaled = self.scalers["task_load"].fit_transform(features)
            self.models["task_load"].fit(X_scaled, y_load)

    def _extract_task_features(self, df: pd.DataFrame) -> np.ndarray:
        """Extract features for task prediction"""

        features = []

        for _, row in df.iterrows():
            feature_vector = []

            # Task type encoding
            task_types = [
                "security_scan",
                "code_analysis",
                "intelligence_gathering",
                "performance_analysis",
                "documentation",
                "testing",
            ]
            task_type = row.get("task_type", "unknown")
            for tt in task_types:
                feature_vector.append(1.0 if task_type == tt else 0.0)

            # Target characteristics
            target = str(row.get("target", ""))
            feature_vector.extend(
                [
                    1.0 if "http" in target.lower() else 0.0,  # URL
                    1.0 if "github" in target.lower() else 0.0,  # GitHub
                    1.0 if ".com" in target.lower() else 0.0,  # Domain
                    len(target),  # Target complexity
                ]
            )

            # Parameters
            params = row.get("parameters", {})
            feature_vector.extend(
                [
                    len(params),  # Parameter count
                    1.0 if "comprehensive" in str(params) else 0.0,
                    1.0 if "quick" in str(params) else 0.0,
                ]
            )

            # Agent characteristics
            agents = row.get("agents_used", [])
            feature_vector.extend(
                [
                    len(agents),  # Number of agents
                    1.0 if "security_expert" in agents else 0.0,
                    1.0 if "code_analysis" in agents else 0.0,
                    1.0 if "intelligence_gathering" in agents else 0.0,
                ]
            )

            # Temporal features
            timestamp = row.get("timestamp", datetime.now().isoformat())
            try:
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                feature_vector.extend(
                    [
                        dt.hour,  # Hour of day
                        dt.weekday(),  # Day of week
                    ]
                )
            except:
                feature_vector.extend([12, 1])  # Default values

            features.append(feature_vector)

        return np.array(features)

    def _extract_resource_features(self, df: pd.DataFrame) -> np.ndarray:
        """Extract features for resource prediction"""

        features = []

        for i, row in df.iterrows():
            feature_vector = []

            # Historical resource usage (if available)
            if i >= 5:  # Need at least 5 previous points
                recent_data = df.iloc[max(0, i - 5) : i]
                feature_vector.extend(
                    [
                        (
                            recent_data["cpu_usage"].mean()
                            if "cpu_usage" in recent_data
                            else 0
                        ),
                        (
                            recent_data["memory_usage"].mean()
                            if "memory_usage" in recent_data
                            else 0
                        ),
                        (
                            recent_data["task_load"].mean()
                            if "task_load" in recent_data
                            else 0
                        ),
                        (
                            recent_data["cpu_usage"].std()
                            if "cpu_usage" in recent_data
                            else 0
                        ),
                        (
                            recent_data["memory_usage"].std()
                            if "memory_usage" in recent_data
                            else 0
                        ),
                    ]
                )
            else:
                feature_vector.extend([0, 0, 0, 0, 0])  # Default for early samples

            # Current system state
            feature_vector.extend(
                [
                    row.get("active_agents", 0),
                    row.get("queue_length", 0),
                    row.get("error_count", 0),
                ]
            )

            # Temporal features
            timestamp = row.get("timestamp", datetime.now().isoformat())
            try:
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                feature_vector.extend(
                    [
                        dt.hour,
                        dt.weekday(),
                        dt.minute,
                    ]
                )
            except:
                feature_vector.extend([12, 1, 0])

            features.append(feature_vector)

        return np.array(features)

    async def predict_task_outcome(
        self,
        task_type: str,
        target: str,
        parameters: Dict[str, Any],
        agents_planned: List[str],
    ) -> TaskOutcomePrediction:
        """Predict the outcome of a task before execution"""

        # Prepare feature vector
        task_data = {
            "task_type": task_type,
            "target": target,
            "parameters": parameters,
            "agents_used": agents_planned,
            "timestamp": datetime.now().isoformat(),
        }

        features = self._extract_task_features(pd.DataFrame([task_data]))

        predictions = {}
        confidence = 0.5

        try:
            # Success probability prediction
            if "task_success" in self.models:
                X_scaled = self.scalers["task_success"].transform(features)
                success_proba = self.models["task_success"].predict_proba(X_scaled)
                predictions["success_probability"] = float(success_proba[0][1])
            else:
                predictions["success_probability"] = 0.8  # Default optimistic

            # Duration prediction
            if "task_duration" in self.models:
                X_scaled = self.scalers["task_duration"].transform(features)
                duration = self.models["task_duration"].predict(X_scaled)
                predictions["estimated_duration"] = float(duration[0])
            else:
                predictions["estimated_duration"] = 120.0  # Default 2 minutes

            # Quality prediction
            if "quality_score" in self.models:
                X_scaled = self.scalers["quality_score"].transform(features)
                quality = self.models["quality_score"].predict(X_scaled)
                predictions["quality_score_prediction"] = float(quality[0])
            else:
                predictions["quality_score_prediction"] = 0.8  # Default good quality

            confidence = 0.7  # Model-based confidence

        except Exception as e:
            self.logger.warning(f"⚠️ Prediction error: {e}, using defaults")
            predictions = {
                "success_probability": 0.8,
                "estimated_duration": 120.0,
                "quality_score_prediction": 0.8,
            }
            confidence = 0.3  # Lower confidence for defaults

        # Generate risk factors and suggestions
        risk_factors = self._identify_risk_factors(task_data, predictions)
        optimization_suggestions = self._generate_optimization_suggestions(
            task_data, predictions
        )

        return TaskOutcomePrediction(
            task_id=f"pred_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            success_probability=predictions["success_probability"],
            estimated_duration=predictions["estimated_duration"],
            quality_score_prediction=predictions["quality_score_prediction"],
            risk_factors=risk_factors,
            optimization_suggestions=optimization_suggestions,
            confidence=confidence,
        )

    def _identify_risk_factors(
        self, task_data: Dict[str, Any], predictions: Dict[str, float]
    ) -> List[str]:
        """Identify potential risk factors for the task"""

        risk_factors = []

        # Success probability risks
        if predictions["success_probability"] < 0.6:
            risk_factors.append("Low predicted success probability")

        # Duration risks
        if predictions["estimated_duration"] > 300:  # 5 minutes
            risk_factors.append("Task may take longer than expected")

        # Quality risks
        if predictions["quality_score_prediction"] < 0.7:
            risk_factors.append("Lower quality results predicted")

        # Agent combination risks
        agents = task_data.get("agents_used", [])
        if len(agents) > 4:
            risk_factors.append("Too many agents may cause coordination overhead")
        elif len(agents) < 2 and task_data["task_type"] in [
            "security_scan",
            "intelligence_gathering",
        ]:
            risk_factors.append("Complex task may benefit from additional agents")

        # Target complexity risks
        target = str(task_data.get("target", ""))
        if len(target) > 100:
            risk_factors.append("Complex target may increase failure risk")

        # Parameter risks
        params = task_data.get("parameters", {})
        if params.get("depth") == "comprehensive":
            risk_factors.append("Comprehensive analysis may take significantly longer")

        return risk_factors

    def _generate_optimization_suggestions(
        self, task_data: Dict[str, Any], predictions: Dict[str, float]
    ) -> List[str]:
        """Generate optimization suggestions for the task"""

        suggestions = []

        # Success rate optimizations
        if predictions["success_probability"] < 0.7:
            suggestions.append("Consider adding a specialized agent for better results")

            if "security_expert" not in task_data.get("agents_used", []):
                suggestions.append(
                    "Adding security expert agent may improve success rate"
                )

        # Duration optimizations
        if predictions["estimated_duration"] > 240:  # 4 minutes
            suggestions.append(
                "Consider using 'quick' depth parameter for faster execution"
            )
            suggestions.append("Split complex targets into smaller subtasks")

        # Quality optimizations
        if predictions["quality_score_prediction"] < 0.8:
            suggestions.append("Use 'comprehensive' depth for better quality results")
            suggestions.append("Add code analysis agent for enhanced quality")

        # Agent optimization
        agents = task_data.get("agents_used", [])
        task_type = task_data["task_type"]

        if task_type == "security_scan" and "intelligence_gathering" not in agents:
            suggestions.append(
                "Add intelligence gathering agent for enhanced security analysis"
            )

        if task_type == "code_analysis" and "security_expert" not in agents:
            suggestions.append(
                "Add security expert for comprehensive code security review"
            )

        # Parameter optimizations
        params = task_data.get("parameters", {})
        if not params.get("depth"):
            suggestions.append(
                "Specify depth parameter (quick/standard/comprehensive) for better results"
            )

        return suggestions

    async def predict_system_resources(
        self, time_horizon_minutes: int = 60
    ) -> SystemResourcePrediction:
        """Predict system resource usage for the next time period"""

        try:
            # Use recent system metrics to predict future usage
            current_time = datetime.now()

            # Generate time series features for prediction
            future_points = []
            for i in range(time_horizon_minutes):
                future_time = current_time + timedelta(minutes=i)

                # Create feature vector for this time point
                feature_vector = [
                    50.0,  # Baseline CPU
                    60.0,  # Baseline memory
                    5,  # Baseline task load
                    10.0,  # CPU variance
                    15.0,  # Memory variance
                    7,  # Active agents
                    3,  # Queue length
                    0,  # Error count
                    future_time.hour,
                    future_time.weekday(),
                    future_time.minute,
                ]
                future_points.append(feature_vector)

            future_features = np.array(future_points)

            # Predict resource usage
            predictions = {}

            if "cpu_usage" in self.models and hasattr(
                self.models["cpu_usage"], "predict"
            ):
                try:
                    cpu_scaled = self.scalers["cpu_usage"].transform(future_features)
                    cpu_pred = self.models["cpu_usage"].predict(cpu_scaled)
                    predictions["cpu"] = float(np.mean(cpu_pred))
                except:
                    predictions["cpu"] = 45.0  # Default
            else:
                predictions["cpu"] = 45.0

            if "memory_usage" in self.models and hasattr(
                self.models["memory_usage"], "predict"
            ):
                try:
                    mem_scaled = self.scalers["memory_usage"].transform(future_features)
                    mem_pred = self.models["memory_usage"].predict(mem_scaled)
                    predictions["memory"] = float(np.mean(mem_pred))
                except:
                    predictions["memory"] = 55.0  # Default
            else:
                predictions["memory"] = 55.0

            if "task_load" in self.models and hasattr(
                self.models["task_load"], "predict"
            ):
                try:
                    load_scaled = self.scalers["task_load"].transform(future_features)
                    load_pred = self.models["task_load"].predict(load_scaled)
                    predictions["task_load"] = int(np.mean(load_pred))
                except:
                    predictions["task_load"] = 5  # Default
            else:
                predictions["task_load"] = 5

        except Exception as e:
            self.logger.warning(f"⚠️ Resource prediction error: {e}, using defaults")
            predictions = {"cpu": 45.0, "memory": 55.0, "task_load": 5}

        # Identify potential bottlenecks
        bottlenecks = []
        if predictions["cpu"] > 80:
            bottlenecks.append("High CPU usage predicted")
        if predictions["memory"] > 85:
            bottlenecks.append("High memory usage predicted")
        if predictions["task_load"] > 20:
            bottlenecks.append("High task queue predicted")

        # Generate scaling recommendations
        scaling_recommendations = []
        if predictions["cpu"] > 70:
            scaling_recommendations.append(
                "Consider horizontal scaling for CPU-intensive tasks"
            )
        if predictions["memory"] > 75:
            scaling_recommendations.append("Consider increasing memory allocation")
        if predictions["task_load"] > 15:
            scaling_recommendations.append("Consider adding more worker processes")

        return SystemResourcePrediction(
            time_horizon_minutes=time_horizon_minutes,
            predicted_cpu_usage=predictions["cpu"],
            predicted_memory_usage=predictions["memory"],
            predicted_task_load=predictions["task_load"],
            bottleneck_predictions=bottlenecks,
            scaling_recommendations=scaling_recommendations,
        )

    async def get_prediction_accuracy_report(self) -> Dict[str, Any]:
        """Generate a report on prediction accuracy"""

        accuracy_metrics = {}

        for model_name, model in self.models.items():
            if hasattr(model, "score") and model_name in self.training_data:
                try:
                    # Get training data for this model
                    if model_name in ["task_success", "task_duration", "quality_score"]:
                        df = self.training_data.get("task_outcome", pd.DataFrame())
                    else:
                        df = self.training_data.get("resource_usage", pd.DataFrame())

                    if len(df) > 10:
                        if model_name == "task_success":
                            features = self._extract_task_features(df)
                            if "success_rate" in df.columns:
                                y = (df["success_rate"] > 0.8).astype(int)
                                X_scaled = self.scalers[model_name].transform(features)
                                accuracy = model.score(X_scaled, y)
                                accuracy_metrics[model_name] = {
                                    "accuracy": accuracy,
                                    "samples": len(df),
                                    "type": "classification",
                                }

                        elif model_name in ["task_duration", "quality_score"]:
                            features = self._extract_task_features(df)
                            target_col = (
                                "execution_time"
                                if model_name == "task_duration"
                                else "quality_score"
                            )
                            if target_col in df.columns:
                                y = df[target_col].values
                                X_scaled = self.scalers[model_name].transform(features)
                                r2 = model.score(X_scaled, y)
                                accuracy_metrics[model_name] = {
                                    "r2_score": r2,
                                    "samples": len(df),
                                    "type": "regression",
                                }
                except Exception as e:
                    self.logger.warning(
                        f"⚠️ Could not calculate accuracy for {model_name}: {e}"
                    )

        return {
            "model_accuracies": accuracy_metrics,
            "total_predictions": len(self.prediction_history),
            "last_training": datetime.now().isoformat(),
            "feature_importance": self.feature_importance,
        }

# CLI interface for testing
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AMAS Predictive Intelligence Engine")
    parser.add_argument("--test", action="store_true", help="Run test predictions")
    parser.add_argument("--train", action="store_true", help="Train with sample data")

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    engine = PredictiveIntelligenceEngine()

    async def test_predictions():
        """Test prediction capabilities"""
        print("🧪 Testing Predictive Intelligence Engine...")

        # Test task outcome prediction
        task_prediction = await engine.predict_task_outcome(
            task_type="security_scan",
            target="example.com",
            parameters={"depth": "comprehensive"},
            agents_planned=["security_expert", "intelligence_gathering"],
        )

        print(f"\n🎯 Task Prediction:")
        print(f"  Success Probability: {task_prediction.success_probability:.2f}")
        print(f"  Estimated Duration: {task_prediction.estimated_duration:.1f}s")
        print(f"  Quality Score: {task_prediction.quality_score_prediction:.2f}")
        print(f"  Confidence: {task_prediction.confidence:.2f}")
        print(f"  Risk Factors: {task_prediction.risk_factors}")
        print(f"  Suggestions: {task_prediction.optimization_suggestions}")

        # Test resource prediction
        resource_prediction = await engine.predict_system_resources(60)

        print(f"\n📊 Resource Prediction (60 minutes):")
        print(f"  Predicted CPU: {resource_prediction.predicted_cpu_usage:.1f}%")
        print(f"  Predicted Memory: {resource_prediction.predicted_memory_usage:.1f}%")
        print(f"  Predicted Task Load: {resource_prediction.predicted_task_load}")
        print(f"  Bottlenecks: {resource_prediction.bottleneck_predictions}")
        print(f"  Recommendations: {resource_prediction.scaling_recommendations}")

        print("\n✅ Prediction tests completed!")

    async def train_with_sample_data():
        """Train models with sample data"""
        print("🏋️ Training models with sample data...")

        # Add sample task outcome data
        sample_tasks = [
            {
                "task_type": "security_scan",
                "target": "example.com",
                "parameters": {"depth": "quick"},
                "agents_used": ["security_expert"],
                "execution_time": 45.2,
                "success_rate": 0.9,
                "quality_score": 0.8,
                "timestamp": datetime.now().isoformat(),
            },
            {
                "task_type": "code_analysis",
                "target": "github.com/test/repo",
                "parameters": {"depth": "comprehensive"},
                "agents_used": ["code_analysis", "security_expert"],
                "execution_time": 180.5,
                "success_rate": 0.95,
                "quality_score": 0.9,
                "timestamp": datetime.now().isoformat(),
            },
            # Add more sample data...
        ]

        for task in sample_tasks:
            await engine.add_training_data("task_outcome", task)

        # Add sample resource data
        sample_resources = [
            {
                "cpu_usage": 45.2,
                "memory_usage": 62.1,
                "task_load": 5,
                "active_agents": 7,
                "queue_length": 2,
                "error_count": 0,
                "timestamp": datetime.now().isoformat(),
            }
            # Add more sample data...
        ]

        for resource in sample_resources:
            await engine.add_training_data("resource_usage", resource)

        # Generate accuracy report
        report = await engine.get_prediction_accuracy_report()
        print(f"\n📈 Accuracy Report: {report}")

        print("\n✅ Training completed!")

    if args.test:
        asyncio.run(test_predictions())
    elif args.train:
        asyncio.run(train_with_sample_data())
    else:
        print("Use --test to run predictions or --train to train with sample data")
