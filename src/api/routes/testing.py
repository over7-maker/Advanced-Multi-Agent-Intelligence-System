"""
Testing Routes - Comprehensive testing endpoints for all AMAS components
"""

import logging
import time
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.amas.security.enhanced_auth import get_current_user_optional

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/testing", tags=["testing"])

# Database dependency (optional)
async def get_db():
    """Get database session (optional)"""
    try:
        from src.database.connection import get_session
        async for session in get_session():
            yield session
            return
    except Exception:
        yield None

# Redis dependency (optional) - matches tasks_integrated.py pattern
async def get_redis():
    """Get Redis client (optional)"""
    redis_client = None
    try:
        from src.cache.redis import get_redis_client
        redis_client = get_redis_client()
    except HTTPException as http_exc:
        logger.warning(f"Redis not available (auth error): {http_exc.detail}")
        redis_client = None
    except Exception as e:
        logger.warning(f"Redis not available: {e}")
        redis_client = None
    try:
        yield redis_client
    finally:
        pass

# Check if auth is available
try:
    from src.amas.security.enhanced_auth import get_current_user
    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False
    get_current_user = None


# Response Models
class TestResult(BaseModel):
    """Test result model"""
    test_name: str
    success: bool
    message: str
    duration: float
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class AgentTestResponse(BaseModel):
    """Agent test response"""
    agent_id: str
    agent_name: str
    available: bool
    test_result: Optional[TestResult] = None


class ProviderTestResponse(BaseModel):
    """AI Provider test response"""
    provider: str
    available: bool
    test_result: Optional[TestResult] = None
    latency: Optional[float] = None


class DatabaseTestResponse(BaseModel):
    """Database test response"""
    connected: bool
    test_result: Optional[TestResult] = None
    query_time: Optional[float] = None


class CacheTestResponse(BaseModel):
    """Cache test response"""
    connected: bool
    test_result: Optional[TestResult] = None
    operations: Optional[Dict[str, Any]] = None


class GraphDBTestResponse(BaseModel):
    """Graph database (Neo4j) test response"""
    connected: bool
    test_result: Optional[TestResult] = None
    node_count: Optional[int] = None


class WebSocketTestResponse(BaseModel):
    """WebSocket test response"""
    connected: bool
    test_result: Optional[TestResult] = None


class IntegrationTestResponse(BaseModel):
    """Integration test response"""
    platform: str
    connected: bool
    test_result: Optional[TestResult] = None


class MLTestResponse(BaseModel):
    """ML Prediction test response"""
    available: bool
    test_result: Optional[TestResult] = None
    prediction: Optional[Dict[str, Any]] = None


class SystemTestResponse(BaseModel):
    """System component test response"""
    component: str
    status: str
    test_result: Optional[TestResult] = None


# Agents Testing
@router.get("/agents", response_model=List[AgentTestResponse])
async def list_agents_for_testing(
    current_user = Depends(get_current_user_optional if AUTH_AVAILABLE else None)
):
    """List all available agents for testing"""
    try:
        from src.amas.core.unified_intelligence_orchestrator import get_unified_orchestrator
        
        orchestrator = get_unified_orchestrator()
        agents = []
        
        for agent_id, agent in orchestrator.agents.items():
            agents.append(AgentTestResponse(
                agent_id=agent_id,
                agent_name=getattr(agent, 'name', agent_id),
                available=True
            ))
        
        return agents
    except Exception as e:
        logger.error(f"Failed to list agents: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to list agents: {str(e)}")


@router.post("/agents/{agent_id}/test", response_model=AgentTestResponse)
async def test_agent(
    agent_id: str,
    target: str = Query(..., description="Target to test agent with"),
    current_user = Depends(get_current_user_optional if AUTH_AVAILABLE else None)
):
    """Test a specific agent"""
    test_start = time.time()
    
    try:
        from src.amas.core.unified_intelligence_orchestrator import get_unified_orchestrator
        
        orchestrator = get_unified_orchestrator()
        
        if agent_id not in orchestrator.agents:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        
        agent = orchestrator.agents[agent_id]
        agent_name = getattr(agent, 'name', agent_id)
        
        # Execute agent test
        test_task_id = f"test_{int(time.time())}"
        result = await agent.execute(
            task_id=test_task_id,
            target=target,
            parameters={"depth": "standard"}
        )
        
        test_duration = time.time() - test_start
        
        test_result = TestResult(
            test_name=f"Agent {agent_id} execution",
            success=result.get("success", False),
            message="Agent executed successfully" if result.get("success") else "Agent execution failed",
            duration=test_duration,
            data=result
        )
        
        return AgentTestResponse(
            agent_id=agent_id,
            agent_name=agent_name,
            available=True,
            test_result=test_result
        )
    
    except HTTPException:
        raise
    except Exception as e:
        test_duration = time.time() - test_start
        logger.error(f"Agent test failed: {e}", exc_info=True)
        
        test_result = TestResult(
            test_name=f"Agent {agent_id} execution",
            success=False,
            message=f"Test failed: {str(e)}",
            duration=test_duration,
            error=str(e)
        )
        
        return AgentTestResponse(
            agent_id=agent_id,
            agent_name=agent_id,
            available=False,
            test_result=test_result
        )


# AI Providers Testing
@router.get("/providers", response_model=List[ProviderTestResponse])
async def list_providers_for_testing(
    current_user = Depends(get_current_user_optional if AUTH_AVAILABLE else None)
):
    """List all available AI providers for testing"""
    try:
        from src.amas.ai.enhanced_router_v2 import get_available_providers, PROVIDER_CONFIGS
        
        available_providers = get_available_providers()
        providers = []
        
        # Get provider list from available providers
        for provider_name in available_providers:
            config = PROVIDER_CONFIGS.get(provider_name)
            providers.append(ProviderTestResponse(
                provider=provider_name,
                available=True
            ))
        
        # Also include configured providers that might not be available
        for provider_name, config in PROVIDER_CONFIGS.items():
            if provider_name not in available_providers:
                providers.append(ProviderTestResponse(
                    provider=provider_name,
                    available=False
                ))
        
        return providers
    except Exception as e:
        logger.error(f"Failed to list providers: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to list providers: {str(e)}")


@router.post("/providers/{provider}/test", response_model=ProviderTestResponse)
async def test_provider(
    provider: str,
    prompt: str = Query("Hello, this is a test", description="Test prompt"),
    current_user = Depends(get_current_user_optional if AUTH_AVAILABLE else None)
):
    """Test a specific AI provider"""
    test_start = time.time()
    
    try:
        from src.amas.ai.enhanced_router_class import get_ai_router
        
        router_instance = get_ai_router()
        
        # Test provider
        response = await router_instance.generate_with_fallback(
            prompt=prompt,
            model_preference=provider,
            max_tokens=100,
            temperature=0.3
        )
        
        test_duration = time.time() - test_start
        
        test_result = TestResult(
            test_name=f"Provider {provider} connection",
            success=bool(response.content),
            message="Provider responded successfully" if response.content else "Provider failed to respond",
            duration=test_duration,
            data={
                "provider": response.provider,
                "tokens_used": response.tokens_used,
                "cost_usd": response.cost_usd
            }
        )
        
        return ProviderTestResponse(
            provider=provider,
            available=True,
            test_result=test_result,
            latency=test_duration
        )
    
    except Exception as e:
        test_duration = time.time() - test_start
        logger.error(f"Provider test failed: {e}", exc_info=True)
        
        test_result = TestResult(
            test_name=f"Provider {provider} connection",
            success=False,
            message=f"Test failed: {str(e)}",
            duration=test_duration,
            error=str(e)
        )
        
        return ProviderTestResponse(
            provider=provider,
            available=False,
            test_result=test_result
        )


# Database Testing
@router.get("/database/status", response_model=DatabaseTestResponse)
async def test_database_status(
    db = Depends(get_db),
    current_user = Depends(get_current_user_optional if AUTH_AVAILABLE else None)
):
    """Test database connection status"""
    test_start = time.time()
    
    try:
        # Try to check connection using is_connected
        from src.database.connection import is_connected
        
        db_connected = await is_connected()
        
        if not db_connected:
            return DatabaseTestResponse(
                connected=False,
                test_result=TestResult(
                    test_name="Database connection",
                    success=False,
                    message="Database not connected",
                    duration=time.time() - test_start
                )
            )
        
        # If db session is available, test query
        query_time = None
        if db is not None:
            try:
                from sqlalchemy import text
                query_start = time.time()
                result = await db.execute(text("SELECT 1"))
                query_time = time.time() - query_start
                result.fetchone()
            except Exception as query_err:
                logger.warning(f"Database query test failed: {query_err}")
        
        test_duration = time.time() - test_start
        
        test_result = TestResult(
            test_name="Database connection",
            success=True,
            message="Database connected successfully",
            duration=test_duration,
            data={"query_time": query_time}
        )
        
        return DatabaseTestResponse(
            connected=True,
            test_result=test_result,
            query_time=query_time
        )
    
    except Exception as e:
        test_duration = time.time() - test_start
        logger.error(f"Database test failed: {e}", exc_info=True)
        
        test_result = TestResult(
            test_name="Database connection",
            success=False,
            message=f"Database test failed: {str(e)}",
            duration=test_duration,
            error=str(e)
        )
        
        return DatabaseTestResponse(
            connected=False,
            test_result=test_result
        )


@router.post("/database/query", response_model=TestResult)
async def test_database_query(
    query: str = Query("SELECT COUNT(*) FROM tasks", description="SQL query to test"),
    db = Depends(get_db),
    current_user = Depends(get_current_user_optional if AUTH_AVAILABLE else None)
):
    """Test database query execution"""
    test_start = time.time()
    
    try:
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")
        
        from sqlalchemy import text
        result = await db.execute(text(query))
        rows = result.fetchall()
        
        test_duration = time.time() - test_start
        
        return TestResult(
            test_name="Database query execution",
            success=True,
            message=f"Query executed successfully, returned {len(rows)} rows",
            duration=test_duration,
            data={"row_count": len(rows)}
        )
    
    except Exception as e:
        test_duration = time.time() - test_start
        logger.error(f"Database query test failed: {e}", exc_info=True)
        
        return TestResult(
            test_name="Database query execution",
            success=False,
            message=f"Query failed: {str(e)}",
            duration=test_duration,
            error=str(e)
        )


# Cache Testing
@router.get("/cache/status", response_model=CacheTestResponse)
async def test_cache_status(
    redis = Depends(get_redis),
    current_user = Depends(get_current_user_optional if AUTH_AVAILABLE else None)
):
    """Test cache (Redis) connection status"""
    test_start = time.time()
    
    try:
        # Try to check connection using is_connected
        from src.cache.redis import is_connected
        
        redis_connected = await is_connected()
        
        if not redis_connected:
            return CacheTestResponse(
                connected=False,
                test_result=TestResult(
                    test_name="Cache connection",
                    success=False,
                    message="Redis not connected",
                    duration=time.time() - test_start
                )
            )
        
        # If redis client is available, test operations
        operations = None
        if redis is not None:
            try:
                # Test operations
                test_key = f"test_{int(time.time())}"
                test_value = "test_value"
                
                # SET
                await redis.set(test_key, test_value, ex=60)
                
                # GET
                retrieved = await redis.get(test_key)
                retrieved_value = retrieved.decode() if isinstance(retrieved, bytes) else retrieved
                
                # DELETE
                await redis.delete(test_key)
                
                operations = {
                    "set": True,
                    "get": retrieved_value == test_value,
                    "delete": True
                }
            except Exception as ops_err:
                logger.warning(f"Redis operations test failed: {ops_err}")
                operations = {"set": False, "get": False, "delete": False}
        
        test_duration = time.time() - test_start
        
        test_result = TestResult(
            test_name="Cache connection",
            success=redis_connected,
            message="Cache connected successfully" if redis_connected else "Cache connection failed",
            duration=test_duration,
            data={"operations": operations}
        )
        
        return CacheTestResponse(
            connected=redis_connected,
            test_result=test_result,
            operations=operations or {"set": False, "get": False, "delete": False}
        )
    
    except Exception as e:
        test_duration = time.time() - test_start
        logger.error(f"Cache test failed: {e}", exc_info=True)
        
        test_result = TestResult(
            test_name="Cache connection",
            success=False,
            message=f"Cache test failed: {str(e)}",
            duration=test_duration,
            error=str(e)
        )
        
        return CacheTestResponse(
            connected=False,
            test_result=test_result
        )


# Graph Database (Neo4j) Testing
@router.get("/graphdb/status", response_model=GraphDBTestResponse)
async def test_graphdb_status(
    current_user = Depends(get_current_user_optional if AUTH_AVAILABLE else None)
):
    """Test Neo4j graph database connection status"""
    test_start = time.time()
    
    try:
        from src.graph.neo4j import is_connected, get_driver
        
        neo4j_connected = await is_connected()
        
        if not neo4j_connected:
            return GraphDBTestResponse(
                connected=False,
                test_result=TestResult(
                    test_name="Neo4j connection",
                    success=False,
                    message="Neo4j not connected",
                    duration=time.time() - test_start
                )
            )
        
        # Try to get node count
        node_count = None
        try:
            driver = get_driver()
            async with driver.session() as session:
                result = await session.run("MATCH (n) RETURN count(n) as count")
                record = await result.single()
                if record:
                    node_count = record["count"]
        except Exception as query_err:
            logger.warning(f"Neo4j query test failed: {query_err}")
        
        test_duration = time.time() - test_start
        
        test_result = TestResult(
            test_name="Neo4j connection",
            success=True,
            message="Neo4j connected successfully",
            duration=test_duration,
            data={"node_count": node_count}
        )
        
        return GraphDBTestResponse(
            connected=True,
            test_result=test_result,
            node_count=node_count
        )
    
    except Exception as e:
        test_duration = time.time() - test_start
        logger.error(f"Neo4j test failed: {e}", exc_info=True)
        
        test_result = TestResult(
            test_name="Neo4j connection",
            success=False,
            message=f"Neo4j test failed: {str(e)}",
            duration=test_duration,
            error=str(e)
        )
        
        return GraphDBTestResponse(
            connected=False,
            test_result=test_result
        )


# WebSocket Testing
@router.get("/websocket/status", response_model=WebSocketTestResponse)
async def test_websocket_status(
    current_user = Depends(get_current_user_optional if AUTH_AVAILABLE else None)
):
    """Test WebSocket connection status"""
    test_start = time.time()
    
    try:
        from src.api.websocket import websocket_manager
        
        active_connections = len(websocket_manager.active_connections)
        
        test_duration = time.time() - test_start
        
        test_result = TestResult(
            test_name="WebSocket manager",
            success=True,
            message=f"WebSocket manager available, {active_connections} active connections",
            duration=test_duration,
            data={"active_connections": active_connections}
        )
        
        return WebSocketTestResponse(
            connected=True,
            test_result=test_result
        )
    
    except Exception as e:
        test_duration = time.time() - test_start
        logger.error(f"WebSocket test failed: {e}", exc_info=True)
        
        test_result = TestResult(
            test_name="WebSocket manager",
            success=False,
            message=f"WebSocket test failed: {str(e)}",
            duration=test_duration,
            error=str(e)
        )
        
        return WebSocketTestResponse(
            connected=False,
            test_result=test_result
        )


# Integrations Testing
@router.get("/integrations", response_model=List[str])
async def list_integrations(
    current_user = Depends(get_current_user_optional if AUTH_AVAILABLE else None)
):
    """List all available integration platforms"""
    try:
        from src.amas.integration.integration_manager import IntegrationPlatform
        
        platforms = [platform.value for platform in IntegrationPlatform]
        return platforms
    except ImportError:
        # Return common platforms if module not available
        return ["github", "slack", "n8n", "notion", "jira", "salesforce"]


@router.post("/integrations/{platform}/test", response_model=IntegrationTestResponse)
async def test_integration(
    platform: str,
    current_user = Depends(get_current_user_optional if AUTH_AVAILABLE else None)
):
    """Test a specific integration platform"""
    test_start = time.time()
    
    try:
        # Try to import integration manager
        try:
            from src.amas.integration.integration_manager import IntegrationManager, IntegrationPlatform
            
            # Create manager instance
            manager = IntegrationManager()
            
            # Check if platform is supported
            try:
                platform_enum = IntegrationPlatform(platform.lower())
            except ValueError:
                raise HTTPException(status_code=404, detail=f"Platform {platform} is not supported")
            
            # Check if connector exists
            connector = manager.connectors.get(platform_enum)
            
            if not connector:
                raise HTTPException(status_code=404, detail=f"Integration connector for {platform} not initialized")
            
            # Test connection (basic validation)
            test_duration = time.time() - test_start
            
            test_result = TestResult(
                test_name=f"Integration {platform}",
                success=True,
                message=f"Integration {platform} connector is available",
                duration=test_duration,
                data={"platform": platform, "connector_type": type(connector).__name__}
            )
            
            return IntegrationTestResponse(
                platform=platform,
                connected=True,
                test_result=test_result
            )
        except ImportError as import_err:
            # Integration module not available
            test_duration = time.time() - test_start
            test_result = TestResult(
                test_name=f"Integration {platform}",
                success=False,
                message=f"Integration module not available: {str(import_err)}",
                duration=test_duration,
                error=str(import_err)
            )
            
            return IntegrationTestResponse(
                platform=platform,
                connected=False,
                test_result=test_result
            )
    
    except HTTPException:
        raise
    except Exception as e:
        test_duration = time.time() - test_start
        logger.error(f"Integration test failed: {e}", exc_info=True)
        
        test_result = TestResult(
            test_name=f"Integration {platform}",
            success=False,
            message=f"Integration test failed: {str(e)}",
            duration=test_duration,
            error=str(e)
        )
        
        return IntegrationTestResponse(
            platform=platform,
            connected=False,
            test_result=test_result
        )


# ML Predictions Testing
@router.post("/ml/predict", response_model=MLTestResponse)
async def test_ml_prediction(
    task_type: str = Query("security_scan", description="Task type for prediction"),
    target: str = Query("example.com", description="Target for prediction"),
    current_user = Depends(get_current_user_optional if AUTH_AVAILABLE else None)
):
    """Test ML prediction generation"""
    test_start = time.time()
    
    try:
        # Try to import ML predictor
        try:
            from src.amas.intelligence.predictive_engine import PredictiveIntelligenceEngine
            
            # Create predictor instance
            predictor = PredictiveIntelligenceEngine()
            
            # Generate prediction (with default agents list)
            prediction = await predictor.predict_task_outcome(
                task_type=task_type,
                target=target,
                parameters={},
                agents_planned=[]  # Empty list for testing
            )
            
            # Convert prediction to dict if it's a dataclass
            if hasattr(prediction, '__dict__'):
                prediction_dict = {
                    "success_probability": getattr(prediction, 'success_probability', 0.0),
                    "estimated_duration": getattr(prediction, 'estimated_duration', 0.0),
                    "quality_score_prediction": getattr(prediction, 'quality_score_prediction', 0.0),
                    "risk_factors": getattr(prediction, 'risk_factors', []),
                    "optimization_suggestions": getattr(prediction, 'optimization_suggestions', []),
                    "confidence": getattr(prediction, 'confidence', 0.0),
                }
            else:
                prediction_dict = prediction if isinstance(prediction, dict) else {"result": str(prediction)}
            
            test_duration = time.time() - test_start
            
            test_result = TestResult(
                test_name="ML prediction",
                success=bool(prediction),
                message="ML prediction generated successfully" if prediction else "ML prediction failed",
                duration=test_duration,
                data=prediction_dict
            )
            
            return MLTestResponse(
                available=True,
                test_result=test_result,
                prediction=prediction_dict
            )
        except ImportError as import_err:
            # ML module not available
            test_duration = time.time() - test_start
            test_result = TestResult(
                test_name="ML prediction",
                success=False,
                message=f"ML prediction module not available: {str(import_err)}",
                duration=test_duration,
                error=str(import_err)
            )
            
            return MLTestResponse(
                available=False,
                test_result=test_result
            )
    
    except Exception as e:
        test_duration = time.time() - test_start
        logger.error(f"ML prediction test failed: {e}", exc_info=True)
        
        test_result = TestResult(
            test_name="ML prediction",
            success=False,
            message=f"ML prediction test failed: {str(e)}",
            duration=test_duration,
            error=str(e)
        )
        
        return MLTestResponse(
            available=False,
            test_result=test_result
        )


# System Components Testing
@router.get("/system/health", response_model=SystemTestResponse)
async def test_system_health(
    current_user = Depends(get_current_user_optional if AUTH_AVAILABLE else None)
):
    """Test overall system health"""
    test_start = time.time()
    
    try:
        from src.api.routes.health import health_check
        
        health_status = await health_check()
        
        test_duration = time.time() - test_start
        
        overall_status = "healthy" if health_status.get("status") == "healthy" else "unhealthy"
        
        test_result = TestResult(
            test_name="System health check",
            success=overall_status == "healthy",
            message=f"System status: {overall_status}",
            duration=test_duration,
            data=health_status
        )
        
        return SystemTestResponse(
            component="system",
            status=overall_status,
            test_result=test_result
        )
    
    except Exception as e:
        test_duration = time.time() - test_start
        logger.error(f"System health test failed: {e}", exc_info=True)
        
        test_result = TestResult(
            test_name="System health check",
            success=False,
            message=f"System health test failed: {str(e)}",
            duration=test_duration,
            error=str(e)
        )
        
        return SystemTestResponse(
            component="system",
            status="unknown",
            test_result=test_result
        )

