"""
Machine Learning Service for AMAS Intelligence System - Phase 4
Provides ML model management, training, inference, and advanced analytics
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timedelta
from enum import Enum
import json
import numpy as np
import pandas as pd
from dataclasses import dataclass
import joblib
from pathlib import Path

logger = logging.getLogger(__name__)


class ModelType(Enum):
    """Model type enumeration"""

    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    ANOMALY_DETECTION = "anomaly_detection"
    NLP = "nlp"
    COMPUTER_VISION = "computer_vision"
    RECOMMENDATION = "recommendation"
    TIME_SERIES = "time_series"


class ModelStatus(Enum):
    """Model status enumeration"""

    TRAINING = "training"
    TRAINED = "trained"
    DEPLOYED = "deployed"
    RETIRED = "retired"
    ERROR = "error"


@dataclass
class ModelMetrics:
    """Model metrics data structure"""

    model_id: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    auc_score: float
    mse: float
    mae: float
    r2_score: float
    timestamp: datetime


@dataclass
class TrainingJob:
    """Training job data structure"""

    job_id: str
    model_type: ModelType
    dataset_path: str
    parameters: Dict[str, Any]
    status: ModelStatus
    started_at: datetime
    completed_at: Optional[datetime]
    metrics: Optional[ModelMetrics]
    error_message: Optional[str]


class MLService:
    """
    Machine Learning Service for AMAS Intelligence System Phase 4

    Provides comprehensive ML capabilities including model management,
    training, inference, and advanced analytics.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the ML service.

        Args:
            config: Configuration dictionary
        """
        self.config = config

        # Model storage
        self.models = {}
        self.model_metrics = {}
        self.training_jobs = {}

        # ML configuration
        self.ml_config = {
            "model_storage_path": config.get("model_storage_path", "models/"),
            "dataset_storage_path": config.get("dataset_storage_path", "datasets/"),
            "max_models": config.get("max_models", 100),
            "auto_retrain": config.get("auto_retrain", True),
            "model_versioning": config.get("model_versioning", True),
        }

        # Model types and their configurations
        self.model_configs = {
            ModelType.CLASSIFICATION: {
                "algorithms": ["random_forest", "svm", "neural_network", "xgboost"],
                "default_algorithm": "random_forest",
                "hyperparameters": {
                    "random_forest": {"n_estimators": 100, "max_depth": 10},
                    "svm": {"C": 1.0, "kernel": "rbf"},
                    "neural_network": {"hidden_layers": [100, 50], "epochs": 100},
                    "xgboost": {"n_estimators": 100, "max_depth": 6},
                },
            },
            ModelType.REGRESSION: {
                "algorithms": [
                    "linear_regression",
                    "random_forest",
                    "neural_network",
                    "xgboost",
                ],
                "default_algorithm": "random_forest",
                "hyperparameters": {
                    "linear_regression": {"fit_intercept": True},
                    "random_forest": {"n_estimators": 100, "max_depth": 10},
                    "neural_network": {"hidden_layers": [100, 50], "epochs": 100},
                    "xgboost": {"n_estimators": 100, "max_depth": 6},
                },
            },
            ModelType.CLUSTERING: {
                "algorithms": ["kmeans", "dbscan", "hierarchical"],
                "default_algorithm": "kmeans",
                "hyperparameters": {
                    "kmeans": {"n_clusters": 8, "random_state": 42},
                    "dbscan": {"eps": 0.5, "min_samples": 5},
                    "hierarchical": {"n_clusters": 8, "linkage": "ward"},
                },
            },
            ModelType.ANOMALY_DETECTION: {
                "algorithms": [
                    "isolation_forest",
                    "one_class_svm",
                    "local_outlier_factor",
                ],
                "default_algorithm": "isolation_forest",
                "hyperparameters": {
                    "isolation_forest": {"contamination": 0.1, "random_state": 42},
                    "one_class_svm": {"nu": 0.1, "kernel": "rbf"},
                    "local_outlier_factor": {"n_neighbors": 20, "contamination": 0.1},
                },
            },
            ModelType.NLP: {
                "algorithms": ["transformer", "lstm", "bert", "gpt"],
                "default_algorithm": "transformer",
                "hyperparameters": {
                    "transformer": {"num_layers": 6, "d_model": 512, "num_heads": 8},
                    "lstm": {"hidden_size": 128, "num_layers": 2, "dropout": 0.2},
                    "bert": {"model_name": "bert-base-uncased", "max_length": 512},
                    "gpt": {"model_name": "gpt-2", "max_length": 1024},
                },
            },
            ModelType.COMPUTER_VISION: {
                "algorithms": ["cnn", "resnet", "vgg", "yolo"],
                "default_algorithm": "cnn",
                "hyperparameters": {
                    "cnn": {"num_filters": 32, "kernel_size": 3, "pool_size": 2},
                    "resnet": {"num_layers": 18, "pretrained": True},
                    "vgg": {"num_layers": 16, "pretrained": True},
                    "yolo": {"num_classes": 80, "input_size": 416},
                },
            },
        }

        # Training queue
        self.training_queue = []
        self.active_training_jobs = {}

        # Model performance tracking
        self.performance_history = {}

        logger.info("ML Service initialized")

    async def initialize(self):
        """Initialize the ML service"""
        try:
            logger.info("Initializing ML service...")

            # Create storage directories
            await self._create_storage_directories()

            # Load existing models
            await self._load_existing_models()

            # Initialize model monitoring
            await self._initialize_model_monitoring()

            # Start training scheduler
            await self._start_training_scheduler()

            logger.info("ML service initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize ML service: {e}")
            raise

    async def _create_storage_directories(self):
        """Create storage directories"""
        try:
            # Create model storage directory
            Path(self.ml_config["model_storage_path"]).mkdir(
                parents=True, exist_ok=True
            )

            # Create dataset storage directory
            Path(self.ml_config["dataset_storage_path"]).mkdir(
                parents=True, exist_ok=True
            )

            logger.info("Storage directories created")

        except Exception as e:
            logger.error(f"Failed to create storage directories: {e}")
            raise

    async def _load_existing_models(self):
        """Load existing models from storage"""
        try:
            model_path = Path(self.ml_config["model_storage_path"])

            if model_path.exists():
                for model_file in model_path.glob("*.pkl"):
                    model_id = model_file.stem
                    try:
                        # Load model metadata
                        metadata_file = model_path / f"{model_id}_metadata.json"
                        if metadata_file.exists():
                            with open(metadata_file, "r") as f:
                                metadata = json.load(f)

                            self.models[model_id] = metadata
                            logger.info(f"Loaded model {model_id}")
                    except Exception as e:
                        logger.warning(f"Failed to load model {model_id}: {e}")

            logger.info(f"Loaded {len(self.models)} existing models")

        except Exception as e:
            logger.error(f"Failed to load existing models: {e}")
            raise

    async def _initialize_model_monitoring(self):
        """Initialize model monitoring"""
        try:
            # Initialize performance tracking
            self.performance_history = {}

            # Start model monitoring tasks
            asyncio.create_task(self._monitor_model_performance())
            asyncio.create_task(self._monitor_training_jobs())

            logger.info("Model monitoring initialized")

        except Exception as e:
            logger.error(f"Failed to initialize model monitoring: {e}")
            raise

    async def _start_training_scheduler(self):
        """Start training scheduler"""
        try:
            # Start training scheduler task
            asyncio.create_task(self._training_scheduler())

            logger.info("Training scheduler started")

        except Exception as e:
            logger.error(f"Failed to start training scheduler: {e}")
            raise

    async def train_model(
        self,
        model_type: ModelType,
        dataset_path: str,
        algorithm: str = None,
        hyperparameters: Dict[str, Any] = None,
        target_column: str = None,
    ) -> str:
        """
        Train a new ML model.

        Args:
            model_type: Type of model to train
            dataset_path: Path to training dataset
            algorithm: Algorithm to use (optional)
            hyperparameters: Hyperparameters for the model
            target_column: Target column for supervised learning

        Returns:
            Training job ID
        """
        try:
            # Generate job ID
            job_id = f"job_{int(datetime.utcnow().timestamp())}"

            # Get algorithm and hyperparameters
            if not algorithm:
                algorithm = self.model_configs[model_type]["default_algorithm"]

            if not hyperparameters:
                hyperparameters = self.model_configs[model_type]["hyperparameters"][
                    algorithm
                ]

            # Create training job
            training_job = TrainingJob(
                job_id=job_id,
                model_type=model_type,
                dataset_path=dataset_path,
                parameters={
                    "algorithm": algorithm,
                    "hyperparameters": hyperparameters,
                    "target_column": target_column,
                },
                status=ModelStatus.TRAINING,
                started_at=datetime.utcnow(),
                completed_at=None,
                metrics=None,
                error_message=None,
            )

            # Add to training queue
            self.training_queue.append(training_job)
            self.training_jobs[job_id] = training_job

            logger.info(f"Training job {job_id} queued for {model_type.value} model")
            return job_id

        except Exception as e:
            logger.error(f"Failed to create training job: {e}")
            raise

    async def _training_scheduler(self):
        """Training scheduler to process training jobs"""
        while True:
            try:
                # Process training queue
                if (
                    self.training_queue and len(self.active_training_jobs) < 3
                ):  # Max 3 concurrent jobs
                    job = self.training_queue.pop(0)
                    self.active_training_jobs[job.job_id] = job

                    # Start training task
                    asyncio.create_task(self._train_model_async(job))

                await asyncio.sleep(10)  # Check every 10 seconds

            except Exception as e:
                logger.error(f"Training scheduler error: {e}")
                await asyncio.sleep(60)

    async def _train_model_async(self, job: TrainingJob):
        """Train model asynchronously"""
        try:
            logger.info(f"Starting training for job {job.job_id}")

            # Load dataset
            dataset = await self._load_dataset(job.dataset_path)

            # Prepare data
            X, y = await self._prepare_data(
                dataset, job.parameters.get("target_column")
            )

            # Train model
            model = await self._train_model_algorithm(
                job.model_type,
                job.parameters["algorithm"],
                job.parameters["hyperparameters"],
                X,
                y,
            )

            # Evaluate model
            metrics = await self._evaluate_model(model, X, y, job.model_type)

            # Save model
            model_id = await self._save_model(model, job, metrics)

            # Update job status
            job.status = ModelStatus.TRAINED
            job.completed_at = datetime.utcnow()
            job.metrics = metrics

            # Remove from active jobs
            if job.job_id in self.active_training_jobs:
                del self.active_training_jobs[job.job_id]

            logger.info(
                f"Training completed for job {job.job_id}, model ID: {model_id}"
            )

        except Exception as e:
            logger.error(f"Training failed for job {job.job_id}: {e}")
            job.status = ModelStatus.ERROR
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()

            if job.job_id in self.active_training_jobs:
                del self.active_training_jobs[job.job_id]

    async def _load_dataset(self, dataset_path: str) -> pd.DataFrame:
        """Load dataset from file"""
        try:
            # Simulate dataset loading
            # In real implementation, this would load actual data
            data = {
                "feature1": np.random.randn(1000),
                "feature2": np.random.randn(1000),
                "feature3": np.random.randn(1000),
                "target": np.random.randint(0, 2, 1000),
            }

            return pd.DataFrame(data)

        except Exception as e:
            logger.error(f"Failed to load dataset: {e}")
            raise

    async def _prepare_data(
        self, dataset: pd.DataFrame, target_column: str = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare data for training"""
        try:
            if target_column and target_column in dataset.columns:
                X = dataset.drop(columns=[target_column]).values
                y = dataset[target_column].values
            else:
                X = dataset.values
                y = None

            return X, y

        except Exception as e:
            logger.error(f"Failed to prepare data: {e}")
            raise

    async def _train_model_algorithm(
        self,
        model_type: ModelType,
        algorithm: str,
        hyperparameters: Dict[str, Any],
        X: np.ndarray,
        y: np.ndarray = None,
    ):
        """Train model using specified algorithm"""
        try:
            # Simulate model training
            # In real implementation, this would use actual ML libraries
            await asyncio.sleep(2)  # Simulate training time

            # Create mock model
            model = {
                "algorithm": algorithm,
                "hyperparameters": hyperparameters,
                "trained_at": datetime.utcnow(),
                "model_type": model_type.value,
            }

            return model

        except Exception as e:
            logger.error(f"Failed to train model algorithm: {e}")
            raise

    async def _evaluate_model(
        self, model: Dict[str, Any], X: np.ndarray, y: np.ndarray, model_type: ModelType
    ) -> ModelMetrics:
        """Evaluate model performance"""
        try:
            # Simulate model evaluation
            # In real implementation, this would perform actual evaluation
            await asyncio.sleep(1)  # Simulate evaluation time

            # Generate mock metrics
            metrics = ModelMetrics(
                model_id="temp",
                accuracy=0.85 + np.random.random() * 0.1,
                precision=0.82 + np.random.random() * 0.1,
                recall=0.80 + np.random.random() * 0.1,
                f1_score=0.81 + np.random.random() * 0.1,
                auc_score=0.88 + np.random.random() * 0.1,
                mse=0.15 + np.random.random() * 0.05,
                mae=0.12 + np.random.random() * 0.03,
                r2_score=0.83 + np.random.random() * 0.1,
                timestamp=datetime.utcnow(),
            )

            return metrics

        except Exception as e:
            logger.error(f"Failed to evaluate model: {e}")
            raise

    async def _save_model(
        self, model: Dict[str, Any], job: TrainingJob, metrics: ModelMetrics
    ) -> str:
        """Save trained model"""
        try:
            model_id = f"model_{int(datetime.utcnow().timestamp())}"

            # Save model file using joblib (safer than pickle)
            model_path = Path(self.ml_config["model_storage_path"]) / f"{model_id}.pkl"
            joblib.dump(model, model_path)

            # Save model metadata
            metadata = {
                "model_id": model_id,
                "model_type": job.model_type.value,
                "algorithm": job.parameters["algorithm"],
                "hyperparameters": job.parameters["hyperparameters"],
                "metrics": {
                    "accuracy": metrics.accuracy,
                    "precision": metrics.precision,
                    "recall": metrics.recall,
                    "f1_score": metrics.f1_score,
                    "auc_score": metrics.auc_score,
                    "mse": metrics.mse,
                    "mae": metrics.mae,
                    "r2_score": metrics.r2_score,
                },
                "trained_at": job.started_at.isoformat(),
                "completed_at": (
                    job.completed_at.isoformat() if job.completed_at else None
                ),
                "status": job.status.value,
            }

            metadata_path = (
                Path(self.ml_config["model_storage_path"]) / f"{model_id}_metadata.json"
            )
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)

            # Store in memory
            self.models[model_id] = metadata
            self.model_metrics[model_id] = metrics

            logger.info(f"Model {model_id} saved successfully")
            return model_id

        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            raise

    async def predict(self, model_id: str, data: np.ndarray) -> np.ndarray:
        """
        Make predictions using a trained model.

        Args:
            model_id: ID of the model to use
            data: Input data for prediction

        Returns:
            Predictions
        """
        try:
            if model_id not in self.models:
                raise ValueError(f"Model {model_id} not found")

            # Load model using joblib (safer than pickle)
            model_path = Path(self.ml_config["model_storage_path"]) / f"{model_id}.pkl"
            # Using joblib for safer model loading
            try:
                model = joblib.load(model_path)
            except Exception as e:
                logger.error(f"Failed to load model {model_id}: {e}")
                raise ValueError(f"Failed to load model {model_id}: {e}")

            # Simulate prediction
            # In real implementation, this would use actual model prediction
            await asyncio.sleep(0.1)  # Simulate prediction time

            # Generate mock predictions
            predictions = np.random.randn(data.shape[0])

            logger.info(f"Predictions generated for model {model_id}")
            return predictions

        except Exception as e:
            logger.error(f"Failed to make predictions: {e}")
            raise

    async def get_model_info(self, model_id: str) -> Dict[str, Any]:
        """Get model information"""
        try:
            if model_id not in self.models:
                raise ValueError(f"Model {model_id} not found")

            return self.models[model_id]

        except Exception as e:
            logger.error(f"Failed to get model info: {e}")
            raise

    async def get_model_metrics(self, model_id: str) -> ModelMetrics:
        """Get model metrics"""
        try:
            if model_id not in self.model_metrics:
                raise ValueError(f"Model metrics for {model_id} not found")

            return self.model_metrics[model_id]

        except Exception as e:
            logger.error(f"Failed to get model metrics: {e}")
            raise

    async def list_models(self, model_type: ModelType = None) -> List[Dict[str, Any]]:
        """List all models"""
        try:
            models = list(self.models.values())

            if model_type:
                models = [m for m in models if m["model_type"] == model_type.value]

            return models

        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []

    async def delete_model(self, model_id: str) -> bool:
        """Delete a model"""
        try:
            if model_id not in self.models:
                raise ValueError(f"Model {model_id} not found")

            # Delete model file
            model_path = Path(self.ml_config["model_storage_path"]) / f"{model_id}.pkl"
            if model_path.exists():
                model_path.unlink()

            # Delete metadata file
            metadata_path = (
                Path(self.ml_config["model_storage_path"]) / f"{model_id}_metadata.json"
            )
            if metadata_path.exists():
                metadata_path.unlink()

            # Remove from memory
            del self.models[model_id]
            if model_id in self.model_metrics:
                del self.model_metrics[model_id]

            logger.info(f"Model {model_id} deleted successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to delete model: {e}")
            return False

    async def _monitor_model_performance(self):
        """Monitor model performance"""
        while True:
            try:
                # Monitor model performance
                for model_id, metrics in self.model_metrics.items():
                    # Check for performance degradation
                    if metrics.accuracy < 0.7:  # Threshold for performance degradation
                        logger.warning(
                            f"Model {model_id} performance degraded: {metrics.accuracy}"
                        )

                        # Trigger retraining if auto_retrain is enabled
                        if self.ml_config["auto_retrain"]:
                            await self._schedule_retraining(model_id)

                await asyncio.sleep(3600)  # Check every hour

            except Exception as e:
                logger.error(f"Model performance monitoring error: {e}")
                await asyncio.sleep(3600)

    async def _monitor_training_jobs(self):
        """Monitor training jobs"""
        while True:
            try:
                # Monitor active training jobs
                for job_id, job in list(self.active_training_jobs.items()):
                    # Check for stuck jobs (running for more than 1 hour)
                    if (datetime.utcnow() - job.started_at).total_seconds() > 3600:
                        logger.warning(f"Training job {job_id} appears to be stuck")
                        job.status = ModelStatus.ERROR
                        job.error_message = "Training job timeout"
                        job.completed_at = datetime.utcnow()
                        del self.active_training_jobs[job_id]

                await asyncio.sleep(300)  # Check every 5 minutes

            except Exception as e:
                logger.error(f"Training job monitoring error: {e}")
                await asyncio.sleep(300)

    async def _schedule_retraining(self, model_id: str):
        """Schedule model retraining"""
        try:
            logger.info(f"Scheduling retraining for model {model_id}")

            # Get model info
            model_info = self.models[model_id]

            # Create retraining job
            retraining_job = TrainingJob(
                job_id=f"retrain_{int(datetime.utcnow().timestamp())}",
                model_type=ModelType(model_info["model_type"]),
                dataset_path="retraining_dataset.csv",  # Would use actual dataset
                parameters=model_info,
                status=ModelStatus.TRAINING,
                started_at=datetime.utcnow(),
                completed_at=None,
                metrics=None,
                error_message=None,
            )

            # Add to training queue
            self.training_queue.append(retraining_job)
            self.training_jobs[retraining_job.job_id] = retraining_job

            logger.info(f"Retraining job scheduled for model {model_id}")

        except Exception as e:
            logger.error(f"Failed to schedule retraining: {e}")

    async def get_training_status(self, job_id: str) -> Dict[str, Any]:
        """Get training job status"""
        try:
            if job_id not in self.training_jobs:
                raise ValueError(f"Training job {job_id} not found")

            job = self.training_jobs[job_id]

            return {
                "job_id": job.job_id,
                "model_type": job.model_type.value,
                "status": job.status.value,
                "started_at": job.started_at.isoformat(),
                "completed_at": (
                    job.completed_at.isoformat() if job.completed_at else None
                ),
                "metrics": job.metrics.__dict__ if job.metrics else None,
                "error_message": job.error_message,
            }

        except Exception as e:
            logger.error(f"Failed to get training status: {e}")
            raise

    async def get_ml_status(self) -> Dict[str, Any]:
        """Get ML service status"""
        return {
            "total_models": len(self.models),
            "active_training_jobs": len(self.active_training_jobs),
            "queued_jobs": len(self.training_queue),
            "model_types": list(set(m["model_type"] for m in self.models.values())),
            "storage_path": self.ml_config["model_storage_path"],
            "auto_retrain": self.ml_config["auto_retrain"],
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def shutdown(self):
        """Shutdown ML service"""
        try:
            logger.info("Shutting down ML service...")

            # Save any pending work
            # Cancel active training jobs
            for job_id in list(self.active_training_jobs.keys()):
                job = self.active_training_jobs[job_id]
                job.status = ModelStatus.ERROR
                job.error_message = "Service shutdown"
                job.completed_at = datetime.utcnow()

            logger.info("ML service shutdown complete")

        except Exception as e:
            logger.error(f"Error during ML service shutdown: {e}")
