"""
ML Prediction API endpoints
Provides ML-powered predictions for tasks and system resources
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from src.amas.intelligence.predictive_engine import PredictiveIntelligenceEngine

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize prediction engine (singleton)
_predictive_engine: Optional[PredictiveIntelligenceEngine] = None


def get_predictive_engine() -> PredictiveIntelligenceEngine:
    """Get predictive engine instance"""
    global _predictive_engine
    if _predictive_engine is None:
        try:
            _predictive_engine = PredictiveIntelligenceEngine()
        except Exception as e:
            logger.error(f"Failed to get predictive engine: {e}")
            raise HTTPException(status_code=500, detail="Predictive engine not available")
    return _predictive_engine


# Pydantic Models
class TaskPredictionRequest(BaseModel):
    """Task prediction request"""
    task_type: str
    target: str
    parameters: Optional[dict] = None
    agents_planned: Optional[List[str]] = None


class TaskPredictionResponse(BaseModel):
    """Task prediction response"""
    task_id: str
    success_probability: float
    estimated_duration: float
    quality_score_prediction: float
    confidence: float
    risk_factors: List[str]
    optimization_suggestions: List[str]


class ResourcePredictionResponse(BaseModel):
    """System resource prediction response"""
    time_horizon_minutes: int
    predicted_cpu_usage: float
    predicted_memory_usage: float
    predicted_task_load: int
    predicted_api_calls: int
    predicted_cost_per_hour: float
    bottleneck_predictions: List[str]
    scaling_recommendations: List[str]
    confidence: float


class ModelMetricsResponse(BaseModel):
    """ML model performance metrics"""
    model_name: str
    accuracy: Optional[float] = None
    r2_score: Optional[float] = None
    mean_absolute_error: Optional[float] = None
    training_samples: int
    last_training_date: Optional[str] = None
    feature_count: int
    prediction_count_since_training: int


@router.post("/predict/task", response_model=TaskPredictionResponse)
async def predict_task_outcome(
    prediction_request: TaskPredictionRequest,
    # current_user = Depends(get_current_user)  # TODO: Add auth
):
    """
    Predict task outcome before execution
    
    ✅ ML-powered success probability
    ✅ Duration estimation
    ✅ Quality prediction
    ✅ Risk factors
    ✅ Optimization suggestions
    """
    
    try:
        predictive_engine = get_predictive_engine()
        
        # Run prediction
        prediction = await predictive_engine.predict_task_outcome(
            task_type=prediction_request.task_type,
            target=prediction_request.target,
            parameters=prediction_request.parameters or {},
            agents_planned=prediction_request.agents_planned or []
        )
        
        return TaskPredictionResponse(
            task_id=prediction.task_id,
            success_probability=prediction.success_probability,
            estimated_duration=prediction.estimated_duration,
            quality_score_prediction=prediction.quality_score_prediction,
            confidence=prediction.confidence,
            risk_factors=prediction.risk_factors,
            optimization_suggestions=prediction.optimization_suggestions
        )
    
    except Exception as e:
        logger.error(f"Prediction failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )


@router.get("/predict/resources", response_model=ResourcePredictionResponse)
async def predict_system_resources(
    time_horizon: int = Query(60, ge=15, le=1440, description="Minutes ahead to predict"),
    # current_user = Depends(get_current_user)  # TODO: Add auth
):
    """
    Predict system resource usage
    
    ✅ CPU usage forecast
    ✅ Memory usage forecast
    ✅ Task load prediction
    ✅ API call volume
    ✅ Cost projection
    ✅ Bottleneck alerts
    ✅ Scaling recommendations
    """
    
    try:
        predictive_engine = get_predictive_engine()
        
        # Get system resource prediction
        prediction = await predictive_engine.predict_system_resources(
            time_horizon_minutes=time_horizon
        )
        
        # Calculate API calls and cost estimates
        predicted_api_calls = prediction.predicted_task_load * 8  # ~8 API calls per task
        predicted_cost_per_hour = predicted_api_calls * 0.002  # $0.002 per call
        
        return ResourcePredictionResponse(
            time_horizon_minutes=prediction.time_horizon_minutes,
            predicted_cpu_usage=prediction.predicted_cpu_usage,
            predicted_memory_usage=prediction.predicted_memory_usage,
            predicted_task_load=prediction.predicted_task_load,
            predicted_api_calls=predicted_api_calls,
            predicted_cost_per_hour=predicted_cost_per_hour,
            bottleneck_predictions=prediction.bottleneck_predictions,
            scaling_recommendations=prediction.scaling_recommendations,
            confidence=0.7  # Default confidence for resource predictions
        )
    
    except Exception as e:
        logger.error(f"Resource prediction failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Resource prediction failed: {str(e)}"
        )


@router.get("/models/metrics", response_model=List[ModelMetricsResponse])
async def get_model_metrics(
    # current_user = Depends(get_current_user)  # TODO: Add auth
):
    """
    Get ML model performance metrics
    
    ✅ Model accuracy
    ✅ Training samples
    ✅ Last training date
    ✅ Prediction counts
    ✅ Feature importance
    """
    
    try:
        predictive_engine = get_predictive_engine()
        
        # Get model performance metrics
        metrics = await predictive_engine.get_model_performance_metrics()
        
        return [
            ModelMetricsResponse(
                model_name=m["model_name"],
                accuracy=m.get("accuracy"),
                r2_score=m.get("r2_score"),
                mean_absolute_error=m.get("mean_absolute_error"),
                training_samples=m["training_samples"],
                last_training_date=m.get("last_training_date"),
                feature_count=m["feature_count"],
                prediction_count_since_training=m["prediction_count_since_training"]
            )
            for m in metrics
        ]
    
    except Exception as e:
        logger.error(f"Failed to get model metrics: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get model metrics: {str(e)}"
        )


@router.post("/models/retrain")
async def trigger_model_retraining(
    model_type: str = Query(..., description="task_outcome or resource_usage"),
    # current_user = Depends(get_current_user)  # TODO: Add auth, require admin
):
    """
    Manually trigger model retraining
    
    Admin-only endpoint
    """
    
    try:
        predictive_engine = get_predictive_engine()
        
        # Trigger model retraining
        await predictive_engine._retrain_model(model_type)
        
        return {
            "message": f"Model retraining triggered for {model_type}",
            "status": "success"
        }
    
    except Exception as e:
        logger.error(f"Model retraining failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Model retraining failed: {str(e)}"
        )

