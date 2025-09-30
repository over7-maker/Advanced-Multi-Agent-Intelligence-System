"""
AMAS Intelligence System - Advanced Analytics Service
Phase 8: Predictive analytics, machine learning models, and AI insights
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Union
from enum import Enum
from dataclasses import dataclass
import json
import pickle
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib
import warnings

warnings.filterwarnings("ignore")

logger = logging.getLogger(__name__)


class AnalyticsType(Enum):
    PREDICTIVE = "predictive"
    DESCRIPTIVE = "descriptive"
    PRESCRIPTIVE = "prescriptive"
    DIAGNOSTIC = "diagnostic"


class ModelType(Enum):
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    ANOMALY_DETECTION = "anomaly_detection"
    TIME_SERIES = "time_series"
    NLP = "nlp"
    COMPUTER_VISION = "computer_vision"


class InsightLevel(Enum):
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class AnalyticsModel:
    model_id: str
    name: str
    model_type: ModelType
    analytics_type: AnalyticsType
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    created_at: datetime
    last_trained: datetime
    status: str
    parameters: Dict[str, Any]


@dataclass
class AnalyticsInsight:
    insight_id: str
    title: str
    description: str
    confidence: float
    impact: str
    recommendations: List[str]
    data_sources: List[str]
    created_at: datetime
    insight_level: InsightLevel


@dataclass
class PredictionResult:
    prediction_id: str
    model_id: str
    input_data: Dict[str, Any]
    prediction: Any
    confidence: float
    probability: Optional[float]
    created_at: datetime


class AdvancedAnalyticsService:
    """Advanced analytics service for Phase 8"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.analytics_enabled = True
        self.models = {}
        self.insights = {}
        self.predictions = {}

        # Model storage
        self.model_storage_path = config.get("model_storage_path", "models/")
        self.insight_storage_path = config.get("insight_storage_path", "insights/")

        # Analytics configuration
        self.analytics_config = {
            "auto_training": config.get("auto_training", True),
            "model_retraining_interval": config.get(
                "model_retraining_interval", 24 * 3600
            ),  # 24 hours
            "insight_generation_interval": config.get(
                "insight_generation_interval", 3600
            ),  # 1 hour
            "prediction_cache_ttl": config.get("prediction_cache_ttl", 3600),  # 1 hour
            "max_models_per_type": config.get("max_models_per_type", 10),
            "min_training_samples": config.get("min_training_samples", 100),
        }

        # Background tasks
        self.analytics_tasks = []

        logger.info("Advanced Analytics Service initialized")

    async def initialize(self):
        """Initialize advanced analytics service"""
        try:
            logger.info("Initializing Advanced Analytics Service...")

            await self._initialize_model_storage()
            await self._initialize_insight_generation()
            await self._initialize_predictive_models()
            await self._initialize_analytics_pipeline()
            await self._start_analytics_tasks()

            logger.info("Advanced Analytics Service initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Advanced Analytics Service: {e}")
            raise

    async def _initialize_model_storage(self):
        """Initialize model storage"""
        try:
            import os

            os.makedirs(self.model_storage_path, exist_ok=True)
            os.makedirs(self.insight_storage_path, exist_ok=True)

            # Load existing models
            await self._load_existing_models()

            logger.info("Model storage initialized")

        except Exception as e:
            logger.error(f"Failed to initialize model storage: {e}")
            raise

    async def _load_existing_models(self):
        """Load existing models from storage"""
        try:
            import os
            import glob

            model_files = glob.glob(f"{self.model_storage_path}*.pkl")

            for model_file in model_files:
                try:
                    model_data = joblib.load(model_file)
                    if isinstance(model_data, dict) and "model" in model_data:
                        model_id = model_data.get("model_id", "unknown")
                        self.models[model_id] = model_data
                        logger.info(f"Loaded model: {model_id}")
                except Exception as e:
                    logger.warning(f"Failed to load model from {model_file}: {e}")

            logger.info(f"Loaded {len(self.models)} existing models")

        except Exception as e:
            logger.error(f"Failed to load existing models: {e}")

    async def _initialize_insight_generation(self):
        """Initialize insight generation"""
        try:
            # Initialize insight generation rules
            self.insight_rules = [
                {
                    "name": "performance_trend_analysis",
                    "condition": lambda data: len(data) > 100,
                    "generator": self._generate_performance_trend_insights,
                    "priority": 1,
                },
                {
                    "name": "anomaly_detection_insights",
                    "condition": lambda data: len(data) > 50,
                    "generator": self._generate_anomaly_insights,
                    "priority": 2,
                },
                {
                    "name": "predictive_insights",
                    "condition": lambda data: len(data) > 200,
                    "generator": self._generate_predictive_insights,
                    "priority": 3,
                },
            ]

            logger.info("Insight generation initialized")

        except Exception as e:
            logger.error(f"Failed to initialize insight generation: {e}")
            raise

    async def _initialize_predictive_models(self):
        """Initialize predictive models"""
        try:
            # Initialize default models
            default_models = [
                {
                    "model_id": "threat_classification",
                    "name": "Threat Classification Model",
                    "model_type": ModelType.CLASSIFICATION,
                    "analytics_type": AnalyticsType.PREDICTIVE,
                    "algorithm": "RandomForestClassifier",
                },
                {
                    "model_id": "performance_prediction",
                    "name": "Performance Prediction Model",
                    "model_type": ModelType.REGRESSION,
                    "analytics_type": AnalyticsType.PREDICTIVE,
                    "algorithm": "GradientBoostingRegressor",
                },
                {
                    "model_id": "anomaly_detection",
                    "name": "Anomaly Detection Model",
                    "model_type": ModelType.ANOMALY_DETECTION,
                    "analytics_type": AnalyticsType.DIAGNOSTIC,
                    "algorithm": "DBSCAN",
                },
                {
                    "model_id": "user_behavior_clustering",
                    "name": "User Behavior Clustering Model",
                    "model_type": ModelType.CLUSTERING,
                    "analytics_type": AnalyticsType.DESCRIPTIVE,
                    "algorithm": "KMeans",
                },
            ]

            for model_config in default_models:
                if model_config["model_id"] not in self.models:
                    await self._create_model(model_config)

            logger.info("Predictive models initialized")

        except Exception as e:
            logger.error(f"Failed to initialize predictive models: {e}")
            raise

    async def _initialize_analytics_pipeline(self):
        """Initialize analytics pipeline"""
        try:
            # Data preprocessing pipeline
            self.preprocessing_pipeline = {
                "scaler": StandardScaler(),
                "label_encoder": LabelEncoder(),
                "feature_selector": None,  # Would be implemented based on specific needs
            }

            # Model evaluation metrics
            self.evaluation_metrics = {
                "classification": ["accuracy", "precision", "recall", "f1_score"],
                "regression": ["mse", "rmse", "mae", "r2_score"],
                "clustering": ["silhouette_score", "inertia"],
                "anomaly_detection": ["precision", "recall", "f1_score"],
            }

            logger.info("Analytics pipeline initialized")

        except Exception as e:
            logger.error(f"Failed to initialize analytics pipeline: {e}")
            raise

    async def _start_analytics_tasks(self):
        """Start background analytics tasks"""
        try:
            logger.info("Starting analytics tasks...")

            self.analytics_tasks = [
                asyncio.create_task(self._auto_train_models()),
                asyncio.create_task(self._generate_insights()),
                asyncio.create_task(self._update_model_performance()),
                asyncio.create_task(self._cleanup_old_data()),
            ]

            logger.info("Analytics tasks started")

        except Exception as e:
            logger.error(f"Failed to start analytics tasks: {e}")
            raise

    async def create_model(self, model_config: Dict[str, Any]) -> str:
        """Create a new analytics model"""
        try:
            model_id = model_config.get(
                "model_id", f"model_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            )

            # Create model instance
            model = await self._create_model_instance(model_config)

            # Store model
            self.models[model_id] = {
                "model_id": model_id,
                "model": model,
                "config": model_config,
                "metrics": {},
                "created_at": datetime.utcnow(),
                "last_trained": None,
                "status": "created",
            }

            logger.info(f"Created model: {model_id}")
            return model_id

        except Exception as e:
            logger.error(f"Failed to create model: {e}")
            raise

    async def _create_model(self, model_config: Dict[str, Any]):
        """Create model instance"""
        try:
            model_id = model_config["model_id"]

            # Create analytics model
            analytics_model = AnalyticsModel(
                model_id=model_id,
                name=model_config["name"],
                model_type=model_config["model_type"],
                analytics_type=model_config["analytics_type"],
                accuracy=0.0,
                precision=0.0,
                recall=0.0,
                f1_score=0.0,
                created_at=datetime.utcnow(),
                last_trained=None,
                status="created",
                parameters=model_config.get("parameters", {}),
            )

            # Create ML model instance
            algorithm = model_config.get("algorithm", "RandomForestClassifier")
            model_instance = await self._get_model_instance(
                algorithm, model_config.get("parameters", {})
            )

            # Store model
            self.models[model_id] = {
                "model_id": model_id,
                "analytics_model": analytics_model,
                "model": model_instance,
                "config": model_config,
                "metrics": {},
                "created_at": datetime.utcnow(),
                "last_trained": None,
                "status": "created",
            }

            # Save model to storage
            await self._save_model(model_id)

        except Exception as e:
            logger.error(f"Failed to create model {model_config['model_id']}: {e}")
            raise

    async def _get_model_instance(self, algorithm: str, parameters: Dict[str, Any]):
        """Get model instance based on algorithm"""
        try:
            if algorithm == "RandomForestClassifier":
                return RandomForestClassifier(
                    n_estimators=parameters.get("n_estimators", 100),
                    max_depth=parameters.get("max_depth", None),
                    random_state=42,
                )
            elif algorithm == "GradientBoostingRegressor":
                return GradientBoostingRegressor(
                    n_estimators=parameters.get("n_estimators", 100),
                    learning_rate=parameters.get("learning_rate", 0.1),
                    random_state=42,
                )
            elif algorithm == "KMeans":
                return KMeans(
                    n_clusters=parameters.get("n_clusters", 3), random_state=42
                )
            elif algorithm == "DBSCAN":
                return DBSCAN(
                    eps=parameters.get("eps", 0.5),
                    min_samples=parameters.get("min_samples", 5),
                )
            else:
                raise ValueError(f"Unknown algorithm: {algorithm}")

        except Exception as e:
            logger.error(f"Failed to get model instance: {e}")
            raise

    async def train_model(
        self, model_id: str, training_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Train a model with provided data"""
        try:
            if model_id not in self.models:
                raise ValueError(f"Model {model_id} not found")

            model_data = self.models[model_id]
            model = model_data["model"]

            # Prepare training data
            X, y = await self._prepare_training_data(
                training_data, model_data["config"]
            )

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            # Train model
            model.fit(X_train, y_train)

            # Evaluate model
            metrics = await self._evaluate_model(
                model, X_test, y_test, model_data["config"]
            )

            # Update model data
            model_data["last_trained"] = datetime.utcnow()
            model_data["status"] = "trained"
            model_data["metrics"] = metrics

            # Update analytics model
            if "analytics_model" in model_data:
                analytics_model = model_data["analytics_model"]
                analytics_model.accuracy = metrics.get("accuracy", 0.0)
                analytics_model.precision = metrics.get("precision", 0.0)
                analytics_model.recall = metrics.get("recall", 0.0)
                analytics_model.f1_score = metrics.get("f1_score", 0.0)
                analytics_model.last_trained = datetime.utcnow()
                analytics_model.status = "trained"

            # Save model
            await self._save_model(model_id)

            logger.info(f"Model {model_id} trained successfully")
            return metrics

        except Exception as e:
            logger.error(f"Failed to train model {model_id}: {e}")
            raise

    async def _prepare_training_data(
        self, training_data: Dict[str, Any], model_config: Dict[str, Any]
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare training data for model"""
        try:
            # Convert to DataFrame if needed
            if isinstance(training_data, dict):
                df = pd.DataFrame([training_data])
            else:
                df = pd.DataFrame(training_data)

            # Extract features and target
            feature_columns = model_config.get("feature_columns", [])
            target_column = model_config.get("target_column", "target")

            if not feature_columns:
                # Auto-detect features (exclude target column)
                feature_columns = [col for col in df.columns if col != target_column]

            X = df[feature_columns].values
            y = (
                df[target_column].values
                if target_column in df.columns
                else np.zeros(len(df))
            )

            # Handle missing values
            X = np.nan_to_num(X)
            y = np.nan_to_num(y)

            return X, y

        except Exception as e:
            logger.error(f"Failed to prepare training data: {e}")
            raise

    async def _evaluate_model(
        self,
        model,
        X_test: np.ndarray,
        y_test: np.ndarray,
        model_config: Dict[str, Any],
    ) -> Dict[str, float]:
        """Evaluate model performance"""
        try:
            model_type = model_config.get("model_type", ModelType.CLASSIFICATION)

            if model_type == ModelType.CLASSIFICATION:
                y_pred = model.predict(X_test)
                return {
                    "accuracy": accuracy_score(y_test, y_pred),
                    "precision": precision_score(y_test, y_pred, average="weighted"),
                    "recall": recall_score(y_test, y_pred, average="weighted"),
                    "f1_score": f1_score(y_test, y_pred, average="weighted"),
                }
            elif model_type == ModelType.REGRESSION:
                y_pred = model.predict(X_test)
                mse = np.mean((y_test - y_pred) ** 2)
                rmse = np.sqrt(mse)
                mae = np.mean(np.abs(y_test - y_pred))
                r2 = model.score(X_test, y_test)
                return {"mse": mse, "rmse": rmse, "mae": mae, "r2_score": r2}
            elif model_type == ModelType.CLUSTERING:
                labels = model.predict(X_test)
                return {
                    "n_clusters": len(set(labels)),
                    "inertia": model.inertia_ if hasattr(model, "inertia_") else 0.0,
                }
            else:
                return {
                    "score": (
                        model.score(X_test, y_test) if hasattr(model, "score") else 0.0
                    )
                }

        except Exception as e:
            logger.error(f"Failed to evaluate model: {e}")
            return {}

    async def predict(
        self, model_id: str, input_data: Dict[str, Any]
    ) -> PredictionResult:
        """Make prediction using trained model"""
        try:
            if model_id not in self.models:
                raise ValueError(f"Model {model_id} not found")

            model_data = self.models[model_id]
            model = model_data["model"]

            if model_data["status"] != "trained":
                raise ValueError(f"Model {model_id} is not trained")

            # Prepare input data
            X = await self._prepare_input_data(input_data, model_data["config"])

            # Make prediction
            prediction = model.predict(X)
            probability = None

            # Get prediction probability if available
            if hasattr(model, "predict_proba"):
                probabilities = model.predict_proba(X)
                probability = float(np.max(probabilities))

            # Create prediction result
            prediction_id = f"pred_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
            result = PredictionResult(
                prediction_id=prediction_id,
                model_id=model_id,
                input_data=input_data,
                prediction=(
                    prediction[0] if len(prediction) == 1 else prediction.tolist()
                ),
                confidence=probability or 0.0,
                probability=probability,
                created_at=datetime.utcnow(),
            )

            # Store prediction
            self.predictions[prediction_id] = result

            logger.info(f"Prediction made with model {model_id}: {result.prediction}")
            return result

        except Exception as e:
            logger.error(f"Failed to make prediction: {e}")
            raise

    async def _prepare_input_data(
        self, input_data: Dict[str, Any], model_config: Dict[str, Any]
    ) -> np.ndarray:
        """Prepare input data for prediction"""
        try:
            # Convert to DataFrame
            df = pd.DataFrame([input_data])

            # Extract features
            feature_columns = model_config.get("feature_columns", [])
            if not feature_columns:
                feature_columns = [col for col in df.columns if col != "target"]

            X = df[feature_columns].values
            X = np.nan_to_num(X)

            return X

        except Exception as e:
            logger.error(f"Failed to prepare input data: {e}")
            raise

    async def generate_insights(self, data: Dict[str, Any]) -> List[AnalyticsInsight]:
        """Generate analytics insights from data"""
        try:
            insights = []

            # Apply insight generation rules
            for rule in self.insight_rules:
                if rule["condition"](data):
                    rule_insights = await rule["generator"](data)
                    insights.extend(rule_insights)

            # Store insights
            for insight in insights:
                self.insights[insight.insight_id] = insight

            logger.info(f"Generated {len(insights)} insights")
            return insights

        except Exception as e:
            logger.error(f"Failed to generate insights: {e}")
            return []

    async def _generate_performance_trend_insights(
        self, data: Dict[str, Any]
    ) -> List[AnalyticsInsight]:
        """Generate performance trend insights"""
        try:
            insights = []

            # Mock performance trend analysis
            insight = AnalyticsInsight(
                insight_id=f"insight_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                title="Performance Trend Analysis",
                description="System performance shows improving trends over the last 24 hours",
                confidence=0.85,
                impact="positive",
                recommendations=[
                    "Continue current optimization strategies",
                    "Monitor for any performance regressions",
                    "Consider scaling resources if trends continue",
                ],
                data_sources=["performance_metrics", "system_logs"],
                created_at=datetime.utcnow(),
                insight_level=InsightLevel.INTERMEDIATE,
            )

            insights.append(insight)
            return insights

        except Exception as e:
            logger.error(f"Failed to generate performance trend insights: {e}")
            return []

    async def _generate_anomaly_insights(
        self, data: Dict[str, Any]
    ) -> List[AnalyticsInsight]:
        """Generate anomaly detection insights"""
        try:
            insights = []

            # Mock anomaly detection
            insight = AnalyticsInsight(
                insight_id=f"anomaly_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                title="Anomaly Detected",
                description="Unusual patterns detected in system behavior",
                confidence=0.92,
                impact="warning",
                recommendations=[
                    "Investigate the source of anomalies",
                    "Review security logs for potential threats",
                    "Consider implementing additional monitoring",
                ],
                data_sources=["anomaly_detection_model", "security_logs"],
                created_at=datetime.utcnow(),
                insight_level=InsightLevel.ADVANCED,
            )

            insights.append(insight)
            return insights

        except Exception as e:
            logger.error(f"Failed to generate anomaly insights: {e}")
            return []

    async def _generate_predictive_insights(
        self, data: Dict[str, Any]
    ) -> List[AnalyticsInsight]:
        """Generate predictive insights"""
        try:
            insights = []

            # Mock predictive insights
            insight = AnalyticsInsight(
                insight_id=f"predictive_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                title="Future Performance Prediction",
                description="Models predict system performance will remain stable over the next 7 days",
                confidence=0.78,
                impact="informational",
                recommendations=[
                    "Monitor actual performance against predictions",
                    "Adjust models if predictions prove inaccurate",
                    "Plan capacity based on predicted trends",
                ],
                data_sources=["performance_prediction_model", "historical_data"],
                created_at=datetime.utcnow(),
                insight_level=InsightLevel.EXPERT,
            )

            insights.append(insight)
            return insights

        except Exception as e:
            logger.error(f"Failed to generate predictive insights: {e}")
            return []

    async def _auto_train_models(self):
        """Auto-train models with new data"""
        while self.analytics_enabled:
            try:
                # Check if any models need retraining
                for model_id, model_data in self.models.items():
                    if model_data["status"] == "trained":
                        last_trained = model_data.get("last_trained")
                        if last_trained:
                            time_since_training = (
                                datetime.utcnow() - last_trained
                            ).total_seconds()
                            if (
                                time_since_training
                                > self.analytics_config["model_retraining_interval"]
                            ):
                                # Retrain model
                                await self._retrain_model(model_id)

                await asyncio.sleep(self.analytics_config["model_retraining_interval"])

            except Exception as e:
                logger.error(f"Auto-training error: {e}")
                await asyncio.sleep(3600)  # Wait 1 hour on error

    async def _retrain_model(self, model_id: str):
        """Retrain a model with new data"""
        try:
            # Mock retraining - in real implementation, this would use new data
            logger.info(f"Retraining model {model_id}")

            # Update last trained time
            self.models[model_id]["last_trained"] = datetime.utcnow()

            # Save model
            await self._save_model(model_id)

        except Exception as e:
            logger.error(f"Failed to retrain model {model_id}: {e}")

    async def _generate_insights(self):
        """Generate insights from available data"""
        while self.analytics_enabled:
            try:
                # Mock insight generation
                mock_data = {"sample_data": "mock"}
                insights = await self.generate_insights(mock_data)

                await asyncio.sleep(
                    self.analytics_config["insight_generation_interval"]
                )

            except Exception as e:
                logger.error(f"Insight generation error: {e}")
                await asyncio.sleep(3600)

    async def _update_model_performance(self):
        """Update model performance metrics"""
        while self.analytics_enabled:
            try:
                # Update performance metrics for all models
                for model_id, model_data in self.models.items():
                    if model_data["status"] == "trained":
                        # Mock performance update
                        model_data["metrics"]["last_updated"] = datetime.utcnow()

                await asyncio.sleep(3600)  # Update every hour

            except Exception as e:
                logger.error(f"Model performance update error: {e}")
                await asyncio.sleep(3600)

    async def _cleanup_old_data(self):
        """Cleanup old analytics data"""
        while self.analytics_enabled:
            try:
                # Cleanup old predictions
                cutoff_time = datetime.utcnow() - timedelta(days=7)
                old_predictions = [
                    pred_id
                    for pred_id, pred in self.predictions.items()
                    if pred.created_at < cutoff_time
                ]

                for pred_id in old_predictions:
                    del self.predictions[pred_id]

                # Cleanup old insights
                old_insights = [
                    insight_id
                    for insight_id, insight in self.insights.items()
                    if insight.created_at < cutoff_time
                ]

                for insight_id in old_insights:
                    del self.insights[insight_id]

                await asyncio.sleep(24 * 3600)  # Cleanup daily

            except Exception as e:
                logger.error(f"Data cleanup error: {e}")
                await asyncio.sleep(3600)

    async def _save_model(self, model_id: str):
        """Save model to storage"""
        try:
            if model_id in self.models:
                model_data = self.models[model_id]
                model_file = f"{self.model_storage_path}{model_id}.pkl"
                joblib.dump(model_data, model_file)
                logger.info(f"Saved model {model_id} to {model_file}")

        except Exception as e:
            logger.error(f"Failed to save model {model_id}: {e}")

    async def get_analytics_status(self) -> Dict[str, Any]:
        """Get analytics service status"""
        try:
            return {
                "analytics_enabled": self.analytics_enabled,
                "total_models": len(self.models),
                "trained_models": len(
                    [m for m in self.models.values() if m["status"] == "trained"]
                ),
                "total_insights": len(self.insights),
                "total_predictions": len(self.predictions),
                "analytics_tasks": len(self.analytics_tasks),
                "models": {
                    model_id: {
                        "name": model_data.get("config", {}).get("name", "Unknown"),
                        "status": model_data["status"],
                        "last_trained": model_data.get("last_trained"),
                        "metrics": model_data.get("metrics", {}),
                    }
                    for model_id, model_data in self.models.items()
                },
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"Failed to get analytics status: {e}")
            return {"error": str(e)}

    async def shutdown(self):
        """Shutdown analytics service"""
        try:
            logger.info("Shutting down Advanced Analytics Service...")

            self.analytics_enabled = False

            # Cancel analytics tasks
            for task in self.analytics_tasks:
                task.cancel()

            await asyncio.gather(*self.analytics_tasks, return_exceptions=True)

            # Save all models
            for model_id in self.models:
                await self._save_model(model_id)

            logger.info("Advanced Analytics Service shutdown complete")

        except Exception as e:
            logger.error(f"Error during analytics service shutdown: {e}")
